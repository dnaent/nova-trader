"""
Nova Engine — adapters/asset_allocation.py

Low-turnover, regime-gated buy-and-hold ALLOCATION strategy — built for the SIPP
pension book, whose objective is income/compounding with the tightest drawdown,
NOT tactical trading.

How it works with the engine (no special-casing needed):
  * macro_gate(): the same proven regime gate the tactical books use.
  * scan(): always proposes holding a quality/broad ETF basket at high conviction
    while the regime is favourable. Once a holding is open, the engine's
    correlation guardrail (a symbol correlates ~1.0 with itself) blocks re-buying
    it — so it simply HOLDS. Turnover only occurs on regime transitions.
  * de-risk: the SIPP book sets aggressive_liquidation + a high per-book gate_min,
    so when the regime weakens the engine closes to cash; it re-enters when the
    regime recovers.

Sizing should be buy-and-hold (large allocation, wide stop so normal volatility
doesn't churn it, no take-profit) — configured per-book in portfolio.yaml.
"""
from __future__ import annotations

import json
from typing import Iterable

from core.context import Candidate
from layers.macro_gate import MacroGate
from layers.data_loader import get_latest_price, format_markers

# A broad, liquid core for a pension book. VWRL.L = Vanguard FTSE All-World
# (global diversification in one holding). Extendable to a multi-ETF basket.
DEFAULT_BASKET = ["VWRL.L"]


class AllocationAdapter:
    """Regime-gated buy-and-hold allocation (SIPP/pension)."""
    asset_class = "ETF"
    handles = {"EQUITY", "ETF"}
    strategy = "allocation"

    def __init__(self, basket: Iterable[str] | None = None):
        self.gate = MacroGate()
        self.basket = list(basket) if basket else list(DEFAULT_BASKET)
        self._last_gate_result: dict = {}

    def macro_gate(self) -> float:
        self._last_gate_result = self.gate.evaluate()
        return self._last_gate_result.get("gate_score", 50.0)

    def scan(self, universe: Iterable[str]) -> list:
        """Propose holding the basket (high conviction) at the point-in-time price.

        The basket is the book's PER-BOOK `universe` (passed in by the engine) when
        set — this lets distinct allocation books hold different baskets (e.g. an
        aggressive growth ISA vs a diversified SIPP) through one shared adapter. Falls
        back to the adapter's construction basket when the book has none. The engine's
        correlation guardrail prevents re-buying anything already held (low turnover).
        """
        basket = list(universe) if universe else self.basket
        out = []
        for sym in basket:
            px = get_latest_price(sym)
            if px is None or px <= 0:
                continue
            out.append(Candidate(sym, "ETF", 100.0, px,
                                  meta={"strategy": "allocation", "markers": {}}))
        return out

    def auditor_prompt(self, c: Candidate) -> str:
        return (
            f"Long-horizon ALLOCATION hold review for {c.symbol} "
            f"(SIPP/pension — income & compounding, low turnover).\n\n"
            f"=== INFERENCE CONTEXT BUNDLE ===\n"
            f"Macro Regime:\n"
            f"{json.dumps(self._last_gate_result, indent=2) if self._last_gate_result else 'None'}\n\n"
            f"{format_markers(c.meta.get('markers', {}))}\n"
            f"================================\n\n"
            f"This is a buy-and-hold-while-the-regime-is-favourable decision for a "
            f"pension core holding, not a tactical trade. Assess whether the macro "
            f"regime supports staying invested. End your response exactly with 'SCORE: <number>'."
        )
