---
name: chrome-devtools
description: Expert-level browser automation, debugging, and performance analysis using Chrome DevTools MCP. Use for interacting with web pages, capturing screenshots, analyzing network traffic, and profiling performance.
license: MIT
---

# Chrome DevTools Skill

## When to Use

Use this skill when:

- **Browser Automation**: Navigating pages, clicking elements, filling forms, and handling dialogs
- **Visual Inspection**: Taking screenshots or text snapshots of web pages
- **Debugging**: Inspecting console messages, evaluating JavaScript, analyzing network requests
- **Performance Analysis**: Recording and analyzing performance traces, identifying bottlenecks and Core Web Vitals
- **Emulation**: Resizing viewport or emulating network/CPU conditions

## Key Tools

### Navigation & Pages
- `new_page`, `navigate_page`, `select_page`, `list_pages`, `close_page`
- `wait_for`: Wait for specific text to appear

### Interaction
- `click`, `fill`, `fill_form`, `hover`, `press_key`, `drag`
- `handle_dialog`, `upload_file`

### Debugging
- `take_snapshot`: Get accessibility tree with `uid` values (preferred for element identification)
- `take_screenshot`: Visual capture for verification
- `list_console_messages`, `evaluate_script`
- `list_network_requests`, `get_network_request`

### Performance & Emulation
- `resize_page`, `emulate` (CPU/Network throttling)
- `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight`

## Workflow Patterns

### Pattern A: Element Identification (Snapshot-First)

Always prefer `take_snapshot` over `take_screenshot` for finding elements. Snapshots provide `uid` values required by interaction tools.

1. `take_snapshot` to get current page structure
2. Find the `uid` of the target element
3. Use `click(uid=...)` or `fill(uid=..., value=...)`

### Pattern B: Error Troubleshooting

When a page fails, check both console and network:

1. `list_console_messages` for JavaScript errors
2. `list_network_requests` for failed (4xx/5xx) resources
3. `evaluate_script` to inspect DOM elements or global variables

### Pattern C: Performance Profiling

Identify why a page is slow:

1. `performance_start_trace(reload=true, autoStop=true)`
2. Wait for page load / trace completion
3. `performance_analyze_insight` to find LCP issues or layout shifts

## Best Practices

- **Context Awareness**: Run `list_pages` and `select_page` if unsure which tab is active
- **Snapshots**: Take new snapshots after navigation or DOM changes (uid values may change)
- **Timeouts**: Use reasonable timeouts for `wait_for` to avoid hanging
- **Screenshots**: Use sparingly for visual verification; rely on `take_snapshot` for logic
