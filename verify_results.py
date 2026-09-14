"""Re-derive the published headline numbers from the stored artifacts.

Nothing here reads a cached result table. Every figure is recomputed from the
raw probability arrays, so these functions detect drift anywhere in the chain:
threshold selection, confusion counting, or the cost function itself.
"""
import json
from pathlib import Path

import numpy as np

import paths
from fraud_cost import optimal_threshold, total_cost

ROOT = Path(__file__).resolve().parent


def reproduce_headline(c_review=3.0, artifacts_dir=None):
    """Recompute the report's headline figures from stored probabilities.

    The decision threshold is re-derived from the VALIDATION arrays and then
    applied to the TEST arrays -- the same order the pipeline used, and the
    same order the integrity claim depends on. Reading a cached threshold
    would make these tests vacuous.
    """
    art = Path(artifacts_dir) if artifacts_dir else paths.artifacts_dir()

    champion = json.loads((art / "preregistration.json").read_text())["declared_winner"]

    va = np.load(art / "val_probabilities.npz")
    te = np.load(art / "test_probabilities.npz")

    threshold, _, _ = optimal_threshold(
        va["y"], va[champion], va["amounts"], c_review
    )

    y, amounts, p = te["y"], te["amounts"], te[champion]
    pred = (p >= threshold).astype(int)

    is_fraud = y == 1
    caught = is_fraud & (pred == 1)
    missed = is_fraud & (pred == 0)

    return {
        "champion": champion,
        "threshold": float(threshold),
        "champion_test_cost": float(total_cost(y, pred, amounts, c_review)),
        "test_rows": int(len(y)),
        "test_frauds": int(is_fraud.sum()),
        "test_fraud_value": float(amounts[is_fraud].sum()),
        "caught": int(caught.sum()),
        "recovered": float(amounts[caught].sum()),
        "lost": float(amounts[missed].sum()),
        "alerts": int(pred.sum()),
        "reviews": float(c_review * pred.sum()),
    }
