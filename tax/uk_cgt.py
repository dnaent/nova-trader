from __future__ import annotations
from decimal import Decimal

class UkCgtPolicy:
    """
    Simplified UK CGT estimator for GIA/taxable books (2025/26).
    Annual exempt amount: £3,000. Rates on shares/other assets: 18% basic / 24% higher.

    NOTE: This is a per-disposal *estimate* using current remaining allowance and
    does NOT persist year-scoped tracking — that belongs in a later phase alongside
    the ledger. estimate() is non-mutating; call consume() when a disposal is booked.
    """
    applicable = True
    ANNUAL_EXEMPT_AMOUNT = Decimal("3000")

    def __init__(self, higher_rate: bool = False):
        self.higher_rate = higher_rate
        self.rate = Decimal("0.24") if higher_rate else Decimal("0.18")
        self.allowance_remaining = self.ANNUAL_EXEMPT_AMOUNT

    def estimate(self, gain: Decimal) -> dict:
        gain = Decimal(gain)
        if gain <= 0:
            return {"applicable": True, "taxable": Decimal("0"), "tax": Decimal("0"),
                    "rate": self.rate}
        applied = min(gain, self.allowance_remaining)
        taxable = gain - applied
        tax = (taxable * self.rate).quantize(Decimal("0.01"))
        return {"applicable": True, "gain": gain, "allowance_applied": applied,
                "taxable": taxable, "rate": self.rate, "tax": tax}

    def consume(self, gain: Decimal) -> None:
        """Record that a disposal used part of the annual allowance."""
        self.allowance_remaining = max(Decimal("0"),
                                       self.allowance_remaining - max(Decimal("0"), Decimal(gain)))
