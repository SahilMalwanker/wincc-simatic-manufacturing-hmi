import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import tia_printout  # noqa: E402

PRINTOUT = ROOT / "docs" / "pdf" / "tia-portal-project-documentation.pdf"


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def printout() -> tia_printout.Printout:
    return tia_printout.parse_printout(PRINTOUT)
