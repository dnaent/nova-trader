# Weekend Optimisation Proposal - 2026_06_09

## Walk-Forward Validation Results
The walk-forward validation matrix tested various `gate_min` and `exec_threshold` parameters.
- **Current Base Sharpe (Simulated)**: ~0.8
- **Proposed Best Sharpe**: 0.88

**Proposed Changes to `portfolio.yaml`:**
```yaml
gate_min: 45
exec_threshold: 80
```

## Monte Carlo Stress Test
10,000 bootstrap shuffles of the historical trade sequence.
- **Mean Expected Max Drawdown**: 8.9%
- **95% Confidence Worst-Case Drawdown**: 15.1%
- **99% Confidence Worst-Case Drawdown**: 19.4%

> **Action Required**: Review the above parameters. If the 99% drawdown exceeds your comfort level, manually reduce `max_per_position_pct` in `portfolio.yaml`. The engine will NOT apply these changes automatically.
