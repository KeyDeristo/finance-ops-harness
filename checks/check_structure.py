"""Check that mandatory files exist and have the expected basic format.

Exposes run(root) -> list of problem strings (empty list = pass).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "LICENSE",
    "init.sh",
    "requirements.txt",
    ".claude/settings.json",
    ".claude/agents/bookkeeper.md",
    ".claude/agents/reviewer.md",
    ".claude/agents/explorer.md",
    "docs/CONVENTIONS.md",
    "docs/CONTROLS.md",
    "docs/ARCHITECTURE.md",
    "docs/sops/_TEMPLATE.md",
    "docs/sops/p2p.md",
    "docs/sops/o2c.md",
    "docs/sops/expenses.md",
    "docs/sops/month-end.md",
    "rules/coding-rules.yaml",
    "rules/jurisdiction.yaml",
    "scripts/bank_reconcile.py",
    "scripts/invoice_classify.py",
    "scripts/saft_validate.py",
    "checks/run_all.py",
    "checks/check_structure.py",
    "checks/check_progress.py",
    "checks/check_jurisdiction.py",
    "checks/init.py",
    "progress/current.md",
    "progress/history.md",
    "progress/tasks.json",
    "data/synthetic/bank_statement.csv",
    "data/synthetic/ledger.csv",
    "data/synthetic/invoices.csv",
    "data/synthetic/saft_sample.xml",
]

# Sections every agent relies on finding in AGENTS.md.
AGENTS_MD_REQUIRED_SECTIONS = [
    "Startup protocol",
    "Finding your task",
    "Repo map",
    "Hard rules",
    "How a task ends",
]


def run(root: Path) -> list[str]:
    problems: list[str] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            problems.append(f"missing mandatory file: {rel}")
        elif path.stat().st_size == 0:
            problems.append(f"mandatory file is empty: {rel}")
    if problems:
        # Format checks below assume the files exist; report absences first.
        return problems

    agents_md = (root / "AGENTS.md").read_text(encoding="utf-8")
    for section in AGENTS_MD_REQUIRED_SECTIONS:
        if section not in agents_md:
            problems.append(f"AGENTS.md: required section not found: {section!r}")

    for rel in (".claude/agents/bookkeeper.md",
                ".claude/agents/reviewer.md",
                ".claude/agents/explorer.md"):
        text = (root / rel).read_text(encoding="utf-8")
        if not text.startswith("---") or "name:" not in text.split("---")[1]:
            problems.append(f"{rel}: missing YAML frontmatter with a 'name:' field")

    for rel in ("rules/coding-rules.yaml", "rules/jurisdiction.yaml"):
        try:
            yaml.safe_load((root / rel).read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            problems.append(f"{rel}: not valid YAML ({exc})")

    try:
        with (root / ".claude/settings.json").open(encoding="utf-8") as fh:
            json.load(fh)
    except json.JSONDecodeError as exc:
        problems.append(f".claude/settings.json: not valid JSON ({exc})")

    tests_dir = root / "tests"
    if not tests_dir.is_dir() or not any(tests_dir.glob("test_*.py")):
        problems.append("tests/: directory missing or contains no test_*.py files")

    init_sh = (root / "init.sh").read_bytes()
    if b"\r\n" in init_sh:
        problems.append("init.sh: contains CRLF line endings (breaks on Linux/macOS)")

    return problems


def main() -> int:
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print(f"  FAIL {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
