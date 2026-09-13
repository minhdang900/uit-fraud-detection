"""Tests for model selection logic (plan Step 4, AC-8)."""
import pytest

from modeling import select_champion_per_family


def test_champion_selection_keeps_one_model_per_family():
    """Critic M2: "carry the top 3 forward" can silently break the rubric.

    The course requires at least 3 models. Taking the global top 3 by cost can
    return three variants of ONE algorithm, dropping the others entirely --
    which fails the requirement while looking like it passed.

    This fixture is built so the two strategies diverge:

      family   arm        cost
      logreg   none        900
      logreg   balanced    800
      rf       none        500
      rf       balanced    400
      xgb      none        300
      xgb      balanced    200

    Global top 3 by cost -> xgb/balanced, xgb/none, rf/balanced.
      Two XGBoost variants, and logreg vanishes: only 2 algorithms survive.
    Per family     -> xgb/balanced (200), rf/balanced (400), logreg/balanced (800).
      All three algorithms survive, each represented by its best arm.
    """
    results = [
        {"family": "logreg", "arm": "none", "cost": 900.0},
        {"family": "logreg", "arm": "balanced", "cost": 800.0},
        {"family": "rf", "arm": "none", "cost": 500.0},
        {"family": "rf", "arm": "balanced", "cost": 400.0},
        {"family": "xgb", "arm": "none", "cost": 300.0},
        {"family": "xgb", "arm": "balanced", "cost": 200.0},
    ]

    champions = select_champion_per_family(results)

    # one per family, cheapest first
    assert [c["family"] for c in champions] == ["xgb", "rf", "logreg"]
    assert [c["arm"] for c in champions] == ["balanced", "balanced", "balanced"]
    assert [c["cost"] for c in champions] == [200.0, 400.0, 800.0]

    # the rubric's minimum is met by construction, not by luck
    assert len({c["family"] for c in champions}) == 3


def test_champion_selection_rejects_an_empty_result_set():
    """A silent empty list would mean "no models to carry forward" sailing
    through to test scoring. Fail loudly instead."""
    with pytest.raises(ValueError):
        select_champion_per_family([])
