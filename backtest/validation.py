"""
Nova Engine — backtest/validation.py

Per-book paper->live validation gate. Encodes the four success profiles
(SIPP / ISA / GIA / FOREX) plus the universal floor, and judges a book's
realised paper-trading record against its OWN profile. A book graduates
paper->live only when its profile passes AND the operator explicitly
authorizes going live.

Design rules honoured (see CLAUDE.md "Per-book success criteria"):
  * Universal floor for EVERY book: positive net expectancy after costs
    (profit factor > 1) that SURVIVES walk-forward + Monte-Carlo robustness.
  * Each book is judged against its OWN profile — not one global composite.
  * Forex is judged at the ACCOUNT / equity-curve level: win rate and
    reward:risk are interchangeable style choices, so they are LOGGED for
    transparency but NOT gated.
  * Nothing here promotes a book to live. It only produces a verdict; the hard
    safety gate (paper default + explicit operator authorization) still stands.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from backtest.walk_forward import run_walk_forward_grid
from backtest.monte_carlo import run_monte_carlo_drawdown

# --------------------------------------------------------------------------- #
# Profiles
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class BookProfile:
    """Success criteria for one book. ``None`` => criterion not gated here.

    The universal floor (profit factor > 1 + walk-forward + Monte-Carlo
    robustness) is applied to EVERY profile in addition to these fields.
    """
    name: str
    min_trades: int
    min_win_rate: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    min_profit_factor: Optional[float] = None
    min_sortino: Optional[float] = None
    min_expectancy: Optional[float] = None        # mean per-trade PnL must exceed this
    max_consec_losses: Optional[int] = None
    account_level: bool = False                    # Forex: win rate / RR logged, not gated
    note: str = ""


# The four authoritative profiles (CLAUDE.md, 2026-06-14).
PROFILES: dict[str, BookProfile] = {
    "SIPP": BookProfile(
        name="SIPP", min_trades=150, min_win_rate=0.70, max_drawdown_pct=5.0,
        note="Income/compounding pension: tightest drawdown, lowest turnover.",
    ),
    "ISA": BookProfile(
        name="ISA", min_trades=200, min_profit_factor=1.6, min_expectancy=0.0,
        max_drawdown_pct=18.0, min_sortino=1.0, min_win_rate=0.45,
        note="Tax-free growth/high-reward: realise freely; honest (not forced) win rate.",
    ),
    "GIA": BookProfile(
        name="GIA", min_trades=150, min_win_rate=0.60, max_drawdown_pct=10.0,
        note="Tax-efficient core: low turnover; after-tax return >= benchmark.",
    ),
    "FOREX": BookProfile(
        name="FOREX", min_trades=300, min_profit_factor=1.5, min_sortino=1.0,
        max_drawdown_pct=20.0, max_consec_losses=6, account_level=True,
        note="Leverage <=5:1, per-trade risk <=2%; judged on the equity curve.",
    ),
}


def profile_for_book(ctx) -> BookProfile:
    """Pick the success profile for an AccountContext.

    Any book that may trade FX -> FOREX (leveraged Forex is wrapper-locked to a
    taxable margin account, so it is identified by asset class, not wrapper).
    Otherwise selected by wrapper. Falls back to a universal-floor-only profile.
    """
    if "FX" in getattr(ctx, "allowed_assets", set()):
        return PROFILES["FOREX"]
    wrapper = getattr(ctx, "wrapper", "")
    return PROFILES.get(wrapper, BookProfile(name="GENERIC", min_trades=100))


# --------------------------------------------------------------------------- #
# Metrics (pure functions — no I/O, unit-testable in isolation)
# --------------------------------------------------------------------------- #
def win_rate(pnls: Sequence[float]) -> Optional[float]:
    """Fraction of closed trades with positive PnL. None if no trades."""
    if not pnls:
        return None
    return sum(1 for p in pnls if p > 0) / len(pnls)


def profit_factor(pnls: Sequence[float]) -> Optional[float]:
    """Gross profit / gross loss. ``inf`` if there are no losing trades.

    None if there are no trades at all. PF > 1 is the universal-floor signal
    that the book makes more than it loses.
    """
    if not pnls:
        return None
    gross_profit = sum(p for p in pnls if p > 0)
    gross_loss = -sum(p for p in pnls if p < 0)
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def expectancy(pnls: Sequence[float]) -> Optional[float]:
    """Mean PnL per trade. None if no trades."""
    if not pnls:
        return None
    return sum(pnls) / len(pnls)


def max_consecutive_losses(pnls: Sequence[float]) -> int:
    """Longest run of consecutive losing trades."""
    worst = run = 0
    for p in pnls:
        if p < 0:
            run += 1
            worst = max(worst, run)
        else:
            run = 0
    return worst


def sortino_ratio(returns: Sequence[float], target: float = 0.0) -> Optional[float]:
    """Downside-deviation-adjusted return (non-annualised, trade-level).

    ``inf`` if there is no downside; None if fewer than two returns.
    """
    if returns is None or len(returns) < 2:
        return None
    arr = np.asarray(returns, dtype=float)
    mean_excess = float(arr.mean()) - target
    downside = arr[arr < target] - target
    if downside.size == 0:
        return math.inf if mean_excess > 0 else 0.0
    downside_dev = math.sqrt(float((downside ** 2).mean()))
    if downside_dev == 0:
        return None
    return mean_excess / downside_dev


def max_drawdown_pct(nav_curve: Optional[Sequence[float]] = None,
                     returns: Optional[Sequence[float]] = None) -> Optional[float]:
    """Maximum drawdown as a percentage.

    Prefers a real NAV equity curve; falls back to a curve compounded from
    fractional returns. None if neither is usable.
    """
    curve: Optional[np.ndarray] = None
    if nav_curve is not None and len(nav_curve) >= 2:
        curve = np.asarray(nav_curve, dtype=float)
    elif returns is not None and len(returns) >= 1:
        curve = np.cumprod(1.0 + np.asarray(returns, dtype=float))
    if curve is None or curve.size == 0:
        return None
    peaks = np.maximum.accumulate(curve)
    with np.errstate(divide="ignore", invalid="ignore"):
        drawdowns = np.where(peaks > 0, (peaks - curve) / peaks, 0.0)
    return float(np.max(drawdowns)) * 100.0


def compute_metrics(pnls: Sequence[float],
                    returns: Optional[Sequence[float]] = None,
                    nav_curve: Optional[Sequence[float]] = None) -> dict:
    """Assemble the full metric set a profile is judged against."""
    return {
        "n_trades": len(pnls),
        "win_rate": win_rate(pnls),
        "profit_factor": profit_factor(pnls),
        "expectancy": expectancy(pnls),
        "max_consec_losses": max_consecutive_losses(pnls),
        "sortino": sortino_ratio(returns) if returns is not None else None,
        "max_drawdown_pct": max_drawdown_pct(nav_curve=nav_curve, returns=returns),
    }


# --------------------------------------------------------------------------- #
# Result objects
# --------------------------------------------------------------------------- #
@dataclass
class CriterionResult:
    """One pass/fail check, with the value, threshold and whether it gates."""
    name: str
    value: Optional[float]
    rule: str                 # human-readable, e.g. ">= 0.70"
    passed: bool
    gated: bool               # False => logged for transparency, doesn't block


@dataclass
class ValidationResult:
    book_id: str
    profile: str
    passed: bool
    metrics: dict
    criteria: list[CriterionResult] = field(default_factory=list)

    def summary(self) -> str:
        verdict = "PASS" if self.passed else "FAIL"
        lines = [f"[{self.book_id}] profile={self.profile} -> {verdict}"]
        for c in self.criteria:
            mark = "OK " if c.passed else "XX "
            tag = "" if c.gated else "  (logged, not gated)"
            val = "n/a" if c.value is None else f"{c.value:.4g}"
            lines.append(f"  {mark}{c.name}: {val} {c.rule}{tag}")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Robustness (universal floor)
# --------------------------------------------------------------------------- #
def _survives_walk_forward(returns: Sequence[float]) -> tuple[bool, float]:
    """True if a small walk-forward parameter sweep stays net-positive (Sharpe>0)."""
    grid = [{"gate_min": 40}, {"gate_min": 50}, {"exec_threshold": 80}]
    res = run_walk_forward_grid(pd.Series(returns, dtype=float), grid)
    best = float(res.get("best_sharpe", 0.0))
    return best > 0.0, best


def portfolio_returns(nav_curve: Optional[Sequence[float]]) -> Optional[list]:
    """PORTFOLIO-level per-event returns from the NAV equity curve.

    Drawdown is a portfolio property, so the drawdown Monte-Carlo must bootstrap
    NAV returns — not per-trade `pnl/notional` (position-level) returns, which
    model betting 100% of capital on each trade and massively overstate drawdown.
    Keeps only the non-zero steps (the actual P&L events). None if unusable.
    """
    if nav_curve is None or len(nav_curve) < 2:
        return None
    arr = np.asarray(nav_curve, dtype=float)
    prev = arr[:-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(prev != 0, (arr[1:] - prev) / prev, 0.0)
    r = r[np.isfinite(r)]
    r = r[r != 0.0]
    return r.tolist()


def _survives_monte_carlo(returns: Sequence[float], dd_cap_pct: Optional[float]
                          ) -> tuple[bool, float]:
    """True if the bootstrapped 95th-percentile max drawdown stays within the cap.

    `returns` must be PORTFOLIO-level (see portfolio_returns). Uses the book's
    drawdown cap when set, else a universal 30% sanity bound.
    """
    _, p95, _ = run_monte_carlo_drawdown(list(returns), num_simulations=2000)
    cap = (dd_cap_pct if dd_cap_pct is not None else 30.0) / 100.0
    return p95 <= cap, p95 * 100.0


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #
def validate_book(profile: BookProfile,
                  pnls: Sequence[float],
                  returns: Optional[Sequence[float]] = None,
                  nav_curve: Optional[Sequence[float]] = None,
                  *,
                  book_id: str = "",
                  run_robustness: bool = True,
                  seed: Optional[int] = None) -> ValidationResult:
    """Judge one book's realised record against its profile + the universal floor.

    Args:
        profile: the book's success profile.
        pnls: realised PnL per closed trade (account currency).
        returns: per-trade fractional returns (pnl / notional) — for Sortino and
            the robustness checks. Optional; some criteria become n/a without it.
        nav_curve: the NAV equity curve (preferred drawdown source).
        run_robustness: run walk-forward + Monte-Carlo (the universal floor).
        seed: seed numpy for reproducible robustness checks (tests/CI).

    Returns:
        A ValidationResult. ``passed`` is True only when every GATED criterion
        passes. Never auto-promotes the book to live.
    """
    if seed is not None:
        np.random.seed(seed)

    m = compute_metrics(pnls, returns=returns, nav_curve=nav_curve)
    crits: list[CriterionResult] = []

    def add(name, value, ok, rule, gated=True):
        crits.append(CriterionResult(name, value, rule, bool(ok), gated))

    # ---- sample size --------------------------------------------------- #
    n = m["n_trades"]
    add("sample_size", float(n), n >= profile.min_trades, f">= {profile.min_trades}")

    # ---- universal floor: profit factor > 1 ---------------------------- #
    pf = m["profit_factor"]
    add("profit_factor(floor)", pf, pf is not None and pf > 1.0, "> 1.0 (universal floor)")

    # ---- universal floor: robustness ----------------------------------- #
    # MC drawdown bootstraps PORTFOLIO returns (NAV curve); falls back to the
    # per-trade series only if no NAV curve is available.
    port_ret = portfolio_returns(nav_curve)
    if run_robustness and returns is not None and len(returns) >= 2:
        wf_ok, wf_sharpe = _survives_walk_forward(returns)
        add("walk_forward", wf_sharpe, wf_ok, "Sharpe > 0 (universal floor)")
        mc_input = port_ret if port_ret else list(returns)
        mc_ok, mc_p95 = _survives_monte_carlo(mc_input, profile.max_drawdown_pct)
        cap = profile.max_drawdown_pct if profile.max_drawdown_pct is not None else 30.0
        add("monte_carlo_dd_p95", mc_p95, mc_ok, f"<= {cap:g}% (universal floor)")
    elif run_robustness:
        # Can't prove robustness without a return series — floor not met.
        add("walk_forward", None, False, "Sharpe > 0 (insufficient data)")
        add("monte_carlo_dd_p95", None, False, "p95 DD within cap (insufficient data)")

    # ---- profile-specific ---------------------------------------------- #
    if profile.min_win_rate is not None:
        wr = m["win_rate"]
        # Forex: win rate is a style choice -> logged, not gated.
        add("win_rate", wr, wr is not None and wr >= profile.min_win_rate,
            f">= {profile.min_win_rate:.0%}", gated=not profile.account_level)

    if profile.max_drawdown_pct is not None:
        dd = m["max_drawdown_pct"]
        add("max_drawdown_pct", dd, dd is not None and dd <= profile.max_drawdown_pct,
            f"<= {profile.max_drawdown_pct:g}%")

    if profile.min_profit_factor is not None:
        add("profit_factor", pf, pf is not None and pf >= profile.min_profit_factor,
            f">= {profile.min_profit_factor:g}")

    if profile.min_sortino is not None:
        so = m["sortino"]
        add("sortino", so, so is not None and so >= profile.min_sortino,
            f">= {profile.min_sortino:g}")

    if profile.min_expectancy is not None:
        ex = m["expectancy"]
        add("expectancy", ex, ex is not None and ex > profile.min_expectancy,
            f"> {profile.min_expectancy:g}")

    if profile.max_consec_losses is not None:
        cl = m["max_consec_losses"]
        add("max_consec_losses", float(cl), cl <= profile.max_consec_losses,
            f"<= {profile.max_consec_losses}")

    passed = all(c.passed for c in crits if c.gated)
    return ValidationResult(book_id=book_id or profile.name, profile=profile.name,
                            passed=passed, metrics=m, criteria=crits)


def validate_from_ledger(ctx, ledger, *, run_robustness: bool = True,
                         seed: Optional[int] = None) -> ValidationResult:
    """Validate a book straight from the ledger using its AccountContext."""
    profile = profile_for_book(ctx)
    return validate_book(
        profile,
        pnls=ledger._closed_pnls(ctx.book_id),
        returns=ledger.closed_returns(ctx.book_id),
        nav_curve=ledger.nav_series(ctx.book_id),
        book_id=ctx.book_id,
        run_robustness=run_robustness,
        seed=seed,
    )
