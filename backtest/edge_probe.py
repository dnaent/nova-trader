"""
Nova Engine — backtest/edge_probe.py

Phase-A (PRELIMINARY) supervised edge probe for the local-model-training scope
(research/LOCAL_MODEL_TRAINING_SCOPE.md). Asks the decisive, honest question:

    Among the trades the engine TOOK, do the 32 markers add any OUT-OF-SAMPLE
    predictive power BEYOND the regime gate?  (gate-only vs gate+markers)

Read-only: reads a corpus DB's `training_records` (acted + outcome-labelled),
builds a feature matrix from the marker snapshot, does a TIME-ORDERED 70/30 split
(no shuffle, no leakage; median-impute fit on train only), trains a gradient-boosted
classifier to predict a profitable trade (R-multiple > 0), and reports OOS AUC +
expectancy uplift vs the gate-only baseline.

HONEST CAVEAT: this uses ACTED trades only — a selection-biased, modest sample. A
near-0.5 AUC / no uplift = no learnable edge beyond regime (the likely, prior-consistent
answer). A meaningful OOS lift motivates the full unbiased probe (Phase 0 counterfactual
labelling of NOT-acted candidates first). It NEVER promotes anything — it's a measurement.

Usage:
    python -m backtest.edge_probe --db nova_corpus.db
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from core.ledger import Ledger


def _frame(samples: list[dict]) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Build (markers DataFrame, gate Series, target Series) from acted+labelled records,
    in chronological order. Target = 1 if R-multiple > 0 (profitable)."""
    rows, gate, y = [], [], []
    for s in samples:
        m = s.get("markers") or {}
        if not m:
            continue
        r = s.get("r_multiple")
        if r is None:
            pnl = s.get("realized_pnl")
            if pnl is None:
                continue
            r = float(pnl)
        rows.append({k: v for k, v in m.items() if isinstance(v, (int, float))})
        gate.append(float(s.get("gate") or 0.0))
        y.append(1 if float(r) > 0 else 0)
    X = pd.DataFrame(rows).apply(pd.to_numeric, errors="coerce")
    return X, pd.Series(gate, name="gate"), pd.Series(y, name="profitable")


def probe_book(led: Ledger, book_id: str, n_splits: int = 5) -> None:
    # HistGradientBoosting handles NaN natively (markers can be missing per record).
    from sklearn.ensemble import HistGradientBoostingClassifier as GBM
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import roc_auc_score
    samples = [s for s in led.training_samples(book_id)
               if s.get("acted") and (s.get("r_multiple") is not None or s.get("realized_pnl") is not None)]
    print(f"\n===== {book_id} =====")
    X, gate, y = _frame(samples)
    n = len(y)
    if n < 150 or y.nunique() < 2:
        print(f"  insufficient data (n={n}) — skipped")
        return
    # drop all-NaN and constant columns — a single distinct value breaks the histogram
    # binning and carries no signal anyway.
    X = X.dropna(axis=1, how="all")
    X = X[[c for c in X.columns if X[c].nunique(dropna=True) >= 2]]
    r_mult = pd.Series([float(s["r_multiple"]) if s.get("r_multiple") is not None else np.nan
                        for s in samples if s.get("markers")], name="R").reset_index(drop=True)
    print(f"  n={n}  base rate profitable={float(y.mean()):.1%}  features={X.shape[1]}  "
          f"walk-forward folds={n_splits}")

    feats = {"gate-only": pd.DataFrame({"gate": gate.values}),
             "gate+markers": X.assign(gate=gate.values)}
    aucs = {name: [] for name in feats}
    pooled_y, pooled_p, pooled_R = [], [], []
    tss = TimeSeriesSplit(n_splits=n_splits)
    for tr, te in tss.split(X):
        ytr, yte = y.iloc[tr], y.iloc[te]
        if ytr.nunique() < 2 or yte.nunique() < 2:
            continue
        for name, Xf in feats.items():
            m = GBM(random_state=42)
            m.fit(Xf.iloc[tr], ytr)
            p = m.predict_proba(Xf.iloc[te])[:, 1]
            aucs[name].append(roc_auc_score(yte, p))
            if name == "gate+markers":
                pooled_y.extend(yte.tolist()); pooled_p.extend(p.tolist())
                pooled_R.extend(r_mult.iloc[te].tolist())
    for name in feats:
        a = aucs[name]
        if a:
            print(f"  {name:14} walk-forward OOS AUC: mean {np.mean(a):.3f}  "
                  f"folds [{', '.join(f'{x:.2f}' for x in a)}]")
        else:
            print(f"  {name:14} OOS AUC: n/a")
    # pooled expectancy uplift across all OOS folds
    if pooled_R:
        R = np.array(pooled_R, float); P = np.array(pooled_p, float)
        ok = ~np.isnan(R)
        R, P = R[ok], P[ok]
        if len(R):
            top = np.argsort(-P)[: len(P) // 2]
            print(f"  pooled OOS expectancy (mean R): all={R.mean():+.3f}  "
                  f"model-top-half={R[top].mean():+.3f}  uplift={R[top].mean() - R.mean():+.3f}")
    # verdict on the MEAN walk-forward AUC (robust to a lucky single split)
    if aucs["gate+markers"] and aucs["gate-only"]:
        edge = float(np.mean(aucs["gate+markers"])); base = float(np.mean(aucs["gate-only"]))
        lo = min(aucs["gate+markers"])
        robust = edge > 0.56 and (edge - base) > 0.03 and lo > 0.52
        verdict = ("MARKERS ADD ROBUST OOS EDGE — worth Phase 0 (counterfactual) + Phase B"
                   if robust else
                   "NO robust OOS edge beyond the regime gate (prior-consistent)")
        print(f"  >>> {verdict}  (mean AUC {edge:.3f} vs gate-only {base:.3f}, worst fold {lo:.2f})")


def main() -> None:
    p = argparse.ArgumentParser(description="Preliminary supervised edge probe (read-only).")
    p.add_argument("--db", default="nova_corpus.db", help="corpus DB with training_records")
    p.add_argument("--books", nargs="*",
                   default=["ibkr_gia_equity", "ibkr_forex_margin"],
                   help="books to probe (feature-rich tactical books)")
    args = p.parse_args()
    print("PRELIMINARY EDGE PROBE (acted-only, selection-biased — exploratory, not decisive)")
    led = Ledger(args.db)
    try:
        for b in args.books:
            probe_book(led, b)
    finally:
        led.close()
    print("\nNOTE: acted-only sample. A no-edge result is prior-consistent (the edge is the "
          "regime gate). A positive result motivates Phase 0 (counterfactual labelling).")


if __name__ == "__main__":
    main()
