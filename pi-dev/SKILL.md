---
name: pi-dev
description: |
  Develop and configure pi-coding-agent (the pi terminal coding harness).
  Use this skill whenever the user wants to:
  - Create, modify, or debug pi extensions (TypeScript .ts/.js files)
  - Create or edit pi themes (.json theme files)
  - Create or edit pi skills (SKILL.md files)
  - Create or edit pi prompt templates (.md files with frontmatter)
  - Create or configure pi packages (npm/git packages with pi manifest)
  - Configure pi settings, keybindings, or models
  - Build custom tools, commands, UI components, or event handlers for pi
  - Use the pi SDK programmatically
  - Ask anything about pi's ExtensionAPI, TUI components, events, or lifecycle
  This includes requests like "write a pi extension that...", "how do I add a custom command to pi?", "help me configure pi settings", "create a pi theme", "build a pi skill", or any question about pi customization and extensibility.
compatibility: |
  Requires access to pi-coding-agent docs and examples at
  /home/smh/node_modules/@earendil-works/pi-coding-agent/
---

# Pi Development Skill

This skill helps you build and configure pi-coding-agent extensions, themes, skills, prompt templates, packages, and SDK integrations.

## How to use this skill

1. **Identify the user's intent** — what aspect of pi are they working on?
2. **Read the relevant sub-guide** from `references/` before writing any code.
3. **Reference working examples** from the pi examples directory when appropriate.
4. **Follow pi conventions** — paths, file formats, and APIs have specific requirements.

## Intent Routing

Match the user's request to the correct sub-guide:

| User wants to... | Read this guide |
|---|---|
| Write a pi extension (custom tools, commands, events, UI) | `references/extensions-guide.md` |
| Configure pi (settings, keybindings, models, providers) | `references/settings-guide.md` |
| Create a pi theme | `references/themes-guide.md` |
| Create a pi skill | `references/skills-guide.md` |
| Create a pi prompt template | `references/prompts-guide.md` |
| Create or publish a pi package | `references/packages-guide.md` |
| Build custom TUI components (overlays, widgets, editors) | `references/tui-guide.md` |
| Use pi programmatically via SDK or RPC | `references/sdk-guide.md` |

**Important:** Always read the relevant sub-guide before generating code. Each guide contains the exact APIs, schemas, and patterns you need.

## Common patterns across all pi development

### File locations

Pi discovers resources from these locations (in order of priority):

1. `.pi/` in the current project directory
2. Parent directories (walking up from cwd)
3. `~/.pi/agent/` (global user config)
4. Installed pi packages

| Resource | Project path | Global path |
|---|---|---|
| Settings | `.pi/settings.json` | `~/.pi/agent/settings.json` |
| Keybindings | `.pi/keybindings.json` | `~/.pi/agent/keybindings.json` |
| Models | `.pi/models.json` | `~/.pi/agent/models.json` |
| Extensions | `.pi/extensions/*.ts` | `~/.pi/agent/extensions/*.ts` |
| Skills | `.pi/skills/` or `.agents/skills/` | `~/.pi/agent/skills/` or `~/.agents/skills/` |
| Prompts | `.pi/prompts/*.md` | `~/.pi/agent/prompts/*.md` |
| Themes | `.pi/themes/*.json` | `~/.pi/agent/themes/*.json` |
| System prompt | `.pi/SYSTEM.md` | `~/.pi/agent/SYSTEM.md` |
| Context files | `AGENTS.md`, `CLAUDE.md` (any parent dir) | `~/.pi/agent/AGENTS.md` |

### Extension boilerplate

Every pi extension is a TypeScript file with a default export:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // Register tools, commands, events, UI here
}
```

The default export can also be `async` for initialization that requires await.

### Testing extensions

Load an extension during development with:

```bash
pi -e ./path/to/my-extension.ts
```

After editing, run `/reload` in pi to reload extensions without restarting the session.

### Key npm packages

| Package | Purpose |
|---|---|
| `@earendil-works/pi-coding-agent` | ExtensionAPI, tool helpers, utils |
| `@earendil-works/pi-ai` | LLM types (Message, Model, Tool, etc.) |
| `@earendil-works/pi-tui` | TUI components (Text, Box, Container, etc.) |
| `@earendil-works/pi-agent-core` | Agent framework types |

### Pi examples directory

Reference working examples at:
```
/home/smh/node_modules/@earendil-works/pi-coding-agent/examples/
├── extensions/     # 80+ extension examples
│   ├── hello.ts              # Minimal custom tool
│   ├── custom-provider-*/    # Custom providers
│   ├── subagent/             # Subagent tool
│   ├── sandbox/              # Sandbox execution
│   ├── doom-overlay/         # Full game overlay
│   ├── plan-mode/            # Plan mode
│   └── ...
├── sdk/            # SDK usage examples (01-minimal.ts to 12-full-control.ts)
└── README.md       # Examples overview
```

## When the user's request spans multiple areas

Some requests touch multiple sub-guides. Read all relevant guides. For example:
- "A pi package with an extension and a skill" → read `packages-guide.md` + `extensions-guide.md` + `skills-guide.md`
- "An extension with a custom TUI overlay" → read `extensions-guide.md` + `tui-guide.md`
- "A custom tool with settings configuration" → read `extensions-guide.md` + `settings-guide.md`

## Anti-patterns to avoid

- **Don't** invent API methods — pi's ExtensionAPI is well-defined. Check the guide or examples.
- **Don't** put extensions in wrong locations — they must be in `.ts` or `.js` files in `extensions/` directories.
- **Don't** forget `export default function (pi: ExtensionAPI)` — this is the required entry point.
- **Don't** use `console.log` in extensions meant for interactive mode — use `ctx.ui.notify()` instead.
- **Don't** assume pi has subagents or MCP built-in — these are extension-level features if needed.

## Output conventions

When generating pi code, always:
1. Include clear JSDoc comments explaining what the extension/tool/command does
2. Show how to load/test it (`pi -e ./path` or install as package)
3. Mention any npm dependencies needed
4. Reference the relevant pi docs for deeper reading
