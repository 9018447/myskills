---
name: ulw
description: "Inspect an entire working directory, build a repository architecture map, summarize each meaningful file, and produce a concrete AGENTS.md that follows create-agentsmd-style guidance. Use this whenever the user asks for a repo inventory, codebase map, file-by-file summary, onboarding notes for coding agents, or wants AGENTS.md / agent instructions generated from an existing project. Prefer autonomous inspection over follow-up questions: infer from repository evidence first, keep questions rare, and only ask when a required fact truly cannot be discovered from files, configs, scripts, or CI."
---

# ULW - Understand, List, Write

This skill is for repository reconnaissance that ends in a useful `AGENTS.md`.

It is designed for instruction-following models that are capable but too eager to ask the user for clarification. The cure is not silence; it is disciplined evidence gathering. Read the repo broadly, infer carefully, and draft a strong result before considering questions.

## Goals

When this skill triggers, complete all three outcomes in one pass unless the user explicitly narrows scope:

1. **Repository architecture** - explain the top-level structure and major subsystems.
2. **File inventory with summaries** - provide a concise summary for each meaningful file, grouped by directory.
3. **`AGENTS.md` output** - generate or update a repo-root `AGENTS.md` using evidence from the codebase.

## Default behavior

- **Inspect first, ask later.** Start from the filesystem, config files, scripts, and docs.
- **Assume the standard filename is `AGENTS.md`.** If the user says `AGENT.md`, treat that as intent for the standard `AGENTS.md` format unless the repo already uses a different convention.
- **Prefer a useful draft over blocking on uncertainty.** If one detail is missing, note the assumption and continue.
- **Ask at most one precise question** only after exhausting available evidence.
- **Do not pretend you inspected files you did not inspect.** Mark grouped or partial treatment clearly.

## Evidence-first workflow

### 1. Establish repository shape

Inspect the working directory and identify:

- Top-level folders and their purpose
- Build/test/package files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `docker-compose.yml`, etc.)
- CI/CD and automation (`.github/workflows`, scripts, task runners)
- Existing docs (`README*`, `CONTRIBUTING*`, existing `AGENTS.md`, design notes)
- Monorepo boundaries or nested apps/packages

If the repo is large, still cover the whole tree, but compress treatment for obviously generated, vendored, cached, or binary-heavy areas.

### 2. Build the architecture map

Produce a directory-oriented explanation, not just a raw tree dump.

For each top-level directory or major package, explain:

- What it contains
- Whether it is source, tests, scripts, docs, config, build output, or external/generated material
- How it relates to other directories

### 3. Summarize files systematically

Summarize files in grouped order by directory.

For each file, capture the most useful fact for a future coding agent:

- **Source files** - primary responsibility, exported behavior, or subsystem role
- **Config files** - what they configure and which tools depend on them
- **Docs** - what guidance they provide
- **Scripts** - what they automate and likely entry points
- **Tests** - what behavior they verify and test framework clues

For large or low-value areas, use a grouped note instead of noisy one-line summaries for every artifact. Examples:

- Generated files
- Vendored dependencies
- Minified bundles
- Binary assets with no agent-facing logic
- Cache directories

When grouping, say so explicitly.

### 4. Extract actionable commands

Before writing `AGENTS.md`, gather commands from actual repo evidence:

- Install / bootstrap
- Development server / watch mode
- Test commands
- Lint / format / typecheck
- Build / package / deploy
- Targeted test commands when discoverable

Prefer commands from scripts and CI over guesses. If a command is inferred rather than directly declared, label it as an inference.

### 5. Write `AGENTS.md`

Create a repo-root `AGENTS.md` that is practical for future coding agents.

Base it on the outline in `references/agents-outline.md` and adapt it to the repo. Include sections only when supported by evidence.

Good `AGENTS.md` qualities:

- Concrete commands instead of vague advice
- Repo-specific structure instead of generic filler
- Clear testing and verification expectations
- Important gotchas, generated paths, and boundaries
- Explicit distinction between fact and assumption when needed
- Tight enough to stay high-signal; prefer roughly 150 lines or less unless the repository genuinely needs more

## Anti-over-questioning rules

Use these rules to avoid the annoying habit of repeatedly interrogating the user:

1. **Do not ask for permission to inspect the repo.** Inspect it.
2. **Do not ask what framework the project uses before checking files.** Read the evidence.
3. **Do not ask how to run tests before checking package scripts, Makefiles, CI, or docs.**
4. **Do not ask whether the user wants `AGENTS.md` sections that can be inferred from the repo.** Draft them.
5. **If one fact is missing, continue with a best-effort draft and label the uncertainty.**
6. **Only ask a question if the answer changes the final output materially and cannot be derived from inspection.**

## Output format

Use this structure unless the user requested a different format:

````markdown
# Repository Architecture
## Overview
## Top-level structure
## Major subsystems

# File Inventory
## <directory>
- `<path>` - <concise summary>

# Draft AGENTS.md
```markdown
# AGENTS.md
...
```

# Notes
- Assumptions
- Missing evidence
- Suggested follow-up improvements
````

## Quality bar for file summaries

A strong file summary answers one of these questions quickly:

- Why does this file exist?
- What breaks if it changes?
- Which tool, service, or workflow depends on it?
- Is it hand-written, generated, or low-signal support material?

Avoid empty summaries like "configuration file" or "contains code" when something more precise is available.

## Monorepo handling

If the repository contains multiple packages or apps:

- Start with a root architecture summary
- Explain each package/app boundary
- Prefer one root `AGENTS.md` plus notes recommending nested `AGENTS.md` files where appropriate
- Call out package-specific setup or test commands when they differ

## Safety and scope rules

- Do not invent commands that are unsupported by repo evidence.
- Do not summarize secrets or dump sensitive values.
- Do not spend excessive space on lockfiles, caches, or generated assets.
- Do not overwrite an existing high-quality `AGENTS.md` blindly; compare and improve it.
- Do not stop after producing only the tree; the file summaries and `AGENTS.md` are part of the job.

## Boundaries section for generated AGENTS.md

When the repository evidence supports it, prefer a short three-tier boundaries section inside the generated `AGENTS.md`:

- `✅ Always do` - required habits such as running tests, lint, or respecting package boundaries
- `⚠️ Ask first` - risky changes like schema changes, dependency additions, or CI edits
- `🚫 Never do` - editing generated/vendor directories, committing secrets, deleting tests to bypass failures

Keep this section repo-specific and grounded in actual project constraints.

## Example trigger phrases

This skill should be used when the user says things like:

- "Scan this repo and tell me what every file does"
- "Give me a codebase map before we start changing things"
- "Generate an AGENTS.md for this project"
- "Inventory this repository and summarize the architecture"
- "Create agent onboarding docs from the current working directory"

## Final reminder

Your job is not merely to describe the repository. Your job is to convert repository evidence into a working mental model and then into a useful `AGENTS.md` that helps the next coding agent succeed without bothering the user for information the repo already contains.
