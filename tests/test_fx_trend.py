"""Tests for the FX trend-following redesign (2026-06-16) and the short-side
plumbing it required. Equities stay long-only; these cover the new FX paths."""
from decimal import Decimal

import pandas as pd
import pytest

from core.context import AccountContext, Candidate, Order, NullTaxPolicy
from core.engine import Engine, EngineConfig
from core.ledger import Ledger
from core.risk import AtrSizing
from adapters.asset_fx import FxAdapter, ADX_MIN
from adapters.broker_ibkr import IBKRAdapter
from layers.analyst import StubAuditor
import layers.data_loader as dl


def _ta_frame(close, ema20, ema50, adx):
    """Minimal technical-features frame the FX adapter reads (last row used)."""
    return pd.DataFrame({
        "Open": [close], "High": [close], "Low": [close], "Close": [close],
        "Volume": [0], "EMA_20": [ema20], "EMA_50": [ema50], "ADX_14": [adx],
        "RSI_14": [55.0], "ATRr_14": [0.005],
    })


def _fx_book(book_id="ibkr_forex_margin", sizing=None):
    return AccountContext(book_id, "MARGIN", "IBKR", "U_fx", {"FX"},
                          NullTaxPolicy(), sizing or AtrSizing(leverage=5.0))


# --------------------------------------------------------------------------- #
# Scanner: trend direction + chop filter
# --------------------------------------------------------------------------- #
def test_fx_scanner_emits_long_in_uptrend(monkeypatch):
    monkeypatch.setattr("adapters.asset_fx.get_technical_features",
                        lambda s, lookback_days=500: _ta_frame(1.12, 1.11, 1.10, 30.0))
    cands = FxAdapter().scan(["EURUSD=X"])
    assert len(cands) == 1
    assert cands[0].side == "BUY"
    assert cands[0].asset_class == "FX"
    assert cands[0].quant_score == pytest.approx(70.0)        # 40 + ADX(30)
    assert cands[0].meta["markers"]                            # 32-marker snapshot attached


def test_fx_scanner_emits_short_in_downtrend(monkeypatch):
    monkeypatch.setattr("adapters.asset_fx.get_technical_features",
                        lambda s, lookback_days=500: _ta_frame(1.08, 1.09, 1.10, 35.0))
    cands = FxAdapter().scan(["EURUSD=X"])
    assert len(cands) == 1 and cands[0].side == "SELL"


def test_fx_scanner_sits_out_chop(monkeypatch):
    # ADX below the trend floor -> no candidate even though EMAs are aligned.
    monkeypatch.setattr("adapters.asset_fx.get_technical_features",
                        lambda s, lookback_days=500: _ta_frame(1.12, 1.11, 1.10, ADX_MIN - 5))
    assert FxAdapter().scan(["EURUSD=X"]) == []


def test_fx_macro_gate_scales_with_dxy_adx(monkeypatch):
    monkeypatch.setattr("adapters.asset_fx.get_technical_features",
                        lambda s, lookback_days=400: _ta_frame(100.0, 101.0, 100.0, 40.0))
    gate = FxAdapter().macro_gate()
    assert gate == pytest.approx(60.0)                         # 20 + ADX(40)
    # Choppy USD -> gate falls below the global floor (book holds cash).
    monkeypatch.setattr("adapters.asset_fx.get_technical_features",
                        lambda s, lookback_days=400: _ta_frame(100.0, 100.0, 100.0, 12.0))
    assert FxAdapter().macro_gate() < 40.0


# --------------------------------------------------------------------------- #
# Sizing: short brackets invert
# --------------------------------------------------------------------------- #
def test_atr_sizing_short_brackets(monkeypatch):
    monkeypatch.setattr("core.risk.calculate_atr", lambda s: Decimal("0.0050"))
    ctx = _fx_book()
    ctx.nav = Decimal("5000")
    short = AtrSizing(leverage=5.0).size(
        Candidate("EURUSD=X", "FX", 80.0, Decimal("1.1000"), side="SELL"), ctx, 80.0)
    long = AtrSizing(leverage=5.0).size(
        Candidate("EURUSD=X", "FX", 80.0, Decimal("1.1000"), side="BUY"), ctx, 80.0)
    assert short.side == "SELL"
    # Fixed ATR brackets, inverted for the short side; trailing OFF (fixed take
    # captures the trend edge — the trailing-only variant destroyed PF).
    assert short.stop_loss > short.price and short.take_profit < short.price   # inverted
    assert long.stop_loss < long.price and long.take_profit > long.price       # normal
    assert short.trailing_atr is None and long.trailing_atr is None
    # FX precision preserved (4 dp), not collapsed to 0.01.
    assert short.stop_loss == Decimal("1.1100")               # 1.10 + 2*0.005


def test_trailing_stop_ratchets_long_and_exits(monkeypatch):
    """A long's trailing stop ratchets UP as price rises, then exits on reversal."""
    monkeypatch.setattr("core.risk.calculate_atr", lambda s: Decimal("0.0050"))
    led = Ledger(":memory:")
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U_fx": 5000})
    broker.connect()
    ctx = _fx_book()
    led.record_trade(ctx.book_id, "U_fx", "EURUSD=X", "BUY", Decimal("1000"),
                     Decimal("1.10"), Decimal("1100"), stop_loss=Decimal("1.09"),
                     trailing_atr=Decimal("2.0"))
    broker.place(Order(ctx.book_id, "U_fx", "EURUSD=X", "BUY", Decimal("1000"),
                       Decimal("1.10"), Decimal("1100")), ctx)
    cfg = EngineConfig(universe=["EURUSD=X"], gate_min=40, exec_threshold=50)
    engine = Engine([ctx], [], broker, StubAuditor(), led, cfg)
    # Price rises to 1.12 -> trailing stop ratchets to 1.12 - 2*0.005 = 1.11 (no exit).
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("1.12"))
    engine._evaluate_exits(ctx)
    pos = led.open_trades(ctx.book_id)
    assert pos and pos[0]["stop_loss"] == pytest.approx(1.11)   # ratcheted up
    # Price reverses to 1.105 (< 1.11 trailed stop) -> exit with a locked-in gain.
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("1.105"))
    engine._evaluate_exits(ctx)
    assert led.open_trades(ctx.book_id) == []
    assert led._closed_pnls(ctx.book_id)[0] > 0                 # exited above entry
    led.close()


def test_circuit_breaker_pauses_entries_after_streak():
    """After N consecutive losses the breaker pauses new entries for a cooldown."""
    from core.context import RiskGuardrails
    led = Ledger(":memory:")
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U_fx": 5000})
    broker.connect()
    ctx = _fx_book()
    ctx.guardrails = RiskGuardrails(circuit_breaker_losses=3, circuit_breaker_cooldown=5)
    # Three closed losers in a row.
    for _ in range(3):
        tid = led.record_trade(ctx.book_id, "U_fx", "EURUSD=X", "BUY", Decimal("1"),
                               Decimal("1.10"), Decimal("1.10"))
        led.close_trade(tid, Decimal("1.09"), Decimal("-0.01"))
    cfg = EngineConfig(universe=["EURUSD=X"], gate_min=40, exec_threshold=50)
    engine = Engine([ctx], [], broker, StubAuditor(), led, cfg)
    assert engine._circuit_broken(ctx) is True                 # trips on the 3-loss streak
    assert engine._cb_cooldown[ctx.book_id] == 5
    # A subsequent winning trade clears the streak once the cooldown elapses.
    engine._cb_cooldown[ctx.book_id] = 0
    tid = led.record_trade(ctx.book_id, "U_fx", "EURUSD=X", "BUY", Decimal("1"),
                           Decimal("1.10"), Decimal("1.10"))
    led.close_trade(tid, Decimal("1.12"), Decimal("0.02"))
    assert engine._circuit_broken(ctx) is False                # streak broken by the win
    led.close()


def test_circuit_breaker_does_not_deadlock_after_cooldown():
    """Regression: after a trip + cooldown with NO new trades, the breaker must NOT
    re-trip on the SAME old streak (which froze the book — 121 trips, 26 trades)."""
    from core.context import RiskGuardrails
    led = Ledger(":memory:")
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U_fx": 5000})
    broker.connect()
    ctx = _fx_book()
    ctx.guardrails = RiskGuardrails(circuit_breaker_losses=3, circuit_breaker_cooldown=2)
    for _ in range(3):
        tid = led.record_trade(ctx.book_id, "U_fx", "EURUSD=X", "BUY", Decimal("1"),
                               Decimal("1.10"), Decimal("1.10"))
        led.close_trade(tid, Decimal("1.09"), Decimal("-0.01"))
    cfg = EngineConfig(universe=["EURUSD=X"], gate_min=40, exec_threshold=50)
    engine = Engine([ctx], [], broker, StubAuditor(), led, cfg)
    assert engine._circuit_broken(ctx) is True        # trips, cooldown=2
    assert engine._circuit_broken(ctx) is True         # cooldown 2->1
    assert engine._circuit_broken(ctx) is True         # cooldown 1->0 (still serving)
    # Cooldown now elapsed and NO new trades closed: must NOT re-trip on the old streak.
    assert engine._circuit_broken(ctx) is False
    led.close()


def test_circuit_breaker_off_for_equities():
    """No circuit_breaker_losses (equities) => breaker never trips."""
    led = Ledger(":memory:")
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U": 5000})
    broker.connect()
    ctx = AccountContext("isa", "ISA", "IBKR", "U", {"EQUITY"}, NullTaxPolicy(), AtrSizing())
    for _ in range(10):
        tid = led.record_trade(ctx.book_id, "U", "SPY", "BUY", Decimal("1"),
                               Decimal("100"), Decimal("100"))
        led.close_trade(tid, Decimal("99"), Decimal("-1"))
    cfg = EngineConfig(universe=["SPY"], gate_min=40, exec_threshold=50)
    engine = Engine([ctx], [], broker, StubAuditor(), led, cfg)
    assert engine._circuit_broken(ctx) is False                # off by default
    led.close()


# --------------------------------------------------------------------------- #
# Engine: short exits + PnL sign
# --------------------------------------------------------------------------- #
def _short_engine(led):
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U_fx": 5000})
    broker.connect()
    ctx = _fx_book()
    # open a SHORT: entry 1.10, stop 1.12 (above), take 1.06 (below)
    led.record_trade(ctx.book_id, "U_fx", "EURUSD=X", "SELL", Decimal("1000"),
                     Decimal("1.10"), Decimal("1100"), stop_loss=Decimal("1.12"),
                     take_profit=Decimal("1.06"))
    broker.place(Order(ctx.book_id, "U_fx", "EURUSD=X", "SELL", Decimal("1000"),
                       Decimal("1.10"), Decimal("1100")), ctx)
    cfg = EngineConfig(universe=["EURUSD=X"], gate_min=40, exec_threshold=50)
    return Engine([ctx], [], broker, StubAuditor(), led, cfg), ctx


def test_engine_closes_short_at_stop_with_loss(monkeypatch):
    led = Ledger(":memory:")
    engine, ctx = _short_engine(led)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("1.13"))  # rose past stop
    engine._evaluate_exits(ctx)
    assert led.open_trades(ctx.book_id) == []                  # closed
    pnls = led._closed_pnls(ctx.book_id)
    assert len(pnls) == 1 and pnls[0] < 0                      # short loses when price rises
    led.close()


def test_engine_closes_short_at_take_with_profit(monkeypatch):
    led = Ledger(":memory:")
    engine, ctx = _short_engine(led)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("1.05"))  # fell past take
    engine._evaluate_exits(ctx)
    assert led.open_trades(ctx.book_id) == []
    pnls = led._closed_pnls(ctx.book_id)
    assert len(pnls) == 1 and pnls[0] > 0                      # short profits when price falls
    # PnL = (entry - take) * qty = (1.10 - 1.06) * 1000 = 40
    assert pnls[0] == pytest.approx(40.0)
    led.close()
