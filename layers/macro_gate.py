import pandas as pd
from layers.data_loader import get_daily_data
from layers.hmm_regime import predict_regime_prob

class MacroGate:
    def evaluate(self) -> dict:
        """
        Calculates composite 0-100 gate score based on:
        1. HMM Regime (SPY returns)
        2. VIX Term Structure
        3. Cross-Asset Correlation
        
        Returns a dict containing the overall score and the individual metrics
        (which can also be used by the local LLM for context).
        """
        spy = get_daily_data("SPY")
        vix = get_daily_data("^VIX")
        vix3m = get_daily_data("^VIX3M")
        tlt = get_daily_data("TLT")
        gld = get_daily_data("GLD")
        tnx = get_daily_data("^TNX")
        irx = get_daily_data("^IRX")
        
        if any(df.empty for df in [spy, vix, vix3m, tlt, gld]):
            return {"gate_score": 50.0, "hmm_safe_prob": 0.5}
            
        spy_returns = spy['Close'].pct_change(fill_method=None).dropna()
        safe_prob = predict_regime_prob(spy_returns)
        
        current_vix = vix['Close'].iloc[-1]
        current_vix3m = vix3m['Close'].iloc[-1]
        vix_ratio = current_vix / current_vix3m if current_vix3m > 0 else 1.0
        vix_score = max(0.0, min(100.0, (1.2 - vix_ratio) * 250))
        
        yield_spread = 0.0
        if not tnx.empty and not irx.empty:
            yield_spread = float(tnx['Close'].iloc[-1] - irx['Close'].iloc[-1])
        
        df_corr = pd.DataFrame({
            'SPY': spy_returns,
            'TLT': tlt['Close'].pct_change(fill_method=None),
            'GLD': gld['Close'].pct_change(fill_method=None)
        }).dropna()
        
        recent_corr = df_corr.iloc[-30:].corr()
        spy_tlt_corr = recent_corr.loc['SPY', 'TLT']
        spy_gld_corr = recent_corr.loc['SPY', 'GLD']
        avg_corr = (spy_tlt_corr + spy_gld_corr) / 2
        corr_score = max(0.0, min(100.0, (0.5 - avg_corr) * 100))
        
        blended_score = (safe_prob * 100 * 0.5) + (vix_score * 0.3) + (corr_score * 0.2)
        gate_score = float(max(0.0, min(100.0, blended_score)))
        
        return {
            "gate_score": gate_score,
            "hmm_safe_prob": safe_prob,
            "vix_ratio": float(vix_ratio),
            "avg_safe_haven_corr": float(avg_corr),
            "current_vix": float(current_vix),
            "yield_curve_spread": yield_spread
        }
