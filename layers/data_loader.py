import os
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
        
        # Clean up NaNs from lookback periods
        df = df.dropna()
        return df
    except Exception:
        return pd.DataFrame()
