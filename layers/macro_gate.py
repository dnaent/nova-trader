import pandas as pd
from layers.data_loader import get_daily_data
from layers.hmm_regime import predict_regime_prob

class MacroGate:
    # Component weights for the composite gate. When every input feed is present
    # these sum to 1.0 and reproduce the original formula exactly; when a feed is
    # missing that component is dropped and the remaining weights are renormalised
    # (see evaluate()). Kept as named constants so the weighting is auditable.
    W_HMM = 0.5    # HMM regime (SPY returns) — the core component
    W_VIX = 0.3    # VIX term structure (^VIX / ^VIX3M)
    W_CORR = 0.2   # cross-asset safe-haven correlation (SPY/TLT/GLD)

    def evaluate(self) -> dict:
        """
        Calculate the composite 0-100 macro-gate score from up to three components:
          1. HMM regime probability (SPY returns)        — weight 0.5
          2. VIX term structure (^VIX / ^VIX3M)           — weight 0.3
          3. Cross-asset safe-haven correlation (SPY/TLT/GLD) — weight 0.2

        GRACEFUL DEGRADATION (fault tolerance): each component is computed only if
        its inputs are available. A missing/empty feed (a download hiccup live, or
        a date before an instrument existed in a historical replay) drops just that
        component and the remaining weights are renormalised — instead of the whole
        gate collapsing to a flat neutral 50 (which, being below every book's
        derisk_gate, would spuriously de-risk all books from a single missing feed).

        When all five feeds are present this is identical to the original formula
        (the weights sum to 1.0). Only the HMM/SPY component is mandatory; if SPY
        itself is unavailable the gate returns the neutral 50 fallback.

        Returns a dict with the overall score and the individual metrics (also used
        by the local LLM for context). `components_used` lists which were available.
        """
        spy = get_daily_data("SPY")
        if spy.empty:
            return {"gate_score": 50.0, "hmm_safe_prob": 0.5, "components_used": []}

        spy_returns = spy['Close'].pct_change(fill_method=None).dropna()
        safe_prob = predict_regime_prob(spy_returns)

        components: list[tuple[float, float]] = []   # (score_0_100, weight)
        used: list[str] = []
        result: dict = {"hmm_safe_prob": safe_prob}

        # 1. HMM regime — always available given SPY.
        components.append((float(safe_prob) * 100, self.W_HMM))
        used.append("hmm")

        # 2. VIX term structure — needs both ^VIX and ^VIX3M.
        vix = get_daily_data("^VIX")
        vix3m = get_daily_data("^VIX3M")
        if not vix.empty and not vix3m.empty:
            current_vix = vix['Close'].iloc[-1]
            current_vix3m = vix3m['Close'].iloc[-1]
            vix_ratio = current_vix / current_vix3m if current_vix3m > 0 else 1.0
            vix_score = max(0.0, min(100.0, (1.2 - vix_ratio) * 250))
            components.append((vix_score, self.W_VIX))
            used.append("vix")
            result["vix_ratio"] = float(vix_ratio)
            result["current_vix"] = float(current_vix)

        # 3. Cross-asset safe-haven correlation — needs SPY + TLT + GLD with >=30
        #    overlapping return days (always true for full-history validated runs,
        #    so this guard never changes their result).
        tlt = get_daily_data("TLT")
        gld = get_daily_data("GLD")
        if not tlt.empty and not gld.empty:
            df_corr = pd.DataFrame({
                'SPY': spy_returns,
                'TLT': tlt['Close'].pct_change(fill_method=None),
                'GLD': gld['Close'].pct_change(fill_method=None)
            }).dropna()
            if len(df_corr) >= 30:
                recent_corr = df_corr.iloc[-30:].corr()
                spy_tlt_corr = recent_corr.loc['SPY', 'TLT']
                spy_gld_corr = recent_corr.loc['SPY', 'GLD']
                avg_corr = (spy_tlt_corr + spy_gld_corr) / 2
                corr_score = max(0.0, min(100.0, (0.5 - avg_corr) * 100))
                components.append((corr_score, self.W_CORR))
                used.append("corr")
                result["avg_safe_haven_corr"] = float(avg_corr)

        # Yield-curve spread — informational context, not a gate component.
        tnx = get_daily_data("^TNX")
        irx = get_daily_data("^IRX")
        if not tnx.empty and not irx.empty:
            result["yield_curve_spread"] = float(tnx['Close'].iloc[-1] - irx['Close'].iloc[-1])
        else:
            result["yield_curve_spread"] = 0.0

        # Renormalise weights over the components actually computed.
        total_w = sum(w for _, w in components)
        blended = sum(s * w for s, w in components) / total_w if total_w > 0 else 50.0
        result["gate_score"] = float(max(0.0, min(100.0, blended)))
        result["components_used"] = used
        return result
