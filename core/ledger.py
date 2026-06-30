"""
Nova Engine — core/ledger.py

SQLite-backed trade ledger + decision log + performance scoring.
Asset-agnostic: works identically for every book.

Two tables:
  decisions  — every candidate the engine evaluated, acted or not, with the reason
  trades     — every order routed (paper or live), with optional realised P&L

Performance metrics are deliberately simple in Phase 1 (trade-level, not
annualised). Replace with time-series Sharpe and proper return series in a
later phase. Methods return None when there's insufficient data.
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional


_SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    book_id     TEXT NOT NULL,
    symbol      TEXT,
    gate        REAL,
    quant_score REAL,
    claude_score REAL,
    blended     REAL,
    acted       INTEGER NOT NULL,
    reason      TEXT
);
CREATE TABLE IF NOT EXISTS trades (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT NOT NULL,
    book_id      TEXT NOT NULL,
    account_id   TEXT NOT NULL,
    symbol       TEXT NOT NULL,
    side         TEXT NOT NULL,
    quantity     REAL NOT NULL,
    price        REAL NOT NULL,
    notional     REAL NOT NULL,
    status       TEXT NOT NULL,        -- 'paper' | 'staged' | 'live' | 'closed'
    realized_pnl REAL,                 -- NULL until the position is closed
    stop_loss    REAL,
    take_profit  REAL,
    trailing_atr REAL,                 -- ATR multiple for trailing stops (FX trend); NULL => fixed-stop only
    broker_ref   TEXT
);
CREATE INDEX IF NOT EXISTS idx_trades_book ON trades(book_id);
CREATE INDEX IF NOT EXISTS idx_decisions_book ON decisions(book_id);

CREATE TABLE IF NOT EXISTS nav_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    date_str    TEXT NOT NULL,
    book_id     TEXT NOT NULL,
    nav         REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nav_history_book ON nav_history(book_id);

-- The parent model's training dataset (the parent->child bridge the cloud model
-- reads). One row per audited candidate: the full Inference Context Bundle
-- (macro regime + the 32-marker snapshot), the book context, the decision +
-- all three scores, the sizing, and the outcome (backfilled on trade close).
CREATE TABLE IF NOT EXISTS training_records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT NOT NULL,
    book_id      TEXT NOT NULL,
    wrapper      TEXT,
    asset_class  TEXT,
    symbol       TEXT NOT NULL,
    gate         REAL,
    macro_json   TEXT,                 -- macro regime snapshot (JSON)
    markers_json TEXT,                 -- 32-marker snapshot (JSON)
    quant_score  REAL,
    claude_score REAL,
    blended      REAL,
    acted        INTEGER NOT NULL,
    reason       TEXT,
    side         TEXT,
    quantity     REAL,
    price        REAL,
    notional     REAL,
    stop_loss    REAL,
    take_profit  REAL,
    trade_id     INTEGER,              -- FK -> trades.id, for the outcome join
    realized_pnl REAL,                 -- backfilled on close
    r_multiple   REAL                  -- backfilled on close
);
CREATE INDEX IF NOT EXISTS idx_training_book ON training_records(book_id);
CREATE INDEX IF NOT EXISTS idx_training_trade ON training_records(trade_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Ledger:
    def __init__(self, db_path: str = "nova_ledger.db"):
        # timeout + WAL so the daily allocation cron (run_paper) and the intraday
        # FX/Crypto task (run_intraday) can write the shared ledger concurrently
        # without "database is locked" (WAL = concurrent readers + one writer;
        # busy_timeout makes a writer wait rather than error). No-op on :memory:.
        self.conn = sqlite3.connect(db_path, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA busy_timeout=30000")
        except Exception:
            pass
        self.conn.executescript(_SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self) -> None:
        """Idempotent column adds for DBs created before a schema bump."""
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(trades)")}
        if "trailing_atr" not in cols:
            self.conn.execute("ALTER TABLE trades ADD COLUMN trailing_atr REAL")

    # ----- writes --------------------------------------------------------- #
    def record_decision(self, book_id: str, symbol: Optional[str], gate: float,
                         quant_score: Optional[float], claude_score: Optional[float],
                         blended: Optional[float], acted: bool, reason: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO decisions (ts,book_id,symbol,gate,quant_score,claude_score,"
            "blended,acted,reason) VALUES (?,?,?,?,?,?,?,?,?)",
            (_now(), book_id, symbol, gate, quant_score, claude_score,
             blended, int(acted), reason),
        )
        self.conn.commit()
        return cur.lastrowid

    def record_trade(self, book_id: str, account_id: str, symbol: str, side: str,
                     quantity: Decimal, price: Decimal, notional: Decimal,
                     status: str = "paper", stop_loss: Optional[Decimal] = None,
                     take_profit: Optional[Decimal] = None,
                     broker_ref: Optional[str] = None,
                     trailing_atr: Optional[Decimal] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO trades (ts,book_id,account_id,symbol,side,quantity,price,"
            "notional,status,stop_loss,take_profit,trailing_atr,broker_ref) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (_now(), book_id, account_id, symbol, side, float(quantity), float(price),
             float(notional), status,
             float(stop_loss) if stop_loss is not None else None,
             float(take_profit) if take_profit is not None else None,
             float(trailing_atr) if trailing_atr is not None else None, broker_ref),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_stop(self, trade_id: int, stop_loss: Decimal) -> None:
        """Ratchet a position's stop-loss (used by ATR trailing stops)."""
        self.conn.execute("UPDATE trades SET stop_loss=? WHERE id=?",
                          (float(stop_loss), trade_id))
        self.conn.commit()

    def record_training_sample(self, *, book_id: str, symbol: str,
                               wrapper: Optional[str] = None,
                               asset_class: Optional[str] = None,
                               macro: Optional[dict] = None,
                               markers: Optional[dict] = None,
                               gate: Optional[float] = None,
                               quant_score: Optional[float] = None,
                               claude_score: Optional[float] = None,
                               blended: Optional[float] = None,
                               acted: bool = False, reason: str = "",
                               order=None, trade_id: Optional[int] = None) -> int:
        """Log one parent-model training record (the parent->child bridge dataset).

        Captures the full Inference Context Bundle (macro regime + 32-marker
        snapshot), book context, decision + all three scores, and sizing. The
        outcome columns are backfilled later by close_trade() via trade_id.
        ``order`` is a core.context.Order (or None when no order was placed).
        """
        side = quantity = price = notional = stop_loss = take_profit = None
        if order is not None:
            side = order.side
            quantity = float(order.quantity)
            price = float(order.price)
            notional = float(order.notional)
            stop_loss = float(order.stop_loss) if order.stop_loss is not None else None
            take_profit = float(order.take_profit) if order.take_profit is not None else None
        cur = self.conn.execute(
            "INSERT INTO training_records (ts,book_id,wrapper,asset_class,symbol,gate,"
            "macro_json,markers_json,quant_score,claude_score,blended,acted,reason,"
            "side,quantity,price,notional,stop_loss,take_profit,trade_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (_now(), book_id, wrapper, asset_class, symbol, gate,
             json.dumps(macro or {}), json.dumps(markers or {}),
             quant_score, claude_score, blended, int(acted), reason,
             side, quantity, price, notional, stop_loss, take_profit, trade_id),
        )
        self.conn.commit()
        return cur.lastrowid

    def close_trade(self, trade_id: int, exit_price: Decimal, realized_pnl: Decimal) -> None:
        self.conn.execute(
            "UPDATE trades SET status='closed', realized_pnl=?, broker_ref=broker_ref "
            "WHERE id=?", (float(realized_pnl), trade_id))
        # Backfill the training record's outcome: realized PnL + R-multiple, where
        # initial risk = (entry - stop) * qty. R-multiple is left NULL if no stop.
        pnl = float(realized_pnl)
        row = self.conn.execute(
            "SELECT price, stop_loss, quantity FROM training_records WHERE trade_id=?",
            (trade_id,)).fetchone()
        r_multiple = None
        if row is not None and row["stop_loss"] is not None and row["quantity"]:
            risk = abs(row["price"] - row["stop_loss"]) * row["quantity"]
            if risk > 0:
                r_multiple = pnl / risk
        self.conn.execute(
            "UPDATE training_records SET realized_pnl=?, r_multiple=? WHERE trade_id=?",
            (pnl, r_multiple, trade_id))
        self.conn.commit()

    def record_nav(self, book_id: str, nav: Decimal) -> None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.conn.execute(
            "INSERT INTO nav_history (ts, date_str, book_id, nav) VALUES (?, ?, ?, ?)",
            (_now(), date_str, book_id, float(nav))
        )
        self.conn.commit()

    # ----- reads / metrics ------------------------------------------------ #
    def _closed_pnls(self, book_id: Optional[str]) -> list[float]:
        q = "SELECT realized_pnl FROM trades WHERE realized_pnl IS NOT NULL"
        args: tuple = ()
        if book_id:
            q += " AND book_id=?"
            args = (book_id,)
        q += " ORDER BY id ASC"
        return [r["realized_pnl"] for r in self.conn.execute(q, args)]

    def closed_returns(self, book_id: Optional[str]) -> list[float]:
        """Per-trade fractional returns (realized_pnl / notional) for closed trades.

        These are the unit-free returns the robustness tools (walk-forward,
        Monte-Carlo) and Sortino consume. Trades with non-positive notional are
        skipped so a bad row can't produce a divide-by-zero.
        """
        q = ("SELECT realized_pnl, notional FROM trades "
             "WHERE realized_pnl IS NOT NULL AND notional > 0")
        args: tuple = ()
        if book_id:
            q += " AND book_id=?"
            args = (book_id,)
        q += " ORDER BY id ASC"
        return [r["realized_pnl"] / r["notional"] for r in self.conn.execute(q, args)]

    def nav_series(self, book_id: str) -> list[float]:
        """The book's NAV equity curve, ordered oldest-first."""
        rows = self.conn.execute(
            "SELECT nav FROM nav_history WHERE book_id=? ORDER BY ts ASC", (book_id,)
        ).fetchall()
        return [r["nav"] for r in rows]

    def open_trades(self, book_id: Optional[str] = None) -> list[dict]:
        """Open paper positions not yet closed (realized_pnl NULL): BUY (long) and
        SELL (short, FX trend-following). The ``side`` is returned so exit P&L and
        stop/take logic can be direction-aware. Equities only ever open BUY, so
        their behaviour is unchanged.

        The ledger is the source of truth for open positions, so exit evaluation
        is broker-agnostic.
        """
        q = ("SELECT id, book_id, account_id, symbol, side, quantity, price, stop_loss, "
             "take_profit, trailing_atr FROM trades WHERE realized_pnl IS NULL "
             "AND status != 'closed'")
        args: tuple = ()
        if book_id:
            q += " AND book_id=?"
            args = (book_id,)
        q += " ORDER BY id ASC"
        return [dict(r) for r in self.conn.execute(q, args)]

    def realized_pnl_total(self, book_id: Optional[str] = None) -> float:
        """Cumulative realised PnL across closed trades (a book, or all books)."""
        q = "SELECT COALESCE(SUM(realized_pnl), 0.0) s FROM trades WHERE realized_pnl IS NOT NULL"
        args: tuple = ()
        if book_id:
            q += " AND book_id=?"
            args = (book_id,)
        return float(self.conn.execute(q, args).fetchone()["s"])

    def get_peak_nav(self, book_id: str) -> Optional[float]:
        row = self.conn.execute(
            "SELECT MAX(nav) as peak FROM nav_history WHERE book_id=?", (book_id,)
        ).fetchone()
        return row["peak"] if row and row["peak"] is not None else None

    def get_daily_loss_pct(self, book_id: str, current_nav: Decimal) -> float:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        row = self.conn.execute(
            "SELECT nav FROM nav_history WHERE book_id=? AND date_str < ? ORDER BY ts DESC LIMIT 1",
            (book_id, date_str)
        ).fetchone()
        if not row:
            return 0.0
        start_nav = row["nav"]
        if start_nav <= 0:
            return 0.0
        loss_pct = ((start_nav - float(current_nav)) / start_nav) * 100.0
        return max(0.0, loss_pct)

    @staticmethod
    def _sharpe(pnls: list[float]) -> Optional[float]:
        """Trade-level Sharpe proxy (not annualised). None if < 2 closed trades."""
        if len(pnls) < 2:
            return None
        mean = sum(pnls) / len(pnls)
        var = sum((p - mean) ** 2 for p in pnls) / (len(pnls) - 1)
        std = math.sqrt(var)
        return None if std == 0 else round(mean / std, 4)

    @staticmethod
    def _max_drawdown(pnls: list[float]) -> Optional[float]:
        """Max drawdown of the cumulative realised-P&L curve. None if no data."""
        if not pnls:
            return None
        cum, peak, mdd = 0.0, 0.0, 0.0
        for p in pnls:
            cum += p
            peak = max(peak, cum)
            mdd = min(mdd, cum - peak)
        return round(mdd, 2)

    def performance_summary(self, book_id: Optional[str] = None) -> dict:
        pnls = self._closed_pnls(book_id)
        total_q = "SELECT COUNT(*) n FROM trades"
        args: tuple = ()
        if book_id:
            total_q += " WHERE book_id=?"
            args = (book_id,)
        n_trades = self.conn.execute(total_q, args).fetchone()["n"]
        wins = sum(1 for p in pnls if p > 0)
        return {
            "book_id": book_id or "ALL",
            "trades_recorded": n_trades,
            "trades_closed": len(pnls),
            "win_rate": round(wins / len(pnls), 3) if pnls else None,
            "total_realized_pnl": round(sum(pnls), 2) if pnls else 0.0,
            "sharpe_trade_level": self._sharpe(pnls),
            "max_drawdown": self._max_drawdown(pnls),
        }

    def training_samples(self, book_id: Optional[str] = None) -> list[dict]:
        """Return training records as dicts, JSON columns parsed back to objects.

        This is the curated parent-model dataset the cloud child reads (per-tenant
        isolated at the SaaS layer — never cross-book/cross-tenant).
        """
        q = "SELECT * FROM training_records"
        args: tuple = ()
        if book_id:
            q += " WHERE book_id=?"
            args = (book_id,)
        q += " ORDER BY id ASC"
        out = []
        for r in self.conn.execute(q, args):
            d = dict(r)
            d["macro"] = json.loads(d.pop("macro_json") or "{}")
            d["markers"] = json.loads(d.pop("markers_json") or "{}")
            out.append(d)
        return out

    def export_training_jsonl(self, path: str, book_id: Optional[str] = None) -> int:
        """Write the training dataset to newline-delimited JSON. Returns row count."""
        rows = self.training_samples(book_id)
        with open(path, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
        return len(rows)

    def close(self) -> None:
        self.conn.close()
