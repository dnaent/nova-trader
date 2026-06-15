"""
Nova Engine — saas/ (SaaS productization layer)

The CLOUD CHILD side of the parent->child architecture. The local/parent model
(Ollama on the 3080 Ti) trades the operator's portfolio and LOGS training data;
the cloud child reads that curated dataset to power the SaaS product.

Hard rules enforced here (CLAUDE.md, 2026-06-14):
  * The child ADVISES ONLY — it never executes and never touches IBKR. The SaaS
    is positioned as a signals / decision-support tool (UK FCA: least-hurdle
    route, avoids discretionary-management authorization).
  * Per-tenant data isolation from day one: a tenant's model context is built
    only from its own curated export — never cross-tenant.
  * No guaranteed performance: context is framed as historically validated
    against the per-book criteria, never a forward promise.

The engine itself is unchanged: productization is a backend swap via dependency
injection (VertexAuditor in place of LLMAuditor), not a fork.
"""
