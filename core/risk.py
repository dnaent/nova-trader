from __future__ import annotations
from decimal import Decimal, ROUND_DOWN
from typing import Protocol, runtime_checkable

from core.context import AccountContext, Candidate, Order


def gate_capacity(gate_score: float) -> Decimal:
    """Macro-gate capacity factor: continuous scaling between 40 and 70."""
    if gate_score >= 70:
        return Decimal("1.0")
    if gate_score <= 40:
        return Decimal("0.0")
    
    capacity = (gate_score - 40.0) / 30.0
    return Decimal(str(capacity)).quantize(Decimal("0.01"))


class NavPctSizing:
    """
    NAV-based sizing scaled by the macro gate (replaces the old £100 budget logic).
    Allocation = NAV * max_per_position_pct% * capacity(gate). Whole shares only
    in Phase 1 (fractional support is a later refinement). Placeholder brackets.
    """
    def __init__(self, max_per_position_pct: float = 8.0, leverage: float = 1.0,
                 unit: str = "shares", stop_pct: float = 0.05, take_pct: float = 0.10):
        self.max_per_position_pct = Decimal(str(max_per_position_pct))
        self.leverage = Decimal(str(leverage))
        self.unit = unit
        self.stop_pct = Decimal(str(stop_pct))
        self.take_pct = Decimal(str(take_pct))

    def size(self, candidate: Candidate, ctx: AccountContext, gate_score: float) -> Order:
        capacity = gate_capacity(gate_score)
        allocation = (ctx.nav * (self.max_per_position_pct / Decimal("100"))
                      * capacity * self.leverage)
        price = Decimal(candidate.price)
        qty = (allocation / price).to_integral_value(rounding=ROUND_DOWN) if price > 0 else Decimal("0")
        notional = (qty * price).quantize(Decimal("0.01"))
        return Order(
            book_id=ctx.book_id,
            account_id=ctx.ibkr_account_id,
            symbol=candidate.symbol,
            side="BUY",
            quantity=qty,
            price=price,
            notional=notional,
            stop_loss=(price * (Decimal("1") - self.stop_pct)).quantize(Decimal("0.01")),
            take_profit=(price * (Decimal("1") + self.take_pct)).quantize(Decimal("0.01")),
            meta={"capacity_factor": str(capacity)},
        )
