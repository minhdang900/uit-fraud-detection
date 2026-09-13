"""Preprocessing for the fraud detection dataset (Do an CS114)."""
import numpy as np
from sklearn.model_selection import train_test_split


def hour_of_day(time_seconds):
    """Hour of day (0-23) from `Time`, seconds since the first transaction.

    The dataset spans ~48 hours, so the modulo is what makes day 2 line up
    with day 1 instead of occupying hours 24-47.
    """
    return (np.asarray(time_seconds) // 3600 % 24).astype(int)


def cyclic_encode_hour(hours):
    """Encode hour-of-day as (sin, cos) of its angle around the clock.

    Returns an (n, 2) array. Linear scaling would place 23:00 and 00:00 at
    opposite ends of the feature range despite being one hour apart; this
    keeps the wrap continuous so "late night" is a single region.
    """
    angle = 2.0 * np.pi * np.asarray(hours, dtype=float) / 24.0
    return np.column_stack([np.sin(angle), np.cos(angle)])


def stratified_split_60_20_20(y, random_state=42):
    """Stratified 60/20/20 split. Returns (train_idx, val_idx, test_idx).

    Stratification is not optional at a 0.172% positive rate: an unstratified
    split can leave a split with almost no frauds by luck, making its metrics
    meaningless. It also lets the report answer the rubric's question about
    imbalance in each split rather than assuming it carried over.
    """
    y = np.asarray(y)
    idx = np.arange(len(y))

    trainval, test = train_test_split(
        idx, test_size=0.2, stratify=y, random_state=random_state
    )
    # 0.25 of the remaining 80% is 20% of the whole
    train, val = train_test_split(
        trainval, test_size=0.25, stratify=y[trainval], random_state=random_state
    )
    return train, val, test
