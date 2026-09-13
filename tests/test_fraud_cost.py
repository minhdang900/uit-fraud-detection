"""Tests for the cost model (Do an CS114 - plan Step 3, risk R1/Critical).

Every number in these fixtures is hand-computed in the docstring so a
reviewer can verify the expectation without running the code.
"""
import numpy as np

from fraud_cost import (
    best_amount_baseline,
    cost_curve,
    optimal_threshold,
    policy_e_predict,
    total_cost,
    undo_class_weight,
)


def test_charges_review_cost_per_alert_and_full_amount_per_missed_fraud():
    """Hand-computed 4-row fixture, c_review = 3.

    i | y_true | y_pred | Amount | outcome | cost
    0 |   1    |   1    |  100   |   TP    |   3   (reviewed)
    1 |   1    |   0    |  500   |   FN    | 500   (money lost)
    2 |   0    |   1    |   50   |   FP    |   3   (reviewed)
    3 |   0    |   0    |   20   |   TN    |   0

    TotalCost = 3*(TP+FP) + sum(Amount over FN)
              = 3*(1+1)   + 500
              = 6 + 500 = 506
    """
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 0])
    amounts = np.array([100.0, 500.0, 50.0, 20.0])

    assert total_cost(y_true, y_pred, amounts, c_review=3.0) == 506.0


def test_cost_curve_reports_only_thresholds_achievable_when_scores_tie():
    """Ties make the naive rank-based optimum unreachable (Critic Major #5).

    RandomForest(n_estimators=100) emits ~101 distinct probabilities, so
    many rows share a boundary score. This fixture is the minimal case.

    i | score | y_true | Amount
    0 |  0.5  |   1    |  1000
    1 |  0.5  |   0    |    10
    2 |  0.5  |   0    |    10

    All three scores tie, so a rule `p >= t` can only ever produce two
    alert sets:
      t > 0.5  -> alert {}       : 0 alerts, fraud 0 missed -> cost = 1000
      t <= 0.5 -> alert {0,1,2}  : 3 alerts, none missed    -> cost = 3*3 = 9
    Achievable minimum = 9.

    A naive sweep over "top k" ranks would also consider k=1 (alert only
    the fraud) and report cost = 3 -- which no threshold can actually
    produce. Reporting 3 would understate cost and hand the report a
    threshold that cannot be implemented.
    """
    scores = np.array([0.5, 0.5, 0.5])
    y_true = np.array([1, 0, 0])
    amounts = np.array([1000.0, 10.0, 10.0])

    thresholds, costs = cost_curve(y_true, scores, amounts, c_review=3.0)

    assert costs.min() == 9.0, "naive rank sweep would report the unreachable 3.0"
    assert sorted(costs.tolist()) == [9.0, 1000.0]


def test_policy_e_alerts_on_expected_loss_not_on_probability():
    """`alert iff p * Amount > c_review` -- the Bayes rule for this objective.

    i |   p   | Amount | p*Amount | > 3? | alert
    0 | 0.01  |  1000  |   10.00  | yes  |  1    <- low probability, big money
    1 | 0.50  |     4  |    2.00  | no   |  0
    2 | 0.001 | 10000  |   10.00  | yes  |  1    <- very low probability, huge money
    3 | 0.90  |     1  |    0.90  | no   |  0    <- high probability, trivial money

    Rows 0 and 3 are the point of the whole policy: a global threshold would
    alert on row 3 and ignore row 0, which is backwards for a cost objective.
    """
    probabilities = np.array([0.01, 0.50, 0.001, 0.90])
    amounts = np.array([1000.0, 4.0, 10000.0, 1.0])

    alerts = policy_e_predict(probabilities, amounts, c_review=3.0)

    assert alerts.tolist() == [1, 0, 1, 0]


def test_optimal_threshold_reports_the_implied_alert_rate():
    """Plan M4: t* must be recorded as a probability AND as an alert rate,
    because the probability does not transfer across a refit but the alert
    rate does ("flag the top 0.75%").

    i | score | y_true | Amount        total fraud = 100 + 200 = 300
    0 |  0.9  |   1    |   100
    1 |  0.8  |   0    |    10
    2 |  0.7  |   1    |   200
    3 |  0.6  |   0    |    10

    threshold | alerts | missed fraud | cost = 3*alerts + missed
        inf   |   0    |  100 + 200   | 0   + 300 = 300
        0.9   |   1    |        200   | 3   + 200 = 203
        0.8   |   2    |        200   | 6   + 200 = 206
        0.7   |   3    |          0   | 9   +   0 =   9   <- minimum
        0.6   |   4    |          0   | 12  +   0 =  12

    Optimum: threshold 0.7, cost 9, alerting 3 of 4 rows = 0.75.
    """
    scores = np.array([0.9, 0.8, 0.7, 0.6])
    y_true = np.array([1, 0, 1, 0])
    amounts = np.array([100.0, 10.0, 200.0, 10.0])

    threshold, cost, alert_rate = optimal_threshold(
        y_true, scores, amounts, c_review=3.0
    )

    assert threshold == 0.7
    assert cost == 9.0
    assert alert_rate == 0.75


def test_undo_class_weight_recovers_the_true_posterior():
    """Plan Major #3: `class_weight='balanced'` inflates probabilities by
    roughly the inverse class ratio, so Policy E applied to a reweighted
    model alerts on almost everything. Invert before applying Policy E.

    Reweighting maps a true posterior p to  p_w = w*p / (w*p + (1-p)).
    Inverting:                              p   = p_w / (w*(1-p_w) + p_w)

    With w = 9:
      p_w = 0.0 -> 0.0 / (9*1.0 + 0.0) = 0.0
      p_w = 0.5 -> 0.5 / (9*0.5 + 0.5) = 0.5 / 5.0 = 0.1
      p_w = 0.9 -> 0.9 / (9*0.1 + 0.9) = 0.9 / 1.8 = 0.5
      p_w = 1.0 -> 1.0 / (9*0.0 + 1.0) = 1.0
    """
    reweighted = np.array([0.0, 0.5, 0.9, 1.0])

    recovered = undo_class_weight(reweighted, weight_ratio=9.0)

    np.testing.assert_allclose(recovered, [0.0, 0.1, 0.5, 1.0])


def test_every_cost_the_curve_reports_is_reproducible_by_applying_it():
    """Round-trip invariant binding cost_curve to total_cost.

    For every (threshold, cost) the curve reports, actually applying
    `scores >= threshold` and re-costing it must give back that same cost.
    Any threshold the curve cannot reproduce is one the report would quote
    and the pipeline could never implement.

    Fixture deliberately contains a tied block (three scores at 0.5):

    i | score | y_true | Amount      total fraud = 100 + 1000 + 50 = 1150
    0 |  0.9  |   1    |   100
    1 |  0.5  |   1    |  1000
    2 |  0.5  |   0    |    10
    3 |  0.5  |   0    |    10
    4 |  0.1  |   1    |    50

    threshold | alerts | missed fraud | cost
        inf   |   0    | 100+1000+50  | 1150
        0.9   |   1    |    1000+50   | 1053
        0.5   |   4    |          50  |   62
        0.1   |   5    |           0  |   15
    """
    scores = np.array([0.9, 0.5, 0.5, 0.5, 0.1])
    y_true = np.array([1, 1, 0, 0, 1])
    amounts = np.array([100.0, 1000.0, 10.0, 10.0, 50.0])

    thresholds, costs = cost_curve(y_true, scores, amounts, c_review=3.0)

    for threshold, reported in zip(thresholds, costs):
        applied = total_cost(
            y_true, (scores >= threshold).astype(int), amounts, c_review=3.0
        )
        assert applied == reported, (
            f"threshold {threshold} claims cost {reported} "
            f"but applying it actually costs {applied}"
        )


def test_amount_baseline_is_the_same_sweep_with_amount_as_the_score():
    """AC-22: the no-ML baseline "review every transaction above X".

    If no model beats this, that is the finding -- and it is the check that
    establishes whether machine learning earns its keep here at all.
    Critic Major #4: X must be selected on validation, never on test, or the
    baseline gets an oracle advantage over the pre-registered champion.

    i | y_true | Amount        total fraud = 500 + 20 = 520
    0 |   1    |   500
    1 |   0    |   100
    2 |   1    |    20
    3 |   0    |    10

      X    | alerts (Amount >= X) | missed fraud | cost = 3*alerts + missed
     inf   |         0            |    500 + 20  | 0  + 520 = 520
     500   |         1            |          20  | 3  +  20 =  23
     100   |         2            |          20  | 6  +  20 =  26
      20   |         3            |           0  | 9  +   0 =   9   <- minimum
      10   |         4            |           0  | 12 +   0 =  12

    Best: review everything at or above EUR 20, for a cost of EUR 9.
    """
    y_true = np.array([1, 0, 1, 0])
    amounts = np.array([500.0, 100.0, 20.0, 10.0])

    threshold, cost = best_amount_baseline(y_true, amounts, c_review=3.0)

    assert threshold == 20.0
    assert cost == 9.0


def test_policy_e_never_alerts_on_a_zero_amount_fraud():
    """Characterisation test -- passes against current code, locks in intent.

    A zero-amount fraud has zero expected loss, so paying to review it is a
    pure loss. Policy E correctly ignores it. Recorded because it looks like
    a bug ("your rule ignores some frauds!") and someone will try to "fix"
    it; this test makes that break loudly. It is also the prepared answer if
    a reviewer asks.
    """
    probabilities = np.array([0.99, 0.99])
    amounts = np.array([0.0, 1000.0])

    alerts = policy_e_predict(probabilities, amounts, c_review=3.0)

    assert alerts.tolist() == [0, 1]
