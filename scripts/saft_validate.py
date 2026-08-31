"""Basic structural validation of a Norwegian SAF-T Financial XML file.

This is the template's worked example of a jurisdiction-specific check (see
docs/ARCHITECTURE.md — the core is jurisdiction-agnostic; country checks like
this one live alongside it). It is NOT a full XSD validation: it checks the
structural essentials an accountant cares about before archiving/submitting:

  - well-formed XML with an AuditFile root
  - mandatory sections: Header, MasterFiles, GeneralLedgerEntries
  - Header carries AuditFileVersion, AuditFileCountry, DefaultCurrencyCode
    and a Company with RegistrationNumber and Name
  - MasterFiles has GeneralLedgerAccounts with at least one Account (AccountID)
  - every Transaction has a TransactionID and balances: sum of debit lines
    equals sum of credit lines (to the cent)
  - every Line's AccountID exists in GeneralLedgerAccounts
  - declared NumberOfEntries / TotalDebit / TotalCredit match the computed values

Usage:
  python scripts/saft_validate.py data/synthetic/saft_sample.xml [--output FILE]

Exit code 0 if valid, 1 if any error. Warnings do not fail validation.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path

EXPECTED_COUNTRY = "NO"
MANDATORY_SECTIONS = ["Header", "MasterFiles", "GeneralLedgerEntries"]
MANDATORY_HEADER_FIELDS = ["AuditFileVersion", "AuditFileCountry",
                           "DefaultCurrencyCode"]


def _local(tag: str) -> str:
    """Strip the XML namespace from a tag name."""
    return tag.split("}", 1)[-1]


def _find(parent: ET.Element, name: str) -> ET.Element | None:
    return next((el for el in parent if _local(el.tag) == name), None)


def _findall(parent: ET.Element, name: str) -> list[ET.Element]:
    return [el for el in parent if _local(el.tag) == name]


def _text(parent: ET.Element, name: str) -> str:
    el = _find(parent, name)
    return (el.text or "").strip() if el is not None else ""


def _amount(line: ET.Element, side: str) -> Decimal | None:
    """Return the Amount of a DebitAmount/CreditAmount child, if present."""
    wrapper = _find(line, side)
    if wrapper is None:
        return None
    raw = _text(wrapper, "Amount")
    try:
        return Decimal(raw)
    except InvalidOperation:
        raise ValueError(f"{side} has non-numeric Amount {raw!r}")


def validate(path: str | Path) -> tuple[list[str], list[str]]:
    """Validate the file. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        # ET.parse opens the file in binary mode and takes the encoding from
        # the XML declaration (UTF-8 when absent), so it is independent of the
        # platform locale -- there is no encoding argument to pass here.
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"not well-formed XML: {exc}"], []

    if _local(root.tag) != "AuditFile":
        errors.append(f"root element is <{_local(root.tag)}>, expected <AuditFile>")
        return errors, warnings

    sections = {_local(el.tag): el for el in root}
    for name in MANDATORY_SECTIONS:
        if name not in sections:
            errors.append(f"mandatory section missing: <{name}>")
    if errors:
        return errors, warnings

    header = sections["Header"]
    for field in MANDATORY_HEADER_FIELDS:
        if not _text(header, field):
            errors.append(f"Header: missing or empty <{field}>")
    country = _text(header, "AuditFileCountry")
    if country and country != EXPECTED_COUNTRY:
        warnings.append(f"Header: AuditFileCountry is {country!r}; this "
                        f"validator targets the Norwegian profile "
                        f"({EXPECTED_COUNTRY!r})")
    company = _find(header, "Company")
    if company is None:
        errors.append("Header: missing <Company>")
    else:
        for field in ("RegistrationNumber", "Name"):
            if not _text(company, field):
                errors.append(f"Header/Company: missing or empty <{field}>")

    gl_accounts = _find(sections["MasterFiles"], "GeneralLedgerAccounts")
    account_ids: set[str] = set()
    if gl_accounts is None:
        errors.append("MasterFiles: missing <GeneralLedgerAccounts>")
    else:
        for account in _findall(gl_accounts, "Account"):
            account_id = _text(account, "AccountID")
            if account_id:
                account_ids.add(account_id)
        if not account_ids:
            errors.append("GeneralLedgerAccounts: no <Account> with an <AccountID>")

    entries = sections["GeneralLedgerEntries"]
    n_transactions = 0
    total_debit = Decimal("0")
    total_credit = Decimal("0")

    for journal in _findall(entries, "Journal"):
        journal_id = _text(journal, "JournalID") or "?"
        for tx in _findall(journal, "Transaction"):
            n_transactions += 1
            tx_id = _text(tx, "TransactionID")
            tx_label = tx_id or f"journal {journal_id} transaction #{n_transactions}"
            if not tx_id:
                errors.append(f"{tx_label}: missing <TransactionID>")

            tx_debit = Decimal("0")
            tx_credit = Decimal("0")
            lines = _findall(tx, "Line")
            if not lines:
                errors.append(f"{tx_label}: has no <Line> elements")
            for line in lines:
                account_id = _text(line, "AccountID")
                if not account_id:
                    errors.append(f"{tx_label}: line missing <AccountID>")
                elif account_ids and account_id not in account_ids:
                    errors.append(f"{tx_label}: AccountID {account_id!r} not "
                                  f"in GeneralLedgerAccounts")
                try:
                    debit = _amount(line, "DebitAmount")
                    credit = _amount(line, "CreditAmount")
                except ValueError as exc:
                    errors.append(f"{tx_label}: {exc}")
                    continue
                if debit is None and credit is None:
                    errors.append(f"{tx_label}: line has neither DebitAmount "
                                  f"nor CreditAmount")
                tx_debit += debit or Decimal("0")
                tx_credit += credit or Decimal("0")

            if tx_debit != tx_credit:
                errors.append(f"{tx_label}: unbalanced -- debits {tx_debit} "
                              f"!= credits {tx_credit}")
            total_debit += tx_debit
            total_credit += tx_credit

    if n_transactions == 0:
        warnings.append("GeneralLedgerEntries contains no transactions")

    declared = {
        "NumberOfEntries": (str(n_transactions), _text(entries, "NumberOfEntries")),
        "TotalDebit": (str(total_debit), _text(entries, "TotalDebit")),
        "TotalCredit": (str(total_credit), _text(entries, "TotalCredit")),
    }
    for name, (computed, stated) in declared.items():
        if not stated:
            warnings.append(f"GeneralLedgerEntries: <{name}> not declared "
                            f"(computed: {computed})")
        else:
            try:
                equal = Decimal(stated) == Decimal(computed)
            except InvalidOperation:
                equal = False
            if not equal:
                errors.append(f"GeneralLedgerEntries: declared {name}={stated} "
                              f"but computed {computed}")

    return errors, warnings


def format_report(path: str | Path, errors: list[str],
                  warnings: list[str]) -> str:
    lines = [f"SAF-T Financial structural validation: {path}", "=" * 72]
    verdict = "VALID" if not errors else "INVALID"
    lines.append(f"Result: {verdict} "
                 f"({len(errors)} error(s), {len(warnings)} warning(s))")
    for e in errors:
        lines.append(f"  ERROR   {e}")
    for w in warnings:
        lines.append(f"  WARNING {w}")
    lines.append("Note: structural check only -- not a substitute for full "
                 "XSD validation against the official schema.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Structurally validate a Norwegian SAF-T Financial XML file.")
    parser.add_argument("xml_file", help="SAF-T Financial XML file to validate")
    parser.add_argument("--output", metavar="FILE",
                        help="also save the report to FILE "
                             "(conventionally under progress/)")
    args = parser.parse_args(argv)

    errors, warnings = validate(args.xml_file)
    report = format_report(args.xml_file, errors, warnings)
    print(report)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"\nReport saved to {args.output}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
