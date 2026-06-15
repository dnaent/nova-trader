from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

import adapters.asset_equity as ae
import adapters.asset_fx as afx
from core.context import AccountContext, Candidate, NullTaxPolicy, Order
from core.engine import Engine, EngineConfig
from core.ledger import Ledger
from core.risk import NavPctSizing
from adapters.broker_ibkr import IBKRAdapter
from layers.analyst import StubAuditor
from layers.data_loader import format_markers
from layers.ml_scanner import MLScanner


def _mock_ohlcv(days=400):
    np.random.seed(7)
    idx = pd.date_range("2021-01-01", periods=days, freq="B")
    close = np.cumprod(1 + np.random.normal(0.0005, 0.02, days)) * 100
    high = close * 1.01
    low = close * 0.99
    return pd.DataFrame({"Open": (high + low) / 2, "High": high, "Low": low,
                         "Close": close, "Volume": np.random.randint(1e5, 1e6, days),
                         "Dividends": 0.0, "Stock Splits": 0.0}, index=idx)


# --------------------------------------------------------------------------- #
# (A) Markers attach to the Candidate
# --------------------------------------------------------------------------- #
@patch("layers.data_loader.get_daily_data")
def test_scanner_attaches_marker_snapshot(mock_daily):
    mock_daily.return_value = _mock_ohlcv()
    cand = MLScanner(asset_class="EQUITY").scan(["AAPL"])[0]
    markers = cand.meta.get("markers")
    assert isinstance(markers, dict) and markers
    assert "RSI_14" in markers and "MACD_12_26_9" in markers
    assert all(isinstance(v, float) for v in markers.values())


# --------------------------------------------------------------------------- #
# (B) Markers reach the Inference Context Bundle
# --------------------------------------------------------------------------- #
def test_format_markers():
    out = format_markers({"RSI_14": 55.123456, "MACD_12_26_9": 1.2})
    assert "### Technical Markers" in out
    assert "RSI_14: 55.1235" in out
    assert out.index("MACD_12_26_9") < out.index("RSI_14")   # sorted
    assert format_markers({}) == "No technical markers available."

def test_equity_prompt_includes_markers(monkeypatch):
    monkeypatch.setattr(ae, "get_financials", lambda s: "FIN")
    monkeypatch.setattr(ae, "get_recent_news", lambda s: "NEWS")
    c = Candidate("AAPL", "EQUITY", 90.0, Decimal("100"),
                  meta={"markers": {"RSI_14": 55.0}})
    prompt = ae.EquityAdapter().auditor_prompt(c)
    assert "Technical Markers" in prompt and "RSI_14" in prompt

def test_fx_prompt_includes_markers(monkeypatch):
    monkeypatch.setattr(afx, "get_recent_news", lambda s: "NEWS")
    c = Candidate("EURUSD=X", "FX", 80.0, Decimal("1.1"),
                  meta={"markers": {"ATRr_14": 0.0021}})
    prompt = afx.FxAdapter().auditor_prompt(c)
    assert "Technical Markers" in prompt and "ATRr_14" in prompt


# --------------------------------------------------------------------------- #
# (C) Training records: write, outcome backfill, read, export
# --------------------------------------------------------------------------- #
def test_record_and_read_training_sample():
    led = Ledger(":memory:")
    led.record_training_sample(
        book_id="b1", symbol="AAPL", wrapper="ISA", asset_class="EQUITY",
        macro={"regime": "risk-on"}, markers={"RSI_14": 55.0}, gate=80.0,
        quant_score=90.0, claude_score=80.0, blended=86.0, acted=False,
        reason="below exec threshold")
    rows = led.training_samples("b1")
    assert len(rows) == 1
    r = rows[0]
    assert r["markers"] == {"RSI_14": 55.0}        # JSON parsed back
    assert r["macro"] == {"regime": "risk-on"}
    assert r["acted"] == 0 and r["blended"] == 86.0
    led.close()

def test_close_trade_backfills_outcome():
    led = Ledger(":memory:")
    order = Order(book_id="b1", account_id="U1", symbol="AAPL", side="BUY",
                  quantity=Decimal("10"), price=Decimal("100"),
                  notional=Decimal("1000"), stop_loss=Decimal("95"))
    tid = led.record_trade("b1", "U1", "AAPL", "BUY", Decimal("10"),
                           Decimal("100"), Decimal("1000"), stop_loss=Decimal("95"))
    led.record_training_sample(book_id="b1", symbol="AAPL", acted=True,
                               reason="executed", order=order, trade_id=tid,
                               markers={"RSI_14": 55.0})
    # PnL +250 against initial risk of (100-95)*10 = 50 -> R-multiple = 5.0
    led.close_trade(tid, Decimal("125"), Decimal("250"))
    r = led.training_samples("b1")[0]
    assert r["realized_pnl"] == 250.0
    assert r["r_multiple"] == pytest.approx(5.0)
    led.close()

def test_export_training_jsonl(tmp_path):
    led = Ledger(":memory:")
    for i in range(3):
        led.record_training_sample(book_id="b1", symbol=f"S{i}", acted=False,
                                   reason="x", markers={"RSI_14": float(i)})
    path = tmp_path / "train.jsonl"
    n = led.export_training_jsonl(str(path))
    assert n == 3
    assert len(path.read_text().strip().splitlines()) == 3
    led.close()


# --------------------------------------------------------------------------- #
# (D) End-to-end: a full engine cycle writes a complete training record
# --------------------------------------------------------------------------- #
class _FakeAdapter:
    asset_class = "EQUITY"
    handles = {"EQUITY", "ETF"}
    def __init__(self):
        self._last_gate_result = {"regime": "risk-on", "gate_score": 80.0}
    def macro_gate(self):
        return 80.0
    def scan(self, universe):
        return [Candidate("AAPL", "EQUITY", 90.0, Decimal("100"),
                          meta={"ml_prob": "90%",
                                "markers": {"RSI_14": 55.0, "MACD_12_26_9": 1.2}})]
    def auditor_prompt(self, c):
        return f"audit {c.symbol}"

def test_engine_cycle_logs_training_record():
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U1": 10000})
    broker.connect()
    book = AccountContext("b1", "ISA", "IBKR", "U1", {"EQUITY", "ETF"},
                          NullTaxPolicy(), NavPctSizing(max_per_position_pct=8))
    led = Ledger(":memory:")
    cfg = EngineConfig(universe=["AAPL"], exec_threshold=75, gate_min=40)
    Engine([book], [_FakeAdapter()], broker, StubAuditor(), led, cfg).run_cycle()

    samples = led.training_samples("b1")
    assert len(samples) == 1
    s = samples[0]
    assert s["acted"] == 1                          # blended 0.6*90+0.4*80 = 86 >= 75
    assert s["markers"]["RSI_14"] == 55.0           # 32-marker snapshot captured
    assert s["macro"]["regime"] == "risk-on"        # macro regime captured
    assert s["trade_id"] is not None                # linked for outcome join
    assert s["side"] == "BUY" and s["notional"] > 0 # sizing captured
    led.close()
