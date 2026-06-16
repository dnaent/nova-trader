import pandas as pd
from decimal import Decimal
from core.context import Candidate
from layers.data_loader import get_daily_data

class RegimeAwareScanner:
    def scan(self, universe: list[str], hmm_safe_prob: float) -> list[Candidate]:
        candidates = []
        is_trend_regime = hmm_safe_prob >= 0.5
        
        for symbol in universe:
            df = get_daily_data(symbol)
            if df.empty or len(df) < 50:
                continue
                
            close = df['Close'].iloc[-1]
            returns = df['Close'].pct_change(fill_method=None)
            
            if is_trend_regime:
                mom = (close / df['Close'].iloc[-21]) - 1
                score = max(0.0, min(100.0, 50 + mom * 500)) 
            else:
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                std20 = df['Close'].rolling(20).std().iloc[-1]
                lower_band = ma20 - 2 * std20
                if close > 0:
                    dist = (close - lower_band) / close
                    score = max(0.0, min(100.0, 100 - dist * 1000))
                else:
                    score = 0.0
                
            asset_class = "ETF" if symbol in ["SPY", "VWRL", "QQQ"] else "EQUITY"
            candidates.append(Candidate(symbol, asset_class, score, Decimal(str(round(close, 2)))))
            
        candidates.sort(key=lambda x: x.quant_score, reverse=True)
        return candidates
