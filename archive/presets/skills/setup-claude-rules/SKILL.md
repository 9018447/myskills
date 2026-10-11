---
name: setup-claude-rules
description: Install the agent ruleset into the current repo via the install.sh script — code-search routing (details .claude/rules/code-search.md), coding division of labor (.claude/rules/coding-principle.md), verification & review rules (.claude/rules/verification.md), and work principles (.claude/rules/work-principles.md, distilled from the pstack principle-* series); the summary block goes into CLAUDE.md/AGENTS.md; plus a SessionStart routing hook (.claude/hooks/session-start.sh, extracted from the pstack-claude plugin and adapted) that injects poteto-mode routing at session start, and a PreToolUse reminder hook (.claude/hooks/tool-reminder.sh) that nudges routing per tool call. Script-driven: the agent only runs the script and relays its output, then does one read-only check of two companion skills (setup-matt-pocock-skills, show-me-your-work) and the rule-companion skills (jev, jevgrep, poteto-mode) — skip the ones present, suggest only the missing ones. Use when the user says "install search routing / install coding rules / set up claude rules". The ruleset keeps growing.
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

- **Tool check** — calls `check-tools.sh` in this directory, reporting the status of `jg`, `rg`, `zg`, `ast-grep`, `gitnexus`, `acpx` (jg additionally gets an auth check). Missing tools do not block the install.
- **Write rule details** — ensure `.claude/rules/` exists and symlink `code-search.md`, `coding-principle.md`, `verification.md`, `work-principles.md` to [ADD_RULES.md](./ADD_RULES.md), [CODING_RULES.md](./CODING_RULES.md), [VERIFY_RULES.md](./VERIFY_RULES.md), and [PRINCIPLES_RULES.md](./PRINCIPLES_RULES.md), overwriting what is there.
- **Pick the summary target** — `CLAUDE.md` if it exists, otherwise `AGENTS.md` (created if neither); never both.
- **Write the summary** — replace everything from the first `## Tool Routing` heading to the end of the target file with [APPEND_CLAUDE.md](./APPEND_CLAUDE.md); user content above the block survives.
- **Install the SessionStart routing hook** — symlink the two hook files into `.claude/hooks/` and register the SessionStart entry (idempotent, merge-not-overwrite) in `.claude/settings.json`. The injected text routes multi-file / design / unknown-cause-bug tasks through `poteto-mode`, with direct entry points `tdd`, `architect`, `how`, `why`, `arena`, `interrogate`. Disable per-repo by removing the entry.
- **Install the PreToolUse reminder hook** — symlink [tool-reminder.sh](./tool-reminder.sh) into `.claude/hooks/` and register the PreToolUse entry for `Bash|Read|Write|Edit|NotebookEdit` in the same settings file. Per call it injects: Bash with `find`/`grep`/`rg` → the jg → zg/ast-grep/GitNexus routing reminder plus the context-mode note; any Bash → the context-mode note; `Read` → analyze with `ctx_execute_file` unless editing; `Write`/`Edit`/`NotebookEdit` → batch chains in one codemode script. Disable per-repo by removing the entry.

## Companion-skill check

After running the script and relaying, do one read-only check of two companion skills in the target repo. Check first, never overwrite blindly: anything already present gets one line "already installed, skipping"; only missing items get a suggestion.

- **setup-matt-pocock-skills** — look for an `## Agent skills` section in AGENTS.md/CLAUDE.md, a repo-root `GLOSSARY.md`, or `docs/agents/`. Any of these, skip; otherwise suggest the user run `/setup-matt-pocock-skills` (that skill forbids model-triggered runs).
- **show-me-your-work** — look for `.scratch/`, `.audit/`, or an existing decision-log convention in steering files. If present, skip; otherwise tell the user that in later long-running tasks, autonomous runs, or when the user says "until … is done" / sets a goal, the agent will use that skill directly to record the decision trail (the agent may trigger it itself, no permission needed).
- **rule-companion skills** — the rules reference skills that carry the details: `jev`, `jevgrep`, and `poteto-mode`. Check whether each is present in the target agent's skills directory; report any that are missing with one line: "fetch it from https://github.com/9018447/myskills". This check is informational only and never blocks the install.

## Completion criteria

The run succeeds when all writes have landed — the four rule files match their templates, the summary block matches [APPEND_CLAUDE.md](./APPEND_CLAUDE.md) with no duplicate sections, and the script exits 0 — plus a verdict for the companion check: each of the three marked "present" or "missing".
