import pytest
from layers.data_loader import get_technical_features
from layers.ml_scanner import MLScanner

def test_get_technical_features():
    # Use a large enough lookback for the 200 EMA
    df = get_technical_features("AAPL", lookback_days=400)
    # Should not be empty
    assert not df.empty
    
    # Check that pandas-ta columns exist
    assert 'RSI_14' in df.columns
    assert 'MACD_12_26_9' in df.columns
    assert 'EMA_200' in df.columns

def test_ml_scanner():
    scanner = MLScanner(asset_class="EQUITY", prediction_horizon=5)
    universe = ["AAPL"]  # Train on a single reliable ticker for speed
    
    candidates = scanner.scan(universe)
    assert len(candidates) > 0
    
    cand = candidates[0]
    assert cand.symbol == "AAPL"
    assert "ml_prob" in cand.meta
    assert 0.0 <= cand.quant_score <= 100.0
