"""Run all harness checks with clear output and a meaningful exit code.

Usage: python checks/run_all.py
Exit code 0 = all checks pass, 1 = at least one problem found.

To add a check: create checks/check_<name>.py exposing
run(root: Path) -> list[str] (empty list = pass) and add it to CHECKS below.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_jurisdiction
import check_progress
import check_structure

CHECKS = [
    ("structure", check_structure),
    ("progress", check_progress),
    ("jurisdiction", check_jurisdiction),
]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    total_problems = 0

    print("Running harness checks")
    print("=" * 60)
    for name, module in CHECKS:
        problems = module.run(root)
        status = "PASS" if not problems else "FAIL"
        print(f"[{status}] check_{name}")
        for p in problems:
            print(f"       - {p}")
        total_problems += len(problems)
    print("=" * 60)

    if total_problems:
        print(f"RESULT: FAIL ({total_problems} problem(s) across "
              f"{len(CHECKS)} checks)")
        return 1
    print(f"RESULT: PASS ({len(CHECKS)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
