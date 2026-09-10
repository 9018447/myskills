#!/usr/bin/env python3
"""
Validate session-reflection scripts work correctly.

Runs all scripts against a session file and checks for:
- Import errors
- Runtime crashes
- Missing dict keys
- False positive errors (errors matched in skill content)
- Data quality issues (empty results when data expected)

Usage:
    python validate_scripts.py <session.html> [--output-format json|text]
    python validate_scripts.py <session.html> --strict     # fail on warnings too
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent

SCRIPTS = {
    "parse_session": {
        "file": "parse_session.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "parse_session.py")],
        "check": "imports",
    },
    "extract_errors": {
        "file": "extract_errors.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "extract_errors.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
    "extract_tool_calls": {
        "file": "extract_tool_calls.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "extract_tool_calls.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
    "extract_user_feedback": {
        "file": "extract_user_feedback.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "extract_user_feedback.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
    "extract_skills": {
        "file": "extract_skills.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "extract_skills.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
    "extract_error_fix_chains": {
        "file": "extract_error_fix_chains.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "extract_error_fix_chains.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
    "extract_workflow": {
        "file": "extract_workflow.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "extract_workflow.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
    "analyze_session": {
        "file": "analyze_session.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "analyze_session.py")],
        "args": ["--output-dir", "/tmp/session-reflection-validation"],
        "check": "files_created",
    },
    "detect_self_changes": {
        "file": "detect_self_changes.py",
        "test_cmd": [sys.executable, str(SCRIPTS_DIR / "detect_self_changes.py")],
        "args": ["--output-format", "json"],
        "check": "json_output",
    },
}

# Required keys for each script's JSON output
REQUIRED_KEYS = {
    "extract_errors": ["analysis", "errors"],
    "extract_tool_calls": ["analysis"],
    "extract_user_feedback": ["analysis", "feedback"],
    "extract_skills": ["analysis", "skills"],
    "extract_error_fix_chains": ["analysis", "chains"],
    "extract_workflow": ["workflows"],
    "detect_self_changes": ["skill_invoked", "files_changed", "recommendations"],
}

# Keys that must exist in analysis sub-objects
ANALYSIS_KEYS = {
    "extract_tool_calls": ["total", "successful", "failed"],
    "extract_errors": ["total"],
}


def validate_script(name: str, config: dict, session_path: str, strict: bool = False) -> dict:
    """Run a single script and validate its output."""
    result = {
        "script": name,
        "file": config["file"],
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "output_preview": "",
        "duration_ms": 0,
    }

    file_path = SCRIPTS_DIR / config["file"]
    if not file_path.exists():
        result["status"] = "SKIP"
        result["warnings"].append(f"File not found: {config['file']}")
        return result

    cmd = list(config["test_cmd"])
    cmd.append(session_path)
    cmd.extend(config.get("args", []))

    start = datetime.now()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(SCRIPTS_DIR),
        )
        elapsed = (datetime.now() - start).total_seconds() * 1000
        result["duration_ms"] = int(elapsed)

        if proc.returncode != 0:
            result["status"] = "FAIL"
            stderr = proc.stderr.strip()
            result["errors"].append(f"Exit code {proc.returncode}: {stderr[:200]}")
            return result

        stdout = proc.stdout.strip()
        result["output_preview"] = stdout[:200]

        if not stdout:
            if config["check"] == "json_output":
                result["status"] = "FAIL"
                result["errors"].append("Empty output (expected JSON)")
            return result

        # ── JSON output validation ──
        if config["check"] == "json_output":
            try:
                data = json.loads(stdout)
            except json.JSONDecodeError as e:
                result["status"] = "FAIL"
                result["errors"].append(f"Invalid JSON output: {e}")
                return result

            # Check required top-level keys
            if name in REQUIRED_KEYS:
                for key in REQUIRED_KEYS[name]:
                    if key not in data:
                        result["status"] = "FAIL"
                        result["errors"].append(f"Missing required key: '{key}'")

            # Check analysis sub-keys
            if name in ANALYSIS_KEYS:
                analysis = data.get("analysis", {})
                for key in ANALYSIS_KEYS[name]:
                    if key not in analysis:
                        result["status"] = "FAIL"
                        result["errors"].append(f"Missing analysis key: '{key}'")

            # ── Quality checks ──
            if name == "extract_errors":
                errors_list = data.get("errors", [])
                false_positives = [
                    e for e in errors_list
                    if e.get("role") == "user"
                    or (e.get("role") == "toolResult"
                        and e.get("related_tool") == "read"
                        and "error" in e.get("context", "").lower())
                ]
                if false_positives:
                    result["warnings"].append(
                        f"{len(false_positives)} possible false positive(s) detected "
                        f"(errors from user role or read tool results)"
                    )
                    if strict:
                        result["status"] = "WARN"

            if name == "extract_tool_calls":
                analysis = data.get("analysis", {})
                total = analysis.get("total", 0)
                successful = analysis.get("successful", 0)
                failed = analysis.get("failed", 0)
                if total > 0 and successful + failed != total:
                    result["warnings"].append(
                        f"successful({successful}) + failed({failed}) ≠ total({total})"
                    )

            if name == "extract_error_fix_chains":
                chains = data.get("chains", [])
                unresolved = [c for c in chains if not c.get("resolved", False)]
                if unresolved:
                    result["warnings"].append(
                        f"{len(unresolved)} unresolved error-fix chain(s)"
                    )

        # ── File creation validation ──
        elif config["check"] == "files_created":
            out_dir = Path("/tmp/session-reflection-validation")
            required_files = ["summary.json", "session_analysis.json", "session_analysis.txt"]
            for fname in required_files:
                fpath = out_dir / fname
                if not fpath.exists():
                    result["status"] = "FAIL"
                    result["errors"].append(f"Expected output file not created: {fname}")

        # ── Import validation ──
        elif config["check"] == "imports":
            if proc.returncode == 0:
                result["output_preview"] = "Import OK"

    except subprocess.TimeoutExpired:
        result["status"] = "FAIL"
        result["errors"].append("Script timed out after 60 seconds")
    except Exception as e:
        result["status"] = "FAIL"
        result["errors"].append(f"Unexpected error: {str(e)[:200]}")

    return result


def validate_all(session_path: str, strict: bool = False) -> dict:
    """Run all script validations."""
    results = []
    pass_count = 0
    fail_count = 0
    warn_count = 0
    skip_count = 0

    for name, config in SCRIPTS.items():
        r = validate_script(name, config, session_path, strict)
        results.append(r)
        if r["status"] == "PASS":
            pass_count += 1
        elif r["status"] == "FAIL":
            fail_count += 1
        elif r["status"] == "WARN":
            warn_count += 1
        elif r["status"] == "SKIP":
            skip_count += 1

    return {
        "session": session_path,
        "timestamp": datetime.now().isoformat(),
        "strict": strict,
        "summary": {
            "total": len(results),
            "pass": pass_count,
            "fail": fail_count,
            "warn": warn_count,
            "skip": skip_count,
            "overall": "PASS" if fail_count == 0 and (not strict or warn_count == 0) else "FAIL",
        },
        "results": results,
    }


def format_text(report: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("SCRIPT VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Session: {report['session']}")
    lines.append(f"Strict mode: {report['strict']}")
    lines.append(f"Timestamp: {report['timestamp']}")
    lines.append("")

    s = report["summary"]
    overall_icon = "✅" if s["overall"] == "PASS" else "❌"
    lines.append(f"OVERALL: {overall_icon} {s['overall']}")
    lines.append(f"  Pass: {s['pass']}  Fail: {s['fail']}  Warn: {s['warn']}  Skip: {s['skip']}")
    lines.append("")

    lines.append("DETAILS:")
    lines.append("-" * 40)
    for r in report["results"]:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}[r["status"]]
        lines.append(f"  {icon} {r['script']:30s} [{r['status']}] ({r['duration_ms']}ms)")
        for err in r["errors"]:
            lines.append(f"     ❌ {err}")
        for warn in r["warnings"]:
            lines.append(f"     ⚠️  {warn}")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_scripts.py <session.html> [--output-format json|text] [--strict]")
        sys.exit(1)

    session_path = sys.argv[1]
    output_format = "text"
    strict = "--strict" in sys.argv

    if "--output-format" in sys.argv:
        idx = sys.argv.index("--output-format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not Path(session_path).exists():
        print(f"Error: File not found: {session_path}", file=sys.stderr)
        sys.exit(1)

    report = validate_all(session_path, strict)

    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_text(report))

    # Exit code: 0 if all pass, 1 if any fail
    sys.exit(0 if report["summary"]["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()
