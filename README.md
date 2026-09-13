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
fraud_cost.py                cost model (test-driven)
preprocessing.py             feature prep and splitting (test-driven)
tests/                       11 tests, every expectation hand-computed
notebooks/                   smoke test
docs/PLAN.md                 implementation plan (consensus-reviewed)
.github/workflows/tests.yml  CI: pytest on every push and PR
```

## Running it

### Docker (recommended)

```bash
./run.sh          # build, start, wait for healthy, open JupyterLab
./run.sh test     # run the test suite inside the container
./run.sh logs     # follow logs
./run.sh stop     # stop and remove
```

`run.sh` prints the URL with the token. On first run it generates a random
192-bit token into `.env` (gitignored) — no token is committed to this repo.
Override with `JUPYTER_TOKEN=... ./run.sh`.

`notebooks/00_cost_model_demo.ipynb` is a smoke test — run all cells to confirm
the container is wired up correctly.

**Security:** the port is bound to `127.0.0.1` only, the container runs as a
non-root user (uid 1001), and the token is random per machine. Do **not** add
`--ServerApp.allow_origin=*` — it buys nothing (the browser is same-origin) and
disables the CORS protection that stops a page you visit from driving the
kernel, which executes arbitrary Python. Loopback binding does not help there,
because the request originates from your own browser.

### Without Docker

The container is the canonical environment — `./run.sh test` is the reliable way
to run the suite. If you do go local, **use Python 3.11** to match it; on older
versions pip may fall back to building scikit-learn from source, which takes a
very long time on Apple Silicon.

```bash
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m pytest tests/ -v
```

## Status

- [x] Cost model — `total_cost`, `cost_curve`, `policy_e_predict`, `optimal_threshold`, `undo_class_weight`, `best_amount_baseline`
- [ ] EDA
- [~] Preprocessing — `hour_of_day`, `cyclic_encode_hour`, `stratified_split_60_20_20` done; scaling pending the dataset
- [ ] Model matrix (≥3 models)
- [ ] Evaluation & error analysis
- [ ] Report + slides
