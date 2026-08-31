"""Check that progress/tasks.json is valid and consistent with current.md.

Enforces control C-02 mechanically: nothing is `done` without evidence.

Exposes run(root) -> list of problem strings (empty list = pass).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_KEYS = {"id", "title", "description", "acceptance_criteria",
                 "status", "evidence", "owner"}
VALID_STATUSES = {"pending", "in_progress", "done", "blocked"}

# progress/current.md in its empty state contains this marker (see CONVENTIONS.md).
EMPTY_MARKER = "No task in progress"


def run(root: Path) -> list[str]:
    problems: list[str] = []

    tasks_path = root / "progress" / "tasks.json"
    current_path = root / "progress" / "current.md"
    if not tasks_path.is_file():
        return ["progress/tasks.json is missing"]
    if not current_path.is_file():
        return ["progress/current.md is missing"]

    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"progress/tasks.json is not valid JSON: {exc}"]

    if not isinstance(tasks, list):
        return ["progress/tasks.json must be a JSON list of task objects"]

    seen_ids: set[str] = set()
    in_progress_count = 0

    for i, task in enumerate(tasks):
        label = f"task[{i}]"
        if not isinstance(task, dict):
            problems.append(f"{label}: not an object")
            continue
        task_id = task.get("id", "")
        if task_id:
            label = str(task_id)

        missing = REQUIRED_KEYS - task.keys()
        if missing:
            problems.append(f"{label}: missing keys: {', '.join(sorted(missing))}")
            continue

        if not task_id or not isinstance(task_id, str):
            problems.append(f"{label}: 'id' must be a non-empty string")
        elif task_id in seen_ids:
            problems.append(f"{label}: duplicate task id")
        else:
            seen_ids.add(task_id)

        status = task["status"]
        if status not in VALID_STATUSES:
            problems.append(
                f"{label}: invalid status {status!r} "
                f"(expected one of: {', '.join(sorted(VALID_STATUSES))})")
            continue

        criteria = task["acceptance_criteria"]
        if (not isinstance(criteria, list) or not criteria
                or not all(isinstance(c, str) and c.strip() for c in criteria)):
            problems.append(f"{label}: acceptance_criteria must be a non-empty "
                            f"list of non-empty strings")

        evidence = task["evidence"]
        if not isinstance(evidence, list):
            problems.append(f"{label}: evidence must be a list")
            evidence = []

        if status == "done":
            if not evidence or not all(isinstance(e, str) and e.strip()
                                       for e in evidence):
                problems.append(
                    f"{label}: status is 'done' but evidence is empty or "
                    f"invalid — control C-02: nothing is done without evidence")
            if not str(task["owner"]).strip():
                problems.append(f"{label}: status is 'done' but owner is empty")

        if status == "in_progress":
            in_progress_count += 1
            if not str(task["owner"]).strip():
                problems.append(f"{label}: status is 'in_progress' but owner is empty")

    if in_progress_count > 1:
        problems.append(
            f"{in_progress_count} tasks are in_progress — the harness works "
            f"one task at a time (see AGENTS.md §2)")

    current = current_path.read_text(encoding="utf-8")
    current_is_empty = EMPTY_MARKER in current
    if in_progress_count > 0 and current_is_empty:
        problems.append(
            "a task is in_progress but progress/current.md is in its empty "
            "state — work must be reflected in current.md (AGENTS.md §2)")
    has_blocked = any(isinstance(t, dict) and t.get("status") == "blocked"
                      for t in tasks)
    if in_progress_count == 0 and not has_blocked and not current_is_empty:
        problems.append(
            "progress/current.md describes work but no task is in_progress "
            "or blocked in tasks.json")

    return problems


def main() -> int:
    problems = run(Path(__file__).resolve().parent.parent)
    for p in problems:
        print(f"  FAIL {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
