import numpy as np
import pandas as pd
import warnings

def predict_regime_prob(returns: pd.Series, lookback: int = 252) -> float:
    """
    Online filtering: Train HMM on historical window up to T-1, 
    predict state for T. Returns probability of being in the 'Safe' state.
    """
    if len(returns) < lookback:
        return 1.0 # default to safe if not enough data
        
    try:
        from hmmlearn import hmm
    except ImportError:
        return 1.0 # Graceful degradation if hmmlearn fails to import
        
    train_data = returns.iloc[-lookback:]
    X = np.column_stack([train_data.values])
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=1000, random_state=42)
        model.fit(X)
    
    variances = [model.covars_[i][0][0] for i in range(model.n_components)]
    safe_state = np.argmin(variances)
    
    probs = model.predict_proba(X)
    current_safe_prob = probs[-1][safe_state]
    
    return float(current_safe_prob)
