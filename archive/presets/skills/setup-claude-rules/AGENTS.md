# setup-claude-rules — source directory

This directory is the source of the `setup-claude-rules` skill. All steering content lives in the source files below; do not duplicate it here.

- `SKILL.md` — skill flow (script-driven install, companion-skill check)
- `install.sh` / `check-tools.sh` — deterministic installer + tool availability check
- `ADD_RULES.md` → installed as `.claude/rules/code-search.md`
- `CODING_RULES.md` → installed as `.claude/rules/coding-principle.md`
- `VERIFY_RULES.md` → installed as `.claude/rules/verification.md`
- `PRINCIPLES_RULES.md` → installed as `.claude/rules/work-principles.md`
- `APPEND_CLAUDE.md` — the summary block appended to CLAUDE.md/AGENTS.md

The installed summary block (Tool Routing / Division of Labor / Verification / Work Principles) is generated from `APPEND_CLAUDE.md`: edit that file, then re-run `install.sh` against the target repo.
