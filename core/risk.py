from __future__ import annotations
from decimal import Decimal, ROUND_DOWN
from typing import Protocol, runtime_checkable

from core.context import AccountContext, Candidate, Order
from layers.data_loader import get_daily_data
import pandas as pd
import numpy as np

def check_correlation(candidate_symbol: str, open_symbols: list[str], max_corr: float) -> tuple[bool, str]:
    """Returns (True, reason) if correlation with any open position exceeds max_corr. False otherwise."""
    if not open_symbols:
        return False, ""
        
    try:
        cand_df = get_daily_data(candidate_symbol, lookback_days=90)
        if cand_df.empty or "Close" not in cand_df.columns:
            return False, ""
        cand_returns = cand_df["Close"].pct_change().dropna()
        
        for osym in open_symbols:
            o_df = get_daily_data(osym, lookback_days=90)
            if o_df.empty or "Close" not in o_df.columns:
                continue
            o_returns = o_df["Close"].pct_change().dropna()
            
            # Align indices
            aligned = pd.concat([cand_returns, o_returns], axis=1, join="inner")
            if len(aligned) < 30: # Need at least 30 days of overlap to be meaningful
                continue
            corr = float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))
            if corr > max_corr:
                return True, f"corr {corr:.2f} with {osym} > {max_corr}"
                
    except Exception:
        pass
        
    return False, ""


def gate_capacity(gate_score: float) -> Decimal:
    """Macro-gate capacity factor: continuous scaling between 40 and 70."""
    if gate_score >= 70:
        return Decimal("1.0")
    if gate_score <= 40:
        return Decimal("0.0")
    
    capacity = (gate_score - 40.0) / 30.0
    return Decimal(str(capacity)).quantize(Decimal("0.01"))


class NavPctSizing:
    """
    NAV-based sizing scaled by the macro gate (replaces the old £100 budget logic).
    Allocation = NAV * max_per_position_pct% * capacity(gate). Whole shares only
    in Phase 1 (fractional support is a later refinement). Placeholder brackets.
    """
    def __init__(self, max_per_position_pct: float = 8.0, leverage: float = 1.0,
                 unit: str = "shares", stop_pct: float = 0.05, take_pct: float = 0.10):
        self.max_per_position_pct = Decimal(str(max_per_position_pct))
        self.leverage = Decimal(str(leverage))
        self.unit = unit
        self.stop_pct = Decimal(str(stop_pct))
        self.take_pct = Decimal(str(take_pct))

    def size(self, candidate: Candidate, ctx: AccountContext, gate_score: float) -> Order:
        capacity = gate_capacity(gate_score)
        allocation = (ctx.nav * (self.max_per_position_pct / Decimal("100"))
                      * capacity * self.leverage)
        price = Decimal(candidate.price)
        qty = (allocation / price).to_integral_value(rounding=ROUND_DOWN) if price > 0 else Decimal("0")
        notional = (qty * price).quantize(Decimal("0.01"))
        return Order(
            book_id=ctx.book_id,
            account_id=ctx.ibkr_account_id,
            symbol=candidate.symbol,
            side="BUY",
            quantity=qty,
            price=price,
            notional=notional,
            stop_loss=(price * (Decimal("1") - self.stop_pct)).quantize(Decimal("0.01")),
            take_profit=(price * (Decimal("1") + self.take_pct)).quantize(Decimal("0.01")),
            meta={"capacity_factor": str(capacity)},
        )

def calculate_atr(symbol: str, lookback_days: int = 14) -> Decimal:
    """Calculate the 14-day Average True Range (ATR) for position sizing."""
    try:
        # Fetch slightly more days to ensure we have enough trading days for the rolling window
        df = get_daily_data(symbol, lookback_days=lookback_days + 10)
        if df.empty or len(df) < lookback_days:
            return Decimal("0")
            
        high = df['High']
        low = df['Low']
        close_prev = df['Close'].shift(1)
        
        tr = np.maximum(high - low, 
             np.maximum(abs(high - close_prev), abs(low - close_prev)))
        
        # Simple moving average of TR for ATR
        atr = tr.rolling(window=lookback_days).mean().iloc[-1]
        
        if pd.isna(atr):
            return Decimal("0")
        return Decimal(str(atr)).quantize(Decimal("0.0001"))
    except Exception:
        return Decimal("0")

class AtrSizing:
    """
    ATR-based sizing scaled by the macro gate.
    Allocation units = (Risk Capital per trade) / ATR
    Risk Capital = NAV * risk_pct (e.g., 2% of portfolio at risk)
    """
    def __init__(self, risk_pct: float = 2.0, leverage: float = 1.0,
                 unit: str = "shares", stop_atr_multiplier: float = 2.0, take_atr_multiplier: float = 4.0):
        self.risk_pct = Decimal(str(risk_pct))
        self.leverage = Decimal(str(leverage))
        self.unit = unit
        self.stop_atr_multiplier = Decimal(str(stop_atr_multiplier))
        self.take_atr_multiplier = Decimal(str(take_atr_multiplier))

    def size(self, candidate: Candidate, ctx: AccountContext, gate_score: float) -> Order:
        capacity = gate_capacity(gate_score)
        price = Decimal(candidate.price)
        
        # Calculate ATR
        atr = calculate_atr(candidate.symbol)
        
        if atr == Decimal("0") or price == Decimal("0"):
            # Fallback to zero sizing if ATR cannot be calculated
            return Order(
                book_id=ctx.book_id, account_id=ctx.ibkr_account_id, symbol=candidate.symbol, side="BUY",
                quantity=Decimal("0"), price=price, notional=Decimal("0")
            )
            
        # Capital at risk = NAV * risk_pct * gate_capacity
        capital_at_risk = (ctx.nav * (self.risk_pct / Decimal("100")) * capacity)
        
        # Number of shares = capital at risk / (ATR * stop multiplier)
        qty = (capital_at_risk / (atr * self.stop_atr_multiplier)).to_integral_value(rounding=ROUND_DOWN)
        
        notional = (qty * price).quantize(Decimal("0.01"))
        
        stop_loss = (price - (atr * self.stop_atr_multiplier)).quantize(Decimal("0.01"))
        take_profit = (price + (atr * self.take_atr_multiplier)).quantize(Decimal("0.01"))
        
        return Order(
            book_id=ctx.book_id,
            account_id=ctx.ibkr_account_id,
            symbol=candidate.symbol,
            side="BUY",
            quantity=qty,
            price=price,
            notional=notional,
            stop_loss=stop_loss,
            take_profit=take_profit,
            meta={"capacity_factor": str(capacity), "atr": str(atr)}
        )

