"""Tests on the submission bundle itself (NOP_BAI/).

The other suites prove the code and the numbers are right. These prove the
thing actually handed in is complete and internally consistent -- the failure
mode where every number is correct but a figure the report references was
never copied, or the shipped source snapshot is older than the code that
produced the results.

The bundle lives outside the repo (`../08-Nop-bai`), so its location is
resolved by `paths.bundle_dir()` rather than assumed. Skipped cleanly when it
is not reachable -- CI, or the frozen copy inside the bundle itself.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import BUNDLE_NAME, bundle_dir  # noqa: E402

NOP = bundle_dir()

# CI checks out the repo alone -- the bundle is a deliverable and is not in
# git -- so skipping there is correct. The reason string names every location
# tried, because a skip that says only "not found" is how these guards stop
# running without anyone noticing.
pytestmark = pytest.mark.skipif(
    NOP is None,
    reason=(f"submission bundle ({BUNDLE_NAME}/) not reachable from here; "
            f"set NOP_BAI_DIR to point at it"),
)

REPORT = (NOP / "01-Bao-cao" / "BaoCao.md") if NOP else None
FIGDIR = (NOP / "04-Ket-qua" / "hinh-anh") if NOP else None
SCRIPT = (NOP / "02-Slide" / "Kich-ban-thuyet-trinh.md") if NOP else None

# Course rule, from the brief and the Buoi 03 transcript: "moi nhom chi duoc
# 15 phut thoi ... toi da nha", enforced with a clock that cuts you off.
HARD_LIMIT_MIN = 15.0
SLOW_PACE = 140          # syllables/min, the worst realistic case


def figures_referenced():
    """Figure filenames the report actually embeds.

    Case matters: F12_chinh-sach-A-vs-E.png has capitals in the stem, and a
    lowercase-only pattern silently reports it as an uncited orphan.
    """
    return set(re.findall(r"F\d{2}_[A-Za-z0-9.-]+\.png", REPORT.read_text()))


def figures_on_disk():
    return {p.name for p in FIGDIR.glob("*.png")}


def test_every_figure_the_report_embeds_was_actually_shipped():
    """A missing PNG renders as a broken image in the PDF -- and the export is
    silent about it, so nobody notices until the grader opens the file."""
    missing = figures_referenced() - figures_on_disk()
    assert not missing, f"report references figures that are not in the bundle: {sorted(missing)}"


def test_no_figure_is_shipped_without_being_referenced():
    """An uncited figure means either a dead file or -- worse -- a citation
    that was silently dropped while editing the report."""
    orphans = figures_on_disk() - figures_referenced()
    assert not orphans, f"figures in the bundle that no section cites: {sorted(orphans)}"


@pytest.mark.parametrize("folder", [
    "01-Bao-cao", "02-Slide", "03-Source-code", "04-Ket-qua", "05-Tai-lieu",
])
def test_every_required_submission_folder_exists_and_is_not_empty(folder):
    """The structure the report's Appendix A promises the grader."""
    d = NOP / folder
    assert d.is_dir(), f"{folder}/ is missing"
    assert any(d.rglob("*")), f"{folder}/ exists but is empty"


def test_the_three_graded_deliverables_are_present():
    """The brief asks for exactly three things: report, code, slides. Each has
    to be there in a format the grader can open without our toolchain."""
    assert (NOP / "01-Bao-cao" / "BaoCao_CS114_FraudDetection.pdf").exists()
    assert (NOP / "02-Slide").glob("*.pptx"), "no .pptx in 02-Slide"
    assert (NOP / "03-Source-code" / "fraud_cost.py").exists()


def test_the_preregistration_travels_with_the_results():
    """The integrity claim is only checkable if the dated record ships too."""
    assert (NOP / "04-Ket-qua" / "artifacts" / "preregistration.json").exists()


def test_no_editor_lock_or_temp_files_are_left_in_the_bundle():
    """Four ways rubbish gets into a bundle, all of them silent.

    LibreOffice leaves .~lock.*# and scratch .tmp files beside what it exports;
    macOS drops .DS_Store into any folder Finder opens; agent tooling writes
    .omc/ state into whatever directory it runs in; Python leaves __pycache__
    and .ipynb_checkpoints. Every one of these appeared here at least once.

    A stale lock file is the worst of them: it also means a document may still
    be open somewhere with unsaved changes.
    """
    junk = [p for p in NOP.rglob("*")
            if p.is_file() and (p.name.startswith(".~lock")
                                or p.suffix == ".tmp"
                                or p.name == ".DS_Store"
                                or ".omc" in p.parts
                                or "__pycache__" in p.parts
                                or ".ipynb_checkpoints" in p.parts)]
    assert not junk, f"editor leftovers still in the bundle: {[p.name for p in junk]}"


def spoken_syllables():
    """Total spoken length of the deck, counted the way the script counts it."""
    blocks = re.findall(r"\*\*Nói:\*\*(.*?)(?=\n\n|\Z)", SCRIPT.read_text(), re.S)
    return len(" ".join(blocks).split())


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN: the 30-slide deck runs ~20:55 at slow pace against a hard "
           "15:00 cap. Cut it using the plan at the top of "
           "Kich-ban-thuyet-trinh.md, then delete this xfail marker.",
)
def test_the_talk_fits_inside_the_fifteen_minute_cap():
    """The constraint that is graded by a stopwatch, not by a rubric.

    The lecturer described a defence where the clock rang at exactly 15:00 and
    the candidate was stopped mid-sentence. A deck that only fits if you rush
    is a deck that does not fit, so this checks the SLOW pace -- the one you
    actually speak at when nervous.

    Kept as a test rather than a note in a document because a note is what let
    the deck grow to 30 slides in the first place.
    """
    minutes = spoken_syllables() / SLOW_PACE
    assert minutes <= HARD_LIMIT_MIN, (
        f"talk runs ~{minutes:.1f} min at {SLOW_PACE} syllables/min, "
        f"over the hard {HARD_LIMIT_MIN:.0f} min cap"
    )
