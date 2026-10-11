# Agent Compatibility

Read this reference when porting a skill or adding support for a new agent runtime.

## Separate the layers

Model a skill as three layers:

1. **Portable semantics** — triggers, workflow, domain rules, resources, and safety constraints in `SKILL.md`.
2. **Capability bindings** — how the target runtime exposes shell, browser, MCP, APIs, files, or sub-agents.
3. **Presentation and discovery** — UI labels, icons, registries, installation paths, and invocation syntax.

Keep layer 1 independent. Implement layers 2 and 3 only for known targets.

## Inspect before adapting

Prefer evidence in this order: repository agent instructions, official runtime documentation, working installed skills, then local validators and schemas. Do not infer a universal rule from a single vendor example.

## Compatibility matrix

| Dimension | Portable default | Adapter question |
|---|---|---|
| Entry file | `SKILL.md` | Does the runtime require another filename? |
| Frontmatter | `name`, `description` | Which additional keys are supported or required? |
| Resources | relative paths | Are folders named or loaded differently? |
| Tools | describe the capability generically | How are tools declared and invoked? |
| Discovery | metadata description | Is a registry, manifest, or UI file required? |
| Invocation | natural-language trigger | Is explicit `$name`, slash-command, or another syntax used? |
| Installation | repository-defined | Where and how does the runtime distribute skills? |

## Adapter rules

- Place target-specific metadata under a clearly named directory when prescribed.
- Keep adapter generators separate from portable initialization.
- Never require an optional adapter to understand the core workflow.
- Avoid machine-specific absolute paths and credentials.
- If targets conflict, preserve one portable core and create separate adapters.
- Validate each adapter with its target runtime.

## Porting checklist

- Replace vendor identity with “agent” or “runtime” where semantics are unchanged.
- Replace fixed tool commands with capability requirements plus optional adapter examples.
- Remove product-only metadata from portable frontmatter.
- Check every relative link after moving files.
- Exercise scripts outside the source runtime when possible.
- Document intentional limitations and their evidence.
