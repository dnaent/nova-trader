from decimal import Decimal
import core.risk as risk
from core.context import AccountContext, NullTaxPolicy, RiskGuardrails, Candidate
from core.risk import NavPctSizing, AtrSizing, gate_capacity

def test_guardrails_parsing():
    ctx = AccountContext("test", "ISA", "IBKR", "U1", set(), NullTaxPolicy(), NavPctSizing(), RiskGuardrails(
        max_drawdown_pct=10.0,
        daily_loss_cap_pct=5.0,
        max_concurrent_positions=8,
        max_correlation=0.7
    ))
    assert ctx.guardrails.max_drawdown_pct == 10.0
    assert ctx.guardrails.max_concurrent_positions == 8
    assert ctx.guardrails.max_correlation == 0.7

def test_gate_capacity():
    assert gate_capacity(75.0) == Decimal("1.00")
    assert gate_capacity(30.0) == Decimal("0.00")
    assert gate_capacity(55.0) == Decimal("0.50")

def _fx_ctx(nav):
    ctx = AccountContext("ibkr_forex_margin", "MARGIN", "IBKR", "U_FX",
                         {"FX"}, NullTaxPolicy(), AtrSizing())
    ctx.nav = Decimal(str(nav))
    return ctx

def test_atr_sizing_caps_notional_at_leverage(monkeypatch):
    """A tiny ATR would size a huge position; the leverage cap must bound the
    notional exposure to NAV * leverage (here 5:1)."""
    monkeypatch.setattr(risk, "calculate_atr", lambda *a, **k: Decimal("0.001"))
    sizing = AtrSizing(risk_pct=2.0, leverage=5.0, stop_atr_multiplier=2.0)
    ctx = _fx_ctx(5000)
    cand = Candidate("EURUSD=X", "FX", 90.0, Decimal("1.10"))
    order = sizing.size(cand, ctx, gate_score=75.0)   # capacity = 1.0
    assert order.notional <= ctx.nav * Decimal("5")   # <= 25000
    assert order.notional > Decimal("0")              # cap engaged, not zeroed

def test_atr_sizing_default_leverage_caps_at_nav(monkeypatch):
    """Default leverage 1.0 must keep notional within NAV (no implicit margin)."""
    monkeypatch.setattr(risk, "calculate_atr", lambda *a, **k: Decimal("0.001"))
    sizing = AtrSizing(risk_pct=2.0, leverage=1.0, stop_atr_multiplier=2.0)
    ctx = _fx_ctx(5000)
    cand = Candidate("SPY", "EQUITY", 90.0, Decimal("100"))
    order = sizing.size(cand, ctx, gate_score=75.0)
    assert order.notional <= ctx.nav

def test_atr_sizing_zero_atr_returns_zero_qty(monkeypatch):
    """If ATR can't be computed, size to zero rather than guess."""
    monkeypatch.setattr(risk, "calculate_atr", lambda *a, **k: Decimal("0"))
    order = AtrSizing().size(Candidate("X", "EQUITY", 90.0, Decimal("100")), _fx_ctx(5000), 75.0)
    assert order.quantity == Decimal("0")

def test_calculate_atr(monkeypatch):
    import pandas as pd
    n = 30
    df = pd.DataFrame({"High": [101.0] * n, "Low": [99.0] * n, "Close": [100.0] * n})
    monkeypatch.setattr(risk, "get_daily_data", lambda *a, **k: df)
    atr = risk.calculate_atr("X")
    assert atr > Decimal("0")                    # ~2.0 true range

def test_check_correlation_no_open_symbols():
    from core.risk import check_correlation
    assert check_correlation("X", [], 0.8) == (False, "")

def test_check_correlation_flags_highly_correlated(monkeypatch):
    import pandas as pd, numpy as np
    from core.risk import check_correlation
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    series = pd.Series(np.linspace(1.0, 2.0, 60) + np.random.RandomState(0).normal(0, 0.01, 60),
                       index=idx)
    monkeypatch.setattr(risk, "get_daily_data",
                        lambda *a, **k: pd.DataFrame({"Close": series.copy()}))
    flagged, reason = check_correlation("X", ["Y"], 0.8)   # both return the same series
    assert flagged is True and "Y" in reason


# --------------------------------------------------------------------------- #
# UK CGT edge branches
# --------------------------------------------------------------------------- #
def test_uk_cgt_higher_rate_and_zero_gain():
    from tax.uk_cgt import UkCgtPolicy
    pol = UkCgtPolicy(higher_rate=True)
    out = pol.estimate(Decimal("5000"))
    assert out["taxable"] == Decimal("2000")
    assert out["tax"] == Decimal("480.00")        # 2000 * 24%
    assert pol.estimate(Decimal("-100"))["tax"] == Decimal("0")   # losses: no tax
    pol.consume(Decimal("1000"))                   # uses part of the allowance
    assert pol.allowance_remaining == Decimal("2000")
