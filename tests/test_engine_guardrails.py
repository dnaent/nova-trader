"""Engine risk-guardrail paths: drawdown, daily-loss cap, max-concurrent, and
aggressive liquidation. These are safety-critical and were previously untested."""
from decimal import Decimal

from core.context import AccountContext, NullTaxPolicy, RiskGuardrails, Order, Candidate
from core.engine import Engine, EngineConfig
from core.ledger import Ledger
from core.risk import NavPctSizing
from adapters.broker_ibkr import IBKRAdapter
from layers.analyst import StubAuditor


class _ActingAdapter:
    """Would always buy AAPL if the engine reaches the scan stage."""
    asset_class = "EQUITY"
    handles = {"EQUITY", "ETF"}
    def __init__(self, gate=80.0):
        self._g = gate
        self._last_gate_result = {}
    def macro_gate(self):
        return self._g
    def scan(self, universe):
        return [Candidate("AAPL", "EQUITY", 90.0, Decimal("100"), meta={"markers": {}})]
    def auditor_prompt(self, c):
        return "audit AAPL"


def _engine(adapter, *, nav=10000, aggressive=False, guardrails=None):
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs={"U1": nav})
    broker.connect()
    gr = guardrails or RiskGuardrails(max_drawdown_pct=10, daily_loss_cap_pct=3,
                                      max_concurrent_positions=2)
    book = AccountContext("b1", "ISA", "IBKR", "U1", {"EQUITY", "ETF"},
                          NullTaxPolicy(), NavPctSizing(), gr)
    led = Ledger(":memory:")
    cfg = EngineConfig(universe=["AAPL"], gate_min=40, exec_threshold=50,
                       aggressive_liquidation=aggressive)
    return Engine([book], [adapter], broker, StubAuditor(), led, cfg), book, led, broker


def test_drawdown_breach_pauses_buys():
    eng, book, led, broker = _engine(_ActingAdapter())
    led.record_nav("b1", Decimal("10000"))             # establish a peak
    broker.set_simulated_nav("U1", Decimal("8000"))    # 20% down vs 10% cap
    eng.run_cycle()
    assert led.performance_summary("b1")["trades_recorded"] == 0
    led.close()

def test_daily_loss_cap_pauses_buys():
    gr = RiskGuardrails(max_drawdown_pct=50, daily_loss_cap_pct=3, max_concurrent_positions=2)
    eng, book, led, broker = _engine(_ActingAdapter(), guardrails=gr)
    # A prior-day NAV so today's loss can be computed; drawdown cap is loose (50%).
    led.conn.execute("INSERT INTO nav_history (ts,date_str,book_id,nav) "
                     "VALUES ('t','2020-01-01','b1',10000)")
    led.conn.commit()
    broker.set_simulated_nav("U1", Decimal("9000"))    # 10% daily loss vs 3% cap
    eng.run_cycle()
    assert led.performance_summary("b1")["trades_recorded"] == 0
    led.close()

def test_max_concurrent_positions_skips_scan():
    eng, book, led, broker = _engine(_ActingAdapter())  # cap = 2
    for sym in ("MSFT", "GOOG"):
        broker.place(Order("b1", "U1", sym, "BUY", Decimal("1"), Decimal("100"),
                           Decimal("100")), book)
    eng.run_cycle()
    assert led.performance_summary("b1")["trades_recorded"] == 0  # engine never scanned
    led.close()

def test_crash_derisk_liquidates_on_drawdown(monkeypatch):
    """Crash de-risk liquidates to cash on a mark-to-market drawdown breach EVEN
    WHEN the macro gate is still high (above the floor) — the case the lagging HMM
    gate / regime de-risk misses. Stop-loss is avoided (price held above it) so the
    liquidation is provably the crash circuit-breaker, not an exit."""
    import layers.data_loader as dl
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("100"))
    gr = RiskGuardrails(max_drawdown_pct=50, daily_loss_cap_pct=99,
                        max_concurrent_positions=5, crash_derisk_dd_pct=8.0)
    eng, book, led, broker = _engine(_ActingAdapter(gate=80.0), guardrails=gr)  # gate >> floor
    broker.set_simulated_nav("U1", Decimal("10000"))
    eng.run_cycle()                                    # cycle 1: HWM=10000, opens a position
    assert led.open_trades("b1"), "cycle 1 should open a position"

    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("99"))  # above the 95 stop
    broker.set_simulated_nav("U1", Decimal("9000"))    # 10% book drawdown > 8% threshold
    eng.run_cycle()                                    # cycle 2: crash de-risk fires
    assert led.open_trades("b1") == [], "crash de-risk should liquidate despite the high gate"
    assert eng._crash_state["b1"] == "armed"
    led.close()


def test_crash_derisk_regime_confirmed_reentry(monkeypatch):
    """After a crash liquidation the book stays in cash through a still-high gate
    (no churn), confirms only when the gate falls below the de-risk floor, and
    re-enters only once the gate recovers above the entry floor."""
    import layers.data_loader as dl
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("100"))
    gr = RiskGuardrails(max_drawdown_pct=50, daily_loss_cap_pct=99,
                        max_concurrent_positions=5, crash_derisk_dd_pct=8.0)
    adapter = _ActingAdapter(gate=80.0)
    eng, book, led, broker = _engine(adapter, guardrails=gr)      # gate_min=40, derisk_floor=40
    broker.set_simulated_nav("U1", Decimal("10000"))
    eng.run_cycle()                                               # HWM=10000, opens

    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("99"))
    broker.set_simulated_nav("U1", Decimal("9000"))
    eng.run_cycle()                                               # crash trip -> armed, cash
    assert eng._crash_state["b1"] == "armed" and led.open_trades("b1") == []

    # gate stays high -> still blocked (no confirm, no re-entry, no churn)
    n_before = led.performance_summary("b1")["trades_recorded"]
    eng.run_cycle()
    assert eng._crash_state["b1"] == "armed"
    assert led.performance_summary("b1")["trades_recorded"] == n_before

    adapter._g = 30.0                                            # regime turns down (< derisk floor)
    eng.run_cycle()
    assert eng._crash_state["b1"] == "confirmed"
    assert led.open_trades("b1") == []

    adapter._g = 80.0                                            # regime recovers (>= entry floor)
    eng.run_cycle()
    assert eng._crash_state["b1"] is None
    assert led.open_trades("b1"), "should re-enter after a confirmed regime recovery"
    led.close()


def test_aggressive_liquidation_closes_positions(monkeypatch):
    import layers.data_loader as dl
    eng, book, led, broker = _engine(_ActingAdapter(gate=30.0), aggressive=True)  # gate < floor
    tid = led.record_trade("b1", "U1", "MSFT", "BUY", Decimal("1"), Decimal("100"),
                           Decimal("100"))                # open position in the ledger
    broker.place(Order("b1", "U1", "MSFT", "BUY", Decimal("1"), Decimal("100"),
                       Decimal("100")), book)
    monkeypatch.setattr(dl, "get_latest_price", lambda s: Decimal("90"))  # de-risk price
    eng.run_cycle()
    assert led.open_trades("b1") == []                   # regime de-risk closed it
    row = led.conn.execute("SELECT realized_pnl FROM trades WHERE id=?", (tid,)).fetchone()
    assert row["realized_pnl"] == -10.0                  # (90-100)*1, real PnL recorded
    led.close()
