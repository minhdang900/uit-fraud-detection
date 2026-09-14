"""Recompute the calibration numbers the report quotes, from stored arrays.

`notebooks/03_calibration.ipynb` is shipped with its outputs cleared, so the
figures it once printed cannot be audited from the file. This module recomputes
them with the notebook's own binning, so every calibration number in the report
has a one-line source.

    python3 verify_calibration.py
"""
from pathlib import Path

import numpy as np

import paths
import pandas as pd

from fraud_cost import undo_class_weight

C_REVIEW = 3.0
ROOT = Path(__file__).resolve().parent
MODELS = ["xgb/balanced", "rf/none", "logreg/none"]


def _posterior(arr, y_ref, key):
    """The probability Policy E actually consumes (prior-shift corrected)."""
    p = arr[key]
    if key.endswith("/balanced"):
        return undo_class_weight(p, (y_ref == 0).sum() / (y_ref == 1).sum())
    return p


def reproduce_calibration(artifacts_dir=None, c_review=C_REVIEW):
    art = Path(artifacts_dir) if artifacts_dir else paths.artifacts_dir()
    te, va = np.load(art / "test_probabilities.npz"), np.load(art / "val_probabilities.npz")
    y, amt, yva = te["y"], te["amounts"], va["y"]
    post = {k: _posterior(te, yva, k) for k in MODELS}

    nonzero = amt > 0
    t_i = c_review / amt[nonzero]                      # Policy E's per-transaction threshold
    deciles = pd.qcut(amt[nonzero], 10, duplicates="drop")

    out = {"aggregate": {}, "decile_range": {}, "boundary": {}}
    every_decile_ratio = []
    for k in MODELS:
        p, yy = post[k][nonzero], y[nonzero]
        out["aggregate"][k] = float(post[k].mean() / y.mean())

        ratios = [g.p.mean() / g.yy.mean()
                  for _, g in pd.DataFrame({"p": p, "yy": yy, "d": deciles}).groupby("d", observed=True)
                  if g.yy.mean() > 0]
        out["decile_range"][k] = (float(min(ratios)), float(max(ratios)))
        every_decile_ratio += ratios

        near = (p / t_i >= 1 / 3) & (p / t_i <= 3)     # within 3x of its own threshold
        obs = yy[near].mean() if near.sum() else float("nan")
        out["boundary"][k] = {
            "n": int(near.sum()), "n_fraud": int(yy[near].sum()),
            "ratio": float(p[near].mean() / obs) if obs > 0 else float("nan"),
        }
    out["decile_range_all_models"] = (float(min(every_decile_ratio)),
                                      float(max(every_decile_ratio)))
    return out


if __name__ == "__main__":
    r = reproduce_calibration()
    print("Aggregate calibration ratio (mean p / base rate):")
    for k, v in r["aggregate"].items():
        print(f"  {k:<14} {v:.2f}x")
    print("\nRatio by Amount decile (= by Policy E's own threshold):")
    for k, (lo, hi) in r["decile_range"].items():
        print(f"  {k:<14} {lo:.2f}x .. {hi:.2f}x")
    lo, hi = r["decile_range_all_models"]
    print(f"  {'ALL MODELS':<14} {lo:.2f}x .. {hi:.2f}x")
    print("\nAt each model's own decision boundary (1/3 <= p/t_i <= 3):")
    for k, v in r["boundary"].items():
        print(f"  {k:<14} ratio {v['ratio']:.2f}x   n={v['n']}  (n_fraud={v['n_fraud']})")
