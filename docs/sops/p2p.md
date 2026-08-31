# SOP: Purchase to Pay (P2P)

<!-- TEMPLATE STATUS: generic skeleton. Sections marked ⚠️ FILL-IN are
     company-specific and MUST be completed when instantiating this template.
     Changes go through reviewer approval (C-06). -->

| Field | Value |
|---|---|
| Process | Purchase to Pay — supplier invoice receipt through payment |
| Owner (role) | bookkeeper |
| Version | 0.1 (template) |
| Last reviewed | ⚠️ FILL-IN |
| Controls applied | C-01, C-02, C-04, C-05, C-06, C-08 |

## Purpose

Ensure every supplier invoice is captured, validated, coded, approved and paid
exactly once, with a complete evidence trail from invoice to payment.

## Scope

Supplier invoices and credit notes. Out of scope: employee expenses (see
`expenses.md`), payroll, intercompany settlements.
⚠️ FILL-IN: adjust scope to your entity structure.

## Trigger

A supplier invoice arrives.
⚠️ FILL-IN: name the actual channels (e-invoicing network per
`rules/jurisdiction.yaml` → `e_invoicing_standard`, email inbox, portal) and
the intake system.

## Prerequisites

- `checks/init.py` passes (C-09).
- `rules/coding-rules.yaml` is current.
- ⚠️ FILL-IN: system access required (ERP, invoice workflow tool).

## Steps

| # | Action | Tool / reference | Evidence to record |
|---|---|---|---|
| 1 | Register the invoice: id, supplier, date, amount, currency, due date. Reject duplicates by supplier + invoice number. | ⚠️ FILL-IN: intake system | invoice id + source reference |
| 2 | Validate against order/receipt. ⚠️ FILL-IN: matching policy (2-way/3-way, tolerances). | ⚠️ FILL-IN | match result or documented exception |
| 3 | Propose account and cost center. Confidence below threshold ⇒ flag for human decision, never auto-accept (C-08). | `scripts/invoice_classify.py` + `rules/coding-rules.yaml` | script-output saved under `progress/` |
| 4 | Route for approval. ⚠️ FILL-IN: approval matrix (who approves what amount). | ⚠️ FILL-IN | approver + timestamp reference |
| 5 | Post the invoice. | ⚠️ FILL-IN: ERP posting instructions | journal-entry reference (`JE-…`) |
| 6 | Schedule payment per terms. ⚠️ FILL-IN: payment run cadence, method, release procedure (four-eyes on release, C-01). | ⚠️ FILL-IN | payment batch reference |
| 7 | Archive invoice and trail for the retention period. | `rules/jurisdiction.yaml` → `retention_years` (C-05) | archive locator |

## Outputs and evidence

Posted, approved, paid (or scheduled) invoice; classification output and
approval trail referenced in `progress/current.md`; task closed per AGENTS.md §5.

## Escalation

Mark the task `blocked` when: supplier not in any rule and coding unclear;
match exception outside tolerance; missing approval; suspected duplicate or
fraud signal. Record what is missing and hand off to the reviewer.

## Jurisdiction touchpoints

`e_invoicing_standard` (intake), `vat` (input VAT treatment — ⚠️ FILL-IN your
VAT coding policy), `retention_years` (step 7).
