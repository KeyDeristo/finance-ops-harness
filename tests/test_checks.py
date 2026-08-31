"""Tests for the checks/ modules — on the real repo and on crafted bad states."""
from __future__ import annotations

import json

import check_jurisdiction
import check_progress
import check_structure


def test_repo_passes_all_checks(repo_root):
    assert check_structure.run(repo_root) == []
    assert check_progress.run(repo_root) == []
    assert check_jurisdiction.run(repo_root) == []


def _write_progress(tmp_path, tasks, current="# Current task\n\n_No task in progress._\n"):
    progress = tmp_path / "progress"
    progress.mkdir()
    (progress / "tasks.json").write_text(json.dumps(tasks), encoding="utf-8")
    (progress / "current.md").write_text(current, encoding="utf-8")


def _task(**overrides):
    task = {
        "id": "T-001", "title": "t", "description": "d",
        "acceptance_criteria": ["c"], "status": "pending",
        "evidence": [], "owner": "",
    }
    task.update(overrides)
    return task


def test_done_without_evidence_fails(tmp_path):
    _write_progress(tmp_path, [_task(status="done", owner="bookkeeper")])
    problems = check_progress.run(tmp_path)
    assert any("C-02" in p for p in problems)


def test_done_with_evidence_passes(tmp_path):
    _write_progress(tmp_path, [_task(status="done", owner="bookkeeper",
                                     evidence=["file: progress/x.txt — report"])])
    assert check_progress.run(tmp_path) == []


def test_two_in_progress_tasks_fail(tmp_path):
    _write_progress(
        tmp_path,
        [_task(id="T-001", status="in_progress", owner="bookkeeper"),
         _task(id="T-002", status="in_progress", owner="bookkeeper")],
        current="# Current task\n\nWorking on T-001.\n")
    problems = check_progress.run(tmp_path)
    assert any("one task at a time" in p for p in problems)


def test_in_progress_with_empty_current_md_fails(tmp_path):
    _write_progress(tmp_path, [_task(status="in_progress", owner="bookkeeper")])
    problems = check_progress.run(tmp_path)
    assert any("empty state" in p for p in problems)


def test_duplicate_task_ids_fail(tmp_path):
    _write_progress(tmp_path, [_task(id="T-001"), _task(id="T-001")])
    problems = check_progress.run(tmp_path)
    assert any("duplicate" in p for p in problems)


def _write_jurisdiction(tmp_path, content):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "jurisdiction.yaml").write_text(content, encoding="utf-8")


def test_template_as_active_profile_fails(tmp_path):
    _write_jurisdiction(tmp_path, (
        'active_profile: "_TEMPLATE"\n'
        'profiles:\n  "_TEMPLATE":\n    country_name: ""\n'))
    problems = check_jurisdiction.run(tmp_path)
    assert any("_TEMPLATE" in p for p in problems)


def test_incomplete_profile_fails(tmp_path):
    _write_jurisdiction(tmp_path, (
        'active_profile: "XX"\n'
        'profiles:\n'
        '  "XX":\n'
        '    country_name: Testland\n'
        '    currency: XTS\n'))
    problems = check_jurisdiction.run(tmp_path)
    assert any("chart_of_accounts_standard" in p for p in problems)
    assert any("vat" in p for p in problems)
    assert any("retention_years" in p for p in problems)


def test_invalid_cadence_fails(tmp_path):
    _write_jurisdiction(tmp_path, (
        'active_profile: "XX"\n'
        'profiles:\n'
        '  "XX":\n'
        '    country_name: Testland\n'
        '    currency: XTS\n'
        '    chart_of_accounts_standard: local\n'
        '    statutory_export_format: none\n'
        '    e_invoicing_standard: none\n'
        '    vat: {filing_cadence: fortnightly}\n'
        '    retention_years: 5\n'
        '    statutory_reporting_deadlines:\n'
        '      - {name: n, frequency: annual, deadline_rule: r}\n'))
    problems = check_jurisdiction.run(tmp_path)
    assert any("filing_cadence" in p for p in problems)


def test_missing_structure_reported(tmp_path):
    problems = check_structure.run(tmp_path)
    assert any("AGENTS.md" in p for p in problems)
