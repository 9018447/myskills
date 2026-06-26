# TUI Guide

Quick reference for building custom UI in pi extensions.

## Using Components

```typescript
import { Text, Box, Container, Spacer, Markdown } from "@earendil-works/pi-tui";

// In an overlay
ctx.ui.custom({
  render: () => Container({
    children: [
      Text({ content: "Hello" }),
      Box({ border: true, children: [Markdown({ content: "# Title" })] }),
      Spacer()
    ]
  })
});
```

## Built-in Components

| Component | Purpose |
|-----------|---------|
| `Text` | Plain text display |
| `Box` | Bordered container |
| `Container` | Layout container (vertical/horizontal) |
| `Spacer` | Flexible empty space |
| `Markdown` | Rendered markdown |
| `Image` | Image display (requires image data) |

## Overlays

```typescript
ctx.ui.custom({
  render: () => /* component tree */,
  onKey: (key) => {
    if (key.name === "q") return { close: true };
    return { handled: true };
  }
});
```

## Key Rules

- All components are pure functions returning component trees
- Use `invalidate()` to trigger re-render
- Handle `onKey` for keyboard input
- IME support via `focusable` interface

## Common Patterns

1. **Selection dialog**: Use `ctx.ui.select()`
2. **Async with cancel**: Render loader + cancel button
3. **Settings toggles**: Checkbox list with state
4. **Status indicator**: Persistent widget above editor
5. **Custom footer**: Override footer via extension
6. **Custom editor**: Full editor replacement

## Full Documentation & Examples

- **Complete TUI docs**: `references/docs/tui.md`
- **TUI examples**: `references/examples/extensions/doom-overlay/`, `references/examples/extensions/snake.ts`
