# Nova Engine — Build & Handoff Specification
### A portfolio-context, multi-book automated trading engine (IBKR-first)

> **Purpose of this document.** This is the master handoff for the project which will be running on the local Windows 11 / RTX 3080 Ti machine (GitHub Source Control lean edits on Macbook Pro -> <- Lean GitHub -> <- Local run and future N8n automation on Windows 11 machine) full build and engine will run on local Windows 11 RTX 3080 Ti). It defines what to build, in what order, and the hard rules that must never be violated. It evolves the original **Nova_Trader** (a sole-Forex SaaS concept) into **Nova Engine** — one engine that understands the user's *portfolio context* and routes each trade to the correct account "book" with the correct asset rules, tax policy, and execution adapter.

> **Not financial advice.** This system will trade the operator's own ISA, GIA, and SIPP capital, including pension funds at the operators choice. Optimised for IBKR - Future brokers coming soon. Automated trading carries real risk of loss. Build paper-trading-first, keep a human approval gate, and treat every safety rule below as non-negotiable.

---

## 1. Decision record (read first)

These decisions are settled. Do not re-litigate them during the build.

1. **Build the personal IBKR engine first**, not the Forex SaaS product. The SaaS is a separate future track.
2. **One engine, many books** — do not build parallel per-asset bots. A *book* = (account wrapper × asset class × broker × tax policy). The engine reads a portfolio manifest and routes candidates to the right book.
3. **IBKR is the first broker.** It is effectively forced for the UK ISA/SIPP/GIA use case (Alpaca offers no UK tax wrappers).
4. **Equities + ETFs are the first asset class.** Forex is a later fork (Section 12).
5. **Paper trading first, always.** No live capital until the engine runs clean in IBKR paper mode for at least two consecutive weeks with positive risk-adjusted results.
6. **Human-in-the-loop by default.** Autonomous, no-approval execution is the riskiest mode and is explicitly out of scope for the first build.

### Corrected facts that override the older Nova Bot / research documents

The earlier research notes contain stale or wrong assumptions. Use these instead:

- **IBKR now has an official Claude connector** (launched 2 June 2026, via Claude's certified connector marketplace). It links an existing IBKR account with standard login, shares no API keys, and routes AI-drafted trades to an "AI Instructions" tab for the client to **approve before execution**. This is the preferred approval-gated path. A local `ib_async` engine is only needed for genuinely autonomous execution, which is out of scope for now.
- **UK CGT (2025/26):** annual exempt amount is **£3,000** (not £6,000). Rates on shares/other assets are **18% basic / 24% higher** (not 10%/20%) since 6 April 2025. The old Nova Bot tax module had both wrong.
- **ISA and SIPP are tax-free / tax-sheltered.** There is no CGT to optimise inside them. The tax module is active **only** in the GIA / taxable account.
- **Options and Forex cannot be held in an ISA or SIPP** (HMRC rules). They require a GIA or standard margin account.
- **Latency / co-location is irrelevant** for the strategies here (daily macro gates, swing/position trades). Ignore any "sub-5ms" advice.
- **No self-modifying live code.** Backtesting may *propose* parameter changes; a human approves the diff before it touches live config.
- **Drop the "£100/month compounding & banking" logic** entirely. It was a retail-app gimmick. Replace with NAV-based position sizing scaled by the macro gate.

### From Nova Bot to Nova Engine — what changed and why

Nova Engine is a direct refinement of the original Nova Bot. The core insight that triggered the redesign: Nova Bot was really *two different systems wearing one name* — a Forex SaaS product for other users, and (implicitly) a tool for managing the operator's own money. They have different brokers, asset classes, tax treatment, and deployment. Nova Engine resolves this by collapsing the trading logic into **one portfolio-context engine with pluggable books**, and parking the SaaS as a separate future track.

| Dimension | Nova Bot (previous) | Nova Engine (now) | Why it changed |
|---|---|---|---|
| **Identity** | Sole-Forex SaaS for paying users | Personal portfolio-context engine, multi-book | The personal engine is more structurally sound and testable with the operator's own funds first |
| **Asset class** | Forex only (EUR/USD, GBP/USD…) | Equities/ETFs first; Forex as a later additive fork | Equities map cleanly to ISA/SIPP/GIA; FX cannot live in tax wrappers |
| **Account model** | Single trading account | Books = (wrapper × asset × broker × tax policy); ISA/SIPP/GIA routed separately | The engine must understand portfolio context, not just symbols |
| **Broker** | OANDA / IG / Forex.com multi-broker layer | IBKR-first (the multi-broker layer is redundant for personal use) | IBKR is effectively forced for UK ISA/SIPP/GIA |
| **Signal core** | "Self-training LSTM predicts Forex direction" + 30+ weighted indicators | Deterministic 3-layer spine; Claude is a *qualitative auditor*, not a predictor | LLM price-prediction rarely survives live markets; the deterministic-first/auditor split is the genuinely sound idea |
| **Tax module** | UK CGT optimiser, always on, £6,000 AEA, 10%/20% | CGT active **only** in GIA; £3,000 AEA, 18%/24%; null inside ISA/SIPP | Wrappers are tax-free/sheltered; old figures were stale |
| **Capital logic** | £100/month budget, 50% compound / 50% bank | NAV-based sizing scaled by the macro gate | Compounding/banking was a retail gimmick that doesn't map to a lump-sum portfolio |
| **Deployment** | GCP / Cloud Run / Firebase, multi-user | Local Windows 11 + WSL2 + RTX 3080 Ti, single operator | Local hardware suits heavy weekend backtesting; no SaaS overhead needed yet |
| **IBKR access** | n/a | Official Claude connector (approval-gated) first; local `ib_async` only for later autonomy | The connector launched 2 June 2026 and replaces most of the local-gateway plumbing |
| **Autonomy** | Implied fully-automated 24/7 | Paper-first, human approval gate; no self-modifying live code | Autonomous live trading of one's own pension is the riskiest mode |

**What carried over unchanged:** the risk manager, position sizing concept, trade ledger, performance scoring (Sharpe/drawdown), backtesting discipline, and the multi-timeframe/indicator toolkit — these were always asset-agnostic and remain the reusable backbone.

---

## 2. Architecture overview

The engine is a **deterministic-first, three-layer pipeline** with Claude as a qualitative auditor — *not* a price predictor. The spine is asset- and account-agnostic; only the adapters and policies hanging off it change between books.

```
                         ┌─────────────────────────────────────────┐
                         │           PORTFOLIO MANIFEST              │
                         │  (books: ISA / GIA / SIPP, NAV, rules)    │
                         └────────────────────┬────────────────────┘
                                              │  for each book:
                                              ▼
   LAYER 1                LAYER 2                 LAYER 3
 ┌──────────────┐      ┌──────────────┐      ┌────────────────────┐
 │ Macro Gate   │ pass │ Quant Scanner│ topN │ Claude Auditor     │
 │ (0–100,      │─────▶│ (deterministic│─────▶│ (qualitative score │
 │  class-      │      │  ranking)    │      │  via API, reviews  │
 │  specific)   │      └──────────────┘      │  fundamentals/risk)│
 └──────────────┘                            └─────────┬──────────┘
         │ if gate < threshold: hold cash               │
         │                                    Blended score = 0.60·Quant + 0.40·Claude
         ▼                                              ▼
                          ┌───────────────────────────────────────┐
                          │ Risk + Sizing (NAV %, gate-scaled,     │
                          │ drawdown/daily caps, per-book rules)   │
                          └────────────────────┬──────────────────┘
                                               ▼
                          ┌───────────────────────────────────────┐
                          │ Execution Adapter → IBKR               │
                          │ (approval-gated; paper first)          │
                          └───────────────────────────────────────┘
                                               │
                                               ▼
                          ┌───────────────────────────────────────┐
                          │ Trade ledger (SQLite) + performance    │
                          │ scoring (Sharpe, max drawdown)         │
                          └───────────────────────────────────────┘

      WEEKEND (offline): GPU walk-forward + Monte Carlo → PROPOSE params → human approves → config
```

### What generalises vs what is book-specific

| Component | Universal? | Notes |
|---|---|---|
| Three-layer spine (gate → scan → audit) | ✅ | Only inputs change per asset class |
| Risk manager, NAV sizing, ledger, Sharpe/drawdown scoring | ✅ | Asset-agnostic |
| Weekend GPU backtest/optimisation loop | ✅ | Asset-agnostic |
| Instrument permissions | ❌ | Hard rule per book (options/FX barred from ISA/SIPP) |
| Tax policy | ❌ | Null in wrappers; UK CGT in GIA only |
| Execution units (shares/notional vs pips/leverage) | ❌ | Per adapter |
| Layer 3 auditor prompt | ❌ | Strong for equities; thinner for FX (Section 12) |

---

## 3. The "book" abstraction (define on day one)

Code the engine against these interfaces, never against equity-specific assumptions. Implement only the equity/IBKR concretes now; Forex later becomes a new adapter, not a rewrite.

```python
from typing import Protocol
from dataclasses import dataclass, field

@dataclass
class AccountContext:
    book_id: str                 # e.g. "ibkr_isa_equity"
    wrapper: str                 # "ISA" | "SIPP" | "GIA" | "MARGIN"
    broker: str                  # "IBKR"
    ibkr_account_id: str         # e.g. "U1234567" (the ISA sub-account string)
    allowed_assets: set          # {"EQUITY","ETF"} for ISA/SIPP; {"FX"} for an FX GIA book
    tax_policy: "TaxPolicy"      # NullTaxPolicy() in wrappers; UkCgtPolicy() in GIA
    sizing: "SizingPolicy"       # NAV %, leverage caps, unit type
    nav: float = 0.0             # refreshed live from broker

class TaxPolicy(Protocol):
    def estimate(self, gain: float, ctx: AccountContext) -> dict: ...   # {} when Null

class SizingPolicy(Protocol):
    def size(self, candidate, ctx: AccountContext, gate_score: float): ...

class AssetAdapter(Protocol):                 # one per asset class
    asset_class: str
    def macro_gate(self) -> float: ...        # 0–100, class-specific inputs
    def scan(self, universe) -> list: ...     # deterministic ranked candidates
    def auditor_prompt(self, candidate) -> str: ...   # what Claude reviews

class BrokerAdapter(Protocol):                # IBKR connector OR ib_async OR (future) OANDA
    def refresh_nav(self, ctx: AccountContext) -> float: ...
    def positions(self, ctx: AccountContext) -> list: ...
    def place(self, order, ctx: AccountContext) -> dict: ...   # paper first; approval-gated live
```

### Generic engine loop (stays identical across all books)

```python
def run_cycle(books, adapters, broker, claude, cfg):
    for ctx in books:
        adapter = adapters[(ctx.broker, _asset_for(ctx))]
        gate = adapter.macro_gate()
        log(f"[{ctx.book_id}] macro gate = {gate:.0f}")
        if gate < cfg.gate_min:                       # e.g. < 40 → hold cash
            log(f"[{ctx.book_id}] gate below floor — no new buys")
            continue

        candidates = adapter.scan(cfg.universe_for(ctx))[: cfg.top_n]
        for c in candidates:
            if c.asset_class not in ctx.allowed_assets:    # HARD permission rule
                continue
            claude_score = claude.audit(adapter.auditor_prompt(c))   # 0–100
            blended = 0.60 * c.quant_score + 0.40 * claude_score
            if blended < cfg.exec_threshold:               # e.g. < 75
                continue
            order = ctx.sizing.size(c, ctx, gate_score=gate)
            broker.place(order, ctx)                        # paper / approval-gated
            ledger.record(ctx, c, order, blended, gate)
```

### Sample portfolio manifest (`portfolio.yaml`)

```yaml
gate_min: 40            # below this, hold cash
exec_threshold: 75      # blended score required to act
top_n: 10
books:
  - book_id: ibkr_isa_equity
    wrapper: ISA
    broker: IBKR
    ibkr_account_id: "U_ISA_PLACEHOLDER"
    allowed_assets: ["EQUITY", "ETF"]
    tax_policy: null            # tax-free wrapper
    sizing: { type: nav_pct, max_per_position_pct: 8, leverage: 1.0, unit: shares }
  - book_id: ibkr_sipp_equity
    wrapper: SIPP
    broker: IBKR
    ibkr_account_id: "U_SIPP_PLACEHOLDER"
    allowed_assets: ["EQUITY", "ETF"]   # long-term ETFs preferred
    tax_policy: null            # tax-sheltered
    sizing: { type: nav_pct, max_per_position_pct: 6, leverage: 1.0, unit: shares }
  - book_id: ibkr_gia_equity
    wrapper: GIA
    broker: IBKR
    ibkr_account_id: "U_GIA_PLACEHOLDER"
    allowed_assets: ["EQUITY", "ETF"]
    tax_policy: uk_cgt          # ACTIVE here only
    sizing: { type: nav_pct, max_per_position_pct: 8, leverage: 1.0, unit: shares }
```

---

## 4. Scope for the first build

**In scope:** IBKR broker adapter, equity/ETF asset adapter, ISA + SIPP + GIA books, paper trading, the three layers, NAV sizing, deterministic risk guardrails, SQLite ledger, performance scoring, local terminal dashboard, weekend GPU backtest that *proposes* (never auto-applies) parameters.

**Explicitly out of scope (for now):** options trading, Forex, fully autonomous no-approval live execution, self-modifying live code, Telegram/Ngrok control, any SaaS/multi-user features, Firebase/Canva frontends.

---

## 5. Local environment setup (Windows 11 / RTX 3080 Ti)

1. **WSL2 (Ubuntu).** Run all Python loops, loggers, and the database inside WSL2 — not native Command Prompt. Claude Cowork/Code works cleanly inside WSL2.
2. **NVIDIA CUDA Toolkit inside WSL2** so backtests can offload to the 3080 Ti (12 GB VRAM). Use the GPU for weekend grid-search / Monte Carlo only — it is not needed for live cycles.
3. **Python 3.11+**, virtual environment, `pip`/`uv`.
4. **IBKR access — two paths:**
   - **Path A (preferred, approval-gated):** Use the official IBKR ↔ Claude connector via Claude's connector marketplace. AI-drafted orders land in the IBKR "AI Instructions" tab for manual approval. No local gateway, no keys shared.
   - **Path B (local, for later autonomy):** IB Gateway on Windows host. Configure → API → Settings: enable ActiveX and Socket Clients; socket port `4002` for **paper** (`7496` live); add Trusted IPs `127.0.0.1` and the WSL2 range `172.0.0.0/8`; leave ReadOnly **unchecked** only when intentionally enabling execution. Connect via `ib_async`.
5. **Downtime protection** (only relevant once running unattended): UPS battery backup, disable Windows auto-restart/active-hours reboots, set power to "Never Sleep."
6. **Start in paper mode** on both paths. Confirm orders appear correctly in the native IBKR mobile app before considering live.

---

## 6. Repository structure

```
nova-engine/
├── CLAUDE.md                    # condensed build rules (Section 11) for Cowork/Code
├── portfolio.yaml               # the manifest (Section 3)
├── config.yaml                  # gate_min, thresholds, universe, API settings
├── requirements.txt
├── core/
│   ├── engine.py                # generic run_cycle loop
│   ├── context.py               # AccountContext, policies, protocols
│   ├── risk.py                  # deterministic guardrails + NAV sizing
│   └── ledger.py                # SQLite trade ledger + performance scoring
├── adapters/
│   ├── asset_equity.py          # EquityAdapter (macro_gate, scan, auditor_prompt)
│   ├── broker_ibkr.py           # IBKRAdapter (connector path + ib_async path)
│   └── (future) asset_fx.py     # FxAdapter — Section 12
├── layers/
│   ├── macro_gate.py            # equity macro inputs (VIX, breadth, credit spreads)
│   ├── scanner.py               # deterministic momentum/mean-reversion ranking
│   └── analyst.py               # Claude API auditor (qualitative score)
├── tax/
│   └── uk_cgt.py                # £3,000 AEA, 18%/24% rates — GIA only
├── ui/
│   └── dashboard.py             # local rich/terminal dashboard
├── backtest/
│   ├── walk_forward.py          # GPU-accelerated, weekend
│   └── monte_carlo.py           # drawdown probability
└── tests/                       # >90% coverage on core/, risk/, tax/
```

---

## 7. The three layers (equity build)

**Layer 1 — Macro Gate (deterministic, 0–100).** Pull broad-market risk metrics (e.g. VIX level and term structure, market breadth, high-yield credit spreads). Blend into a single 0–100 composite. ≥70 → full sizing; 40–70 → scaled sizing (e.g. 60%); <40 → no new buys. Fully backtestable; never changes its own logic at runtime.

**Layer 2 — Quant Scanner (deterministic).** If the gate passes, rank the universe by objective mathematical rules (e.g. sector-relative momentum percentile, mean-reversion thresholds). Output a 5–10 ticker shortlist with a numeric `quant_score`.

**Layer 3 — Claude Auditor (qualitative, via API).** For each shortlisted name, fetch the last ~4 quarters of raw financials and pass them to Claude with instructions to score earnings quality and flag hidden risks (debt, margin deterioration, red flags). Claude acts as a "hole-poker," **not** a price oracle. Output 0–100.

**Blend:** `Final = 0.60 × quant_score + 0.40 × claude_score`. Act only above the execution threshold.

> Use the Anthropic API for Layer 3. Keep prompts tight and structured; require a numeric score plus a short rationale. Log model, prompt, and response for every audit (auditable decision trail).

---

## 8. Risk management & sizing

- **NAV-based sizing**, scaled by the macro gate (replaces the old £100 budget logic entirely). Example: base risk = X% of book NAV per position, multiplied by the gate's capacity factor.
- **Per-book caps** from the manifest (`max_per_position_pct`, leverage = 1.0 in wrappers).
- **Deterministic guardrails (hard stops):** max drawdown limit → pause new buys; daily loss cap; max concurrent positions; correlation check to avoid over-exposure.
- **Bracket orders:** attach stop-loss and take-profit on entry; never rely on a separate script to close losers.
- **Permission enforcement:** the engine must refuse any order whose asset class is not in the book's `allowed_assets` (prevents an options/FX order ever hitting an ISA/SIPP).

---

## 9. Safety & governance (non-negotiable)

1. **Paper first** — two clean weeks minimum before any live capital.
2. **Human approval gate** — via the IBKR connector's AI Instructions tab (Path A) or an explicit confirm step (Path B). No silent live execution in the first build.
3. **No auto-promotion of backtested parameters.** The weekend optimiser writes *proposals* to a review file; a human approves the diff before it reaches live `config.yaml`.
4. **Heartbeat + kill switch** — alert/log if the broker connection drops >30s; a single command halts all new activity.
5. **Never log credentials or account secrets.**
6. **SIPP caution** — confirm the SIPP administrator permits automated/frequent trading before enabling that book live; some restrict it.

---

## 10. Weekend GPU optimisation loop

Every weekend (markets closed), use the 3080 Ti to: pull the week's ledger, run **walk-forward validation** across rolling historical windows (guards against overfitting), run **Monte Carlo** trade-sequence shuffles (estimates catastrophic-drawdown probability), and model transaction costs/slippage. Output: a proposed parameter set + expected impact. **A human reviews and approves before anything goes live.**

---

## 11. CLAUDE.md — condensed rules for Cowork/Code

```markdown
# Nova Engine — Build Rules
- Build IBKR + equities first. Paper trading only until told otherwise.
- One engine, many books. Code against the AccountContext/Adapter/Policy
  interfaces — never hard-code equity or IBKR assumptions into core/.
- Tax module (uk_cgt.py) is active ONLY for GIA. £3,000 AEA, 18%/24% rates.
  Inside ISA/SIPP, tax_policy is null.
- Refuse any order whose asset class is not in the book's allowed_assets.
- NAV-based sizing scaled by the macro gate. No "£100 monthly" logic.
- Three layers: deterministic gate → deterministic scanner → Claude auditor
  (qualitative, NOT price prediction). Blend 60/40.
- Every function: type hints, docstrings, error handling. Use Decimal for money.
- Never log credentials. Never auto-promote backtested params to live.
- >90% test coverage on core/, risk/, tax/.
- Acceptance for Phase 1: engine runs a full paper cycle across ISA/SIPP/GIA
  books, enforces permissions, logs to SQLite, and renders the dashboard.
```

---

## 12. Forex fork (future — do not build yet)

When ready, Forex is additive, not a rewrite:

- Add `adapters/asset_fx.py` (`FxAdapter`): macro gate reads DXY trend, rate differentials, risk-on/off proxies (e.g. AUD/JPY), central-bank calendar; scanner uses FX momentum/mean-reversion; **Layer 3 auditor is thinner** — it reviews positioning, central-bank guidance, and event risk rather than fundamentals (be honest: a weaker edge than equities).
- FX books are **GIA / margin only** (never ISA/SIPP). Tax policy = UK CGT (or note spread betting is CGT-free but not API-automatable this way).
- Reuse `IBKRAdapter` (IBKR trades spot FX) or add an `OANDAAdapter`.
- Execution units switch to pips/leverage via the book's `SizingPolicy`.
- **No core engine changes.**

---

## 13. Phased roadmap

| Phase | Goal | Done when |
|---|---|---|
| 0 | Env: WSL2 + CUDA + IBKR paper (connector and/or Gateway) | Paper connection verified; NAV reads back |
| 1 | Core skeleton: interfaces, engine loop, manifest, SQLite ledger | Full paper cycle runs across ISA/SIPP/GIA; permissions enforced |
| 2 | Layer 1 macro gate (live data) + Layer 2 scanner | Gate scales sizing; scanner returns ranked shortlist |
| 3 | Layer 3 Claude auditor + 60/40 blend | Audited, blended scores drive paper orders; decisions logged |
| 4 | Risk guardrails + NAV sizing + dashboard | Drawdown/daily caps trigger; dashboard live; >90% test coverage |
| 5 | Weekend GPU walk-forward + Monte Carlo (propose-only) | Proposals written to review file; no auto-apply |
| 6 | Two clean paper weeks → consider live (approval-gated) | Positive risk-adjusted paper results; human sign-off |
| 7+ | Forex fork (Section 12) | FxAdapter added with zero core changes |

---

## 14. Migration context (background, runs in parallel)

FreeTrade has no API and cannot be automated, so funds migrate to IBKR. Use **in-specie transfers** (whole shares move without selling; fractional remainders are liquidated to cash). ISA → IBKR ISA via official ISA transfer; SIPP → IBKR SIPP via an IBKR-approved UK SIPP administrator. Typical timeline 3–6 weeks — use that window to build and paper-test. All three (ISA/SIPP/GIA) appear under one IBKR login via linked accounts, each with its own account ID string for the manifest.

---

*End of specification. Build Phase 0 → Phase 1 first. Confirm paper connectivity before writing any execution code.*
