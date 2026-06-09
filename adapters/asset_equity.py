from __future__ import annotations
from typing import Iterable
from decimal import Decimal
from core.context import Candidate
from layers.macro_gate import MacroGate
from layers.scanner import RegimeAwareScanner
from layers.data_loader import get_financials, get_recent_news
import json

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
        financials = get_financials(c.symbol)
        news = get_recent_news(c.symbol)
        
        prompt = (
            f"Please audit the following company: {c.symbol}\n\n"
            f"=== INFERENCE CONTEXT BUNDLE ===\n"
            f"Macro Environment:\n"
            f"{json.dumps(self._last_gate_result, indent=2) if self._last_gate_result else 'None'}\n\n"
            f"Company Financials (Last 4 Quarters):\n"
            f"{financials}\n\n"
            f"{news}\n"
            f"================================\n\n"
            f"Evaluate the company's debt, margins, and revenue trends against the Macro Environment risks above. "
            f"Also consider any breaking geopolitical or corporate risks highlighted in the news. "
            f"Provide your analysis, and remember to end your response exactly with 'SCORE: <number>'."
        )
        return prompt
