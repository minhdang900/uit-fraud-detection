"""Cost model for credit-card fraud detection (Do an CS114)."""
import numpy as np


def total_cost(y_true, y_pred, amounts, c_review):
    """Expected monetary cost of a set of alerting decisions.

    TotalCost = c_review * (TP + FP) + sum(Amount over FN)

    Every alert costs a review regardless of whether it turns out to be
    fraud, because the analyst's time is spent before the label is known.
    Every missed fraud costs its full transaction amount.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    amounts = np.asarray(amounts, dtype=float)

    alerts = int(y_pred.sum())
    missed = (y_true == 1) & (y_pred == 0)
    return c_review * alerts + float(amounts[missed].sum())


def cost_curve(y_true, scores, amounts, c_review):
    """Achievable (threshold, cost) points for the rule `score >= threshold`.

    Only thresholds a real rule can produce are returned. Where scores tie,
    a threshold alerts the whole tied block, so cost is taken at the LAST
    index of each block. A rank-based "top k" sweep would report optima
    inside a tied block that no threshold can reach -- silently, with
    plausible-looking numbers.

    Returns (thresholds, costs); thresholds[0] is inf, the alert-nothing point.
    """
    y_true = np.asarray(y_true)
    scores = np.asarray(scores, dtype=float)
    amounts = np.asarray(amounts, dtype=float)

    order = np.argsort(-scores, kind="stable")
    y_s, a_s, p_s = y_true[order], amounts[order], scores[order]

    total_fraud = float((amounts * (y_true == 1)).sum())
    k = np.arange(1, len(scores) + 1)
    fn_amt = total_fraud - np.cumsum(a_s * (y_s == 1))
    costs_k = c_review * k + fn_amt

    last_of_block = np.r_[p_s[1:] != p_s[:-1], True]
    thresholds = np.r_[np.inf, p_s[last_of_block]]
    costs = np.r_[total_fraud, costs_k[last_of_block]]
    return thresholds, costs


def policy_e_predict(probabilities, amounts, c_review):
    """Amount-dependent decision rule: alert iff expected loss beats review cost.

        alert iff  p_i * Amount_i > c_review

    This is the cost-minimising rule for
    `c_review * (TP + FP) + sum(Amount over FN)`. A global threshold is the
    special case where every Amount is replaced by a constant A_bar, with
    t = c_review / A_bar.

    Requires *calibrated* probabilities: p is compared against the
    transaction-specific quantity c_review / Amount_i, so a monotone
    transform of p changes the decision set (unlike a global threshold).
    """
    probabilities = np.asarray(probabilities, dtype=float)
    amounts = np.asarray(amounts, dtype=float)
    return (probabilities * amounts > c_review).astype(int)


def optimal_threshold(y_true, scores, amounts, c_review):
    """Cost-minimising achievable threshold.

    Returns (threshold, cost, alert_rate). The alert rate matters as much as
    the threshold: a probability cut does not transfer across a refit (the
    score distribution shifts), but "flag the top X%" does. Record both and
    check the test alert rate lands near the selection alert rate.
    """
    scores = np.asarray(scores, dtype=float)
    thresholds, costs = cost_curve(y_true, scores, amounts, c_review)

    best = int(np.argmin(costs))
    threshold = float(thresholds[best])
    alert_rate = float((scores >= threshold).sum()) / len(scores)
    return threshold, float(costs[best]), alert_rate


def undo_class_weight(probabilities, weight_ratio):
    """Recover the true posterior from a class-weighted model's output.

    Training with `class_weight='balanced'` re-weights the minority class by
    roughly the inverse class ratio, mapping a true posterior p to

        p_w = w*p / (w*p + (1 - p))

    which inverts to

        p = p_w / (w*(1 - p_w) + p_w)

    Policy E compares p against c_review / Amount_i, so it must be fed a true
    posterior. Skipping this makes a reweighted model alert on a large
    fraction of all transactions -- silently, with a plausible-looking cost.
    """
    p_w = np.asarray(probabilities, dtype=float)
    return p_w / (weight_ratio * (1.0 - p_w) + p_w)


def best_amount_baseline(y_true, amounts, c_review):
    """No-ML baseline: "review every transaction at or above X euros".

    This is exactly the threshold sweep with Amount used as the score, so it
    inherits the same tie-safety. Returns (X, cost).

    Select X on the SAME set used to select the model threshold (validation),
    never on test -- otherwise the baseline is tuned with hindsight the
    pre-registered champion never had, and "no model beat a one-line rule"
    becomes an artefact rather than a finding.
    """
    return optimal_threshold(y_true, amounts, amounts, c_review)[:2]
