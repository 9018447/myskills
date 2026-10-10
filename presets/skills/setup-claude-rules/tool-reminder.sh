#!/bin/sh
# PreToolUse reminder hook. Injects a routing reminder before tool calls:
# Bash with find/grep/rg gets the jg -> zg/ast-grep/GitNexus routing reminder
# (plus the context-mode note every Bash call gets), Read gets the
# analyze-with-ctx_execute_file note, Write/Edit/NotebookEdit get the
# codemode-batching note. Installed per-repo by setup-claude-rules' install.sh,
# which symlinks this file into .claude/hooks/ and registers the PreToolUse
# entry in .claude/settings.json. Disable per-repo by removing that entry;
# there is no separate off-switch file.
node -e '
let s = "";
process.stdin.on("data", d => s += d).on("end", () => {
  let ev = {};
  try { ev = JSON.parse(s); } catch {}
  const tool = ev.tool_name || "";
  const cmd = String((ev.tool_input || {}).command || "");
  const tips = [];
  if (tool === "Bash") {
    if (/(^|[;&|(\s])(sudo\s+)?(find|grep|rg)\b/.test(cmd))
      tips.push("Shell find/grep/rg is the last resort: go to zg / GitNexus instead (see .claude/rules/code-search.md).");
    tips.push("Processing command output? ctx_batch_execute / ctx_execute keeps the raw bytes out of context; Bash is for observing short fixed output or mutating state.");
  }
  if (tool === "Read")
    tips.push("Reading to analyze (not to edit)? ctx_execute_file keeps the file out of context; Read only what you edit or need verbatim.");
  if (tool === "Write" || tool === "Edit" || tool === "NotebookEdit")
    tips.push("Chained or multi-file changes? Batch reads + edits in one mcp__codemode__execute script; direct Write/Edit for single-target writes only.");
  if (tips.length)
    console.log(JSON.stringify({ hookSpecificOutput: { hookEventName: "PreToolUse", additionalContext: tips.join(" ") } }));
});
'
