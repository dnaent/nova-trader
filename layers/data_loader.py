import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

CACHE_DIR = ".cache"

def get_daily_data(symbol: str, lookback_days: int = 365, use_cache: bool = True) -> pd.DataFrame:
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
