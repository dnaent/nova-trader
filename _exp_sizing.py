"""SCRATCH (gitignored intent; delete after use) — risk-based equity sizing experiment.

Swaps ISA/GIA from flat NAV-% sizing to ATR (risk-based, vol-throttled) sizing and
re-runs the GFC out-of-sample + in-sample windows for before/after comparison.
SIPP (allocation) and Forex are left UNCHANGED. The leverage field is reused as a
per-position notional cap (notional <= NAV * leverage), so leverage<1 caps
concentration while risk_pct sets the per-trade risk (the vol-throttle).
"""
from __future__ import annotations
import sys, os, dataclasses
sys.stdout.reconfigure(line_buffering=True)


def _fresh(db: str) -> str:
    """Delete a stale experiment DB so the Ledger starts empty (it APPENDS, so
    re-running over an existing file double-counts trades and corrupts the curve)."""
    if db != ":memory:" and os.path.exists(db):
        os.remove(db)
    return db

import pandas as pd
from core.context import load_books, Candidate, Order
from core.risk import AtrSizing
from adapters.asset_equity import EquityAdapter
from adapters.asset_fx import FxAdapter
from adapters.asset_allocation import AllocationAdapter
from backtest.replay import run_replay

EXEC = 35.0
TACTICAL = {"ibkr_isa_equity", "ibkr_gia_equity"}   # books to switch to ATR sizing


def build_books(risk_pct: float, lev_cap: float):
    books = load_books("portfolio.yaml")
    out = []
    for b in books:
        if b.book_id in TACTICAL:
            sizing = AtrSizing(risk_pct=risk_pct, leverage=lev_cap, unit="shares",
                               stop_atr_multiplier=2.0, take_atr_multiplier=4.0,
                               trailing_atr_multiplier=2.0)
            out.append(dataclasses.replace(b, sizing=sizing))
        else:
            out.append(b)
    return out


def run_window(label, start, end, risk_pct, lev_cap, db, sipp_basket, step=1):
    print(f"\n########## {label}: {start}->{end} ATR risk={risk_pct}% levcap={lev_cap} "
          f"sipp_basket={sipp_basket} ##########", flush=True)
    books = build_books(risk_pct, lev_cap)
    adapters = [EquityAdapter(), FxAdapter(), AllocationAdapter(basket=sipp_basket)]
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=adapters, books=books, do_report=True)
    led.close()


class _TrailAtr(AtrSizing):
    """ATR risk-based sizing but LET WINNERS RUN: trailing stop active, no fixed
    take. Thesis: improving the win/loss asymmetry could lift the GFC Sortino."""
    def size(self, c, ctx, gate_score):
        o = super().size(c, ctx, gate_score)
        o.take_profit = None
        o.trailing_atr = self.trailing_atr_multiplier
        return o


def build_books_sortino(variant):
    """ISA/GIA variants for the GFC-Sortino thesis; SIPP/FX untouched."""
    books = load_books("portfolio.yaml")
    out = []
    for b in books:
        if b.book_id in TACTICAL:
            if variant == "trail":
                sz = _TrailAtr(risk_pct=0.35, leverage=0.35, unit="shares",
                               stop_atr_multiplier=2.0, take_atr_multiplier=4.0,
                               trailing_atr_multiplier=2.0)
                out.append(dataclasses.replace(b, sizing=sz))
            elif variant == "crash":   # canonical ATR sizing + crash de-risk circuit-breaker
                gr = dataclasses.replace(b.guardrails, crash_derisk_dd_pct=12.0)
                out.append(dataclasses.replace(b, guardrails=gr))
            else:
                out.append(b)
        else:
            out.append(b)
    return out


def run_sortino(label, start, end, variant, db, sipp_basket, step=1):
    print(f"\n########## {label} [{variant}]: {start}->{end} ##########", flush=True)
    books = build_books_sortino(variant)
    adapters = [EquityAdapter(), FxAdapter(), AllocationAdapter(basket=sipp_basket)]
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=adapters, books=books, do_report=True)
    led.close()


def run_canon(label, start, end, sipp_basket, db, step=1):
    """Confirm the CANONICAL manifest (ISA/GIA now ATR-sized; GIA profile = ISA)."""
    print(f"\n########## {label}: {start}->{end} CANONICAL sipp={sipp_basket} ##########", flush=True)
    adapters = [EquityAdapter(), FxAdapter(), AllocationAdapter(basket=sipp_basket)]
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=adapters, books=None, do_report=True)  # books=None => canonical
    led.close()


class _WeightedAlloc:
    """Allocation adapter with per-symbol target weights (core+satellite)."""
    asset_class = "ETF"; handles = {"EQUITY", "ETF"}; strategy = "allocation"
    def __init__(self, weights):
        from layers.macro_gate import MacroGate
        self.gate = MacroGate(); self.weights = dict(weights); self._last_gate_result = {}
    def macro_gate(self):
        self._last_gate_result = self.gate.evaluate()
        return self._last_gate_result.get("gate_score", 50.0)
    def scan(self, universe):
        from layers.data_loader import get_latest_price
        out = []
        for sym, w in self.weights.items():
            px = get_latest_price(sym)
            if px is None or px <= 0:
                continue
            out.append(Candidate(sym, "ETF", 100.0, px,
                                 meta={"strategy": "allocation", "markers": {}, "weight": w}))
        return out
    def auditor_prompt(self, c):
        return f"hold {c.symbol}"


class _WeightedSizing:
    """NAV-% sizing using the candidate's target weight (buy-and-hold; wide stop)."""
    def __init__(self, stop_pct=0.30):
        from decimal import Decimal
        self.stop_pct = Decimal(str(stop_pct))
    def size(self, candidate, ctx, gate_score):
        from decimal import Decimal, ROUND_DOWN
        from core.risk import gate_capacity
        from core.context import Order
        w = Decimal(str(candidate.meta.get("weight", 0)))
        alloc = ctx.nav * w * gate_capacity(gate_score)
        price = Decimal(candidate.price)
        qty = (alloc / price).to_integral_value(rounding=ROUND_DOWN) if price > 0 else Decimal("0")
        notional = (qty * price).quantize(Decimal("0.01"))
        return Order(book_id=ctx.book_id, account_id=ctx.ibkr_account_id, symbol=candidate.symbol,
                     side="BUY", quantity=qty, price=price, notional=notional,
                     stop_loss=(price * (Decimal("1") - self.stop_pct)).quantize(Decimal("0.01")),
                     take_profit=None, trailing_pct=None, meta={"weight": str(w)})


def run_hybrid(label, start, end, weights, db, step=1):
    """SIPP-only core+satellite replay (fast: no ML scanner / FX). Reads SIPP result."""
    print(f"\n########## {label}: {start}->{end} weights={weights} ##########", flush=True)
    books = load_books("portfolio.yaml")
    sipp = next(b for b in books if b.book_id == "ibkr_sipp_equity")
    gr = dataclasses.replace(sipp.guardrails, max_correlation=0.99)   # hold the whole basket
    sipp2 = dataclasses.replace(sipp, guardrails=gr, sizing=_WeightedSizing())
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=[_WeightedAlloc(weights)], books=[sipp2],
                     do_report=True)
    led.close()


def run_enriched(label, start, end, proxies, db, step=1):
    """SIPP-only: enriched diversified 'Pension Fortress' via long-history PROXIES
    (gold/global/income core + thematic satellites), ~fully invested (equal weight)."""
    from core.risk import NavPctSizing
    print(f"\n########## {label}: {start}->{end} enriched_proxies={proxies} ##########", flush=True)
    books = load_books("portfolio.yaml")
    sipp = next(b for b in books if b.book_id == "ibkr_sipp_equity")
    w = max(1, int(100 / len(proxies)))
    sz = NavPctSizing(max_per_position_pct=w, leverage=1.0, unit="shares",
                      stop_pct=0.30, take_pct=10.0, trailing_pct=0.30)
    sipp2 = dataclasses.replace(sipp, sizing=sz)   # SIPP already has max_correlation 0.99
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=[AllocationAdapter(basket=proxies)],
                     books=[sipp2], do_report=True)
    led.close()


class _FxTsmom:
    """Forex re-think: TIME-SERIES MOMENTUM (TSMOM) — the canonical managed-futures FX
    edge. Long if the pair's trailing ~12-month return is positive, short if negative
    (sized by ATR via the book's sizing). Uses ONLY price (get_daily_data) — never the
    marker pipeline that the failed EMA/ADX trend used. Permissive gate (TSMOM is an
    always-positioned momentum strategy)."""
    asset_class = "FX"; handles = {"FX"}; strategy = "tactical"
    def __init__(self, lookback=252, min_abs=0.0, gate=60.0):
        self.lookback = lookback; self.min_abs = min_abs; self.gate = gate
        self._last_gate_result = {}
    def macro_gate(self):
        self._last_gate_result = {"regime": "tsmom", "gate_score": self.gate}
        return self.gate
    def scan(self, universe):
        from decimal import Decimal as D
        from layers.data_loader import get_daily_data
        out = []
        for sym in universe:
            df = get_daily_data(sym, lookback_days=self.lookback + 40)
            if df is None or df.empty or "Close" not in df.columns or len(df) < self.lookback + 2:
                continue
            close = df["Close"].astype(float)
            r = close.iloc[-1] / close.iloc[-self.lookback] - 1.0
            if abs(r) < self.min_abs:
                continue
            side = "BUY" if r > 0 else "SELL"
            score = float(min(95.0, max(60.0, 60.0 + abs(r) * 200.0)))
            out.append(Candidate(sym, "FX", score, D(str(round(float(close.iloc[-1]), 6))),
                                 side=side, meta={"markers": {}, "r12": round(float(r), 4)}))
        out.sort(key=lambda x: x.quant_score, reverse=True)
        return out
    def auditor_prompt(self, c):
        return f"tsmom {c.symbol}"


def run_fx(label, start, end, adapter, db, step=1):
    """Backtest an FX adapter on the ibkr_forex_margin book (account-level FOREX profile)."""
    print(f"\n########## {label}: {start}->{end} ##########", flush=True)
    books = load_books("portfolio.yaml")
    fx = next(b for b in books if b.book_id == "ibkr_forex_margin")
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=[adapter], books=[fx], do_report=True)
    led.close()


def run_alloc(book_id, label, start, end, proxies, db, step=1):
    """Validate ANY allocation book with long-history PROXIES, injected as its PER-BOOK
    universe (the engine passes ctx.universe to the adapter — passing basket= to the
    adapter is overridden by a book's per-book universe, so we must replace ctx.universe).
    ~fully invested equal-weight; curve-validated."""
    from core.risk import NavPctSizing
    print(f"\n########## {label}: {start}->{end} {book_id} proxies={proxies} ##########", flush=True)
    books = load_books("portfolio.yaml")
    b = next(x for x in books if x.book_id == book_id)
    w = max(1, int(100 / len(proxies)))
    sz = NavPctSizing(max_per_position_pct=w, leverage=1.0, unit="shares",
                      stop_pct=0.30, take_pct=10.0, trailing_pct=0.30)
    b2 = dataclasses.replace(b, universe=list(proxies), sizing=sz)
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=[AllocationAdapter()], books=[b2], do_report=True)
    led.close()


def run_thematic(label, start, end, proxies, db, step=1):
    """SIPP-only thesis: equal-weight thematic basket through a window. ISA/GIA/FX
    stay canonical (untouched); we read the SIPP result. Relax the SIPP correlation
    guard so all four (correlated) themes are actually held."""
    print(f"\n########## THEMATIC_{label}: {start}->{end} basket={proxies} ##########", flush=True)
    books = load_books("portfolio.yaml")
    out = []
    for b in books:
        if b.book_id == "ibkr_sipp_equity":
            from core.risk import NavPctSizing
            gr = dataclasses.replace(b.guardrails, max_correlation=0.99)  # hold the whole basket
            # 25% each x 4 themes = ~100% invested; wide stop/no-take (buy-and-hold).
            sz = NavPctSizing(max_per_position_pct=25, leverage=1.0, unit="shares",
                              stop_pct=0.30, take_pct=10.0, trailing_pct=0.30)
            out.append(dataclasses.replace(b, guardrails=gr, sizing=sz))
        else:
            out.append(b)
    adapters = [EquityAdapter(), FxAdapter(), AllocationAdapter(basket=proxies)]
    led = run_replay(pd.Timestamp(start), pd.Timestamp(end), db_path=_fresh(db), step_days=step,
                     exec_threshold=EXEC, adapters=adapters, books=out, do_report=True)
    led.close()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if mode == "smoke":
        # fast 1-year sanity check: do ISA/GIA actually open ATR-sized trades?
        run_window("smoke", "2021-01-04", "2022-01-03", 0.5, 0.35,
                   "nova_exp_smoke.db", ["VWRL.L"], step=1)
    elif mode == "sweep":
        configs = [(0.35, 0.35), (0.60, 0.50)]
        for rp, lc in configs:
            tag = f"r{int(rp*100)}_l{int(lc*100)}"
            run_window(f"GFC_{tag}", "2007-01-03", "2018-01-02", rp, lc,
                       f"nova_exp_gfc_{tag}.db", ["SPY"], step=1)
            run_window(f"INSAMPLE_{tag}", "2018-01-02", "2026-06-01", rp, lc,
                       f"nova_exp_ins_{tag}.db", ["VWRL.L"], step=1)
    elif mode == "thematic":
        # THESIS: is a 4-theme equal-weight thematic SIPP too high-beta for the
        # pension mandate? Use long-history USD proxies (the real Acc thematic ETFs
        # are 2019-2022 inception, can't be GFC-tested):
        #   AI/tech infra -> QQQ (1999) | data centres -> VNQ (2004)
        #   critical materials -> XME (2006) | renewables -> PBW (2005, WilderHill)
        # All four cover the 2008 crash. Equal-weight (25% each), correlation guard
        # relaxed so all four are held (we WANT the chosen basket, not de-duped).
        proxies = ["QQQ", "VNQ", "XME", "PBW"]
        run_thematic("GFC", "2007-01-03", "2018-01-02", proxies, "nova_exp_them_gfc.db")
        run_thematic("INSAMPLE", "2018-01-02", "2026-06-01", proxies, "nova_exp_them_ins.db")
    elif mode == "canon":
        run_canon("CANON_GFC", "2007-01-03", "2018-01-02", ["SPY"], "nova_canon_gfc.db")
        run_canon("CANON_INS", "2018-01-02", "2026-06-01", ["VWRL.L"], "nova_canon_ins.db")
    elif mode == "final":
        # 1) Confirm the canonical ISA/GIA (ATR sizing + GIA=ISA mandate), both windows.
        run_canon("CANON_GFC", "2007-01-03", "2018-01-02", ["SPY"], "nova_canon_gfc.db")
        run_canon("CANON_INS", "2018-01-02", "2026-06-01", ["VWRL.L"], "nova_canon_ins.db")
        # 2) SIPP core+satellite frontier (defensive AGG core and broad SPY core).
        frontier = {
            "agg80_them20": {"AGG": 0.80, "QQQ": 0.05, "VNQ": 0.05, "XME": 0.05, "PBW": 0.05},
            "agg60_them40": {"AGG": 0.60, "QQQ": 0.10, "VNQ": 0.10, "XME": 0.10, "PBW": 0.10},
            "spy60_them40": {"SPY": 0.60, "QQQ": 0.10, "VNQ": 0.10, "XME": 0.10, "PBW": 0.10},
            "spy40_them60": {"SPY": 0.40, "QQQ": 0.15, "VNQ": 0.15, "XME": 0.15, "PBW": 0.15},
        }
        for tag, w in frontier.items():
            run_hybrid(f"HYB_{tag}_GFC", "2007-01-03", "2018-01-02", w, f"nova_hyb_{tag}_gfc.db")
            run_hybrid(f"HYB_{tag}_INS", "2018-01-02", "2026-06-01", w, f"nova_hyb_{tag}_ins.db")
    elif mode == "corpus":
        # STEP 2: generate a deep, regime-diverse parent training corpus across all 4
        # books on the finalized config (2007-2026: GFC + COVID + bull/bear). Allocation
        # books use long-history PROXIES for the young Acc funds (regime depth); GIA trades
        # its real US names; Forex its pairs. Layer 3 = NeutralAuditor (too slow live for
        # thousands of cycles; the live cron adds real Ollama audits). Then export JSONL.
        isa_px = ["SPY", "QQQ", "SOXX", "XME", "GLD"]           # ISA growth-allocation proxies
        sipp_px = ["GLD", "SPY", "AGG", "QQQ", "XME", "PBW"]    # SIPP diversified proxies
        books = load_books("portfolio.yaml")
        out = []
        for b in books:
            if b.book_id == "ibkr_isa_equity":
                out.append(dataclasses.replace(b, universe=isa_px))
            elif b.book_id == "ibkr_sipp_equity":
                out.append(dataclasses.replace(b, universe=sipp_px))
            else:
                out.append(b)
        led = run_replay(pd.Timestamp("2007-01-03"), pd.Timestamp("2026-06-01"),
                         db_path=_fresh("nova_corpus.db"), step_days=1, exec_threshold=EXEC,
                         adapters=[EquityAdapter(), FxAdapter(), AllocationAdapter()],
                         books=out, do_report=True)
        n = led.export_training_jsonl("nova_training_corpus.jsonl")
        print(f"\n>>> CORPUS exported: {n} records -> nova_training_corpus.jsonl")
        for b in out:
            s = led.training_samples(b.book_id)
            acted = sum(1 for x in s if x["acted"])
            lab = sum(1 for x in s if x.get("realized_pnl") is not None)
            print(f"  {b.book_id:22} records={len(s):6} acted={acted:5} outcome_labelled={lab:5}")
        led.close()
    elif mode == "isa_alloc":
        # Thesis: run the ISA as a low-turnover regime-gated GROWTH allocation (like the
        # enriched SIPP, growth-tilted) instead of the choppy tactical scanner. Growth
        # core + gold crash-diversifier, long-history proxies, curve-validated both windows.
        g = ["SPY", "QQQ", "SOXX", "XME", "GLD"]
        run_alloc("ibkr_isa_equity", "ISA_ALLOC_GFC", "2007-01-03", "2018-01-02", g, "nova_isaalloc_gfc.db")
        run_alloc("ibkr_isa_equity", "ISA_ALLOC_INS", "2018-01-02", "2026-06-01", g, "nova_isaalloc_ins.db")
    elif mode == "fx_tsmom":
        # Forex re-think: 12-month time-series momentum vs the failed EMA/ADX trend.
        run_fx("FX_TSMOM_GFC", "2007-01-03", "2018-01-02", _FxTsmom(), "nova_fxtsmom_gfc.db")
        run_fx("FX_TSMOM_INS", "2018-01-02", "2026-06-01", _FxTsmom(), "nova_fxtsmom_ins.db")
    elif mode == "gia_alloc":
        # GIA reworked to aggressive US-growth allocation: validate via proxies (current,
        # leakage-free features post-bugfix). Aggressive US growth + gold crash-diversifier.
        g = ["QQQ", "SOXX", "SPY", "GLD"]
        run_alloc("ibkr_gia_equity", "GIA_ALLOC_GFC", "2007-01-03", "2018-01-02", g, "nova_giaalloc_gfc.db")
        run_alloc("ibkr_gia_equity", "GIA_ALLOC_INS", "2018-01-02", "2026-06-01", g, "nova_giaalloc_ins.db")
    elif mode == "modern":
        # ISA/GIA in-sample on the NEW canonical per-book universes (read ISA/GIA result).
        run_canon("MODERN_INS", "2018-01-02", "2026-06-01", ["VWRL.L"], "nova_modern_ins.db")
        # Enriched diversified SIPP via long-history proxies (gold/global/income + thematic):
        enriched = ["GLD", "SPY", "AGG", "QQQ", "XME", "PBW"]
        run_enriched("ENRICHED_GFC", "2007-01-03", "2018-01-02", enriched, "nova_enriched_gfc.db")
        run_enriched("ENRICHED_INS", "2018-01-02", "2026-06-01", enriched, "nova_enriched_ins.db")
    elif mode == "sortino":
        for v in ["trail", "crash"]:
            run_sortino(f"GFC_{v}", "2007-01-03", "2018-01-02", v,
                        f"nova_sortino_{v}_gfc.db", ["SPY"])
            run_sortino(f"INS_{v}", "2018-01-02", "2026-06-01", v,
                        f"nova_sortino_{v}_ins.db", ["VWRL.L"])
    print(">>> DONE", flush=True)
