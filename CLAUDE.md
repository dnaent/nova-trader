# Nova Engine — Build Rules
- Build IBKR + equities first. Paper trading only until told otherwise.
- **CRITICAL**: Universal AI analyzes 32+ indicators at TOP LEVEL across ALL books (GIA, ISA, SIPP, Forex)
- One engine, many books. Code against the AccountContext/Adapter/Policy
  interfaces — never hard-code equity or IBKR assumptions into core/.
- **Universal Intelligence**: All 32 markers (RSI, MACD, HMM, VIX, correlations, etc.) analyzed for EVERY asset class and book type
- Tax module (uk_cgt.py) is active ONLY for GIA. £3,000 AEA, 18%/24% rates.
  Inside ISA/SIPP, tax_policy is null.
- Refuse any order whose asset class is not in the book's allowed_assets.
- NAV-based sizing scaled by the macro gate. No "£100 monthly" logic.
- Three layers: deterministic gate → deterministic scanner → Claude auditor
  (qualitative, NOT price prediction). Blend 60/40.
- **Cross-Asset Correlation**: Real-time analysis across ALL books and asset types
- Every function: type hints, docstrings, error handling. Use Decimal for money.
- Never log credentials. Never auto-promote backtested params to live.
- >90% test coverage on core/, risk/, tax/.
- Acceptance for Phase 1: engine runs a full paper cycle across ISA/SIPP/GIA/FOREX
  books, enforces permissions, logs to SQLite, and renders the dashboard.

## Phase 2 & 3 Additions
- **Continuous Sizing**: `gate_capacity` scales continuously from 70 to 40 instead of hard discrete steps.
- **Aggressive Liquidation**: If `aggressive_liquidation` is True in config, dropping below the `gate_min` will actively execute `SELL` orders for open positions to move to cash.
- **HMM Integration**: The Macro Gate blends VIX contango, Cross-Asset Correlation, and a Gaussian HMM (using *only* online filtered probabilities to prevent lookahead bias).
- **Multi-API Auditor**: Layer 3 supports `local` (Ollama/OpenAI compatible), `anthropic`, and `gemini` backends. The "Inference Context Bundle" (Macro markers + trailing 4Q financials) acts as the standardized prompt across all models.

## AI Model Training Requirements (3080Ti Deployment) - COMPREHENSIVE CONTEXT

> **⚠️ SUPERSEDED in part:** the success metrics in this older section (75%-win-everywhere, 95% composite, 0.8ms latency) are **superseded by "CONFIRMED ARCHITECTURE DECISIONS (2026-06-14)"** at the end of this file — see the per-book success profiles there for the authoritative validation criteria. The "all 32 markers / cross-asset / multi-book context" intent below still holds.

### **CRITICAL: AI Model Must Be Context-Aware of Full Project Scope**

#### **Universal Intelligence Training Dataset**:
- **32+ Indicators**: Model trained on all technical, fundamental, macro, and risk indicators
- **Cross-Asset Learning**: Simultaneous training on equities, forex, bonds, commodities data
- **Multi-Book Awareness**: Understanding of GIA, ISA, SIPP, Forex account types and tax implications
- **Ultra-Low Latency Context**: Model optimized for sub-millisecond decision making (0.8ms target)
- **Hardware Optimization**: Training specifically for 3080Ti inference with kernel bypass awareness

#### **Training Protocol & Performance Targets**:
- **Primary Model**: Local LLaMA-based model running on 3080Ti via Ollama
- **Universal Validation**: Paper trading across ALL asset classes (equities, forex, bonds) and ALL books (GIA, ISA, SIPP, Forex)
- **Enhanced Success Criteria (6-Metric Validation)**:
  - **Win Rate**: 75%+ across ALL books and asset classes (Weight: 25%)
  - **Sharpe Ratio**: ≥1.0 for risk-adjusted performance (Weight: 25%)
  - **Max Drawdown**: ≤5% capital protection across ALL books (Weight: 20%)
  - **Trade Sample**: Minimum 200 trades across ALL asset classes (Weight: 15%)
  - **Consecutive Losses**: ≤5 trades risk management (Weight: 10%)
  - **Profit Factor**: ≥1.25 gross profit efficiency (Weight: 5%)
- **Composite Score**: ≥95% weighted performance before live authorization

#### **Ultra-Low Latency Training Context**:
- **Speed Requirements**: Model trained to make decisions within 0.8ms IBKR execution pipeline
- **Hardware Awareness**: Understanding of CPU affinity, memory locking, kernel bypass
- **Latency Optimization**: Training on high-frequency data with microsecond timestamps
- **Performance Monitoring**: Real-time latency tracking integration in training loop

#### **Cross-Asset Intelligence Training**:
- **Market Regime Detection**: HMM models trained on SPY, VIX, bond correlations
- **Multi-Timeframe Analysis**: 5-minute, 1-hour, daily chart coordination training
- **Correlation Awareness**: Training on 90-day Pearson matrices across ALL asset classes
- **Risk Management**: Training on portfolio-wide exposure and concentration limits

#### **Context-Aware Learning Objectives**:
- **Tax Optimization**: Model understanding of UK CGT, ISA, SIPP tax implications
- **Regulatory Compliance**: Training on UK investment rules and account restrictions
- **Professional Trading Standards**: Model trained to institutional-grade performance benchmarks
- **Risk-First Design**: Primary objective is capital preservation, secondary is profit maximization

## 🌐 GOOGLE CLOUD PLATFORM INFRASTRUCTURE (PREFERRED)

### **Cloud Architecture & Deployment Strategy**
- **Platform**: Google Cloud Platform (GCP) - preferred over AWS for EU operations
- **Region**: Europe-West2 (London) for GDPR compliance and UK market proximity
- **Compute**: Hybrid approach with local 3080Ti edge inference + GCP services

### **Core GCP Services Integration**:
```
🔥 COMPUTE & DEPLOYMENT:
├── Compute Engine: High-performance VM instances for 3080Ti deployment
├── Cloud Run: Serverless containers for API services (ultra-low latency)
├── Google Kubernetes Engine: Container orchestration for scalable infrastructure
└── Cloud Functions: Event-driven market data processing

💾 STORAGE & DATABASES:
├── Cloud SQL: PostgreSQL for transaction history and audit logs
├── Firestore: NoSQL for real-time market data and user sessions
├── Cloud Storage: AI model artifacts, backups, static assets
└── Memorystore: Redis for ultra-low latency caching (sub-millisecond)

🤖 AI/ML & ANALYTICS:
├── Vertex AI: Model training, deployment, and monitoring
├── AI Platform: Custom model serving for local 3080Ti integration
├── BigQuery: High-performance analytics for trading pattern analysis
└── Cloud Monitoring: Real-time performance and latency tracking

🔐 SECURITY & COMPLIANCE:
├── Cloud IAM: Fine-grained access control for trading operations
├── Secret Manager: Secure credential storage for broker APIs
├── VPC Networks: Private networking for trading infrastructure
├── Cloud Armor: DDoS protection and security policies
└── Audit Logs: Comprehensive compliance tracking

🌐 REAL-TIME & NETWORKING:
├── Cloud Pub/Sub: Real-time message streaming for market data
├── Cloud Load Balancing: Global load balancing for trading endpoints
├── Cloud CDN: Content delivery optimization
└── Network Service Tiers: Premium tier for ultra-low latency
```

### **Deployment Pipeline**:
```bash
# Deploy to GCP Cloud Run for production scalability
gcloud run deploy trading-engine --image gcr.io/nova-trader/engine:latest
gcloud run deploy ai-inference --image gcr.io/nova-trader/ai:latest
gcloud sql instances create nova-trader-db --database-version=POSTGRES_13
```

### **Cost Optimization & Scaling**:
- **Sustained Use Discounts**: Automatic discounts for long-running workloads
- **Preemptible Instances**: Cost-effective compute for non-critical operations
- **Auto-scaling**: Cloud Run scales from 0 to thousands of instances automatically
- **European Data Residency**: GDPR compliance with data sovereignty

### **Integration Benefits**:
- **Local 3080Ti**: Ultra-fast edge inference for microsecond decisions
- **Cloud Services**: Scalable infrastructure for data processing and storage
- **Hybrid Performance**: Best of both worlds - edge speed + cloud scale
- **Enterprise Security**: Bank-grade security with GCP enterprise features

### **🚀 HYBRID EDGE-CLOUD AI MODEL ARCHITECTURE**

#### **Training-to-Deployment Pipeline** (BREAKTHROUGH APPROACH):
```
📍 PHASE 1: Local 3080Ti Edge Training
├── LLaMA model trained locally via Ollama
├── Paper trading dataset generation (200+ trades)
├── Training data logging to SQLite + secure backup
└── Validation metrics tracking (6-metric system)

🔄 PHASE 2: Training Data Transfer
├── Encrypted training dataset export from 3080Ti
├── Secure upload to GCP Cloud Storage
├── Vertex AI ingestion and model replication
└── Performance baseline verification

☁️ PHASE 3: Cloud Deployment with Zero Performance Loss
├── Vertex AI model deployment (identical to local)
├── Training data context preserved
├── Performance parity validation
└── Live trading enablement
```

#### **Technical Implementation Strategy**:
```python
# Local 3080Ti Training Data Export
class TrainingDataExporter:
    def export_training_dataset(self):
        """Export comprehensive training dataset for cloud replication"""
        return {
            "model_weights": self.local_model.state_dict(),
            "training_history": self.paper_trading_logs,
            "performance_metrics": self.validation_scores,
            "market_context": self.market_regime_data,
            "decision_patterns": self.ai_decision_log
        }

# GCP Vertex AI Model Replication
class VertexAIModelReplicator:
    def replicate_local_model(self, training_data):
        """Create identical model in Vertex AI with preserved performance"""
        # Deploy with identical architecture and training context
        # Ensure zero performance degradation
```

#### **Performance Preservation Strategy**:
- **Identical Architecture**: Vertex AI model mirrors exact 3080Ti configuration
- **Complete Context Transfer**: Full training dataset and decision patterns
- **Performance Validation**: Side-by-side comparison before live deployment
- **Fallback Capability**: Local 3080Ti remains available for critical operations

#### **Benefits of Hybrid Approach**:
🔥 **Ultra-Low Latency**: Local inference maintains sub-30ms execution
☁️ **Cloud Scalability**: Vertex AI provides enterprise-grade scaling
📊 **Training Continuity**: Model learns continuously in both environments
🛡️ **Risk Mitigation**: Dual deployment provides redundancy and reliability
💰 **Cost Efficiency**: Optimize compute costs between edge and cloud
🌍 **Global Reach**: Cloud deployment enables worldwide accessibility

## CRITICAL: Technical Feasibility & Optimization Requirements (2026-06-11)

### **CLAUDE FABLE OPTIMIZATION MANDATE**
- **Feasibility Scrutiny**: Complete technical analysis available in `NOVA_TRADER_FEASIBILITY_SCRUTINY.md`
- **Reality Calibration Required**: Current performance targets need systematic adjustment
- **3080Ti Deployment**: Must address computational and latency constraints

### **IMMEDIATE OPTIMIZATION PRIORITIES**:
1. **Latency Targets Adjustment**:
   - Current 0.8ms claim → Realistic 15-30ms (still excellent for retail)
   - Market data processing: 5ms (vs 0.12ms claim)
   - Order execution pipeline: 15ms total (vs 0.8ms claim)

2. **AI Performance Recalibration**:
   - Win rate: 60-70% (vs 75% claim) - more realistic for industry standards
   - Sharpe ratio: 0.8 (vs 1.0 claim) - achievable with proper risk management
   - Max drawdown: 8% (vs 5% claim) - realistic for retail trading
   - Composite validation: 80% (vs 95% claim) - still above industry 70%

3. **Universal Intelligence Optimization**:
   - Tiered indicator system: 8-12 core indicators initially (vs all 32)
   - Smart selection based on market conditions and computational resources
   - Progressive rollout: Phase 1 (core) → Phase 2 (enhanced) → Phase 3 (advanced)

### **CLAUDE FABLE ACTION ITEMS**:
- **Phase 1**: Reality calibration of all performance targets and documentation
- **Phase 2**: Implementation of tiered indicator system with smart selection
- **Phase 3**: Market regime-based adaptive performance scaling
- **Success Criteria**: Achieve realistic targets consistently before live deployment

### **TECHNICAL CONSTRAINTS ACKNOWLEDGMENT**:
- **Python overhead**: Interpreted language limits vs C++/FPGA HFT systems
- **Network latency**: Home internet to IBKR servers introduces 5-20ms minimum
- **Computational complexity**: 32+ indicators across all assets requires optimization
- **Market reality**: 95% of retail algorithmic trading attempts fail - conservative approach essential

## Phase 4 & 5 Additions
- **Risk Guardrails**: Deterministic rules integrated directly into `core/engine.py` using the `RiskGuardrails` dataclass. Tracks Max Drawdown and Daily Loss Caps directly via the `nav_history` ledger. Evaluated *per-book* dynamically.
- **Mathematical Correlation**: The engine enforces a strict mathematical correlation check. `check_correlation()` in `core/risk.py` uses `yfinance` to compute a 90-day Pearson correlation matrix against all open positions to prevent over-exposure.
- **Terminal Dashboard**: A live terminal UI built with `rich` (`ui/dashboard.py`). It must remain decoupled from the engine process, reading strictly from the SQLite database to avoid latency in the engine loop.
- **Fault-Tolerance**: The engine is fully fault-tolerant against external API disconnects (yfinance failures, LLM timeouts). It gracefully falls back to a 50.0 score or default state without crashing the main loop.

## SaaS UI Infrastructure (COMPLETED 2026-06-11) - ULTRA-LOW LATENCY FOCUSED

### **CRITICAL: Speed is Everything in Trading - 0.8ms Target Pipeline**

- **Design System**: Transitioned from Obsidian Glassmorphic to **Material-UI Joy** professional trading interface
- **Ultra-Low Latency Focus**: ALL UI components optimized for zero-delay trading operations targeting 0.8ms IBKR execution
- **Performance Specifications**:
  - Order Execution: <0.8ms to IBKR TWS Gateway
  - Market Data Latency: <0.12ms feed processing
  - UI Response Time: <16ms for critical trading operations
  - Memory Footprint: <1GB RAM for entire system
  - CPU Utilization: <10% on dedicated cores
- **Hardware Optimization Ready**: Kernel bypass, CPU affinity, memory locking guidance integrated
- **Trading Infrastructure**: Complete broker API integration, latency monitoring, and AI model validation systems
- **AI Safety Protocol**: Local 3080Ti model with mandatory 95% composite score across ALL asset classes before live deployment

### Completed Infrastructure (MacBook Pro → 3080Ti Handoff Ready):
1. **Trading Broker API Settings** (`saas_ui/src/components/TradingBrokerSettings.tsx`):
   - IBKR TWS Gateway connection (localhost:7497 paper, 7496 live)
   - Alpaca, TD Ameritrade multi-broker support
   - Paper/Live environment switching with safety warnings
   - Encrypted API credentials storage
   - Real-time connection testing and status monitoring
   - Auto-connect configuration for startup

2. **Ultra-Low Latency Monitor** (`saas_ui/src/components/LatencyMonitor.tsx`):
   - Sub-millisecond pipeline tracking (0.8ms target IBKR)
   - Hardware optimization controls: kernel bypass, CPU affinity, memory locking
   - Real-time latency metrics: market data, order execution, network RTT
   - Performance alerts and optimization recommendations
   - Co-location and hardware upgrade guidance

3. **Modern Dashboard System** (`saas_ui/src/components/Dashboard.tsx`):
   - Material-UI Joy component architecture
   - Bento Grid layout for data portability
   - Light/Dark mode optimized for trading workflows
   - AI Copilot integration for market intelligence
   - Professional Inter font typography and 8px grid system
   - Tab navigation: Overview, Order Management, Risk Monitor, AI Training, Analytics, Broker APIs, Latency Monitor, Engine Config

4. **AI Copilot** (`saas_ui/src/components/AICopilot.tsx`):
   - Market regime analysis with confidence scoring
   - Real-time trading insights and recommendations
   - Minimizable interface that stays out of the way
   - Risk assessment and opportunity identification

5. **Bento Grid Layout** (`saas_ui/src/components/layout/BentoGrid.tsx`):
   - Multi-sized cards for spatial organization
   - Responsive grid system with visible orientation guides
   - Professional data portability

### Development Status:
- **Environment**: MacBook Pro infrastructure complete
- **Theme System**: Material-UI with custom Nova branding
- **Component Library**: All trading UI components implemented
- **Performance**: Optimized for ultra-low latency operations
- **AI Model Integration**: Local 3080Ti training and validation system complete
- **Ready for 3080Ti**: Complete handoff package prepared with AI safety protocols

### AI Model Safety & Validation (FINAL STATUS):
6. **AI Model Training Dashboard** (`saas_ui/src/components/AIModelTraining.tsx`):
   - Local LLaMA-based model training interface for 3080Ti deployment
   - Paper trading validation with 75%+ win rate requirement across all books
   - Real-time performance tracking: win rate, Sharpe ratio, drawdown monitoring
   - Multi-book validation for GIA, ISA, SIPP account segregation
   - Live trading safety gate - physically locked until validation criteria met
   - Minimum 200 paper trades required before live trading approval
   - Continuous learning system with risk-adjusted performance feedback
   - Emergency stop integration (F12 key) for immediate trading halt
   - Model performance charts and trade history logging
   - Hardware-specific optimization for NVIDIA RTX 3080Ti inference

## UI/UX & Developer Skills Guidelines
- **Developer Skills**: Repository-specific automation workflows are defined under the `skills/` directory. Each skill folder contains a `SKILL.md` defining its operational rules (e.g. [backtest-optimization](file:///Users/Phantom/Desktop/DNAENT™/Nova_Trader/skills/backtest-optimization/SKILL.md), [ledger-audit](file:///Users/Phantom/Desktop/DNAENT™/Nova_Trader/skills/ledger-audit/SKILL.md)).

## CONFIRMED ARCHITECTURE DECISIONS (2026-06-14)

These supersede earlier conflicting notes where they overlap.

### Two-tier model hierarchy (parent → child)
- **Local model = PARENT.** Runs on the Windows RTX 3080 Ti, trades the operator's **personal portfolio**, connects to IBKR for low-latency real-time data + execution, and runs a continuous-learning protocol. It is expected to stay slightly ahead of the cloud child.
- **Cloud model (Claude / Vertex AI) = CHILD.** Powers the SaaS product. **Never touches IBKR.** It consumes the **training data the parent logs** (the `core/ledger.py` decision/trade/NAV store) — parent generates, child reads.
- **The engine code is identical for both.** Productization is a **backend swap via dependency injection, NOT a fork**: the `Auditor` (`layers/analyst.py`), `BrokerAdapter`, and storage are pluggable. Local = Ollama + ib_async + SQLite; SaaS = Vertex endpoint + per-tenant broker + cloud DB.

### IBKR access
- Only the **local/parent** model connects to IBKR, via the `gateway` (ib_async → TWS/IB Gateway) path in `adapters/broker_ibkr.py`.
- **Do NOT build IBKR's official Claude connector (`claude_connector`).** Not needed under this design.
- Operator **has real-time IBKR market-data subscriptions** — the feed targets true real-time, with yfinance kept only as fallback.
- Resource-intensive infrastructure is justified **only when it improves the local model's performance** (low-latency data, training throughput).

### HARD safety gate — paper until validated
- **No personal-portfolio / live trading occurs until the local model is trained on paper trading to a per-book success rate the operator is satisfied with, AND the operator explicitly authorizes going live.** Enforced by: `IBKRAdapter` refusing `mode="live"` with the stub, paper-as-default, the AI Training dashboard live-lock, and the new per-book validation gate.

### Per-book success criteria (replaces the single global 6-metric composite)

**Universal floor (all books):** positive net expectancy after costs + tax (i.e. profit factor > 1 — "make more than you lose"), proven on a statistically meaningful sample that survives **walk-forward + Monte Carlo** (`backtest/walk_forward.py`, `backtest/monte_carlo.py`) so it isn't overfit. All claims are *historically-validated* results — never "100%", never a forward guarantee.

**Wrapper ⊥ Strategy (asset location):** the tax wrapper (tax/contribution/access) is independent of the strategy (risk/reward profile). Only **leveraged Forex is wrapper-locked** (GIA/margin, not ISA/SIPP-eligible). Tax-optimal placement = aggressive/high-turnover strategies in tax-free wrappers (ISA), tax-efficient long-holds in the taxable GIA.

Four distinct success profiles, one per book:

| Book | Profile | Primary "trained correctly" signal | Risk rails | Min sample |
|---|---|---|---|---|
| **SIPP** | Income / Compounding (locked pension) | **Win rate ≥70% + Max DD ≤5%** + long-horizon CAGR; dividends **reinvested** | tightest drawdown; lowest turnover | 150 |
| **ISA** | Growth / High-Reward (tax-free) | **Profit factor ≥1.6 + positive expectancy**; realize freely (no CGT) | DD ≤18%; Sortino ≥1.0; win rate ≥45% (honest, not forced) | 200 |
| **GIA** | Tax-Efficient Core | **After-tax return ≥ benchmark + low turnover**; tax-alpha via loss-harvesting + £3k AEA; long holds defer the CGT event | DD ≤10%; win rate ≥60% | 150 |
| **Forex** | Style-agnostic, account-level | **MAR/Calmar + Sortino ≥1.0 + profit factor ≥1.5** | leverage ≤5:1; per-trade risk ≤2%; max consec losses ≤6; DD ≤20% | 300 |

- **Forex is judged at the ACCOUNT/equity-curve level, not the trade level.** Win rate and reward:risk are interchangeable style choices (scalp: many tiny wins; swing: few big wins) that net the same result — so they are **logged for transparency but NOT gated**. The model finds its own style; we judge whether the account compounds safely.
- **GIA tax-efficiency:** UK CGT has no long-hold discount, but holding longer **defers** the taxable event (gains compound pre-tax). The model learns to minimize unnecessary realizations in the GIA, while realizing freely in the tax-free ISA.
- A book graduates paper→live only when **its own** profile passes.

### Model dataset / training objective
Four training objectives, one per book profile. The **wrapper is a context feature** (tax rate, access lock, AEA headroom) so the model times realizations correctly per book. A "good decision" label = the book's primary signal: e.g. in Forex a *losing* trade that respected the 2% risk cap is still **good**; in GIA an unnecessary taxable realization is **bad** even if profitable. Each logged record: `{macro regime + marker snapshot, book_id, candidate, decision + scores, sizing, outcome (R-multiple, PnL, holding period, dividends, tax)}`.

**All 32 markers stay universal across every book.** They are the model's INPUTS (observed everywhere); the per-book success definitions are the OBJECTIVE (what a good decision means). The success profiles never prune markers — they change how the model *weights/interprets* the same 32 per book (e.g. SIPP leans on stability/trend markers, Forex on regime/ATR/momentum). NOTE the pipeline (as of 2026-06-15, roadmap #4 ✅): the 32-marker matrix (`data_loader.get_technical_features`) feeds the **ML scanner** (Layer 2), and the snapshot now also flows — via `Candidate.meta["markers"]` — into the **LLM auditor's Inference Context Bundle** (Layer 3, alongside macro + financials + news) and into the **parent model's training records** (`training_records` table). The marker snapshot is captured per audited candidate; trade outcomes (PnL, R-multiple) backfill on close.

### Build roadmap (ALL paper/read-only until each book is validated AND the operator authorizes live)
1. **Read-only IBKR real-time data feed** — ✅ **DONE & LIVE-VERIFIED (2026-06-15).** `adapters/ibkr_feed.py` (`IBKRDataFeed`) is a persistent, read-only (`readonly=True` — IBKR broker-enforces no orders) connection manager over `ib_async`. It supplies daily bars + snapshot prices and is injected into the hot path via `data_loader.set_price_feed()`: `get_daily_data()` tries the feed first and **falls back to yfinance** on any failure (proven by tests). Executes nothing.
   - **TWS vs IB Gateway — DECIDED (2026-06-15):** use **TWS now** (paper port **7497**) for dev/paper-validation visibility; ib_async is port-identical so switch to **IB Gateway** (paper 4002 / live 4001) for the always-on box later — config change only.
   - **TWS API enablement (done):** Global Config → API → Settings → Enable ActiveX and Socket Clients, Socket port 7497, Read-Only API checked, "Allow connections from localhost only". Must click **Apply/OK** for the socket to bind.
   - **Live verification:** connected (server v178, readonly, mktDataType=1). **Daily bars work for equity + FX** (the actual hot path) and **FX real-time snapshot works** (EURUSD). **US-equity real-time snapshot returns Error 10089** — needs a US securities market-data subscription enabled *for API* in IBKR Account Management; does NOT block the pipeline (engine uses the scanner's last close from daily bars, not `get_price()`). FX/historical unaffected.
2. **Wire the Forex book** — ✅ **DONE (2026-06-15).** `ibkr_forex_margin` book in `portfolio.yaml` (`wrapper: MARGIN` — kept distinct from GIA so margins are tunable per book; `tax_policy: uk_cgt`, `atr_sizing` leverage 5:1, per-trade risk 2%). `FxAdapter` registered alongside `EquityAdapter` in `core/engine.py`; FX pairs added to `config.yaml` under an asset-class-keyed `universe`; engine routes per asset class via `EngineConfig.universe_for(handles)`. `AtrSizing` leverage cap activated in `core/risk.py` (notional ≤ NAV × leverage).
3. **Per-book validation layer** — ✅ **DONE (2026-06-15).** `backtest/validation.py` encodes the four `BookProfile`s + the universal floor (profit factor > 1, survives `walk_forward.py` + `monte_carlo.py`). `validate_from_ledger(ctx, ledger)` reads closed PnLs / per-trade returns / NAV curve (new `Ledger.closed_returns` + `Ledger.nav_series`) and returns a per-criterion PASS/FAIL `ValidationResult`. Forex win-rate/RR logged-but-not-gated (account-level). It produces a verdict only — never auto-promotes to live.
4. **Training-dataset / feature enrichment** — ✅ **DONE (2026-06-15).** The ML scanner now attaches the full 32-marker snapshot to `Candidate.meta["markers"]`; both adapters inject it into the LLM **Inference Context Bundle** via `data_loader.format_markers()`; and the engine logs a per-audited-candidate **training record** (`Ledger.record_training_sample` → new `training_records` table) capturing macro regime + markers + book context + all three scores + sizing, with outcome (realized PnL + R-multiple) **backfilled on `close_trade`**. Read/export via `Ledger.training_samples()` / `export_training_jsonl()` — the **parent→child bridge** dataset (per-tenant isolated at the SaaS layer).
**Paper-training loop (2026-06-15):** `run_paper.py` is the parent's paper-training runner — wires the read-only IBKR feed + Ollama auditor + persistent `nova_ledger.db` + all 4 books, runs N cycles, reports per-book validation. Execution stays on the paper stub (never live). **Position exits implemented:** `Engine._evaluate_exits()` runs first each cycle, marks open positions to market (`data_loader.get_latest_price`), and closes any hitting stop/take-profit (filled at the level → clean R-multiples), which `close_trade()` backfills onto the linked training record (realized PnL + R). `Ledger.open_trades()` is the broker-agnostic source of truth for open positions. Daily-resolution exits for now (intrabar needs tick data); long-only paper. Runner has a paper-only `--exec-threshold` override to exercise the open→close→outcome loop. **Ticker hygiene:** international/index tickers (e.g. `VWRL.L`, `DX-Y.NYB`) route through the yfinance fallback (the IBKR feed's simple SMART/USD resolver returns None for `.`/`-` symbols — proper exchange mapping is a later enhancement).

**Historical replay harness (2026-06-15):** `backtest/replay.py` runs the REAL engine cycle-by-cycle over history to build the parent's training dataset fast (years of trades in minutes) rather than waiting on forward paper. **Point-in-time correct (no lookahead):** a `ReplayFeed` installed via `data_loader.set_price_feed` serves, per symbol, only bars up to the current as-of date — so the scanner (32 markers), macro gate, correlation, and exits all become point-in-time with zero engine changes. Layer 3 uses `NeutralAuditor` (50.0) by default (the live LLM is too slow for thousands of cycles and historical news/fundamentals aren't point-in-time available). Equity-curve compounds via `broker.set_simulated_nav` (+ `Ledger.realized_pnl_total`); open positions force-closed at the end so every trade is outcome-labelled; then per-book validation runs. Writes to `nova_replay.db` (separate from forward `nova_ledger.db`). Run: `python -m backtest.replay --years 5 --step 5`. Execution stays paper — never live.

**Validation findings — first full 5-year replay (2026-06-15):** 1,254 daily steps, ~10,081 training samples in `nova_replay.db`. **The current strategy does NOT pass validation, and it's a SIGNAL-QUALITY problem, not sample size** (sample sizes now met for equity: ISA 271, SIPP 216, GIA 271; Forex only 45). Key results: equity books are gross-positive (expectancy +0.74R, 58% win, 2:1 reward:risk, PF 2–3.3) BUT fail on Monte-Carlo p95 drawdown (40–57% vs caps 5–18%), Sortino <1.0, and short win rates (SIPP/GIA). **Crucially, the ML scanner's `quant_score` has ~no predictive power** — high-conviction trades (+0.79R) ≈ low-conviction (+0.69R) for equity, and *worse* for FX. The equity "edge" is long-bias drift in a 5-year bull market + favourable R:R, not skill. **Forex has negative edge** (expectancy −0.28R, 24% win, PF 0.64, 14 consecutive losses, −£953) — the weekly run's +£3.6k was small-sample luck (MC correctly flagged the fragility). **Conclusion: infrastructure/validation/harness are sound and working as designed (honestly refusing to bless a fragile/drifty/negative strategy); the alpha signal is not there yet.** Next work (strategy — for operator): rethink the scanner target/features (5-day breakout via RandomForest yields no alpha), tame tail drawdown (sizing/regime gating), and park or redesign Forex. NO strategy changes made autonomously.

**Risk-first follow-up (2026-06-15):** (1) **MC methodology corrected** — the Monte-Carlo drawdown floor was bootstrapping per-trade `pnl/notional` (position-level, = 100%-capital bets) and overstating DD ~3-10x (reported 40-57% vs a true ~15%); now bootstraps NAV-curve (portfolio-level) returns. Post-fix honest picture: ISA fails ONLY Sortino (0.74); SIPP fails win 47%/DD 15% (caps 70%/5%); GIA fails win 58%/DD 14.5% (caps 60%/10%); Forex negative edge. (2) **The regime macro gate is the real edge/lever, NOT the scanner** — trades at gate≥~79 earn +1.21R vs +0.27R at lower gate (SIPP +0.83R vs −0.03R). A gate-sensitivity experiment (gate_min 40→75) improved win rate (+5-7pp), Sortino (+0.18-0.21) AND cut drawdown across all equity books, and auto-parked Forex (DXY-proxy gate never reaches 75). Decisive daily `gate_min=75` confirmation run pending. **Implication:** the path to validation is leaning into regime gating (risk-first), not chasing scanner alpha. Raising config `gate_min` is the candidate change — still pending operator decision + daily confirmation. Known noise: the macro-gate HMM logs "not converging" frequently (hmmlearn) — works but worth hardening later.

**Per-book strategy + SIPP low-turnover allocation (2026-06-15, operator-approved):** The engine now supports **per-book strategy routing, per-book `gate_min`, and per-book `aggressive_liquidation`** (all default-preserving via `AccountContext` fields; tactical books unchanged). New **`AllocationAdapter`** (`strategy="allocation"`): holds a broad/quality ETF core (VWRL.L) at high conviction while the macro gate signals a good regime; the engine's self-correlation guardrail blocks re-buying a held position (=> low turnover), and per-book regime de-risk closes to cash when gate<floor. Also fixed the liquidation path to close at the real price + record realized PnL (was selling at stub price 0). SIPP book switched to `strategy: allocation, gate_min: 75, aggressive_liquidation: true`, buy-hold sizing. **Smoke result (5y weekly):** 20 trades (low turnover), **win 80% — clears the strict 70% pension bar** the tactical strategy never could; DD 7% weekly is the only gap, addressable by lowering SIPP equity weight (win rate is position-size-independent). **Operator decisions confirmed:** keep SIPP's 70%-win bar (build a strategy to meet it, done); adopt per-book `gate_min` (the architecture win). **Gate→edge validated daily (gate75):** GIA PASSES its profile; ISA fails only Sortino (0.986, passes at gate78); GIA fails only DD (fixed by 6% sizing at gate78). **PENDING operator sign-off:** making `gate_min`/sizing canonical in config.yaml/portfolio.yaml (ISA/GIA) — run experiments only until then. Next: comprehensive daily validation across all 4 books at tuned settings.

5. **Vertex child** — context/RAG injection first, fine-tune later; strictly tenant-isolated. **Step 1 (in-repo scaffolding) ✅ DONE (2026-06-15):** new `saas/` package — `TenantTrainingStore` (hard, fail-closed per-tenant isolation over the parent's JSONL export), `RagContextBuilder` (turns the parent's outcome-labelled records into a tenant-scoped precedent block appended to the Inference Context Bundle), and `VertexAuditor` (drop-in `Auditor` backend; `executes = False`; Vertex SDK call lazy/injectable so it's offline-testable). Engine unchanged — pure DI backend swap. **Step 2 (live GCP) PARKED — operator directive (2026-06-15):** ALL GCP infrastructure stays parked until the operator is satisfied with the **locally trained model's training, track record of success, and dataset**. Only then begin GCP (project ID, region europe-west2, billing, creds/Secret Manager, `google-cloud-aiplatform` dep). The child has nothing to RAG over until the parent has generated a validated dataset anyway, so this ordering is also the logical one. RAG-first; fine-tune later as the moat.

### Forex book
- `adapters/asset_fx.py` (`FxAdapter`) is fully implemented (DXY-proxy macro gate, FX scanner, FX auditor prompt) and ✅ **now wired in** (roadmap #2): `ibkr_forex_margin` book in `portfolio.yaml` (`wrapper: MARGIN`, `allowed_assets: ["FX"]`), `FxAdapter` registered in the engine, FX pairs in `config.yaml`'s asset-class-keyed universe, `atr_sizing` with a **5:1 leverage cap** (enforced in `core/risk.py` `AtrSizing`) and 2% per-trade risk. FX/options remain forbidden in ISA/SIPP `allowed_assets`.
- **Wrapper label — DECIDED (2026-06-15):** the Forex book uses `wrapper: MARGIN`, kept **separate from the GIA book** so the four books are independently defined and per-book margins/limits can be tuned without confusion. Tax/permissions key off `tax_policy`/`allowed_assets`, not the wrapper label.
- **Tax — DECIDED:** both **GIA and Forex** books use `tax_policy: uk_cgt` (CGT applies to spot FX gains for a UK individual). ISA/SIPP remain `null` (tax-sheltered).

### SaaS productization notes
- **Vertex "access" to training data = either (a) fine-tune a Vertex-hosted open model on the exported dataset, or (b) inject the data as context/RAG via the existing "Inference Context Bundle".** Foundation models do not share weights with the local Ollama model. Recommended path: (b) first (fast, no training infra), (a) later as the moat.
- **Regulatory (UK FCA) — DECIDED:** the SaaS is positioned as a **signals / decision-support tool** (the customer reviews and executes) — the least-regulatory-hurdle route, avoiding discretionary-management authorization. The cloud child **advises only; never executes**. Whitepaper + all product copy must reflect this stance and avoid any "we trade for you / managed" language.
- **No guaranteed performance:** frame success as **historically validated against the per-book criteria**, never a promise (markets are non-stationary). The validation gate is the honest trust signal.
- **Tenant data isolation:** the child trains only on the parent's curated export — never cross-tenant. Per-tenant DB isolation; no customer's positions/PII ever enter another tenant's model context. Design into the storage layer from day one.
