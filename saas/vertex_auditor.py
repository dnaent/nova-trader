"""
Nova Engine — saas/vertex_auditor.py

The CLOUD CHILD auditor (Layer 3 backend for the SaaS product). Drop-in for
`LLMAuditor` — same `audit(prompt) -> float` contract — so the engine swaps
backends by dependency injection, never a fork.

What makes it the child:
  * ADVISES ONLY. It returns a qualitative score; it has no broker and never
    executes — `executes = False`. IBKR access belongs solely to the parent.
  * Tenant-isolated RAG. Before scoring, it enriches the Inference Context
    Bundle with the operator's validated precedents for THIS tenant only
    (via RagContextBuilder over a TenantTrainingStore).
  * No forward guarantees — the system prompt frames the task as qualitative
    risk assessment, consistent with the parent's blend-and-validate discipline.

The Vertex AI SDK call is lazily imported and injectable, so this module is
fully offline-testable; live provisioning (project/region/creds) is step 2.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

from layers.analyst import extract_score
from saas.rag_bridge import RagContextBuilder

log = logging.getLogger("nova.saas.vertex")

_SYSTEM_PROMPT = (
    "You are the Nova cloud auditor (Layer 3, decision-support). Read the macro "
    "context, technical marker snapshot, fundamentals/news, and the operator's "
    "historical decision precedents, then output a QUALITATIVE risk score from 0 "
    "to 100 (100 = strong, low-risk setup; 0 = toxic). This is advisory only — "
    "you never place trades and you never guarantee future performance. Include a "
    "brief rationale and end your response exactly with 'SCORE: <number>'."
)


class VertexAuditor:
    """SaaS child auditor: tenant-isolated RAG + Vertex AI scoring. Advisory only."""

    executes = False  # hard, explicit: the child never executes

    def __init__(self, tenant_id: str, rag: RagContextBuilder, *,
                 project: Optional[str] = None, location: str = "europe-west2",
                 model_name: str = "gemini-1.5-pro",
                 system_prompt: str = _SYSTEM_PROMPT,
                 call: Optional[Callable[[str], str]] = None):
        if rag.store.tenant_id != tenant_id:
            raise ValueError(
                f"RAG store tenant {rag.store.tenant_id!r} != auditor tenant {tenant_id!r}")
        self.tenant_id = tenant_id
        self.rag = rag
        self.project = project
        self.location = location
        self.model_name = model_name
        self.system_prompt = system_prompt
        # `call` lets tests/offline demos inject a fake LLM; default = real Vertex.
        self._call = call or self._call_vertex

    def audit(self, prompt: str, book_id: Optional[str] = None) -> float:
        """Enrich with tenant-scoped precedents, score via the model, parse 0-100.

        Never raises into the engine: on any backend failure it returns a neutral
        50.0 (matching LLMAuditor's fault-tolerant contract).
        """
        try:
            enriched = self.rag.augment(prompt, book_id=book_id)
            return extract_score(self._call(enriched))
        except Exception as e:  # noqa: BLE001 - fault tolerance is the contract
            log.warning("VertexAuditor[%s] error: %s — neutral 50.0", self.tenant_id, e)
            return 50.0

    def _call_vertex(self, prompt: str) -> str:
        """Call Vertex AI (lazy import — only needed for live use)."""
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project, location=self.location)
        model = GenerativeModel(self.model_name, system_instruction=self.system_prompt)
        resp = model.generate_content(
            prompt, generation_config={"temperature": 0.1, "max_output_tokens": 300})
        return resp.text


# =========================================================================== #
# Offline demo (no GCP needed — uses an injected fake model)
# =========================================================================== #
def _demo() -> None:
    from saas.tenant_store import TenantTrainingStore
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    records = [
        {"ts": "2026-06-10T00:00:00", "book_id": "ibkr_isa_equity", "asset_class": "EQUITY",
         "symbol": "AAPL", "macro": {"regime": "risk-on"}, "markers": {"RSI_14": 55.0},
         "blended": 86.0, "acted": 1, "realized_pnl": 250.0, "r_multiple": 2.3},
    ]
    store = TenantTrainingStore("tenant-001", records, stamp=True)
    rag = RagContextBuilder(store)
    auditor = VertexAuditor("tenant-001", rag,
                            call=lambda p: "Looks constructive given precedents. SCORE: 78")
    print(f"executes = {auditor.executes}")
    print(f"audit score = {auditor.audit('Please audit AAPL ...')}")


if __name__ == "__main__":
    _demo()
