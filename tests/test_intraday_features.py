"""Phase-1 intraday/temporal FX features (observe-only). Offline: no TWS, no network."""
import pandas as pd

import layers.data_loader as dl
from layers.data_loader import _fx_session_code, get_intraday_data, temporal_fx_features


def _intraday(n=10, start="2024-03-04 00:00", tz="UTC"):
    """Synthetic hourly OHLCV frame, tz-aware index. Default: Mon 2024-03-04 00:00..09:00
    so the LAST bar is Monday 09:00 UTC (dow 0, London session)."""
    idx = pd.date_range(start, periods=n, freq="h", tz=tz)
    close = pd.Series([100.0 + i * 0.1 for i in range(n)], index=idx)
    return pd.DataFrame({"Open": close, "High": close * 1.002, "Low": close * 0.998,
                         "Close": close, "Volume": [1000] * n}, index=idx)


# --------------------------------------------------------------------------- #
# Session mapping
# --------------------------------------------------------------------------- #
def test_fx_session_code_buckets():
    assert _fx_session_code(3) == 1.0     # Asia
    assert _fx_session_code(9) == 2.0     # London
    assert _fx_session_code(14) == 3.0    # London/NY overlap (peak)
    assert _fx_session_code(18) == 4.0    # NY
    assert _fx_session_code(23) == 5.0    # off-hours
    assert _fx_session_code(27) == 1.0    # wraps (27 % 24 = 3 -> Asia)


# --------------------------------------------------------------------------- #
# get_intraday_data routing (replay-safe)
# --------------------------------------------------------------------------- #
class _ReplayLike:
    """A feed WITHOUT get_intraday_bars (like the replay ReplayFeed)."""
    def is_connected(self): return True

class _LiveLike:
    """A feed WITH get_intraday_bars (like the live IBKRDataFeed)."""
    def __init__(self, df): self._df = df
    def is_connected(self): return True
    def get_intraday_bars(self, symbol, lookback_days=5): return self._df


def test_intraday_skipped_under_replay_feed():
    """A feed lacking intraday support (replay) must return EMPTY — no lookahead,
    no yfinance network call during a feed session."""
    dl.set_price_feed(_ReplayLike())
    try:
        assert get_intraday_data("EURUSD=X").empty
    finally:
        dl.set_price_feed(None)


def test_intraday_uses_live_feed():
    df = _intraday()
    dl.set_price_feed(_LiveLike(df))
    try:
        out = get_intraday_data("EURUSD=X")
        assert not out.empty and len(out) == len(df)
    finally:
        dl.set_price_feed(None)


# --------------------------------------------------------------------------- #
# temporal_fx_features
# --------------------------------------------------------------------------- #
def test_temporal_features_from_intraday(monkeypatch):
    monkeypatch.setattr(dl, "get_intraday_data", lambda *a, **k: _intraday())
    f = temporal_fx_features("EURUSD=X")
    assert f["fx_dow"] == 0.0                       # last bar Mon 2024-03-04 09:00
    assert f["fx_hour_utc"] == 9.0
    assert f["fx_session"] == 2.0                   # 09:00 UTC -> London
    assert f["fx_range_24h_pct"] > 0               # intraday vol context present
    assert "fx_ret_24h_pct" in f


def test_temporal_features_empty_when_no_intraday(monkeypatch):
    """During replay (no intraday) the feature set is empty -> daily corpus unchanged."""
    monkeypatch.setattr(dl, "get_intraday_data", lambda *a, **k: pd.DataFrame())
    assert temporal_fx_features("EURUSD=X") == {}
