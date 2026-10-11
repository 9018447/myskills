---
name: repo-map-agentsmd
description: 'Use this skill whenever the user asks to map a repository, create a code map, document architecture, onboard into a repo, create or improve AGENTS.md, or produce agent-facing repository documentation. This skill produces a single root AGENTS.md that contains both the operational agent instructions and the deeper code maps inside the same file.'
compatibility: 'Cross-platform. Works best when repository files, config, and optional git history are available.'
argument-hint: 'Optional: focus area such as "architecture only", "testing and commands", or "AGENTS.md refresh"'
---

# Create a single AGENTS.md with embedded deeper code maps

Use this skill when the user wants one final documentation artifact.

The only required output is a root `AGENTS.md`. That file must contain:

1. the concise agent operating guidance, and
2. the deeper code maps inside the same file.

Do not split the output into `docs/codebase/` files unless the user explicitly asks for that variant.

Only document what is verifiable from repository files, configuration, and terminal output. Never infer architecture, tooling, or workflows from naming alone.

## Output contract

Before finishing, all of the following must be true:

1. `AGENTS.md` exists at the repository root.
2. `AGENTS.md` is the single source of output for this skill.
3. `AGENTS.md` contains both the operational instructions and the deeper code maps.
4. Every non-trivial claim is traceable to files, config, or terminal output.
5. Unknowns are marked as `[TODO]`.
6. Team-intent decisions that cannot be verified from the repo are marked as `[ASK USER]`.
7. The final `AGENTS.md` is internally organized so that the quick-start operational guidance appears first and the deeper maps appear later in clearly named sections.
8. Final response summarizes what was created, lists numbered `[ASK USER]` items, and highlights any intent-vs-reality gaps.

## Single-file rule

This skill intentionally produces one file.

- Put quick operational guidance near the top of `AGENTS.md`.
- Put deeper reference material later in the same file under dedicated sections.
- Do not create `docs/codebase/STACK.md`, `STRUCTURE.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `INTEGRATIONS.md`, `TESTING.md`, or `CONCERNS.md` unless the user explicitly asks for multi-file output.
- Keep one-file output readable by using short summary sections first, then deeper sections later.

## Recommended workflow

Copy and track this checklist:

```text
- [ ] Phase 1: Capture scope and read repo intent
- [ ] Phase 2: Investigate the repository and gather evidence
- [ ] Phase 3: Draft AGENTS.md with operational guidance first
- [ ] Phase 4: Embed the deeper code maps in AGENTS.md
- [ ] Phase 5: Validate for accuracy, readability, and single-file completeness
```

## Focus area mode

If the user gives a focus area such as `architecture only`, `testing and commands`, or `AGENTS.md refresh`:

1. Still inspect repository intent and structure first.
2. Fully complete the focus area sections first.
3. Keep non-focus sections present when they are required for a usable `AGENTS.md`, but mark unresolved parts as `[TODO]`.
4. If the user asked only for an `AGENTS.md` refresh, still verify the underlying evidence before rewriting the file.

## Phase 1: Capture scope and read repo intent

1. Read the user request carefully and determine whether they want:
   - full repository onboarding,
   - a code map only,
   - an `AGENTS.md` only,
   - or a one-file merged output.
2. Read repository intent documents before reading implementation details. Prioritize files such as:
   - `README*`
   - `PRD*`
   - `TRD*`
   - `SPEC*`
   - `DESIGN*`
   - `ROADMAP*`
3. Summarize the stated project intent in a few lines.
4. Treat repository intent as a claim to verify, not a fact to copy blindly.

## Phase 2: Investigate the repository

Gather evidence for these documentation areas:

1. stack and runtime,
2. repository structure and entry points,
3. architecture and flow,
4. conventions and editing rules,
5. integrations and environment,
6. testing workflow,
7. risks and open questions.

Use file-backed evidence for every section.

## Investigation prompts

### Stack

- What manifest files define the runtime and dependencies?
- What exact versions are declared for the runtime and major frameworks?
- Which commands are actually wired in manifests, task runners, or CI?

### Structure

- Where does source code live?
- What are the runtime, worker, CLI, or job entry points?
- How is the repository partitioned by layer, feature, or package?
- Which directories are source, generated output, tooling, or infrastructure?

### Architecture

- What is the real flow from entry point to domain logic to data or integration layers?
- Which files prove that flow?
- What constraints shape the system design?

### Conventions

- What naming patterns appear repeatedly across real source files?
- Which linting, formatting, and type-check settings are enforced by config?
- How are errors, logs, and imports handled in practice?

### Integrations

- What external systems are used?
- Where are credentials sourced from?
- What retry, timeout, or observability patterns exist?

### Testing

- What test frameworks and commands are configured?
- Where do tests live?
- What mocking and coverage patterns are visible in code and config?

### Concerns

- Which risks are visible from TODOs, fragile files, or missing safeguards?
- Which areas look high-churn or tightly coupled?
- Which questions require team intent instead of repository evidence?

## Phase 3: Draft the operational part of AGENTS.md

Write the agent-facing guidance first, because that is what a coding agent needs to act quickly.

At minimum, include these top-level sections when the evidence exists:

1. `## Project Overview`
2. `## Repository Map`
3. `## Setup Commands`
4. `## Development Workflow`
5. `## Testing Instructions`
6. `## Code Style and Conventions`
7. `## Integrations and Environment`
8. `## Risks and Gotchas`
9. `## Deeper Code Maps`

Add `## Monorepo Notes` when applicable.

### How to write the operational sections

#### `Project Overview`

- Briefly describe what the project does.
- Mention the primary stack and architecture shape.
- Keep it short and action-oriented.

#### `Repository Map`

- Summarize the top-level layout in a compact way.
- Mention the main entry points and major module boundaries.
- Keep this section short; deeper structural detail belongs later in the file.

#### `Setup Commands`

- Include only commands that are verified from manifests, task files, CI, or docs.
- Prefer exact commands over prose.

#### `Development Workflow`

- Document how to run the app locally, where to make changes, and how to move safely between modules.
- Include package-manager or workspace specifics when relevant.

#### `Testing Instructions`

- Tell the agent exactly how to run relevant tests.
- Explain where tests live and any focused-test patterns.

#### `Code Style and Conventions`

- Capture the conventions that affect edits: naming, imports, formatting, linting, and error handling.

#### `Integrations and Environment`

- Summarize external systems and config sources the agent must respect.
- Mention safe handling of secrets and environment templates.

#### `Risks and Gotchas`

- Surface the highest-risk areas, fragile boundaries, and common mistakes.
- Keep it practical.

## Phase 4: Embed the deeper code maps in AGENTS.md

After the operational sections, add a deeper reference block inside the same file.

Use this structure:

```markdown
## Deeper Code Maps

### Stack and Tooling
### Structure Map
### Architecture Map
### Conventions Map
### Integrations Map
### Testing Map
### Concerns and Open Questions
```

### What each deeper section should contain

#### `### Stack and Tooling`

Document:

- primary language and runtime version,
- package manager and build system,
- production frameworks and key dependencies,
- development tooling,
- important commands,
- environment and runtime constraints.

#### `### Structure Map`

This is the deeper repo map / code map. Include:

- a top-level map of meaningful directories and files,
- entry points,
- major module boundaries,
- naming and organization rules,
- monorepo workspace boundaries if present.

#### `### Architecture Map`

Document:

- architectural style,
- primary runtime or request flow,
- layer or module responsibilities,
- repeated design patterns,
- architectural risks or constraints.

#### `### Conventions Map`

Document:

- naming patterns,
- linting and formatting configuration,
- import and module conventions,
- error and logging behavior,
- testing conventions that shape day-to-day work.

#### `### Integrations Map`

Document:

- external APIs,
- databases and queues,
- auth and credential handling,
- reliability behavior,
- observability around integrations.

#### `### Testing Map`

Document:

- frameworks and commands,
- test layout,
- scope matrix for unit/integration/e2e coverage,
- mocking and isolation strategy,
- quality signals and gaps.

#### `### Concerns and Open Questions`

Document:

- top risks,
- technical debt,
- security concerns,
- performance and scaling concerns,
- fragile or high-churn areas,
- numbered `[ASK USER]` questions.

For each deeper section, end with a short evidence list.

## Writing pattern for one-file output

Use summary-first, detail-later structure.

- Put short operational guidance before deeper reference material.
- Avoid repeating the same sentences in both places.
- In the upper operational sections, summarize.
- In the deeper sections, provide the detailed map and evidence.

## Validation loop

Before finalizing, run this validation loop:

1. Check every section for unsupported claims.
2. Check every required section for empty placeholders.
3. Make sure unknowns use `[TODO]` instead of guesses.
4. Make sure intent gaps use `[ASK USER]`.
5. Confirm each deeper map section ends with concrete evidence paths.
6. Confirm `AGENTS.md` contains actionable instructions and verified commands.
7. Confirm the file stays readable as one artifact:
   - quick operational guidance first,
   - deeper code maps later,
   - no chaotic duplication between the two layers.
8. Re-read `AGENTS.md` as if you were a coding agent opening the repo for the first time.

Validation passes only when:

- no major claim lacks evidence,
- no required section is empty,
- the operational sections are scannable,
- the deeper maps are present in the same file,
- the file remains coherent as a single deliverable.

## Monorepo handling

If the repository is a monorepo:

- map the root structure first,
- identify every workspace or subproject,
- note package-specific entry points, commands, and conventions,
- keep the root operational guidance focused on navigation and shared workflow,
- place package-specific deeper maps under the relevant deeper section when they materially change agent behavior.

If the monorepo is large, mention that nested `AGENTS.md` files may still be appropriate, but only create them when the user explicitly asks for multi-file agent docs.

## Gotchas

- README files may describe intended architecture rather than the current system. Verify against source.
- Do not document `dist/`, `build/`, `.next/`, `generated/`, or other compiled artefacts as source conventions.
- TypeScript path aliases and workspace indirection can hide real module boundaries; resolve them before writing the repo map.
- `.env.example`, `.env.template`, and CI configs often reveal required environment variables and runtime assumptions.
- Test TODOs are not the same as production debt; separate them clearly.

## Anti-patterns

| Don’t | Do instead |
|---|---|
| Create seven extra files when the user asked for one file | Embed the deeper code maps inside `AGENTS.md` |
| Dump every detail at the top of the file | Put operational guidance first and deeper maps later |
| Guess frameworks from folder names | Verify with manifests and imports |
| List vague commands like “run tests” | Provide exact commands the agent can execute |
| Hide uncertainty | Mark `[TODO]` or `[ASK USER]` explicitly |

## Final response requirements

When the work is done, provide:

1. a short summary of the generated `AGENTS.md`,
2. notable intent-vs-reality differences,
3. every `[ASK USER]` item as a numbered list,
4. any follow-up recommendation for keeping the file current as the repository evolves.
