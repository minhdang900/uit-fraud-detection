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


class PreregistrationViolation(RuntimeError):
    """The champion on record no longer matches what validation now prefers.

    Raised rather than handled: a pre-registration that quietly updates itself
    proves nothing, because it would agree with every run by construction.
    """


def build_preregistration(champions, c_review, today):
    """The dated record declaring a champion BEFORE test is ever scored."""
    if not champions:
        raise ValueError("cannot pre-register an empty champion list")
    declared = f"{champions[0]['family']}/{champions[0]['arm']}"
    return {
        "date": str(today),
        "selected_on": "validation split only; test not yet scored",
        "c_review": c_review,
        "champions": champions,
        "declared_winner": declared,
        "note": ("Declared BEFORE any test scoring. The headline number is this "
                 "model's test cost whether or not it turns out lowest on test."),
    }


def verify_preregistration(recorded, champions, c_review):
    """Check a rerun against an existing pre-registration.

    Returns the recorded dict unchanged when the run still agrees with it.
    Raises `PreregistrationViolation` otherwise -- the caller must NOT paper
    over this by rewriting the file, because the file's only value is that it
    was written before the test set was touched.

    `c_review` is checked too: the champion was chosen to minimise cost under
    one review fee, so a different fee makes the record inapplicable even when
    the same model happens to come out on top.
    """
    declared = f"{champions[0]['family']}/{champions[0]['arm']}"

    if recorded["declared_winner"] != declared:
        raise PreregistrationViolation(
            f"PRE-REGISTRATION VIOLATED\n"
            f"  recorded {recorded['date']}: {recorded['declared_winner']}\n"
            f"  this run              : {declared}\n"
            f"The champion was declared in writing before test was scored. It has\n"
            f"now changed, so every claim resting on it is void. Explain why in the\n"
            f"report, or pass --rewrite-preregistration to start a NEW, honestly\n"
            f"dated pre-registration (which invalidates the old test results)."
        )

    if recorded["c_review"] != c_review:
        raise PreregistrationViolation(
            f"c_review changed ({recorded['c_review']} -> {c_review}); the recorded "
            f"champion was selected under the old cost and no longer applies."
        )

    return recorded
