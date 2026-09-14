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

The CSV is **not** committed (144MB, gitignored). Fetch it into `data/`:

```bash
curl -sL -H "Authorization: Bearer $KAGGLE_TOKEN" \
  https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud \
  -o data/cc.zip && unzip -o data/cc.zip -d data/ && rm data/cc.zip
```

A copy without the `Time` column is also on OpenML (`data_id=1597`) and needs no
credentials — but `Time` is required for `hour_of_day` and the temporal check.

### Verified dataset facts

284,807 rows · 492 frauds (0.173%) · 31 columns · 0 nulls · `Time` spans 48.0 h.

**42% of frauds (205 of 492) are worth less than the €3 review fee**, and 27 are
exactly €0 — so a cost-optimal policy ignores nearly half of all fraud on
purpose. Fraud is *bimodal in cost terms*: median €9.25 (below the legit median
of €22.00) but mean €122.21 (above legit's €88.29), driven by a heavy tail.

## Layout

```
paths.py                     resolves where the submission bundle lives
fraud_cost.py                cost model (test-driven)
preprocessing.py             feature prep and splitting (test-driven)
modeling.py                  champion selection + pre-registration guard
run_model_matrix.py          fit 6 configs → pre-register → only then score test
analyse_results.py           baselines, Policy A vs E, paired bootstrap
verify_results.py            recompute every headline number from raw arrays
verify_calibration.py        recompute the tail-calibration numbers in §5.7
make_figures.py              all 14 report/slide figures (300 dpi)
demo.py                      one-command walkthrough — no 144MB CSV needed
tests/                       42 tests, every expectation hand-computed
notebooks/                   cost demo · EDA · error analysis · calibration
docs/PLAN.md                 implementation plan (consensus-reviewed)
docs/AUDIT.md                independent audit of this project
../08-Nop-bai/               the assembled submission bundle (outside this repo)
.github/workflows/tests.yml  CI: pytest on every push and PR
```

## Running it

### Docker (recommended)

```bash
./run.sh          # build, start, wait for healthy, open JupyterLab
./run.sh demo     # print the whole result story to the terminal
./run.sh test     # run the test suite inside the container
./run.sh verify   # recompute every headline number from the raw arrays
./run.sh logs     # follow logs
./run.sh stop     # stop and remove
```

`./run.sh demo` is the fastest way to see what this project concluded. It reads
only the stored probability arrays, so it runs on a machine that never
downloaded the dataset, and it recomputes every figure it prints rather than
reciting one:

```bash
./run.sh demo                    # cost model → policy rule → results → baselines
./run.sh demo --score 0.02 1500  # score one transaction under both policies
./run.sh demo --quick            # skip the 1,000-replicate bootstrap
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
rm -rf .venv                 # any pre-existing .venv here is a stale stub
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
PYTHONPATH=. ./.venv/bin/python -m pytest tests/ -v
```

`PYTHONPATH=.` matters: the empty root `conftest.py` is what puts the repo on
`sys.path` under pytest, and the container sets `PYTHONPATH=/work` for
everything else.

## Status

- [x] Cost model — `total_cost`, `cost_curve`, `policy_e_predict`, `optimal_threshold`, `undo_class_weight`, `best_amount_baseline`
- [x] EDA — `notebooks/01_eda.ipynb`, all cells execute clean
- [x] Preprocessing — `hour_of_day`, `cyclic_encode_hour`, `stratified_split_60_20_20`, scaler fit on train only (asserted)
- [x] Model matrix — 3 families × 2 imbalance arms, champion pre-registered before test was scored
- [x] Evaluation & error analysis — baselines, paired bootstrap, calibration, `notebooks/02`–`03`
- [x] Report + slides — assembled in `../08-Nop-bai/` (a deliverable, deliberately not in git)
- [ ] **Cut the deck to ≤15 min** — it currently runs ~17–21 min against a hard cap;
      plan at the top of `../08-Nop-bai/02-Slide/Kich-ban-thuyet-trinh.md`, guarded by an
      xfail in `tests/test_submission.py`

### Headline result

| | |
|---|---|
| Champion (pre-registered `2026-09-13`) | `xgb/balanced` |
| Test cost | **€2,223.93** — 79% below doing nothing |
| Best no-ML rule | €12,398.63 — *worse than doing nothing* |
| Can a winner be named? | **No.** €6.67 gap, CI spans 0, champion wins 53.3% of replicates |

The last row is the finding, not a failure: with 98 test frauds and a heavy-tailed
cost the effective sample size is 18.1. See `docs/RESULTS.md`.
