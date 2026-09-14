"""Where the submission bundle lives, resolved in one place.

The bundle sits OUTSIDE this repository (`../08-Nop-bai`) because it is a
deliverable, not source: it carries generated PDFs and a frozen copy of the
code, and versioning that alongside the code it was copied from invites the
two to drift.

That placement means the path is no longer a constant, so it is resolved here
rather than hard-coded in each caller. In particular the container bind-mounts
only the repo, so inside Docker the bundle is reachable at NOP_BAI_DIR and
nowhere else -- see the `nop-bai` volume in docker-compose.yml.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUNDLE_NAME = "08-Nop-bai"


def bundle_dir():
    """The submission bundle, or None if this checkout has no copy of it.

    Order matters: an explicit override wins, then the case where this code is
    itself the frozen copy inside the bundle, then the normal sibling layout.
    """
    override = os.environ.get("NOP_BAI_DIR")
    if override:
        p = Path(override)
        return p if p.is_dir() else None

    # Running from <bundle>/03-Source-code: the bundle is our parent.
    if (ROOT.parent / "01-Bao-cao").is_dir():
        return ROOT.parent

    # Normal layout: sibling of the repo.
    sibling = ROOT.parent / BUNDLE_NAME
    if sibling.is_dir():
        return sibling

    return None


def require_bundle_dir():
    """Same, but refuses to carry on without it.

    Used by the figure generator: silently writing 14 PNGs into a freshly
    created empty directory, while the real bundle keeps the stale ones, is
    the failure this prevents.
    """
    found = bundle_dir()
    if found is None:
        raise SystemExit(
            f"Cannot find the submission bundle ({BUNDLE_NAME}/).\n"
            f"  looked at: $NOP_BAI_DIR, {ROOT.parent / '01-Bao-cao'}, "
            f"{ROOT.parent / BUNDLE_NAME}\n"
            f"Inside Docker it is mounted at /nop-bai -- if that is missing, "
            f"run `docker compose up -d --build` to pick up the volume."
        )
    return found


ARTIFACTS_IN_BUNDLE = ("04-Ket-qua", "artifacts")


def artifacts_dir(must_exist=True):
    """Where the stored probability arrays and result tables actually are.

    Two layouts, one resolver. In the repo they sit next to the code as
    `artifacts/`. In the frozen copy inside the bundle they do NOT: bundling
    moves them to `04-Ket-qua/artifacts/` so the deliverable groups results
    together. Hard-coding `ROOT / "artifacts"` therefore breaks every
    reproducibility check the moment the code is read from the bundle -- which
    is exactly where a grader reads it.

    Resolution order: the local directory wins (a repo checkout, or a bundle
    that genuinely has its own), then the bundle's results directory.

    `must_exist=False` is for the writer: `run_model_matrix.py` must be able to
    name a directory that does not exist yet on a fresh checkout and create it.
    """
    local = ROOT / "artifacts"
    if local.is_dir():
        return local

    bundle = bundle_dir()
    if bundle is not None:
        candidate = bundle.joinpath(*ARTIFACTS_IN_BUNDLE)
        if candidate.is_dir():
            return candidate

    if must_exist:
        raise SystemExit(
            "Cannot find the artifacts directory.\n"
            f"  looked at: {local}\n"
            f"             {bundle.joinpath(*ARTIFACTS_IN_BUNDLE) if bundle else '(no bundle found)'}\n"
            "Generate them with: docker compose exec -T lab python run_model_matrix.py"
        )
    return local
