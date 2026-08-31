# finance-ops-harness

A generic, open-source template that applies **harness engineering** — the
discipline of giving AI agents a verified environment, explicit rules and
file-based memory — to **finance operations**. SOPs, controls, coding rules, a
jurisdiction profile, deterministic scripts and integrity checks live together
in one repository that doubles as audit documentation.

> **Notice:** this is a generic template with no affiliation to any company.
> All data, suppliers, amounts and names in it are synthetic and invented.
> Jurisdiction values (including the Norway example) are illustrative, not
> legal or accounting advice — verify against official sources before relying
> on them.

## Who this is for

Finance teams (and the engineers who support them) who want to run
bookkeeping-adjacent work — reconciliations, invoice coding, statutory
validation, month-end close — with AI agents **under controls**, instead of via
ad-hoc prompting. Also useful without any AI, as a disciplined,
checklist-driven way to structure finance ops in a repo.

## The three pillars

1. **The repo is the system.** Everything an agent needs — SOPs
   (`docs/sops/`), controls (`docs/CONTROLS.md`), coding rules and the
   jurisdiction profile (`rules/`), tools (`scripts/`) — lives here.
   `AGENTS.md` is the mandatory entry point; the repo map inside it means no
   agent has to read the whole project.
2. **Orchestration with separated roles.** A `bookkeeper` executes tasks
   following the SOP. A `reviewer` applies the four-eyes principle and
   approves or rejects with concrete reasons. An `explorer` researches and
   documents but never touches data. They communicate only by writing to
   `progress/`, never from memory.
3. **Verification with evidence.** Nothing is marked done without linked
   evidence (file, journal entry reference, check result) — enforced
   mechanically by `checks/check_progress.py`. `checks/init.py` verifies the
   whole harness (environment, structure, progress, jurisdiction, tests)
   before any work starts.

## Quick start

Requires Python 3.11+.

```bash
git clone <your-fork-or-clone-url>
cd finance-ops-harness
python -m pip install -r requirements.txt
./init.sh                 # Linux, macOS, Git Bash
```

On Windows without Git Bash:

```
python -m pip install -r requirements.txt
python checks/init.py
```

Both entry points are the same thing: `init.sh` is a thin wrapper around
`checks/init.py`. A green run means the harness is intact; a non-zero exit
means stop and fix before working.

Try the tools on the synthetic data:

```bash
python scripts/bank_reconcile.py data/synthetic/bank_statement.csv data/synthetic/ledger.csv
python scripts/invoice_classify.py data/synthetic/invoices.csv
python scripts/saft_validate.py data/synthetic/saft_sample.xml
```

## Instantiating this template for your company

Company-specific content lives in exactly **three places**. Instantiating the
template means filling them; everything else is generic machinery you should
not need to touch.

1. **`rules/`**
   - `coding-rules.yaml` — replace the synthetic suppliers, accounts and cost
     centers with your chart of accounts and rules. Set your
     `confidence_threshold`.
   - `jurisdiction.yaml` — set `active_profile` to your country. The `NO`
     profile ships as a worked example (NS 4102, SAF-T Financial, EHF/Peppol,
     bimonthly VAT, 5-year retention); copy the `_TEMPLATE` block for other
     countries and have every value verified (explorer drafts, reviewer
     approves).
2. **`docs/sops/`** — work through the `⚠️ FILL-IN` markers in each SOP
   (approval matrices, systems, tolerances, calendars). `_TEMPLATE.md` is the
   scaffold for new processes.
3. **`data/`** — replace the synthetic CSVs/XML with your real extracts
   (bank statements, ledgers, invoices, statutory exports). Keep real data out
   of public repos; the company instance should be private.

Then reset `progress/tasks.json` with your real tasks and clear the example
line from `progress/history.md`.

## Working with agents

With [Claude Code](https://claude.com/claude-code) (or any agent runner that
reads `AGENTS.md`), start a session in the repo root. The agent definitions in
`.claude/agents/` provide the three roles:

- **bookkeeper** — executes a task step by step per the SOP, records evidence,
  hands off for review.
- **reviewer** — verifies against an explicit checklist, writes
  `APPROVED`/`REJECTED` with reasons to `progress/current.md`; the only role
  that closes tasks or approves changes to `rules/` and `docs/sops/`.
- **explorer** — researches and documents (e.g. drafts a jurisdiction profile
  for a new country); never modifies data.

Every session: `checks/init.py` must pass first (the `.claude` hook also runs
it at session end). Tasks live in `progress/tasks.json` with acceptance
criteria, status and evidence; the flow is described in `AGENTS.md` §5 and
`docs/ARCHITECTURE.md`.

## Design constraints

- Python 3.11+, standard library + `pandas` + `pyyaml` only (`pytest` as a
  dev/test dependency, never imported by scripts).
- **No API calls anywhere in the codebase.** Where an LLM would add value,
  the scripts output a proposal with a confidence level and leave a documented
  extension point (`llm_propose()` in `scripts/invoice_classify.py`). The LLM
  suggests; it never decides.
- Jurisdiction-agnostic core: country specifics are declared in
  `rules/jurisdiction.yaml`, never hard-coded. `scripts/saft_validate.py` is
  the one deliberate country-specific script, kept as a worked example of a
  jurisdiction check.

## License

[MIT](LICENSE).
