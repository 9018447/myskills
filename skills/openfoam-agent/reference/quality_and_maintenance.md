# Documentation quality and maintenance

## Quality goals (actionable for an AI assistant)

Each reference document should:

- state a clear purpose / scope
- include a checklist that can be executed step-by-step
- include at least one copy-pastable config/command snippet
- map common errors to root causes and a fix path (especially troubleshooting docs)
- use traceable relative links between docs

## Language convention

All documentation, code, and comments in this repository must be written in English.

## Maintenance conventions

- keep `SKILL.md` as navigation + workflow, not a long dump of details
- keep details in `reference/`, split by topic
- any new doc must:
  - add an entry link in `SKILL.md`
  - pass `scripts/skill_quality_check.py` (broken links + length limits)

## Suggested future topics

- `boundary_conditions.md`: boundary types and baseline combinations
- `fv_solution_patterns.md`: common linear solver / relaxation templates
- `snappyhexmesh_playbook.md`: STL cleanup and snappy strategies
- `parallel_run.md`: parallel decompose/reconstruct conventions
