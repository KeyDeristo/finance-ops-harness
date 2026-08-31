"""Tests for scripts/saft_validate.py against data/synthetic/saft_sample.xml."""
from __future__ import annotations

import pytest

import saft_validate


@pytest.fixture(scope="module")
def sample_text(synthetic_dir):
    return (synthetic_dir / "saft_sample.xml").read_text(encoding="utf-8")


def test_sample_is_valid(synthetic_dir):
    errors, warnings = saft_validate.validate(synthetic_dir / "saft_sample.xml")
    assert errors == []
    assert warnings == []


def test_missing_section_is_an_error(sample_text, tmp_path):
    broken = sample_text.replace("<MasterFiles>", "<Ignored>") \
                        .replace("</MasterFiles>", "</Ignored>")
    path = tmp_path / "broken.xml"
    path.write_text(broken, encoding="utf-8")
    errors, _ = saft_validate.validate(path)
    assert any("MasterFiles" in e for e in errors)


def test_unbalanced_transaction_is_an_error(sample_text, tmp_path):
    broken = sample_text.replace("<Amount>4200.50</Amount>\n          </CreditAmount>",
                                 "<Amount>4200.49</Amount>\n          </CreditAmount>")
    assert broken != sample_text
    path = tmp_path / "unbalanced.xml"
    path.write_text(broken, encoding="utf-8")
    errors, _ = saft_validate.validate(path)
    assert any("unbalanced" in e and "JE-7002" in e for e in errors)
    # The declared totals no longer match the computed ones either.
    assert any("TotalCredit" in e for e in errors)


def test_unknown_account_is_an_error(sample_text, tmp_path):
    broken = sample_text.replace("<AccountID>6340</AccountID>\n          <DebitAmount>",
                                 "<AccountID>9999</AccountID>\n          <DebitAmount>")
    assert broken != sample_text
    path = tmp_path / "unknown_account.xml"
    path.write_text(broken, encoding="utf-8")
    errors, _ = saft_validate.validate(path)
    assert any("9999" in e and "GeneralLedgerAccounts" in e for e in errors)


def test_wrong_country_is_a_warning_not_error(sample_text, tmp_path):
    broken = sample_text.replace("<AuditFileCountry>NO</AuditFileCountry>",
                                 "<AuditFileCountry>SE</AuditFileCountry>")
    path = tmp_path / "wrong_country.xml"
    path.write_text(broken, encoding="utf-8")
    errors, warnings = saft_validate.validate(path)
    assert errors == []
    assert any("AuditFileCountry" in w for w in warnings)


def test_not_xml_is_an_error(tmp_path):
    path = tmp_path / "not_xml.xml"
    path.write_text("this is not xml", encoding="utf-8")
    errors, _ = saft_validate.validate(path)
    assert any("not well-formed" in e for e in errors)


def test_cli_exit_codes(synthetic_dir, tmp_path):
    assert saft_validate.main([str(synthetic_dir / "saft_sample.xml")]) == 0
    bad = tmp_path / "bad.xml"
    bad.write_text("<AuditFile><Header/></AuditFile>", encoding="utf-8")
    assert saft_validate.main([str(bad)]) == 1
