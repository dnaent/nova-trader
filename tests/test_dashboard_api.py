"""Smoke tests for the local read-only dashboard API (ui/dashboard_api.py)."""
import ui.dashboard_api as api


def test_health():
    h = api.ep_health()
    assert h["status"] == "ok" and "ts" in h and "db" in h


def test_routes_present():
    assert {"/api/health", "/api/summary", "/api/trades",
            "/api/positions", "/api/nav", "/api/regime"} <= set(api.ROUTES)


def test_summary_structure(monkeypatch):
    """ep_summary returns one row per book with the UI-mapped keys (empty ledger ok)."""
    monkeypatch.setattr(api, "DB_PATH", ":memory:")
    s = api.ep_summary()
    assert "books" in s and len(s["books"]) >= 3
    needed = {"book_id", "wrapper", "strategy", "nav", "gate",
              "open_positions", "closed_trades", "validation"}
    assert needed <= set(s["books"][0])


def test_trades_and_regime_shapes(monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", ":memory:")
    assert "trades" in api.ep_trades({"limit": ["5"]})
    assert "regime" in api.ep_regime()
    assert "positions" in api.ep_positions()
