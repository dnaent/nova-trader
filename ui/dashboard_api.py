"""
Nova Engine — ui/dashboard_api.py

Local, READ-ONLY monitoring API for the SaaS dashboard (saas_ui on :5173). Exposes
the live paper-trading state from nova_ledger.db as JSON so the React UI can replace
its mock data with real engine data.

SAFETY: read-only (SELECTs only; never writes the ledger), localhost-only, and entirely
decoupled from the trading engine — it cannot affect trading. Zero new dependencies
(Python stdlib http.server) to keep the trading repo lean; the CLOUD product uses FastAPI
(see research/SAAS_PRODUCTIZATION_SCOPE.md). This is the local "monitor, don't fiddle"
layer for watching the out-of-sample track record mature.

Endpoints (all GET, JSON):
    /api/health                      -> {status, ts, db}
    /api/status                      -> operational health: last-cycle freshness,
                                        forward.log recency, TWS + Ollama reachability
    /api/summary                     -> per-book overview (nav, strategy, gate, positions,
                                        closed, win_rate, validation verdict)
    /api/trades?book=<id>&limit=50   -> recent trades (TradeRecord[]-shaped)
    /api/positions                   -> open positions + live price + unrealized PnL
    /api/nav?book=<id>               -> NAV history (for the equity-curve chart)
    /api/regime                      -> latest macro-gate reading per book (MarketRegime-ish)

Run:  python -m ui.dashboard_api            (serves http://127.0.0.1:8000)
      NOVA_LEDGER_DB=nova_ledger.db NOVA_API_PORT=8000 python -m ui.dashboard_api
      python -m ui.dashboard_api --status   (one-shot health check, no server; exit 0=healthy)
"""
from __future__ import annotations

import json
import os
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from core.context import load_books
from core.ledger import Ledger
from backtest.validation import validate_from_ledger

DB_PATH = os.environ.get("NOVA_LEDGER_DB", "nova_ledger.db")
PORT = int(os.environ.get("NOVA_API_PORT", "8000"))
# The Vite dev server origin (CORS). Adjust if the frontend runs elsewhere.
ALLOW_ORIGIN = os.environ.get("NOVA_API_CORS", "http://localhost:5173")


def _books():
    return load_books("portfolio.yaml")


def _ledger() -> Ledger:
    # A fresh read connection per request keeps it simple + thread-safe (read-only).
    return Ledger(DB_PATH)


# --------------------------------------------------------------------------- #
# Operational-health helpers (all read-only; used by /api/status so the
# "monitor, don't fiddle" phase can SEE the cron + deps at a glance).
# --------------------------------------------------------------------------- #
def _last_activity_ts(led: Ledger) -> str | None:
    """Most recent engine activity (max ts across the three written tables).

    This is the strongest signal of "did the daily paper cycle run" — the cron
    (`NovaParentPaperTraining`) writes decisions/nav/training rows every cycle.
    """
    best = None
    for tbl in ("decisions", "nav_history", "training_records"):
        try:
            row = led.conn.execute(f"SELECT MAX(ts) m FROM {tbl}").fetchone()
        except Exception:
            continue
        if row and row["m"] and (best is None or row["m"] > best):
            best = row["m"]
    return best


def _age_hours(ts_iso: str | None) -> float | None:
    """Hours since an ISO-8601 UTC timestamp (None-safe)."""
    if not ts_iso:
        return None
    import datetime as _dt
    try:
        t = _dt.datetime.fromisoformat(ts_iso)
        if t.tzinfo is None:
            t = t.replace(tzinfo=_dt.timezone.utc)
        return round((_dt.datetime.now(_dt.timezone.utc) - t).total_seconds() / 3600.0, 2)
    except Exception:
        return None


def _file_age_hours(path: str) -> float | None:
    """Hours since a file was last modified (None if missing)."""
    import time
    try:
        return round((time.time() - os.path.getmtime(path)) / 3600.0, 2)
    except OSError:
        return None


def _check_tws() -> dict:
    """Is a TWS/Gateway API socket listening? A bare TCP connect (no IB handshake,
    no orders) — purely read-only liveness for the data feed."""
    import socket
    port = int(os.environ.get("NOVA_IBKR_PORT", "7497"))
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.6):
            return {"ok": True, "port": port}
    except OSError as e:
        return {"ok": False, "port": port, "detail": e.__class__.__name__}


def _check_ollama() -> dict:
    """Is the Ollama auditor reachable? GET /api/tags (read-only)."""
    import urllib.request
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    if not host.startswith("http"):
        host = "http://" + host
    try:
        with urllib.request.urlopen(host + "/api/tags", timeout=0.8) as r:
            return {"ok": r.status == 200, "host": host}
    except Exception as e:
        return {"ok": False, "host": host, "detail": e.__class__.__name__}


# --------------------------------------------------------------------------- #
# Endpoint handlers (pure data; each returns a JSON-able object)
# --------------------------------------------------------------------------- #
def ep_health() -> dict:
    import time
    return {"status": "ok", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "db": DB_PATH,
            "db_exists": os.path.exists(DB_PATH)}


def ep_summary() -> dict:
    led, out = _ledger(), []
    try:
        for ctx in _books():
            perf = led.performance_summary(ctx.book_id)
            try:
                v = validate_from_ledger(ctx, led, run_robustness=False)
                verdict, metrics = ("PASS" if v.passed else "FAIL"), v.metrics
            except Exception:
                verdict, metrics = "n/a", {}
            row = led.conn.execute(
                "SELECT gate FROM decisions WHERE book_id=? ORDER BY ts DESC LIMIT 1",
                (ctx.book_id,)).fetchone()
            navrow = led.conn.execute(
                "SELECT nav FROM nav_history WHERE book_id=? ORDER BY ts DESC LIMIT 1",
                (ctx.book_id,)).fetchone()
            out.append({
                "book_id": ctx.book_id, "wrapper": ctx.wrapper, "strategy": ctx.strategy,
                "nav": float(navrow["nav"]) if navrow else None,
                "gate": float(row["gate"]) if row and row["gate"] is not None else None,
                "gate_min": ctx.gate_min,
                "open_positions": len(led.open_trades(ctx.book_id)),
                "closed_trades": perf.get("trades_closed", 0),
                "win_rate": metrics.get("win_rate"),
                "max_drawdown_pct": metrics.get("max_drawdown_pct"),
                "mar": metrics.get("mar"),
                "validation": verdict,
            })
        return {"books": out}
    finally:
        led.close()


def ep_trades(qs: dict) -> dict:
    book = (qs.get("book") or [None])[0]
    limit = int((qs.get("limit") or ["50"])[0])
    led = _ledger()
    try:
        sql = ("SELECT id,ts,book_id,symbol,side,quantity,price,notional,status,"
               "realized_pnl FROM trades")   # r_multiple lives in training_records, not trades
        params = ()
        if book:
            sql += " WHERE book_id=?"; params = (book,)
        sql += " ORDER BY ts DESC LIMIT ?"; params = params + (limit,)
        rows = [dict(r) for r in led.conn.execute(sql, params)]
        return {"trades": rows}
    finally:
        led.close()


def ep_positions() -> dict:
    from layers.data_loader import get_latest_price
    led, out = _ledger(), []
    try:
        for ctx in _books():
            for p in led.open_trades(ctx.book_id):
                entry = float(p["price"]); qty = float(p["quantity"])
                try:
                    cur = get_latest_price(p["symbol"])
                    cur = float(cur) if cur is not None else None
                except Exception:
                    cur = None
                side = p.get("side", "BUY")
                upnl = None
                if cur is not None:
                    upnl = (cur - entry) * qty if side == "BUY" else (entry - cur) * qty
                out.append({"book_id": ctx.book_id, "symbol": p["symbol"], "side": side,
                            "quantity": qty, "avgPrice": entry, "currentPrice": cur,
                            "unrealizedPnL": round(upnl, 2) if upnl is not None else None})
        return {"positions": out}
    finally:
        led.close()


def ep_nav(qs: dict) -> dict:
    book = (qs.get("book") or [None])[0]
    led = _ledger()
    try:
        if book:
            rows = [dict(r) for r in led.conn.execute(
                "SELECT date_str,nav FROM nav_history WHERE book_id=? ORDER BY ts", (book,))]
            return {"book_id": book, "nav": rows}
        out = {}
        for ctx in _books():
            out[ctx.book_id] = [dict(r) for r in led.conn.execute(
                "SELECT date_str,nav FROM nav_history WHERE book_id=? ORDER BY ts",
                (ctx.book_id,))]
        return {"nav": out}
    finally:
        led.close()


def ep_regime() -> dict:
    led, out = _ledger(), []
    try:
        for ctx in _books():
            row = led.conn.execute(
                "SELECT gate,ts FROM decisions WHERE book_id=? ORDER BY ts DESC LIMIT 1",
                (ctx.book_id,)).fetchone()
            gate = float(row["gate"]) if row and row["gate"] is not None else None
            floor = ctx.gate_min if ctx.gate_min is not None else 40
            label = "n/a"
            if gate is not None:
                label = "risk-on" if gate >= floor else "risk-off / cash"
            out.append({"book_id": ctx.book_id, "gate": gate, "gate_min": floor,
                        "regime": label, "ts": row["ts"] if row else None})
        return {"regime": out}
    finally:
        led.close()


def ep_status() -> dict:
    """Operational health for the 'monitor, don't fiddle' phase: did the daily
    paper cycle run, is it stale, and are TWS + Ollama reachable. Read-only.

    `stale` flags the last cycle older than NOVA_STALE_HOURS (default 72h, which
    spans a Fri->Mon weekend gap of the weekday cron). `healthy` is the rollup.
    """
    stale_after = float(os.environ.get("NOVA_STALE_HOURS", "72"))
    led = _ledger()
    try:
        last = _last_activity_ts(led)
    finally:
        led.close()
    cycle_age = _age_hours(last)
    log_age = _file_age_hours(os.path.join("logs", "forward.log"))
    stale = cycle_age is None or cycle_age > stale_after
    tws, ollama = _check_tws(), _check_ollama()
    # The cron self-heals (yfinance / neutral-auditor fallbacks), so a down dep is
    # a WARN not a failure; "healthy" is really "is the cycle running & fresh".
    return {
        "healthy": (last is not None) and (not stale),
        "last_cycle": last,
        "last_cycle_age_hours": cycle_age,
        "stale": stale,
        "stale_after_hours": stale_after,
        "forward_log_age_hours": log_age,
        "dependencies": {"tws": tws, "ollama": ollama},
        "note": "deps down => cron self-heals via yfinance / neutral-50 auditor",
    }


ROUTES = {
    "/api/health": lambda qs: ep_health(),
    "/api/status": lambda qs: ep_status(),
    "/api/summary": lambda qs: ep_summary(),
    "/api/trades": ep_trades,
    "/api/positions": lambda qs: ep_positions(),
    "/api/nav": ep_nav,
    "/api/regime": lambda qs: ep_regime(),
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        handler = ROUTES.get(parsed.path)
        if handler is None:
            self._send(404, {"error": "not found", "routes": list(ROUTES)})
            return
        try:
            self._send(200, handler(parse_qs(parsed.query)))
        except Exception as e:  # never crash the server on a bad read
            self._send(500, {"error": type(e).__name__, "detail": str(e)})

    def log_message(self, *args) -> None:   # quiet
        pass


def main() -> None:
    import sys
    if "--status" in sys.argv[1:]:
        # One-shot operational health check (no server) — a quick terminal glance
        # for the "monitor, don't fiddle" phase. Exit 0 if healthy, 1 if not.
        s = ep_status()
        print(json.dumps(s, indent=2, default=str))
        sys.exit(0 if s.get("healthy") else 1)
    print(f"Nova dashboard API (READ-ONLY) -> http://127.0.0.1:{PORT}  db={DB_PATH}")
    print(f"CORS allow-origin: {ALLOW_ORIGIN}  | routes: {', '.join(ROUTES)}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
