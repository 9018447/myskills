---
name: pycrs-cosmors
description: Help with pyCRS, COSMO-RS, COSMO-SAC, and PLAMS workflows using the bundled PyCRS documentation. Use this whenever the user wants to write, explain, adapt, debug, or translate pyCRS scripts; work with COSKF databases, CRSManager, PropPred, FastSigma, Molecule/Input/Output APIs; or solve tasks around activity coefficients, partition coefficients, solubility, cocrystals, ionic liquids, sigma profiles or moments, phase diagrams, pKa, or related COSMO-RS examples, even if they only mention PLAMS, ADFCRS, .coskf files, or SCM examples.
compatibility: Works best inside this PyCRS documentation repository where the referenced markdown source files are available.
---

# PyCRS / COSMO-RS Skill

Use this skill to turn the repository's pyCRS and PLAMS documentation into practical help: API explanations, runnable scripts, workflow selection, debugging guidance, or concise summaries.

## What this skill should do

1. Classify the request quickly.
2. Read only the relevant reference file(s).
3. Answer in the user's language, but keep code and API names exactly as documented.
4. Produce something directly useful: a runnable script, a corrected snippet, a workflow recommendation, or a distilled explanation.

## Request routing

Use this routing table before answering:

| Request type | Read first | Then use |
| --- | --- | --- |
| Environment setup, database path, common script skeletons | `references/overview.md` | `references/source-map.md` if the user wants the original doc |
| Module/API questions about `Database`, `Input`, `Molecule`, `Output`, `PropPred`, `FastSigma`, `CRSManager` | `references/api-modules.md` | original markdown named in `references/source-map.md` for exact signatures/examples |
| "Which example should I use?" or "Give me a workflow for X" | `references/workflows.md` | `references/source-map.md` |
| Need exact source provenance or coverage audit | `references/source-map.md` | original markdown files |

## Core behavior

### 1. Map the user to a pyCRS task

Place the request into one of these buckets:

- **API explanation**: explain one module/class/function and its typical use.
- **Script authoring**: write a complete example from scratch.
- **Script adaptation**: modify an existing example to new compounds, conditions, or outputs.
- **Debugging**: inspect likely issues in imports, database paths, COSKF inputs, settings, mixture definitions, or result extraction.
- **Workflow discovery**: point the user to the best matching example(s) and summarize the steps.
- **Documentation compression**: turn long docs into a checklist, table, or minimal example.

### 2. Reuse repository conventions

Follow the documented patterns unless the user asks otherwise:

- Assume pyCRS is used alongside SCM/AMS tooling and COSKF files.
- Keep `database_path` or database file locations explicit; use placeholders instead of inventing local paths.
- Call out required downloaded COSKF datasets when the source example depends on them.
- Preserve the user's intended method or domain: `COSMO-RS`, `COSMO-SAC`, `PropPred`, `FastSigma`, database-backed workflows, or direct PLAMS jobs.
- Prefer small runnable examples over long prose.

### 3. Fill in missing details carefully

Only ask for information that blocks a useful answer, such as:

- database location or whether the user has `ADFCRS-2018`
- required compounds / `.coskf` files
- target property or problem type
- temperature, pressure, composition grid, or screening criteria
- whether they want pyCRS database workflows or direct PLAMS scripting

If those details are missing but a template would still help, provide a template with clearly labeled placeholders.

### 4. Output rules

#### If writing code

Return a complete snippet that includes:

- imports
- one obvious place to set the database path
- molecule / mixture setup
- settings or problem definition
- execution step
- result extraction or plotting hook

Mention assumptions only when they materially affect correctness.

#### If explaining documentation

Compress the answer into this order:

1. what the module or workflow is for
2. the minimum objects/functions to touch
3. a short step sequence
4. one compact example or pseudo-example
5. key caveats

#### If debugging

State the likely failure point first, then show the corrected code or configuration. Focus on issues that are common in this repo's examples: wrong database path, missing COSKF files, wrong mixture/problem setup, or misunderstanding of result containers.

## Coverage expectations

This skill should cover all major content families in the repo:

- database creation and querying
- conformer workflows
- `CRSManager` single-job and iteration workflows
- `PropPred` and temperature-dependent properties
- `FastSigma`, sigma profiles, and sigma moments
- activity coefficients, partition coefficients, and solubility
- cocrystal, ionic-liquid, eutectic, binodal/spinodal, and multispecies examples
- automated pKa workflows
- direct COSMO-RS scripting with PLAMS

## When to consult original docs

If the user needs exact API signatures, long code examples, or niche workflows, open the original markdown files listed in `references/source-map.md`. Do not guess undocumented parameter names.

## Recommended response patterns

**Example: user asks for a new script**
- pick the closest documented workflow
- adapt compound names, conditions, and outputs
- preserve the structure of the documented example
- explicitly mark any placeholders the user must fill in

**Example: user asks "which file covers this?"**
- answer with the best-match file(s)
- say why each file is relevant
- optionally add a one-line "start here first" recommendation

**Example: user pastes code that fails**
- infer which documented workflow it resembles
- compare expected objects/settings with the docs
- show the smallest fix that restores the documented pattern

## Reference files in this skill

- `references/overview.md` - environment assumptions, shared patterns, and a starter script shape
- `references/api-modules.md` - core module summaries and when to use them
- `references/workflows.md` - high-level map of all example workflows in the repo
- `references/source-map.md` - direct mapping from source markdown files to topics
