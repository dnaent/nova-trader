"""
Nova Engine — adapters/ibkr_feed.py

Read-only IBKR real-time market-data feed (roadmap item #1). A persistent
connection manager over `ib_async` that supplies prices + daily bars to the
hot path (scanner + macro gate), with yfinance kept as the fallback.

HARD SAFETY: this connects with ``readonly=True`` so IBKR itself refuses any
order from this session — it can ONLY read market data. Execution lives in
`broker_ibkr.py` and remains stubbed/paper. This module never places an order.

Connection (TWS vs IB Gateway is just a port — ib_async is identical for both):
    * TWS         paper 7497 / live 7496   (default here: dev + paper-validation)
    * IB Gateway  paper 4002 / live 4001   (later, for the always-on box)

Enable in TWS: Global Configuration -> API -> Settings ->
    [x] Enable ActiveX and Socket Clients
    Socket port = 7497 (paper)
    [x] Read-Only API   (recommended; matches readonly=True)
    Trusted IPs include 127.0.0.1

Quick check (with TWS running and the API enabled):
    python -m adapters.ibkr_feed
"""
from __future__ import annotations

import logging
from decimal import Decimal
from math import ceil, isnan
from typing import Optional

import pandas as pd

log = logging.getLogger("nova.feed.ibkr")

# Market-data types (ib.reqMarketDataType): 1=live, 2=frozen, 3=delayed, 4=delayed-frozen.
LIVE, FROZEN, DELAYED, DELAYED_FROZEN = 1, 2, 3, 4


def _is_fx(symbol: str) -> bool:
    """Universe FX tickers use the Yahoo '=X' suffix, e.g. 'EURUSD=X'."""
    return symbol.upper().endswith("=X")


def _duration_str(lookback_days: int) -> str:
    """IBKR durationStr — daily bars over ~a year+ are requested in years."""
    if lookback_days >= 365:
        return f"{ceil(lookback_days / 365)} Y"
    return f"{max(1, lookback_days)} D"


class IBKRDataFeed:
    """Persistent, read-only IBKR data feed with graceful degradation.

    Every public getter returns None / an empty frame on any failure so callers
    can fall back to yfinance without try/except at the call site.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7497,
                 client_id: int = 17, *, readonly: bool = True,
                 timeout: float = 10.0, market_data_type: int = LIVE):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.readonly = readonly
        self.timeout = timeout
        self.market_data_type = market_data_type
        self._ib = None  # lazily created ib_async.IB

    # ----- connection ----------------------------------------------------- #
    def connect(self) -> bool:
        """Open the (read-only) connection. Idempotent; safe to call repeatedly."""
        try:
            from ib_async import IB
        except ImportError:
            log.warning("ib_async not installed — IBKR feed unavailable, using fallback.")
            return False

        if self._ib is not None and self._ib.isConnected():
            return True

        ib = IB()
        try:
            ib.connect(self.host, self.port, clientId=self.client_id,
                       readonly=self.readonly, timeout=self.timeout)
        except Exception as e:
            log.warning("IBKR connect failed (%s:%s): %s — using fallback.",
                        self.host, self.port, e)
            return False

        ib.reqMarketDataType(self.market_data_type)
        self._ib = ib
        log.info("IBKR feed connected %s:%s clientId=%s readonly=%s mktDataType=%s",
                 self.host, self.port, self.client_id, self.readonly, self.market_data_type)
        return True

    def is_connected(self) -> bool:
        return self._ib is not None and self._ib.isConnected()

    def _ensure_connected(self) -> bool:
        return self.is_connected() or self.connect()

    def disconnect(self) -> None:
        if self._ib is not None and self._ib.isConnected():
            self._ib.disconnect()
            log.info("IBKR feed disconnected.")

    # ----- contracts ------------------------------------------------------ #
    def _contract(self, symbol: str):
        """Build a best-effort IBKR contract, or None to defer to yfinance.

        Returns None for symbols this simple resolver can't map to a US
        SMART/USD contract — international/suffixed tickers (e.g. 'VWRL.L') and
        index proxies (e.g. 'DX-Y.NYB'). Proper exchange/currency mapping is a
        later enhancement; until then those flow through the yfinance fallback
        without noisy contract-resolution errors.
        """
        from ib_async import Stock, Forex
        if _is_fx(symbol):
            pair = symbol.upper().replace("=X", "")   # 'EURUSD=X' -> 'EURUSD'
            return Forex(pair)
        if "." in symbol or "-" in symbol:            # non-US / index proxy -> fallback
            return None
        return Stock(symbol.upper(), "SMART", "USD")

    # ----- market data ---------------------------------------------------- #
    def get_price(self, symbol: str) -> Optional[Decimal]:
        """Latest price (snapshot). None on any failure."""
        if not self._ensure_connected():
            return None
        try:
            contract = self._contract(symbol)
            if contract is None:
                return None
            qualified = self._ib.qualifyContracts(contract)
            if not qualified:
                return None
            ticker = self._ib.reqTickers(contract)[0]
            for px in (ticker.marketPrice(), ticker.last, ticker.close):
                if px is not None and not (isinstance(px, float) and isnan(px)) and px > 0:
                    return Decimal(str(px))
            return None
        except Exception as e:
            log.debug("get_price(%s) failed: %s", symbol, e)
            return None

    def get_daily_bars(self, symbol: str, lookback_days: int = 365) -> pd.DataFrame:
        """Daily OHLCV history as a yfinance-compatible frame (capitalised
        columns, DatetimeIndex). Empty frame on any failure."""
        if not self._ensure_connected():
            return pd.DataFrame()
        try:
            from ib_async import util
            contract = self._contract(symbol)
            if contract is None or not self._ib.qualifyContracts(contract):
                return pd.DataFrame()
            what = "MIDPOINT" if _is_fx(symbol) else "TRADES"
            bars = self._ib.reqHistoricalData(
                contract, endDateTime="", durationStr=_duration_str(lookback_days),
                barSizeSetting="1 day", whatToShow=what, useRTH=True, formatDate=1)
            if not bars:
                return pd.DataFrame()
            df = util.df(bars)
            if df is None or df.empty:
                return pd.DataFrame()
            df = df.rename(columns={"open": "Open", "high": "High", "low": "Low",
                                    "close": "Close", "volume": "Volume"})
            df["Date"] = pd.to_datetime(df["date"])
            df = df.set_index("Date")
            return df[["Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            log.debug("get_daily_bars(%s) failed: %s", symbol, e)
            return pd.DataFrame()


# =========================================================================== #
# Quick connectivity check
# =========================================================================== #
def _demo() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    feed = IBKRDataFeed()  # TWS paper @ 127.0.0.1:7497, read-only
    if not feed.connect():
        print("Could not connect — is TWS running with the API enabled on 7497?")
        return
    try:
        for sym in ("SPY", "EURUSD=X"):
            px = feed.get_price(sym)
            bars = feed.get_daily_bars(sym, lookback_days=30)
            print(f"{sym}: price={px} | bars={len(bars)} rows"
                  f"{' (' + str(bars.index[-1].date()) + ' last)' if not bars.empty else ''}")
    finally:
        feed.disconnect()


if __name__ == "__main__":
    _demo()
