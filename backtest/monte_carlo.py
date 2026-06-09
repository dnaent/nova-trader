import numpy as np
from typing import List, Tuple

def calculate_max_drawdown(equity_curve: np.ndarray) -> float:
    """Calculate maximum drawdown of an equity curve."""
    if len(equity_curve) == 0:
        return 0.0
    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = (peaks - equity_curve) / peaks
    return np.max(drawdowns)

def run_monte_carlo_drawdown(trade_returns: List[float], num_simulations: int = 10000) -> Tuple[float, float, float]:
    """
    Bootstrap trade sequence to find 95% and 99% Max Drawdown bounds.
    """
    if not trade_returns:
        return 0.0, 0.0, 0.0
        
    returns_array = np.array(trade_returns)
    max_drawdowns = []
    
    for _ in range(num_simulations):
        # Sample with replacement
        shuffled = np.random.choice(returns_array, size=len(returns_array), replace=True)
        # Build equity curve starting at 1.0
        equity_curve = np.cumprod(1.0 + shuffled)
        mdd = calculate_max_drawdown(equity_curve)
        max_drawdowns.append(mdd)
        
    max_drawdowns.sort()
    
    mean_mdd = np.mean(max_drawdowns)
    mdd_95 = np.percentile(max_drawdowns, 95)
    mdd_99 = np.percentile(max_drawdowns, 99)
    
    return mean_mdd, mdd_95, mdd_99
