# Scope — Training a Local Model on the Corpus

**Date:** 2026-06-19 · **Status:** SCOPE for review (nothing built) · **Origin:** operator — "what would *actually* training a local AI on the corpus involve?"

## The honest starting point
Everything we proved this week says **the edge is the deterministic macro-regime gate**, not the scanner/markers (the RandomForest scanner had ~no edge; the books that won did so via regime-gating + diversification + trend, not feature prediction). So this scope is not "bolt on an AI and it'll print money." It is: **measure whether a model can learn anything that beats the deterministic baseline — cheaply first — and only build the heavy machinery if the data earns it.** Same discipline that caught the no-edge scanner. The realistic outcomes are (a) a marginal trade-selection/sizing improvement, or (b) an honest "no learnable edge beyond regime," which is itself worth knowing before investing in a fine-tune.

## The corpus as training data — and 4 hard constraints
The corpus (`nova_training_corpus.jsonl`, 26.5k records, growing live) is per-decision: `{macro regime, 32 markers, gate, quant/claude/blended scores, sizing, side, book, outcome (realized PnL + R-multiple)}`. Before any training, these constraints are decisive:

1. **Outcomes exist only for ACTED trades.** Of 26.5k records only ~2,736 are acted+labelled (GIA 1,068 / Forex 1,336 / SIPP 212 / ISA 120). The other ~24k are not-acted decisions with **no outcome** — unusable as-is for supervised learning. ⇒ the real labelled set is modest *and* selection-biased (only trades the engine chose).
2. **Markers are GIA-only.** Allocation books (ISA/SIPP) log empty markers (they hold baskets, no scanner). Forex logs its own trend markers. So the feature-rich, outcome-labelled subset is essentially **GIA (~1,068)** + Forex trend features (~1,336).
3. **`claude_score` is constant (50) in the replay-generated bulk** (NeutralAuditor). Only *live* records carry a real auditor score. So in the historical corpus that feature is uninformative.
4. **Selection bias / no counterfactuals.** We only know outcomes for what was traded — we can't learn "what we *should* have traded but didn't" from the raw corpus.

## Prerequisite — Phase 0: data enrichment (counterfactual labels)
The single highest-leverage fix: **extend the replay to label NOT-ACTED candidates with counterfactual outcomes** (simulate, per candidate, what a trade would have returned over the same exit logic). That turns ~1,068 labelled GIA records into **~24k labelled** examples, removes the selection bias, and gives a proper supervised dataset. Without this, any learned model trains on a tiny, biased slice. *Effort: medium (replay already prices everything point-in-time; add a shadow-outcome pass).* **This should come first.**

## Options (with honest pros/cons + 3080 Ti feasibility)
| Option | What | Pros | Cons / honesty | 3080 Ti |
|---|---|---|---|---|
| **B. Supervised scanner** (recommended *probe*) | Gradient-boosted trees / small NN: features → P(profit) or expected R; replaces the no-edge RandomForest | Cheap, fast, directly tests "is there learnable signal beyond regime?"; the right tool for tabular data | May confirm *no* edge (consistent with prior findings); modest sample | Trivial (CPU/GPU) |
| **A. Fine-tune the LLM auditor** | QLoRA-fine-tune qwen2.5-7B on context-bundle → score/rationale (or DPO on good vs bad decisions) | Improves Layer 3 (the qualitative 40%); the "parent fine-tune" in the architecture | Heavy for what's a tabular problem; LLM is only 40% of the blend and not where the edge is; risk of overfitting a 7B to ~1-2k examples | Feasible: 7B QLoRA (4-bit) fits ~12 GB |
| **C. RAG (no training)** | Inject corpus precedents into the auditor prompt ("similar past setups → outcomes") | Cheapest; already scaffolded (`saas/rag_bridge.py`); the recommended SaaS/Vertex path | Not "learning," just retrieval; helps the child more than the parent | n/a |
| **D. RL / policy learning** | Train an agent to learn a trading policy | The most "AI learns to trade" | Highest overfit/instability risk, hardest, least honest for retail; not recommended | Hard |

## Recommended phased path (evidence-first)
- **Phase 0 — Enrich (counterfactual labels).** Add shadow-outcomes for not-acted candidates in replay ⇒ a real, unbiased supervised dataset. *Do first.*
- **Phase A — Supervised edge PROBE (cheap, decisive).** Gradient-boosted model on the enriched features → outcome, evaluated **walk-forward / out-of-sample** (never in-sample). Measure: does ranking by the model's score improve expectancy vs taking all gate-permitted trades? Report AUC / OOS expectancy uplift vs the deterministic baseline. **If no uplift ⇒ STOP: the honest answer is "no learnable edge beyond regime," and the system stays the validated deterministic engine + RAG for the SaaS child.** This is the gate for everything below.
- **Phase B — LLM auditor QLoRA fine-tune (ONLY if Phase A shows signal).** On the 3080 Ti: build instruction/preference pairs from the labelled corpus, QLoRA-tune qwen-7B, A/B it against stock qwen in replay on held-out data. Promote only on an OOS win.
- **Phase C — RAG (parallel, cheap).** Wire the scaffolded `saas/rag_bridge` so the (Vertex) child gets corpus precedents — independent of A/B, the recommended first move for the SaaS side.

## Success criteria & guardrails
- Any learned model must **beat the deterministic baseline on walk-forward / out-of-sample** — in-sample improvement is meaningless (the overfit trap).
- **Never auto-promoted.** A trained model is a *candidate* Layer-2/3 backend swapped via DI; it faces the same per-book validation + the hard operator-sign-off gate. Still 100% PAPER.
- Prefer the **smallest model that works** (a GBM that matches a fine-tuned LLM wins — cheaper, faster, interpretable).

## Effort & dependencies
- Phase 0: ~medium (replay shadow-outcome pass). Phase A: ~small (scikit-learn / xgboost — add dep). Phase B: ~large (QLoRA stack: `transformers`, `peft`, `bitsandbytes`, a base 7B). Phase C: ~small (RAG over the existing export; `saas/` scaffolded).
- **Gating:** none of this is urgent — it sits behind the live track record maturing (the priority). Phase 0+A is the cheap, honest first probe whenever we choose to start.

## Bottom line
"Training a local AI to trade" concretely = **(0) label the data properly → (A) cheaply probe whether a model beats the regime baseline out-of-sample → (B) only then fine-tune the LLM.** The most likely honest result is a modest selection/sizing improvement or none — and the framework is built to tell us which, rather than assume. The validated deterministic engine is the floor; a learned model only earns its place by beating it OOS.
