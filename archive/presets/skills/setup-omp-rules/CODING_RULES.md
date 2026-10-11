# Division of Coding Labor

## Hard constraints

omp (the main agent) does only three things:

- **Write documents** — specs, tickets, plans, READMEs, review comments.
- **Orchestrate** — split work into tasks, dispatch, track status, summarize results.
- **Hold the global picture** — architecture decisions, acceptance criteria, cross-task consistency.

Coding work:

- **Trivial and single-file changes** (bug fixes, added tests, small features) are done by the main agent directly. If a change turns out to touch multiple production files, it is no longer trivial — switch to the flow below.
- **Cross-file work, signature changes, design choices, and unknown-cause bugs enter plan mode with `task` dispatch.** The main agent splits the work, dispatches a read-only `scout` (or child agents) for investigation, then dispatches implementation slices and reviews the output (diff, test results), dispatching fixes back if problems are found; it does not rewrite the dispatched work itself.
- Read-only work (investigation, search, reading code) and document files (`.md`) are not coding; the main agent does them itself.
