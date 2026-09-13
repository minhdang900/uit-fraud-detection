"""Step 4 — model matrix (AC-8, AC-9, AC-24, AC-25).

Order matters and is enforced here:
  1. fit 3 families x 2 imbalance arms on TRAIN
  2. score VALIDATION only, rank, pick one champion per family
  3. WRITE the pre-registration to disk
  4. only then score TEST for the 3 finalists

Test is never used for selection. Artifacts land in artifacts/ so every
downstream analysis is pure post-processing on stored arrays.
"""
import json
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from fraud_cost import optimal_threshold, total_cost
from modeling import select_champion_per_family
from preprocessing import cyclic_encode_hour, hour_of_day, stratified_split_60_20_20

SEED = 42
C_REVIEW = 3.0
ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------- data
log("loading data")
df = pd.read_csv(ROOT / "data" / "creditcard.csv")
y = df.Class.values
amounts = df.Amount.values

# AC-4: raw Time dropped, replaced by cyclic hour. AC-5: log1p(Amount).
hours = hour_of_day(df.Time.values)
X = np.column_stack([
    df[[f"V{i}" for i in range(1, 29)]].values,
    np.log1p(df.Amount.values),
    cyclic_encode_hour(hours),
])
log(f"X {X.shape}, frauds {int(y.sum())}")

train, val, test = stratified_split_60_20_20(y, random_state=SEED)

# AC-6: scaler fit on TRAIN ONLY.
scaler = StandardScaler().fit(X[train])
assert scaler.n_samples_seen_ == len(train), "scaler saw more than train -- leakage"
Xtr, Xva, Xte = scaler.transform(X[train]), scaler.transform(X[val]), scaler.transform(X[test])
ytr, yva, yte = y[train], y[val], y[test]
log(f"split train={len(train)} val={len(val)} test={len(test)}")

pos_weight = (ytr == 0).sum() / (ytr == 1).sum()


def build(family, arm):
    """AC-25: every estimator carries an explicit random_state."""
    if family == "logreg":
        return LogisticRegression(
            max_iter=1000, random_state=SEED,
            class_weight="balanced" if arm == "balanced" else None)
    if family == "rf":
        return RandomForestClassifier(
            n_estimators=100, n_jobs=-1, random_state=SEED,
            class_weight="balanced" if arm == "balanced" else None)
    if family == "xgb":
        return XGBClassifier(
            tree_method="hist", eval_metric="aucpr", random_state=SEED, n_jobs=-1,
            scale_pos_weight=pos_weight if arm == "balanced" else 1.0)
    raise ValueError(family)


# ------------------------------------------- phase 1: fit + score VALIDATION
results, fitted, val_probs = [], {}, {}
for family in ["logreg", "rf", "xgb"]:
    for arm in ["none", "balanced"]:
        key = f"{family}/{arm}"
        t0 = time.time()
        model = build(family, arm).fit(Xtr, ytr)
        p_va = model.predict_proba(Xva)[:, 1]

        thr, cost, rate = optimal_threshold(yva, p_va, amounts[val], C_REVIEW)
        results.append({
            "family": family, "arm": arm, "cost": float(cost),
            "threshold": float(thr), "alert_rate": float(rate),
            "pr_auc": float(average_precision_score(yva, p_va)),
            "fit_seconds": round(time.time() - t0, 1),
        })
        fitted[key], val_probs[key] = model, p_va
        log(f"{key:<16} val cost EUR{cost:>9,.2f}  PR-AUC {results[-1]['pr_auc']:.4f}  "
            f"alert {rate*100:.3f}%  ({results[-1]['fit_seconds']}s)")

np.savez_compressed(ART / "val_probabilities.npz",
                    y=yva, amounts=amounts[val], **val_probs)

# ------------------------------------------- phase 2: pre-register champions
champions = select_champion_per_family(results)
prereg = {
    "date": str(date.today()),
    "selected_on": "validation split only; test not yet scored",
    "c_review": C_REVIEW,
    "champions": champions,
    "declared_winner": f"{champions[0]['family']}/{champions[0]['arm']}",
    "note": ("Declared BEFORE any test scoring. The headline number is this "
             "model's test cost whether or not it turns out lowest on test."),
}
(ART / "preregistration.json").write_text(json.dumps(prereg, indent=2))
log(f"PRE-REGISTERED champion: {prereg['declared_winner']} "
    f"(val cost EUR{champions[0]['cost']:,.2f})")

# ------------------------------------------- phase 3: score TEST, finalists only
test_probs, test_rows = {}, []
for c in champions:
    key = f"{c['family']}/{c['arm']}"
    p_te = fitted[key].predict_proba(Xte)[:, 1]   # first and only test scoring
    test_probs[key] = p_te

    pred = (p_te >= c["threshold"]).astype(int)
    test_rows.append({
        "family": c["family"], "arm": c["arm"],
        "val_cost": c["cost"],
        "test_cost_at_val_threshold": float(total_cost(yte, pred, amounts[test], C_REVIEW)),
        "test_pr_auc": float(average_precision_score(yte, p_te)),
        "test_alert_rate": float(pred.mean()),
    })
    log(f"{key:<16} test cost EUR{test_rows[-1]['test_cost_at_val_threshold']:>9,.2f}")

np.savez_compressed(ART / "test_probabilities.npz",
                    y=yte, amounts=amounts[test], **test_probs)
pd.DataFrame(results).to_csv(ART / "validation_results.csv", index=False)
pd.DataFrame(test_rows).to_csv(ART / "test_results.csv", index=False)
log(f"artifacts written to {ART}")
