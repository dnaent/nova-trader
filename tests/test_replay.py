from decimal import Decimal

import numpy as np
import pandas as pd

import layers.data_loader as dl
from adapters.asset_equity import EquityAdapter
from adapters.asset_fx import FxAdapter
from backtest.replay import ReplayFeed, run_replay


# --------------------------------------------------------------------------- #
# Point-in-time correctness (no lookahead) — the core guarantee
# --------------------------------------------------------------------------- #
def test_replayfeed_serves_only_past_bars():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame({"Open": range(10), "High": range(10), "Low": range(10),
                       "Close": [float(i) for i in range(10)], "Volume": [1] * 10}, index=idx)
    feed = ReplayFeed(loader=lambda s: df)

    feed.set_as_of(idx[5])                                  # 2024-01-06
    bars = feed.get_daily_bars("X", lookback_days=100)
    assert bars.index.max() == idx[5]                      # nothing AFTER as-of
    assert len(bars) == 6
    assert feed.get_price("X") == Decimal("5.0")           # as-of close

    feed.set_as_of(idx[7])                                  # advancing reveals more
    assert len(feed.get_daily_bars("X", 100)) == 8

def test_replayfeed_returns_copies():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"Close": [1.0, 2, 3, 4, 5]}, index=idx)
    feed = ReplayFeed(loader=lambda s: df)
    feed.set_as_of(idx[-1])
    out = feed.get_daily_bars("X")
    out["INDICATOR"] = 1.0                                  # scanner appends in place
    assert "INDICATOR" not in feed.full_history("X").columns

def test_replayfeed_not_connected_without_as_of():
    feed = ReplayFeed(loader=lambda s: pd.DataFrame({"Close": [1.0]}))
    assert feed.is_connected() is False                    # no as-of set yet


# --------------------------------------------------------------------------- #
# End-to-end: replay generates a closed, outcome-labelled, 32-marker dataset
# --------------------------------------------------------------------------- #
def _synth(symbol: str) -> pd.DataFrame:
    """A strongly trending series so the scanner produces high-conviction signals."""
    n = 500
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    seed = abs(hash(symbol)) % (2**32)
    noise = np.random.RandomState(seed).normal(0, 1.0, n)
    close = pd.Series(np.linspace(100, 220, n) + noise, index=idx).clip(lower=1.0)
    high, low = close * 1.01, close * 0.99
    return pd.DataFrame({"Open": (high + low) / 2, "High": high, "Low": low,
                         "Close": close, "Volume": [500000] * n,
                         "Dividends": 0.0, "Stock Splits": 0.0}, index=idx)

def test_replay_generates_labelled_marker_dataset(monkeypatch):
    # Neutralise the macro gate so the run is deterministic and trades fire.
    monkeypatch.setattr(EquityAdapter, "macro_gate", lambda self: 80.0)
    monkeypatch.setattr(FxAdapter, "macro_gate", lambda self: 80.0)

    idx = _synth("REF").index
    start, end = idx[-4], idx[-1]                           # a tiny, fast window

    ledger = run_replay(start, end, db_path=":memory:", step_days=1,
                        exec_threshold=30.0, loader=_synth, do_report=False)
    try:
        samples = ledger.training_samples()
        acted = [s for s in samples if s["acted"]]
        assert acted, "replay should have produced at least one trade"
        # Every acted record carries the 32-marker snapshot...
        assert all(s["markers"] for s in acted)
        assert any("RSI_14" in s["markers"] for s in acted)
        # ...and force-close at the end means outcomes are labelled.
        assert any(s["realized_pnl"] is not None for s in acted)
        assert all( s["realized_pnl"] is not None for s in acted)  # all closed
    finally:
        ledger.close()
    # Feed must be uninstalled after the run.
    assert dl.get_price_feed() is None
