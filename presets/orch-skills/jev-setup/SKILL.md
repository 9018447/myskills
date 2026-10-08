---
name: jev-setup
description: Set up Jev for an agent, choose OpenRouter, official TypeSafe or SiliconFlow, or guide an explicitly approved current-agent/DeepSeek simulation when no Jev key is available. Checks presence without exposing keys or making paid calls.
---

# Set up Jev

Use the user's current host and existing account where possible. Setup is not a
model call, account creation, provider switch or permission to spend.

## Setup: choose the service or simulation

Check only the presence of `OPENROUTER_API_KEY`, `TYPESAFE_API_KEY` and
`SILICONFLOW_API_KEY`; never print credentials. Respect the user's already chosen mode. For a new setup,
prefer the user's existing OpenRouter account; otherwise offer official TypeSafe.
If OpenRouter is missing, explain that direct TypeSafe is also real Jev. Do not
silently change destination, send data, create an account or switch the host model.

If no route has been chosen, explain the available routes and ask:

> **A — Real Jev:** use/get an OpenRouter key at https://openrouter.ai/settings/keys
> if you use OpenRouter; a TypeSafe key at
> https://console.typesafe.ai; or a SiliconFlow key at
> https://cloud.siliconflow.cn/account/ak if you use SiliconFlow.
> Configure it locally, not in chat.
> **B — Simulate:** use the current agent, or an explicitly selected available
> model such as DeepSeek, with the same context, questions and criteria.

**Wait for an explicit choice.** Do not ask again for every record in the same
approved task. API errors do not authorize switching providers or simulation.
Missing both keys is not a dead end: offer B. It requires no Jev key but the
chosen agent/model's ordinary access, usage costs and privacy terms still apply.
Do not assume DeepSeek is installed, free or locally hosted.

In B, return `mode: agent_simulation` for the current host or
`mode: model_simulation` for another explicitly approved model, plus its actual
model identity when available and `jev_called: false`. Each question has `value`,
`needs_review`, a brief evidence-based `reason`, `probability: null` and
`confidence: null`. Choice values must be supplied labels, Noul values booleans,
and Score values integer rubric indices. Use null/review for missing evidence.
Never present this as Jev, calibrated probability or equivalent speed/accuracy.
Skip Jev CLI/API steps in B; use the approved model's existing interface and do
not install a substitute or send data elsewhere without consent.

In A, select the CLI destination explicitly: `--provider openrouter`,
`--provider typesafe` or `--provider siliconflow`. The typesafe provider uses
`TYPESAFE_API_KEY` and maps the bundled OpenRouter model ID to `jev-1.13.0`.
The siliconflow provider uses `SILICONFLOW_API_KEY` and defaults to model
`Kev-4b` (same native Jev protocol endpoint, no adapter needed; see the
local CLI patch below). `--dry-run` only validates; it neither
classifies nor makes a network call. `jev-decide setup` reports presence only,
not key validity, credits or permission. Continue below for the selected route, or use the
[copyable simulation prompt](references/simulation.md).

## Complete the selected route

| Route | Local environment | CLI option | Endpoint / model |
|---|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | `--provider openrouter` | `https://openrouter.ai/api/alpha/decisions` / `typesafe/jev-1.13` |
| Official TypeSafe | `TYPESAFE_API_KEY` | `--provider typesafe` | `https://api.typesafe.ai/v1/systemone` / `jev-1.13.0` |
| SiliconFlow | `SILICONFLOW_API_KEY` | `--provider siliconflow` | `https://api.siliconflow.cn/v1/systemone` / `Kev-4b` (local CLI patch, see below) |
| Current agent / approved DeepSeek | Existing host or selected model access | No Jev CLI call | [Simulation prompt](references/simulation.md); never invent an API receipt |

If the user uses OpenRouter but has no key, point them to its key page. If they
do not use OpenRouter, offer the official console rather than requiring another
aggregator account. If neither route is possible or desired, offer simulation.
A missing key is never a reason to collect a secret in chat or browser history.
Let the user complete account/terms/payment steps; describe environment-variable
names and ask them to configure their host locally. Do not edit shell profiles.

Run `jev-decide setup` if already installed. Otherwise check environment presence
with the host tools; the skill does not require Python just to offer choices.
For A, ensure Python 3.10+ and the reviewed shared CLI are available, then:

```bash
jev-decide decide /path/to/request.json --provider typesafe --dry-run
# Only after approval for this input, destination and API usage:
jev-decide decide /path/to/request.json --provider typesafe > result.json
```

Replace `typesafe` with `openrouter` or `siliconflow` for that route. A dry run maps the known
bundled model ID for direct TypeSafe; use `--model` for a deliberate override.
Report which mode/provider was selected, which prerequisite is missing, what was
actually verified, and the next user action. Do not call an API merely to test a
key. A 401/402/403 is not permission to retry or silently switch services.

The agent does not inherit context into Jev calls. For later work, supply
sufficient context and batch independent questions in the same request; the
host schedules bounded concurrency, not dependent steps in parallel.

## SiliconFlow provider: local CLI patch

Upstream `jev-skill` (0.2.0) only ships openrouter/typesafe. SiliconFlow support
is a **local patch applied in place** to the installed CLI and is **lost on
`uv tool upgrade`/reinstall** — re-apply this patch after any upgrade.

**Locate the file** (single-module package; the uv build source dir is deleted
after install, so edit the installed copy):

```bash
# Resolve via the shim's own interpreter (jev-decide → uv tool venv python)
PY=$(head -1 "$(readlink -f "$(command -v jev-decide)")" | sed 's/^#!//')
FILE=$("$PY" -c 'import jev; print(jev.__file__)')
```

**Patch `jev.py`** — 7 touch points:

1. Docstring: add "or SiliconFlow".
2. Constants, after `TYPESAFE_MODEL`:
   ```python
   SILICONFLOW_URL = "https://api.siliconflow.cn/v1/systemone"
   SILICONFLOW_MODEL = "Kev-4b"
   ```
3. `http_json()` `endpoints` dict, add:
   `SILICONFLOW_URL: ("SILICONFLOW_API_KEY", "SiliconFlow"),`
   and extend the unsupported-URL error message.
4. `request_decisions()`: add `"siliconflow"` to the allowed provider set and the
   url mapping `{"openrouter": DECISIONS_URL, "typesafe": TYPESAFE_URL, "siliconflow": SILICONFLOW_URL}`.
5. `setup_report()` `available` list, add: `("siliconflow", "SILICONFLOW_API_KEY")`.
6. `parser()`: `--provider` choices add `"siliconflow"`.
7. `main()`: replace the default-model conditional with
   `{"openrouter": DEFAULT_MODEL, "typesafe": TYPESAFE_MODEL, "siliconflow": SILICONFLOW_MODEL}[args.provider]`.

**Re-verify (no network call):**

```bash
jev-decide setup                                  # available must include "siliconflow"
echo '{"state":"s","questions":{"q":{"type":"noul","instructions":"i"}}}' \
  | jev-decide decide - --provider siliconflow --dry-run   # model must be Kev-4b
jev-decide decide - --provider bogus              # must reject with the three valid choices
```

If the patched file is gone after an upgrade, the patch above reproduces it
exactly. Do not test the SiliconFlow key with a live call just to confirm.

[TypeSafe contract](https://docs.typesafe.ai/api) · [TypeSafe models](https://docs.typesafe.ai/models) ·
[OpenRouter contract](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-questions-and-answers-request).
