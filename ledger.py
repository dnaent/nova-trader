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
    broker_ref   TEXT
);
CREATE INDEX IF NOT EXISTS idx_trades_book ON trades(book_id);
CREATE INDEX IF NOT EXISTS idx_decisions_book ON decisions(book_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Ledger:
    def __init__(self, db_path: str = "nova_ledger.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

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
                     broker_ref: Optional[str] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO trades (ts,book_id,account_id,symbol,side,quantity,price,"
            "notional,status,stop_loss,take_profit,broker_ref) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (_now(), book_id, account_id, symbol, side, float(quantity), float(price),
             float(notional), status,
             float(stop_loss) if stop_loss is not None else None,
             float(take_profit) if take_profit is not None else None, broker_ref),
        )
        self.conn.commit()
        return cur.lastrowid

    def close_trade(self, trade_id: int, exit_price: Decimal, realized_pnl: Decimal) -> None:
        self.conn.execute(
            "UPDATE trades SET status='closed', realized_pnl=?, broker_ref=broker_ref "
            "WHERE id=?", (float(realized_pnl), trade_id))
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

    def close(self) -> None:
        self.conn.close()
