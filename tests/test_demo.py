"""Tests for demo.py -- the one command run in front of the committee.

A demo that prints numbers disagreeing with the report is worse than no demo,
because it fails in public. These bind the demo's output to the same source of
truth the report uses, so drift breaks the suite instead of the defence.
"""
import numpy as np
import pytest

import demo
from verify_results import reproduce_headline

C = 3.0


@pytest.fixture(scope="module")
def loaded():
    return demo.load()


def test_demo_reads_the_same_artifacts_the_report_was_built_from(loaded):
    te, va, prereg = loaded
    assert prereg["declared_winner"] in te.files
    assert prereg["declared_winner"] in va.files
    assert len(te["y"]) == reproduce_headline(C)["test_rows"]


def test_the_headline_the_demo_prints_matches_verify_results(loaded, capsys):
    """Both recompute from the raw arrays, so they must agree exactly.

    demo.py derives its threshold independently rather than importing the
    number, which is the point: if the two ever disagree, one of them is
    reading a stale path.
    """
    te, va, prereg = loaded

    champ, cost = demo.demo_headline(te, va, prereg)

    expected = reproduce_headline(C)
    assert champ == expected["champion"]
    assert cost == pytest.approx(expected["champion_test_cost"], abs=0.01)
    assert cost == pytest.approx(2223.93, abs=0.01)


def test_the_worked_cost_example_still_totals_506(capsys):
    """demo.py asserts this internally; the test makes the failure land in CI
    rather than on a projector."""
    demo.demo_cost_model()
    assert "€506.00" in capsys.readouterr().out


def test_the_policy_table_shows_the_reversal_that_justifies_the_project(capsys):
    """The demo's second panel has to actually demonstrate its claim: alert on
    a low-probability large amount, ignore a high-probability trivial one."""
    demo.demo_policy_rule()
    out = capsys.readouterr().out
    assert "€1,000.00" in out and "€10,000.00" in out


def test_scoring_a_cheap_high_probability_transaction_splits_the_policies(loaded, capsys):
    """p = 0.90 on a EUR2 transaction: above any sane global threshold, but
    expected loss EUR1.80 < EUR3 review fee, so Policy E declines. This is the
    disagreement the whole report is about, and the demo must surface it."""
    _, va, prereg = loaded

    demo.demo_score(0.90, 2.0, va, prereg)

    out = capsys.readouterr().out
    assert "BẤT ĐỒNG" in out


def test_scoring_an_expensive_likely_fraud_makes_both_policies_agree(loaded, capsys):
    """p = 0.02 on EUR1,500: expected loss EUR30, far over the fee, and above
    the tuned threshold too. Both alert -- the demo must not cry wolf."""
    _, va, prereg = loaded

    demo.demo_score(0.02, 1500.0, va, prereg)

    assert "đồng ý" in capsys.readouterr().out


def test_the_demo_needs_no_dataset_csv():
    """It must run on a machine that never downloaded the 144MB Kaggle file --
    otherwise it cannot be shown on a borrowed laptop."""
    import inspect
    src = inspect.getsource(demo)
    assert "creditcard.csv" not in src
    assert "read_csv" not in src
