"""Tests for the HYBRID intraday adapter (2026-06-26) — the merge of the two Forex
implementations (daily trend-regime gate + intraday momentum confluence) reused for
FX and Crypto, plus the account-level CRYPTO validation profile.

Covers: the regime gate (driver ADX), the daily skeleton, intraday confluence/veto,
graceful degradation when intraday data is absent (replay), fault tolerance, and the
CRYPTO profile routing (Crypto follows Forex's account-level principles).
"""
from decimal import Decimal

import pandas as pd
import pytest

from core.context import AccountContext, Candidate, NullTaxPolicy
from core.risk import AtrSizing, FrictionSizing
from adapters.asset_intraday import HybridIntradayAdapter
from backtest.validation import profile_for_book, PROFILES
from layers.data_loader import to_yf_symbol


def _daily(close, ema20, ema50, adx):
    """Daily technical-features frame the hybrid's daily skeleton reads (last row)."""
    return pd.DataFrame({
        "Open": [close], "High": [close], "Low": [close], "Close": [close],
        "Volume": [0], "EMA_20": [ema20], "EMA_50": [ema50], "ADX_14": [adx],
        "RSI_14": [55.0], "ATRr_14": [0.005],
    })


def _intraday(side):
    """Two-row 5m frame producing a fresh MACD cross in the given direction."""
    if side == "BUY":
        macd_prev, macd_last, ema200, close, rsi = -0.1, 0.1, 1.00, 1.12, 55.0
    else:  # SELL
        macd_prev, macd_last, ema200, close, rsi = 0.1, -0.1, 1.20, 1.12, 45.0
    return pd.DataFrame({
        "Open": [close, close], "High": [close, close], "Low": [close, close],
        "Close": [close, close], "Volume": [0, 0],
        "MACD_12_26_9": [macd_prev, macd_last], "MACDs_12_26_9": [0.0, 0.0],
        "RSI_14": [rsi, rsi], "EMA_200": [ema200, ema200],
    })


# --------------------------------------------------------------------------- #
# Layer 1: regime gate
# --------------------------------------------------------------------------- #
def test_fx_regime_gate_scales_with_dxy_adx(monkeypatch):
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features",
                        lambda s, lookback_days=400: _daily(100.0, 101.0, 100.0, 40.0))
    adapter = HybridIntradayAdapter(asset_class="FX", regime_symbol="DX-Y.NYB")
    assert adapter.macro_gate() == pytest.approx(60.0)            # 20 + ADX(40)
    assert adapter._last_gate_result["driver"] == "DX-Y.NYB"


def test_crypto_regime_gate_uses_bitcoin(monkeypatch):
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features",
                        lambda s, lookback_days=400: _daily(60000, 61000, 60000, 35.0))
    adapter = HybridIntradayAdapter(asset_class="CRYPTO", regime_symbol="BTC-USD")
    assert adapter.macro_gate() == pytest.approx(55.0)           # 20 + ADX(35)
    assert adapter._last_gate_result["driver"] == "BTC-USD"


def test_regime_gate_falls_back_neutral_on_failure(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("feed down")
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features", boom)
    adapter = HybridIntradayAdapter(asset_class="CRYPTO", regime_symbol="BTC-USD")
    assert adapter.macro_gate() == 50.0                          # fault-tolerant


# --------------------------------------------------------------------------- #
# Layer 2: daily skeleton + intraday confluence/veto/degradation
# --------------------------------------------------------------------------- #
def test_degrades_to_daily_trend_when_no_intraday(monkeypatch):
    """Replay/historical: no intraday data => trade the daily skeleton alone."""
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features",
                        lambda s, lookback_days=500: _daily(61000, 60500, 60000, 30.0))
    monkeypatch.setattr("adapters.asset_intraday.get_intraday_features",
                        lambda *a, **k: pd.DataFrame())          # empty => unavailable
    cands = HybridIntradayAdapter(asset_class="CRYPTO").scan(["BTC-USD"])
    assert len(cands) == 1
    c = cands[0]
    assert c.side == "BUY" and c.asset_class == "CRYPTO"
    assert c.meta["intraday_confirmed"] is False
    assert c.quant_score == pytest.approx(70.0)                  # 40 + ADX(30), no bonus


def test_intraday_confluence_boosts_conviction(monkeypatch):
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features",
                        lambda s, lookback_days=500: _daily(1.12, 1.11, 1.10, 30.0))
    monkeypatch.setattr("adapters.asset_intraday.get_intraday_features",
                        lambda *a, **k: _intraday("BUY"))
    cands = HybridIntradayAdapter(asset_class="CRYPTO").scan(["BTC-USD"])
    assert len(cands) == 1
    assert cands[0].meta["intraday_confirmed"] is True
    assert cands[0].quant_score == pytest.approx(75.0)          # 70 + 5 confluence bonus


def test_intraday_opposing_momentum_vetoes_trade(monkeypatch):
    """Daily uptrend but a fresh intraday SELL cross => no trade (MTF veto)."""
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features",
                        lambda s, lookback_days=500: _daily(1.12, 1.11, 1.10, 30.0))
    monkeypatch.setattr("adapters.asset_intraday.get_intraday_features",
                        lambda *a, **k: _intraday("SELL"))
    assert HybridIntradayAdapter(asset_class="CRYPTO").scan(["BTC-USD"]) == []


def test_sits_out_when_no_daily_trend(monkeypatch):
    """ADX below the floor => ranging => no candidate even with aligned EMAs."""
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features",
                        lambda s, lookback_days=500: _daily(1.12, 1.11, 1.10, 10.0))
    monkeypatch.setattr("adapters.asset_intraday.get_intraday_features",
                        lambda *a, **k: pd.DataFrame())
    assert HybridIntradayAdapter(asset_class="CRYPTO").scan(["BTC-USD"]) == []


def test_scan_is_foolproof_against_bad_data(monkeypatch):
    """A symbol that explodes inside the scan must be skipped, not crash the loop."""
    def boom(*a, **k):
        raise ValueError("corrupt frame")
    monkeypatch.setattr("adapters.asset_intraday.get_technical_features", boom)
    assert HybridIntradayAdapter(asset_class="CRYPTO").scan(["BTC-USD", "ETH-USD"]) == []


# --------------------------------------------------------------------------- #
# Validation: Crypto follows Forex's account-level principles
# --------------------------------------------------------------------------- #
def _book(allowed):
    return AccountContext("b", "MARGIN", "IBKR", "U", allowed,
                          NullTaxPolicy(), AtrSizing())


def test_crypto_routes_to_account_level_profile():
    prof = profile_for_book(_book({"CRYPTO"}))
    assert prof.name == "CRYPTO"
    assert prof.account_level is True                            # win/RR/Sortino logged, not gated
    assert prof.min_profit_factor and prof.min_mar              # gated like FOREX
    assert prof.max_drawdown_pct == 35.0                        # wider crypto DD tolerance


def test_fx_still_routes_to_forex_profile():
    assert profile_for_book(_book({"FX"})).name == "FOREX"


def test_crypto_profile_mirrors_forex_gating_shape():
    """Same account-level shape as FOREX (PF + MAR gated; style metrics logged)."""
    crypto, forex = PROFILES["CRYPTO"], PROFILES["FOREX"]
    assert crypto.account_level == forex.account_level is True
    assert (crypto.min_profit_factor is not None) and (crypto.min_mar is not None)


# --------------------------------------------------------------------------- #
# Sizing: Isaak's friction-relative brackets (net-entry based)
# --------------------------------------------------------------------------- #
def test_friction_brackets_hang_off_net_entry_long():
    """LONG: net entry = price*(1+friction); TP/SL measured from that net entry."""
    ctx = _book({"CRYPTO"})
    ctx.nav = Decimal("5000")
    sizing = FrictionSizing(risk_pct=2.0, leverage=2.0, stop_pct=0.02,
                            take_pct=0.04, friction_buffer=0.001)
    order = sizing.size(Candidate("BTC-USD", "CRYPTO", 80.0, Decimal("100.00"),
                                  side="BUY"), ctx, 80.0)
    # net_entry = 100*(1.001)=100.1; stop=100.1*0.98=98.098; take=100.1*1.04=104.104
    assert order.meta["net_entry"] == "100.10"
    assert order.stop_loss == Decimal("98.10")        # below entry (long), off net entry
    assert order.take_profit == Decimal("104.10")     # above entry, off net entry
    assert order.side == "BUY" and order.quantity > 0


def test_friction_brackets_invert_for_short():
    """SHORT: net entry = price*(1-friction); stop ABOVE, take BELOW."""
    ctx = _book({"FX"})
    ctx.nav = Decimal("5000")
    sizing = FrictionSizing(risk_pct=1.0, leverage=5.0, stop_pct=0.002,
                            take_pct=0.004, friction_buffer=0.0001)
    order = sizing.size(Candidate("EURUSD", "FX", 80.0, Decimal("1.1000"),
                                  side="SELL"), ctx, 80.0)
    assert order.side == "SELL"
    assert order.stop_loss > order.price              # short stop is ABOVE
    assert order.take_profit < order.price            # short take is BELOW
    # FX precision preserved at 4 dp (not collapsed to 0.01).
    assert order.stop_loss.as_tuple().exponent == -4


# --------------------------------------------------------------------------- #
# Data: spot-FX yfinance symbol normalization (so FX runs without the live feed)
# --------------------------------------------------------------------------- #
def test_fx_pairs_map_to_yfinance_suffix():
    assert to_yf_symbol("EURUSD") == "EURUSD=X"
    assert to_yf_symbol("usdjpy") == "USDJPY=X"            # case-insensitive


def test_non_fx_symbols_pass_through_unchanged():
    for s in ("BTC-USD", "ETH-USD", "SPY", "VWRL.L", "^VIX", "DX-Y.NYB"):
        assert to_yf_symbol(s) == s
