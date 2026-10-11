---
name: setup-omp-rules
description: Install the omp ruleset into the current repo via the install.sh script — code-search routing (details .omp/context/code-search.md), coding division of labor (.omp/context/coding-labor.md), verification & review rules (.omp/context/verification.md), and work principles (.omp/context/work-principles.md); the summary block goes into AGENTS.md (or .omp/AGENTS.md when shadowing requires it); plus one TTSR nudge rule (.omp/rules/no-shell-search.md) that steers shell find/grep/rg toward omp search tools. Script-driven: the agent only runs the script and relays its output, then does the read-only companion-skill check below. Claude version untouched (see setup-claude-rules).
tags: [user]
disable-model-invocation: true
---

# Install the omp ruleset (script-driven)

The install is done deterministically by `install.sh` in this skill directory; the agent does not write anything itself. All decisions (where the summary block goes, overwriting existing context files, updating the summary block in place) are made by the script. The agent does not explore, show drafts, or ask the user — it runs the script, relays the output, then does the read-only companion-skill check below. The skill is re-runnable: the script is idempotent, old blocks are updated in place, never appended twice.

## Trigger

Run the script with one optional argument — the target repo root, defaulting to the current working directory:

```bash
bash <skill-dir>/install.sh [repo-root]
```

The skill directory is where this SKILL.md lives; the scripts sit next to it.

## Relaying results

The script outputs one result summary. Relay it to the user verbatim, without extra commentary. If the summary marks a tool `MISSING`, tell the user which one is missing and that re-running this script after installing it is enough — the context files are written regardless, because a missing tool does not block the install.

What the script does (fully deterministic, no agent involvement):

- **Tool check** — calls `check-tools.sh` in this directory, reporting the status of `jg`, `rg`, `zg`, `ast-grep`, `gitnexus`, `omp` (jg additionally gets an auth check). Missing tools do not block the install.
- **Write context details** — ensure `.omp/context/` exists and symlink `code-search.md`, `coding-labor.md`, `verification.md`, `work-principles.md` to [ADD_RULES.md](./ADD_RULES.md), [CODING_RULES.md](./CODING_RULES.md), [VERIFY_RULES.md](./VERIFY_RULES.md), and [PRINCIPLES_RULES.md](./PRINCIPLES_RULES.md), overwriting what is there.
- **Install the TTSR nudge rule** — ensure `.omp/rules/` exists and symlink `no-shell-search.md` to [rules/no-shell-search.md](./rules/no-shell-search.md). No settings merge, no hook modules.
- **Pick the summary target** (exactly one, never both `AGENTS.md` and `.omp/AGENTS.md`) — existing `.omp/AGENTS.md` wins; otherwise existing root `AGENTS.md`; otherwise (only `.claude/CLAUDE.md` present, whose claude provider outranks standalone `AGENTS.md`) create `.omp/AGENTS.md` so the block is not shadowed; otherwise create root `AGENTS.md`. A root `CLAUDE.md` is not recognized by omp and is left untouched.
- **Write the summary** — replace everything from the first `## Tool Routing` heading to the end of the target file with [APPEND_AGENTS.md](./APPEND_AGENTS.md) (with its `{{CTX}}` placeholder resolved to the matching relative context path); user content above the block survives.

## Companion-skill check

After running the script and relaying, do one read-only check of two companion skills in the target repo. Check first, never overwrite blindly: anything already present gets one line "already installed, skipping"; only missing items get a suggestion.

- **setup-matt-pocock-skills** — look for an `## Agent skills` section in AGENTS.md/CLAUDE.md, a repo-root `GLOSSARY.md`, or `docs/agents/`. Any of these, skip; otherwise suggest the user run `/setup-matt-pocock-skills` (that skill forbids model-triggered runs).
- **show-me-your-work** — look for `.scratch/`, `.audit/`, or an existing decision-log convention in steering files. If present, skip; otherwise tell the user that in later long-running tasks, autonomous runs, or when the user says "until … is done" / sets a goal, the agent will use that skill directly to record the decision trail (the agent may trigger it itself, no permission needed).
- **rule-companion skills** — the rules reference skills that carry the details: `jev` and `jevgrep`. Check whether each is present under the omp layout (`.omp/skills/`, `~/.omp/agent/skills/`) and the compat location (`.claude/skills/`); report any that are missing with one line: "fetch it from https://github.com/9018447/myskills". `poteto-mode` is intentionally not checked: it is Claude-only, and on the omp side its dispatch chain is replaced by the plan-mode + `task` division of labor in the summary. This check is informational only and never blocks the install.

## Completion criteria

The run succeeds when all writes have landed — the four context files match their templates, the TTSR rule file is in place, the summary block matches [APPEND_AGENTS.md](./APPEND_AGENTS.md) with `{{CTX}}` resolved and no duplicate sections, and the script exits 0 — plus a verdict for the companion check: each of the three marked "present" or "missing".
