from __future__ import annotations
from typing import Iterable, Optional
from decimal import Decimal, ROUND_DOWN
import math
import pandas as pd
import json

from core.context import Candidate
from layers.macro_gate import MacroGate
from layers.data_loader import (get_financials, get_recent_news, format_markers,
                                get_intraday_features, get_technical_features,
                                temporal_fx_features)

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


# --------------------------------------------------------------------------- #
# Hybrid adapter helpers (module-level, fault-tolerant)
# --------------------------------------------------------------------------- #
_EXCLUDE_COLS = {"Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"}


def _latest(df, col: str) -> Optional[float]:
    """Last finite value of a column, or None if absent/empty/NaN."""
    if df is None or getattr(df, "empty", True) or col not in df.columns:
        return None
    try:
        f = float(df.iloc[-1][col])
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _col_prefix(row, prefix: str) -> Optional[float]:
    """First finite column in `row` whose name starts with `prefix` (e.g. MACD_)."""
    for c in row.index:
        if c.startswith(prefix):
            try:
                f = float(row[c])
            except (TypeError, ValueError):
                return None
            return None if math.isnan(f) else f
    return None


class HybridIntradayAdapter:
    """HYBRID of the two Forex implementations (built 2026-06-26).

    Merges the strengths of both prior FX designs into one multi-timeframe adapter,
    reused for FX and Crypto (and optionally equity intraday):

      * Layer 1 — REGIME GATE (from ``FxAdapter``): a higher-timeframe trend-regime
        gate on the asset complex's DRIVER. FX => the US-Dollar index (DX-Y.NYB) ADX;
        Crypto => Bitcoin (BTC-USD) ADX, the crypto-complex leader. Strong driver
        trend (either direction) => high gate; chop => gate falls below the floor and
        the book holds cash. (Equity intraday: ``regime_symbol=None`` => the general
        ``MacroGate``.) This restores the project's one proven edge — regime gating —
        that the naive ``gate_min: 0`` intraday book threw away.

      * Layer 2 — SIGNAL = DAILY trend skeleton + INTRADAY entry confluence:
        - DAILY trend bias (from ``FxAdapter``): EMA20/EMA50 + ADX on daily bars give
          the directional bias, and ONLY when ADX confirms a real trend (>= adx_min).
          This skeleton is what CAN be validated over years of history (the replay /
          walk-forward / Monte-Carlo harness is daily).
        - INTRADAY momentum (from ``IntradayAdapter``): 5-minute MACD/RSI/EMA200 gives
          the entry TIMING. It CONFIRMS (boosts conviction) when it agrees with the
          daily trend, and VETOES the trade when fresh intraday momentum opposes it.

      * GRACEFUL DEGRADATION (the honesty mechanism): intraday history does not exist
        in replay/backtest, so when intraday data is unavailable the adapter trades the
        DAILY trend skeleton alone. So the book is HISTORICALLY validatable on its daily
        skeleton, while the live book additionally refines entry with intraday timing.

    HONEST FRAMING (operator-acknowledged 2026-06-26): there is only so much edge we can
    PROVE in data for FX/Crypto — intraday timing edges can only be checked on a recent
    (short) window (no GFC-scale stress test), and the corrected-feature daily FX trend is
    weak. These books are therefore ROBUSTLY ENGINEERED (regime-gated, friction-aware,
    leverage-capped, circuit-broken) rather than strongly edge-proven — a deliberately
    LOWER trust tier than the daily-validated equity allocation books. They stay PAPER
    until the per-book account-level profile passes AND the operator authorizes live.
    """
    strategy = "intraday"

    def __init__(self, asset_class: str = "FX", handles: Optional[set] = None,
                 regime_symbol: Optional[str] = "DX-Y.NYB", *,
                 adx_min: float = 20.0, interval: str = "5m", lookback_days: int = 5,
                 friction_buffer: float = 0.0005):
        self.asset_class = asset_class
        self.handles = handles or {asset_class}
        self.regime_symbol = regime_symbol          # None => use the general MacroGate
        self.adx_min = float(adx_min)
        self.interval = interval
        self.lookback_days = lookback_days
        self.friction_buffer = friction_buffer
        self._macro = MacroGate() if regime_symbol is None else None
        self._last_gate_result: dict = {}

    # ----- Layer 1: regime gate ------------------------------------------- #
    def macro_gate(self) -> float:
        """Trend-regime gate on the complex driver (DXY for FX, BTC for Crypto), or
        the general MacroGate for equity intraday. Fault-tolerant: any failure falls
        back to a neutral 50.0 so the engine loop never crashes."""
        if self.regime_symbol is None:
            try:
                self._last_gate_result = self._macro.evaluate()
                return float(self._last_gate_result.get("gate_score", 50.0))
            except Exception as e:                                 # never crash the loop
                self._last_gate_result = {"error": str(e), "gate_score": 50.0}
                return 50.0
        try:
            df = get_technical_features(self.regime_symbol, lookback_days=400)
            adx = _latest(df, "ADX_14")
            if adx is None:
                self._last_gate_result = {"regime": "Unknown", "gate_score": 50.0}
                return 50.0
            direction = self._trend_direction(df)
            gate_score = float(min(85.0, max(25.0, 20.0 + adx)))
            self._last_gate_result = {
                "regime": f"{direction} (ADX {adx:.0f})",
                "driver": self.regime_symbol,
                "driver_adx": round(adx, 2),
                "driver_direction": direction,
                "gate_score": gate_score,
            }
            return gate_score
        except Exception as e:                                     # fault-tolerant
            self._last_gate_result = {"error": str(e), "gate_score": 50.0}
            return 50.0

    # ----- Layer 2: hybrid scanner ---------------------------------------- #
    def scan(self, universe: Iterable[str]) -> list:
        """Emit at most one candidate per symbol, strongest conviction first. Never
        raises — a bad symbol is skipped, not fatal."""
        out: list[Candidate] = []
        for symbol in universe:
            try:
                c = self._hybrid_candidate(symbol)
            except Exception:                                      # foolproof: skip, don't crash
                c = None
            if c is not None:
                out.append(c)
        out.sort(key=lambda x: x.quant_score, reverse=True)
        return out

    def _hybrid_candidate(self, symbol: str) -> Optional[Candidate]:
        # 1. DAILY trend skeleton (the historically-validatable base signal).
        daily = get_technical_features(symbol, lookback_days=500)
        close = _latest(daily, "Close")
        ema_fast = _latest(daily, "EMA_20")
        ema_slow = _latest(daily, "EMA_50")
        adx = _latest(daily, "ADX_14")
        if None in (close, ema_fast, ema_slow, adx):
            return None
        if adx < self.adx_min:
            return None                                            # ranging -> sit out
        if ema_fast > ema_slow and close > ema_slow:
            daily_side = "BUY"
        elif ema_fast < ema_slow and close < ema_slow:
            daily_side = "SELL"
        else:
            return None                                            # no aligned daily trend

        markers = {col: round(float(daily.iloc[-1][col]), 6)
                   for col in daily.columns
                   if col not in _EXCLUDE_COLS and pd.api.types.is_numeric_dtype(daily[col])}

        # 2. INTRADAY momentum confluence (entry-timing overlay). Returns
        #    (side, available): available=False in replay/no-intraday => trade the
        #    daily skeleton alone (graceful degradation, the honesty mechanism).
        intra_side, intra_available = self._intraday_signal(symbol, markers)
        if intra_available and intra_side is not None and intra_side != daily_side:
            return None                                            # MTF veto: momentum opposes the trend
        confirmed = bool(intra_available and intra_side == daily_side)

        # quant_score scales with daily trend strength (ADX); +confluence bonus.
        quant_score = float(min(95.0, max(60.0, 40.0 + adx)))
        if confirmed:
            quant_score = min(99.0, quant_score + 5.0)

        # FX-only temporal features (session/day/intraday-vol); {} in replay.
        if self.asset_class == "FX":
            markers.update(temporal_fx_features(symbol))

        return Candidate(
            symbol=symbol, asset_class=self.asset_class, quant_score=quant_score,
            price=Decimal(str(round(float(close), 6))), side=daily_side,
            meta={"trend": daily_side, "adx": round(adx, 2),
                  "intraday_confirmed": confirmed, "markers": markers,
                  "friction_buffer": self.friction_buffer},
        )

    def _intraday_signal(self, symbol: str, markers: dict) -> tuple[Optional[str], bool]:
        """Intraday MACD/RSI/EMA200 entry signal. Returns (side, available).

        ``available=False`` => no intraday data (replay/historical) so the caller
        trades the daily skeleton alone. ``side`` is "BUY"/"SELL" on a fresh MACD
        cross with RSI + EMA200 confirmation, else None (intraday is neutral — does
        NOT block the daily trend). Also merges intraday markers into the snapshot
        (prefixed ``intra_``) for the corpus + Inference Context Bundle.
        """
        df = get_intraday_features(symbol, interval=self.interval,
                                   lookback_days=self.lookback_days)
        if df is None or df.empty or len(df) < 2:
            return None, False
        last, prev = df.iloc[-1], df.iloc[-2]
        macd = _col_prefix(last, "MACD_")
        sig = _col_prefix(last, "MACDs_")
        macd_p = _col_prefix(prev, "MACD_")
        sig_p = _col_prefix(prev, "MACDs_")
        rsi = _col_prefix(last, "RSI_")
        ema200 = _latest(df, "EMA_200")
        try:
            price = float(last["Close"])
        except (TypeError, ValueError, KeyError):
            price = None
        if None in (macd, sig, macd_p, sig_p, rsi, ema200, price):
            return None, True                                      # data present but incomplete -> neutral

        markers.update({f"intra_{c}": round(float(last[c]), 6) for c in df.columns
                        if c not in _EXCLUDE_COLS and pd.api.types.is_numeric_dtype(df[c])})

        if macd > sig and macd_p < sig_p and rsi < 70 and price > ema200:
            return "BUY", True
        if macd < sig and macd_p > sig_p and rsi > 30 and price < ema200:
            return "SELL", True
        return None, True                                          # no fresh cross -> neutral

    # ----- Layer 3: auditor prompt ---------------------------------------- #
    def auditor_prompt(self, c: Candidate) -> str:
        """Asset-class-aware prompt. Currencies/crypto have no financials, so focus
        on the trend signal, the regime, and breaking news / sentiment."""
        financials = get_financials(c.symbol) if c.asset_class == "EQUITY" else "N/A for FX/Crypto."
        news = get_recent_news(c.symbol)
        confirmed = "CONFIRMED by intraday momentum" if c.meta.get("intraday_confirmed") \
            else "daily trend only (intraday neutral / unavailable)"
        return (
            f"Please audit the following HYBRID intraday {c.asset_class} candidate: {c.symbol}\n\n"
            f"=== INFERENCE CONTEXT BUNDLE ===\n"
            f"Trend signal: {c.meta.get('trend', '?')} (daily ADX {c.meta.get('adx', '?')}) — {confirmed}\n"
            f"Regime ({self.regime_symbol or 'macro'}):\n"
            f"{json.dumps(self._last_gate_result, indent=2) if self._last_gate_result else 'None'}\n\n"
            f"{format_markers(c.meta.get('markers', {}))}\n\n"
            f"Context (Financials/News):\n{financials}\n\n{news}\n"
            f"================================\n\n"
            f"This is a multi-timeframe TREND + MOMENTUM candidate. Judge whether the "
            f"{c.meta.get('trend', '?')} move is likely to PERSIST or is exhausted / at risk "
            f"from imminent central-bank, regulatory or geopolitical events. Provide your "
            f"analysis, and end your response exactly with 'SCORE: <number>'."
        )

    # ----- helpers -------------------------------------------------------- #
    @staticmethod
    def _trend_direction(df) -> str:
        ema_fast = _latest(df, "EMA_20")
        ema_slow = _latest(df, "EMA_50")
        if ema_fast is None or ema_slow is None:
            return "Unknown"
        return "Up" if ema_fast > ema_slow else "Down"
