# Extensions Guide

Quick reference for developing pi extensions.

## Extension Boilerplate

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // React to events
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });

  // Register a custom tool
  pi.registerTool({
    name: "my_tool",
    label: "My Tool",
    description: "Does something useful",
    // ...
  });

  // Register a command
  pi.registerCommand("mycommand", {
    description: "My custom command",
    handler: async (ctx) => { /* ... */ }
  });
}
```

## Key API Quick Reference

| What | How |
|------|-----|
| React to events | `pi.on(eventName, handler)` |
| Register tool | `pi.registerTool(definition)` |
| Register command | `pi.registerCommand(name, options)` |
| Notify user | `ctx.ui.notify(msg, "info"\|"warning"\|"error")` |
| Confirm dialog | `ctx.ui.confirm(title, message)` |
| Select dialog | `ctx.ui.select(title, options)` |
| Custom overlay | `ctx.ui.custom(component)` |
| Session state | `pi.appendEntry(type, data)` |
| Execute command | `pi.exec(command, args, options)` |
| Get system prompt | `ctx.getSystemPrompt()` |
| Set model | `pi.setModel(model)` |

## Common Events

- `session_start`, `session_end`
- `tool_call`, `tool_result`, `tool_error`
- `before_send`, `after_send`
- `user_input`, `bash_spawn`, `bash_output`
- `compact`, `model_change`

## File Locations

- Global: `~/.pi/agent/extensions/*.ts`
- Project: `.pi/extensions/*.ts`
- Test: `pi -e ./path.ts`, then `/reload`

## Full Documentation & Examples

- **Complete API docs**: `references/docs/extensions.md`
- **Working examples**: `references/examples/extensions/`
- **TUI components**: `references/docs/tui.md`
