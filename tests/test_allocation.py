from decimal import Decimal

from core.context import AccountContext, NullTaxPolicy, Candidate, load_books
from core.engine import Engine, EngineConfig
from core.ledger import Ledger
from core.risk import NavPctSizing
from adapters.broker_ibkr import IBKRAdapter
from adapters.asset_allocation import AllocationAdapter
from layers.analyst import StubAuditor


# --------------------------------------------------------------------------- #
# AllocationAdapter basics
# --------------------------------------------------------------------------- #
def test_allocation_adapter_basics():
    a = AllocationAdapter()
    assert a.strategy == "allocation"
    assert a.handles == {"EQUITY", "ETF"}
    assert a.basket                                  # non-empty default core

def test_allocation_scan_uses_point_in_time_price(monkeypatch):
    monkeypatch.setattr("adapters.asset_allocation.get_latest_price", lambda s: Decimal("132.5"))
    cands = AllocationAdapter(basket=["VWRL.L"]).scan(["ignored", "universe"])
    assert len(cands) == 1
    assert cands[0].symbol == "VWRL.L"
    assert cands[0].price == Decimal("132.5")
    assert cands[0].quant_score == 100.0            # high-conviction hold

def test_allocation_scan_skips_missing_price(monkeypatch):
    monkeypatch.setattr("adapters.asset_allocation.get_latest_price", lambda s: None)
    assert AllocationAdapter().scan([]) == []


# --------------------------------------------------------------------------- #
# portfolio.yaml wiring
# --------------------------------------------------------------------------- #
def test_sipp_book_uses_allocation():
    books = {b.book_id: b for b in load_books("portfolio.yaml")}
    sipp = books["ibkr_sipp_equity"]
    assert sipp.strategy == "allocation"
    assert sipp.gate_min == 75
    assert sipp.aggressive_liquidation is True
    # tactical books stay tactical with the global gate (unchanged behaviour)
    assert books["ibkr_isa_equity"].strategy == "tactical"
    assert books["ibkr_isa_equity"].gate_min is None


# --------------------------------------------------------------------------- #
# Per-book strategy routing & gate_min
# --------------------------------------------------------------------------- #
class _Fake:
    def __init__(self, strategy, symbol, gate=80.0):
        self.strategy = strategy
        self.handles = {"EQUITY", "ETF"}
        self._symbol = symbol
        self._gate = gate
        self._last_gate_result = {"regime": "test"}
    def macro_gate(self):
        return self._gate
    def scan(self, universe):
        return [Candidate(self._symbol, "EQUITY", 90.0, Decimal("10"), meta={"markers": {}})]
    def auditor_prompt(self, c):
        return "x"

def _book(book_id, **kw):
    return AccountContext(book_id, "ISA", "IBKR", "U_" + book_id, {"EQUITY", "ETF"},
                          NullTaxPolicy(), NavPctSizing(), **kw)

def _symbols(led, book_id):
    return {r["symbol"] for r in
            led.conn.execute("SELECT symbol FROM training_records WHERE book_id=?", (book_id,))}

def test_engine_routes_each_book_to_its_strategy():
    broker = IBKRAdapter(mode="paper", connector="stub",
                         simulated_navs={"U_t": 1000, "U_a": 1000})
    broker.connect()
    tact = _book("t", strategy="tactical")
    alloc = _book("a", strategy="allocation")
    led = Ledger(":memory:")
    cfg = EngineConfig(universe=["X"], gate_min=40, exec_threshold=50)
    Engine([tact, alloc], [_Fake("tactical", "TACT"), _Fake("allocation", "ALLOC")],
           broker, StubAuditor(), led, cfg).run_cycle()
    assert _symbols(led, "t") == {"TACT"}            # tactical book ran only the tactical adapter
    assert _symbols(led, "a") == {"ALLOC"}           # allocation book ran only the allocation adapter
    led.close()

def test_per_book_gate_min_overrides_global():
    broker = IBKRAdapter(mode="paper", connector="stub",
                         simulated_navs={"U_hi": 1000, "U_lo": 1000})
    broker.connect()
    hi = _book("hi", gate_min=90)                    # needs gate >= 90
    lo = _book("lo")                                 # uses global gate_min (40)
    led = Ledger(":memory:")
    cfg = EngineConfig(universe=["X"], gate_min=40, exec_threshold=50)
    Engine([hi, lo], [_Fake("tactical", "S", gate=80.0)], broker, StubAuditor(), led, cfg).run_cycle()
    assert _symbols(led, "hi") == set()              # gate 80 < 90 -> held cash
    assert _symbols(led, "lo") == {"S"}              # gate 80 >= 40 -> traded
    led.close()
