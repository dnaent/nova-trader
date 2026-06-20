"""
Nova Engine — backtest/fx_xsectional_probe.py

Forex alternative-route probe: CROSS-SECTIONAL / DOLLAR-NEUTRAL momentum. Everything
that failed (daily trend, intraday, risk-proxy) was DIRECTIONAL and risk-on-correlated
— long-FX bets that crater in risk-off while the gate lags. A cross-sectional long-short
book ranks currencies AGAINST EACH OTHER (long strongest vs USD, short weakest), so it's
~dollar-neutral / market-neutral: no directional risk-on exposure ⇒ should sidestep the
crash-lag AND the equity-correlation that killed the rest. This is the academic gold
standard for systematic FX (here: the momentum leg only — price-only, no FRED needed).

Decisive questions: (1) positive Sharpe net of costs? (2) LOW correlation to equities
(SPY)? — i.e. does it actually DIVERSIFY, which is the only reason to add FX at all.

Run: python -m backtest.fx_xsectional_probe
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# foreign-vs-USD: pairs quoted USD-per-foreign (EURUSD) use price as-is; USDxxx pairs
# (JPY/CAD/CHF per USD) are inverted so a RISE always = the foreign currency strengthening.
PAIRS = {"EURUSD=X": True, "GBPUSD=X": True, "AUDUSD=X": True,
         "USDJPY=X": False, "USDCAD=X": False, "USDCHF=X": False}
LOOKBACK_M = 12          # 12-month momentum
COST = 0.0002            # 2-pip round-trip per leg traded


def _foreign_vs_usd(pair: str, invert: bool) -> pd.Series:
    import yfinance as yf
    h = yf.Ticker(pair).history(start="2006-01-01", interval="1d")
    if h is None or h.empty:
        return pd.Series(dtype=float)
    c = h["Close"].astype(float)
    c.index = c.index.tz_localize(None) if c.index.tz is not None else c.index
    return (1.0 / c) if invert else c


def main() -> None:
    print("Cross-sectional dollar-neutral FX momentum (long top-2 / short bottom-2, monthly)\n")
    # monthly close per currency (foreign vs USD)
    series = {}
    for p, asis in PAIRS.items():
        s = _foreign_vs_usd(p, not asis)
        if not s.empty:
            series[p] = s.resample("ME").last()
    px = pd.DataFrame(series).dropna()
    spy = (__import__("yfinance").Ticker("SPY").history(start="2006-01-01", interval="1d")
           ["Close"].astype(float))
    spy.index = spy.index.tz_localize(None) if spy.index.tz is not None else spy.index
    spy_m = spy.resample("ME").last().reindex(px.index)

    mom = px / px.shift(LOOKBACK_M) - 1.0          # 12m momentum per currency
    fwd = px.shift(-1) / px - 1.0                   # next-month return per currency
    rows = []
    for dt in px.index[LOOKBACK_M:-1]:
        r = mom.loc[dt].dropna()
        f = fwd.loc[dt]
        if len(r) < 4:
            continue
        ranked = r.sort_values()
        shorts, longs = ranked.index[:2], ranked.index[-2:]
        ret = f[longs].mean() - f[shorts].mean() - COST * 2     # 4 legs traded ~ 2x round-trip
        rows.append((dt, ret, spy_m.pct_change().get(dt, np.nan)))
    res = pd.DataFrame(rows, columns=["date", "ret", "spy"]).dropna(subset=["ret"]).set_index("date")
    r = res["ret"]
    sharpe = r.mean() / r.std() * np.sqrt(12) if r.std() > 0 else 0.0
    cum = (1 + r).prod() - 1
    pos = (r > 0).mean()
    # max drawdown of the monthly equity curve
    eq = (1 + r).cumprod()
    dd = float((1 - eq / eq.cummax()).max() * 100)
    corr = float(r.corr(res["spy"])) if res["spy"].notna().sum() > 5 else float("nan")
    print(f"months={len(r)}  ann.Sharpe={sharpe:+.2f}  %pos={pos:.0%}  total={cum*100:+.0f}%  "
          f"maxDD={dd:.0f}%")
    print(f"correlation to SPY (monthly): {corr:+.2f}   "
          f"({'GENUINELY DIVERSIFYING' if abs(corr) < 0.3 else 'still equity-correlated'})")
    # sub-period: does it survive 2008 + recent separately?
    for lbl, sl in [("2007-2012 (incl GFC)", r.loc[:"2012"]), ("2013-2019", r.loc["2013":"2019"]),
                    ("2020-2026", r.loc["2020":])]:
        if len(sl) > 6:
            sh = sl.mean() / sl.std() * np.sqrt(12) if sl.std() > 0 else 0.0
            print(f"   {lbl:22} Sharpe {sh:+.2f}  total {((1+sl).prod()-1)*100:+.0f}%")
    verdict = ("WORTH the full factor build (add carry+value)" if (sharpe > 0.5 and abs(corr) < 0.4)
               else "NO robust dollar-neutral edge either — FX is genuinely done")
    print(f"\n>>> {verdict}")
    print("CAVEAT: momentum leg only (no carry/value); 6 USD-majors (a fuller book needs 10+ "
          "crosses); FX factor premia have decayed post-2008. A POSITIVE+uncorrelated result "
          "motivates the bigger carry+value cross-sectional build; a negative one closes FX.")


if __name__ == "__main__":
    main()
