# Step 4–6 Results (test set, 56,962 rows, 98 frauds, €10,644.93 of fraud)

Pre-registered champion: **xgb/balanced**, declared on validation before any
test scoring — see `artifacts/preregistration.json`.

## 1. Machine learning earns its keep

| Policy | Test cost | vs doing nothing |
|---|---|---|
| Flag everything | €170,886.00 | 16× worse |
| **No-ML: review Amount ≥ €549** | **€12,398.63** | **worse than nothing** |
| Flag nothing | €10,644.93 | — |
| logreg/none | €2,231.31 | −79% |
| rf/none | €2,453.93 | −77% |
| **xgb/balanced (champion)** | **€2,223.93** | **−79%** |

The no-ML baseline is the important row: reviewing every transaction above €549
costs **more than ignoring fraud entirely**. Without that comparison the project
could not claim ML was necessary. With it, the claim is established.

## 2. …but no winner can be named

Paired bootstrap, 1,000 class-stratified replicates, all models scored on the
same resample each time:

| Model | Mean cost | 95% CI |
|---|---|---|
| xgb/balanced | €2,234.70 | [€529.92, €4,413.90] |
| logreg/none | €2,241.36 | [€535.84, €4,444.43] |
| rf/none | €2,474.28 | [€697.00, €4,605.12] |

Paired differences against the pre-registered champion:

| Comparison | Mean Δ | 95% CI | Verdict |
|---|---|---|---|
| logreg/none − champion | €6.67 | [−€67.41, €93.32] | **not significant** |
| rf/none − champion | €239.59 | [−€145.01, €928.43] | **not significant** |

The champion beats Logistic Regression in **53.3% of replicates** — a coin flip.

This is exactly what the plan predicted. With 98 test frauds and a heavy-tailed
cost, the effective sample size is **n_eff = 18.1**, so a €6.67 gap on a €2,200
estimate is far inside the noise. R4 pre-committed to reporting this as a
finding rather than dressing it up as a win.

**The defensible claim is "all three models are equivalent and all beat every
baseline", not "XGBoost won".**

## 3. Policy A vs Policy E

Policy A = global threshold tuned on validation. Policy E = `p × Amount > c_review`,
no tuned parameter. Reweighted arms are prior-shift corrected first.

| Model | Policy A | Policy E | E − A (paired bootstrap) |
|---|---|---|---|
| xgb/balanced | €2,223.93 | €2,316.64 | +€100.95 [−201.75, 570.40] not sig. |
| rf/none | €2,453.93 | €2,415.60 | −€16.52 [−1586.75, 935.74] not sig. |
| logreg/none | €2,231.31 | €2,431.08 | +€199.23 [132.51, 266.36] **significant, E worse** |

**Policy E did not win.** It is indistinguishable from a tuned threshold for two
models and significantly worse for Logistic Regression.

The honest framing: Policy E carries **zero free parameters** while Policy A's
threshold is fitted on validation. Matching a tuned threshold with no tuning
(xgb, rf) is a real observation — but it is not the "E beats A" result the plan
hoped for, and the report should say so plainly.

**Open question.** Aggregate calibration is good for all three models (mean
predicted p ≈ the 0.00172 base rate), so simple miscalibration does **not**
explain it. Policy E depends on `p` being accurate at the *per-transaction*
thresholds `c_review/Amount`, which aggregate calibration does not guarantee.
Tail calibration is the natural next check — not yet run, and it should not be
asserted as the cause until it is.

## 4. Validation results (all 6 configurations)

| Config | Val cost | PR-AUC | Alert rate | Fit |
|---|---|---|---|---|
| logreg/none | €3,419.35 | 0.7142 | 0.160% | 0.2s |
| logreg/balanced | €3,561.31 | 0.6686 | 0.186% | 0.3s |
| rf/none | €3,382.76 | 0.7992 | 0.139% | 5.8s |
| rf/balanced | €3,390.00 | 0.7981 | 0.144% | 3.6s |
| xgb/none | €3,160.05 | 0.8200 | 0.276% | 1.0s |
| **xgb/balanced** | **€3,052.05** | **0.8228** | 0.212% | 1.1s |

Champions carried forward, one per family: xgb/balanced, rf/none, logreg/none.
