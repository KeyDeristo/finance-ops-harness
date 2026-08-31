"""Tests for scripts/invoice_classify.py against data/synthetic/ and rules/."""
from __future__ import annotations

import pandas as pd
import pytest

import invoice_classify


@pytest.fixture(scope="module")
def rules(repo_root):
    return invoice_classify.load_rules(repo_root / "rules" / "coding-rules.yaml")


@pytest.fixture(scope="module")
def proposals(synthetic_dir, rules):
    invoices = pd.read_csv(synthetic_dir / "invoices.csv", encoding="utf-8")
    df = invoice_classify.classify_all(invoices, rules)
    return df.set_index("invoice_id")


def test_supplier_rule_wins(proposals):
    row = proposals.loc["SI-1001"]
    assert row["proposed_account"] == "6340"
    assert row["proposed_cost_center"] == "CC-FAC"
    assert row["rule_type"] == "supplier"
    assert row["confidence"] == 0.95
    assert not row["needs_review"]


def test_supplier_rule_beats_amount_range(proposals):
    # SI-1002 is above the capitalization threshold but has a supplier rule.
    row = proposals.loc["SI-1002"]
    assert row["rule_type"] == "supplier"
    assert row["proposed_account"] == "6420"


def test_keyword_rule(proposals):
    row = proposals.loc["SI-1004"]
    assert row["rule_type"] == "keyword"
    assert row["proposed_account"] == "7140"
    assert row["proposed_cost_center"] == "CC-SAL"
    assert not row["needs_review"]


def test_amount_range_rule_needs_review(proposals):
    row = proposals.loc["SI-1006"]
    assert row["rule_type"] == "amount_range"
    assert row["proposed_account"] == "1250"
    assert row["needs_review"]


def test_fallback_needs_review(proposals):
    row = proposals.loc["SI-1007"]
    assert row["rule_type"] == "fallback"
    assert row["proposed_account"] == "7790"
    assert row["confidence"] == 0.30
    assert row["needs_review"]


def test_every_invoice_gets_a_proposal(proposals):
    assert len(proposals) == 8
    assert (proposals["proposed_account"] != "").all()
    assert proposals["confidence"].between(0, 1).all()


def test_needs_review_count(proposals):
    # Exactly the amount-range item and the fallback item are below threshold.
    assert proposals["needs_review"].sum() == 2


def test_llm_stub_returns_none():
    # The template ships with no model integration: the extension point is inert.
    assert invoice_classify.llm_propose({}, {}) is None


def test_cli_writes_output_csv(synthetic_dir, tmp_path):
    out = tmp_path / "proposals.csv"
    exit_code = invoice_classify.main([
        str(synthetic_dir / "invoices.csv"), "--output", str(out)])
    assert exit_code == 0
    saved = pd.read_csv(out, encoding="utf-8")
    assert len(saved) == 8
    assert saved["needs_review"].sum() == 2
