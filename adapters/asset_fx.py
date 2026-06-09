from __future__ import annotations
from typing import Iterable
from decimal import Decimal
from core.context import Candidate
from layers.data_loader import get_daily_data, get_recent_news
import json

class FxAdapter:
    """Forex Adapter integrating FX-specific Macro Gate and Scanner."""
    asset_class = "FX"
    handles = {"FX"}

    def __init__(self):
        self._last_gate_result = {}

    def macro_gate(self) -> float:
        """
        Evaluate FX macro environment.
        Checks US Dollar Index (DXY) momentum as a proxy for FX regime.
        """
        try:
            # DX-Y.NYB is the US Dollar Index on Yahoo Finance
            df = get_daily_data("DX-Y.NYB", lookback_days=30)
            if df.empty or len(df) < 10:
                gate_score = 50.0
                trend = "Unknown"
            else:
                current_price = df['Close'].iloc[-1]
                sma_10 = df['Close'].rolling(window=10).mean().iloc[-1]
                
                if current_price > sma_10:
                    gate_score = 65.0
                    trend = "Bullish USD"
                else:
                    gate_score = 35.0
                    trend = "Bearish USD"
                    
            self._last_gate_result = {
                "dxy_trend": trend,
                "gate_score": gate_score
            }
            return gate_score
            
        except Exception as e:
            self._last_gate_result = {"error": str(e), "gate_score": 50.0}
            return 50.0

    def scan(self, universe: Iterable[str]) -> list:
        """
        Scan major FX pairs for momentum.
        """
        candidates = []
        for symbol in universe:
            try:
                df = get_daily_data(symbol, lookback_days=30)
                if df.empty or len(df) < 10:
                    continue
                    
                current_price = df['Close'].iloc[-1]
                sma_10 = df['Close'].rolling(window=10).mean().iloc[-1]
                
                # Simple momentum score based on distance from 10-day SMA
                momentum = ((current_price - sma_10) / sma_10) * 100
                
                # Normalize momentum to a 0-100 score (rough approximation)
                score = 50.0 + (momentum * 10.0) 
                score = max(0.0, min(100.0, score))
                
                candidates.append(Candidate(
                    symbol=symbol,
                    asset_class="FX",
                    quant_score=float(score),
                    price=Decimal(str(current_price)).quantize(Decimal("0.0001"))
                ))
            except Exception:
                continue
                
        # Sort by highest score
        candidates.sort(key=lambda c: c.quant_score, reverse=True)
        return candidates

    def auditor_prompt(self, c: Candidate) -> str:
        """
        FX-specific LLM Auditor prompt.
        Currencies don't have financials, so we focus on news and macro data.
        """
        news = get_recent_news(c.symbol)
        
        prompt = (
            f"Please audit the following Currency Pair: {c.symbol}\n\n"
            f"=== INFERENCE CONTEXT BUNDLE ===\n"
            f"Macro Environment (US Dollar Proxy):\n"
            f"{json.dumps(self._last_gate_result, indent=2) if self._last_gate_result else 'None'}\n\n"
            f"Recent Geopolitical and Economic News:\n"
            f"{news}\n"
            f"================================\n\n"
            f"Evaluate the currency pair's potential trajectory based on the USD Macro Environment "
            f"and any breaking geopolitical or central bank risks highlighted in the news. "
            f"Provide your analysis, and remember to end your response exactly with 'SCORE: <number>'."
        )
        return prompt
