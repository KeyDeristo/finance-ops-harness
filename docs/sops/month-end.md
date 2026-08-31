# SOP: Month-End Close

<!-- TEMPLATE STATUS: generic skeleton. Sections marked ⚠️ FILL-IN are
     company-specific and MUST be completed when instantiating this template.
     Changes go through reviewer approval (C-06). -->

| Field | Value |
|---|---|
| Process | Month-end close |
| Owner (role) | bookkeeper (execution) + reviewer (sign-off per task) |
| Version | 0.1 (template) |
| Last reviewed | ⚠️ FILL-IN |
| Controls applied | C-01, C-02, C-04, C-05, C-07, C-09 |

## Purpose

Produce a complete, reconciled, reviewable set of books for the closed month,
on a predictable timetable, with evidence for every closing step.

## Scope

Monthly close activities. Quarterly/annual extras (audit schedules, annual
statutory filings) are out of scope here — add them as separate SOPs.
⚠️ FILL-IN: closing calendar (working day D+1…D+n per step).

## Trigger

Calendar month end.
⚠️ FILL-IN: who opens the close (creates the month's tasks in
`progress/tasks.json` from this checklist) and by when.

## Prerequisites

- `checks/init.py` passes (C-09).
- Bank statements and subledger extracts for the month are available in the
  agreed location. ⚠️ FILL-IN: where extracts come from and who provides them.

## Steps

Each step is tracked as its own task in `progress/tasks.json` with acceptance
criteria and evidence (C-02), and individually reviewed (C-01).

| # | Action | Tool / reference | Evidence to record |
|---|---|---|---|
| 1 | Reconcile every bank account against the ledger; list, explain or escalate all unmatched items (C-07). | `scripts/bank_reconcile.py` | reconciliation report under `progress/` |
| 2 | Review open AP: items overdue or older than ⚠️ FILL-IN days; confirm completeness of invoice capture (accrue for known missing invoices). | AP extract; ⚠️ FILL-IN: source | open AP review note under `progress/` |
| 3 | Review open AR and aging; assess doubtful items per policy. ⚠️ FILL-IN: provisioning policy. | AR extract | aging + assessment under `progress/` |
| 4 | Post accruals, prepayments and recurring journals. ⚠️ FILL-IN: standard journal list with owners. | ⚠️ FILL-IN: ERP | journal-entry references |
| 5 | VAT position check: period per filing cadence, draft the return if a filing period closed (C-05). | `rules/jurisdiction.yaml` → `vat.filing_cadence`, deadlines | VAT summary under `progress/` |
| 6 | If a statutory export is produced this period, validate it before archiving. | `scripts/saft_validate.py` (worked example for the Norwegian profile) | validation report under `progress/` |
| 7 | Lock the period. ⚠️ FILL-IN: how the period is locked in your system, and who may reopen it. | ⚠️ FILL-IN | lock confirmation |
| 8 | Produce the reporting pack. ⚠️ FILL-IN: contents and recipients. | ⚠️ FILL-IN | pack location |

## Outputs and evidence

All close tasks `done` with evidence in `progress/tasks.json`; one
`history.md` line per closed task; locked period; reporting pack delivered.

## Escalation

Mark the affected task `blocked` — not the whole close — when: unreconciled
difference cannot be explained; a subledger extract is missing; a statutory
export fails validation. The close does not complete while any close task is
`blocked` or unreviewed.

## Jurisdiction touchpoints

`vat.filing_cadence` and `statutory_reporting_deadlines` (step 5),
`statutory_export_format` (step 6), `chart_of_accounts_standard` (journal
postings throughout).
