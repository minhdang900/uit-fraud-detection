"""Regression tests locking the PUBLISHED results to the stored artifacts.

The unit tests in test_fraud_cost.py prove the functions are correct. These
prove the NUMBERS IN THE REPORT are still the numbers the pipeline produces.

Without these, docs/REPORT.md and docs/SLIDES.md quote EUR2,223.93 and nothing
detects it if a change to preprocessing, the split, or the threshold search
makes that figure stale. A grader re-running the notebook would get a different
answer than the report claims, and nobody would know until they asked.
"""
import numpy as np
import pytest

from verify_results import reproduce_headline

C_REVIEW = 3.0


@pytest.fixture(scope="module")
def headline():
    return reproduce_headline(c_review=C_REVIEW)


def test_champion_matches_the_dated_preregistration(headline):
    """The champion was declared in writing before test was scored. If the
    pipeline now favours a different model, the pre-registration is void and
    the report's integrity claim is false."""
    assert headline["champion"] == "xgb/balanced"


def test_champion_test_cost_reproduces_the_published_figure(headline):
    """docs/REPORT.md, docs/RESULTS.md and docs/SLIDES.md all quote EUR2,223.93.

    Recomputed here from the stored probability arrays: the threshold is
    re-derived from the VALIDATION probabilities, then applied to the TEST
    probabilities. That exercises the whole chain, not just a cached number.
    """
    assert headline["champion_test_cost"] == pytest.approx(2223.93, abs=0.01)


def test_cost_decomposes_exactly_into_reviews_plus_lost_fraud(headline):
    """TotalCost = c_review x alerts + sum(Amount over FN).

    The two parts must sum to the whole. If they ever disagree, either the
    cost function or the confusion counting is wrong -- and every downstream
    figure in the report inherits the error.
    """
    reviews = headline["reviews"]
    lost = headline["lost"]
    assert reviews + lost == pytest.approx(headline["champion_test_cost"], abs=0.01)
    assert reviews == pytest.approx(396.00, abs=0.01)
    assert lost == pytest.approx(1827.93, abs=0.01)


def test_recovered_plus_lost_equals_total_test_fraud_value(headline):
    """Every euro of fraud is either recovered or lost -- there is no third
    bucket. EUR8,817.00 + EUR1,827.93 = EUR10,644.93."""
    assert headline["recovered"] + headline["lost"] == pytest.approx(
        headline["test_fraud_value"], abs=0.01
    )
    assert headline["test_fraud_value"] == pytest.approx(10644.93, abs=0.01)


def test_test_split_still_holds_98_frauds(headline):
    """n_eff = 18.1 is derived from 98 test frauds. If the split changes, every
    confidence interval in the report is wrong."""
    assert headline["test_frauds"] == 98
    assert headline["caught"] == 85
