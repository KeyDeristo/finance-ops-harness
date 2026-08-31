# SOP: Employee Expenses

<!-- TEMPLATE STATUS: generic skeleton. Sections marked ⚠️ FILL-IN are
     company-specific and MUST be completed when instantiating this template.
     Changes go through reviewer approval (C-06). -->

| Field | Value |
|---|---|
| Process | Employee expense claims — submission through reimbursement |
| Owner (role) | bookkeeper |
| Version | 0.1 (template) |
| Last reviewed | ⚠️ FILL-IN |
| Controls applied | C-01, C-02, C-04, C-05, C-08 |

## Purpose

Reimburse employees correctly and quickly while keeping expense postings
policy-compliant, correctly coded and fully documented.

## Scope

Out-of-pocket employee expenses and company card transactions.
⚠️ FILL-IN: which of the two apply, and any per-diem / mileage schemes.

## Trigger

An employee submits an expense claim.
⚠️ FILL-IN: submission tool and required attachments (receipt standards).

## Prerequisites

- `checks/init.py` passes (C-09).
- ⚠️ FILL-IN: expense policy document (limits per category, receipt
  requirements, approval chain).

## Steps

| # | Action | Tool / reference | Evidence to record |
|---|---|---|---|
| 1 | Check the claim against policy: limits, receipt present, business purpose stated. ⚠️ FILL-IN: policy limits per category. | ⚠️ FILL-IN | claim id + policy check result |
| 2 | Propose coding from claim description (keyword rules). Low confidence ⇒ human decision (C-08). | `scripts/invoice_classify.py` + `rules/coding-rules.yaml` | script-output under `progress/` |
| 3 | Route for approval. ⚠️ FILL-IN: approver (usually claimant's manager), never the claimant (C-01). | ⚠️ FILL-IN | approver + timestamp |
| 4 | Post the expense. | ⚠️ FILL-IN: ERP | journal-entry reference |
| 5 | Reimburse. ⚠️ FILL-IN: payout method and cycle. | ⚠️ FILL-IN | payment reference |
| 6 | Archive claim + receipts for the retention period. | `rules/jurisdiction.yaml` → `retention_years` (C-05) | archive locator |

## Outputs and evidence

Approved, posted, reimbursed claim with receipts archived; exceptions
documented; task closed per AGENTS.md §5.

## Escalation

Mark `blocked` when: no receipt and policy requires one; claim over policy
limit; suspected duplicate (same amount/date/merchant); unclear business
purpose. Never post a claim "provisionally" (C-04).

## Jurisdiction touchpoints

`retention_years` (step 6), `vat` (recoverable VAT on expenses — ⚠️ FILL-IN
per-category recoverability rules for your country).
