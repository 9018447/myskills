#!/usr/bin/env bash
# Deterministically install the agent ruleset into the target repo. Script-driven, idempotent, missing tools do not block.
# Usage: install.sh [target repo root, defaults to the current directory]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(pwd)}"
ROOT="$(cd "$ROOT" && pwd)"
RULES_DIR="$ROOT/.claude/rules"

# 1. Tool check (check-tools.sh always exits 0; missing tools are reported, not fatal)
TOOLS="$(bash "$SCRIPT_DIR/check-tools.sh" 2>&1 || true)"

# 2. Write the four rule files (as symlinks to the skill's source files)
mkdir -p "$RULES_DIR"
ln -sfn "$SCRIPT_DIR/ADD_RULES.md"  "$RULES_DIR/code-search.md"
ln -sfn "$SCRIPT_DIR/CODING_RULES.md" "$RULES_DIR/coding-principle.md"
ln -sfn "$SCRIPT_DIR/VERIFY_RULES.md" "$RULES_DIR/verification.md"
ln -sfn "$SCRIPT_DIR/PRINCIPLES_RULES.md" "$RULES_DIR/work-principles.md"

# 2b. Install hooks (files + settings registration): SessionStart routing and PreToolUse reminders
HOOKS_DIR="$ROOT/.claude/hooks"
mkdir -p "$HOOKS_DIR"
ln -sfn "$SCRIPT_DIR/session-start.sh" "$HOOKS_DIR/session-start.sh"
ln -sfn "$SCRIPT_DIR/session-start-context.md" "$HOOKS_DIR/session-start-context.md"
ln -sfn "$SCRIPT_DIR/tool-reminder.sh" "$HOOKS_DIR/tool-reminder.sh"
node - "$ROOT/.claude/settings.json" <<'EOF'
const fs = require('fs');
const file = process.argv[2];
let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {}
const hooks = (cfg.hooks ??= {});
const add = (event, matcher, cmdPart) => {
  const entries = hooks[event] ??= [];
  if (!entries.some(e => (e.hooks ?? []).some(h => String(h.command).includes(cmdPart)))) {
    entries.push({ matcher, hooks: [{ type: 'command', command: cmdPart }] });
  }
};
add('SessionStart', 'startup|resume|clear|compact', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/session-start.sh');
add('PreToolUse', 'Bash|Read|Write|Edit|NotebookEdit', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/tool-reminder.sh');
fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + '\n');
EOF

# 3. Pick the summary target: CLAUDE.md if it exists; otherwise AGENTS.md; create AGENTS.md if neither exists
summary_action="updated summary"
if [[ -f "$ROOT/CLAUDE.md" ]]; then
  SUMMARY="$ROOT/CLAUDE.md"
elif [[ -f "$ROOT/AGENTS.md" ]]; then
  SUMMARY="$ROOT/AGENTS.md"
else
  SUMMARY="$ROOT/AGENTS.md"
  summary_action="created summary file"
fi

# 4. Idempotent append: truncate the old block starting at the first '## Tool Routing', then append the template.
#    Only the tail block is touched; user sections above it are preserved.
tmp="$(mktemp)"
# Truncate when the file has an old block; empty output when the file does not exist (first AGENTS.md creation)
if [[ -f "$SUMMARY" ]]; then
  awk '!/^## Tool Routing/ { print } /^## Tool Routing/ { exit }' "$SUMMARY" > "$tmp"
fi
mv "$tmp" "$SUMMARY"
cat "$SCRIPT_DIR/APPEND_CLAUDE.md" >> "$SUMMARY"

# 5. 结果摘要
echo "$TOOLS"
echo "rules -> $RULES_DIR/code-search.md, $RULES_DIR/coding-principle.md, $RULES_DIR/verification.md, $RULES_DIR/work-principles.md"
echo "summary: $SUMMARY ($summary_action)"
echo "hook:    $HOOKS_DIR/session-start.sh + tool-reminder.sh -> $SCRIPT_DIR; SessionStart + PreToolUse registered in $ROOT/.claude/settings.json"
echo "done:   code-search.md, coding-principle.md, verification.md, work-principles.md written; summary block in place; routing hook installed; all writes complete."
