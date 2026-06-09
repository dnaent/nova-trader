from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class Auditor(Protocol):
    """Layer 3. Real impl calls the Anthropic API and returns a 0-100 score."""
    def audit(self, prompt: str) -> float: ...

class StubAuditor:
    """Layer 3 stub. Replace with a real Anthropic API call (Phase 3)."""
    def audit(self, prompt: str) -> float:
        # FORD is the classic 'low fundamental grade' example -> penalise it
        return 35.0 if "FORD" in prompt else 80.0
