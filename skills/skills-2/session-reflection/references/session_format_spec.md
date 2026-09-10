# Pi Session Format Specification (v3)

Reference for understanding pi session HTML exports.

## HTML Structure

HTML exports contain session data in a `<script id="session-data">` tag with base64-encoded JSON.

## Entry Types

| Type | Description | Key Fields |
|------|-------------|------------|
| `session` | Header (first line) | version, id, timestamp, cwd |
| `message` | Conversation message | message.role, message.content |
| `model_change` | User switched model | provider, modelId |
| `thinking_level_change` | User changed thinking level | thinkingLevel |
| `compaction` | Context was compacted | summary, tokensBefore, firstKeptEntryId |
| `branch_summary` | Alternative approach abandoned | summary, fromId |
| `custom` | Extension state (not in LLM context) | customType, data |
| `custom_message` | Extension message (in LLM context) | customType, content, display |
| `label` | User-defined bookmark | targetId, label |
| `session_info` | Session display name | name |

## Message Roles

| Role | Description | Key Fields |
|------|-------------|------------|
| `user` | User message | content (string or text/image blocks) |
| `assistant` | Model response | content, model, provider, api, usage, stopReason, errorMessage |
| `toolResult` | Tool output | toolCallId, toolName, content, isError, details |
| `bashExecution` | Bash command execution | command, output, exitCode, cancelled, truncated, fullOutputPath |
| `custom` | Extension message | customType, content |
| `branchSummary` | Branch context summary | summary, fromId |
| `compactionSummary` | Compaction context | summary |

## Content Block Types

| Type | Fields |
|------|--------|
| `text` | text |
| `image` | data (base64), mimeType |
| `thinking` | thinking |
| `toolCall` | id, name, arguments |

## Tree Structure

Entries form a tree via `id`/`parentId`:
- First entry has `parentId: null`
- Each subsequent entry points to its parent
- Branching creates multiple children from one parent
- The "leaf" is the current position

```
[user] → [assistant] → [user] → [assistant] ─┬─ [user] ← current
                                               └─ [branch_summary] → [user] ← alt branch
```

## Key Metrics in Summary

| Metric | Meaning |
|--------|--------|
| `session_version` | Format version (1/2/3) |
| `has_branching` | Session contains alternative branches |
| `has_compaction` | Context was compacted |
| `stop_reasons` | Distribution: stop, toolUse, length, error, aborted |
| `models_used` | Which models were used |
| `providers_used` | Which API providers were used |
| `compaction_tokens_saved` | Tokens freed by compaction |
| `branch_point_count` | Number of branch points |
| `edit_operations_count` | Number of edit tool calls |
| `total_edit_diff_chars` | Total old+new text in edits |
| `total_thinking_chars` | Total thinking content |
| `total_tool_result_chars` | Total tool output |
| `total_bash_output_chars` | Total bash output |

## Key Patterns to Search For

| Pattern | What it indicates |
|---------|------------------|
| `<skill name="...">` | An existing skill was loaded |
| `isError: true` | A tool call failed |
| `stopReason: error` | Model stopped due to error |
| `stopReason: aborted` | User aborted generation |
| `stopReason: length` | Output hit max token limit |
| `Successfully replaced/wrote` | A file edit succeeded |
| `@ts-expect-error` | TypeScript suppression |
| `Cannot find module` | LSP module resolution issue |
| `object-template` | API parameter format mismatch |
| `compaction` entry | Context was compacted |
| `branch_summary` entry | Alternative approach was tried |
