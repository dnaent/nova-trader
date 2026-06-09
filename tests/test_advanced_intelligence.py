import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from layers.data_loader import get_technical_features
from layers.ml_scanner import MLScanner

def create_mock_ohlcv(days=500):
    np.random.seed(42)
    dates = pd.date_range(start="2020-01-01", periods=days, freq="B")
    close = np.cumprod(1 + np.random.normal(0.0005, 0.02, days)) * 100
    high = close * (1 + np.abs(np.random.normal(0.005, 0.01, days)))
    low = close * (1 - np.abs(np.random.normal(0.005, 0.01, days)))
    open_price = (high + low) / 2
    volume = np.random.randint(100000, 1000000, days)
    
    df = pd.DataFrame({
        'Open': open_price,
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume,
        'Dividends': 0.0,
        'Stock Splits': 0.0
    }, index=dates)
    return df

@patch('layers.data_loader.get_daily_data')
def test_get_technical_features(mock_get_daily):
    mock_get_daily.return_value = create_mock_ohlcv(500)
    
    df = get_technical_features("AAPL", lookback_days=500)
    assert not df.empty
    
    # Check that pandas-ta columns exist
    assert 'RSI_14' in df.columns
    assert 'MACD_12_26_9' in df.columns
    assert 'EMA_200' in df.columns

@patch('layers.data_loader.get_daily_data')
def test_ml_scanner(mock_get_daily):
    mock_get_daily.return_value = create_mock_ohlcv(500)
    
    scanner = MLScanner(asset_class="EQUITY", prediction_horizon=5)
    universe = ["AAPL"]
    
    candidates = scanner.scan(universe)
    assert len(candidates) > 0
    
    cand = candidates[0]
    assert cand.symbol == "AAPL"
    assert "ml_prob" in cand.meta
    assert 0.0 <= cand.quant_score <= 100.0
