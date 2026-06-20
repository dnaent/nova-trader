"""
Nova Engine — backtest/fx_intraday_probe.py

Forex intraday Phase-2 PROBE (research/INTRADAY_FX_TIMING_SCOPE.md). The daily FX
signals had no edge (EMA/ADX + TSMOM both failed on corrected features); the thesis is
that FX's edge is INTRADAY (session / time-of-day). This probe answers, cheaply and
honestly, BEFORE building any intraday execution engine:

  A. Does FX hourly data show systematic SESSION / DAY-OF-WEEK structure at all?
  B. Does the canonical intraday FX strategy — the ASIAN-RANGE BREAKOUT — have an edge
     NET OF REALISTIC COSTS across the majors?

DISCIPLINE (this is offline research, not a live change):
  * Costs are charged (a 2-pip round-trip ~ 0.02%) — an intraday "edge" that dies on
    costs is not an edge.
  * Look for ROBUST, cross-pair patterns with a plausible mechanism — NOT cherry-picked
    cells (6 pairs x 5 sessions x 5 days = many cells; some look great by chance).
  * History is only ~2.75y (yfinance 1h cap) — recent-window only, NO crash stress test.
  ⇒ Bar to proceed to the (expensive) Phase-3 intraday engine: a clear, consistent,
    cost-surviving edge. Otherwise the honest call is to ABANDON FX.

Run: python -m backtest.fx_intraday_probe
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X"]
COST = 0.0002            # ~2-pip round-trip on a major, as a fraction
SESSIONS = {"Asia": (0, 7), "London": (7, 12), "Overlap": (12, 16), "NY": (16, 21)}


def _hourly(pair: str) -> pd.DataFrame:
    import yfinance as yf
    h = yf.Ticker(pair).history(period="730d", interval="1h")
    if h is None or h.empty:
        return pd.DataFrame()
    h = h[["Open", "High", "Low", "Close"]].copy()
    idx = h.index
    h.index = (idx.tz_convert("UTC") if idx.tz is not None else idx.tz_localize("UTC"))
    return h


def _session(hour: int) -> str:
    for name, (lo, hi) in SESSIONS.items():
        if lo <= hour < hi:
            return name
    return "Off"


# --------------------------------------------------------------------------- #
# A. Session / day-of-week return structure
# --------------------------------------------------------------------------- #
def structure(frames: dict) -> None:
    print("\n========== A. SESSION / DAY-OF-WEEK STRUCTURE (hourly log returns) ==========")
    rows = []
    for pair, h in frames.items():
        r = np.log(h["Close"]).diff()
        df = pd.DataFrame({"r": r})
        df["session"] = [ _session(t.hour) for t in h.index ]
        df["dow"] = h.index.dayofweek
        df["pair"] = pair
        rows.append(df.dropna())
    allr = pd.concat(rows)

    def _tab(by):
        g = allr.groupby(by)["r"]
        # annualised Sharpe of the hourly returns within each bucket (~6000 trading hrs/yr)
        sh = g.mean() / g.std() * np.sqrt(6000)
        return pd.DataFrame({"mean_bp": g.mean() * 1e4, "sharpe_ann": sh, "n": g.size()})

    print("\n-- by SESSION (UTC), pooled across pairs --")
    print(_tab("session").round(3).to_string())
    print("\n-- by DAY-OF-WEEK (0=Mon..4=Fri) --")
    print(_tab("dow").round(3).to_string())
    print("\n(mean_bp = mean hourly return in basis points; ~0 and |Sharpe|<~0.5 => no exploitable drift)")


# --------------------------------------------------------------------------- #
# B. Asian-range breakout (the canonical intraday FX strategy)
# --------------------------------------------------------------------------- #
def asian_breakout(frames: dict) -> None:
    print("\n========== B. ASIAN-RANGE BREAKOUT (London/overlap breakout, net of costs) ==========")
    print("Rule: range = Asian-session (00-07 UTC) high/low; during 07-16 UTC go long on a")
    print("break above the Asian high / short below the low (first break only); exit 21:00 UTC.\n")
    agg = []
    for pair, h in frames.items():
        trades = []
        for day, g in h.groupby(h.index.date):
            asia = g[(g.index.hour >= 0) & (g.index.hour < 7)]
            sess = g[(g.index.hour >= 7) & (g.index.hour < 21)]
            if len(asia) < 3 or len(sess) < 3:
                continue
            hi, lo = asia["High"].max(), asia["Low"].min()
            brk = sess[(sess.index.hour >= 7) & (sess.index.hour < 16)]
            entry = side = None
            for t, row in brk.iterrows():
                if row["High"] > hi:
                    entry, side = hi, 1; break
                if row["Low"] < lo:
                    entry, side = lo, -1; break
            if entry is None:
                continue
            exit_px = sess.iloc[-1]["Close"]
            ret = side * (exit_px / entry - 1.0) - COST
            trades.append(ret)
        if len(trades) < 30:
            print(f"  {pair:9} insufficient trades ({len(trades)})"); continue
        tr = np.array(trades)
        wr = float((tr > 0).mean())
        sharpe = float(tr.mean() / tr.std() * np.sqrt(252)) if tr.std() > 0 else 0.0
        pf = float(tr[tr > 0].sum() / -tr[tr < 0].sum()) if (tr < 0).any() else float("inf")
        print(f"  {pair:9} trades={len(tr):4}  win={wr:5.1%}  mean={tr.mean()*1e4:+6.1f}bp  "
              f"PF={pf:4.2f}  Sharpe={sharpe:+5.2f}  total={tr.sum()*100:+6.1f}%")
        agg.append(tr)
    if agg:
        a = np.concatenate(agg)
        sh = a.mean() / a.std() * np.sqrt(252) if a.std() > 0 else 0.0
        pf = a[a > 0].sum() / -a[a < 0].sum() if (a < 0).any() else float("inf")
        print(f"\n  ALL-PAIRS  trades={len(a)}  win={ (a>0).mean():.1%}  mean={a.mean()*1e4:+.1f}bp  "
              f"PF={pf:.2f}  Sharpe={sh:+.2f}")
        verdict = ("EDGE WORTH PHASE 3" if (sh > 0.7 and pf > 1.2 and a.mean() > 0)
                   else "NO cost-surviving edge — lean ABANDON (per the high-bar discipline)")
        print(f"  >>> {verdict}")


def session_momentum(frames: dict) -> None:
    """Cross-session momentum: at London open (07 UTC), trade in the direction of the
    Asian-session return (long if Asia up, short if down); exit 16 UTC. Its inverse is
    mean-reversion, so a clearly-negative result here means BOTH directions fail on costs
    (no exploitable cross-session autocorrelation)."""
    print("\n========== C. SESSION MOMENTUM (Asia->London continuation, net of costs) ==========")
    agg, raw_agg = [], []
    for pair, h in frames.items():
        trades, raws = [], []
        for day, g in h.groupby(h.index.date):
            asia = g[(g.index.hour >= 0) & (g.index.hour < 7)]
            lon = g[(g.index.hour >= 7) & (g.index.hour < 16)]
            if len(asia) < 3 or len(lon) < 3:
                continue
            asia_ret = asia["Close"].iloc[-1] / asia["Open"].iloc[0] - 1.0
            if asia_ret == 0:
                continue
            side = 1 if asia_ret > 0 else -1
            lon_ret = side * (lon["Close"].iloc[-1] / lon["Open"].iloc[0] - 1.0)
            raws.append(lon_ret); trades.append(lon_ret - COST)
        if len(trades) < 30:
            continue
        tr = np.array(trades)
        sh = float(tr.mean() / tr.std() * np.sqrt(252)) if tr.std() > 0 else 0.0
        print(f"  {pair:9} trades={len(tr):4}  win={(tr>0).mean():5.1%}  net={tr.mean()*1e4:+6.1f}bp  "
              f"raw(pre-cost)={np.mean(raws)*1e4:+6.1f}bp  Sharpe={sh:+5.2f}")
        agg.append(tr); raw_agg.append(np.array(raws))
    if agg:
        a = np.concatenate(agg); raw = np.concatenate(raw_agg)
        sh = a.mean() / a.std() * np.sqrt(252) if a.std() > 0 else 0.0
        print(f"\n  ALL-PAIRS  net mean={a.mean()*1e4:+.1f}bp  raw mean={raw.mean()*1e4:+.1f}bp  Sharpe={sh:+.2f}")
        print(f"  >>> raw |mean| {abs(raw.mean())*1e4:.1f}bp vs ~2bp cost ⇒ "
              + ("exploitable autocorrelation" if abs(raw.mean())*1e4 > 4 else
                 "no exploitable cross-session autocorrelation (both momentum & its inverse die on cost)"))


def main() -> None:
    print("Fetching ~2.75y hourly data for the FX majors (yfinance)...")
    frames = {}
    for p in PAIRS:
        h = _hourly(p)
        if not h.empty:
            frames[p] = h
    print(f"loaded {len(frames)}/{len(PAIRS)} pairs")
    if not frames:
        print("no data"); return
    structure(frames)
    asian_breakout(frames)
    session_momentum(frames)
    print("\nCAVEATS: ~2.75y only (no crash stress test); costs charged at 2pip; beware "
          "data-mining across many session/day cells. Proceed to Phase 3 ONLY on a clear, "
          "consistent, cost-surviving edge.")


if __name__ == "__main__":
    main()
