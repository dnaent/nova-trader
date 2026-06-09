from __future__ import annotations
from typing import Iterable
from decimal import Decimal
from core.context import Candidate
from layers.macro_gate import MacroGate
from layers.scanner import RegimeAwareScanner

class EquityAdapter:
    """Equity Adapter integrating Phase 2 Macro Gate and Scanner."""
    asset_class = "EQUITY"
    handles = {"EQUITY", "ETF"}

    def __init__(self):
        self.gate = MacroGate()
        self.scanner = RegimeAwareScanner()
        self._last_gate_result = {}

    def macro_gate(self) -> float:
        self._last_gate_result = self.gate.evaluate()
        return self._last_gate_result.get("gate_score", 50.0)

    def scan(self, universe: Iterable[str]) -> list:
        hmm_prob = self._last_gate_result.get("hmm_safe_prob", 0.5)
        return self.scanner.scan(list(universe), hmm_prob)

    def auditor_prompt(self, c: Candidate) -> str:
        context = f"Macro Context: {self._last_gate_result}. " if self._last_gate_result else ""
        return f"{context}Review last 4 quarters for {c.symbol}; flag debt/margin risks; score 0-100."
