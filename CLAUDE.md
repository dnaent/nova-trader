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

## Phase 2 & 3 Additions
- **Continuous Sizing**: `gate_capacity` scales continuously from 70 to 40 instead of hard discrete steps.
- **Aggressive Liquidation**: If `aggressive_liquidation` is True in config, dropping below the `gate_min` will actively execute `SELL` orders for open positions to move to cash.
- **HMM Integration**: The Macro Gate blends VIX contango, Cross-Asset Correlation, and a Gaussian HMM (using *only* online filtered probabilities to prevent lookahead bias).
- **Multi-API Auditor**: Layer 3 supports `local` (Ollama/OpenAI compatible), `anthropic`, and `gemini` backends. The "Inference Context Bundle" (Macro markers + trailing 4Q financials) acts as the standardized prompt across all models.

## Local AI Model Training Requirements (3080Ti Deployment)
- **Primary Model**: Local LLaMA-based model running on 3080Ti via Ollama
- **Training Protocol**: Paper trading only until 75% success rate achieved across all books (GIA, ISA, SIPP)
- **Historical Validation**: Minimum 200 paper trades logged with detailed performance metrics
- **Success Criteria**:
  - 75%+ win rate across all account books
  - Maximum drawdown <5% on paper capital
  - Sharpe ratio >1.0 over 30+ trading days
  - Risk-adjusted returns consistently positive
- **Live Trading Gate**: Only activated after paper trading success validation
- **Model Architecture**: Fine-tuned quantitative trading model optimized for UK equity/ETF markets
- **Continuous Learning**: Model adapts based on live market conditions while maintaining risk guardrails

## Phase 4 & 5 Additions
- **Risk Guardrails**: Deterministic rules integrated directly into `core/engine.py` using the `RiskGuardrails` dataclass. Tracks Max Drawdown and Daily Loss Caps directly via the `nav_history` ledger. Evaluated *per-book* dynamically.
- **Mathematical Correlation**: The engine enforces a strict mathematical correlation check. `check_correlation()` in `core/risk.py` uses `yfinance` to compute a 90-day Pearson correlation matrix against all open positions to prevent over-exposure.
- **Terminal Dashboard**: A live terminal UI built with `rich` (`ui/dashboard.py`). It must remain decoupled from the engine process, reading strictly from the SQLite database to avoid latency in the engine loop.
- **Fault-Tolerance**: The engine is fully fault-tolerant against external API disconnects (yfinance failures, LLM timeouts). It gracefully falls back to a 50.0 score or default state without crashing the main loop.

## SaaS UI Infrastructure (COMPLETED 2026-06-11)
- **Design System**: Transitioned from Obsidian Glassmorphic to **Material-UI Joy** professional trading interface
- **Ultra-Low Latency Focus**: All UI components optimized for zero-delay trading operations
- **Trading Infrastructure**: Complete broker API integration, latency monitoring, and AI model validation systems
- **AI Safety Protocol**: Local 3080Ti model with mandatory 75%+ paper trading success before live deployment

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
