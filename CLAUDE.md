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
