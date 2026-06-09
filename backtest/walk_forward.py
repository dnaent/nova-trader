import numpy as np
import pandas as pd
from typing import List, Dict

def run_walk_forward_grid(returns: pd.Series, param_grid: List[Dict]) -> Dict:
    """
    Simulate Walk-Forward Validation across different parameter grids.
    This is a mocked scaffold for the parameter search.
    In a live system, this would actually run the engine loop over historical data.
    Here we calculate a simulated Sharpe ratio shift based on parameters to demonstrate the loop.
    """
    best_param = None
    best_sharpe = -999.0
    
    results = []
    
    for params in param_grid:
        # Mock calculation: 
        # Tighter execution threshold slightly improves sharpe, but reduces trade count
        # Higher gate minimum reduces drawdown but reduces total return
        base_sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(252) if len(returns) > 0 else 0
        
        simulated_sharpe = base_sharpe
        
        exec_thresh = params.get('exec_threshold', 75)
        if exec_thresh > 75:
            simulated_sharpe += 0.1 * ((exec_thresh - 75) / 5)
            
        gate_min = params.get('gate_min', 40)
        if gate_min > 40:
            simulated_sharpe += 0.05 * ((gate_min - 40) / 5)
            
        # Add a tiny bit of random noise
        simulated_sharpe += np.random.normal(0, 0.05)
        
        results.append({
            'params': params,
            'simulated_sharpe': simulated_sharpe
        })
        
        if simulated_sharpe > best_sharpe:
            best_sharpe = simulated_sharpe
            best_param = params
            
    return {
        'best_params': best_param,
        'best_sharpe': best_sharpe,
        'all_results': results
    }
