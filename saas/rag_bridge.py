"""
Nova Engine — saas/rag_bridge.py

The parent->child bridge as RAG (the decided first path: context-injection now,
fine-tune later). Turns the parent's curated, outcome-labelled training records
into a tenant-scoped context block appended to the Inference Context Bundle, so
the cloud child reasons with the operator's validated experience.

Retrieval here is deliberately simple (recency + outcome quality, tenant-scoped);
a vector/semantic retriever is the step-2 upgrade. The isolation guarantee comes
from TenantTrainingStore, which this class only ever reads through.
"""
from __future__ import annotations

from typing import Optional

from saas.tenant_store import TenantTrainingStore

# A handful of markers worth surfacing in the precedent lines (kept short so the
# prompt stays readable). Absent markers are simply skipped.
_HEADLINE_MARKERS = ("RSI_14", "MACD_12_26_9", "ADX_14", "ATRr_14")


class RagContextBuilder:
    """Builds tenant-isolated RAG context from the parent dataset."""

    def __init__(self, store: TenantTrainingStore, top_k: int = 3):
        self.store = store
        self.top_k = top_k

    def _retrieve(self, book_id: Optional[str]) -> list[dict]:
        """Most relevant precedents: prefer outcome-labelled, acted decisions,
        most recent first; fall back to recent decisions of any kind."""
        labelled = self.store.samples(book_id=book_id, acted_only=True, with_outcome=True)
        pool = labelled or self.store.samples(book_id=book_id)
        pool = sorted(pool, key=lambda r: r.get("ts", ""), reverse=True)
        return pool[: self.top_k]

    @staticmethod
    def _format_record(r: dict) -> str:
        book = r.get("book_id", "?")
        ac = r.get("asset_class", "?")
        sym = r.get("symbol", "?")
        regime = (r.get("macro") or {}).get("regime", "n/a")
        markers = r.get("markers") or {}
        marks = ", ".join(f"{m}={markers[m]:.2f}" for m in _HEADLINE_MARKERS
                          if isinstance(markers.get(m), (int, float)))
        decision = "ACTED" if r.get("acted") else "held"
        blended = r.get("blended")
        blended_s = f"{blended:.0f}" if isinstance(blended, (int, float)) else "n/a"
        outcome = ""
        if r.get("realized_pnl") is not None:
            rmult = r.get("r_multiple")
            rmult_s = f"{rmult:+.2f}R" if isinstance(rmult, (int, float)) else "n/a"
            outcome = f" -> outcome {rmult_s} (PnL {r['realized_pnl']:+.0f})"
        head = f"[{book} {ac} {sym}] regime={regime}"
        if marks:
            head += f", {marks}"
        return f"{head}, blended={blended_s} -> {decision}{outcome}"

    def build(self, book_id: Optional[str] = None) -> str:
        """Return the formatted, tenant-scoped precedent block (or a safe note)."""
        recs = self._retrieve(book_id)
        if not recs:
            return ("=== PARENT DECISION PRECEDENTS (tenant: "
                    f"{self.store.tenant_id}) ===\nNo validated precedents available yet.")
        lines = [
            f"=== PARENT DECISION PRECEDENTS (tenant: {self.store.tenant_id}, "
            "historical — NOT predictions) ===",
            f"{len(recs)} most relevant past decisions from the operator's validated dataset:",
        ]
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {self._format_record(r)}")
        lines.append(
            "These are historical outcomes provided as decision-support context only. "
            "The system advises; it never executes. No guarantee of future performance.")
        return "\n".join(lines)

    def augment(self, prompt: str, book_id: Optional[str] = None) -> str:
        """Append the precedent block to an existing Inference Context Bundle."""
        return f"{prompt}\n\n{self.build(book_id)}"
