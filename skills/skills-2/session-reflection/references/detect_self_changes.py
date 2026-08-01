#!/usr/bin/env python3
"""
Detect when session-reflection was used to analyze/modify itself.

Scans a session for:
1. Whether session-reflection skill was invoked
2. All edits/writes to files under the session-reflection directory
3. Error-fix chains where the fix targeted session-reflection scripts
4. Recommendations for applying detected improvements

Usage:
    python detect_self_changes.py <session.html> [--output-format json|text]
    python detect_self_changes.py <session.html> --output-format json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from parse_session import decode_session_html, extract_text_from_content
except ImportError:
    print("Error: parse_session.py not found. Run from the references/ directory.", file=sys.stderr)
    sys.exit(1)

SKILL_NAME = "session-reflection"
SKILL_DIR_KEYWORDS = [
    "session-reflection",
    "session_reflection",
]


def detect_self_changes(html_path: str) -> dict:
    """Main detection logic."""
    data = decode_session_html(html_path)
    entries = data.get("entries", [])
    skill_dir = str(Path(__file__).resolve().parent.parent)

    skill_invoked = False
    skill_invocations = []

    changed_files = []        # edits/writes to session-reflection files
    error_fix_chains = []     # errors fixed by edits to session-reflection files
    new_scripts_created = []  # scripts written for the first time
    metrics = {
        "total_edits": 0,
        "total_writes": 0,
        "error_fix_chains_count": 0,
        "new_scripts_count": 0,
        "improvement_categories": {},
    }

    # Pending errors: entry_idx → error_info
    pending_errors: dict = {}

    for i, entry in enumerate(entries):
        msg = entry.get("message", {})
        role = msg.get("role", "")
        content = msg.get("content", "")

        # ── Detect skill invocation ──────────────────────────
        if role == "user" and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                text = block.get("text", "")
                if (
                    f'<skill name="{SKILL_NAME}"' in text
                    or f"<skill name=\"{SKILL_NAME}\"" in text
                ):
                    skill_invoked = True
                    skill_invocations.append({
                        "entry": i,
                        "type": "skill_load",
                    })

        if role == "user" and isinstance(content, str):
            if SKILL_NAME in content and ("分析" in content or "analyze" in content.lower()):
                skill_invocations.append({
                    "entry": i,
                    "type": "user_mention",
                    "preview": content[:100],
                })

        # ── Collect errors ──────────────────────────────────
        if role == "toolResult" and msg.get("isError", False):
            tool_name = msg.get("toolName", "")
            err_text = extract_text_from_content(content) if isinstance(content, (str, list)) else str(content)
            pending_errors[i] = {
                "entry": i,
                "tool": tool_name,
                "message": (err_text or "")[:200],
            }

        # ── Detect edits/writes to session-reflection files ─
        if role == "assistant" and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "toolCall":
                    continue

                tool_name = block.get("name", "")
                args = block.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except (json.JSONDecodeError, TypeError):
                        args = {}

                target_path = args.get("path", "")

                if not any(kw in target_path for kw in SKILL_DIR_KEYWORDS):
                    continue

                # ── edit operation ──
                if tool_name == "edit":
                    edits_list = args.get("edits", [])
                    for ed in edits_list:
                        old_text = ed.get("oldText", "")
                        new_text = ed.get("newText", "")
                        changed_files.append({
                            "entry": i,
                            "operation": "edit",
                            "file": target_path,
                            "oldText_preview": old_text[:200],
                            "newText_preview": new_text[:200],
                            "oldText_len": len(old_text),
                            "newText_len": len(new_text),
                        })
                    metrics["total_edits"] += 1

                # ── write operation ──
                elif tool_name == "write":
                    file_content = args.get("content", "")
                    is_new = not Path(target_path).exists()
                    changed_files.append({
                        "entry": i,
                        "operation": "write",
                        "file": target_path,
                        "is_new_file": is_new,
                        "content_len": len(file_content),
                        "content_preview": file_content[:200],
                    })
                    metrics["total_writes"] += 1
                    if is_new:
                        new_scripts_created.append(target_path)

        # ── Match error→fix chains ──────────────────────────
        # After a toolResult error, look for subsequent edit/write
        # to the same or related file in session-reflection
        if role == "toolResult" and not msg.get("isError", False):
            # Check if this successful result is a fix for a prior error
            tool_name = msg.get("toolName", "")
            result_text = extract_text_from_content(content) if isinstance(content, (str, list)) else ""

            if tool_name in ("edit", "write") and "Successfully" in (result_text or ""):
                # Find the closest pending error that was fixed
                result_file = ""
                if isinstance(content, str):
                    import re
                    m = re.search(r"to\s+(/\S+)", content)
                    if m:
                        result_file = m.group(1)

                for err_idx, err_info in sorted(pending_errors.items()):
                    if err_idx >= i:
                        break  # error is after this fix, skip
                    error_fix_chains.append({
                        "error_entry": err_info["entry"],
                        "error_message": err_info["message"],
                        "error_tool": err_info["tool"],
                        "fix_entry": i,
                        "fix_tool": tool_name,
                        "fix_file": result_file,
                        "steps_to_fix": i - err_info["entry"],
                    })
                    del pending_errors[err_idx]
                    metrics["error_fix_chains_count"] += 1
                    break

    # ── Build recommendations ────────────────────────────
    recommendations = []

    if skill_invoked and changed_files:
        recommendations.append(
            "Skill was invoked AND modified during this session. "
            "Review the changes below and apply improvements to the current scripts."
        )

    if new_scripts_created:
        recommendations.append(
            f"New scripts were created: {new_scripts_created}. "
            "Check if current versions are up-to-date."
        )

    if error_fix_chains:
        recommendations.append(
            f"{len(error_fix_chains)} error-fix chain(s) detected in skill scripts. "
            "These fixes should be applied to prevent the same errors in future sessions."
        )

    for chain in error_fix_chains:
        fname = Path(chain["fix_file"]).name if chain["fix_file"] else "unknown"
        recommendations.append(
            f"  → {chain['error_message'][:80]}... "
            f"(fixed by edit at entry {chain['fix_entry']}, file: {fname})"
        )

    if not skill_invoked:
        recommendations.append(
            "This session did not use session-reflection. "
            "No self-iteration changes to apply."
        )

    # ── Build result ─────────────────────────────────────
    return {
        "session_id": data.get("header", {}).get("id", "unknown"),
        "skill_invoked": skill_invoked,
        "invocations": skill_invocations,
        "files_changed": changed_files,
        "new_scripts_created": new_scripts_created,
        "error_fix_chains": error_fix_chains,
        "unresolved_errors": list(pending_errors.values()),
        "metrics": metrics,
        "recommendations": recommendations,
    }


# ── Output formatters ────────────────────────────────────

def format_text(result: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("SELF-ITERATION DETECTION REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Session: {result['session_id']}")
    lines.append(f"Skill invoked: {'YES' if result['skill_invoked'] else 'NO'}")
    lines.append("")

    if result["invocations"]:
        lines.append(f"INVOCATIONS ({len(result['invocations'])}):")
        for inv in result["invocations"]:
            lines.append(f"  [{inv['type']}] Entry {inv['entry']}")
        lines.append("")

    m = result["metrics"]
    lines.append("METRICS:")
    lines.append(f"  Edits to skill files: {m['total_edits']}")
    lines.append(f"  Writes to skill files: {m['total_writes']}")
    lines.append(f"  Error-fix chains: {m['error_fix_chains_count']}")
    lines.append(f"  New scripts created: {m['new_scripts_count']}")
    lines.append("")

    if result["files_changed"]:
        lines.append(f"FILES CHANGED ({len(result['files_changed'])}):")
        for fc in result["files_changed"]:
            fname = Path(fc["file"]).name
            op = fc["operation"]
            if op == "edit":
                lines.append(f"  [edit] Entry {fc['entry']}: {fname} "
                             f"({fc['oldText_len']}→{fc['newText_len']} chars)")
            else:
                new_tag = " (NEW)" if fc.get("is_new_file") else ""
                lines.append(f"  [write] Entry {fc['entry']}: {fname}{new_tag} "
                             f"({fc['content_len']} chars)")
        lines.append("")

    if result["error_fix_chains"]:
        lines.append("ERROR-FIX CHAINS:")
        for c in result["error_fix_chains"]:
            lines.append(f"  Error [{c['error_entry']}]: {c['error_message'][:80]}")
            lines.append(f"    Fix  [{c['fix_entry']}]: {c['fix_tool']} → {c['fix_file']}")
            lines.append(f"    Steps: {c['steps_to_fix']}")
        lines.append("")

    if result["recommendations"]:
        lines.append("RECOMMENDATIONS:")
        for r in result["recommendations"]:
            lines.append(f"  • {r}")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_self_changes.py <session.html> [--output-format json|text]")
        sys.exit(1)

    html_path = sys.argv[1]
    output_format = "text"
    if "--output-format" in sys.argv:
        idx = sys.argv.index("--output-format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not Path(html_path).exists():
        print(f"Error: File not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    result = detect_self_changes(html_path)

    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
