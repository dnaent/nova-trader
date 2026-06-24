import os
from decimal import Decimal
import pandas as pd
try:
    import pandas_ta as ta  # original library (legacy/dev machines)
except ImportError:
    import pandas_ta_classic as ta  # maintained fork; registers the same `.ta` accessor
import yfinance as yf
from datetime import datetime, timedelta

CACHE_DIR = ".cache"

# Optional real-time price source (adapters.ibkr_feed.IBKRDataFeed). When set
# and connected, it is the PRIMARY source for daily bars; yfinance stays as the
# automatic fallback. Injected via set_price_feed() so this module never imports
# ib_async directly and the engine stays broker-agnostic.
_PRICE_FEED = None


def set_price_feed(feed) -> None:
    """Register (or clear, with None) the real-time price feed used by the hot path."""
    global _PRICE_FEED
    _PRICE_FEED = feed


def get_price_feed():
    """Return the currently registered price feed, if any."""
    return _PRICE_FEED


def get_latest_price(symbol: str):
    """Latest price as Decimal: real-time feed snapshot first, else last daily
    close (which itself uses the feed/yfinance). None if unavailable.

    Used by the engine's exit evaluation to mark open positions to market.
    """
    feed = _PRICE_FEED
    if feed is not None:
        try:
            if feed.is_connected():
                px = feed.get_price(symbol)
                if px is not None:
                    return px
        except Exception:
            pass
    df = get_daily_data(symbol)
    if df is not None and not df.empty and "Close" in df.columns:
        return Decimal(str(df["Close"].iloc[-1]))
    return None


def get_daily_data(symbol: str, lookback_days: int = 365, use_cache: bool = True) -> pd.DataFrame:
    # Primary: the real-time IBKR feed if one is registered and connected.
    # Any failure (unresolved contract, disconnect, empty frame) falls through
    # to the yfinance + cache path below — yfinance is always the safety net.
    feed = _PRICE_FEED
    if feed is not None:
        try:
            if feed.is_connected():
                df = feed.get_daily_bars(symbol, lookback_days)
                if df is not None and not df.empty:
                    return df
        except Exception:
            pass

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{symbol}_daily.csv")
    
    if use_cache and os.path.exists(cache_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - mtime < timedelta(hours=12):
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                if len(df) > 0:
                    return df
            except Exception:
                pass
                
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{lookback_days}d")
    if not df.empty:
        df.to_csv(cache_path)
    return df

def _fx_session_code(hour_utc) -> float:
    """Map a UTC hour to an FX session bucket (numeric, for the marker matrix):
    1=Asia, 2=London, 3=London/NY overlap (peak liquidity), 4=NY, 5=off-hours."""
    h = int(hour_utc) % 24
    if 0 <= h < 7:   return 1.0    # Asia
    if 7 <= h < 12:  return 2.0    # London
    if 12 <= h < 16: return 3.0    # London/NY overlap (peak)
    if 16 <= h < 21: return 4.0    # NY
    return 5.0                     # 21-24 off-hours


def get_intraday_data(symbol: str, interval: str = "1h", lookback_days: int = 5) -> pd.DataFrame:
    """Intraday OHLCV bars for the temporal-feature layer (Phase 1, FX observe-only).

    Routing (replay-safe): a registered feed WITH `get_intraday_bars` (the live
    IBKRDataFeed) is primary; a feed WITHOUT it (the replay ReplayFeed) returns an
    EMPTY frame by design — there is no point-in-time intraday history in replay, so
    we skip it (no lookahead; the daily corpus is unaffected). With no feed (dev) we
    use the yfinance intraday fallback. Empty frame on any failure.
    """
    feed = _PRICE_FEED
    if feed is not None and getattr(feed, "get_intraday_bars", None) is None:
        return pd.DataFrame()                      # ReplayFeed etc.: no intraday in replay
    if feed is not None:
        try:
            if feed.is_connected():
                df = feed.get_intraday_bars(symbol, lookback_days=lookback_days)
                if df is not None and not df.empty:
                    return df
        except Exception:
            pass
    try:
        # yfinance limits intraday historical data based on interval.
        # for '5m', max is 60 days.
        days = min(lookback_days, 60) if interval in ["1m", "2m", "5m", "15m", "30m", "90m"] else lookback_days
        df = yf.Ticker(symbol).history(period=f"{days}d", interval=interval)
        return df if (df is not None and not df.empty) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def temporal_fx_features(symbol: str) -> dict:
    """Phase-1 OBSERVE-ONLY temporal features for FX, from recent intraday bars.

    Merged into the FX marker snapshot (training records + Inference Context Bundle)
    WITHOUT affecting the daily signal/sizing/exits. Returns {} when intraday data is
    unavailable (e.g. historical replay) so the daily corpus is unchanged — derived
    from the latest bar's timestamp (point-in-time), never wall-clock now().

    HONEST NOTE: with DAILY execution the entry hour/session is ~constant (cron time),
    so the *varying* useful observe signals are day-of-week (the 'specific days' half of
    the idea) + intraday volatility/return context. The intraday ENTRY-timing edge ('a
    certain time window') needs Phase 3 (intraday cadence). This phase just makes the
    model SEE time, and lets the corpus reveal whether the edge is there.
    """
    df = get_intraday_data(symbol, interval="1h", lookback_days=5)
    if df is None or df.empty or "Close" not in df.columns or len(df) < 2:
        return {}
    try:
        ts = df.index[-1]
        if getattr(ts, "tzinfo", None) is not None:
            ts = ts.tz_convert("UTC")
        out = {
            "fx_dow": float(ts.dayofweek),          # 0=Mon .. 6=Sun (decision day)
            "fx_hour_utc": float(ts.hour),
            "fx_session": _fx_session_code(ts.hour),
        }
        close = df["Close"].astype(float)
        last = float(close.iloc[-1])
        if last:
            hi = float(df["High"].astype(float).tail(24).max())
            lo = float(df["Low"].astype(float).tail(24).min())
            first = float(close.tail(24).iloc[0])
            out["fx_range_24h_pct"] = round((hi - lo) / last * 100.0, 4)
            out["fx_ret_24h_pct"] = round((last / first - 1.0) * 100.0, 4) if first else 0.0
        return out
    except Exception:
        return {}


def format_markers(markers: dict) -> str:
    """Render a marker snapshot for the LLM Inference Context Bundle (Layer 3).

    Markers are the same 32-indicator matrix the ML scanner (Layer 2) sees; this
    wires them into the auditor's context so both layers reason over identical
    inputs. Returns a stable, sorted, human-readable block.
    """
    if not markers:
        return "No technical markers available."
    lines = ["### Technical Markers (current snapshot)"]
    for name in sorted(markers):
        value = markers[name]
        lines.append(f"- {name}: {value:.4f}" if isinstance(value, (int, float))
                     else f"- {name}: {value}")
    return "\n".join(lines)


def get_financials(symbol: str) -> str:
    """Fetch the trailing 4 quarters of financials for the LLM prompt."""
    ticker = yf.Ticker(symbol)
    parts = []
    
    try:
        inc = ticker.quarterly_income_stmt
        if inc is not None and not inc.empty:
            parts.append("### Income Statement (Quarterly)")
            parts.append(inc.iloc[:, :4].to_string())
            
        bs = ticker.quarterly_balance_sheet
        if bs is not None and not bs.empty:
            parts.append("### Balance Sheet (Quarterly)")
            parts.append(bs.iloc[:, :4].to_string())
            
        cf = ticker.quarterly_cashflow
        if cf is not None and not cf.empty:
            parts.append("### Cash Flow (Quarterly)")
            parts.append(cf.iloc[:, :4].to_string())
            
    except Exception as e:
        return f"Financial data unavailable for {symbol}: {str(e)}"
        
    if not parts:
        return f"No financial data found for {symbol}."
        
    return "\n\n".join(parts)

def get_recent_news(symbol: str) -> str:
    """Fetch recent news headlines and publishers."""
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if not news:
            return f"No recent news found for {symbol}."
            
        parts = ["### Recent News Headlines"]
        for item in news[:5]:
            title = item.get("title", "No Title")
            publisher = item.get("publisher", "Unknown")
            parts.append(f"- [{publisher}] {title}")
            
        return "\n".join(parts)
    except Exception as e:
        return f"News data unavailable for {symbol}: {str(e)}"

def get_technical_features(symbol: str, lookback_days: int = 730) -> pd.DataFrame:
    """Fetch base data and append the 30+ indicator matrix using pandas-ta."""
    df = get_daily_data(symbol, lookback_days=lookback_days, use_cache=True)
    if df.empty or len(df) < 50:
        return pd.DataFrame()
        
    try:
        # We use pandas-ta to append multiple indicators
        df.ta.rsi(append=True)
        df.ta.macd(append=True)
        df.ta.stoch(append=True)
        df.ta.bbands(append=True)
        df.ta.atr(append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        df.ta.adx(append=True)
        # Ichimoku can return tuple, use direct append safely
        df.ta.ichimoku(append=True)

        # BUGFIX (2026-06-19): pandas-ta appends the chikou span ICS_* = close.shift(-N)
        # — a FUTURE close. Two problems: (a) LOOKAHEAD if used as a feature, and worse
        # (b) its trailing NaNs make the dropna() below drop the most RECENT N (~26) rows,
        # silently feeding the scanner ~26-day-STALE features (raw ended 2026-06-18 but the
        # feature frame ended 2026-05-12). Drop the chikou BEFORE dropna so features stay
        # current; the other Ichimoku lines (tenkan/kijun/senkou) are past-derived and kept.
        df = df.drop(columns=[c for c in df.columns if c.upper().startswith("ICS")],
                     errors="ignore")

        # Clean up NaNs from lookback periods
        df = df.dropna()
        return df
    except Exception:
        return pd.DataFrame()

def get_intraday_features(symbol: str, interval: str = "5m", lookback_days: int = 5) -> pd.DataFrame:
    """Fetch intraday base data and append the 30+ indicator matrix using pandas-ta."""
    df = get_intraday_data(symbol, interval=interval, lookback_days=lookback_days)
    if df.empty or len(df) < 50:
        return pd.DataFrame()
        
    try:
        # We use pandas-ta to append multiple indicators
        df.ta.rsi(append=True)
        df.ta.macd(append=True)
        df.ta.stoch(append=True)
        df.ta.bbands(append=True)
        df.ta.atr(append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        df.ta.adx(append=True)
        # Ichimoku can return tuple, use direct append safely
        df.ta.ichimoku(append=True)

        # Drop the chikou span which introduces lookahead bias
        df = df.drop(columns=[c for c in df.columns if c.upper().startswith("ICS")],
                     errors="ignore")

        # Clean up NaNs from lookback periods
        df = df.dropna()
        return df
    except Exception:
        return pd.DataFrame()

