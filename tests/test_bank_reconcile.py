"""Tests for scripts/bank_reconcile.py against data/synthetic/."""
from __future__ import annotations

import bank_reconcile


def _reconciled(synthetic_dir, tolerance_days=3):
    bank = bank_reconcile._load(str(synthetic_dir / "bank_statement.csv"),
                                "reference")
    ledger = bank_reconcile._load(str(synthetic_dir / "ledger.csv"),
                                  "entry_ref")
    return bank_reconcile.reconcile(bank, ledger, tolerance_days)


def test_synthetic_data_match_counts(synthetic_dir):
    result = _reconciled(synthetic_dir)
    exact = [m for m in result["matches"] if m["match_type"] == "exact"]
    fuzzy = [m for m in result["matches"] if m["match_type"] == "date-tolerance"]
    assert len(exact) == 6
    assert len(fuzzy) == 2
    assert len(result["unmatched_bank"]) == 1
    assert len(result["unmatched_ledger"]) == 1


def test_unmatched_items_are_the_designed_ones(synthetic_dir):
    result = _reconciled(synthetic_dir)
    assert result["unmatched_bank"]["reference"].tolist() == ["B-1009"]
    assert result["unmatched_ledger"]["entry_ref"].tolist() == ["JE-7009"]


def test_fuzzy_pairs_match_on_amount_within_tolerance(synthetic_dir):
    result = _reconciled(synthetic_dir)
    fuzzy = {m["bank_ref"]: m["ledger_ref"] for m in result["matches"]
             if m["match_type"] == "date-tolerance"}
    assert fuzzy == {"B-1006": "JE-7006", "B-1008": "JE-7008"}


def test_zero_tolerance_disables_fuzzy_matching(synthetic_dir):
    result = _reconciled(synthetic_dir, tolerance_days=0)
    assert len(result["matches"]) == 6
    assert all(m["match_type"] == "exact" for m in result["matches"])
    assert len(result["unmatched_bank"]) == 3
    assert len(result["unmatched_ledger"]) == 3


def test_cli_writes_output_file(synthetic_dir, tmp_path):
    out = tmp_path / "recon.txt"
    exit_code = bank_reconcile.main([
        str(synthetic_dir / "bank_statement.csv"),
        str(synthetic_dir / "ledger.csv"),
        "--output", str(out),
    ])
    assert exit_code == 0
    report = out.read_text(encoding="utf-8")
    assert "Matched: 8 (6 exact, 2 within 3-day tolerance)" in report
    assert "B-1009" in report and "JE-7009" in report
