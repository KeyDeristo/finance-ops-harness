# SOP: Order to Cash (O2C)

<!-- TEMPLATE STATUS: generic skeleton. Sections marked ⚠️ FILL-IN are
     company-specific and MUST be completed when instantiating this template.
     Changes go through reviewer approval (C-06). -->

| Field | Value |
|---|---|
| Process | Order to Cash — customer order through cash settlement |
| Owner (role) | bookkeeper |
| Version | 0.1 (template) |
| Last reviewed | ⚠️ FILL-IN |
| Controls applied | C-01, C-02, C-04, C-05, C-07 |

## Purpose

Ensure every delivered order is invoiced correctly and on time, receivables are
monitored, and incoming cash is matched to invoices — completeness of revenue
and of cash application.

## Scope

Customer invoicing, receivables monitoring, cash application. Out of scope:
pricing decisions, contract management.
⚠️ FILL-IN: adjust to your revenue streams.

## Trigger

⚠️ FILL-IN: what makes an order invoiceable (delivery confirmation, milestone,
subscription cycle).

## Prerequisites

- `checks/init.py` passes (C-09).
- ⚠️ FILL-IN: credit policy — when is a credit check required and against what.

## Steps

| # | Action | Tool / reference | Evidence to record |
|---|---|---|---|
| 1 | Verify the order is invoiceable per trigger; check credit policy. ⚠️ FILL-IN: policy | ⚠️ FILL-IN | order reference + check result |
| 2 | Issue the invoice (`INV-…`) in the format the jurisdiction requires. | `rules/jurisdiction.yaml` → `e_invoicing_standard` (C-05); ⚠️ FILL-IN: invoicing system | invoice id + issue date |
| 3 | Record the receivable. | ⚠️ FILL-IN: ERP | journal-entry reference |
| 4 | Monitor open items; age receivables. ⚠️ FILL-IN: aging buckets and review cadence. | ⚠️ FILL-IN | aging list saved under `progress/` |
| 5 | Dun overdue customers. ⚠️ FILL-IN: dunning schedule, tone/steps, interest policy. | ⚠️ FILL-IN | dunning action + date per customer |
| 6 | Match incoming payments to invoices; unmatched receipts are investigated, never parked silently (C-07). | `scripts/bank_reconcile.py` | reconciliation report under `progress/` |
| 7 | Write off only per policy and with approval (C-01). ⚠️ FILL-IN: write-off policy and authority levels. | ⚠️ FILL-IN | approval reference + journal entry |

## Outputs and evidence

Issued invoices, current aging list, matched cash, documented exceptions;
task closed per AGENTS.md §5.

## Escalation

Mark `blocked` when: order data incomplete; customer disputes an invoice;
receipt cannot be matched and no counterparty responds; write-off would exceed
policy limits.

## Jurisdiction touchpoints

`e_invoicing_standard` (step 2), `vat` (output VAT on invoices — ⚠️ FILL-IN
your VAT coding policy), `statutory_reporting_deadlines` (revenue cut-off near
period end).
