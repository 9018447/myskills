# Division of Coding Labor

## Hard constraints

Claude Code (the main agent) does only three things:

- **Write documents** — specs, tickets, plans, READMEs, review comments.
- **Orchestrate** — split work into tasks, dispatch, track status, summarize results.
- **Hold the global picture** — architecture decisions, acceptance criteria, cross-task consistency.

Coding work:

- **Trivial and single-file changes** (bug fixes, added tests, small features) are done by the main agent directly. If a change turns out to touch multiple production files, it is no longer trivial — switch to the flow below.
- **Cross-file implementation always enters through `/poteto-mode`.** The dispatch chain (grilling → `/split-tickets` → `/acpxtodo` → review), the single-agent vs concurrent choice, worktrees, and review gates are all defined inside that skill — they are not restated here. The main agent never codes across files itself: when a task needs it and `/poteto-mode` is not running, the user starts it.
- After dispatch, the main agent reviews the output (diff, test results) and dispatches fixes back if problems are found; it does not rewrite the work itself.
- Read-only work (investigation, search, reading code) and document files (`.md`) are not coding; the main agent does them itself.
