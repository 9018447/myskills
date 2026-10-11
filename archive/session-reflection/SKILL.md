---
name: session-reflection
description: >
  Analyze pi session exports to extract lessons learned, identify errors, and produce skill improvements.
---

# Session Reflection

Analyze a pi session export to extract lessons learned, identify errors, and produce skill improvements or new skills.

## How to Determine the Mode

When the user provides a session file, first run the quick analysis to determine which mode applies:

```bash
python references/analyze_session.py <session.html> --output-dir /tmp/session-analysis/
```

Then read the summary:
- **Skills used > 0** → Use **Update Mode** (improve existing skill)
- **Skills used = 0** but workflow exists → Use **Create Mode** (capture as new skill)

If unsure, ask the user which mode they prefer.

---

## Quick Analysis with Scripts

The `references/` directory contains Python scripts for fast session parsing.

### Full Analysis (Recommended)

```bash
# Run all extractors and save results
python references/analyze_session.py <session.html> --output-dir /tmp/session-analysis/

# Read the summary
cat /tmp/session-analysis/summary.json
```

This produces:
- `summary.json` — High-level metrics (skills, errors, tool calls, resolution rate)
- `session_analysis.json` — Full structured data
- `session_analysis.txt` — Human-readable report

### Individual Extractors

| Script | Purpose | Command |
|--------|---------|---------|
| `parse_session.py` | Raw session data | `python references/parse_session.py <file>` |
| `extract_errors.py` | Errors with categories | `python references/extract_errors.py <file>` |
| `extract_error_fix_chains.py` | **Error→Fix correlation** | `python references/extract_error_fix_chains.py <file>` |
| `extract_tool_calls.py` | Tool invocations | `python references/extract_tool_calls.py <file>` |
| `extract_user_feedback.py` | User messages | `python references/extract_user_feedback.py <file>` |
| `extract_skills.py` | Skill usage | `python references/extract_skills.py <file>` |
| `extract_workflow.py` | **Workflow sequences** | `python references/extract_workflow.py <file>` |
| `detect_self_changes.py` | **Self-iteration detection** | `python references/detect_self_changes.py <file>` |
| `validate_scripts.py` | **Script validation** | `python references/validate_scripts.py <file>` |

### Key Metrics to Check

| Metric | What it tells you |
|--------|-------------------|
| `errors_resolved` | How many errors were fixed |
| `errors_unresolved` | Errors that persisted (skill gaps) |
| `avg_steps_to_fix` | Efficiency of error resolution |
| `anti_patterns_found` | Repeated bad approaches (should be in skill) |
| `workflow_success` | Did the session achieve its goal? |
| `workflow_domains` | Type of task (config, debugging, code-gen) |
| `has_branching` | Alternative approaches were tried |
| `has_compaction` | Context limits were hit |
| `stop_reasons.aborted` | User aborted (possibly frustration) |
| `stop_reasons.error` | Model errors occurred |
| `compaction_tokens_saved` | How much context was lost |
| `edit_operations_count` | Iterative editing frequency |
| `models_used` | Which models powered the session |

---

## Update Mode (Existing Skill)

When the session used an existing skill and encountered errors or suboptimal behavior.

### Step 1: Extract and Analyze

```bash
python references/analyze_session.py <session.html> --output-dir /tmp/session-analysis/
python references/extract_error_fix_chains.py <session.html> --output-format json > /tmp/session-analysis/chains.json
```

Read the outputs to understand:
1. **What errors occurred** — from `extract_errors.py` output
2. **What caused them** — from `extract_error_fix_chains.py` root_cause field
3. **What fixed them** — from chains fix_method/fix_description
4. **What anti-patterns emerged** — from chains anti_pattern field

### Step 2: Read the Existing Skill

Read the skill's SKILL.md and identify:
- Which sections are missing the guidance that would have prevented the errors
- Where anti-patterns should be documented
- Where best practices should be added

### Step 3: Generate Reflection Report

Produce a structured reflection report:

```markdown
# Session Reflection: <skill-name>

## Task
<what the user was trying to do>

## Error-Fix Chains
| Error | Root Cause | Fix | Steps | Prevention |
|-------|-----------|-----|-------|------------|
| <error> | <cause> | <fix> | N | <prevention> |

## Anti-Patterns Identified
- ❌ <wrong approach> → ✅ <correct approach>
  - Why: <explanation from session>

## Skill Updates Proposed
- Add to § <section>: <what to add>
- Modify § <section>: <what to change>
```

### Step 4: Apply Updates

**Path routing rules:**
- If skill is in `~/.agents/skills/` → Update in place (global skill)
- If skill is in project `.agents/skills/` → Update in place (project skill)

Update the skill files:
1. Add anti-patterns with WHY explanations
2. Add best practices with code examples
3. Add common errors with fix patterns
4. Update reference files if needed

### Step 5: Verify and Report

After updating:
- List what was changed
- Map which session errors are now covered
- Note any remaining gaps

---

## Create Mode (New Skill)

When the session shows a workflow that should be captured as a new skill.

### Step 1: Extract Workflow

```bash
python references/extract_workflow.py <session.html>
```

This gives you:
- Goal (what the user wanted)
- Domain (config, debugging, code-gen, etc.)
- Key steps (the successful sequence)
- Files acted on
- Anti-patterns detected

### Step 2: Determine Skill Scope

Based on the workflow, decide:
- **Skill name** — descriptive, kebab-case
- **Trigger description** — when should this skill activate?
- **Core content** — what instructions should the skill contain?
- **Reference files** — does detailed content need to be in references/?

### Step 3: Determine Output Path

**Path routing rules for new skills:**
- If session references an existing project → `.agents/skills/<skill-name>/` (project-level)
- If session is about general pi usage → `~/.agents/skills/<skill-name>/` (global)
- If unsure → ask the user

To determine if session is project-specific:
- Check session header `cwd` field
- Look for project-specific files in tool calls (package.json, pyproject.toml, etc.)
- Check if user messages reference project context

### Step 4: Write the Skill

Follow skill-creator conventions:

1. **SKILL.md** — under 500 lines, with:
   - YAML frontmatter (name, description — pushy for triggering)
   - Decision tree or workflow
   - Key instructions with WHY explanations
   - Anti-patterns and best practices from the session
   - Pointers to reference files for detailed content

2. **Reference files** (if needed) — for:
   - Detailed code examples
   - API reference tables
   - Extended anti-pattern catalogs

### Step 5: Include Lessons Learned

Every skill created from a session MUST include:
- **Anti-patterns section** — what NOT to do, with explanations of why
- **Best practices** — what TO do, with code examples
- **Common errors** — errors encountered and their fixes

---

## Common Pitfalls & Anti-Patterns

These are lessons learned from real sessions building and debugging these scripts.

### 1. False Positive Errors from Skill Content

❌ **Treating all text pattern matches as real errors**
→ ✅ **Use `isError` field as primary signal, text patterns as secondary**

- Why: Scripts that match `"error"` or `"Error:"` in text will fire on SKILL.md content that documents error handling patterns. The `isError` field on `toolResult` entries is the ground truth.
- The `is_skill_content()` filter in `extract_errors.py` handles most cases, but always validate: run `extract_errors.py --output-format json` and check if any errors have `role: user` or context from markdown files.

### 2. Iterative Debugging with Multiple Edits

❌ **Editing the same file 6+ times to fix bugs**
→ ✅ **Write the complete script once, test against a small input, then fix**

- Why: Each edit risks breaking adjacent code. Writing once reduces total iterations.
- Test scripts with `--output-format json | head -20` before running full pipeline.

### 3. Missing Dict Keys

❌ **Returning incomplete dict structures**
→ ✅ **Always return all expected keys with default values**

- Why: Downstream code (especially `analyze_session.py`) assumes all keys exist. Missing keys cause `KeyError` crashes.
- Example: `return {"total": 0, "successful": 0, "failed": 0, "by_tool": {}}` not just `{"total": 0, "by_tool": {}}`

### 4. Piping Script Output to JSON Parser

❌ **`python script.py file.html | python3 -c "json.load(sys.stdin)"`**
→ ✅ **Use `--output-dir` flag or redirect to file, then read the file**

- Why: Scripts can fail silently or produce empty output, causing `JSONDecodeError`.
- The `--output-dir` flag in `analyze_session.py` handles this safely.

### 5. Running `find /` for File Searches

❌ **`find / -name "pi-session-*"`**
→ ✅ **Scope to `~/.pi/agent` or `~` at most**

- Why: Full filesystem search is slow and can timeout or find irrelevant files.

### 6. LSP Module-Not-Found Warnings

❌ **Treating `Cannot find module '@earendil-works/pi-coding-agent'` as real errors**
→ ✅ **Suppress known pi-internal module warnings**

- Why: The agent runs in its own environment where pi internals aren't installed. These are expected.

---

## Script Development Best Practices

### Writing New Scripts

1. **Start with the data model** — define what the script returns before writing logic
2. **Handle empty input** — `if not entries: return {"total": 0, ...}`
3. **Use defensive dict access** — `msg.get('role', '')` not `msg['role']`
4. **Test incrementally** — run with `--output-format json | head -20` first

### Testing Scripts

```bash
# Quick sanity check
python references/extract_errors.py <session.html> --output-format json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Errors: {d[\"analysis\"][\"total\"]}')"

# Check for false positives
python references/extract_errors.py <session.html> --output-format json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for e in d['errors']:
    if e['role'] == 'user':
        print(f'⚠ Possible false positive: Entry {e["entry_index"]} role={e["role"]}')
"

# Validate all keys present
python references/extract_tool_calls.py <session.html> --output-format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'successful' in d['analysis'], 'Missing key!'"
```

### Error Classification Priority

When classifying errors in a session, use this priority:

1. **`isError: true` on `toolResult`** → Real error (highest confidence)
2. **`errorMessage` field on assistant** → Model-level error
3. **`stopReason: error`** → Model stopped due to error
4. **Text pattern matching** → Lower confidence, validate against context
5. **LSP diagnostic text** → Usually warnings, not errors

---

## Self-Iteration Mode

When analyzing a session that used the `session-reflection` skill itself (or any session that modified skill scripts), the skill can detect its own improvements and apply them automatically.

### When to Use Self-Iteration

- The session being analyzed **invoked session-reflection** (check for `<skill name="session-reflection">`)
- The session **edited or wrote files** under `references/` or `SKILL.md`
- The session **fixed bugs** in the analysis scripts
- The user asks to "iterate", "self-improve", or "apply session fixes"

### Step 1: Detect Self-Changes

```bash
python references/detect_self_changes.py <session.html> --output-format json
```

This reports:
- Whether session-reflection was invoked
- All edits/writes to skill files
- Error-fix chains where fixes targeted skill scripts
- Recommendations for applying improvements

### Step 2: Read Current Scripts

For each changed file, read the current version and compare with the session's changes:
- If the session **wrote a new file** → check if current version needs updating
- If the session **edited a file** → extract the edit (oldText/newText) and apply if not yet present
- If the session **fixed a bug** → ensure the fix is in the current code

### Step 3: Apply Improvements

For each detected change:
1. Read the current file
2. Check if the improvement is already applied (search for newText in current file)
3. If not applied: use `edit` tool with the session's oldText→newText
4. If the file was rewritten entirely: use `write` tool with the new content

### Step 4: Validate After Changes

**Always validate after self-iteration:**

```bash
python references/validate_scripts.py <session.html>
```

This runs all scripts and checks for:
- Import errors or runtime crashes
- Missing dict keys in output
- False positive errors (errors from skill content)
- Data quality issues

If validation fails → revert the change and investigate.

### Step 5: Record the Change

Append to `references/CHANGELOG.md`:

```markdown
## YYYY-MM-DD — Self-iteration from session <id>
- **Source**: <session.html>
- **Changes applied**:
  - <file>: <what changed and why>
- **Validation**: PASS/FAIL
- **Errors covered**: <which session errors are now prevented>
```

### Self-Iteration Loop

The full self-iteration loop is:

```
Session → detect_self_changes → extract improvements →
  apply to current scripts → validate → record changelog
```

This creates a feedback loop: each session that uses and improves the skill makes future sessions more robust.

---

## Session Format Reference

See `references/session_format_spec.md` for the complete Pi session format specification (v3).

---

## Quality Checklist

Before finalizing a reflection:

- [ ] All errors are documented with root causes and fixes
- [ ] Anti-patterns include WHY explanations (not just "don't do this")
- [ ] Best practices include working code examples
- [ ] The skill follows skill-creator conventions
- [ ] Reference files are used for content > 500 lines
- [ ] Path routing: skill saved to correct location
- [ ] The reflection report maps errors to skill sections

---

## Examples

See `references/examples.md` for example reflection reports, self-iteration detection output, and validation output.
