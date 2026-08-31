"""Make scripts/ and checks/ importable and expose shared fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
for path in (ROOT, ROOT / "scripts", ROOT / "checks"):
    sys.path.insert(0, str(path))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def synthetic_dir() -> Path:
    return ROOT / "data" / "synthetic"
