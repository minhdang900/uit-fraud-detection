"""Model matrix and champion selection (Do an CS114, plan Step 4)."""


def select_champion_per_family(results):
    """Best-costing variant of each algorithm family, cheapest family first.

    Deliberately NOT the global top-N. Taking the global top 3 by cost can
    return three variants of one algorithm and silently drop the others,
    failing the course's "at least 3 models" requirement while appearing to
    satisfy it. Selecting per family guarantees every algorithm is
    represented by its own best arm.

    `results` is a list of dicts with at least "family", "arm" and "cost".
    """
    if not results:
        raise ValueError("no results to select a champion from")

    best_by_family = {}
    for r in results:
        current = best_by_family.get(r["family"])
        if current is None or r["cost"] < current["cost"]:
            best_by_family[r["family"]] = r

    return sorted(best_by_family.values(), key=lambda r: r["cost"])
