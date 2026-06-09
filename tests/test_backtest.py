import numpy as np
import pandas as pd
from backtest.monte_carlo import calculate_max_drawdown, run_monte_carlo_drawdown
from backtest.walk_forward import run_walk_forward_grid

def test_calculate_max_drawdown():
    # Peak at 1.0, drops to 0.8 -> 20% drawdown
    equity = np.array([1.0, 0.9, 0.8, 0.95, 1.1])
    mdd = calculate_max_drawdown(equity)
    assert np.isclose(mdd, 0.2)

def test_run_monte_carlo():
    trades = [0.01, -0.02, 0.03, -0.01, 0.05, -0.03]
    mean, p95, p99 = run_monte_carlo_drawdown(trades, num_simulations=100)
    assert 0 <= mean <= 1
    assert 0 <= p95 <= 1
    assert 0 <= p99 <= 1
    assert mean <= p95 <= p99

def test_walk_forward():
    returns = pd.Series(np.random.normal(0.001, 0.01, 100))
    grid = [{'gate_min': 40}, {'gate_min': 50}]
    res = run_walk_forward_grid(returns, grid)
    assert 'best_params' in res
    assert 'best_sharpe' in res
