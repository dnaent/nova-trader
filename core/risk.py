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
        cand_returns = cand_df["Close"].pct_change(fill_method=None).dropna()

        for osym in open_symbols:
            o_df = get_daily_data(osym, lookback_days=90)
            if o_df.empty or "Close" not in o_df.columns:
                continue
            o_returns = o_df["Close"].pct_change(fill_method=None).dropna()
            
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
                 unit: str = "shares", stop_pct: float = 0.05, take_pct: float = 0.10, trailing_pct: float = 0.05):
        self.max_per_position_pct = Decimal(str(max_per_position_pct))
        self.leverage = Decimal(str(leverage))
        self.unit = unit
        self.stop_pct = Decimal(str(stop_pct))
        self.take_pct = Decimal(str(take_pct))
        self.trailing_pct = Decimal(str(trailing_pct))

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
            trailing_pct=self.trailing_pct,
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
                 unit: str = "shares", stop_atr_multiplier: float = 2.0, take_atr_multiplier: float = 4.0, trailing_atr_multiplier: float = 2.0):
        self.risk_pct = Decimal(str(risk_pct))
        self.leverage = Decimal(str(leverage))
        self.unit = unit
        self.stop_atr_multiplier = Decimal(str(stop_atr_multiplier))
        self.take_atr_multiplier = Decimal(str(take_atr_multiplier))
        self.trailing_atr_multiplier = Decimal(str(trailing_atr_multiplier))

    def size(self, candidate: Candidate, ctx: AccountContext, gate_score: float) -> Order:
        capacity = gate_capacity(gate_score)
        price = Decimal(candidate.price)
        side = getattr(candidate, "side", "BUY")     # FX trend-following signals both sides

        # Calculate ATR
        atr = calculate_atr(candidate.symbol)

        if atr == Decimal("0") or price == Decimal("0"):
            # Fallback to zero sizing if ATR cannot be calculated
            return Order(
                book_id=ctx.book_id, account_id=ctx.ibkr_account_id, symbol=candidate.symbol, side=side,
                quantity=Decimal("0"), price=price, notional=Decimal("0")
            )

        # Capital at risk = NAV * risk_pct * gate_capacity
        capital_at_risk = (ctx.nav * (self.risk_pct / Decimal("100")) * capacity)

        # Number of shares = capital at risk / (ATR * stop multiplier)
        qty = (capital_at_risk / (atr * self.stop_atr_multiplier)).to_integral_value(rounding=ROUND_DOWN)

        notional = (qty * price).quantize(Decimal("0.01"))

        # Leverage cap: notional exposure must not exceed NAV * leverage.
        # For FX this enforces the book's leverage limit (e.g. <= 5:1); for a
        # default leverage of 1.0 it caps exposure at NAV (no implicit margin).
        max_notional = (ctx.nav * self.leverage)
        if notional > max_notional and price > 0:
            qty = (max_notional / price).to_integral_value(rounding=ROUND_DOWN)
            notional = (qty * price).quantize(Decimal("0.01"))

        # Price precision: quantizing FX stops/takes to 0.01 destroys pip-level
        # risk (EURUSD ATR ~0.005). Use 4 dp for sub-50 prices (FX majors), 2 dp
        # otherwise (equities, USDJPY).
        quantum = Decimal("0.0001") if price < Decimal("50") else Decimal("0.01")
        stop_dist = atr * self.stop_atr_multiplier
        take_dist = atr * self.take_atr_multiplier
        # Fixed ATR take-profit captures the move (this is what gave the trend book
        # its edge: PF 2.12). A trailing-only / no-take variant gave back ~2 ATR per
        # winner and destroyed the profit factor (PF 0.74) — reverted 2026-06-16.
        # trailing_atr is left OFF on the order (engine trails only when set).
        if side == "SELL":
            stop_loss = (price + stop_dist).quantize(quantum)   # short: stop ABOVE entry
            take_profit = (price - take_dist).quantize(quantum)  # ...take BELOW
        else:
            stop_loss = (price - stop_dist).quantize(quantum)
            take_profit = (price + take_dist).quantize(quantum)

        return Order(
            book_id=ctx.book_id,
            account_id=ctx.ibkr_account_id,
            symbol=candidate.symbol,
            side=side,
            quantity=qty,
            price=price,
            notional=notional,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_atr=None,          # trailing OFF: fixed take captures the trend edge
            meta={"capacity_factor": str(capacity), "atr": str(atr)}
        )


class FrictionSizing:
    """
    Intraday friction-aware sizing — the port of Isaak's FrictionAwareMacdRsi design
    (research/archive/crypto/isaak_strategy_python). Brackets hang off a friction-
    adjusted NET ENTRY (the price you realistically fill at after spread/fees), so the
    take-profit is measured from that net entry and the stop isn't clipped by friction.

    Sizing keeps Nova's multi-book risk discipline (risk-based qty off the real stop
    distance, scaled by the macro gate, capped by book leverage) rather than Isaak's
    single-book fixed-notional (60%) bet — safer across GIA/ISA/SIPP/FX/Crypto.
    """
    def __init__(self, risk_pct: float = 2.0, leverage: float = 1.0,
                 unit: str = "shares", stop_pct: float = 0.05, take_pct: float = 0.10,
                 friction_buffer: float = 0.0005):
        self.risk_pct = Decimal(str(risk_pct))
        self.leverage = Decimal(str(leverage))
        self.unit = unit
        self.stop_pct = Decimal(str(stop_pct))
        self.take_pct = Decimal(str(take_pct))
        self.friction_buffer = Decimal(str(friction_buffer))

    def size(self, candidate: Candidate, ctx: AccountContext, gate_score: float) -> Order:
        capacity = gate_capacity(gate_score)
        price = Decimal(candidate.price)
        side = getattr(candidate, "side", "BUY")

        # Per-candidate friction override (e.g. wider for crypto spreads), else the book default.
        friction = Decimal(str(candidate.meta.get("friction_buffer", self.friction_buffer)))

        if price == Decimal("0"):
            return Order(
                book_id=ctx.book_id, account_id=ctx.ibkr_account_id, symbol=candidate.symbol, side=side,
                quantity=Decimal("0"), price=price, notional=Decimal("0")
            )

        # Isaak's friction-relative brackets: assume the fill is slightly WORSE than the
        # last price (a long fills higher, a short lower), then set TP/SL off that net entry.
        if side == "SELL":
            net_entry = price * (Decimal("1") - friction)               # short fills lower
            stop_loss = net_entry * (Decimal("1") + self.stop_pct)      # stop ABOVE entry
            take_profit = net_entry * (Decimal("1") - self.take_pct)    # take BELOW entry
        else:
            net_entry = price * (Decimal("1") + friction)               # long fills higher
            stop_loss = net_entry * (Decimal("1") - self.stop_pct)
            take_profit = net_entry * (Decimal("1") + self.take_pct)

        # Risk-based quantity off the REAL (friction-adjusted) stop distance, gate-scaled.
        stop_dist = abs(net_entry - stop_loss)
        capital_at_risk = (ctx.nav * (self.risk_pct / Decimal("100")) * capacity)
        qty = (capital_at_risk / stop_dist).to_integral_value(rounding=ROUND_DOWN) \
            if stop_dist > 0 else Decimal("0")
        notional = (qty * price).quantize(Decimal("0.01"))

        # Leverage cap: notional exposure must not exceed NAV * leverage (FX <=5:1, crypto <=2:1).
        max_notional = (ctx.nav * self.leverage)
        if notional > max_notional and price > 0:
            qty = (max_notional / price).to_integral_value(rounding=ROUND_DOWN)
            notional = (qty * price).quantize(Decimal("0.01"))

        # FX needs 4 dp (pip-level); equities/crypto 2 dp.
        quantum = Decimal("0.0001") if price < Decimal("50") else Decimal("0.01")
        return Order(
            book_id=ctx.book_id,
            account_id=ctx.ibkr_account_id,
            symbol=candidate.symbol,
            side=side,
            quantity=qty,
            price=price,
            notional=notional,
            stop_loss=stop_loss.quantize(quantum),
            take_profit=take_profit.quantize(quantum),
            meta={"capacity_factor": str(capacity),
                  "net_entry": str(net_entry.quantize(quantum)),
                  "friction": str(friction)}
        )

