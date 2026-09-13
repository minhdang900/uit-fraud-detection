# Plan: Cost-Based Credit Card Fraud Detection — Đồ án CS114

- **Source spec:** `.omc/specs/deep-interview-credit-card-fraud.md` (ambiguity 18%, PASSED)
- **Mode:** consensus (RALPLAN-DR short) · **Status:** `pending approval`
- **Iteration:** 3 (final) — Critic **APPROVED WITH IMPROVEMENTS**; all six new majors and ten minors applied. Changelog at the end.

---

## Requirements Summary

Team of 4–6 students, ~4 weeks, must be presentable by **course week 8** (random draw). Kaggle `mlg-ulb/creditcardfraud` (~284,807 rows, ~492 frauds, ~0.172%). Select the best fraud-detection policy by **minimizing expected monetary cost**:

```
TotalCost = c_review × (TP + FP) + Σ_{i∈FN} Amount_i
```

Deliverables: Word report (10 sections), Colab notebook, 15-minute slides. Minimum 3 models. All 8 rubric questions answered.

> **Week anchoring (was missing):** project week 1 = course week 4. The 4-week plan ends at course week 7, one week before the earliest possible draw. **Confirm this mapping with the team before starting.**

---

## RALPLAN-DR Summary

### Principles
1. **The objective function is the deliverable.** Every design choice traces to expected cost in EUR.
2. **Score the test set once; never *select* on it.** The test probability vector is computed once and may be re-analysed freely; no threshold, model, or hyperparameter is ever chosen using test outcomes.
3. **Honest uncertainty beats false precision.** Unknown parameters are swept, not guessed; inconclusive is a valid finding.
4. **Rubric coverage is non-negotiable.** All 8 questions are answered inside T1.
5. **Degrade gracefully.** Dropping T2/T3 must never break a principle or a rubric answer.

> Principle 2 was reworded in iteration 2. "Touched exactly once" was self-contradictory — the bootstrap, the `c_review` sweep, and the two-threshold comparison all legitimately re-read test predictions. The real invariant is *score once, never select*.

### Decision Drivers
1. **Week-8 risk** — presentation order is drawn at random; T1 must be complete and rehearsed before the earliest draw.
2. **Statistical fragility** — ~492 positives, and because cost is a heavy-tailed *sum*, the test set's **effective** sample size for cost is `n/(1+CV²) ≈ 18`, not 98. Every comparison must be reported with that in mind.
3. **Rubric traceability** — each of the 8 questions has an explicit home **within T1**.

> D1 and D2 pull in opposite directions (speed vs rigour). Resolution: the *policy comparison* (cheap, high-value) goes in T1; the *variance-reduction machinery* (expensive, second-order) goes in T2.

### Viable Options

**Option A — Single-split global threshold.** Tune `t` on the 20% validation split.
- ✅ Simplest to explain; threshold and evaluation share one fitted model (no transfer problem).
- ❌ ~98 validation frauds (n_eff ≈ 18) → unstable `t*`; cannot produce fold-variance evidence.

**Option B — Out-of-fold CV global threshold.** 5-fold stratified CV over train+val; pick `t*` on pooled OOF predictions.
- ✅ Selection n_eff rises ~18 → ~73; per-fold spread directly answers rubric Q6.
- ❌ 5× fits; introduces an OOF→refit score-scale shift that must be explicitly handled.

**Option C — Fixed threshold 0.5 only.**
- ✅ Trivial.
- ❌ Rejected on substance, not by appeal to principle: at 0.5 a 0.172%-positive-rate model alerts far too rarely, leaving nearly all fraud loss uncaptured. It answers Q1–Q6 but forfeits Q8 and produces no insight beyond a standard metrics table.

**Option D — Cost-sensitive training.** Pass `sample_weight = Amount` for frauds, `c_review` for legitimates, into `fit()`.
- ✅ Optimises the objective at training time; one argument in sklearn/XGBoost.
- ❌ Interacts confusingly with `class_weight` and SMOTE; harder to explain alongside thresholding. **Adopted as a T2 fourth arm, not the spine.**

**Option E — Amount-dependent decision rule.** `alert iff p_i × Amount_i > c_review`, i.e. `p_i > c_review / Amount_i`.
- ✅ **The Bayes-optimal rule for this exact objective.** Zero extra fits — one line of NumPy over an existing probability vector. Easier to present than threshold tuning: *"expected loss of letting it through is probability × amount; if that beats €3, pay the €3."*
- ❌ Requires calibrated probabilities (monotone transforms are **not** neutral here), so it promotes calibration from optional to load-bearing.

**Chosen: Option E as the headline policy + Option B as the comparison spine.** A global threshold is the special case of Option E where every Amount is replaced by **some constant** `Ā` with `t = c_review/Ā` — not necessarily the mean. **Report the implied `Ā = c_review/t*`**: sharper than the mean claim, and correct. **Option A is the T1 fallback for threshold selection.**

> Iteration 1 chose B alone. Both reviewers independently identified that the cost-optimal rule for this objective is *not* a global threshold, making the original choice a provably suboptimal restriction of its own objective.

---

## Scope Tiers

| Tier | Contents | Drop cost |
|---|---|---|
| **T1 — Must** (complete + rehearsed by **end of week 3**; every T1 item is post-processing on cached arrays, so none of it requires week 4) | EDA · preprocessing · 3 models (one per family) at defaults · **3 baselines incl. no-ML `Amount > X`** · **Policy A (global threshold, Option A selection) vs Policy E (amount-dependent)** · Accuracy/P/R/F1/**PR-AUC** · confusion matrices · **`c_review` €1–€20 sweep** · **2-arm imbalance comparison (none vs `class_weight`)** · error analysis by Amount decile · train-vs-val table · **reliability curve (AC-10a)** | — |
| **T2 — Should** | Option B out-of-fold threshold selection + per-fold spread · 3rd imbalance arm (SMOTE) · Option D cost-sensitive training · recalibration AC-10b · paired bootstrap CI | Falls back to Option A; Q6 answered by train-vs-val table alone |
| **T3 — Nice** | Temporal day1→day2 check · hyperparameter tuning · nested CV for finalists | Drop entirely, no rubric gap |

> **Iteration 2 change (Critic C1):** the `c_review` sweep and the 2-arm imbalance comparison moved T2 → T1, because rubric Q8 ("what affects results?") previously had **no T1 coverage** — its three mapped criteria were all outside T1, falsifying the tier table's central claim. Both additions are near-free: the sweep is a loop over a cached probability vector with zero refits, and the second imbalance arm is one argument.

### Rubric coverage trace (verified per question, T1 only)

| # | Question | Answered in T1 by |
|---|---|---|
| 1 | Model nào tốt nhất? | Cost table + `c_review` sweep (both now T1) |
| 2 | Chênh lệch bao nhiêu? | Δcost in EUR between champion and runner-up |
| 3 | Precision/Recall/F1 | Metrics table incl. **PR-AUC** |
| 4 | Model hay nhầm class nào? | Confusion matrices |
| 5 | Phân tích lỗi | Missed-fraud-by-Amount-decile chart |
| 6 | Train vs validation — overfitting? | Train-vs-val table on the **original 20% split** |
| 7 | Model nào phù hợp với dữ liệu? | Train-vs-val + Policy A vs E comparison |
| 8 | Điều gì ảnh hưởng đến kết quả? | **`c_review` sweep + imbalance 2-arm comparison** ✅ *(was uncovered)* |

---

## Acceptance Criteria

Inherits AC-1 … AC-20 from the spec, amended:

- **AC-4 (amended)** — raw `Time` is **dropped** as a feature (not merely scaled), replaced by cyclically-encoded `hour_of_day`; rationale is leakage of fraud-burst position under a random split.
- **AC-7 (retiered to T3)** — the temporal split is a distribution-shift check, not required for any T1 rubric answer.
- **AC-9 (retiered)** — 2 arms (none, `class_weight`) in T1; SMOTE arm in T2.
- **AC-10a (T1) — reliability curve per finalist, diagnostic only.** One `calibration_curve` call on an already-cached probability vector; cheaper than the `c_review` sweep. It is in T1 because **Policy E (T1) depends on calibrated probabilities**, and because R13's mitigation ("if E loses, miscalibration explains it") is otherwise mitigated by a droppable artifact.
- **AC-10b (T2) — recalibration** (`CalibratedClassifierCV`). This is the *remedy*, not the diagnostic; it refits and changes ranking, so it belongs in T2.
- **Calibration rationale** — required **only because Policy E compares `p` against the transaction-specific quantity `c_review/Amount_i`**, where monotone transforms are not neutral. Note: **Platt** scaling is strictly monotone (a genuine no-op for Policy A); **isotonic** has plateaus that merge distinct scores and can only *worsen* the achievable cost frontier. `CalibratedClassifierCV(cv=5)` refits the base estimator and therefore changes the *ranking* — it is not a pure monotone transform.
- **AC-11a (T1)** — Threshold selected on the 20% validation split.
- **AC-11b (T2, supersedes 11a when complete)** — Threshold selected on pooled out-of-fold CV predictions; report per-fold `t*` spread (min/median/max) **and** the width of the threshold interval within 1% of minimum cost (the *flatness*).
- **AC-15 (retiered to T1)** — `c_review` €1–€20 sweep → winner map.
- **AC-21 (T2)** — **Paired** bootstrap: resample the test index set **once** per replicate and score all policies on that same resample. Report the 95% CI on the **paired difference** `cost(A) − cost(B)`, not on absolute costs. 1,000 replicates.
- **AC-22 (new, T1)** — Report three baselines: flag-nothing (= total fraud Amount), flag-everything (= `c_review × N`), and **flag-if-`Amount > X`** (no ML). **`X` is selected on the validation split (same set as AC-11a), never on test**; report test cost at that fixed `X`. If a test sweep of `X` is shown at all, label it explicitly as an unattainable oracle curve. *If no model beats this baseline, that is the finding.*
- **AC-23 (new, T1)** — Report Policy A and Policy E side by side on identical probability vectors.
- **AC-24 (new, T1)** — Persist validation/test probability vectors (and OOF vectors once T2 runs), amounts and labels to Drive (`joblib`/`npz`) immediately after model fitting; **all** downstream analysis is pure post-processing on these arrays.
- **AC-25 (new, T1)** — Every estimator and splitter **that admits one** carries an explicit `random_state` (`StandardScaler` has none).

**Definition of done:** every **T1** AC ticked (T2/T3 ACs are explicitly optional), notebook runs top-to-bottom on a fresh Colab runtime, and the deck rehearses under 15:00.

---

## Implementation Steps

### Step 0 — Team setup *(week 1, day 1, all)*
- **Named owner per component.** Fill in: EDA ___ · Preprocessing ___ · Modeling ___ · Evaluation ___ · Report ___ · Slides ___.
- **Notebook convention:** one notebook per step, owner-prefixed (`01_eda_<name>.ipynb`); merge only at integration points. `.ipynb` JSON merges badly — never two people in one file.
- **Data access:** Kaggle API token → Drive; `creditcard.csv` (~144 MB) stored in Drive, not re-uploaded per session.
- **20-minute CART briefing.** Two of three models rest on decision trees, which **have not been taught**. Cover: splitting criterion (Gini/entropy), depth, and why averaging deep trees reduces *variance* — which ties back to the bias-variance material from Buổi 05b. Also prepare: *why does SMOTE go inside the CV fold?* (synthesising before splitting leaks minority information across the fold boundary).
- **Enumerate now, not in week 4:** the 10 report sections and the 6 rubric dataset questions, copied verbatim from `DoAnMonHoc` into the report skeleton. **Confirm which sections are model-independent** before assigning the weeks 1–3 drafting — the "sections 1–5" assumption below is unverified against the actual document.

### Step 1 — EDA *(week 1)* → AC-1..AC-3 — ✅ **DATA VERIFIED 2026-09-13**

All Step 1 asserts pass: `284,807` rows, `492` frauds (0.173%), **31 columns**, **0 nulls**, `Time` spans 172,792 s = 48.0 h exactly.

**Correction to the earlier prediction.** The plan previously expected "fraud amounts are *smaller* on average than legitimate ones". That is **wrong on the mean**, and the true shape is more useful:

| | fraud | legit |
|---|---|---|
| count | 492 | 284,315 |
| mean | €122.21 | €88.29 |
| **median** | **€9.25** | **€22.00** |
| std | €256.42 | €250.10 |
| max | €2,125.87 | €25,691.16 |

The *typical* fraud is small — median €9.25, under half the legit median of €22.00 — but the **mean** exceeds legit because of a heavy right tail. Neither "smaller" nor "larger" describes it: **bimodal in cost terms**.

**🎯 Headline finding for the presentation: 205 of 492 frauds (42%) are worth less than the €3 review fee, and 27 are exactly €0.** A cost-optimal policy therefore **ignores nearly half of all fraud on purpose** — reviewing a €1 fraud costs €3. Counterintuitive, concrete, and a direct consequence of the objective. Policy E produces this behaviour automatically; a global threshold cannot express it.

**Verified constants — use these, do not re-derive:**

| Constant | Value |
|---|---|
| Total fraud Amount (flag-nothing baseline) | **€60,127.97** |
| Flag-everything baseline | 284,807 × €3 = **€854,421** (**14.2× worse** than doing nothing) |
| Fraud Amount CV | 2.100 → 1 + CV² = 5.41 |
| **n_eff for a 98-fraud test set** | **18.1** |
| Day 1 | 144,786 rows, 281 frauds, €33,239.11 |
| Day 2 | 140,021 rows, **211 frauds**, €26,888.86 |

Day 2 holds **2.2× more frauds** than a random 20% test split (~98), so the temporal robustness check (T3) is statistically viable — R8 is closed.

**Still to produce:** class-distribution plot, `Amount` log-scale histogram by class, fraud rate by `hour_of_day`, correlation scan.

### Step 2 — Preprocessing *(week 1)* → AC-4..AC-7
- `hour_of_day = (Time // 3600) % 24`, **cyclically encoded** (`sin`/`cos`) — linear scaling puts 23:00 and 00:00 maximally apart.
- **Drop raw `Time` as a feature** — under a random split it lets the model memorise fraud-burst positions, which is genuine leakage and would corrupt the temporal check.
- `log1p(Amount)`, then scale. `V1`–`V28` untouched (already PCA output).
- Stratified 60/20/20, fixed seed. **Scaler fit on train only.**
- **Per-split fraud-rate table (AC-2)** — imbalance reported for *each* of train/val/test; this belongs here, after the split, not in Step 1.

### Step 3 — Cost module *(week 1)* → AC-12
- `total_cost(y_true, y_pred, amounts, c_review)`.
- **Unit-test on a hand-computed 4-row fixture before any model runs.** A bug here invalidates everything downstream.
- Implement the threshold sweep as **sort + cumulative sum**, not a loop:
  ```
  order   = argsort(-p)
  alerts  = arange(1, n+1)
  fn_amt  = A_set - cumsum(y[order] * amount[order])   # A_set = fraud Amount total WITHIN the scored set: A_val / A_oof / A_test
  cost    = c_review * alerts + fn_amt
  k_star  = argmin(cost);  t_star = p[order][k_star]
  ```
  **Tie safety (required).** `RandomForest(n_estimators=100)` emits only ~101 distinct probabilities, so hundreds of rows share a boundary value and the rank-based "top k" optimum is **not realizable by any threshold rule**. Evaluate cost only at `np.unique(p)` boundaries, taking `cost_k` at the **last index of each tied block** (all ties alerted), then `argmin` over those achievable points. **Add a tied-score row to the hand-computed fixture** — a 4-row fixture without ties will not catch this, and the failure is silent.
  A naive loop over ~227k unique scores is O(n²) and will appear to hang Colab. This is one pass, and yields the whole AC-14 curve for free.

### Step 4 — Model matrix *(week 2)* → AC-8, AC-9, AC-24, AC-25
- 3 families × 2 imbalance arms (T1) at **fixed defaults**, all with `random_state`:
  Logistic Regression (`max_iter=1000`) · Random Forest (`n_estimators=100, n_jobs=-1`) · XGBoost (`tree_method='hist'`).
- **Rank by PR-AUC and by cost at the validation-selected threshold (AC-11a)** — *not* by the CV threshold, which does not exist until Step 5. *(Iteration 1 had Step 4 consuming Step 5's output — a circular dependency.)*
- **Carry forward the best variant per algorithm family** — exactly one LogReg, one RF, one XGBoost. Taking the global top 3 could select three variants of one algorithm and break the ≥3-model rubric requirement.
- **Pre-register the champion in writing** (one markdown cell, dated) from validation/OOF ranking **before any test scoring**. The headline number is the champion's test cost, win or lose.
- **Persist probability arrays to Drive (AC-24).**

### Step 5 — Policy comparison & threshold optimization *(week 3, serial with Step 6)* → AC-11, AC-14, AC-23
- **Policy E** (`p × Amount > c_review`) and **Policy A** (global `t*`) on identical probability vectors.
- T2: 5-fold OOF selection; report per-fold `t*` spread **and** flatness width.
- **Refit protocol (was undefined):** refit on all of train+val; before transferring `t*`, verify the refit model's score distribution matches the OOF distribution. Record `t*` **both** as a probability **and as an implied alert rate** ("flag the top 0.72%"), and check the test alert rate lands near the OOF alert rate. Thresholds are **not** comparable across imbalance strategies.
- **Policy E applicability (new).** `class_weight='balanced'` inflates predicted probabilities by roughly the inverse class ratio (~580x), so `p > c_review/Amount_i` applied to a reweighted arm alerts on a large fraction of the test set and yields an absurd cost. **Evaluate Policy E only on arms whose probabilities estimate the true posterior (the `none` arm)** — or apply the prior-shift correction `p_corr = p / (p + (1-p)*w)` (w = the applied weight ratio) before Policy E. State which you chose. If the validation-selected champion is a reweighted arm, Policy E is reported on its `none` counterpart.

### Step 6 — Sensitivity & robustness *(week 3, AFTER Step 5)* → AC-15, AC-21, AC-22
> Steps 5 and 6 are **serial, not parallel** — Step 6 bootstraps the champion and sweeps around the threshold Step 5 produces.
- `c_review` €1–€20 sweep → winner map. **Report the recovery-rate equivalence (direction matters):** sweeping `c_review` €3→€20 is equivalent to holding €3 while the **recovery rate on caught fraud falls from 100% to 15%** (equivalently, non-recovery rises 0→85%). The equivalence holds **up to an additive constant**, so the *winner map is unchanged* while absolute costs differ — say "equivalent up to an additive constant", not "identical". Stated backwards, this is exactly the slide claim that invites a fatal follow-up.
- Three baselines (AC-22).
- T2: paired bootstrap CI on the paired difference.
- **Acknowledged gap:** FP friction/churn cost is *not* absorbable by rescaling `c_review` (it hits FP only). State as a limitation and note the direction — adding friction pushes the optimal threshold *up*, so "optimal threshold far below 0.5" is conservative in the wrong direction.

### Step 7 — Error analysis *(**week 3** — T1 content)* → AC-16, AC-17
> **Week 4 = buffer + T2 + polish.** Every T1 artifact exists by end of week 3; week 4 adds optional depth and absorbs slippage. Iteration 2 had T1's headline chart scheduled in week 4 while claiming T1 was complete in week 3.
- Missed frauds by `Amount` decile — **the headline chart**.
- Train vs **validation** = the original held-out 20% split → overfitting diagnosis.
  ⚠️ **T1 caveat:** under AC-11a the threshold *is* selected on that same validation split, so validation P/R/F1/cost at `t*` are optimistically biased. In the T1 branch, answer Q6 on **threshold-independent metrics (PR-AUC)** and say so. Under T2/Option B the split is untouched by selection and the bias disappears.
- *(week 4)* Feature importance, caveated: V-features are anonymised.
- *(week 4, T3)* Temporal check. **Must be labelled a distribution-shift check, not a leakage remedy** — `V1`–`V28` are a PCA basis fitted on all 48 hours, so look-ahead is already baked into the features and no split can undo it. Saying this out loud converts a humiliating question into a display of understanding. n=1 transition → directional only.

### Step 8 — Deliverables *(drafting starts week 1)* → AC-18..AC-20
- **Report sections 1–5 (intro, dataset, EDA, preprocessing, methodology) drafted in weeks 1–3**, owner per section. Only results/analysis/conclusion wait for week 4.
- **First full draft by end of week 3.**
- Notebook integration into one runnable file with fixed seeds.
- **12-slide deck built and rehearsed against a timer by end of week 3** (not week 4).
- Assign one defender per figure: each owner must give a one-sentence defence of their chart.

---

## Risks and Mitigations

| # | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R1 | Cost-function bug invalidates all results | Med | **Crit** | Hand-computed unit test before any model run (Step 3) |
| R2 | Week 8 drawn with T1 incomplete | Med | High | T1 now genuinely covers all 8 questions; **T1 + rehearsed deck complete by end of week 3** |
| R3 | Threshold overfits (~98 val frauds) | High | Med | Policy E needs no threshold at all; T2 adds OOF selection; report flatness width |
| R4 | Champion inside the noise band | **High** | Med | Paired bootstrap; **pre-commit to reporting "no significant difference" as a legitimate result** |
| R5 | ~~SMOTE OOM~~ **RF+SMOTE wall-clock** | Med | Med | *Re-rated: memory is a non-issue (~136 MB vs 12 GB). The real cost is RF training on a doubled set.* SMOTE is T2; drop it first if week 2 slips |
| R6 | Data leakage via scaler fit on full data | Med | **Crit** | Assertion + peer review of the split cell |
| R7 | Colab disconnect mid-run loses everything | **High** | High | **AC-24 checkpointing** — probability arrays persisted; all analysis is post-processing |
| R8 | ~~Too few day-2 frauds~~ **CLOSED — verified** | – | – | Day 1: 144,786 rows / 281 frauds / €33,239. Day 2: 140,021 rows / **211 frauds** / €26,889. Day 2 holds **2.2× more frauds** than a random 20% test split (~98), so the temporal check is statistically viable. |
| R9 | Slides exceed 15:00 | Med | High | Deck exists by end of week 3, rehearsed with a timer |
| **R10** | **Uneven contribution / no accountability** | **High** | High | Named owner per component (Step 0); one defender per figure |
| **R11** | **`.ipynb` merge conflicts destroy work** | High | Med | One notebook per owner; merge only at integration points |
| **R12** | **Q&A on XGBoost/trees (never taught)** | **High** | High | Step 0 CART briefing; prepare the SMOTE-inside-fold answer. *Fallback: substitute `GradientBoostingClassifier`, explainable from Buổi 05b* |
| **R13** | **Headline narrative doesn't materialise** | Med | Med | Policy A vs E gives a finding either way: if E wins, that's the headline; if E loses, miscalibration is the explanation and the reliability curve proves it |
| **R14** | **10-section report compressed into week 4** | High | High | Sections 1–5 drafted weeks 1–3; full draft by end of week 3 |

---

## Verification Steps

*Each step tagged by tier — T2 checks are not evaluable in a T1-only run.*

1. `assert df.shape[0] == 284807 and df.Class.sum() == 492`.
2. Cost-function unit test passes on the hand-computed fixture.
3. Scaler fitted on train only — assert on the fitted object, and **if wrapped in a `Pipeline`/`ColumnTransformer`, assert on the inner scaler** (`n_samples_seen_` breaks silently otherwise).
4. **`predict_proba` on test is called exactly once per model**; all later analysis reads the cached array. *(Iteration 1 said "grep for `X_test`", which fails on correct work — the sweep and bootstrap legitimately re-read test predictions.)*
5. *(T1/T2)* **On the selection set** (validation in T1, OOF in T2): `cost(t*) ≤ cost(0.5)` — true by construction; failure means the search is buggy. **On test: report both numbers as-is.** If `t*` loses to 0.5 on test, that is a reportable finding about threshold transfer under n_eff ≈ 18, **not a defect to fix.** *(Iteration 1 asserted this on test, which would have pushed students to re-tune until it passed — the exact Principle-2 violation the plan exists to prevent.)*
6. *(T2)* **SMOTE applied inside CV folds only** — assert the resampler sits inside the `Pipeline`, never fitted before the split.
7. Every estimator and splitter has an explicit `random_state` (AC-25).
8. *(T2)* Paired bootstrap uses one shared resampled index set per replicate. Prefer a **class-stratified** bootstrap — at n_eff ≈ 18 a simple resample can yield replicates with too few frauds to be meaningful.
9. Rubric traceability table: all 8 questions map to a T1 figure or table number.
10. *(T1)* Fresh-runtime rerun: **pin `nthread=1` for the final XGBoost run and require exact equality.** A 1e-6 tolerance is misconceived — XGBoost nondeterminism is *discrete*: one float flip moves a transaction across the threshold and cost jumps by tens of euros, never by 1e-6. If single-threading is impractical, express tolerance as **alert-set agreement ≥ 99.9% plus cost within 1%**. (`RandomForest` with a fixed `random_state` is deterministic regardless of `n_jobs`.)

---

## ADR

**Decision.** Adopt the amount-dependent rule `p_i × Amount_i > c_review` (Option E) as the headline decision policy, compared against a global-threshold policy (Option A in T1, upgraded to Option B out-of-fold selection in T2), evaluated by expected monetary cost with a pre-registered champion and a paired bootstrap.

**Drivers.** (1) Week-8 draw risk demands a complete T1 by week 3. (2) Effective sample size for the cost metric is ~18, so cheap variance-robust design beats expensive variance reduction. (3) All 8 rubric questions must be answerable from T1 alone.

**Alternatives considered.** A (single-split threshold) — retained as T1 fallback. B (OOF CV) — retained as T2 spine; solves *selection* variance but not *evaluation* variance. C (fixed 0.5) — rejected: forfeits Q8 and yields no insight. D (cost-sensitive training) — adopted as a T2 arm; confusing to explain alongside thresholding.

**Why chosen.** Option E is the Bayes-optimal rule for the stated objective, costs zero additional fits, and is *easier* to present than threshold tuning. Both reviewers independently identified that the global-threshold restriction contradicted Principle 1.

**Consequences.** Calibration is promoted from optional to load-bearing (Policy E compares `p` against an amount-derived quantity). The project gains a genuine finding in either branch. Test-set evaluation noise (n_eff ≈ 18) remains and is reported, not hidden.

**Follow-ups.** Confirm the deadline and course-week mapping with the lecturer. If XGBoost proves indefensible in Q&A, substitute `GradientBoostingClassifier`. Consider nested CV (T3) if week 4 has slack.

---

## Decisions that must be written down before Step 4 (ambiguity guards)

| Question | Decision to record |
|---|---|
| Where is AC-22's `X` selected? | **Validation.** Never test (Major #4) |
| When is test scored? | **Week 3, finalists only** (3 configs) — not all 6 in week 2. Keeps the pre-registration narrative clean |
| "Refit score distribution *matches* OOF" — how measured? | **KS statistic with a stated threshold**, not eyeballed histograms |
| "Test alert rate *near* OOF alert rate" — how near? | **Within ±25% relative** |
| Policy E on reweighted arms? | `none` arm only, **or** prior-shift corrected — state which |

## Operational gates (make Principle 5 real)

- **End of week 3 checkpoint:** if T1 is not complete *and rehearsed*, **T2 is abandoned**. Without a dated gate, tiering is aspirational.
- **If the pre-registered champion loses on test:** script the 30 seconds now. *"We pre-registered X on validation. On test it placed second by €N, inside the bootstrap CI — which is the expected outcome at an effective sample size of ~18, and the reason we report the CI rather than a ranking."* Given R4 is rated High, this is the difference between looking rigorous and looking wrong.
- **Sanity-predict Policy E's alert rate before building slides.** The headline rests on it. If it alerts on >5% of transactions, something is wrong (almost certainly uncalibrated probabilities) — investigate before committing the narrative.
- **Note for Q8:** `c_review` appears *inside* Policy E's rule, so sweeping it **moves the policy itself**, not just the evaluation. That is a genuinely sharp Q8 point and a trap if unnoticed.
- **Zero-Amount frauds:** Policy E can never alert on them — correctly, since their expected loss is €0. Have the one-line answer ready for *"why does your rule ignore some frauds entirely?"*

## Open Questions (non-blocking)
- Exact submission deadline — absent from spec and all transcripts; **ask the lecturer.**
- Does `DoAnMonHoc` award marks per question or holistically? Determines how costly a partial answer is.
- Provenance of `c_review = €3` — swept, but the report needs one sentence justifying the default.

---

## Changelog — iteration 1 → 2

**Critical (Critic, blocking):** C1 rubric Q8 had no T1 coverage → moved AC-15 and 2-arm AC-9 into T1; added a per-question verified trace. C2 verification step 5 instructed test-set tuning → restated against OOF. C3 AC-11 vs tiers mutually exclusive → split into 11a/11b; AC-21 assigned to T2.

**Major:** M1 Step 4→5 circular dependency broken. M2 carry-forward now per algorithm family. M3 bootstrap paired, CI on paired difference. M4 refit protocol + alert-rate transfer check specified. M5 "validation" defined as the original 20% split. M6 Step 8 expanded; report drafting moved to weeks 1–3. M7 R5/R8 re-rated; R10–R14 added. M8/Option E amount-dependent rule adopted as headline.

**Architect:** pre-registered champion (test-selection leak); no-ML `Amount > X` baseline (AC-22); sort+cumsum sweep (O(n²) hang); OOF array caching (AC-24); n_eff ≈ 18 and flatness width reporting; recovery-rate isomorphism; PCA-leakage caveat on the temporal check; raw `Time` dropped; `hour_of_day` cyclically encoded; Platt vs isotonic distinction; CART briefing (Step 0); TP=`c_review` confirmed correct.

**Minor:** PR-AUC named in T1; `random_state` everywhere (AC-25); pipeline-safe scaler assertion; Option C rejected on substance not principle; Kaggle data-loading step; course-week anchoring; SMOTE-inside-folds check; "exactly" → 1e-6.


---

## Changelog — iteration 2 → 3 (final)

Critic verdict: **APPROVED WITH IMPROVEMENTS**, "no further review round required". All improvements applied:

**Majors:** #1 Step 7's T1 bullets moved to week 3, week 4 declared buffer+T2+polish (T1's headline chart was scheduled *after* T1's own deadline). #2 AC-10 split into T1 reliability curve / T2 recalibration — the T1 headline policy no longer depends on a droppable artifact. #3 Policy E scoped to posterior-estimating arms, with the prior-shift correction given (`class_weight` inflates probabilities ~580×, which would have broken Policy E silently). #4 AC-22's `X` pinned to validation selection — otherwise the project's most quotable finding would be a test-selection artifact. #5 sweep made tie-safe (RF emits only ~101 distinct probabilities, so the rank-based optimum is unrealizable), with a tied-score fixture row. #6 AC-4 and AC-7 amendments added so the definition of done is mechanically evaluable.

**Minors:** recovery-rate equivalence direction corrected (recovery *falls* 100%→15%) and downgraded to "up to an additive constant"; `A_set` scoped per evaluation set; reproducibility restated as pinned-thread exact equality or alert-set agreement; T1 train-vs-val optimism flagged with PR-AUC fallback; verification list tiered; "mean Amount" corrected to "a constant `Ā`" with implied-`Ā` reporting; AC-24 wording; AC-25 scoped; AC-2 rehomed to Step 2; report-section assumption flagged for confirmation.

**Added:** ambiguity-guard decision table (5 items to record before Step 4); operational gates — week-3 T2 abandonment checkpoint, a scripted response for a losing pre-registered champion, a Policy E alert-rate sanity prediction, the `c_review`-moves-Policy-E observation for Q8, and the zero-Amount-fraud answer.
