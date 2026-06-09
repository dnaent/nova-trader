from decimal import Decimal
from core.context import AccountContext, NullTaxPolicy, RiskGuardrails
from core.risk import NavPctSizing, gate_capacity

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
