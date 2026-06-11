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
