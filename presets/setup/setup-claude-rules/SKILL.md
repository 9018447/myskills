---
name: setup-claude-rules
description: Install the agent ruleset into the current repo via the install.sh script — code-search routing (details .claude/rules/code-search.md), coding division of labor (.claude/rules/coding-principle.md), verification & review rules (.claude/rules/verification.md), and work principles (.claude/rules/work-principles.md, distilled from the pstack principle-* series); the summary block goes into CLAUDE.md/AGENTS.md. Script-driven: the agent only runs the script and relays its output, then does one read-only check of three companion skills (setup-pre-commit, setup-matt-pocock-skills, show-me-your-work) — skip the ones present, suggest only the missing ones. Use when the user says "install search routing / install coding rules / set up claude rules". The ruleset keeps growing.
tags: [user]
disable-model-invocation: true
---

# Install the agent ruleset (script-driven)

The install is done deterministically by `install.sh` in this skill directory; the agent does not write anything itself. All decisions (where the summary block goes, overwriting existing rule files, updating the summary block in place) are made by the script. The agent does not explore, show drafts, or ask the user — it runs the script, relays the output, then does the read-only companion-skill check below. The skill is re-runnable: the script is idempotent, old blocks are updated in place, never appended twice.

## Trigger

Run the script with one optional argument — the target repo root, defaulting to the current working directory:

```bash
bash <skill-dir>/install.sh [repo-root]
```

The skill directory is where this SKILL.md lives; the scripts sit next to it.

## Relaying results

The script outputs one result summary. Relay it to the user verbatim, without extra commentary. If the summary marks a tool `MISSING`, tell the user which one is missing and that re-running this script after installing it is enough — the rule files are written regardless, because a missing tool does not block the install.

What the script does (fully deterministic, no agent involvement):

- **Tool check** — calls `check-tools.sh` in this directory, reporting the status of `jg`, `rg`, `zg`, `ast-grep`, `gitnexus`, `acpx` (jg additionally gets an auth check; includes an LSP host note).
- **Write rule details** — ensure `.claude/rules/` exists; symlink `code-search.md`, `coding-principle.md`, `verification.md`, and `work-principles.md` to [ADD_RULES.md](./ADD_RULES.md), [CODING_RULES.md](./CODING_RULES.md), [VERIFY_RULES.md](./VERIFY_RULES.md), and [PRINCIPLES_RULES.md](./PRINCIPLES_RULES.md). Existing files are overwritten — install means overwrite, no asking.
- **Pick the summary target** — priority: use `CLAUDE.md` if it exists; otherwise `AGENTS.md` if it exists; if neither exists, create `AGENTS.md`. Never touch both files.
- **Write the summary** — replace everything from the first `## Tool Routing` heading to the end of the target file with the block in [APPEND_CLAUDE.md](./APPEND_CLAUDE.md). User content above the block is left untouched; duplicate blocks are replaced, not appended.

## Companion-skill check

After running the script and relaying, do one read-only check of three companion skills in the target repo. Check first, never overwrite blindly: anything already present gets one line "already installed, skipping"; only missing items get a suggestion.

- **setup-pre-commit** — look for `.husky/pre-commit`, a `"prepare": "husky"` script or `lint-staged` config in package.json. Any of these counts as installed, skip; otherwise suggest the user run `/setup-pre-commit` (that skill forbids model-triggered runs).
- **setup-matt-pocock-skills** — look for an `## Agent skills` section in AGENTS.md/CLAUDE.md, a repo-root `GLOSSARY.md`, or `docs/agents/`. Any of these, skip; otherwise suggest the user run `/setup-matt-pocock-skills` (same restriction).
- **show-me-your-work** — look for `.scratch/`, `.audit/`, or an existing decision-log convention in steering files. If present, skip; otherwise tell the user that in later long-running tasks, autonomous runs, or when the user says "until … is done" / sets a goal, the agent will use that skill directly to record the decision trail (the agent may trigger it itself, no permission needed).

## Completion criteria

The run succeeds only when all writes have landed, and the script guarantees them: the four rule files exist and match the templates; the target file's summary block matches the template with no duplicate sections. The script signals success via its exit code and result lines; the agent reads those, decides, and relays to the user. The companion-skill check also needs a verdict — each of the three marked "present" or "missing" — before the run is over.
