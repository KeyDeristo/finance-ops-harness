"""Propose account and cost-center coding for invoices (control C-08).

Applies rules/coding-rules.yaml as a deterministic cascade — first match wins:
  1. suppliers      (case-insensitive exact match on supplier name)
  2. keywords       (any keyword contained in the lowercased description)
  3. amount_ranges  (amount within [min_amount, max_amount])
  4. fallback       (always matches, low confidence)

Every result is a PROPOSAL with a confidence level. Proposals below the
rules file's confidence_threshold are flagged needs_review and must go to a
human. This script — and any LLM plugged into its extension point — suggests;
it never decides and never posts.

Input CSV columns: invoice_id, supplier, invoice_date, description, amount, currency

Usage:
  python scripts/invoice_classify.py data/synthetic/invoices.csv \\
      [--rules rules/coding-rules.yaml] [--output FILE]

Report goes to stdout; --output additionally saves it as CSV (conventionally
under progress/ as an evidence file). Exit code 0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "rules" / "coding-rules.yaml"


def load_rules(path: str | Path) -> dict:
    rules = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rules, dict) or "fallback" not in rules:
        raise SystemExit(f"error: {path}: not a valid coding rules file "
                         f"(mapping with at least a 'fallback' section)")
    return rules


def llm_propose(invoice: dict, rule_proposal: dict) -> dict | None:
    """EXTENSION POINT — plug a language model in here.

    Called for every invoice after the rule cascade, with the invoice fields
    and the rule-based proposal. A model integration may return a dict:

        {"account": str, "cost_center": str, "confidence": float,
         "rationale": str}

    Contract (control C-08 — non-negotiable for any implementation):
      - The return value is a PROPOSAL. It flows through the same
        confidence_threshold and needs_review path as rule-based proposals.
      - confidence is the model's own calibrated estimate in [0, 1]; the
        harness never treats it as certainty.
      - Returning None means "no opinion" and keeps the rule-based proposal.
      - The implementation must not post, write or mutate anything.

    The template ships with no API calls: this stub always returns None.
    """
    return None


def classify_invoice(invoice: dict, rules: dict) -> dict:
    """Classify one invoice dict; returns the proposal dict."""
    supplier = str(invoice.get("supplier", "")).strip().lower()
    description = str(invoice.get("description", "")).lower()
    amount = float(invoice.get("amount", 0))

    proposal: dict | None = None

    for rule in rules.get("suppliers", []):
        if str(rule.get("supplier", "")).strip().lower() == supplier:
            proposal = {**rule, "rule_type": "supplier",
                        "matched_on": rule["supplier"]}
            break

    if proposal is None:
        for rule in rules.get("keywords", []):
            hit = next((kw for kw in rule.get("keywords", [])
                        if str(kw).lower() in description), None)
            if hit is not None:
                proposal = {**rule, "rule_type": "keyword", "matched_on": hit}
                break

    if proposal is None:
        for rule in rules.get("amount_ranges", []):
            lo = float(rule.get("min_amount", float("-inf")))
            hi = float(rule.get("max_amount", float("inf")))
            if lo <= amount <= hi:
                proposal = {**rule, "rule_type": "amount_range",
                            "matched_on": f"{lo} <= {amount} <= {hi}"}
                break

    if proposal is None:
        proposal = {**rules["fallback"], "rule_type": "fallback",
                    "matched_on": "no rule matched"}

    llm = llm_propose(invoice, proposal)
    if llm is not None:
        proposal = {**llm, "rule_type": "llm",
                    "matched_on": llm.get("rationale", "model proposal")}

    threshold = float(rules.get("confidence_threshold", 0.75))
    confidence = float(proposal.get("confidence", 0.0))
    return {
        "invoice_id": invoice.get("invoice_id", ""),
        "supplier": invoice.get("supplier", ""),
        "amount": amount,
        "proposed_account": str(proposal.get("account", "")),
        "proposed_cost_center": str(proposal.get("cost_center", "")),
        "confidence": confidence,
        "rule_type": proposal["rule_type"],
        "matched_on": str(proposal["matched_on"]),
        "needs_review": confidence < threshold,
        "note": str(proposal.get("note", "")),
    }


def classify_all(invoices: pd.DataFrame, rules: dict) -> pd.DataFrame:
    return pd.DataFrame([classify_invoice(row, rules)
                         for row in invoices.to_dict("records")])


def format_report(result: pd.DataFrame, threshold: float) -> str:
    lines: list[str] = []
    lines.append("Invoice coding proposals")
    lines.append("=" * 78)
    for _, r in result.iterrows():
        flag = "NEEDS REVIEW" if r["needs_review"] else "auto-proposed"
        lines.append(f"  {r['invoice_id']:<9} {r['supplier']:<26} "
                     f"{r['amount']:>10.2f}  -> {r['proposed_account']} / "
                     f"{r['proposed_cost_center']}  "
                     f"conf {r['confidence']:.2f}  [{r['rule_type']}] {flag}")
        if r["note"]:
            lines.append(f"            note: {r['note']}")
    lines.append("=" * 78)
    n_review = int(result["needs_review"].sum())
    lines.append(f"{len(result)} invoices: {len(result) - n_review} at or above "
                 f"confidence threshold ({threshold}), {n_review} need(s) human review")
    lines.append("Proposals are suggestions only -- a human confirms every "
                 "posting; needs_review items are mandatory to route (C-08).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose account/cost-center coding for an invoices CSV.")
    parser.add_argument("invoices_csv", help="invoices CSV (columns: invoice_id, "
                        "supplier, invoice_date, description, amount, currency)")
    parser.add_argument("--rules", default=str(DEFAULT_RULES),
                        help="coding rules YAML (default: %(default)s)")
    parser.add_argument("--output", metavar="FILE",
                        help="also save proposals as CSV "
                             "(conventionally under progress/)")
    args = parser.parse_args(argv)

    invoices = pd.read_csv(args.invoices_csv)
    required = {"invoice_id", "supplier", "description", "amount"}
    missing = required - set(invoices.columns)
    if missing:
        raise SystemExit(f"error: {args.invoices_csv}: missing column(s): "
                         f"{', '.join(sorted(missing))}")

    rules = load_rules(args.rules)
    result = classify_all(invoices, rules)
    print(format_report(result, float(rules.get("confidence_threshold", 0.75))))
    if args.output:
        result.to_csv(args.output, index=False)
        print(f"\nProposals saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
