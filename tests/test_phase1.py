"""
Nova Engine — tests/test_phase1.py

Phase 1 acceptance checks:
  * sizing maths (NAV %, gate-capacity scaling, sub-share -> zero)
  * the macro-gate floor (gate < gate_min => no buys)
  * the hard permission rule (asset class not in a book's allowed_assets is refused)
  * manifest + config loading

Run from the repo root:  python -m pytest -q
"""
from decimal import Decimal
import pytest

from core.context import AccountContext, Candidate, NullTaxPolicy, load_books
from core.risk import NavPctSizing, gate_capacity
from tax.uk_cgt import UkCgtPolicy
from core.engine import Engine, EngineConfig, load_engine_config
from core.ledger import Ledger
from adapters.broker_ibkr import IBKRAdapter

class FakeAdapter:
    asset_class = "EQUITY"
    handles = {"EQUITY", "ETF"}
    def __init__(self, gate, candidates):
        self._gate = gate
        self._candidates = candidates
    def macro_gate(self):
        return self._gate
    def scan(self, universe):
        return list(self._candidates)
    def auditor_prompt(self, c):
        return f"audit {c.symbol}"

class HighAuditor:
    def audit(self, prompt):
        return 90.0

def make_book(allowed, wrapper="ISA", tax=None, pct=8.0, nav="4000"):
    ctx = AccountContext(
        book_id=f"book_{wrapper.lower()}",
        wrapper=wrapper,
        broker="IBKR",
        ibkr_account_id=f"U_{wrapper}",
        allowed_assets=set(allowed),
        tax_policy=tax or NullTaxPolicy(),
        sizing=NavPctSizing(max_per_position_pct=pct),
    )
    ctx.nav = Decimal(nav)
    return ctx

def run_engine(books, adapter, navs, gate_min=40.0, exec_threshold=75.0):
    broker = IBKRAdapter(mode="paper", connector="stub", simulated_navs=navs)
    broker.connect()
    ledger = Ledger(":memory:")
    cfg = EngineConfig(gate_min=gate_min, exec_threshold=exec_threshold,
                       universe=["SPY", "NVDA", "VWRL", "FORD"])
    Engine(books, [adapter], broker, HighAuditor(), ledger, cfg).run_cycle()
    return ledger

def test_gate_capacity_boundaries():
    assert gate_capacity(70) == Decimal("1.0")
    assert gate_capacity(55) == Decimal("0.50")
    assert gate_capacity(40) == Decimal("0.0")
    assert gate_capacity(39.9) == Decimal("0.0")

def test_sizing_full_capacity():
    ctx = make_book({"EQUITY", "ETF"}, pct=8.0, nav="4000")
    c = Candidate("NVDA", "EQUITY", 90.0, Decimal("120"))
    order = ctx.sizing.size(c, ctx, gate_score=72)
    assert order.quantity == Decimal("2")
    assert order.notional == Decimal("240.00")

def test_sizing_scaled_capacity():
    ctx = make_book({"EQUITY", "ETF"}, pct=8.0, nav="4000")
    c = Candidate("NVDA", "EQUITY", 90.0, Decimal("120"))
    order = ctx.sizing.size(c, ctx, gate_score=55)
    assert order.quantity == Decimal("1")

def test_sizing_subshare_rounds_to_zero():
    ctx = make_book({"EQUITY", "ETF"}, pct=8.0, nav="4000")
    c = Candidate("SPY", "ETF", 90.0, Decimal("560"))
    order = ctx.sizing.size(c, ctx, gate_score=72)
    assert order.quantity == Decimal("0")

def test_gate_floor_blocks_all_buys():
    book = make_book({"EQUITY", "ETF"})
    adapter = FakeAdapter(gate=30, candidates=[Candidate("NVDA", "EQUITY", 95.0, Decimal("120"))])
    ledger = run_engine([book], adapter, {"U_ISA": 4000}, gate_min=40.0)
    trades = ledger.performance_summary(book.book_id)["trades_recorded"]
    assert trades == 0
    rows = list(ledger.conn.execute("SELECT reason FROM decisions WHERE acted=0 AND book_id=?", (book.book_id,)))
    assert any("below floor" in r["reason"] for r in rows)

def test_disallowed_asset_class_is_refused():
    book = make_book({"ETF"}, nav="20000")
    adapter = FakeAdapter(gate=72, candidates=[
        Candidate("NVDA", "EQUITY", 95.0, Decimal("120")),
        Candidate("VWRL", "ETF", 95.0, Decimal("110")),
    ])
    ledger = run_engine([book], adapter, {"U_ISA": 20000})
    traded = [r["symbol"] for r in ledger.conn.execute("SELECT symbol FROM trades WHERE book_id=?", (book.book_id,))]
    assert "NVDA" not in traded
    assert "VWRL" in traded
    refused = list(ledger.conn.execute("SELECT reason FROM decisions WHERE symbol='NVDA' AND acted=0"))
    assert any("not permitted" in r["reason"] for r in refused)

def test_null_tax_policy_in_wrappers():
    assert NullTaxPolicy().estimate(Decimal("5000"))["tax"] == Decimal("0")

def test_uk_cgt_applies_allowance_then_rate():
    pol = UkCgtPolicy(higher_rate=False)
    out = pol.estimate(Decimal("5000"))
    assert out["allowance_applied"] == Decimal("3000")
    assert out["taxable"] == Decimal("2000")
    assert out["tax"] == Decimal("360.00")

def test_load_books_and_config():
    pytest.importorskip("yaml")
    books = load_books("portfolio.yaml")
    by_id = {b.book_id: b for b in books}
    assert by_id["ibkr_isa_equity"].tax_policy.applicable is False
    assert by_id["ibkr_gia_equity"].tax_policy.applicable is True
    assert "EQUITY" in by_id["ibkr_isa_equity"].allowed_assets
    # Forex book: FX-only, CGT-taxed, and never permitted inside ISA/SIPP.
    fx = by_id["ibkr_forex_margin"]
    assert fx.allowed_assets == {"FX"}
    assert fx.tax_policy.applicable is True
    assert "FX" not in by_id["ibkr_isa_equity"].allowed_assets
    assert "FX" not in by_id["ibkr_sipp_equity"].allowed_assets
    cfg = load_engine_config("config.yaml")
    assert cfg.gate_min == 40
    assert cfg.exec_threshold == 75
    # Structured universe routes per asset class via universe_for(handles).
    assert "NVDA" in cfg.universe_for({"EQUITY", "ETF"})
    assert "EURUSD=X" in cfg.universe_for({"FX"})
    assert "NVDA" not in cfg.universe_for({"FX"})
