# Scope — SaaS Productization (the Cloud Child)

**Date:** 2026-06-20 · **Status:** PLAN for review — deliberately NOT built ahead of the data.
**Gating principle:** the product is built only as the live equity track record matures (RAG has nothing valuable to serve until the parent has real forward experience — see the wait-time estimate: ~3–6mo clean live + real trades minimum). This doc is the *map* so the eventual build is deliberate, not improvised.

## 1. What the product IS (and is NOT)
- **IS:** a **signals / decision-support** SaaS. The cloud child surfaces the same regime-gated, diversified allocation *recommendations* the parent engine makes, each **explained via RAG** over the operator's validated historical decisions. The customer **reviews and executes themselves.**
- **IS NOT:** discretionary management. The child **never executes, never touches IBKR** (`VertexAuditor.executes = False`, enforced). No performance guarantees — framed as historically-validated, never a promise.
- **Why:** this is the least-regulatory-hurdle route (avoids discretionary-management authorization) AND it's honest (markets are non-stationary).

## 2. Architecture (already decided; backend already built)
```
LOCAL PARENT (this repo, on the 3080 Ti)
  trades personal portfolio via IBKR (read-only feed + paper/live)
  → logs every decision+outcome → Ledger.export_training_jsonl()  [the corpus = the bridge artifact]
        │  (encrypted export → Cloud Storage)
        ▼
CLOUD CHILD (per tenant, advisory only — NEVER executes)
  TenantTrainingStore   (fail-closed per-tenant isolation)        ✅ built+tested
  RagContextBuilder     (tenant-scoped precedent retrieval)       ✅ built+tested
  VertexAuditor         (Layer-3 backend, executes=False, RAG)    ✅ built+tested, proven on real corpus+Ollama
  + the engine running in ADVISORY mode (gate+scan+audit, no broker)   ← needs a cloud entrypoint
```
Productization = a **backend swap via dependency injection, NOT a fork**: same engine, `LLMAuditor`→`VertexAuditor`, local DB→per-tenant cloud DB, IBKR feed→(read-only market data; child needs prices but no execution).

## 3. Build inventory — done vs needed
**Done (offline, tested):** the `saas/` package (store/RAG/auditor); proven end-to-end on the real corpus + Ollama.
**Needed for go-live (the actual product build):**
| Layer | Work |
|---|---|
| **Cloud engine** | A read-only "advisory" entrypoint that runs the gate+scan+audit per book and emits *recommendations* (no broker). Cloud Run service. |
| **Market data (cloud)** | A data source for the cloud engine (the child needs prices for the gate/markers but NO execution) — a market-data API (the child must NOT use the operator's IBKR). |
| **Parent→cloud sync** | Encrypted corpus export → Cloud Storage → per-tenant ingestion job. |
| **Per-tenant data** | Firestore or Cloud SQL, tenant-isolated (the `TenantTrainingStore` boundary enforced at the infra layer too). |
| **Vertex** | `VertexAuditor._call_vertex` is written; needs project/region/creds + a model choice (Gemini on Vertex, or a Vertex-hosted open model for the later fine-tune moat). |
| **Customer UI** | The signals dashboard (recommendations + RAG rationale + disclaimers). `saas_ui/` (Material-UI Joy) is a starting shell. Auth, onboarding. |
| **Billing** | Subscription (Stripe or similar). |
| **Security** | IAM least-privilege, Secret Manager, VPC, audit logs, GDPR (europe-west2 data residency). |

## 4. GCP layout (europe-west2 — UK/GDPR)
- **Cloud Run:** the advisory engine + an API gateway for the UI. Scales 0→N.
- **Vertex AI:** the auditor LLM (RAG context injection first; fine-tune a Vertex-hosted open model later as the moat).
- **Firestore/Cloud SQL:** per-tenant corpus + user/session data.
- **Cloud Storage:** the parent's encrypted corpus exports; model artifacts.
- **Secret Manager + IAM + VPC + Cloud Armor:** creds, least-privilege, network isolation, DDoS.
- **Cloud Monitoring/Logging:** ops + an audit trail (compliance).

## 5. ⚠️ Regulatory (FCA) — the biggest product-shaping risk, FLAG FOR LEGAL REVIEW
The "signals/decision-support, not discretionary management" stance avoids the *heaviest* authorization — BUT it is **NOT automatically exempt**. In the UK, **making a personal recommendation to buy/sell a specific investment is itself a regulated activity** ("advising on investments"). To stay outside the FCA perimeter the product must be framed as **generic research / tools / signals — NOT personalised advice** (no "you should buy X"), or it must be **authorized**. This is a genuine legal question, not a copy tweak — **get qualified UK regulatory/legal advice before launch.** Product copy, disclaimers ("for information only, not a personal recommendation, not advice, capital at risk, no guarantee"), and the UX (generic signals vs personalised) all hinge on this. Do not hand-wave it.

## 6. Tenant isolation & data
- The child trains/RAGs ONLY on the parent's curated export — never cross-tenant (`TenantTrainingStore` is fail-closed; enforce at infra too: per-tenant DB partitions, IAM).
- No customer's positions/PII ever enters another tenant's context. Design in from day one (it is, at the code layer).
- GDPR: EU data residency (europe-west2), right-to-erasure, data-processing terms.

## 7. Phasing (each phase gated)
- **Phase 0 — NOW (done):** offline RAG backend built + proven. ✅
- **Phase 1 — when track record ≥ ~3–6mo with real trades:** stand up the cloud advisory engine + Vertex (single-tenant = the operator) reading the real corpus; validate the cloud child's recommendations match the parent's. RAG-first (no fine-tune).
- **Phase 2 — first external users:** auth, per-tenant isolation infra, the UI, billing, the FCA-reviewed copy. Small private beta.
- **Phase 3 — scale + moat:** fine-tune a Vertex-hosted model on the (now mature) corpus; semantic RAG retrieval; more books/markets.

## 8. Cost note
Cloud Run + Vertex + Firestore at low volume is cheap (~£tens/mo idle, scales with use); the real costs are Vertex inference per audit and engineering time. Keep the child's audit cadence low (it's allocation/low-turnover — few decisions) to control LLM spend.

## 9. Honest pitfalls (the discipline)
1. **Don't build ahead of the data.** RAG over a thin corpus = thin value. The backend is ready; the *product* waits for the track record. (This doc exists so the wait is used for *planning*, not premature coding.)
2. **Regulatory is existential** — get it right (Section 5) before any external user.
3. **The corpus is now small + allocation-only** (the tactical scanner is retired) — RAG precedents will be sparse until live experience accrues; manage expectations on what RAG adds (it *explains*, it doesn't *predict*).
4. **The UI is a big build** needing your product vision — not autonomous engineering.
5. **Single-tenant first** (you) — prove the cloud child mirrors the parent before onboarding anyone.

## Bottom line
The cloud-child **backend is done and proven**; the **product** is a deliberate, multi-phase build that should track the maturing live record and your product/legal decisions. Nothing here should be built until Phase 1's gate (≥3–6mo clean live with real trades). Until then: **wait, monitor, and let this plan be the map.**
