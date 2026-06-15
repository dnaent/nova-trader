from decimal import Decimal

import numpy as np
import pandas as pd

import layers.data_loader as dl
from core.context import Candidate
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
# End-to-end: replay generates a closed, outcome-labelled, marker dataset.
# Uses a deterministic injected adapter so the test verifies the HARNESS
# (point-in-time data -> decision -> sizing -> force-close -> outcome) without
# depending on the stochastic scanner/macro-gate. Point-in-time correctness is
# covered separately above.
# --------------------------------------------------------------------------- #
def _flat(symbol: str) -> pd.DataFrame:
    """Simple valid price history (the injected adapter doesn't need a signal)."""
    n = 400
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    close = pd.Series(np.linspace(100.0, 130.0, n), index=idx)
    return pd.DataFrame({"Open": close, "High": close * 1.01, "Low": close * 0.99,
                         "Close": close, "Volume": [500000] * n}, index=idx)

class _DeterministicAdapter:
    """Always proposes a high-conviction buy at the point-in-time close."""
    asset_class = "EQUITY"
    handles = {"EQUITY", "ETF"}
    def __init__(self):
        self._last_gate_result = {"regime": "test"}
    def macro_gate(self):
        return 80.0
    def scan(self, universe):
        out = []
        for s in universe:
            df = dl.get_daily_data(s)                       # point-in-time via ReplayFeed
            if df is None or df.empty:
                continue
            px = Decimal(str(df["Close"].iloc[-1]))
            out.append(Candidate(s, "EQUITY", 90.0, px, meta={"markers": {"RSI_14": 55.0}}))
        return out
    def auditor_prompt(self, c):
        return f"audit {c.symbol}"

def test_replay_generates_labelled_marker_dataset():
    idx = _flat("REF").index
    start, end = idx[-4], idx[-1]                           # a tiny, fast window

    ledger = run_replay(start, end, db_path=":memory:", step_days=1,
                        exec_threshold=30.0, loader=_flat,
                        adapters=[_DeterministicAdapter()], do_report=False)
    try:
        acted = [s for s in ledger.training_samples() if s["acted"]]
        assert acted, "replay should have produced at least one trade"
        assert all(s["markers"] for s in acted)            # 32-marker snapshot captured
        assert all("RSI_14" in s["markers"] for s in acted)
        assert all(s["realized_pnl"] is not None for s in acted)  # force-closed -> labelled
    finally:
        ledger.close()
    assert dl.get_price_feed() is None                     # feed uninstalled after run


# --------------------------------------------------------------------------- #
# Belt-and-braces: the REAL scanner (RandomForest on the 32-indicator matrix)
# runs end-to-end through replay. Offline + deterministic: the macro gate and the
# network-bound qualitative inputs are stubbed, but the scanner itself is real.
# --------------------------------------------------------------------------- #
def _mixed(symbol: str) -> pd.DataFrame:
    """A seeded random walk -> mixed up/down moves -> two target classes (so the
    real classifier trains without a degenerate single-class case)."""
    n = 500
    idx = pd.date_range("2022-01-03", periods=n, freq="B")
    rng = np.random.RandomState(sum(ord(ch) for ch in symbol))
    close = pd.Series(100.0 + np.cumsum(rng.normal(0.05, 1.5, n)), index=idx).clip(lower=1.0)
    return pd.DataFrame({"Open": close, "High": close + rng.uniform(0.1, 1.0, n),
                         "Low": close - rng.uniform(0.1, 1.0, n), "Close": close,
                         "Volume": [500000] * n, "Dividends": 0.0, "Stock Splits": 0.0},
                        index=idx)

def test_real_scanner_runs_through_replay(monkeypatch):
    import adapters.asset_equity as ae
    from adapters.asset_equity import EquityAdapter
    # Fix the gate so scanning proceeds; stub the network-bound qualitative inputs.
    monkeypatch.setattr(EquityAdapter, "macro_gate", lambda self: 80.0)
    monkeypatch.setattr(ae, "get_financials", lambda s: "FIN")
    monkeypatch.setattr(ae, "get_recent_news", lambda s: "NEWS")

    idx = _mixed("REF").index
    start, end = idx[-3], idx[-1]                           # 2 steps, REAL scanner

    ledger = run_replay(start, end, db_path=":memory:", step_days=1, exec_threshold=50.0,
                        loader=_mixed, adapters=[EquityAdapter()], do_report=False)
    try:
        samples = ledger.training_samples()
        assert samples, "real scanner should have produced audited candidates"
        # The genuine 32-indicator matrix was captured (not a stub's 1-2 markers).
        assert any(len(s["markers"]) >= 10 for s in samples)
        assert any("MACD_12_26_9" in s["markers"] for s in samples)
    finally:
        ledger.close()
