from __future__ import annotations
from typing import Iterable
from decimal import Decimal, ROUND_DOWN
import pandas as pd
import json

from core.context import Candidate
from layers.macro_gate import MacroGate
from layers.data_loader import get_financials, get_recent_news, format_markers, get_intraday_features

class IntradayAdapter:
    """Intraday Adapter integrating 5-minute EMA/MACD/RSI logic."""
    asset_class = "INTRADAY"
    handles = {"EQUITY", "ETF", "FX", "CRYPTO"}
    strategy = "intraday"

    def __init__(self):
        self.gate = MacroGate()
        self._last_gate_result = {}

    def macro_gate(self) -> float:
        self._last_gate_result = self.gate.evaluate()
        return self._last_gate_result.get("gate_score", 50.0)

    def scan(self, universe: Iterable[str]) -> list:
        candidates = []
        for symbol in universe:
            # 5-minute data with full 30+ indicator matrix
            df = get_intraday_features(symbol, interval="5m", lookback_days=5)
            if df.empty or len(df) < 2:
                continue

            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            def get_col(prefix, row):
                for c in row.index:
                    if c.startswith(prefix):
                        return row[c]
                return None

            ema_200 = get_col("EMA_200", last)
            macd_line = get_col("MACD_", last)
            signal_line = get_col("MACDs_", last)
            macd_line_prev = get_col("MACD_", prev)
            signal_line_prev = get_col("MACDs_", prev)
            rsi = get_col("RSI_", last)
            price = last["Close"]

            if None in (ema_200, macd_line, signal_line, macd_line_prev, signal_line_prev, rsi):
                continue
            
            # Friction buffer for bracket logic
            friction_buffer = 0.0005 # 0.05%

            is_long = (
                macd_line > signal_line and
                macd_line_prev < signal_line_prev and
                rsi < 70 and
                price > ema_200
            )

            is_short = (
                macd_line < signal_line and
                macd_line_prev > signal_line_prev and
                rsi > 30 and
                price < ema_200
            )

            if is_long or is_short:
                side = "BUY" if is_long else "SELL"
                # Store all markers for the LLM Auditor
                markers = {c: float(last[c]) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])}
                c = Candidate(
                    symbol=symbol,
                    asset_class="INTRADAY", 
                    quant_score=100.0, 
                    price=price,
                    meta={
                        "markers": markers,
                        "side": side,
                        "friction_buffer": friction_buffer
                    }
                )
                c.side = side 
                
                # Determine asset class from symbol format
                if len(symbol) == 6 and not symbol.endswith(".L") and not symbol.endswith("-USD"):
                    c.asset_class = "FX"
                elif symbol.endswith("-USD") or symbol in ["BTC", "ETH"]:
                    c.asset_class = "CRYPTO"
                else:
                    c.asset_class = "EQUITY"
                    
                candidates.append(c)

        return candidates

    def auditor_prompt(self, c: Candidate) -> str:
        financials = get_financials(c.symbol) if c.asset_class == "EQUITY" else "N/A for FX/Crypto."
        news = get_recent_news(c.symbol)
        
        prompt = (
            f"Please audit the following INTRADAY candidate: {c.symbol}\n\n"
            f"=== INFERENCE CONTEXT BUNDLE ===\n"
            f"Macro Environment:\n"
            f"{json.dumps(self._last_gate_result, indent=2) if self._last_gate_result else 'None'}\n\n"
            f"{format_markers(c.meta.get('markers', {}))}\n\n"
            f"Signal Direction: {c.meta.get('side', 'BUY')}\n\n"
            f"Context (Financials/News):\n"
            f"{financials}\n\n"
            f"{news}\n"
            f"================================\n\n"
            f"Evaluate the intraday momentum, volatility, and news context to determine if this {c.meta.get('side')} trade has edge for the next few hours. "
            f"Provide your analysis, and remember to end your response exactly with 'SCORE: <number>'."
        )
        return prompt
