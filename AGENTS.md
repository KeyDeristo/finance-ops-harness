# AGENTS.md — Entry Point

You are an agent working inside a finance operations harness. This file is your
mandatory entry point. Read it fully before doing anything else. Do not read the
whole repository; the repo map below tells you where to look for what.

Three principles govern everything here:

1. **The repo is the system.** SOPs, coding rules, controls, the jurisdiction
   profile and the scripts live in this repository. If it is not written here,
   it is not part of the process.
2. **Separated roles.** A `bookkeeper` executes, a `reviewer` approves or
   rejects (four-eyes principle), an `explorer` researches but never touches
   data. Agents communicate by writing to `progress/`, never from memory.
3. **Evidence or it did not happen.** Nothing is marked done without linked
   evidence. This repo must stand up as audit documentation.

## 1. Startup protocol

Run the environment check before any work:

- Linux/macOS/Git Bash: `./init.sh`
- Windows (no Git Bash): `python checks/init.py`

If it fails: **stop**. Report the failure in `progress/current.md` and to the
user. Do not work on top of a broken environment — results produced without a
passing check are not trustworthy evidence.

## 2. Finding your task

1. Read `progress/current.md`.
   - If it describes a task in progress, continue that task from where it
     stands. Do not start something new.
   - If it is empty (no task in progress), open `progress/tasks.json`, take the
     **first** task with status `pending`, set its status to `in_progress`, set
     `owner` to your role, and describe the task and your plan in
     `progress/current.md`.
2. Never work on a task that is not reflected in `progress/current.md`. If the
   user asks for ad-hoc work, first record it as a task in `tasks.json`.

### 2.1 Harness work is not a task

One exception to the above. Changes to the harness *itself* — `checks/`,
`scripts/`, `tests/`, `.github/`, `.claude/`, `AGENTS.md`, `README.md` — follow
normal git flow (branch, CI green, review before merge) and are **not** recorded
in `progress/tasks.json`. Work done *with* the harness — reconciliations, coding
runs, jurisdiction profiles, SOP fill-ins, anything touching `data/` or the
content of `rules/` — follows the tasks.json → bookkeeper → reviewer flow.

## 3. Repo map — where to look for what

| You need… | Look in… |
|---|---|
| How to execute a process (P2P, O2C, expenses, month-end) | `docs/sops/` |
| Account and cost-center coding rules | `rules/coding-rules.yaml` |
| Country/statutory requirements (VAT cadence, export format, retention) | `rules/jurisdiction.yaml` |
| Naming, evidence format, commit format | `docs/CONVENTIONS.md` |
| Which controls are mandatory and why | `docs/CONTROLS.md` |
| How the repo fits together, how a task flows | `docs/ARCHITECTURE.md` |
| Tools (reconciliation, invoice coding, SAF-T validation) | `scripts/` (each supports `--help`) |
| Automated integrity checks | `checks/` (run all via `checks/run_all.py`) |
| Current task, task list, changelog | `progress/` |
| Synthetic sample data for tests and demos | `data/synthetic/` |
| Your role definition | `.claude/agents/<role>.md` |

Company-specific content lives **only** in `rules/`, `docs/sops/` and `data/`.
Everything else is generic template machinery.

## 4. Hard rules

These are not preferences. Violating any of them invalidates the work.

1. **Never mark a task `done` without evidence.** Evidence means a concrete,
   checkable reference: a file path, a journal entry reference, a check or
   script output. `checks/check_progress.py` enforces this mechanically.
2. **Never modify `rules/` or `docs/sops/` without reviewer approval.** Propose
   the change in `progress/current.md` and wait for an approving verdict.
3. **Never invent data.** No fabricated amounts, dates, suppliers, references
   or balances. If information is missing, the task is `blocked` — say so in
   `progress/current.md` and state exactly what is missing.
4. **Every result is written to `progress/`.** Work that exists only in your
   context window does not exist. Other agents must be able to pick up from
   your written state alone.
5. **Always check `rules/jurisdiction.yaml` before any statutory or VAT-related
   task.** Filing cadence, export format, e-invoicing standard and retention
   are declared there, not assumed.
6. **Stay in your role.** A bookkeeper does not approve its own work. A
   reviewer does not execute tasks. An explorer does not modify data.

## 5. How a task ends

1. The executing agent finishes the SOP steps, records evidence for each
   acceptance criterion in `progress/current.md`, and hands off to the
   reviewer.
2. The **reviewer** checks the work against its checklist and writes an
   explicit verdict (`APPROVED` or `REJECTED`, with concrete reasons) into
   `progress/current.md`.
3. On approval only:
   - the task's status in `progress/tasks.json` becomes `done`, with its
     `evidence` array filled in;
   - one line is appended to `progress/history.md` (date, role, task id, what
     was done, evidence);
   - `progress/current.md` is reset to its empty state.
4. On rejection: the task stays `in_progress`, the verdict with reasons stays
   in `current.md`, and the executing agent addresses the reasons.

A task without a reviewer verdict is never `done`. No exceptions, including
tasks that "obviously" passed.
