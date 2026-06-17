"""
Tests for MacroGate graceful degradation (layers/macro_gate.py).

The gate composites three components (HMM regime 0.5, VIX term structure 0.3,
safe-haven correlation 0.2). The key contract verified here: a missing input feed
drops only its component and renormalises the remaining weights, instead of the
whole gate collapsing to a flat neutral 50 (which would spuriously de-risk every
book from a single missing feed). When all feeds are present the result is
identical to the original fixed-weight formula.

`predict_regime_prob` is monkeypatched to a constant so the assertions target the
degradation/renormalisation wiring rather than the HMM fit.
"""
import pandas as pd
import pytest

import layers.macro_gate as mg
from layers.macro_gate import MacroGate

SAFE_PROB = 0.9          # mocked HMM output
IDX = pd.date_range("2020-01-01", periods=60, freq="B")


def _frame(closes):
    """Minimal OHLC frame on the shared index."""
    return pd.DataFrame({"Close": closes, "High": closes, "Low": closes}, index=IDX)


def _full_feeds():
    """A complete, well-formed set of feeds for every symbol the gate reads."""
    spy = [100 + i * 0.5 for i in range(60)]          # gently rising
    tlt = [90 - i * 0.1 for i in range(60)]           # mildly inverse to SPY
    gld = [150 + (i % 5) for i in range(60)]
    vix = [20.0] * 60
    vix3m = [25.0] * 60                               # ratio 0.8 -> vix_score 100
    tnx = [4.0] * 60
    irx = [3.5] * 60
    return {
        "SPY": _frame(spy), "TLT": _frame(tlt), "GLD": _frame(gld),
        "^VIX": _frame(vix), "^VIX3M": _frame(vix3m),
        "^TNX": _frame(tnx), "^IRX": _frame(irx),
    }


@pytest.fixture
def patched(monkeypatch):
    """Install a controllable get_daily_data + constant HMM into the gate."""
    feeds = _full_feeds()

    def fake_get(symbol, *a, **k):
        return feeds.get(symbol, pd.DataFrame())

    monkeypatch.setattr(mg, "get_daily_data", fake_get)
    monkeypatch.setattr(mg, "predict_regime_prob", lambda *a, **k: SAFE_PROB)
    return feeds


def _expected_vix(feeds):
    cur = feeds["^VIX"]["Close"].iloc[-1]
    cur3m = feeds["^VIX3M"]["Close"].iloc[-1]
    ratio = cur / cur3m if cur3m > 0 else 1.0
    return max(0.0, min(100.0, (1.2 - ratio) * 250))


def _expected_corr(feeds):
    df = pd.DataFrame({
        "SPY": feeds["SPY"]["Close"].pct_change(fill_method=None),
        "TLT": feeds["TLT"]["Close"].pct_change(fill_method=None),
        "GLD": feeds["GLD"]["Close"].pct_change(fill_method=None),
    }).dropna()
    rc = df.iloc[-30:].corr()
    avg = (rc.loc["SPY", "TLT"] + rc.loc["SPY", "GLD"]) / 2
    return max(0.0, min(100.0, (0.5 - avg) * 100))


def test_all_feeds_present_matches_original_formula(patched):
    """With every feed present the score equals the original 0.5/0.3/0.2 blend."""
    feeds = patched
    vix_score = _expected_vix(feeds)
    corr_score = _expected_corr(feeds)
    expected = SAFE_PROB * 100 * 0.5 + vix_score * 0.3 + corr_score * 0.2

    res = MacroGate().evaluate()
    assert res["components_used"] == ["hmm", "vix", "corr"]
    assert res["gate_score"] == pytest.approx(expected, abs=1e-6)


def test_missing_vix3m_drops_vix_component_and_renormalises(patched, monkeypatch):
    """A missing VIX feed drops the VIX component; weights renormalise over HMM+corr."""
    feeds = patched
    feeds["^VIX3M"] = pd.DataFrame()                  # download hiccup / pre-inception
    corr_score = _expected_corr(feeds)
    expected = (SAFE_PROB * 100 * 0.5 + corr_score * 0.2) / (0.5 + 0.2)

    res = MacroGate().evaluate()
    assert res["components_used"] == ["hmm", "corr"]
    assert "vix_ratio" not in res
    assert res["gate_score"] == pytest.approx(expected, abs=1e-6)


def test_missing_gld_drops_corr_component_and_renormalises(patched):
    """A missing safe-haven feed drops the correlation component (HMM+VIX remain)."""
    feeds = patched
    feeds["GLD"] = pd.DataFrame()
    vix_score = _expected_vix(feeds)
    expected = (SAFE_PROB * 100 * 0.5 + vix_score * 0.3) / (0.5 + 0.3)

    res = MacroGate().evaluate()
    assert res["components_used"] == ["hmm", "vix"]
    assert "avg_safe_haven_corr" not in res
    assert res["gate_score"] == pytest.approx(expected, abs=1e-6)


def test_only_spy_available_falls_back_to_hmm_only(patched):
    """With only SPY, the gate is the pure HMM score (weight renormalises to 1.0),
    NOT the old flat-50 collapse."""
    feeds = patched
    for sym in ("^VIX", "^VIX3M", "TLT", "GLD"):
        feeds[sym] = pd.DataFrame()

    res = MacroGate().evaluate()
    assert res["components_used"] == ["hmm"]
    assert res["gate_score"] == pytest.approx(SAFE_PROB * 100, abs=1e-6)


def test_no_spy_returns_neutral_fallback(patched):
    """SPY (the mandatory core) missing -> neutral 50, no components."""
    feeds = patched
    feeds["SPY"] = pd.DataFrame()

    res = MacroGate().evaluate()
    assert res["gate_score"] == 50.0
    assert res["components_used"] == []
