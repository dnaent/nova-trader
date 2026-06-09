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

## Phase 4 & 5 Additions
- **Risk Guardrails**: Deterministic rules integrated directly into `core/engine.py` using the `RiskGuardrails` dataclass. Tracks Max Drawdown and Daily Loss Caps directly via the `nav_history` ledger. Evaluated *per-book* dynamically.
- **Mathematical Correlation**: The engine enforces a strict mathematical correlation check. `check_correlation()` in `core/risk.py` uses `yfinance` to compute a 90-day Pearson correlation matrix against all open positions to prevent over-exposure.
- **Terminal Dashboard**: A live terminal UI built with `rich` (`ui/dashboard.py`). It must remain decoupled from the engine process, reading strictly from the SQLite database to avoid latency in the engine loop.
- **Fault-Tolerance**: The engine is fully fault-tolerant against external API disconnects (yfinance failures, LLM timeouts). It gracefully falls back to a 50.0 score or default state without crashing the main loop.

## UI/UX & Developer Skills Guidelines
- **Developer Skills**: Repository-specific automation workflows are defined under the `skills/` directory. Each skill folder contains a `SKILL.md` defining its operational rules (e.g. [backtest-optimization](file:///Users/Phantom/Desktop/DNAENT™/Nova_Trader/skills/backtest-optimization/SKILL.md), [ledger-audit](file:///Users/Phantom/Desktop/DNAENT™/Nova_Trader/skills/ledger-audit/SKILL.md)).
- **SaaS UI Design**: Employs an **Obsidian Glassmorphic** visual system (moving away from neumorphic shadows). Key rules: deep background `#0e0e0e`, boundaries defined via color shifts rather than opaque border lines, frosted card surfaces with `backdrop-filter: blur(20px)`, glowing orange/teal primary accents, and Space Mono / JetBrains Mono typography.
