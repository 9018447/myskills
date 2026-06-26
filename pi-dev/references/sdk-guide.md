# SDK Guide

Quick reference for using pi programmatically.

## Quick Start

```typescript
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const session = await createAgentSession({
  model: { provider: "anthropic", model: "claude-sonnet-4-20250514" },
  systemPrompt: "You are a helpful assistant.",
  tools: [/* custom tools */]
});

for await (const event of session) {
  console.log(event);
}
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| `createAgentSession()` | Start an agent session |
| `AgentSession` | Async iterable of events |
| `AgentSessionRuntime` | Session + methods for control |
| `Agent` | Agent configuration |
| `AgentState` | Current agent state |

## Run Modes

| Mode | Use Case |
|------|----------|
| `InteractiveMode` | Full TUI |
| `runPrintMode` | CLI output |
| `runRpcMode` | JSON-RPC |

## Key Options

```typescript
createAgentSession({
  directories: { skills: "...", extensions: "..." },
  model: { provider: "...", model: "...", apiKey: "..." },
  systemPrompt: "...",
  tools: [...],
  extensions: [...],
  skills: [...],
  contextFiles: [...],
  settings: { ... }
});
```

## Full Documentation & Examples

- **Complete SDK docs**: `references/docs/sdk.md`
- **SDK examples**: `references/examples/sdk/01-minimal.ts` through `12-full-control.ts`
- **RPC example**: `references/examples/rpc-extension-ui.ts`
