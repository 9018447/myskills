---
name: {{workflow-name}}
description: {{What this workflow accomplishes, then concrete trigger contexts: the situations and user phrases that should invoke it, including phrasings that don't name the workflow explicitly. Be specific and slightly pushy.}}
---

# {{Workflow Title}}

## Overview

**Goal:** {{one sentence}}

**Run this when:** {{situations}}

**Requires:** {{tools / MCP servers / access this workflow depends on}}

**Inputs → Outputs:** {{what goes in, what comes out}}

## Parameters

| Parameter | Meaning | Default |
|---|---|---|
| `{{param_name}}` | {{what it controls and where it is consumed}} | {{default or "required"}} |

## Workflow

1. **{{Step name}}** — {{what to do, imperatively}}.
   Use `scripts/{{script}}` / adapt `templates/{{template}}`.
   {{Why this step exists, if not obvious.}}
   Verify: {{how to know the step succeeded before proceeding}}.

2. **{{Step name}}** — {{...}}.
   Decision point: if {{condition}}, {{branch A}}; otherwise {{branch B}}.

3. **{{Step name}}** — {{...}}.

## Pitfalls

- {{Do this, not that}} — {{reason, usually a failure seen in the original session}}.
- {{...}}

## Files

- `scripts/` — {{one line per script: purpose and usage}}
- `templates/` — {{one line per template: purpose, placeholders, invocation principles}}
- `references/` — {{optional}}
