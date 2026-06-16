import pandas as pd
import pytest

import layers.data_loader as dl
from adapters.ibkr_feed import IBKRDataFeed, _is_fx, _duration_str


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #
def test_is_fx():
    assert _is_fx("EURUSD=X") is True
    assert _is_fx("usdjpy=x") is True
    assert _is_fx("SPY") is False

def test_duration_str():
    assert _duration_str(30) == "30 D"
    assert _duration_str(365) == "1 Y"
    assert _duration_str(400) == "2 Y"
    assert _duration_str(730) == "2 Y"

def test_feed_unconnected_is_safe():
    """A fresh feed (no TWS) reports not-connected and never raises."""
    feed = IBKRDataFeed(port=9999)   # nothing listening
    assert feed.is_connected() is False
    assert feed.get_price("SPY") is None
    assert feed.get_daily_bars("SPY").empty


def test_contract_routing():
    """US equities -> IBKR Stock; FX -> Forex; index/non-US -> None (yfinance)."""
    feed = IBKRDataFeed(port=9999)
    assert feed._contract("SPY") is not None                 # US equity
    assert feed._contract("EURUSD=X") is not None            # FX
    # Yahoo index symbols and non-US/suffixed tickers defer to yfinance (no noisy
    # IBKR contract errors in the macro gate's hot path).
    for sym in ("^VIX", "^VIX3M", "^TNX", "^IRX", "DX-Y.NYB", "VWRL.L"):
        assert feed._contract(sym) is None, sym


# --------------------------------------------------------------------------- #
# data_loader integration: feed is primary, yfinance is the fallback
# --------------------------------------------------------------------------- #
class _FakeFeed:
    def __init__(self, connected, df=None, raises=False):
        self._connected, self._df, self._raises = connected, df, raises
    def is_connected(self):
        if self._raises:
            raise RuntimeError("boom")
        return self._connected
    def get_daily_bars(self, symbol, lookback_days=365):
        return self._df

def _sample_df(tag):
    idx = pd.to_datetime(["2026-01-01", "2026-01-02"])
    return pd.DataFrame({"Open": [1, 2], "High": [1, 2], "Low": [1, 2],
                         "Close": [tag, tag], "Volume": [10, 20]}, index=idx)

@pytest.fixture(autouse=True)
def _reset_feed():
    dl.set_price_feed(None)
    yield
    dl.set_price_feed(None)

def test_connected_feed_is_primary(monkeypatch):
    monkeypatch.setattr(dl.yf, "Ticker", lambda *a, **k: pytest.fail("yfinance must not be hit"))
    dl.set_price_feed(_FakeFeed(connected=True, df=_sample_df(111)))
    out = dl.get_daily_data("SPY")
    assert out["Close"].iloc[0] == 111      # came from the feed

def test_disconnected_feed_falls_back_to_yfinance(monkeypatch, tmp_path):
    monkeypatch.setattr(dl, "CACHE_DIR", str(tmp_path))
    fake = type("T", (), {"history": lambda self, period: _sample_df(999)})
    monkeypatch.setattr(dl.yf, "Ticker", lambda *a, **k: fake())
    dl.set_price_feed(_FakeFeed(connected=False))
    out = dl.get_daily_data("SPY", use_cache=False)
    assert out["Close"].iloc[0] == 999      # yfinance fallback used

def test_feed_error_falls_back(monkeypatch, tmp_path):
    monkeypatch.setattr(dl, "CACHE_DIR", str(tmp_path))
    fake = type("T", (), {"history": lambda self, period: _sample_df(777)})
    monkeypatch.setattr(dl.yf, "Ticker", lambda *a, **k: fake())
    dl.set_price_feed(_FakeFeed(connected=True, raises=True))   # is_connected() raises
    out = dl.get_daily_data("SPY", use_cache=False)
    assert out["Close"].iloc[0] == 777      # error swallowed, fell back

def test_empty_feed_result_falls_back(monkeypatch, tmp_path):
    monkeypatch.setattr(dl, "CACHE_DIR", str(tmp_path))
    fake = type("T", (), {"history": lambda self, period: _sample_df(555)})
    monkeypatch.setattr(dl.yf, "Ticker", lambda *a, **k: fake())
    dl.set_price_feed(_FakeFeed(connected=True, df=pd.DataFrame()))  # empty -> fall back
    out = dl.get_daily_data("SPY", use_cache=False)
    assert out["Close"].iloc[0] == 555
