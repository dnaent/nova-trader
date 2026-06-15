from decimal import Decimal

import pandas as pd
import pytest

import layers.data_loader as dl
from core.context import AccountContext, NullTaxPolicy, Order
from core.engine import Engine, EngineConfig
from core.ledger import Ledger
from core.risk import NavPctSizing
from adapters.broker_ibkr import IBKRAdapter
from layers.analyst import StubAuditor


# --------------------------------------------------------------------------- #
# Ledger.open_trades
# --------------------------------------------------------------------------- #
def test_open_trades_excludes_closed():
    led = Ledger(":memory:")
    t1 = led.record_trade("b1", "U1", "AAPL", "BUY", Decimal(1), Decimal(100), Decimal(100))
    led.record_trade("b1", "U1", "MSFT", "BUY", Decimal(1), Decimal(200), Decimal(200))
    led.close_trade(t1, Decimal(110), Decimal(10))
    opens = led.open_trades("b1")
    assert len(opens) == 1 and opens[0]["symbol"] == "MSFT"
    led.close()


# --------------------------------------------------------------------------- #
# get_latest_price
# --------------------------------------------------------------------------- #
def test_get_latest_price_uses_feed(monkeypatch):
    class _Feed:
        def is_connected(self): return True
        def get_price(self, s): return Decimal("99")
    monkeypatch.setattr(dl, "_PRICE_FEED", _Feed())
    assert dl.get_latest_price("X") == Decimal("99")

def test_get_latest_price_falls_back_to_close(monkeypatch):
    monkeypatch.setattr(dl, "_PRICE_FEED", None)
    monkeypatch.setattr(dl, "get_daily_data", lambda *a, **k: pd.DataFrame({"Close": [123.0]}))
    assert dl.get_latest_price("X") == Decimal("123.0")


# --------------------------------------------------------------------------- #
# Engine exit evaluation
# --------------------------------------------------------------------------- #
def _engine_with_open_position(entry=100, stop=95, take=110, qty=10):
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U1": 10000})
    broker.connect()
    book = AccountContext("b1", "ISA", "IBKR", "U1", {"EQUITY", "ETF"},
                          NullTaxPolicy(), NavPctSizing())
    ledger = Ledger(":memory:")
    engine = Engine([book], [], broker, StubAuditor(), ledger, EngineConfig())

    order = Order("b1", "U1", "AAPL", "BUY", Decimal(qty), Decimal(entry),
                  Decimal(entry * qty), stop_loss=Decimal(stop), take_profit=Decimal(take))
    broker.place(order, book)                       # paper fill in the stub
    tid = ledger.record_trade("b1", "U1", "AAPL", "BUY", Decimal(qty), Decimal(entry),
                              Decimal(entry * qty), stop_loss=Decimal(stop),
                              take_profit=Decimal(take))
    ledger.record_training_sample(book_id="b1", symbol="AAPL", acted=True,
                                  reason="executed", order=order, trade_id=tid,
                                  markers={"RSI_14": 55.0})
    return engine, book, ledger, tid

def test_exit_on_stop_records_minus_1R(monkeypatch):
    engine, book, ledger, tid = _engine_with_open_position(entry=100, stop=95, take=110)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("94"))   # below stop
    engine._evaluate_exits(book)
    assert ledger.open_trades("b1") == []                  # position closed
    assert engine.broker.positions(book) == []             # broker netted flat
    rec = ledger.training_samples("b1")[0]
    assert rec["realized_pnl"] == -50.0                    # (95-100)*10
    assert rec["r_multiple"] == pytest.approx(-1.0)        # lost exactly 1R
    ledger.close()

def test_exit_on_take_records_positive_R(monkeypatch):
    engine, book, ledger, tid = _engine_with_open_position(entry=100, stop=95, take=110)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("111"))  # above take
    engine._evaluate_exits(book)
    assert ledger.open_trades("b1") == []
    rec = ledger.training_samples("b1")[0]
    assert rec["realized_pnl"] == 100.0                    # (110-100)*10
    assert rec["r_multiple"] == pytest.approx(2.0)         # +2R (10 reward / 5 risk)
    ledger.close()

def test_no_exit_when_price_between(monkeypatch):
    engine, book, ledger, tid = _engine_with_open_position(entry=100, stop=95, take=110)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("103"))  # inside band
    engine._evaluate_exits(book)
    assert len(ledger.open_trades("b1")) == 1              # still open
    assert ledger.training_samples("b1")[0]["realized_pnl"] is None
    ledger.close()

def test_exit_skips_when_price_unavailable(monkeypatch):
    engine, book, ledger, tid = _engine_with_open_position()
    monkeypatch.setattr(dl, "get_latest_price", lambda s: None)
    engine._evaluate_exits(book)
    assert len(ledger.open_trades("b1")) == 1              # left open, no crash
    ledger.close()
