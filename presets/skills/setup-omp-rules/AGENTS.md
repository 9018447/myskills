# setup-omp-rules — source directory

This directory is the source of the `setup-omp-rules` skill. All steering content lives in the source files below; do not duplicate it here.

- `SKILL.md` — skill flow (script-driven install, companion-skill check)
- `install.sh` / `check-tools.sh` — deterministic installer + tool availability check
- `ADD_RULES.md` → installed as `.omp/context/code-search.md`
- `CODING_RULES.md` → installed as `.omp/context/coding-labor.md`
- `VERIFY_RULES.md` → installed as `.omp/context/verification.md`
- `PRINCIPLES_RULES.md` → installed as `.omp/context/work-principles.md`
- `APPEND_AGENTS.md` — the summary block appended to AGENTS.md / .omp/AGENTS.md (`{{CTX}}` resolved by install.sh)
- `rules/no-shell-search.md` → installed as `.omp/rules/no-shell-search.md` (TTSR nudge, no hooks)

The installed summary block (Tool Routing / Division of Labor / Verification / Work Principles) is generated from `APPEND_AGENTS.md`: edit that file, then re-run `install.sh` against the target repo.
