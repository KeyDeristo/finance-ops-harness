"""Harness entry point: verify environment, run all checks, run the tests.

This is the cross-platform startup protocol (control C-09):

  Linux/macOS/Git Bash:  ./init.sh          (thin wrapper around this file)
  Windows:               python checks/init.py

Steps:
  1. environment  - Python >= 3.11, pandas + pyyaml importable, pytest available
  2. checks       - checks/run_all.py (structure, progress, jurisdiction)
  3. tests        - pytest -q

Prints a clear OK/FAIL summary and exits non-zero if anything fails.
Agents: if this fails, stop and report -- do not work (AGENTS.md, section 1).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 11)


def check_environment() -> tuple[bool, str]:
    if sys.version_info < MIN_PYTHON:
        return False, (f"Python {sys.version_info.major}.{sys.version_info.minor} "
                       f"found; {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required")
    missing = []
    for module in ("pandas", "yaml", "pytest"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        return False, (f"missing dependencies: {', '.join(missing)} "
                       f"(run: python -m pip install -r requirements.txt)")
    return True, (f"Python {sys.version_info.major}.{sys.version_info.minor}."
                  f"{sys.version_info.micro}, dependencies present")


def run_step(argv: list[str]) -> tuple[bool, str]:
    # We decode the child's output as UTF-8, so the child must encode it as
    # UTF-8. Without PYTHONIOENCODING a Python child writing to a pipe uses the
    # locale encoding (cp1252 on a default Windows install), which would mangle
    # any non-ASCII character on the way back here.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def main() -> int:
    steps: list[tuple[str, bool, str]] = []

    ok, detail = check_environment()
    steps.append(("environment", ok, detail))

    if ok:
        checks_ok, checks_out = run_step(
            [sys.executable, str(ROOT / "checks" / "run_all.py")])
        steps.append(("checks", checks_ok, checks_out))

        tests_ok, tests_out = run_step(
            [sys.executable, "-m", "pytest", "-q", str(ROOT / "tests")])
        steps.append(("tests", tests_ok, tests_out))
    else:
        steps.append(("checks", False, "skipped: environment check failed"))
        steps.append(("tests", False, "skipped: environment check failed"))

    print("finance-ops-harness init")
    print("=" * 60)
    failed = False
    for name, step_ok, detail in steps:
        status = "OK  " if step_ok else "FAIL"
        print(f"[{status}] {name}")
        if not step_ok:
            failed = True
        # Full output on failure; one summary line on success.
        if not step_ok and detail:
            for line in detail.splitlines():
                print(f"       {line}")
        elif detail:
            summary = detail.splitlines()[-1]
            print(f"       {summary}")
    print("=" * 60)

    if failed:
        print("RESULT: FAIL -- do not work on top of a failing harness. "
              "Fix the problems above and rerun.")
        return 1
    print("RESULT: OK -- harness verified, safe to start work.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
