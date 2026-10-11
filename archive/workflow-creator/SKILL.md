---
name: workflow-creator
description: Distill the CURRENT conversation into a reusable, fixed-procedure workflow skill (goose-recipe style, but in standard skill format). Use this whenever the user wants to capture, save, distill, or productize a process they just walked through — phrases like "turn this conversation into a workflow/skill", "make this repeatable", "save this process", "沉淀这个流程", "把这次对话做成工作流/技能", "extract a recipe from this session", or any request to convert a completed session into a standardized procedure others (or future sessions) can re-run. Also trigger when the user finished a multi-step task and hints they will need to do it again.
---

# Workflow Creator

Turn a just-completed conversation into a durable workflow skill: a skill that looks like a normal skill on the outside, but whose body encodes a **fixed, repeatable procedure** — the Markdown equivalent of a [goose recipe](https://goose-docs.ai/docs/guides/recipes/recipe-reference/) (instructions + parameters + ordered steps + required tools, packaged for reuse).

The output is a standard skill directory:

```
<workflow-name>/
├── SKILL.md          # frontmatter + the fixed procedure
├── scripts/          # reusable scripts extracted from the conversation
├── templates/        # one-off code kept as annotated templates
└── references/       # optional: longer reference material
```

## Core principle

A conversation is a **trace of one execution**. A workflow skill is the **generalized procedure** behind that trace. Your job is abstraction, not transcription: keep the decisions, ordering, and hard-won details; discard the one-off context (specific file contents, timestamps, transient errors that were resolved, secrets).

The value of the generated skill comes from three things, in priority order:

1. **The step sequence and its rationale** — what to do, in what order, and *why* (including steps that were corrected mid-conversation; the correction is the lesson).
2. **Reusable scripts** — anything deterministic that should never be reinvented.
3. **Templates + invocation principles** — for code that cannot be reused verbatim, record the pattern and the rules for adapting it.

## Procedure

### 1. Replay the conversation and build the trace outline

**Input → Output:** the full current conversation → a trace outline (for yourself, not the user) containing:

- **Goal**: what the user ultimately wanted, stated in one sentence.
- **Phases**: the natural chapters of the session (e.g. explore → decide → implement → verify).
- **Key steps**: every action that mattered — commands run, files created/edited, tools called, external resources consulted.
- **Corrections and dead ends**: anything tried that failed or was revised. These are the most valuable content — a workflow that only records the happy path will lead the next execution into the same ditch.
- **User inputs**: every decision or value the user supplied. These are parameter candidates.

If the conversation is long or partially compacted, reconstruct from the summary and any kept messages; ask the user to fill gaps rather than guessing.

### 2. Classify every artifact: script, template, or prose

**Input → Output:** every piece of code/command from the trace outline → a classification per artifact, plus the extracted `scripts/` and `templates/` files. Decide:

- **Reusable script** — the logic is deterministic and only its inputs change next time (e.g. a file-transform script, a report generator, a scaffolding command sequence). Copy it into `scripts/`, generalize its literals into parameters/arguments, and add a short header comment stating purpose, inputs, and usage. If several test runs or steps rewrote the same helper, that is a strong signal it belongs in `scripts/`.
- **Template** — the code is structurally reusable but must be adapted each time (e.g. a config skeleton, a query pattern, a boilerplate file with project-specific holes). Save it in `templates/` with `{{PLACEHOLDER}}` markers, and in SKILL.md record its **invocation principles**: when to reach for it, which placeholders to fill from where, and what constraints must hold (versions, assumptions, ordering).
- **Prose step** — judgment calls, exploration, verification, communication. These become ordered steps in the SKILL.md body, written imperatively.

If you cannot decide between script and template, classify it as a template: an over-generalized script that silently does the wrong thing is worse than a template the executor adapts consciously.

### 3. Identify parameters

**Input → Output:** the user inputs from step 1 + the literals generalized in step 2 → a parameter table (name, meaning, default, where consumed).

Like a goose recipe's `parameters`, list the inputs a future execution must supply. Treat every user decision from this session as a parameter, unless it is structurally guaranteed to be identical next time. Reference parameters in the body as `{{param_name}}`.

### 4. Write the generated SKILL.md

**Input → Output:** the outputs of steps 1–3 + `assets/workflow-skill-template.md` (in this skill's directory) → the draft SKILL.md. Fill in:

- **frontmatter `name`**: short kebab-case verb phrase (e.g. `weekly-report`, `import-legacy-csv`).
- **frontmatter `description`**: what the workflow does + concrete trigger contexts. This is the only thing the triggering mechanism sees, so be specific and slightly pushy: name the situations and phrases that should invoke it, including cases where the user doesn't name the workflow explicitly.
- **Overview**: the goal, when to run it, expected inputs and outputs.
- **Parameters**: the table from step 3.
- **Workflow**: the ordered steps. Number them. For each step state what to do, which script/template/tool to use, and how to verify it succeeded before moving on. Note decision points ("if X, do Y") explicitly — fixed procedures survive by handling the branches that actually occurred.
- **Pitfalls**: the corrections and dead ends from step 1, phrased as "do this, not that" with the reason.

Style rules for the generated body:

- Imperative voice, one action per step.
- Explain *why* for anything non-obvious — the executor is a smart model that handles branches better when it understands intent, so prefer reasons over rigid MUSTs. Reserve hard constraints for steps where deviation genuinely breaks things.
- Keep it under ~500 lines; push long reference material into `references/`.

### 5. Strip session residue

**Input → Output:** the draft skill directory → the same directory with all session residue removed. Sweep the generated files for:

- Secrets, tokens, personal paths, hostnames — replace with placeholders.
- Conversation-specific literals (this repo's file names, today's date, this user's name) that should be parameters.
- References to "the conversation" itself — the workflow must stand alone for someone who never saw this session.

### 6. 🔴 CHECKPOINT: Confirm with the user

**Input → Output:** the sanitized directory + your summary of it → user sign-off, then delivery at the user-chosen location.

🛑 **STOP here — do not deliver before user sign-off.** Show the user: the chosen name, the parameter list, and the step outline. Ask whether any step is missing or over-specified. Adjust, then deliver the directory at the location the user wants (default: a new directory named after the workflow in the current working directory).

Do not run the workflow-creator's own eval loop — delivery of a clean, reviewed directory is the finish line. If the user later wants to test the *generated* workflow skill, use the skill-creator process on it.

## Failure modes and recovery

Distilling a session fails in predictable ways. Handle each explicitly instead of improvising:

| Trigger | First-line fix | If still failing |
|---|---|---|
| Conversation compacted / steps can't be reconstructed | Rebuild from the summary and kept messages; list the gaps as questions for the user | Deliver a "skeleton" workflow (steps + parameters, no scripts) marked `⚠️ incomplete`, rather than guessing content |
| No reusable scripts exist (session was all judgment calls) | Don't force scripts — write the recurring judgments as a decision tree in the body | If the user insists on `scripts/`, convert the strongest 1–2 patterns into `templates/` and explain why they are templates, not scripts |
| Extracted script turns out to depend on session-specific state (paths, env, files) | Parameterize the literals and declare dependencies in the header comment | Demote it to `templates/` with invocation principles — a script with hidden context is a trap |
| Generated body exceeds ~500 lines | Move long material into `references/` and leave pointers in the body | Split into a router SKILL.md + one skill per phase |
| Step order is ambiguous (the session jumped back and forth) | Order by the causal chain of the *successful* path, not by message timestamps | Write the uncertainty as an explicit decision point; never silently pick one |
| User's original goal is itself unclear | Stop and ask before writing anything — a workflow distilled from a misread goal is worse than none | — |

## Anti-patterns — do NOT do these

Each of these produces a workflow skill that *looks* finished but fails on reuse:

| # | Anti-pattern | Why it fails | Do instead |
|---|---|---|---|
| 1 | Transcribing the conversation into steps ("then I ran X, then the user said Y") | The next execution has different files and context; a transcript can't be followed | Abstract each step to its intent: what to achieve, with what tool, verified how |
| 2 | Recording only the happy path | The next executor hits the same dead end you hit, with no warning | Corrections and dead ends go into Pitfalls — they are the most valuable content |
| 3 | Leaving secrets, personal paths, or session-specific literals in scripts/templates | Leaks credentials; breaks on any other machine | Strip in step 5; convert literals to `{{parameters}}` |
| 4 | Over-generalizing one-off code into `scripts/` | A script with hidden session context silently does the wrong thing | When in doubt, demote to `templates/` with invocation principles |
| 5 | Referencing "the conversation" or "this session" inside the generated skill | The workflow must stand alone for an executor who never saw the session | Every fact the workflow needs must live in its own files |
| 6 | Delivering without the step-6 user review | Misread goals and missing steps ship unchallenged | 🔴 CHECKPOINT is mandatory — see step 6 |
| 7 | Padding the generated SKILL.md with generic advice ("write clean code", "test thoroughly") | Filler dilutes the fixed procedure and wastes the executor's context | Only include steps that actually happened or branches that actually occurred |

## Reference: what a goose recipe teaches us

Goose recipes package a repeatable task into `instructions` (the procedure), `parameters` (`{{var}}` inputs), `extensions` (required tools), and a `prompt` (the kickoff message). Map these onto skill format:

| goose recipe | generated skill |
|---|---|
| `title` / `description` | frontmatter `name` / `description` |
| `instructions` | SKILL.md body: the ordered workflow |
| `parameters` | the Parameters section + `{{var}}` markers in body and templates |
| `extensions` | a "Requires" note in the overview (tools/MCPs the workflow needs) |
| `prompt` | the trigger phrases embedded in `description` |

The difference: a recipe is executed by goose's runtime; a workflow skill is executed by a model reading the file. So the skill must carry the *why* and the branch logic inline — there is no runtime to fill the gaps.
