---
name: pi-config
description: >
  Automate pi extension creation, custom provider registration, and model configuration.
  Use this skill whenever the user wants to create a pi extension, register a custom provider,
  configure custom models (Ollama, vLLM, OpenRouter, proxies, etc.), manage pi packages
  (install/remove), or troubleshoot pi configuration issues. Triggers on mentions of
  "pi extension", "pi 扩展", "custom provider", "models.json", "registerTool",
  "registerCommand", "registerProvider", "Ollama 配置", "pi install", "pi package",
  "settings.json", or any request to automate pi setup.
---

# Pi Configuration Assistant

This skill automates creating and managing pi extensions, custom providers, and model configurations. It generates correct files directly into the right paths, then guides the user through manual testing with a structured feedback loop.

## Decision Tree

When the user asks for pi configuration help, first determine which domain(s) they need:

| User says | Go to |
|-----------|-------|
| "create an extension", "write a tool", "add a command", "拦截工具", "自定义UI" | § Extensions |
| "add a provider", "registerProvider", "代理", "OAuth", "custom provider" | § Custom Providers |
| "add a model", "Ollama", "vLLM", "OpenRouter", "models.json", "本地模型" | § Custom Models |
| "install package", "pi install", "remove package" | § Package Management |
| "settings", "pi config", "怎么调试", "报错", "不生效" | § Settings & Debugging |
| Config wizard / interactive setup flow | Read `references/wizard-playbook.md` first |

If unsure, ask the user to clarify, then proceed.

---

## Extensions

### Step 1: Understand the extension type

Ask the user:
- **What should the extension do?** (custom tool, event handler, command, shortcut, UI component?)
- **Where should it apply?** (global `~/.pi/agent/extensions/` or project `.pi/extensions/`?)
- **Does it need npm dependencies?** If so, a package structure with `package.json` is required.

### Step 2: Choose the structure

**Single-file extension** (no dependencies):
```
~/.pi/agent/extensions/my-extension.ts
```

**Directory with dependencies**:
```
~/.pi/agent/extensions/my-extension/
├── index.ts
├── package.json
└── package-lock.json
```
After creating files, tell the user to run `npm install` in the directory, or run it yourself.

### Step 3: Write the code

All extensions follow this skeleton:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // Event handlers, tool registrations, commands, etc.
}
```

The factory can be `async` if initialization needs fetching or setup.

#### Common patterns

**Registering a custom tool:**
```typescript
import { Type } from "typebox";
import { StringEnum } from "@earendil-works/pi-ai";

pi.registerTool({
  name: "my_tool",
  label: "My Tool",
  description: "What this tool does (shown to LLM)",
  promptSnippet: "One-line summary for Available tools section",
  promptGuidelines: ["Optional: tool-specific guidelines bullet"],
  parameters: Type.Object({
    action: StringEnum(["list", "add"] as const),
    text: Type.Optional(Type.String()),
  }),
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    return {
      content: [{ type: "text", text: "Result sent to LLM" }],
      details: { /* for rendering & state persistence */ },
    };
  },
});
```

**Registering a command:**
```typescript
pi.registerCommand("my-cmd", {
  description: "Description shown in /help",
  handler: async (args, ctx) => {
    ctx.ui.notify(`Running: ${args}`, "info");
  },
});
```

**Event interception (tool_call):**
```typescript
pi.on("tool_call", async (event, ctx) => {
  if (event.toolName === "bash" && event.input.command?.includes("rm -rf")) {
    const ok = await ctx.ui.confirm("Dangerous!", "Allow rm -rf?");
    if (!ok) return { block: true, reason: "Blocked by user" };
  }
});
```

**Modifying system prompt:**
```typescript
pi.on("before_agent_start", async (event, ctx) => {
  return { systemPrompt: event.systemPrompt + "\n\nExtra instructions..." };
});
```

**Session state persistence:**
```typescript
pi.appendEntry("my-state", { count: 42 });

pi.on("session_start", async (_event, ctx) => {
  for (const entry of ctx.sessionManager.getEntries()) {
    if (entry.type === "custom" && entry.customType === "my-state") {
      // restore state
    }
  }
});
```

**File mutation queue** (for tools that write files alongside built-in edit/write):
```typescript
import { withFileMutationQueue } from "@earendil-works/pi-coding-agent";
async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
  const absolutePath = resolve(ctx.cwd, params.path);
  return withFileMutationQueue(absolutePath, async () => {
    // read → modify → write
  });
}
```

### Step 4: Save and test

1. Write the file(s) to the chosen path
2. If it has dependencies, run `npm install` in the extension directory
3. Tell the user to run `pi` and test with `/reload` if pi is already running
4. **Feedback**: ask the user to test and report any issues, errors in the pi console, or behavior mismatches

---

## TUI Development Rules

When writing extensions with `ctx.ui.custom()`, follow these rules to avoid crashes and usability issues. For full details with code examples, read `references/tui-rules.md`.

### Core Rules Summary

1. **Prefer standard dialogs** — Use `ctx.ui.select/input/confirm` for config wizards. They support copy/paste, IME, keyboard nav, and correct width calculation. Reserve `ctx.ui.custom()` for complex interactive UIs.

2. **Truncate every line** — In `render(width)`, every line must use `truncateToWidth(line, width)`. ANSI codes and Unicode borders cause width miscalculations. Prefer ASCII borders (`+ - |`).

3. **`ctx.ui.select()` only accepts `string[]`** — NOT `{value, label}[]`. Map objects to strings first, then reverse-lookup by index.

4. **`ctx.ui.custom()` blocks text selection** — Users can't copy URLs/keys from custom components. Use standard dialogs or show plain-text summaries.

5. **LSP/TypeScript** — Use `// @ts-ignore` (not `@ts-expect-error`) for Pi internal modules. Define local interfaces instead of `as any`.

6. **Naming collision** — When a `class` and a `type/interface` share the same name, the class declaration hides the type. Rename one (e.g., prefix interface with `I` or suffix with `Config`).

---

## Custom Providers

Providers can be added via **extension code** (`pi.registerProvider()`) or **static JSON** (`models.json`). For full configuration examples, read `references/provider-config.md`.

| Scenario | Method |
|----------|--------|
| Proxy forwarding (same models, different endpoint) | `models.json` (simpler) |
| New provider with custom models | `models.json` (no code needed) |
| OAuth/SSO authentication | Extension `registerProvider()` (required) |
| Custom streaming API | Extension `registerProvider()` (required) |
| Dynamic model discovery from remote endpoint | Extension `registerProvider()` with async factory (required) |

### Option A: Static JSON (~/.pi/agent/models.json)

For new providers with models:
```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        { "id": "qwen2.5-coder:7b" },
        {
          "id": "deepseek-r1:8b",
          "name": "DeepSeek R1 8B (Local)",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

Key fields per model: `id` (required), `name`, `reasoning`, `thinkingLevelMap`, `input`, `contextWindow`, `maxTokens`, `cost`, `compat`.

Common `compat` flags for OpenAI-compatible servers: `supportsDeveloperRole: false`, `supportsReasoningEffort: false`, `maxTokensField: "max_tokens"`, `thinkingFormat: "qwen-chat-template"`, `thinkingFormat: "deepseek"`.

For the full compat flag table, API types, model field reference, and more examples — read `references/quick-ref.md`.

### Option B: Extension registerProvider()

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default async function (pi: ExtensionAPI) {
  pi.registerProvider("my-provider", {
    name: "My Provider",
    baseUrl: "https://api.example.com/v1",
    apiKey: "MY_PROVIDER_API_KEY",
    api: "openai-completions",
    models: [
      {
        id: "my-model",
        name: "My Model",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 4096,
      },
    ],
  });
}
```

For OAuth providers, the `oauth` block is required — place it in an extension, not in `models.json`.

### Save and validate

1. For `models.json`: write to `~/.pi/agent/models.json`. Merge with existing content — don't overwrite other providers.
2. For extensions: write to `~/.pi/agent/extensions/`.
3. Reload is not needed — `models.json` auto-reloads when opening `/model`; extensions auto-reload with `/reload`.
4. **Feedback**: ask the user to verify with `/model` command or `pi --list-models`.

---

## Custom Models

Models are configured inside providers (see § Custom Providers). For quick reference, here's a minimal Ollama example:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [{ "id": "llama3.1:8b" }]
    }
  }
}
```

For thinking level mapping, modelOverrides, per-model baseUrl, and more — read `references/provider-config.md`.

---

## Package Management

### Installing packages

```bash
pi install npm:@scope/pkg@1.0.0      # npm package
pi install git:github.com/user/repo   # git repository
pi install git:git@github.com:user/repo@v1  # SSH git with version
pi install /absolute/path/to/package  # local path
pi install ./relative/path             # relative path
pi install -l npm:@scope/pkg          # project-local install (not global)
```

### Temporary testing (no install)

```bash
pi -e npm:@scope/pkg
pi -e git:github.com/user/repo
pi -e ./my-extension.ts
```

### Managing packages

```bash
pi list                     # show installed
pi remove npm:@foo/bar      # uninstall
pi update                   # update pi + all non-pinned packages
pi update --extensions      # update packages only
pi update npm:@foo/bar      # update one package
```

### Package version pinning

- Versioned specs (`@1.0.0`) and git refs (`@v1`) are **pinned** — `pi update` skips them
- Unpinned packages are updated when running `pi update`

---

## Settings & Debugging

### Settings locations

| File | Scope |
|------|-------|
| `~/.pi/agent/settings.json` | Global (all projects) |
| `.pi/settings.json` | Project-local |

### Common issues and fixes

**Extension not loading:**
1. Check the file is in `~/.pi/agent/extensions/` or `.pi/extensions/`
2. Run `/reload` in pi or restart
3. Check pi console for TypeScript errors
4. Verify the export is a default function: `export default function (pi: ExtensionAPI) {}`

**Provider/model not showing in /model:**
1. Check `~/.pi/agent/models.json` is valid JSON
2. Open `/model` panel — `models.json` auto-reloads on open
3. Required fields: `baseUrl`, `api`, `apiKey`, `models[{id}]`
4. For shell command `apiKey` (`"!command"`), the command must execute successfully at runtime

**Extension dependencies not found:**
1. Ensure `package.json` exists in the extension directory
2. Run `npm install` in that directory
3. Dependencies must be in `dependencies`, not `devDependencies`

**Quirks with Ollama/vLLM:**
- Always set `compat.supportsDeveloperRole: false` and `compat.supportsReasoningEffort: false`
- Ollama ignores `apiKey`, use any string value (e.g., `"ollama"`)
- For Qwen models on Ollama, add `compat.thinkingFormat: "qwen-chat-template"`

---

## User Feedback Loop

After generating any configuration or extension:

1. **Report what was created**: file path, what it does, key decisions made
2. **Provide testing instructions**: 
   - For extensions: "Run `pi`, then test with `/reload`. Look for errors in the pi console."
   - For models/providers: "Open `/model` in pi and verify the provider appears. Try selecting and using the model."
   - For packages: "Run `pi list` to confirm the package is installed."
3. **Ask for feedback**: "Please test this and let me know: (1) any errors in the console, (2) behavior that doesn't match expectations, (3) missing features you'd like to add."
4. **Iterate**: Based on user feedback, fix issues and regenerate.

---

## Reference Files

For detailed documentation, read these files as needed:

- **`references/quick-ref.md`** — Compat flags, API types, extension locations, UI methods, event names, keybinding IDs, import packages
- **`references/wizard-playbook.md`** — Config wizard development playbook: standard workflow, anti-patterns, LSP fixes, release checklist, code skeleton
- **`references/tui-rules.md`** — Full TUI development rules with code examples
- **`references/provider-config.md`** — Full provider configuration examples (thinking level mapping, modelOverrides, per-model baseUrl, Google AI Studio, OpenRouter)
- **`references/working-notes.md`** — Iteration lessons: errors encountered, root causes, corrections applied

Pi documentation (read for deep API details):
- Extensions API: `~/.nvm/versions/node/v22.17.0/lib/node_modules/@earendil-works/pi-coding-agent/docs/extensions.md`
- Custom Providers: `~/.nvm/versions/node/v22.17.0/lib/node_modules/@earendil-works/pi-coding-agent/docs/custom-provider.md`
- Custom Models: `~/.nvm/versions/node/v22.17.0/lib/node_modules/@earendil-works/pi-coding-agent/docs/models.md`
- TUI Components: `~/.nvm/versions/node/v22.17.0/lib/node_modules/@earendil-works/pi-coding-agent/docs/tui.md`
- Pi Packages: `~/.nvm/versions/node/v22.17.0/lib/node_modules/@earendil-works/pi-coding-agent/docs/packages.md`
