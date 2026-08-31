# Conventions

Shared conventions for every agent and human working in this repo. The point of
conventions in a finance context is traceability: anyone (including an auditor)
must be able to follow a reference without asking the person who wrote it.

## Language

Everything — code, docs, comments, commit messages, progress notes — is written
in **English**.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Files and folders | `kebab-case`, lowercase | `coding-rules.yaml` |
| Dates | ISO 8601, always | `2026-08-31` |
| Task ids | `T-` + 3-digit sequence | `T-004` |
| Journal entry refs | `JE-` + 4-digit sequence | `JE-7003` |
| Customer invoices | `INV-` + 4-digit sequence | `INV-2041` |
| Supplier invoices | `SI-` + 4-digit sequence | `SI-1006` |
| Bank statement refs | `B-` + 4-digit sequence | `B-1005` |
| Cost centers | `CC-` + short uppercase code | `CC-IT` |
| G/L accounts | Always strings, never numbers (leading zeros matter) | `"6340"` |
| Evidence files | `T-<id>-<slug>-<date>.<ext>`, saved under `progress/` | `T-001-bank-reconciliation-2026-07-31.txt` |

## Amounts in CSV files

- Decimal point (`.`), no thousands separators, two decimals.
- Signed from the account holder's perspective: negative = outflow.
- Currency is declared per file or per row (ISO 4217), never assumed.

## Evidence format

Evidence entries (in `progress/tasks.json` and `progress/current.md`) follow:

```
<type>: <path-or-reference> — <one-line description>
```

Allowed types:

- `file` — a file in this repo (preferred; auditors can open it).
- `script-output` — saved output of a script run (say which script and inputs).
- `journal-entry` — a journal entry reference (`JE-…`).
- `check` — result of `checks/run_all.py` or a specific check.
- `external-doc` — a document outside the repo; include system and locator.

An evidence entry must be checkable by someone else without talking to you.
"Reconciled the bank" is not evidence. "file: progress/T-001-bank-reconciliation-2026-07-31.txt —
reconciliation report, 8 matched / 2 unmatched documented" is.

## Commit format

[Conventional Commits](https://www.conventionalcommits.org/), in English:

```
<type>(<optional scope>): <imperative summary>

<optional body: what and why, not how>

Task: T-003        <- when the commit belongs to a tracked task
```

Types used here: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`.
Small commits: one logical change per commit. A commit that touches `rules/`
or `docs/sops/` must reference the approving reviewer verdict in its body.

## Progress files

- `progress/current.md` — exactly one task at a time. Empty state is the file
  containing only the header and `_No task in progress._`
- `progress/history.md` — append-only. One line per closed task:
  `<date> | <role> | <task id> | <what was done> | <evidence summary>`
- `progress/tasks.json` — the task list. Statuses: `pending`, `in_progress`,
  `done`, `blocked`. Only the reviewer sets `done`.
