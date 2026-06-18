import math
from decimal import Decimal

import pytest

from core.context import AccountContext, NullTaxPolicy
from core.ledger import Ledger
from core.risk import NavPctSizing
from backtest.validation import (
    BookProfile, PROFILES, profile_for_book,
    win_rate, profit_factor, expectancy, max_consecutive_losses,
    sortino_ratio, max_drawdown_pct, compute_metrics,
    validate_book, validate_from_ledger,
)


# --------------------------------------------------------------------------- #
# Profile selection
# --------------------------------------------------------------------------- #
def _ctx(book_id, wrapper, allowed):
    return AccountContext(book_id, wrapper, "IBKR", "U", set(allowed),
                          NullTaxPolicy(), NavPctSizing())

def test_profile_selection_by_wrapper_and_asset():
    assert profile_for_book(_ctx("isa", "ISA", {"EQUITY"})).name == "ISA"
    assert profile_for_book(_ctx("sipp", "SIPP", {"EQUITY"})).name == "SIPP"
    assert profile_for_book(_ctx("gia", "GIA", {"EQUITY"})).name == "GIA"
    # FX is identified by asset class, not wrapper (Forex sits in a MARGIN book).
    assert profile_for_book(_ctx("fx", "MARGIN", {"FX"})).name == "FOREX"
    # Unknown wrapper -> generic universal-floor-only profile.
    assert profile_for_book(_ctx("x", "WEIRD", {"EQUITY"})).name == "GENERIC"


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def test_metric_functions():
    pnls = [100, -50, 200, -100, 50]
    assert win_rate(pnls) == pytest.approx(0.6)
    assert profit_factor(pnls) == pytest.approx(350 / 150)
    assert expectancy(pnls) == pytest.approx(40.0)
    assert max_consecutive_losses(pnls) == 1
    assert max_consecutive_losses([10, -5, -5, -5, 20]) == 3

def test_profit_factor_no_losses_is_inf():
    assert profit_factor([10, 20]) == math.inf
    assert win_rate([]) is None

def test_sortino_and_drawdown():
    so = sortino_ratio([0.1, -0.05, 0.2])
    assert so == pytest.approx((0.25 / 3) / 0.05, rel=1e-3)
    # Peak 120, trough 90 -> 25% drawdown.
    assert max_drawdown_pct(nav_curve=[100, 120, 90, 110]) == pytest.approx(25.0)
    # Falls back to compounded returns when no NAV curve is given.
    assert max_drawdown_pct(returns=[0.1, -0.5, 0.1]) == pytest.approx(50.0, rel=1e-3)

def test_compute_metrics_shape():
    m = compute_metrics([10, -5], returns=[0.1, -0.05], nav_curve=[100, 110, 105])
    assert m["n_trades"] == 2
    assert set(m) >= {"win_rate", "profit_factor", "expectancy",
                      "max_consec_losses", "sortino", "max_drawdown_pct"}


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #
def test_insufficient_sample_fails():
    res = validate_book(PROFILES["SIPP"], [10, 20, 30], run_robustness=False)
    assert res.passed is False
    sample = next(c for c in res.criteria if c.name == "sample_size")
    assert sample.passed is False and sample.gated is True

def test_passing_book_meets_profile():
    # Custom small-sample profile so we can exercise a clean PASS deterministically.
    prof = BookProfile(name="TEST", min_trades=5, min_win_rate=0.6,
                       max_drawdown_pct=50.0, min_profit_factor=1.2)
    pnls = [100, 120, -40, 90, 110, -30]      # 4/6 wins, PF high
    res = validate_book(prof, pnls, returns=[0.02, 0.03, -0.01, 0.02, 0.03, -0.01],
                        run_robustness=False)
    assert res.passed is True

def test_universal_floor_blocks_losing_book():
    prof = BookProfile(name="TEST", min_trades=3)
    res = validate_book(prof, [-10, -20, 5], run_robustness=False)  # PF < 1
    assert res.passed is False
    pf = next(c for c in res.criteria if c.name == "profit_factor(floor)")
    assert pf.passed is False

def test_forex_win_rate_logged_not_gated():
    """Forex: a low win rate must NOT block the book if the account compounds."""
    prof = PROFILES["FOREX"]
    # Many small winners offset by big... no: few big wins, many small losses ->
    # low win rate but PF >= 1.5 and strong Sortino. Sample overridden via custom.
    fx = BookProfile(name="FOREX", min_trades=5, min_win_rate=0.90,
                     min_profit_factor=1.5, min_sortino=1.0,
                     max_drawdown_pct=20.0, max_consec_losses=6, account_level=True)
    pnls = [-10, -10, -10, 200, -10]          # 1/5 wins (20%) but big net positive
    returns = [-0.01, -0.01, -0.01, 0.20, -0.01]
    res = validate_book(fx, pnls, returns=returns, run_robustness=False)
    wr = next(c for c in res.criteria if c.name == "win_rate")
    assert wr.gated is False                   # logged, not gated
    assert wr.passed is False                  # 20% < 90%
    assert res.passed is True                  # ... yet the book still passes


# --------------------------------------------------------------------------- #
# End-to-end from the ledger
# --------------------------------------------------------------------------- #
def test_validate_from_ledger_is_deterministic_and_routes_forex():
    led = Ledger(":memory:")
    ctx = _ctx("ibkr_forex_margin", "MARGIN", {"FX"})
    # Record + close a handful of FX trades and a NAV curve.
    for i, (pnl, notional) in enumerate([(50, 1000), (-20, 1000), (80, 1000),
                                         (-10, 1000), (40, 1000)]):
        tid = led.record_trade(ctx.book_id, "U", f"EURUSD=X", "BUY",
                               Decimal("1000"), Decimal("1.1"), Decimal(str(notional)))
        led.close_trade(tid, Decimal("1.1"), Decimal(str(pnl)))
    for nav in [5000, 5050, 5030, 5110, 5150]:
        led.record_nav(ctx.book_id, Decimal(str(nav)))

    res = validate_from_ledger(ctx, led, seed=42)
    assert res.profile == "FOREX"
    assert res.metrics["n_trades"] == 5
    # 5 trades < 300 required -> cannot pass, but robustness ran (criteria present).
    assert res.passed is False
    names = {c.name for c in res.criteria}
    assert "walk_forward" in names and "monte_carlo_dd_p95" in names
    led.close()


def test_forex_profile_gates_mar_logs_sortino_and_streaks():
    """Account-level FOREX (trend): MAR/Calmar is GATED; Sortino and consecutive
    losses are LOGGED but NOT gated (style choices for a lumpy trend equity curve)."""
    pnls = [10, -5, 20, -8, 15, -6, 12, -4, 18]
    rets = [p / 100 for p in pnls]
    nav = [5000, 5100, 5050, 5200, 5150, 5300, 5250, 5400, 5350, 5500]
    res = validate_book(PROFILES["FOREX"], pnls=pnls, returns=rets, nav_curve=nav,
                        run_robustness=False, seed=1)
    by = {c.name: c for c in res.criteria}
    assert by["mar(calmar)"].gated is True            # return-vs-risk is the gate
    assert by["profit_factor"].gated is True
    assert by["sortino"].gated is False               # logged, not gated
    assert by["max_consec_losses"].gated is False     # logged, not gated


def test_mc_cap_field_overrides_drawdown_cap():
    """mc_max_drawdown_pct changes ONLY the cap the p95 drawdown is judged
    against (not the measured value) — used so regime-timed allocation books get
    a book-honest MC bound while keeping their tight realised-DD rail."""
    rets = [0.02, -0.05, 0.03, -0.08, 0.04, -0.02, 0.05, -0.06, 0.03, -0.04]
    base = BookProfile(name="A", min_trades=0, max_drawdown_pct=5.0)
    wide = BookProfile(name="A", min_trades=0, max_drawdown_pct=5.0,
                       mc_max_drawdown_pct=10.0)
    r1 = validate_book(base, pnls=rets, returns=rets, seed=7)
    r2 = validate_book(wide, pnls=rets, returns=rets, seed=7)
    mc1 = next(c for c in r1.criteria if c.name == "monte_carlo_dd_p95")
    mc2 = next(c for c in r2.criteria if c.name == "monte_carlo_dd_p95")
    assert mc1.value == pytest.approx(mc2.value)          # measured value unchanged
    assert "<= 5%" in mc1.rule and "<= 10%" in mc2.rule    # cap differs
    assert (not mc1.passed) or mc2.passed                  # wider cap is >= permissive


def test_allocation_path_uses_longhorizon_profile():
    """Path A (2026-06-18): low-turnover allocation books are judged on the
    LONG-HORIZON profile — % positive months gated at 55%, MAR/Calmar gated, and
    the interim realised-DD rail RETIRED (thematic equity is inherently extreme-DD,
    so DD gating would reject the whole asset class)."""
    led = Ledger(":memory:")
    ctx = AccountContext("ibkr_sipp_equity", "SIPP", "IBKR", "U", {"EQUITY", "ETF"},
                         NullTaxPolicy(), NavPctSizing(), strategy="allocation",
                         gate_min=75)
    for i in range(700):
        led.record_nav(ctx.book_id, Decimal(str(10000 + i * 5)))
    res = validate_from_ledger(ctx, led, run_robustness=False)
    by = {c.name: c for c in res.criteria}
    assert ">= 55%" in by["win_rate"].rule               # % positive months bar lowered
    assert "mar(calmar)" in by and by["mar(calmar)"].gated is True   # MAR is the risk gate
    assert "max_drawdown_pct" not in by                  # interim realised-DD rail retired
    led.close()
