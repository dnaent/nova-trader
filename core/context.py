"""
Nova Engine — core/context.py

The book abstractions that make the engine portfolio-aware and asset-agnostic.
A "book" = (account wrapper x asset class x broker x tax policy). The engine
reads a portfolio manifest, builds an AccountContext per book, and routes
candidates to the right book with the right rules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
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

@dataclass
class RiskGuardrails:
    """Book-level safety limits."""
    max_concurrent_positions: int = 10
    max_drawdown_pct: float = 15.0
    daily_loss_cap_pct: float = 3.0
    max_correlation: float = 0.8

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

@runtime_checkable
class SizingPolicy(Protocol):
    def size(self, candidate: Candidate, ctx: "AccountContext", gate_score: float) -> Order: ...

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
    guardrails: RiskGuardrails = field(default_factory=RiskGuardrails)
    nav: Decimal = Decimal("0")

# --------------------------------------------------------------------------- #
# Manifest loader (portfolio.yaml -> list[AccountContext])
# --------------------------------------------------------------------------- #
def _build_tax_policy(spec) -> TaxPolicy:
    if not spec or spec == "null":
        return NullTaxPolicy()
    if spec == "uk_cgt" or (isinstance(spec, dict) and spec.get("type") == "uk_cgt"):
        from tax.uk_cgt import UkCgtPolicy
        higher = spec.get("higher_rate", False) if isinstance(spec, dict) else False
        return UkCgtPolicy(higher_rate=higher)
    raise ValueError(f"Unknown tax_policy: {spec!r}")

def _build_sizing(spec: dict) -> SizingPolicy:
    from core.risk import NavPctSizing
    spec = spec or {}
    return NavPctSizing(
        max_per_position_pct=spec.get("max_per_position_pct", 8.0),
        leverage=spec.get("leverage", 1.0),
        unit=spec.get("unit", "shares"),
    )

def _build_guardrails(spec: dict) -> RiskGuardrails:
    spec = spec or {}
    return RiskGuardrails(
        max_concurrent_positions=spec.get("max_concurrent_positions", 10),
        max_drawdown_pct=spec.get("max_drawdown_pct", 15.0),
        daily_loss_cap_pct=spec.get("daily_loss_cap_pct", 3.0),
        max_correlation=spec.get("max_correlation", 0.8),
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
            guardrails=_build_guardrails(b.get("guardrails")),
        ))
    return books
