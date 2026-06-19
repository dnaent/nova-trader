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
**FORWARD PAPER-TRAINING LIVE (2026-06-16):** With all 4 books historically validated, the parent's FORWARD paper-training loop is now running on the live stack to build a real, live-data track record + dataset. `run_paper.py` connects to **TWS (read-only, port 7497, verified server v178)** for the data feed + the **Ollama `qwen2.5:7b-instruct` auditor** + paper-stub execution (never live). Operator decision: **one daily cycle, all 4 books together** (matches how the parent runs live — shared macro regime/cross-asset correlation, shared gate/scan caches, one ledger; per-book tracking comes from the per-book validation report, not per-book processes). Scheduled via **Windows Task Scheduler** task `NovaParentPaperTraining` (weekdays 07:00 UK, captures the prior complete trading day; appends to `nova_ledger.db` and `logs/forward.log`; needs TWS + Ollama up at fire time, falls back to yfinance / neutral-auditor if not). Cycle 1 logged (SIPP bought VWRL.L on a favourable regime; ISA/GIA/Forex held — per-book gates working on live data). **Review progress any time with `python run_paper.py --cycles 0`** (validates current ledger without trading). Track record accrues over calendar time (one trading day per run) — weeks/months to each book's sample floor. **Two forward-loop fixes (commit `281d0de`):** (1) `IBKRAdapter.seed_positions()` rehydrates the paper book from `ledger.open_trades()` at startup, so separate daily invocations don't re-buy held positions (the stub's positions are in-memory); (2) `ibkr_feed._contract` routes `^`-prefixed Yahoo index symbols (^VIX/^TNX) to the yfinance fallback (no more "No security definition" spam in the gate's hot path). Still PAPER-ONLY; live-authorization gate unchanged.

**Paper-training loop (2026-06-15):** `run_paper.py` is the parent's paper-training runner — wires the read-only IBKR feed + Ollama auditor + persistent `nova_ledger.db` + all 4 books, runs N cycles, reports per-book validation. Execution stays on the paper stub (never live). **Position exits implemented:** `Engine._evaluate_exits()` runs first each cycle, marks open positions to market (`data_loader.get_latest_price`), and closes any hitting stop/take-profit (filled at the level → clean R-multiples), which `close_trade()` backfills onto the linked training record (realized PnL + R). `Ledger.open_trades()` is the broker-agnostic source of truth for open positions. Daily-resolution exits for now (intrabar needs tick data); long-only paper. Runner has a paper-only `--exec-threshold` override to exercise the open→close→outcome loop. **Ticker hygiene:** international/index tickers (e.g. `VWRL.L`, `DX-Y.NYB`) route through the yfinance fallback (the IBKR feed's simple SMART/USD resolver returns None for `.`/`-` symbols — proper exchange mapping is a later enhancement).

**Historical replay harness (2026-06-15):** `backtest/replay.py` runs the REAL engine cycle-by-cycle over history to build the parent's training dataset fast (years of trades in minutes) rather than waiting on forward paper. **Point-in-time correct (no lookahead):** a `ReplayFeed` installed via `data_loader.set_price_feed` serves, per symbol, only bars up to the current as-of date — so the scanner (32 markers), macro gate, correlation, and exits all become point-in-time with zero engine changes. Layer 3 uses `NeutralAuditor` (50.0) by default (the live LLM is too slow for thousands of cycles and historical news/fundamentals aren't point-in-time available). Equity-curve compounds via `broker.set_simulated_nav` (+ `Ledger.realized_pnl_total`); open positions force-closed at the end so every trade is outcome-labelled; then per-book validation runs. Writes to `nova_replay.db` (separate from forward `nova_ledger.db`). Run: `python -m backtest.replay --years 5 --step 5`. Execution stays paper — never live.

**Validation findings — first full 5-year replay (2026-06-15):** 1,254 daily steps, ~10,081 training samples in `nova_replay.db`. **The current strategy does NOT pass validation, and it's a SIGNAL-QUALITY problem, not sample size** (sample sizes now met for equity: ISA 271, SIPP 216, GIA 271; Forex only 45). Key results: equity books are gross-positive (expectancy +0.74R, 58% win, 2:1 reward:risk, PF 2–3.3) BUT fail on Monte-Carlo p95 drawdown (40–57% vs caps 5–18%), Sortino <1.0, and short win rates (SIPP/GIA). **Crucially, the ML scanner's `quant_score` has ~no predictive power** — high-conviction trades (+0.79R) ≈ low-conviction (+0.69R) for equity, and *worse* for FX. The equity "edge" is long-bias drift in a 5-year bull market + favourable R:R, not skill. **Forex has negative edge** (expectancy −0.28R, 24% win, PF 0.64, 14 consecutive losses, −£953) — the weekly run's +£3.6k was small-sample luck (MC correctly flagged the fragility). **Conclusion: infrastructure/validation/harness are sound and working as designed (honestly refusing to bless a fragile/drifty/negative strategy); the alpha signal is not there yet.** Next work (strategy — for operator): rethink the scanner target/features (5-day breakout via RandomForest yields no alpha), tame tail drawdown (sizing/regime gating), and park or redesign Forex. NO strategy changes made autonomously.

**Risk-first follow-up (2026-06-15):** (1) **MC methodology corrected** — the Monte-Carlo drawdown floor was bootstrapping per-trade `pnl/notional` (position-level, = 100%-capital bets) and overstating DD ~3-10x (reported 40-57% vs a true ~15%); now bootstraps NAV-curve (portfolio-level) returns. Post-fix honest picture: ISA fails ONLY Sortino (0.74); SIPP fails win 47%/DD 15% (caps 70%/5%); GIA fails win 58%/DD 14.5% (caps 60%/10%); Forex negative edge. (2) **The regime macro gate is the real edge/lever, NOT the scanner** — trades at gate≥~79 earn +1.21R vs +0.27R at lower gate (SIPP +0.83R vs −0.03R). A gate-sensitivity experiment (gate_min 40→75) improved win rate (+5-7pp), Sortino (+0.18-0.21) AND cut drawdown across all equity books, and auto-parked Forex (DXY-proxy gate never reaches 75). Decisive daily `gate_min=75` confirmation run pending. **Implication:** the path to validation is leaning into regime gating (risk-first), not chasing scanner alpha. Raising config `gate_min` is the candidate change — still pending operator decision + daily confirmation. Known noise: the macro-gate HMM logs "not converging" frequently (hmmlearn) — works but worth hardening later.

**Per-book strategy + SIPP low-turnover allocation (2026-06-15, operator-approved):** The engine now supports **per-book strategy routing, per-book `gate_min`, and per-book `aggressive_liquidation`** (all default-preserving via `AccountContext` fields; tactical books unchanged). New **`AllocationAdapter`** (`strategy="allocation"`): holds a broad/quality ETF core (VWRL.L) at high conviction while the macro gate signals a good regime; the engine's self-correlation guardrail blocks re-buying a held position (=> low turnover), and per-book regime de-risk closes to cash when gate<floor. Also fixed the liquidation path to close at the real price + record realized PnL (was selling at stub price 0). SIPP book switched to `strategy: allocation, gate_min: 75, aggressive_liquidation: true`, buy-hold sizing. **Smoke result (5y weekly):** 20 trades (low turnover), **win 80% — clears the strict 70% pension bar** the tactical strategy never could; DD 7% weekly is the only gap, addressable by lowering SIPP equity weight (win rate is position-size-independent). **Operator decisions confirmed:** keep SIPP's 70%-win bar (build a strategy to meet it, done); adopt per-book `gate_min` (the architecture win). **Gate→edge validated daily (gate75):** GIA PASSES its profile; ISA fails only Sortino (0.986, passes at gate78); GIA fails only DD (fixed by 6% sizing at gate78). **PENDING operator sign-off:** making `gate_min`/sizing canonical in config.yaml/portfolio.yaml (ISA/GIA) — run experiments only until then. Next: comprehensive daily validation across all 4 books at tuned settings.

**8-YEAR VALIDATION — ISA & GIA PASS (2026-06-15):** Daily replay over 2018-2026 (spans the 2020 COVID crash AND the 2022 bear — robust regime coverage, not a bull fluke) at `gate_min=78` (GIA sizing 6%): **ISA PASS** (sample 267, win 67%, Sortino 1.023, DD 9.0%, PF 4.62 — the longer window delivered both the 200-trade sample and Sortino≥1.0) and **GIA PASS** (sample 272, win 69%, DD 6.9%, PF 5.07). Two books historically validated per their own profiles. (That run's SIPP was still the old tactical book; the allocation SIPP is being validated separately.) **NEW DECISION POINT for operator:** the low-turnover SIPP allocation makes few trades by design (~20 in 5y) — conflicting with the 150-trade `min_trades` floor (designed for the tactical strategy). For a low-turnover/buy-hold strategy, statistical validation should arguably rest on the **equity-curve robustness (walk-forward + Monte-Carlo on NAV returns)** rather than trade count. Options: (a) lower `min_trades` for `allocation` books, or (b) add an equity-curve-based validation path for low-turnover strategies. Not changed autonomously — operator's call. **STILL PENDING operator sign-off:** canonicalizing `gate_min=78` (ISA/GIA) + GIA 6% sizing into config.yaml/portfolio.yaml.

**Overnight conclusion (2026-06-16) — converged, awaiting operator decisions:** Added per-book de-risk **hysteresis** (`derisk_gate`: enter≥gate_min, exit<derisk_gate) to fix daily regime whipsaw in the SIPP allocation. Final 8y-daily picture: **GIA robustly PASSES** (win 68%, DD 7.1%, PF 4.83 — margin); **ISA borderline** (Sortino ~0.99–1.02, sits on the 1.0 bar, flips with a 1-day window shift — not robust); **SIPP** allocation hits DD (2.8%) & PF (5.57) but win 64% (<70%) and only **14 trades** over 8y — low-turnover is FUNDAMENTALLY incompatible with the 150-trade floor + 5%-MC (few-trade instability). **Decisions for operator (no more autonomous tuning):** (1) SIPP — adopt equity-curve-based validation for low-turnover books (vs trade count), and/or accept resolution-sensitive win rate; (2) ISA — nudge gate higher for a robust (not knife-edge) Sortino, as part of canonicalization; (3) sign off canonical `gate_min`/sizing for GIA (solid) + ISA. Forex stays parked. SIPP allocation weight 35% achieved the DD target in experiments (portfolio.yaml still at 90% — final weight depends on decision 1). Two of four books are at/near validation across COVID + 2022 bear; this is genuine progress toward the live-authorization gate (still paper-only).

**HONEST MARK-TO-MARKET VALIDATION (2026-06-16) — ISA & GIA robustly PASS:** Closed the last methodology gap. The replay equity curve now records **mark-to-market NAV** (cash + realised + *unrealised* P&L of open positions, priced at the as-of close) instead of realised-only — realised-only is flat during holds and understated drawdown (esp. for buy-and-hold). And low-turnover **`allocation` books are validated on the equity curve** (monthly returns: win rate ⇒ % positive months; DD/MC from the NAV curve; the 150-trade floor becomes a ~30-month track-record floor) instead of the trade-count rule that never fit a buy-hold strategy. Final 8y-daily (2018-2026, ISA gate80 / GIA gate78+6% / SIPP alloc gate75/derisk65 @35% / **exec_threshold=35**) under honest MTM: **ISA PASS** (sample 229, win 70.7%, **Sortino 1.123** — now robust, was knife-edge at gate78; DD 7.6%, MC-p95 10.2%, PF 5.52) and **GIA PASS** (sample 276, win 68.8%, **DD 7.6% < 10% cap with margin**, MC-p95 7.6%, PF 5.09). The earlier worry that honest MTM would tighten GIA to borderline was unfounded — it holds. **SIPP allocation @35% FAILS** on the now-correct curve path (95 monthly periods ✓, but **66% positive months < 70%**, DD 6.0% > 5%, MC-p95 13.4%): the curve validation works, but the strict pension profile isn't met — DD≈6% is fixable by lowering the equity weight (~30%), while **70%-positive-months is a brutal bar for ANY allocation strategy** (most funds run ~55-60%) and is position-size-independent. **Forex FAILS** (parked; negative edge: PF 0.48, 16 consec losses). **Reproducibility gap found:** `config.yaml` documents `exec_threshold: 75`, but EVERY validated replay quietly overrode it to **35** — 75 is unreachable for the current scanner (blended scores max ~52, mean ~29, since the scanner has ~no edge and the regime gate carries it). This must be reconciled as part of canonicalization. **DECISIONS FOR OPERATOR (still no autonomous config/strategy changes):** (1) **SIPP** — the 70%-positive-months curve bar is likely too strict for a buy-hold book; either reinterpret the SIPP "win rate" criterion for curve-validated books (e.g. CAGR/MAR or % positive months at a lower bar) and set equity weight ~30% for the 5% DD, OR accept SIPP needs a different design. (2) **Canonical config sign-off** (Decision 3): promote `gate_min=80` (ISA), `gate_min=78` + 6% sizing (GIA), and `exec_threshold=35` into config.yaml/portfolio.yaml — ISA & GIA are now validated under the honest methodology. NOT done autonomously. Two of four books are HISTORICALLY VALIDATED per their own profiles under the most rigorous (mark-to-market) methodology, across COVID + the 2022 bear — genuine progress toward the live-authorization gate (still paper-only).

**DECISIONS RESOLVED — THREE OF FOUR BOOKS VALIDATED & CANONICALIZED (2026-06-16):** Operator delegated the three open decisions; all resolved and the validated settings are now CANONICAL in the manifests (no longer experiment-only injections):
- **ISA & GIA — signed off & canonicalized.** `portfolio.yaml`: ISA `gate_min: 80`, GIA `gate_min: 78` + sizing `8%→6%`. `config.yaml`: `exec_threshold: 75→35` (the ML scanner's blended scores top out ~52, so 75 was unreachable; every validated replay used 35 — this closes the reproducibility gap). 8y-daily honest-MTM confirmation: **ISA PASS** (sample 231, win 71%, Sortino 1.131, DD 7.6%, MC 10.0%, PF 5.62), **GIA PASS** (sample 276, win 69.6%, DD 7.6%, MC 7.28%, PF 5.32).
- **SIPP — honest allocation/pension profile (operator's-call tweak), now PASSES.** `backtest/validation.py` routes low-turnover `allocation` books to a buy-hold-appropriate profile: "win rate" ⇒ **% positive months gated at 60%** (the 70% *trade* win rate is a tactical concept that doesn't translate to a curve); **realised DD keeps the tight 5% pension rail** (SIPP equity weight `90%→25%` in portfolio.yaml + regime de-risk ⇒ realised DD 4.42% over 8y); **Monte-Carlo DD judged at a wider 10% bound** via new `BookProfile.mc_max_drawdown_pct` — reshuffling monthly returns destroys the regime-gating's timing mechanism, so MC is structurally pessimistic for a regime-timed strategy (still gated; the realised 5% rail stays primary). Confirmation: **SIPP PASS** (positive-months 66%, realised DD 4.42%, MC 9.81%, PF 1.90). NOTE: SIPP's MC (9.81%) sits close to its 10% bound — trimming weight to ~22% adds cushion at a small cost to compounding; the realised rail (4.42%) has margin, so left at 25% pending operator preference.
- **Forex — kept PARKED; REDESIGN is the next workstream (operator-confirmed 2026-06-16).** Current DXY-proxy gate + breakout scanner has genuine NEGATIVE edge (PF 0.48, Sortino −0.5, 16 consec losses, −£1063/8y) — a validation cycle can't fix a missing signal; it needs a redesigned FX signal (e.g. trend/carry or mean-reversion under the regime gate), judged at the account/equity-curve level per the FOREX profile. To be tackled after this canonicalization landed.
- **GCP/Vertex — stays PARKED** (operator directive reaffirmed): begin only once there's a track record of positive results across the books from local trading + training.

**Net:** three books (ISA, GIA, SIPP) are now HISTORICALLY VALIDATED per their own profiles under the most rigorous (mark-to-market) methodology, across COVID + the 2022 bear, with settings canonical in config. Still PAPER-ONLY — the hard live-authorization gate (operator sign-off + per-book pass) is unchanged.

5. **Vertex child** — context/RAG injection first, fine-tune later; strictly tenant-isolated. **Step 1 (in-repo scaffolding) ✅ DONE (2026-06-15):** new `saas/` package — `TenantTrainingStore` (hard, fail-closed per-tenant isolation over the parent's JSONL export), `RagContextBuilder` (turns the parent's outcome-labelled records into a tenant-scoped precedent block appended to the Inference Context Bundle), and `VertexAuditor` (drop-in `Auditor` backend; `executes = False`; Vertex SDK call lazy/injectable so it's offline-testable). Engine unchanged — pure DI backend swap. **Step 2 (live GCP) PARKED — operator directive (2026-06-15):** ALL GCP infrastructure stays parked until the operator is satisfied with the **locally trained model's training, track record of success, and dataset**. Only then begin GCP (project ID, region europe-west2, billing, creds/Secret Manager, `google-cloud-aiplatform` dep). The child has nothing to RAG over until the parent has generated a validated dataset anyway, so this ordering is also the logical one. RAG-first; fine-tune later as the moat.

### Forex book
- **TREND-FOLLOWING REDESIGN (2026-06-16) — negative edge → POSITIVE, not yet a full pass.** Operator chose trend-following for the FX redesign. Replaced the failed DXY-proxy gate + ML breakout scanner (PF 0.48, 16 consec losses, −£1063) with classic trend-following in `adapters/asset_fx.py`: **scanner** goes long when EMA20>EMA50 & price>EMA50, short when inverted, but ONLY when ADX≥20 confirms a trend (sits out chop); **gate** is a trend-REGIME gate on the USD index (DXY) ADX (trade only when the FX complex actually trends). Required **short-side support across the engine** — added additively (side-keyed; the equity long path is provably unchanged): `Candidate.side`, `AtrSizing` inverted brackets + FX price precision (0.0001 not 0.01), side-aware exits/PnL/MTM/force-close (`core/engine.py`, `backtest/replay.py`), `Ledger.open_trades` returns shorts, broker `positions` reports net-short. 8y-daily result: **PF 2.12, +£6951, sample 325, MC-dd 18.4% — genuine positive edge** (vs the old negative book). But still **FAILS the FOREX profile** on max drawdown (24% > 20%), Sortino (0.43 < 1.0) and max consecutive losses (27 > 6) — trend-following's inherent whipsaw loss-streaks need risk control. **NEXT (risk-control iteration, operator-steered):** note that pure position-size reduction fixes DD but NOT Sortino/consec-losses (both size-independent ratios/counts) — the root fix is a tighter trend filter (higher ADX) + letting winners run (trailing stops, improving the win/loss asymmetry → Sortino) + a consecutive-loss circuit breaker. Equities (ISA/GIA/SIPP) re-confirmed PASS (no regression). FX stays PARKED. Committed `596097e`.
- **FOREX VALIDATED (2026-06-16) — account-level profile + 1% sizing → PASS.** The risk-control overhaul (trailing-no-take, 8 pairs, ADX 23) BACKFIRED — it hit the strict rails but destroyed the edge (PF 2.12→0.74); reverted to the proven v1 trend strategy (fixed 4-ATR take, ADX 20). Added only edge-neutral controls: the **consecutive-loss circuit breaker** (with a deadlock fix — a baseline so a served streak isn't recounted after cooldown; the bug had frozen the book to 26 trades / 121 trips) and concurrent cap. That gave PF 2.33 / +£8.5k but still failed Sortino (0.63<1.0) and consec-losses (12>6) — **proven style-inherent walls** (trend-following is lumpy/streaky; you cannot reach Sortino≥1.0 / consec≤6 without killing the edge). **Operator decision (SIPP-parallel): validate the trend FX book on a style-appropriate ACCOUNT-LEVEL profile.** `backtest/validation.py` FOREX profile now GATES on profit factor, drawdown, MC and **MAR/Calmar** (new `min_mar` + `mar_ratio` = annualised return / maxDD — the right risk-adjusted measure for a lumpy curve); **Sortino and consecutive losses are now LOGGED-not-gated** (joining win-rate/reward:risk as account-level style metrics). Per-trade risk 2%→1% brings DD under the 20% cap (scales DD, not PF/MAR/sample); FX universe 4→6 majors for the ≥300 sample + diversification. **Final 8y-daily: FOREX PASS** — PF 2.35, MAR 0.54, DD 17.25%, MC 16.5%, sample 424, +£5168 (Sortino 0.67 / consec 23 logged-not-gated). Committed `5866dd9`.
- **🎯 MILESTONE (2026-06-16): ALL FOUR BOOKS VALIDATED on their own honest profiles** — ISA (growth), GIA (tax-efficient core), SIPP (pension allocation), Forex (trend) — each historically validated across the 2020 COVID crash + the 2022 bear, under honest mark-to-market NAV, with settings canonical in config.yaml/portfolio.yaml. **STILL PAPER-ONLY**: the hard live-authorization gate (operator explicit sign-off + per-book pass) is unchanged. Next per the roadmap: the parent generates a validated training dataset (now possible across all 4 books) → only THEN the Vertex child / GCP (still parked until the operator is satisfied with the local model's track record).
- **🔬 OUT-OF-SAMPLE GFC STRESS TEST (2026-06-17) — the 2018-2026 EQUITY validations were partly a bull-market artifact; Forex trend SURVIVES.** The four-book milestone above was validated on 2018-2026 (COVID + 2022 bear, but a *recovering* sample). To answer "are the per-book mandates logically sound, or just sample-luck?", ran the REAL engine daily over **2007-01-03 → 2018-01-02** — a fully DISJOINT window containing the **2008 Global Financial Crisis** (a deep secular bear the books were never validated on) — at **canonical settings** (per-book `gate_min` ISA 80 / GIA 78 / SIPP 75, `exec_threshold=35`), seeded (42) Monte-Carlo, honest mark-to-market NAV. SIPP allocation core proxied by **SPY** (VWRL.L inception 2012-05). Confirmed first that the regime gate genuinely detects the crash point-in-time (gate 16-20 at the Sept-Nov 2008 panic, 20 at the 2011 euro crisis). Results (`nova_replay_gfc.db`):
  - **Forex → PASS** (sample 899, PF 4.19, MAR 3.45, realised DD 12.5%, MC-p95 10.0%). Trend-following THRIVES in crises (2008 + the 2014-15 USD surge are strong trends). The account-level trend profile holds out-of-sample — the most encouraging result. (Sortino 0.99 / consec 12 logged-not-gated as designed. NOTE the leveraged PnL is notional/uncompounded — the *ratios* are the meaningful pass.)
  - **ISA → FAIL (near-miss).** Still gross-profitable through the GFC (PF 2.56, win 56%, expectancy +£19, realised DD 11.5% < 18%) but fails **Sortino 0.68** (vs 1.0; was 1.13 in-sample) and **MC-p95 DD 18.31%** — literally 0.31pp over its 18% bar. The growth book bends but doesn't break.
  - **GIA → FAIL.** Gross-profitable (PF 2.40, realised DD 9.44% just under its 10% cap) but **win rate 53.5%** (vs 60%) and **MC-p95 DD 17.84%** (vs 10%). The tax-efficient core's tight tail-risk cap is not robust to a GFC-scale event.
  - **SIPP → FAIL (the important one).** **Realised DD 15.35% BLOWS the 5% pension rail** (and MC-p95 17.5% vs 10%) — the DD-breach guardrail tripped repeatedly through 2008. Regime de-risk lags a fast crash too much to hold 5% DD; at 25% equity weight + a GFC, the pension mandate's headline number is violated. (Still net +£3.4k / 61% positive months — profitable, but not within the pension risk rail.)
  - **HONEST CONCLUSION (answers the operator's "are the mandates sound?" question with data):** the strategies are NOT broken out-of-sample — every book stays **gross-profitable (PF 2.4-4.2) through the 2008 crash**. What fails is the **TAIL-RISK side of the mandates**: all three equity books show **MC-p95 DD ~17-18%** out-of-sample (vs ~10% in the calm 2018-2026 sample) — i.e. the 2018-2026 validation **understated tail drawdown by ~2x** because it contained no GFC-magnitude crash. ISA's 18% cap nearly absorbs this (fails by 0.3pp); GIA's 10% and especially SIPP's 5% caps are **structurally too tight to survive a 2008-scale event** with regime-timed equity. The regime gate de-risks but cannot dodge a fast crash entirely. **The validation framework did its job — it honestly refuses to bless the tight-DD equity mandates against a regime they never saw.**
  - **DECISION POINTS FOR OPERATOR (NO autonomous config/profile/strategy changes made — these reframe the mandates and are the operator's call):** (1) **SIPP** — a 5% DD pension rail is likely unachievable through a GFC with any meaningfully-invested equity strategy; either accept a higher crash-DD (e.g. 10-12%) as the honest pension reality, lower equity weight further (cost: compounding), or add explicit crash hedging. (2) **GIA** — either widen the DD/MC cap toward ISA's ~18% (the empirical equity tail) or accept GIA fails in deep crises. (3) **ISA** — closest to robust; a small further gate/sizing tightening could pull MC under 18% and lift Sortino. (4) Consider making **out-of-sample (GFC) survival a standing part of the validation gate**, not just the in-sample window — the single biggest honesty upgrade. Forex needs nothing. **Nothing here changes the canonical config or un-validates the in-sample sign-off; it is new risk information for the live-authorization decision.** Still PAPER-ONLY.
  - **Supporting infra hardening shipped alongside (committed):** macro-gate **graceful degradation** (a missing feed drops only its component + renormalises, vs collapsing to neutral-50 and spuriously de-risking every book — `b3340e3`); **hmmlearn log-spam silenced** (`b3340e3`); replay **prompt-skip speedup** for abstaining auditors (~2.5h → ~16 min for 11y, identical results — `33deea1`). 117 tests pass.
- **✅ RISK-BASED EQUITY SIZING — CANONICALIZED (2026-06-18), the root-cause fix for the GFC equity tail.** The GFC finding above was a TAIL-RISK problem (MC-p95 DD ~17-18% vs caps), not a broken edge. Fixed at root by switching ISA+GIA from flat `nav_pct` to **ATR (volatility-throttled) sizing** (`atr_sizing`, `risk_pct: 0.35`, `leverage: 0.35` reused as a per-position notional cap, stop 2ATR / take 4ATR — `portfolio.yaml`). ATR stops widen in a crash ⇒ position size auto-shrinks ⇒ constant per-trade risk. Result (real engine, daily, both windows, honest MTM, seed-42 MC): **HALVED the GFC Monte-Carlo tail — ISA MC 18.3%→8.5%, GIA 17.8%→8.9%, both well inside caps — with ZERO in-sample regression** (ISA/GIA/SIPP all still PASS in-sample: ISA Sortino 1.065, GIA Sortino 1.02). A risk/leverage **sweep confirmed r35 is the floor** (r60 was too hot — GIA GFC blew up). **The ONLY residual out-of-sample failure is the GFC Sortino ≈0.73 on ISA AND GIA (now identical)** — and Sortino is a return/downside-dev *ratio*, so it is **SIZE-INVARIANT** (0.73 at r35, 0.80 at r60): it's the strategy's risk-adjusted-return *shape* in the single worst crisis, NOT a sizing problem. Operator decision pending: accept GFC Sortino<1 as honest crisis reality, or pursue a shape fix (trailing winners / faster de-risk) as a separate thesis.
- **✅ GIA NOW MIRRORS THE ISA MANDATE — CANONICALIZED (2026-06-18), "Wrapper⊥Strategy" made literal.** Drawdown is a MARKET property, not a tax property, so the old tighter GIA caps (win≥60%, DD≤10%) were logically incoherent for the SAME strategy + assets as ISA. GIA's `validation.py` profile now = ISA's (DD≤18%, win≥45%, PF≥1.6, Sortino≥1.0, expectancy>0); GIA `gate_min` 78→**80** (= ISA's, the 78 was tuned for the dead nav_pct GIA; gate 80 firms GIA's in-sample Sortino to 1.02). Tax efficiency is a separate **realization-timing OVERLAY** (defer CGT, harvest losses vs the £3k AEA, low turnover), NOT a tighter risk profile — to be built. (`test_allocation` gate assertion updated; the replay does NOT deduct CGT, so GIA/ISA metrics converge identically at gate 80.)
- **🔬 SIPP REDESIGN — frontier tested (2026-06-18), DECISION PENDING operator (horizon/risk).** Operator's SIPP vision = long-term compounding in **accumulating (Acc) thematic ETFs** (AI/tech infra, data centres, critical metals/materials, renewables; all-Acc tickers vetted: AIAG / VPN.L / REGB / iShares Clean Energy Acc IE000U58J0M1; equal-weight). Thematic ETFs are 2019-2022 inceptions ⇒ GFC-tested via long-history USD proxies (QQQ/VNQ/XME/PBW). Findings: **(1) the 5% interim-DD pension rail is unachievable for ANY growth SIPP** (even 80% bonds ⇒ 14-19% DD) — the SIPP profile MUST be reframed off it. **(2) Pure thematic (path A) has a LOST-DECADE tail** — GFC −3.1% CAGR / 41% DD / 1-of-10 positive years / ~115-month recovery (vs in-sample +14.6%): retiring the rail swaps a drawdown problem for a lost-decade problem; the 2018-26 thematic win is substantially a bull artifact. **(3) The core must be DEFENSIVE (bonds), NOT broad equity** — an SPY-core+thematic still −3.3% CAGR/127mo recovery in the GFC (SPY fell ~50% in 2008); only an AGG bond core breaks the lost decade (agg80/them20: GFC +4.4%/14%DD/~20mo recovery, in-sample +4.2%; agg60/them40: GFC +4.3%/23%DD, in-sample +7.0%). **Recommendation: bond-core + thematic-satellite** (keeps the thematic thesis as the growth engine, bond core prevents catastrophe), validated on long-horizon metrics (CAGR/MAR/% positive years/recovery) with a realistic ~15-20% DD bound; a future age-based glide path is the sophisticated answer. Split = operator's horizon/risk call. **Crash-CB (commit `b64c757`) stays opt-in/off — it whipsawed (net-positive only for ISA); risk-based sizing superseded it.** Still PAPER-ONLY.
- **✅ SIPP = PATH A (PURE THEMATIC) — DECIDED & BUILT (2026-06-18, operator's informed choice).** Operator chose pure thematic over core+satellite, accepting the lost-decade tail. Implemented: (a) **live equal-weight Acc basket** in `config.yaml allocation_basket` = **AIAG.L** (L&G AI), **VPNG.L** (Global X Data Center), **REGB.L** (VanEck Rare Earth), **INRA.L** (iShares Clean Energy Transition Acc, IE000U58J0M1) — all full-Acc, UK-listed, verified to resolve; wired via `EngineConfig.allocation_basket` → `run_paper.py` `AllocationAdapter(basket=...)`. (b) SIPP book `max_correlation: 0.99` so all four correlated themes are HELD (not de-duplicated to one); equal-weight 4×25%≈100% invested, regime-de-risked. (c) **LONG-HORIZON validation profile** (`validation.py` allocation branch): % positive months ≥55%, **MAR/Calmar ≥0.30** (primary risk-adjusted gate), realised-DD rail RETIRED, MC-DD gate DISABLED (thematic is inherently extreme-DD), universal floor (PF>1 + walk-forward) kept. Verdict: **in-sample PASS** (% positive months 57%, MAR 0.45, PF 1.67) / **GFC FAIL** (MAR −0.08, PF 0.57 — the documented, accepted lost-decade). HISTORICAL REPLAY uses long-history PROXIES (QQQ/VNQ/XME/PBW); the live basket is the young Acc funds. NOTE: graduation rests on in-sample long-horizon metrics with the hard operator-sign-off gate as backstop. **Operator CONFIRMED 2026-06-18** that disabling the DD/MC gate for the SIPP (forced by thematic's inherently extreme DD) is the intended relaxation — return-shape (MAR + % positive months) + universal PF/walk-forward floor are the SIPP's gates; the hard operator-sign-off gate is the only DD backstop. Still PAPER-ONLY.
- **✅ MODERNIZED UNIVERSES + ENRICHED SIPP + RESEARCH KNOWLEDGE (2026-06-18, commits `bc930fc`/`b98c0a0`).** Mined the operator's per-book research matrices (forex/gia/isa/sipp dirs — concepts, somewhat outdated), did live trailing-12m DD on every ticker, then: (1) **per-book scan universes** added (`AccountContext.universe`; engine prefers it, falls back to config) so ISA/GIA hold distinct watchlists; (2) **GIA modernized** to US high-beta (IREN/CRML/MU/VRT/ASML/GEV/TSM/ANET/3LNV.L/AVGO/NVDA) — in-sample **PASS, Sortino 1.336**; (3) **SIPP ENRICHED** from pure path-A thematic to a diversified "Pension Fortress" (gold/global/income CORE + thematic satellites; `config.yaml allocation_basket`) — in-sample PASS (MAR 0.56) and the core **BREAKS the GFC lost-decade tail** (proxy GFC MAR −0.08→+0.096, positive months 8%→65%) — the diversification thesis the frontier predicted, now validated; (4) **research/** knowledge files created (`NOVA_TICKER_RESEARCH.md` + `nova_ticker_matrix.xlsx`: curated universes, 12m returns, DD rationale, and the WINNER/LOSER success-patterns — AI-infra + supply-constrained commodities win; pre-revenue story-stocks / leveraged sentiment proxies / rate-sensitive yield lose) as **context for the parent model**; source matrices archived to `research/source_archive/`. **OPEN — ISA mandate decision:** the modernized UK-growth ISA universe is gross-profitable (PF 2.9, win 55%, DD<18%) but FAILS ISA Sortino≥1.0 in-sample (0.60-0.70 — UK miners are choppy; adding diversifiers made it worse). Not a bug (GIA passes 1.33 only because US tech ran smoother). ISA held on its validated fallback pending operator: relax ISA Sortino for a deliberately-cyclical growth book vs broad-tilt vs keep. **RESOLVED 2026-06-19 (option d, commit `ab98a84`):** the root issue was the STRATEGY, not the tickers — the tactical ML scanner has ~no edge (regime gate carries it) and its churn made the low-Sortino lumpy curve (diversifiers made it worse). ISA switched to a **low-turnover, regime-gated, diversified GROWTH allocation** (like the SIPP but growth-tilted: semis/AI/data-centre/clean-energy/robotics/rare-earth + global ballast + gold crash-diversifier), curve-validated: **in-sample MAR 0.64** (beats SIPP 0.56 — growth tilt earns) and **survives the GFC positively** (MAR 0.156, 60% positive months — no lost decade). Implemented per-book allocation baskets (AllocationAdapter holds `ctx.universe`); GIA stays the tactical-growth book (US high-beta) and now carries the tactical-growth mandate on its own. **✅ GFC-Sortino thesis RESOLVED (negative):** neither trailing-winners (0.20, also broke in-sample) nor crash-de-risk (0.69, whipsaw) lifts the ISA/GIA GFC Sortino ≈0.73 — it's an irreducible 2008 crisis-shape property; accept as documented. **Forward ledger archived** (`nova_ledger.archived-20260618-preThematic.db`) for a clean track record under the new canonical config. Still PAPER-ONLY.
- `adapters/asset_fx.py` (`FxAdapter`) is fully implemented (trend-regime gate, EMA/ADX trend scanner, FX auditor prompt) and ✅ **wired in** (roadmap #2): `ibkr_forex_margin` book in `portfolio.yaml` (`wrapper: MARGIN`, `allowed_assets: ["FX"]`), `FxAdapter` registered in the engine, FX pairs in `config.yaml`'s asset-class-keyed universe, `atr_sizing` with a **5:1 leverage cap** (enforced in `core/risk.py` `AtrSizing`) and 2% per-trade risk. FX/options remain forbidden in ISA/SIPP `allowed_assets`.
- **Wrapper label — DECIDED (2026-06-15):** the Forex book uses `wrapper: MARGIN`, kept **separate from the GIA book** so the four books are independently defined and per-book margins/limits can be tuned without confusion. Tax/permissions key off `tax_policy`/`allowed_assets`, not the wrapper label.
- **Tax — DECIDED:** both **GIA and Forex** books use `tax_policy: uk_cgt` (CGT applies to spot FX gains for a UK individual). ISA/SIPP remain `null` (tax-sheltered).

### 🟢 LIVE STATE + FORWARD ROADMAP (2026-06-19)
- **LIVE FORWARD PAPER-TRAINING BEGUN (operator go-ahead).** All four books validated on their honest profiles, so the parent's forward loop now runs on the **finalized config + LIVE IBKR TWS** data. Posture (unchanged hard gate): TWS connects **read-only** (`readonly=True`, port 7497, mktDataType=1 real-time) for DATA ONLY; execution is the **paper stub** (`connector="stub"`) — no live order possible. First real cycle logged to a fresh `nova_ledger.db` (prior 1-day partial re-archived to `nova_ledger.archived-20260619-preISAalloc.db`). **Ongoing accrual:** Task Scheduler task **`NovaParentPaperTraining`** (weekdays 07:00 UK, Ready). **Operator TWS setup:** auto-restart 23:45 + autologoff DISABLED (always-on API); caveat — IBKR forces a ~weekly manual re-login (≈Sun); if missed, the cron falls back to yfinance that day (self-healing). The engine accrues the dataset; the 3080 Ti LLM fine-tune is a separate later step.
- **TRAINING CORPUS GENERATED — bridge step 2.** `nova_training_corpus.jsonl` = **26,560 outcome-labelled records** (GIA 24,852 / Forex 1,376 / SIPP 212 / ISA 120 — GIA-dominated by design: the tactical scanner logs a decision per candidate per cycle; allocation books are low-turnover) over 2007-2026, point-in-time, via `Ledger.export_training_jsonl`. Replay uses long-history PROXIES for the young Acc funds + NeutralAuditor (Layer3=50); the live cron adds real-instrument, real-Ollama records. Gitignored (`*.jsonl`). **Balance/weight by book at train time** (don't overfit to GIA). Full-window (2007-2026) re-validation: **Forex PASSES outright** (PF 2.94, MAR 1.61) all regimes; equity books pass all but the MAR/Sortino the GFC drags down (documented tail; in-sample validations stand).
- **INTRADAY FX TEMPORAL FEATURES — Phase 1 OBSERVE-ONLY (commit `a974509`).** Scope: `research/INTRADAY_FX_TIMING_SCOPE.md`. Built `ibkr_feed.get_intraday_bars` (hourly), `data_loader.get_intraday_data` (replay-SAFE: no-intraday feed → empty, no lookahead) + `temporal_fx_features` (session/dow + intraday vol/ret from latest bar timestamp; {} when unavailable), merged into the FX marker snapshot — **logged into the corpus, execution UNCHANGED (daily)**. Verified live vs TWS. Honest limit: daily execution ⇒ entry hour/session ~constant; varying observe signals are day-of-week + intraday vol.

**ROADMAP — next steps once the live parent loop has proven itself** (ordered; the **parent live track record is the priority**, all else gated behind it):
0. **Operational-confidence checkpoint (~2-3 weeks, NOW running).** Let the cron + TWS auto-restart prove themselves across **≥1 weekly TWS re-auth cycle** + clean weekday runs. No build; just confirm reliability. Only manual touch: a weekly glance that TWS is logged in.
1. **Intraday FX — Phase 2 (ANALYZE) + Phase 3 (ACT) as ONE merged sprint — EFFORT-gated, NOT time-gated.** REFRAMES the original scope: do NOT wait on the live corpus (live FX is ~1 trade/wk ⇒ ~50/yr, day-of-week-only since the daily entry hour is constant). The real Phase 2 is an **intraday BACKTEST** over the ~2yr of available hourly history (IBKR/yfinance) → hundreds-thousands of intraday FX trades with session/hour/day labels in minutes. Build the intraday data layer + an **hourly ReplayFeed** (≈ most of Phase 3's infra), analyze session/day edges; **if a real stable edge exists → wire intraday cadence + session/time entry filters (Phase 3)**; validate recent-window only (honest: intraday history too short for a GFC stress test). **No edge → park intraday, keep daily.** Same evidence-first discipline that caught the no-edge ML scanner.
2. **Parent track-record maturation (calendar time, PRIORITY).** Books accrue live-data trades toward sample floors; periodic per-book validation (`python run_paper.py --cycles 0` validates the ledger without trading). Weeks-to-months.
3. **Local-model TRAINING pipeline (NOT built; scoped 2026-06-19 → `research/LOCAL_MODEL_TRAINING_SCOPE.md`).** IMPORTANT framing the operator confirmed: **today's engine is NOT a trained AI** — it's a deterministic regime-gate + rules + a *pre-trained, off-the-shelf* Ollama auditor (inference only). "Training a local AI on the corpus" is this future workstream, and it is evidence-gated, not assumed. Phased path: **Phase 0 — enrich** the corpus with counterfactual outcomes for NOT-acted candidates (only ~2.7k of 26.5k records are acted+labelled, GIA-only markers, replay `claude_score`=50 constant — so the raw labelled set is small + selection-biased; shadow-labelling not-acted candidates in replay turns ~1k into ~24k unbiased examples — do FIRST); **Phase A — cheap supervised PROBE** (gradient-boosted features→outcome, walk-forward OOS) to MEASURE whether any learnable edge beats the deterministic regime baseline — **if none, STOP** (the honest, likely answer: the edge is the regime gate; the system stays the validated deterministic engine + RAG for the child); **Phase B — LLM auditor QLoRA fine-tune** (7B fits the 3080 Ti in 4-bit) ONLY if Phase A shows OOS signal; **Phase C — RAG** (cheap, parallel, `saas/` scaffolded). Guardrails: a learned model must beat the deterministic baseline OUT-OF-SAMPLE, is never auto-promoted (DI backend swap → same per-book validation + sign-off gate), still PAPER. Prefer the smallest model that works.
4. **GCP/Vertex child (PARKED; `saas/` scaffolded).** `TenantTrainingStore` / `RagContextBuilder` / `VertexAuditor` (executes=False, never touches IBKR) exist in-repo. Live GCP (project, europe-west2, Secret Manager, `google-cloud-aiplatform`) begins ONLY when the operator is satisfied with the local track record + dataset.
5. **Live-authorization gate (operator-only; ultimate gate).** Going live needs a per-book pass **on the LIVE track record** (not just historical replay) AND a SEPARATE explicit operator sign-off. Everything above stays **100% PAPER** until then.
- **Housekeeping deferred:** `_exp_sizing.py` (untracked scratch harness — sweeps/validation/corpus) to be folded into a clean reusable `backtest/` tool the next time we re-validate (so it syncs across machines), not as standalone busywork.

### SaaS productization notes
- **Vertex "access" to training data = either (a) fine-tune a Vertex-hosted open model on the exported dataset, or (b) inject the data as context/RAG via the existing "Inference Context Bundle".** Foundation models do not share weights with the local Ollama model. Recommended path: (b) first (fast, no training infra), (a) later as the moat.
- **Regulatory (UK FCA) — DECIDED:** the SaaS is positioned as a **signals / decision-support tool** (the customer reviews and executes) — the least-regulatory-hurdle route, avoiding discretionary-management authorization. The cloud child **advises only; never executes**. Whitepaper + all product copy must reflect this stance and avoid any "we trade for you / managed" language.
- **No guaranteed performance:** frame success as **historically validated against the per-book criteria**, never a promise (markets are non-stationary). The validation gate is the honest trust signal.
- **Tenant data isolation:** the child trains only on the parent's curated export — never cross-tenant. Per-tenant DB isolation; no customer's positions/PII ever enter another tenant's model context. Design into the storage layer from day one.
