---
name: ledger-audit
description: Instructs the agent on how to audit the SQLite transaction ledger, verify UK CGT allowance utilization, and cross-reference account NAV logs against broker states.
---

# Ledger Audit Skill

This skill provides step-by-step instructions for querying, validating, and reporting balance sheets and tax liabilities recorded in the SQLite database ledger (`nova_ledger.db`).

## Applicability
Activate this skill when:
- The user requests to "audit ledger" or "check tax liability".
- You need to verify that realized gains are within wrapper allowances (e.g. GIA CGT allowance).
- You need to check the consistency of NAV history logs.

## Core SQL Queries & Audits

### 1. Connecting to the SQLite Database
Use `sqlite3` to connect to `nova_ledger.db`:
```python
import sqlite3
conn = sqlite3.connect("nova_ledger.db")
```

### 2. Auditing GIA Wrapper Gains & CGT Liabilities
Verify GIA wrapper gains during the active tax year:
- Query completed sell trades inside `trades` table.
- Calculate cost basis and realized gain.
- Cross-reference against the UK CGT exemption allowance limit (£3,000 for the tax year).
- If the realized gains exceed or are within 5% of the limit, ensure the routing system is redirecting buys to the tax-free ISA wrapper.

### 3. NAV Consistency Check
Verify that the `nav_history` matches the sum of positions:
- Verify that NAV logs show a monotonic and consistent curve without sudden irregular spikes that could indicate pricing API errors.
- Confirm peak NAV matches values retrieved in drawdown checks inside the risk management engine.
