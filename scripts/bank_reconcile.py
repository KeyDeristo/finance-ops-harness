"""Reconcile a bank statement against the ledger (control C-07).

Matching strategy, in order:
  1. Exact:          same amount and same date.
  2. Date tolerance: same amount, dates within --tolerance-days (closest wins).
Whatever remains on either side is listed as unmatched — unmatched items are
reported, never dropped.

Input CSVs (see docs/CONVENTIONS.md for amount conventions):
  bank statement: date, description, reference, amount
  ledger:         date, description, entry_ref, amount

Usage:
  python scripts/bank_reconcile.py data/synthetic/bank_statement.csv \\
      data/synthetic/ledger.csv [--tolerance-days N] [--output FILE]

Report goes to stdout; --output additionally saves it (conventionally under
progress/ as an evidence file). Exit code 0; unmatched items are a normal,
reportable outcome, not an error.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

DEFAULT_TOLERANCE_DAYS = 3


def _load(path: str, ref_column: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    required = {"date", "amount", ref_column}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"error: {path}: missing column(s): "
                         f"{', '.join(sorted(missing))}")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    # Compare amounts in integer cents to avoid float-equality surprises.
    df["cents"] = (df["amount"].astype(float).round(2) * 100).round().astype("int64")
    return df


def reconcile(bank: pd.DataFrame, ledger: pd.DataFrame,
              tolerance_days: int = DEFAULT_TOLERANCE_DAYS) -> dict:
    """Match bank rows to ledger rows. Returns a dict with keys:
    matches (list of dicts), unmatched_bank, unmatched_ledger (DataFrames).
    """
    ledger_used: set[int] = set()
    matches: list[dict] = []

    def record(bank_row, ledger_idx, match_type: str) -> None:
        ledger_row = ledger.loc[ledger_idx]
        ledger_used.add(ledger_idx)
        matches.append({
            "bank_ref": bank_row.get("reference", ""),
            "bank_date": bank_row["date"].date().isoformat(),
            "ledger_ref": ledger_row.get("entry_ref", ""),
            "ledger_date": ledger_row["date"].date().isoformat(),
            "amount": bank_row["cents"] / 100,
            "match_type": match_type,
        })

    matched_bank: set[int] = set()

    # Pass 1: exact on amount + date.
    for b_idx, b_row in bank.iterrows():
        candidates = ledger[(ledger["cents"] == b_row["cents"])
                            & (ledger["date"] == b_row["date"])
                            & (~ledger.index.isin(ledger_used))]
        if not candidates.empty:
            record(b_row, candidates.index[0], "exact")
            matched_bank.add(b_idx)

    # Pass 2: same amount within the date tolerance, closest date first.
    for b_idx, b_row in bank.iterrows():
        if b_idx in matched_bank:
            continue
        candidates = ledger[(ledger["cents"] == b_row["cents"])
                            & (~ledger.index.isin(ledger_used))].copy()
        if candidates.empty:
            continue
        candidates["day_diff"] = (candidates["date"] - b_row["date"]).abs()
        candidates = candidates[candidates["day_diff"]
                                <= pd.Timedelta(days=tolerance_days)]
        if not candidates.empty:
            best = candidates.sort_values(["day_diff", "date"]).index[0]
            record(b_row, best, "date-tolerance")
            matched_bank.add(b_idx)

    return {
        "matches": matches,
        "unmatched_bank": bank[~bank.index.isin(matched_bank)],
        "unmatched_ledger": ledger[~ledger.index.isin(ledger_used)],
    }


def format_report(result: dict, tolerance_days: int) -> str:
    lines: list[str] = []
    matches = result["matches"]
    unmatched_bank = result["unmatched_bank"]
    unmatched_ledger = result["unmatched_ledger"]
    exact = sum(1 for m in matches if m["match_type"] == "exact")
    fuzzy = len(matches) - exact

    lines.append("Bank reconciliation report")
    lines.append("=" * 72)
    lines.append(f"Matched: {len(matches)} "
                 f"({exact} exact, {fuzzy} within {tolerance_days}-day tolerance)")
    lines.append(f"Unmatched bank items:   {len(unmatched_bank)}")
    lines.append(f"Unmatched ledger items: {len(unmatched_ledger)}")
    lines.append("")

    lines.append("Matches")
    lines.append("-" * 72)
    for m in matches:
        lines.append(f"  {m['bank_ref']:<8} {m['bank_date']}  <->  "
                     f"{m['ledger_ref']:<8} {m['ledger_date']}  "
                     f"{m['amount']:>12.2f}  [{m['match_type']}]")

    for title, df, ref_col in (("Unmatched bank items", unmatched_bank, "reference"),
                               ("Unmatched ledger items", unmatched_ledger, "entry_ref")):
        lines.append("")
        lines.append(title)
        lines.append("-" * 72)
        if df.empty:
            lines.append("  (none)")
        for _, row in df.iterrows():
            ref = row.get(ref_col, "")
            desc = row.get("description", "")
            lines.append(f"  {ref:<8} {row['date'].date().isoformat()}  "
                         f"{row['cents'] / 100:>12.2f}  {desc}")

    lines.append("")
    lines.append("Every unmatched item must be explained or escalated "
                 "before the reconciliation task can close (control C-07).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile a bank statement CSV against a ledger CSV.")
    parser.add_argument("bank_csv", help="bank statement CSV "
                        "(columns: date, description, reference, amount)")
    parser.add_argument("ledger_csv", help="ledger CSV "
                        "(columns: date, description, entry_ref, amount)")
    parser.add_argument("--tolerance-days", type=int,
                        default=DEFAULT_TOLERANCE_DAYS,
                        help="max day difference for the second matching pass "
                             "(default: %(default)s)")
    parser.add_argument("--output", metavar="FILE",
                        help="also save the report to FILE "
                             "(conventionally under progress/)")
    args = parser.parse_args(argv)

    bank = _load(args.bank_csv, "reference")
    ledger = _load(args.ledger_csv, "entry_ref")
    result = reconcile(bank, ledger, args.tolerance_days)
    report = format_report(result, args.tolerance_days)

    print(report)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"\nReport saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
