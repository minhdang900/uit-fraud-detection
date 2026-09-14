"""Step 5/6 post-processing: policies, baselines, paired bootstrap.

Pure post-processing on the arrays saved by run_model_matrix.py -- no refits.
"""
import json
from pathlib import Path

import numpy as np

import paths

from fraud_cost import (best_amount_baseline, optimal_threshold,
                        policy_e_predict, total_cost, undo_class_weight)

ROOT = Path(__file__).resolve().parent
ART = paths.artifacts_dir()
C = 3.0
SEED = 42

te = np.load(ART / "test_probabilities.npz")
va = np.load(ART / "val_probabilities.npz")
yte, amt_te = te["y"], te["amounts"]
yva, amt_va = va["y"], va["amounts"]
prereg = json.loads((ART / "preregistration.json").read_text())
champ = prereg["declared_winner"]
keys = [k for k in te.files if k not in ("y", "amounts")]

print(f"test set: {len(yte):,} rows, {int(yte.sum())} frauds, "
      f"fraud value EUR{amt_te[yte == 1].sum():,.2f}")
print(f"pre-registered champion: {champ}\n")

# ---------------------------------------------------------------- baselines
print("=== baselines (test) ===")
flag_nothing = amt_te[yte == 1].sum()
flag_all = len(yte) * C
x_val, _ = best_amount_baseline(yva, amt_va, C)          # X chosen on VALIDATION
amt_cost = total_cost(yte, (amt_te >= x_val).astype(int), amt_te, C)
print(f"  flag nothing               EUR{flag_nothing:>10,.2f}")
print(f"  flag everything            EUR{flag_all:>10,.2f}")
print(f"  no-ML: Amount >= EUR{x_val:<6,.0f}   EUR{amt_cost:>10,.2f}   (X picked on validation)")

# ---------------------------------------------------------------- policies
print("\n=== Policy A (global threshold) vs Policy E (p x Amount > c) ===")
rows = {}
for k in keys:
    p_te = te[k]
    thr, _, _ = optimal_threshold(yva, va[k], amt_va, C)   # threshold from VAL
    a_cost = total_cost(yte, (p_te >= thr).astype(int), amt_te, C)

    # Major #3: reweighted arms inflate p; invert before Policy E.
    p_for_e = p_te
    if k.endswith("/balanced"):
        w = (yva == 0).sum() / (yva == 1).sum()
        p_for_e = undo_class_weight(p_te, w)
    e_pred = policy_e_predict(p_for_e, amt_te, C)
    e_cost = total_cost(yte, e_pred, amt_te, C)

    rows[k] = {"A": a_cost, "E": e_cost, "E_alerts": int(e_pred.sum())}
    print(f"  {k:<16} A EUR{a_cost:>9,.2f}   E EUR{e_cost:>9,.2f}   "
          f"E alerts {int(e_pred.sum()):>5}  ({e_pred.mean()*100:.3f}%)")

# ------------------------------------------------- paired bootstrap (AC-21)
print("\n=== paired bootstrap, 1000 replicates, class-stratified ===")
rng = np.random.default_rng(SEED)
pos, neg = np.flatnonzero(yte == 1), np.flatnonzero(yte == 0)
thr_map = {k: optimal_threshold(yva, va[k], amt_va, C)[0] for k in keys}

draws = {k: [] for k in keys}
for _ in range(1000):
    idx = np.concatenate([rng.choice(pos, len(pos), True),
                          rng.choice(neg, len(neg), True)])   # SAME idx for all
    for k in keys:
        draws[k].append(total_cost(yte[idx], (te[k][idx] >= thr_map[k]).astype(int),
                                   amt_te[idx], C))

champ_draws = np.array(draws[champ])
for k in keys:
    d = np.array(draws[k])
    lo, hi = np.percentile(d, [2.5, 97.5])
    print(f"  {k:<16} EUR{d.mean():>9,.2f}  95% CI [{lo:>8,.2f}, {hi:>8,.2f}]")

print("\n  paired differences vs pre-registered champion:")
for k in keys:
    if k == champ:
        continue
    diff = np.array(draws[k]) - champ_draws
    lo, hi = np.percentile(diff, [2.5, 97.5])
    sig = "SIGNIFICANT" if (lo > 0 or hi < 0) else "not significant (CI spans 0)"
    print(f"    {k:<16} - champion = EUR{diff.mean():>8,.2f}  "
          f"95% CI [{lo:>8,.2f}, {hi:>8,.2f}]  -> {sig}")
    print(f"      champion wins {100*(diff > 0).mean():.1f}% of replicates")
