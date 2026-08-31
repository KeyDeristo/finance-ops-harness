# Controls

Mandatory controls in this harness, each with the reason it exists. Controls
are not bureaucracy; each one blocks a specific, known failure mode of either
humans or AI agents doing finance work. SOPs reference controls by id.

| Id | Control | Enforced by |
|---|---|---|
| C-01 | Four-eyes approval | reviewer role, AGENTS.md §5 |
| C-02 | Evidence before done | `checks/check_progress.py` |
| C-03 | Segregation of duties | agent role definitions |
| C-04 | No invented data | AGENTS.md hard rule 3, reviewer checklist |
| C-05 | Jurisdiction check before statutory work | AGENTS.md hard rule 5, reviewer checklist |
| C-06 | Change control for rules/ and docs/sops/ | AGENTS.md hard rule 2, reviewer gate |
| C-07 | Bank-to-ledger reconciliation | `scripts/bank_reconcile.py`, month-end SOP |
| C-08 | Confidence threshold on automated coding | `rules/coding-rules.yaml`, `scripts/invoice_classify.py` |
| C-09 | Environment integrity | `checks/init.py` (startup protocol, SessionEnd hook) |

## C-01 — Four-eyes approval

No task is `done` until a different role (the reviewer) has verified it against
an explicit checklist and written an `APPROVED` verdict with named evidence.
**Why:** the person (or agent) who does the work is the worst-placed to judge
it; self-approval is the root cause of most bookkeeping errors and most fraud.

## C-02 — Evidence before done

Every `done` task carries a non-empty `evidence` array, and every acceptance
criterion has a checkable reference. Enforced mechanically.
**Why:** the repo must function as audit documentation. An unevidenced "done"
is an assertion, not a record.

## C-03 — Segregation of duties

Bookkeeper executes, reviewer approves, explorer researches. No role performs
another role's actions, ever — including "just this once".
**Why:** classic SoD, adapted to agents. It also protects against a single
agent's systematic blind spot propagating unchecked into the books.

## C-04 — No invented data

Missing information blocks a task; it is never guessed. Amounts, dates,
suppliers, references and balances come from source data or not at all.
**Why:** language models fill gaps plausibly by design. Plausible-but-invented
figures are the single most dangerous failure mode of AI in accounting.

## C-05 — Jurisdiction check before statutory work

Any VAT, filing, export or retention decision starts by reading
`rules/jurisdiction.yaml`.
**Why:** statutory requirements differ per country and change over time. Keeping
them in one declared profile — instead of in anyone's memory — makes the
assumption auditable and the template portable across jurisdictions.

## C-06 — Change control for rules/ and docs/sops/

Changes to coding rules, the jurisdiction profile or SOPs are proposed in
`progress/current.md` and land only with an approving reviewer verdict.
**Why:** these files steer every future task. An unreviewed change here
multiplies into every subsequent posting.

## C-07 — Bank-to-ledger reconciliation

Bank statements are reconciled against the ledger every close; unmatched items
are listed, explained or escalated, never dropped.
**Why:** reconciliation is the completeness control — it catches missing
postings, duplicates and timing errors that no per-transaction check can see.

## C-08 — Confidence threshold on automated coding

Automated account/cost-center proposals below the threshold in
`rules/coding-rules.yaml` are flagged `needs_review` and go to a human. The
classifier (and any future LLM plugged into its extension point) **proposes;
it never decides.**
**Why:** an automated coding that is silently wrong 5% of the time corrupts the
books faster than a human ever could. The threshold makes the automation's
uncertainty explicit and routes it to judgment.

## C-09 — Environment integrity

Every session starts (and, via hook, ends) with `checks/init.py`: environment,
structure, progress and jurisdiction checks, plus the test suite. Work never
proceeds on a failing environment.
**Why:** results produced by broken tooling look identical to real results.
Verifying the harness before trusting its output is the whole point of
harness engineering.
