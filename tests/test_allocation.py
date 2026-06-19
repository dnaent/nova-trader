from decimal import Decimal

from core.context import AccountContext, NullTaxPolicy, Candidate, Order, load_books
from core.engine import Engine, EngineConfig
from core.ledger import Ledger
from core.risk import NavPctSizing
from adapters.broker_ibkr import IBKRAdapter
from adapters.asset_allocation import AllocationAdapter
from layers.analyst import StubAuditor
from backtest.validation import validate_from_ledger, periodic_returns


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
    # scan holds the PER-BOOK basket the engine passes (ctx.universe), enabling distinct
    # allocation books (growth ISA vs diversified SIPP) through one shared adapter.
    cands = AllocationAdapter(basket=["FALLBACK"]).scan(["VWRL.L", "IGLG.L"])
    assert {c.symbol for c in cands} == {"VWRL.L", "IGLG.L"}
    assert cands[0].price == Decimal("132.5")
    assert cands[0].quant_score == 100.0            # high-conviction hold
    # falls back to the construction basket when the book declares no universe
    fb = AllocationAdapter(basket=["VWRL.L"]).scan([])
    assert [c.symbol for c in fb] == ["VWRL.L"]

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
    assert len(sipp.universe) == 12                   # per-book diversified basket
    # ISA is now a GROWTH ALLOCATION book (option d, 2026-06-19); GIA stays tactical.
    assert books["ibkr_isa_equity"].strategy == "allocation"
    assert books["ibkr_isa_equity"].gate_min == 75
    assert len(books["ibkr_isa_equity"].universe) == 8   # per-book growth basket
    assert books["ibkr_gia_equity"].strategy == "tactical"
    assert books["ibkr_gia_equity"].gate_min == 80


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

class _UnivEcho:
    """Tactical adapter that proposes one Candidate per symbol it is handed, so the
    test can see exactly which universe the engine scanned for each book."""
    strategy = "tactical"
    handles = {"EQUITY", "ETF"}
    def __init__(self):
        self._last_gate_result = {}
    def macro_gate(self):
        return 80.0
    def scan(self, universe):
        return [Candidate(s, "EQUITY", 90.0, Decimal("10"), meta={"markers": {}}) for s in universe]
    def auditor_prompt(self, c):
        return "x"

def test_per_book_universe_overrides_config():
    """A book's own `universe` (e.g. ISA=UK, GIA=US) is scanned instead of the shared
    config universe; a book without one falls back to config."""
    broker = IBKRAdapter(mode="paper", connector="stub",
                         simulated_navs={"U_uk": 1000, "U_def": 1000})
    broker.connect()
    uk = _book("uk", strategy="tactical", universe=["RIO.L", "GLEN.L"])
    default = _book("def", strategy="tactical")            # no per-book universe
    led = Ledger(":memory:")
    cfg = EngineConfig(universe={"EQUITY": ["SPY"]}, gate_min=40, exec_threshold=50)
    Engine([uk, default], [_UnivEcho()], broker, StubAuditor(), led, cfg).run_cycle()
    assert _symbols(led, "uk") == {"RIO.L", "GLEN.L"}      # scanned its own UK watchlist
    assert _symbols(led, "def") == {"SPY"}                 # fell back to the config universe
    led.close()

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

# --------------------------------------------------------------------------- #
# Curve-based validation for low-turnover (allocation) books
# --------------------------------------------------------------------------- #
def test_periodic_returns_from_curve():
    pr = periodic_returns(list(range(100, 143)), period=21)   # rising 43-pt curve
    assert len(pr) == 2 and all(r > 0 for r in pr)
    assert periodic_returns([1, 2, 3], period=21) == []       # too short

def test_allocation_book_validated_on_equity_curve():
    led = Ledger(":memory:")
    # A steadily rising mark-to-market curve (mostly positive months, tiny DD).
    for i in range(700):
        led.record_nav("ibkr_sipp_equity", Decimal(str(10000 + i * 5)))
    ctx = _book("ibkr_sipp_equity", strategy="allocation", gate_min=75)
    res = validate_from_ledger(ctx, led, run_robustness=False)
    # Routed to the curve path: win rate = % positive months (high on a rising curve),
    # and the sample criterion is track-record length, not 150 trades.
    assert res.metrics["win_rate"] is not None and res.metrics["win_rate"] > 0.9
    sample = next(c for c in res.criteria if c.name == "sample_size")
    assert sample.passed is True                              # ~33 months >= 30
    led.close()


def test_derisk_hysteresis_holds_through_dip(monkeypatch):
    """With a de-risk floor below gate_min, a gate in the hold band must NOT
    liquidate existing positions (anti-whipsaw)."""
    import layers.data_loader as dl
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U_h": 1000})
    broker.connect()
    # entry floor 75, exit floor 65; gate dips to 70 (in the hold band)
    book = _book("h", strategy="allocation", gate_min=75, aggressive_liquidation=True,
                 derisk_gate=65)
    led = Ledger(":memory:")
    led.record_trade("h", "U_h", "VWRL.L", "BUY", Decimal("1"), Decimal("100"), Decimal("100"))
    broker.place(Order("h", "U_h", "VWRL.L", "BUY", Decimal("1"), Decimal("100"),
                       Decimal("100")), book)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("99"))
    cfg = EngineConfig(universe=["X"], gate_min=40, exec_threshold=50)
    Engine([book], [_Fake("allocation", "VWRL.L", gate=70.0)], broker,
           StubAuditor(), led, cfg).run_cycle()
    assert len(led.open_trades("h")) == 1               # gate 70 in [65,75): held, not liquidated

def test_derisk_hysteresis_liquidates_below_floor(monkeypatch):
    """Below the de-risk floor, positions ARE liquidated."""
    import layers.data_loader as dl
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U_h": 1000})
    broker.connect()
    book = _book("h", strategy="allocation", gate_min=75, aggressive_liquidation=True,
                 derisk_gate=65)
    led = Ledger(":memory:")
    led.record_trade("h", "U_h", "VWRL.L", "BUY", Decimal("1"), Decimal("100"), Decimal("100"))
    broker.place(Order("h", "U_h", "VWRL.L", "BUY", Decimal("1"), Decimal("100"),
                       Decimal("100")), book)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("99"))
    cfg = EngineConfig(universe=["X"], gate_min=40, exec_threshold=50)
    Engine([book], [_Fake("allocation", "VWRL.L", gate=60.0)], broker,
           StubAuditor(), led, cfg).run_cycle()
    assert led.open_trades("h") == []                   # gate 60 < 65: de-risked to cash


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
