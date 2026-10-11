---
name: skill-creator
description: Create, revise, audit, or port reusable agent skills. Use when a user wants a new skill, wants to improve an existing SKILL.md, remove vendor-specific assumptions, package repeatable workflows or tools, or make a skill portable across AI agents and harnesses.
---

# Skill Creator

Treat a skill as a reusable instruction package consumed by an AI agent. Design the portable skill first; add harness-specific integration only when the target environment requires it.

## Core contract

Every skill must contain `SKILL.md` with YAML frontmatter followed by operational Markdown. Use this portable baseline:

```text
skill-name/
├── SKILL.md
├── scripts/       # deterministic helpers, when useful
├── references/    # material loaded only when needed
└── assets/        # templates or files used in outputs
```

Require only `name` and `description` in frontmatter. Treat additional fields, UI metadata, tool declarations, directory locations, invocation syntax, and discovery rules as adapter concerns rather than universal properties.

Use neutral terms such as “agent”, “runtime”, and “target harness”. Do not name a vendor in portable instructions unless the behavior genuinely depends on that vendor.

## Design principles

- Assume the agent is capable; include only non-obvious domain knowledge, procedures, constraints, and reusable resources.
- Put all trigger information in `description`, because many runtimes inspect metadata before loading the body.
- Write instructions in imperative form.
- Match specificity to risk: use heuristics for flexible work, pseudocode for preferred patterns, and tested scripts for fragile or repetitive operations.
- Keep `SKILL.md` focused and preferably below 500 lines. Move conditional or detailed material into directly linked reference files.
- Do not add changelogs, installation guides, or process diaries unless they are required inputs.
- Never assume a particular tool exists. State the required capability and give target-specific commands only in an adapter section or reference.

## Workflow

### 1. Establish the target contract

Inspect the destination repository, its agent instructions, installed examples, and validation tools. Determine the triggering requests, portability target, required structure, available capabilities, and validation path.

If no target contract is available, use the portable baseline and label assumptions explicitly. Read [references/agent-compatibility.md](references/agent-compatibility.md) when porting across runtimes or adding an adapter.

### 2. Derive reusable contents

For each representative request, reason through execution from scratch. Add only resources that reduce repeated work:

- add `scripts/` for deterministic, error-prone, or frequently rewritten operations;
- add `references/` for schemas, policies, detailed examples, or variant-specific guidance;
- add `assets/` for templates, boilerplate, icons, fonts, or output inputs.

Avoid empty directories and placeholder resources in the finished skill.

### 3. Initialize or inspect

For a new portable skill, run:

```bash
scripts/init_skill.py <skill-name> --path <parent-directory> [--resources scripts,references,assets] [--examples]
```

For an existing skill, skip initialization. Read its complete `SKILL.md`, directly referenced resources, repository instructions, and adapter metadata before editing.

### 4. Write the portable core

Use a short, hyphen-case name. Make the description explain both capability and trigger conditions. Organize the body around the task: workflow-based, task-based, reference-based, or a concise mixture.

Keep vendor-neutral behavior in the core. Isolate unavoidable platform behavior in clearly named adapter files or metadata directories. Do not let optional UI configuration redefine the skill’s operational semantics.

### 5. Add target adapters only when required

Follow the target harness’s documentation and repository examples. Keep adapter files additive: deleting them should leave a valid portable skill. Do not generate OpenAI, Claude, Gemini, or other vendor metadata by default.

When maintaining multiple adapters, derive them from the same `SKILL.md` semantics and verify that descriptions and example prompts do not drift.

### 6. Validate and exercise

Run the portable validator:

```bash
scripts/quick_validate.py <skill-directory>
```

Then run the target harness’s validator, if available. Execute every new script with a realistic case, inspect generated files, and test at least one representative trigger request. YAML validity alone does not prove the workflow works.

### 7. Review portability

Search for accidental coupling: vendor names, home-directory paths, fixed tool names, proprietary metadata, and assumptions about context loading or invocation syntax. Keep coupling only where documented as an intentional adapter.

Summarize what changed, what was tested, and which target-specific assumptions remain.
