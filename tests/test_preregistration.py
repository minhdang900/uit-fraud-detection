"""Tests for the pre-registration guard (audit finding A-2).

The report's integrity claim is: "the champion was declared in writing, dated,
before the test set was ever scored". That claim is only worth something if the
record CANNOT quietly update itself. Before this guard existed, re-running
`run_model_matrix.py` rewrote `preregistration.json` with today's date -- so the
file agreed with every run by construction and proved nothing at all.

These tests pin the guard's two jobs: pass a genuine rerun, and refuse anything
that would launder a changed result into a fresh-looking record.
"""
import pytest

from modeling import (PreregistrationViolation, build_preregistration,
                      verify_preregistration)

C = 3.0


def champs(*families):
    """Champion list in the pipeline's shape, cheapest first."""
    return [{"family": f, "arm": "balanced", "cost": 100.0 * (i + 1)}
            for i, f in enumerate(families)]


def test_a_rerun_that_still_prefers_the_same_model_is_accepted():
    """The ordinary case: nothing drifted, so the record still stands.

    Returns the RECORDED dict -- not a freshly built one -- so the original
    date survives and downstream code cannot accidentally depend on today's.
    """
    recorded = build_preregistration(champs("xgb", "rf", "logreg"), C, "2026-09-13")

    returned = verify_preregistration(recorded, champs("xgb", "rf", "logreg"), C)

    assert returned is recorded
    assert returned["date"] == "2026-09-13"


def test_a_changed_champion_is_refused_rather_than_silently_rewritten():
    """The case the guard exists for.

    If preprocessing, the split, or a library version changes enough that
    validation now prefers Random Forest, the dated claim about XGBoost is
    void. The old behaviour overwrote the file and the report kept asserting
    an integrity guarantee that no longer held.
    """
    recorded = build_preregistration(champs("xgb", "rf", "logreg"), C, "2026-09-13")

    with pytest.raises(PreregistrationViolation) as exc:
        verify_preregistration(recorded, champs("rf", "xgb", "logreg"), C)

    # the message has to name both sides, or nobody can act on it
    assert "xgb/balanced" in str(exc.value)
    assert "rf/balanced" in str(exc.value)
    assert "2026-09-13" in str(exc.value)


def test_changing_the_review_fee_invalidates_the_record_even_if_the_winner_holds():
    """Subtle failure the champion check alone would miss.

    The champion is whichever model minimises cost AT A GIVEN c_review. Change
    the fee from EUR3 to EUR10 and the recorded ranking was computed against a
    different objective -- the record no longer describes this experiment, even
    when the same model happens to come out on top again.
    """
    recorded = build_preregistration(champs("xgb", "rf", "logreg"), c_review=3.0,
                                     today="2026-09-13")

    with pytest.raises(PreregistrationViolation, match="c_review changed"):
        verify_preregistration(recorded, champs("xgb", "rf", "logreg"), c_review=10.0)


def test_the_declared_winner_is_the_cheapest_champion_not_an_arbitrary_one():
    """`select_champion_per_family` returns cheapest-first, and the declaration
    must follow that order rather than, say, dict insertion order."""
    prereg = build_preregistration(champs("xgb", "rf", "logreg"), C, "2026-09-13")

    assert prereg["declared_winner"] == "xgb/balanced"
    assert prereg["champions"][0]["cost"] == 100.0


def test_an_empty_champion_list_cannot_be_pre_registered():
    """Declaring "the winner is <nothing>" would sail through to test scoring
    and produce a report with an empty headline."""
    with pytest.raises(ValueError):
        build_preregistration([], C, "2026-09-13")


def test_the_record_states_it_was_made_before_test_was_scored():
    """The provenance sentence is the artifact's whole point; a record without
    it is just a results table with a date on it."""
    prereg = build_preregistration(champs("xgb", "rf", "logreg"), C, "2026-09-13")

    assert "validation" in prereg["selected_on"]
    assert "test not yet scored" in prereg["selected_on"]
    assert "BEFORE any test scoring" in prereg["note"]
