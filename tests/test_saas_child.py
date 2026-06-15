import json

import pytest

from layers.analyst import Auditor, extract_score
from saas.tenant_store import TenantTrainingStore, TenantIsolationError
from saas.rag_bridge import RagContextBuilder
from saas.vertex_auditor import VertexAuditor


def _rec(tenant=None, book="ibkr_isa_equity", acted=1, pnl=250.0, r=2.3, ts="2026-06-10"):
    d = {"ts": ts, "book_id": book, "asset_class": "EQUITY", "symbol": "AAPL",
         "macro": {"regime": "risk-on"}, "markers": {"RSI_14": 55.0, "MACD_12_26_9": 1.2},
         "blended": 86.0, "acted": acted, "realized_pnl": pnl, "r_multiple": r}
    if tenant is not None:
        d["tenant_id"] = tenant
    return d


# --------------------------------------------------------------------------- #
# Tenant isolation (the hard boundary)
# --------------------------------------------------------------------------- #
def test_store_stamps_untagged_when_ingesting_own_export():
    store = TenantTrainingStore("t1", [_rec()], stamp=True)
    assert len(store) == 1
    assert store.samples()[0]["tenant_id"] == "t1"

def test_store_rejects_untagged_without_stamp():
    with pytest.raises(TenantIsolationError):
        TenantTrainingStore("t1", [_rec()], stamp=False)

def test_store_rejects_cross_tenant_record():
    with pytest.raises(TenantIsolationError):
        TenantTrainingStore("t1", [_rec(tenant="t2")])

def test_store_accepts_matching_tenant():
    store = TenantTrainingStore("t1", [_rec(tenant="t1")])
    assert len(store) == 1

def test_from_parent_export_roundtrip(tmp_path):
    p = tmp_path / "export.jsonl"
    p.write_text("\n".join(json.dumps(_rec()) for _ in range(2)))
    store = TenantTrainingStore.from_parent_export(str(p), "tenant-xyz")
    assert len(store) == 2
    assert all(r["tenant_id"] == "tenant-xyz" for r in store.samples())

def test_samples_filters():
    recs = [_rec(book="A", acted=1, pnl=100.0), _rec(book="B", acted=0, pnl=None, r=None)]
    store = TenantTrainingStore("t1", recs, stamp=True)
    assert len(store.samples(book_id="A")) == 1
    assert len(store.samples(acted_only=True)) == 1
    assert len(store.samples(with_outcome=True)) == 1


# --------------------------------------------------------------------------- #
# RAG bridge
# --------------------------------------------------------------------------- #
def test_rag_build_contains_isolation_and_disclaimer():
    store = TenantTrainingStore("t1", [_rec()], stamp=True)
    block = RagContextBuilder(store).build()
    assert "tenant: t1" in block
    assert "NOT predictions" in block
    assert "never executes" in block
    assert "AAPL" in block and "+2.30R" in block

def test_rag_empty_store_is_safe():
    store = TenantTrainingStore("t1", [], stamp=True)
    block = RagContextBuilder(store).build()
    assert "No validated precedents" in block

def test_rag_augment_appends_to_prompt():
    store = TenantTrainingStore("t1", [_rec()], stamp=True)
    out = RagContextBuilder(store).augment("ORIGINAL BUNDLE")
    assert out.startswith("ORIGINAL BUNDLE")
    assert "PARENT DECISION PRECEDENTS" in out

def test_rag_prefers_outcome_labelled_recent():
    recs = [
        _rec(acted=0, pnl=None, r=None, ts="2026-06-09"),   # not labelled
        _rec(acted=1, pnl=500.0, r=5.0, ts="2026-06-11"),   # labelled, newest
        _rec(acted=1, pnl=100.0, r=1.0, ts="2026-06-10"),
    ]
    store = TenantTrainingStore("t1", recs, stamp=True)
    block = RagContextBuilder(store, top_k=1).build()
    assert "+5.00R" in block            # picked the newest labelled record


# --------------------------------------------------------------------------- #
# VertexAuditor (the child)
# --------------------------------------------------------------------------- #
def _auditor(capture=None, raises=False):
    store = TenantTrainingStore("t1", [_rec()], stamp=True)
    rag = RagContextBuilder(store)
    def call(prompt):
        if capture is not None:
            capture.append(prompt)
        if raises:
            raise RuntimeError("vertex down")
        return "Reasonable. SCORE: 77"
    return VertexAuditor("t1", rag, call=call)

def test_child_never_executes():
    assert VertexAuditor.executes is False

def test_child_is_drop_in_auditor():
    # Satisfies the same runtime-checkable protocol the engine depends on.
    assert isinstance(_auditor(), Auditor)

def test_child_injects_tenant_context_then_scores():
    seen = []
    auditor = _auditor(capture=seen)
    score = auditor.audit("Please audit AAPL ...")
    assert score == 77.0
    assert "PARENT DECISION PRECEDENTS" in seen[0]   # RAG context was injected
    assert "tenant: t1" in seen[0]

def test_child_tenant_mismatch_rejected():
    store = TenantTrainingStore("t1", [_rec()], stamp=True)
    with pytest.raises(ValueError):
        VertexAuditor("t2", RagContextBuilder(store))   # store is t1, auditor t2

def test_child_is_fault_tolerant():
    assert _auditor(raises=True).audit("x") == 50.0     # neutral on backend failure
