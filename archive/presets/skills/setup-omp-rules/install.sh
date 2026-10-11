#!/usr/bin/env bash
# Deterministically install the omp ruleset into the target repo. Script-driven, idempotent, missing tools do not block.
# Usage: install.sh [target repo root, defaults to the current directory]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(pwd)}"
ROOT="$(cd "$ROOT" && pwd)"
CTX_DIR="$ROOT/.omp/context"
RULES_DIR="$ROOT/.omp/rules"

# 1. Tool check (check-tools.sh always exits 0; missing tools are reported, not fatal)
TOOLS="$(bash "$SCRIPT_DIR/check-tools.sh" 2>&1 || true)"

# 2. Write the four context files (as symlinks to the skill's source files) + the TTSR nudge rule
mkdir -p "$CTX_DIR" "$RULES_DIR"
ln -sfn "$SCRIPT_DIR/ADD_RULES.md"        "$CTX_DIR/code-search.md"
ln -sfn "$SCRIPT_DIR/CODING_RULES.md"     "$CTX_DIR/coding-labor.md"
ln -sfn "$SCRIPT_DIR/VERIFY_RULES.md"     "$CTX_DIR/verification.md"
ln -sfn "$SCRIPT_DIR/PRINCIPLES_RULES.md" "$CTX_DIR/work-principles.md"
ln -sfn "$SCRIPT_DIR/rules/no-shell-search.md" "$RULES_DIR/no-shell-search.md"

# 3. Pick the summary target: exactly one, never both AGENTS.md and .omp/AGENTS.md.
#    .omp/AGENTS.md (native) shadows a same-level AGENTS.md (agents-md), and the
#    claude provider (.claude/CLAUDE.md) outranks standalone AGENTS.md — so with
#    only .claude/CLAUDE.md present, the block must go native to stay visible.
#    A root CLAUDE.md is not recognized by omp and is left untouched.
summary_action="updated summary"
claude_note=""
if [[ -f "$ROOT/.omp/AGENTS.md" ]]; then
  SUMMARY="$ROOT/.omp/AGENTS.md"
  CTX="context"
elif [[ -f "$ROOT/AGENTS.md" ]]; then
  SUMMARY="$ROOT/AGENTS.md"
  CTX=".omp/context"
elif [[ -f "$ROOT/.claude/CLAUDE.md" ]]; then
  SUMMARY="$ROOT/.omp/AGENTS.md"
  CTX="context"
  summary_action="created summary file"
else
  SUMMARY="$ROOT/AGENTS.md"
  CTX=".omp/context"
  summary_action="created summary file"
fi
if [[ -f "$ROOT/CLAUDE.md" ]]; then
  claude_note="note: root CLAUDE.md is not recognized by omp and was left untouched"
fi

# 4. Idempotent append: truncate the old block starting at the first '## Tool Routing', then append the template.
#    Only the tail block is touched; user sections above it are preserved.
#    {{CTX}} resolves to the context path relative to the summary file (never absolute).
tmp="$(mktemp)"
# Truncate when the file has an old block; empty output when the file does not exist (first AGENTS.md creation)
if [[ -f "$SUMMARY" ]]; then
  awk '!/^## Tool Routing/ { print } /^## Tool Routing/ { exit }' "$SUMMARY" > "$tmp"
else
  : > "$tmp"
fi
mv "$tmp" "$SUMMARY"
sed "s|{{CTX}}|$CTX|g" "$SCRIPT_DIR/APPEND_AGENTS.md" >> "$SUMMARY"

# 5. 结果摘要
echo "$TOOLS"
echo "context -> $CTX_DIR/code-search.md, $CTX_DIR/coding-labor.md, $CTX_DIR/verification.md, $CTX_DIR/work-principles.md"
echo "summary: $SUMMARY ($summary_action)"
echo "ttsr:    $RULES_DIR/no-shell-search.md"
[[ -n "$claude_note" ]] && echo "$claude_note"
echo "done:   code-search.md, coding-labor.md, verification.md, work-principles.md written; summary block in place; ttsr rule installed; all writes complete."
echo "verify: omp /extensions 查 Context Files/Rules, 改后 /new 或重启"
