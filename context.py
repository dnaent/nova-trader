"""
Nova Engine — core/context.py

The book abstractions that make the engine portfolio-aware and asset-agnostic.
A "book" = (account wrapper x asset class x broker x tax policy). The engine
reads a portfolio manifest, builds an AccountContext per book, and routes
candidates to the right book with the right rules.

Implemented now: equity/ETF concretes + NullTaxPolicy + UkCgtPolicy + NavPctSizing.
Forex later is a new AssetAdapter, not a rewrite of anything here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_DOWN
from typing import Protocol, runtime_checkable, Optional, Iterable


# --------------------------------------------------------------------------- #
# Value objects
# --------------------------------------------------------------------------- #
@dataclass
class Candidate:
    """A ranked trade idea emerging from Layer 2 (the deterministic scanner)."""
    symbol: str
    asset_class: str            # "EQUITY" | "ETF" | (future) "FX"
    quant_score: float          # 0-100, from the scanner
    price: Decimal              # current price, used for sizing
    meta: dict = field(default_factory=dict)


@dataclass
class Order:
    """A sized, ready-to-route order. Brackets are placeholders in Phase 1."""
    book_id: str
    account_id: str
    symbol: str
    side: str                   # "BUY" | "SELL"
    quantity: Decimal
    price: Decimal
    notional: Decimal
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    meta: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Policies
# --------------------------------------------------------------------------- #
@runtime_checkable
class TaxPolicy(Protocol):
    """Estimates tax on a realised gain. Null inside ISA/SIPP; CGT in GIA only."""
    applicable: bool
    def estimate(self, gain: Decimal) -> dict: ...


class NullTaxPolicy:
    """Used inside ISA and SIPP — gains are tax-free / tax-sheltered."""
    applicable = False

    def estimate(self, gain: Decimal) -> dict:
        return {"applicable": False, "tax": Decimal("0"), "note": "tax-free wrapper"}


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


@runtime_checkable
class SizingPolicy(Protocol):
    def size(self, candidate: Candidate, ctx: "AccountContext", gate_score: float) -> Order: ...


def gate_capacity(gate_score: float) -> Decimal:
    """Macro-gate capacity factor: >=70 full, 40-70 scaled, <40 zero."""
    if gate_score >= 70:
        return Decimal("1.0")
    if gate_score >= 40:
        return Decimal("0.6")
    return Decimal("0.0")


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

    def size(self, candidate: Candidate, ctx: "AccountContext", gate_score: float) -> Order:
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


# --------------------------------------------------------------------------- #
# Adapter protocols (implemented per asset class / per broker)
# --------------------------------------------------------------------------- #
@runtime_checkable
class AssetAdapter(Protocol):
    asset_class: str
    handles: set                # asset classes this adapter covers, e.g. {"EQUITY","ETF"}
    def macro_gate(self) -> float: ...                       # Layer 1, 0-100
    def scan(self, universe: Iterable[str]) -> list: ...     # Layer 2 -> list[Candidate]
    def auditor_prompt(self, candidate: Candidate) -> str: ...  # Layer 3 prompt


@runtime_checkable
class BrokerAdapter(Protocol):
    def refresh_nav(self, ctx: "AccountContext") -> Decimal: ...
    def positions(self, ctx: "AccountContext") -> list: ...
    def place(self, order: Order, ctx: "AccountContext") -> dict: ...


# --------------------------------------------------------------------------- #
# The book
# --------------------------------------------------------------------------- #
@dataclass
class AccountContext:
    book_id: str
    wrapper: str                # "ISA" | "SIPP" | "GIA" | "MARGIN"
    broker: str                 # "IBKR"
    ibkr_account_id: str
    allowed_assets: set         # hard permission set, enforced by the engine
    tax_policy: TaxPolicy
    sizing: SizingPolicy
    nav: Decimal = Decimal("0")


# --------------------------------------------------------------------------- #
# Manifest loader (portfolio.yaml -> list[AccountContext])
# --------------------------------------------------------------------------- #
def _build_tax_policy(spec) -> TaxPolicy:
    if not spec or spec == "null":
        return NullTaxPolicy()
    if spec == "uk_cgt" or (isinstance(spec, dict) and spec.get("type") == "uk_cgt"):
        higher = spec.get("higher_rate", False) if isinstance(spec, dict) else False
        return UkCgtPolicy(higher_rate=higher)
    raise ValueError(f"Unknown tax_policy: {spec!r}")


def _build_sizing(spec: dict) -> SizingPolicy:
    spec = spec or {}
    return NavPctSizing(
        max_per_position_pct=spec.get("max_per_position_pct", 8.0),
        leverage=spec.get("leverage", 1.0),
        unit=spec.get("unit", "shares"),
    )


def load_books(manifest_path: str) -> list[AccountContext]:
    """Read portfolio.yaml and build one AccountContext per book."""
    import yaml  # imported lazily so the demo runs without pyyaml installed
    with open(manifest_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    books = []
    for b in data.get("books", []):
        books.append(AccountContext(
            book_id=b["book_id"],
            wrapper=b["wrapper"],
            broker=b["broker"],
            ibkr_account_id=b["ibkr_account_id"],
            allowed_assets=set(b["allowed_assets"]),
            tax_policy=_build_tax_policy(b.get("tax_policy")),
            sizing=_build_sizing(b.get("sizing")),
        ))
    return books
