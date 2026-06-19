from __future__ import annotations
from typing import Iterable, Optional
from decimal import Decimal
import json

from core.context import Candidate
from layers.data_loader import (get_daily_data, get_technical_features,
                                get_recent_news, format_markers, temporal_fx_features)

# Tunables for the FX trend strategy (deterministic, point-in-time).
ADX_MIN = 20.0          # below this the pair is ranging -> no trend trade. (ADX 23 +
                        # 8 pairs in the risk overhaul thinned trades without helping
                        # edge — reverted to the proven 20 / 4-pair v1.)
EXCLUDE_COLS = {"Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"}


class FxAdapter:
    """Forex adapter — TREND-FOLLOWING redesign (2026-06-16).

    The previous DXY-proxy gate + ML breakout scanner had negative edge (PF 0.48,
    16 consecutive losses) — a breakout signal with no real alpha. This redesign:

      * SCANNER: classic trend-following. Long when EMA20 > EMA50 and price is above
        EMA50; short when EMA20 < EMA50 and price below EMA50 — but ONLY when ADX
        confirms a real trend (ADX >= ADX_MIN), otherwise no trade (sit out chop).
        Signals BOTH directions (Candidate.side) — essential for FX, where half the
        trends are USD-up. quant_score scales with ADX (trend strength).
      * GATE: a trend-REGIME gate. Trend-following only works when the FX complex is
        actually trending, so the gate reads the USD index (DXY) ADX: strong DXY
        trend (either direction) => high gate; chop => gate falls below the floor and
        the book holds cash. This is the opposite need from a mean-reversion book.

    All 32 markers stay universal (snapshotted into Candidate.meta['markers'] for the
    Inference Context Bundle + parent training records). Sizing/exits are unchanged:
    ATR sizing with the book's 5:1 leverage cap and 2% per-trade risk; judged at the
    account/equity-curve level per the FOREX validation profile.
    """
    asset_class = "FX"
    handles = {"FX"}
    strategy = "tactical"

    def __init__(self):
        self._last_gate_result: dict = {}

    # ----- Layer 1: trend-regime gate ------------------------------------- #
    def macro_gate(self) -> float:
        """Gate on whether the FX complex is TRENDING, via the USD index (DXY) ADX.

        A strong DXY trend (up OR down) means the majors are trending against the
        dollar — the regime trend-following needs. Chop (low ADX) => low gate =>
        the book holds cash. Maps roughly: ADX 15 -> 35 (parked), 25 -> 45,
        40 -> 60, 55 -> 75. Falls back to a neutral 50 on any data failure.
        """
        try:
            df = get_technical_features("DX-Y.NYB", lookback_days=400)
            adx = self._latest(df, "ADX_14")
            if adx is None:
                self._last_gate_result = {"regime": "Unknown", "gate_score": 50.0}
                return 50.0
            direction = self._direction(df)
            gate_score = float(min(85.0, max(25.0, 20.0 + adx)))
            self._last_gate_result = {
                "regime": f"{direction} (ADX {adx:.0f})",
                "dxy_adx": round(adx, 2),
                "dxy_direction": direction,
                "gate_score": gate_score,
            }
            return gate_score
        except Exception as e:                                  # fault-tolerant
            self._last_gate_result = {"error": str(e), "gate_score": 50.0}
            return 50.0

    # ----- Layer 2: trend-following scanner ------------------------------- #
    def scan(self, universe: Iterable[str]) -> list:
        """Emit at most one trend candidate per pair (long or short), strongest first."""
        out: list[Candidate] = []
        for symbol in universe:
            c = self._trend_candidate(symbol)
            if c is not None:
                out.append(c)
        out.sort(key=lambda x: x.quant_score, reverse=True)
        return out

    def _trend_candidate(self, symbol: str) -> Optional[Candidate]:
        df = get_technical_features(symbol, lookback_days=500)
        if df.empty:
            return None
        close = self._latest(df, "Close")
        ema_fast = self._latest(df, "EMA_20")
        ema_slow = self._latest(df, "EMA_50")
        adx = self._latest(df, "ADX_14")
        if None in (close, ema_fast, ema_slow, adx):
            return None
        if adx < ADX_MIN:
            return None                                        # ranging -> sit out

        if ema_fast > ema_slow and close > ema_slow:
            side = "BUY"
        elif ema_fast < ema_slow and close < ema_slow:
            side = "SELL"
        else:
            return None                                        # no aligned trend

        # quant_score scales with trend strength (ADX). ADX>=20 -> score>=60.
        quant_score = float(min(95.0, max(60.0, 40.0 + adx)))
        markers = {col: round(float(df.iloc[-1][col]), 6)
                   for col in df.columns if col not in EXCLUDE_COLS}
        # Phase-1 OBSERVE-ONLY temporal features (session/day/intraday-vol). Logged into
        # the marker snapshot for the corpus; does NOT affect side/score/sizing/exits.
        # Returns {} during replay (no point-in-time intraday) so the daily corpus is unchanged.
        markers.update(temporal_fx_features(symbol))
        return Candidate(
            symbol=symbol, asset_class=self.asset_class, quant_score=quant_score,
            price=Decimal(str(round(float(close), 6))), side=side,
            meta={"trend": side, "adx": round(adx, 2), "markers": markers},
        )

    # ----- Layer 3: auditor prompt ---------------------------------------- #
    def auditor_prompt(self, c: Candidate) -> str:
        """FX-specific prompt. Currencies have no financials, so focus on the trend
        signal, the macro (USD) regime and breaking news / central-bank risk."""
        news = get_recent_news(c.symbol)
        return (
            f"Please audit the following Currency Pair: {c.symbol}\n\n"
            f"=== INFERENCE CONTEXT BUNDLE ===\n"
            f"Trend signal: {c.meta.get('trend', '?')} (ADX {c.meta.get('adx', '?')})\n"
            f"Macro Environment (US Dollar regime):\n"
            f"{json.dumps(self._last_gate_result, indent=2) if self._last_gate_result else 'None'}\n\n"
            f"{format_markers(c.meta.get('markers', {}))}\n\n"
            f"Recent Geopolitical and Economic News:\n{news}\n"
            f"================================\n\n"
            f"This is a TREND-FOLLOWING candidate: judge whether the {c.meta.get('trend', '?')} "
            f"trend is likely to PERSIST or is exhausted / at risk from imminent central-bank "
            f"or geopolitical events. Provide your analysis, and end your response exactly "
            f"with 'SCORE: <number>'."
        )

    # ----- helpers -------------------------------------------------------- #
    @staticmethod
    def _latest(df, col: str):
        """Last non-NaN value of a column, or None if absent/empty."""
        import math
        if df is None or df.empty or col not in df.columns:
            return None
        val = df.iloc[-1][col]
        try:
            f = float(val)
        except (TypeError, ValueError):
            return None
        return None if math.isnan(f) else f

    def _direction(self, df) -> str:
        ema_fast = self._latest(df, "EMA_20")
        ema_slow = self._latest(df, "EMA_50")
        if ema_fast is None or ema_slow is None:
            return "Unknown"
        return "USD-up" if ema_fast > ema_slow else "USD-down"
