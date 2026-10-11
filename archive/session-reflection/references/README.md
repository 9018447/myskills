# Session Analysis Scripts

These scripts parse pi session HTML exports and extract key information for reflection.

## Quick Start

```bash
# Full analysis (recommended)
python analyze_session.py <session.html> --output-dir /tmp/session-analysis/

# Individual scripts
python extract_errors.py <session.html>
python extract_tool_calls.py <session.html>
python extract_user_feedback.py <session.html>
python extract_skills.py <session.html>
python extract_error_fix_chains.py <session.html>
python extract_workflow.py <session.html>

# Self-iteration tools
python detect_self_changes.py <session.html>
python validate_scripts.py <session.html>
```

## Scripts

| Script | Size | Purpose |
|--------|------|---------|
| `parse_session.py` | Core | Parse HTML exports into structured data (all entry types, full content preservation) |
| `extract_errors.py` | Analysis | Extract and classify errors with false-positive filtering (`is_skill_content()`) |
| `extract_tool_calls.py` | Analysis | Extract tool invocations with success/failure tracking |
| `extract_user_feedback.py` | Analysis | Extract user messages, classify feedback type, extract keywords |
| `extract_skills.py` | Analysis | Detect skill invocations and measure effectiveness |
| `extract_error_fix_chains.py` | Analysis | Correlate errors with subsequent fixes, identify root causes and anti-patterns |
| `extract_workflow.py` | Analysis | Extract successful workflow sequences, detect anti-patterns |
| `analyze_session.py` | Pipeline | Run all extractors and produce unified summary |
| `detect_self_changes.py` | Self-iter | Detect when session-reflection was used/modified in a session |
| `validate_scripts.py` | Self-iter | Validate all scripts work correctly, catch regressions |

## Output Formats

All analysis scripts support `--output-format json|text`:

```bash
python extract_errors.py <session.html> --output-format json
python extract_errors.py <session.html> --output-format text
python extract_errors.py <session.html> --output-format csv  # errors only
```

`analyze_session.py` uses `--output-dir` to write:
- `summary.json` — High-level metrics
- `session_analysis.json` — Full structured data
- `session_analysis.txt` — Human-readable report

## Self-Iteration

When analyzing a session that used the `session-reflection` skill itself:

```bash
# 1. Detect what changed
python detect_self_changes.py <session.html>

# 2. Apply improvements to current scripts (agent does this)

# 3. Validate everything still works
python validate_scripts.py <session.html>
```

See `CHANGELOG.md` for the history of self-iteration improvements.
