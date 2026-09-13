# Credit Card Fraud Detection — Cost-Based Model Selection

Đồ án môn học **CS114 – Machine Learning**, UIT.

## What makes this different

On this dataset a model reaches **99.8% accuracy by predicting "not fraud" every time**.
Accuracy, and even F1, are therefore poor guides to which model is actually useful.

This project selects models by **expected monetary cost** instead:

```
TotalCost = c_review × (TP + FP) + Σ_{i ∈ FN} Amount_i
```

Read plainly: *review cost × alerts raised, plus money lost to fraud that slipped through.*

| Outcome | Cost | Why |
|---|---|---|
| TP (fraud caught) | `c_review` | The analyst's time is spent **before** the label is known |
| FN (fraud missed) | `Amount_i` | The full transaction value is lost |
| FP (legit flagged) | `c_review` | Reviewed, plus customer friction |
| TN | 0 | No action |

## The headline rule

Minimising that objective does **not** give a single global threshold. It gives a
per-transaction rule:

```
alert  iff  p_i × Amount_i > c_review
```

Expected loss of letting it through, versus the cost of looking. A global threshold is
the special case where every transaction is assigned one constant amount `Ā = c_review/t*`.

Consequence — and the point of the project:

| p | Amount | p × Amount | alert? |
|---|---|---|---|
| 0.01 | €1000 | €10.00 | ✅ low probability, real money |
| 0.90 | €1 | €0.90 | ❌ high probability, trivial money |

A global threshold does the exact opposite on those two rows.

## Dataset

[Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
(ULB / Kaggle) — ~284,807 transactions, ~492 frauds (**0.172%**), 30 features.
`V1`–`V28` are anonymised PCA components; `Time` and `Amount` are raw.
`Amount` is in **EUR** (European cardholders, September 2013).

The CSV is **not** committed. Download it via the Kaggle API.

## Layout

```
fraud_cost.py            cost model (test-driven)
tests/test_fraud_cost.py 8 tests, every expectation hand-computed in its docstring
docs/PLAN.md             implementation plan (consensus-reviewed)
```

## Running the tests

```bash
python3 -m venv .venv
./.venv/bin/pip install numpy pytest
./.venv/bin/python -m pytest tests/ -v
```

## Status

- [x] Cost model — `total_cost`, `cost_curve`, `policy_e_predict`, `optimal_threshold`, `undo_class_weight`, `best_amount_baseline`
- [ ] EDA
- [ ] Preprocessing
- [ ] Model matrix (≥3 models)
- [ ] Evaluation & error analysis
- [ ] Report + slides
