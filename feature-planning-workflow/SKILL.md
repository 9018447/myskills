---
name: feature-planning-workflow
description: "Orchestrate the full planning pipeline in one shot: /grill-with-docs, then /to-prd, then /to-issues, then update the AGENTS.md index. Use whenever the user wants to turn a vague feature idea into grilled requirements, a PRD, numbered implementation issues, and a refreshed tracker index."
---

# feature-planning-workflow

## When to use

Activate when the user wants to move from a feature idea to a structured, ready-to-implement plan:

- "Plan this feature for me."
- "Write a PRD for X."
- "Break X into issues."
- "Grill me on this requirement and then write the PRD."
- "I need a feature spec."
- "Create tickets for X."

Do not activate for one-line fixes or tasks that already have a PRD/issue. In those cases, read the existing ticket directly.

## Goal

Produce, in one continuous workflow:

1. A grilled, agreed-upon understanding of the feature.
2. A PRD at `.scratch/<feature-slug>/PRD.md`.
3. Numbered implementation issues at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`.
4. An updated `AGENTS.md` that indexes all ADRs, PRDs, and issues and records the project's code-exploration / code-execution conventions.

## Code exploration and execution rules

- **Explore with MCP / semble first**: When you need to find functions, classes, callers, or understand code structure, use `codebase-memory-mcp` (`search_graph`, `trace_path`, `get_code_snippet`, `query_graph`) or `semble` (`search`, `find_related`) before falling back to `grep`/`glob`. Only use `grep`/`glob` for string literals, error messages, config values, non-code files, or when MCP/semble returns insufficient results.
- **Run code with context-mode**: Use `context-mode` for running tests, scripts, or any code execution step. Do not run ad-hoc shell snippets when a context-mode invocation is available.

## Workflow

### 1. Read the domain context

Before asking the user anything, read:

- `CONTEXT.md`
- `docs/adr/` (all ADRs)
- `docs/agents/issue-tracker.md`
- `docs/agents/triage-labels.md`
- `docs/agents/domain.md`
- `AGENTS.md`

This gives you the project's language, boundaries, and triage conventions.

### 2. Check for existing PRDs and issues

Scan `.scratch/` for existing feature directories. If a PRD or issue seems related to the user's request, present it and ask whether to:

- extend the existing PRD,
- create a new, separate one, or
- stop because the work is already tracked.

Use `codebase-memory-mcp` or `semble` to compare the user's request against existing PRDs when the relationship is unclear.

🔴 **CHECKPOINT**: Do not proceed to grilling until the user explicitly chooses one of the three options above.

### 3. Grill the requirement with `/grill-with-docs`

Invoke `/grill-with-docs` to interview the user relentlessly until the scope, constraints, success criteria, and out-of-scope items are clear. This skill also creates any needed ADRs and glossary updates via `/domain-modeling` as you go.

🛑 **STOP**: Before handing off to `/to-prd`, present the grilled scope in a tight decision-ready brief and wait for explicit approval or edits. Do not proceed until the user says yes or provides edits.

### 4. Generate the PRD with `/to-prd`

Invoke `/to-prd` to synthesize the grilled context into a PRD and publish it to the local tracker at `.scratch/<feature-slug>/PRD.md`.

- Pass the approved scope, key decisions, and any ADR/glossary changes from `/grill-with-docs`.
- Let `/to-prd` handle the PRD structure and template; do not reimplement its logic.

🛑 **STOP**: Before handing off to `/to-issues`, confirm the published PRD is final. If the user wants changes, edit the PRD first.

### 5. Generate issues with `/to-issues`

Invoke `/to-issues` to break the finalized PRD into numbered, vertically-sliced issues under `.scratch/<feature-slug>/issues/`.

- Pass the PRD path and the approved scope.
- Let `/to-issues` handle the issue template, dependency ordering, and acceptance criteria; do not reimplement its logic.

### 6. Mark completed work

If you know a PRD or issue is already implemented (e.g., the user tells you, or the relevant code is already merged and tested), update its `Status:` line to `ready-for-human` or `done` according to the repo's convention in `docs/agents/triage-labels.md`.

### 7. Update AGENTS.md

Run the bundled script located next to this SKILL.md at `scripts/update_agents_index.py` (for example, `.agents/skills/feature-planning-workflow/scripts/update_agents_index.py`) to refresh the index of ADRs, PRDs, and issues in `AGENTS.md`. The script will:

- list every ADR in `docs/adr/`,
- list every PRD in `.scratch/*/PRD.md`,
- list every issue in `.scratch/*/issues/*.md`,
- preserve a header/trailer so the index stays maintainable.

After the script runs, review the diff to make sure the index is accurate and that the project's code-exploration (`codebase-memory-mcp` / `semble`) and code-execution (`context-mode`) conventions are still present.

## Output format

Return a concise summary to the user:

- Feature slug and paths to the new PRD and issues.
- Whether any existing PRDs/issues were reused or marked complete.
- Key decisions that came out of grilling.
- Whether `AGENTS.md` was updated.
- Next step (e.g., "Review the PRD, then run `/tdd-2` on issue 01").

## Failure handling

| Situation | Action |
| --- | --- |
| User request is too vague to grill | Ask one clarifying question and stop until answered. |
| Existing PRD covers the same scope | Show it and ask: extend, replace, or stop. |
| Domain term conflicts with `CONTEXT.md` | Invoke `/domain-modeling` before writing the PRD. |
| User rejects grilled scope | Update the scope and re-grill; do not invoke `/to-prd` yet. |
| `/to-prd` produces a PRD that does not match the grilled scope | Edit the PRD or re-invoke `/to-prd` with clearer context. |
| `/to-issues` produces slices that are too coarse or too fine | Ask `/to-issues` to adjust the breakdown before publishing. |
| No ADR needed | Skip ADR creation; do not force one. |
| `<skill-dir>/scripts/update_agents_index.py` fails | Report the error, fix the index manually, and explain the workaround. |

## Anti-patterns and blacklist

Do **not** do the following. These are common failure modes that break the local ticket workflow or pollute the tracker.

| # | Anti-pattern | Why it hurts | What to do instead |
| --- | --- | --- | --- |
| 1 | Create a PRD without grilling first | Produces specs that miss constraints and user intent | Complete `/grill-with-docs` and get explicit approval before invoking `/to-prd` |
| 2 | Skip the existing-PRD check | Creates duplicate or conflicting tickets | Always scan `.scratch/` and ask the user when a related PRD/issue exists |
| 3 | Write issues before the PRD is finalized | Issues drift away from the approved spec | Confirm the PRD is final at the 🛑 STOP checkpoint before invoking `/to-issues` |
| 4 | Guess user answers during grilling | Bakes incorrect assumptions into the spec | Ask one question at a time and wait for real user input; do not simulate answers in production |
| 5 | Force an ADR for every feature | Pollutes `docs/adr/` with reversible decisions | Only create an ADR when the decision is hard to reverse, surprising, and a real trade-off |
| 6 | Use `grep`/`glob` as the first exploration tool | Misses semantic relationships and wastes tokens | Use `codebase-memory-mcp` or `semble` first; fall back to `grep`/`glob` only for literals and configs |
| 7 | Run code via ad-hoc shell snippets | Harder to reproduce and audit | Use `context-mode` for tests and script execution |
| 8 | Reimplement `/to-prd` or `/to-issues` logic inside this skill | Duplicates existing skills and drifts out of sync | Delegate PRD writing to `/to-prd` and issue splitting to `/to-issues` |
| 9 | Update `AGENTS.md` manually without the script | Risk of stale or malformed index | Run `<skill-dir>/scripts/update_agents_index.py` and review the diff |
| 10 | Mark issues as `ready-for-agent` automatically | Removes human triage from the loop | Keep new issues as `needs-triage`; only mark `ready-for-agent` or `done` when the user or codebase confirms completion |

## Dependencies

- `/grill-with-docs` — requirement interviews plus ADR/glossary maintenance.
- `/to-prd` — synthesize grilled context into a PRD.
- `/to-issues` — break the PRD into vertically-sliced implementation issues.
- `scripts/update_agents_index.py` — bundled with this skill; refreshes the AGENTS.md index.
