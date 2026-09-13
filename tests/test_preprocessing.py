"""Tests for preprocessing (plan Step 2, AC-4..AC-7).

Fixtures are synthetic so these run without the 144MB Kaggle CSV.
"""
import numpy as np

from preprocessing import (
    cyclic_encode_hour,
    hour_of_day,
    stratified_split_60_20_20,
)


def test_hour_of_day_wraps_at_the_day_boundary():
    """`Time` is seconds elapsed since the first transaction, spanning ~48h.

    The dataset covers two days, so second 86,400 is hour 0 of day 2 -- not
    hour 24. Without the modulo, day 2 would occupy hours 24-47 and never
    line up with day 1.

    seconds |  expected hour
          0 |   0
      3,600 |   1
     86,399 |  23   (last second of day 1)
     86,400 |   0   (first second of day 2)
     90,000 |   1
    """
    seconds = np.array([0, 3600, 86399, 86400, 90000])

    assert hour_of_day(seconds).tolist() == [0, 1, 23, 0, 1]


def _dist(encoded, i, j):
    return float(np.linalg.norm(encoded[i] - encoded[j]))


def test_cyclic_encoding_makes_hour_23_adjacent_to_hour_0():
    """Hour is cyclic; linear scaling is wrong about its geometry.

    Scaled linearly, hours 23 and 00 sit at opposite ends of the range --
    maximally far apart -- when they are in fact one hour apart. A model then
    cannot learn "late night" as a single region.

    Encoding each hour as (sin, cos) of its angle around the clock fixes it:

        angle = 2*pi*hour/24

    Two properties this must satisfy:
      1. 23 -> 0 is the same distance as 0 -> 1 (both one hour apart)
      2. 23 -> 0 is much closer than 0 -> 12 (opposite sides of the clock)
    """
    hours = np.arange(24)
    encoded = cyclic_encode_hour(hours)

    assert encoded.shape == (24, 2)

    # 1. adjacent hours are equidistant, including across the midnight wrap
    assert np.isclose(_dist(encoded, 23, 0), _dist(encoded, 0, 1))

    # 2. the wrap is near, the opposite side of the clock is far
    assert _dist(encoded, 23, 0) < _dist(encoded, 0, 12)


def test_stratified_split_preserves_the_fraud_rate_in_every_split():
    """AC-2/AC-6: 60/20/20, and imbalance must hold in EACH split.

    At a 0.172% fraud rate an unstratified split can hand a split very few
    frauds -- or none -- purely by luck, which would make its metrics
    meaningless. The rubric asks explicitly whether train/val/test are
    imbalanced, so this has to be demonstrable rather than assumed.

    1,000 rows with 20 frauds (2%):
      train 60% -> 600 rows, 12 frauds
      val   20% -> 200 rows,  4 frauds
      test  20% -> 200 rows,  4 frauds
    """
    y = np.zeros(1000, dtype=int)
    y[:20] = 1  # 20 frauds, 2%

    train, val, test = stratified_split_60_20_20(y, random_state=42)

    assert [len(train), len(val), len(test)] == [600, 200, 200]
    assert [int(y[train].sum()), int(y[val].sum()), int(y[test].sum())] == [12, 4, 4]

    # splits must be disjoint and cover everything
    assert len(set(train) | set(val) | set(test)) == 1000
