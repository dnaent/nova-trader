"""Smoke tests for the local read-only dashboard API (ui/dashboard_api.py)."""
import ui.dashboard_api as api


def test_health():
    h = api.ep_health()
    assert h["status"] == "ok" and "ts" in h and "db" in h


def test_routes_present():
    assert {"/api/health", "/api/status", "/api/summary", "/api/trades",
            "/api/positions", "/api/nav", "/api/regime"} <= set(api.ROUTES)


def test_status_structure(monkeypatch):
    """ep_status reports cycle freshness + dependency reachability (empty ledger ok)."""
    monkeypatch.setattr(api, "DB_PATH", ":memory:")
    s = api.ep_status()
    assert {"healthy", "last_cycle", "stale", "dependencies"} <= set(s)
    assert {"tws", "ollama"} <= set(s["dependencies"])
    # An empty in-memory ledger has no activity => not healthy, and stale.
    assert s["last_cycle"] is None and s["healthy"] is False and s["stale"] is True


def test_age_helpers():
    """_age_hours / _file_age_hours are None-safe and monotonic."""
    import datetime as dt
    assert api._age_hours(None) is None
    assert api._file_age_hours("does/not/exist.log") is None
    recent = dt.datetime.now(dt.timezone.utc).isoformat()
    age = api._age_hours(recent)
    assert age is not None and age < 1.0


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
