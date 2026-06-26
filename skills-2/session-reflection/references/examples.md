# Session Reflection Examples

## Example: Update Mode Reflection Report

```markdown
# Session Reflection: pi-config

## Task
Create an interactive `/add-provider` command to visually add model providers.

## Error-Fix Chains
| Error | Root Cause | Fix | Steps | Prevention |
|-------|-----------|-----|-------|------------|
| TUI crash: line exceeds width | No truncation for box-drawing + ANSI | ASCII borders + truncateToWidth() | 3 | Always truncate TUI lines |
| Select shows [object Object] | Passed {value,label}[] to select() | String array with "Label — Desc" | 2 | Check API param types |
| Provider not visible | Only wrote models.json | Dual-write (registerProvider + json) | 1 | Always register + persist |

## Anti-Patterns
- ❌ Passing objects to `ctx.ui.select()` → ✅ Use string arrays
  - Why: select() only accepts string[], objects get toString()'d
- ❌ Writing only to models.json → ✅ Dual-write strategy
  - Why: Runtime providers need registerProvider(), not just file

## Skill Updates Applied
- Added § TUI Development Rules (5 rules)
- Added § Custom Providers: Dual-Write Strategy
- Created references/tui-development.md
```

## Example: Create Mode Reflection Report

```markdown
# Session Reflection: biosteam-deps (NEW SKILL)

## Task
Resolve dependency conflicts in a BioSteam Python project.

## Workflow Summary
1. Read pyproject.toml and setup.py
2. Run `pip install -e .` to identify conflicts
3. Pin conflicting versions in pyproject.toml
4. Add `--no-deps` flag for specific packages
5. Verify with `python -c "import biosteam"`

## Key Steps (Extracted Workflow)
- Domain: dependency-resolution
- Files: pyproject.toml, setup.py
- Success: 5 steps, 0 branches

## Anti-Patterns Detected
- ❌ Running `pip install --upgrade` on all deps → ✅ Pin and upgrade selectively
  - Why: Bulk upgrades break compatibility chains
```

## Example: Self-Iteration Detection Output

```bash
$ python detect_self_changes.py session.html
============================================================
SELF-ITERATION DETECTION REPORT
============================================================

Session: 019e15f6-2819-747f-aaa2-b35fbad29ac1
Skill invoked: YES

INVOCATIONS (2):
  [skill_load] Entry 38
  [user_mention] Entry 101

METRICS:
  Edits to skill files: 6
  Writes to skill files: 4
  Error-fix chains: 3
  New scripts created: 2

FILES CHANGED (10):
  [write] Entry 50: parse_session.py (NEW) (14452 chars)
  [write] Entry 52: extract_errors.py (NEW) (9978 chars)
  [edit] Entry 72: extract_user_feedback.py (73→75 chars)
  [edit] Entry 76: extract_tool_calls.py (150→200 chars)
  ...

ERROR-FIX CHAINS:
  Error [69]: Traceback (most recent call last)...
    Fix  [73]: edit → extract_user_feedback.py
    Steps: 2
  Error [75]: KeyError: 'successful'...
    Fix  [77]: edit → extract_tool_calls.py
    Steps: 1

RECOMMENDATIONS:
  • Skill was invoked AND modified during this session.
    Review the changes below and apply improvements to the current scripts.
  • New scripts were created: ['parse_session.py', 'extract_errors.py', ...]
    Check if current versions are up-to-date.
  • 2 error-fix chain(s) detected in skill scripts.
    These fixes should be applied to prevent the same errors in future sessions.
```

## Example: Validation Output

```bash
$ python validate_scripts.py session.html
============================================================
SCRIPT VALIDATION REPORT
============================================================
Session: session.html
Strict mode: False

OVERALL: ✅ PASS
  Pass: 9  Fail: 0  Warn: 0  Skip: 0

DETAILS:
----------------------------------------
  ✅ parse_session                 [PASS] (120ms)
  ✅ extract_errors                [PASS] (340ms)
  ✅ extract_tool_calls            [PASS] (210ms)
  ✅ extract_user_feedback         [PASS] (180ms)
  ✅ extract_skills                [PASS] (190ms)
  ✅ extract_error_fix_chains      [PASS] (450ms)
  ✅ extract_workflow              [PASS] (320ms)
  ✅ analyze_session               [PASS] (680ms)
  ✅ detect_self_changes           [PASS] (150ms)
```
