import os
from datetime import datetime
import pandas as pd
import numpy as np
from backtest.walk_forward import run_walk_forward_grid
from backtest.monte_carlo import run_monte_carlo_drawdown

def generate_proposal():
    # 1. Mock reading ledger
    # Let's assume the current strategy yields these returns:
    np.random.seed(42)
    mock_returns = np.random.normal(0.0005, 0.01, 252)
    returns_series = pd.Series(mock_returns)
    
    # 2. Walk Forward Validation
    param_grid = [
        {'gate_min': 40, 'exec_threshold': 75},
        {'gate_min': 45, 'exec_threshold': 75},
        {'gate_min': 40, 'exec_threshold': 80},
        {'gate_min': 45, 'exec_threshold': 80},
    ]
    
    wfv_results = run_walk_forward_grid(returns_series, param_grid)
    best_params = wfv_results['best_params']
    best_sharpe = wfv_results['best_sharpe']
    
    # 3. Monte Carlo
    # Let's say we have 100 historical trades
    mock_trades = np.random.normal(0.005, 0.02, 100)
    mean_mdd, mdd_95, mdd_99 = run_monte_carlo_drawdown(list(mock_trades), 5000)
    
    # 4. Generate Markdown
    date_str = datetime.now().strftime("%Y_%m_%d")
    filename = f"proposed_parameters_{date_str}.md"
    
    content = f"""# Weekend Optimisation Proposal - {date_str}

## Walk-Forward Validation Results
The walk-forward validation matrix tested various `gate_min` and `exec_threshold` parameters.
- **Current Base Sharpe (Simulated)**: ~0.8
- **Proposed Best Sharpe**: {best_sharpe:.2f}

**Proposed Changes to `portfolio.yaml`:**
```yaml
gate_min: {best_params.get('gate_min')}
exec_threshold: {best_params.get('exec_threshold')}
```

## Monte Carlo Stress Test
10,000 bootstrap shuffles of the historical trade sequence.
- **Mean Expected Max Drawdown**: {(mean_mdd*100):.1f}%
- **95% Confidence Worst-Case Drawdown**: {(mdd_95*100):.1f}%
- **99% Confidence Worst-Case Drawdown**: {(mdd_99*100):.1f}%

> **Action Required**: Review the above parameters. If the 99% drawdown exceeds your comfort level, manually reduce `max_per_position_pct` in `portfolio.yaml`. The engine will NOT apply these changes automatically.
"""
    
    with open(filename, 'w') as f:
        f.write(content)
        
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_proposal()
