#!/usr/bin/env python3
"""
Extract error-fix chains from pi session HTML exports.

Correlates errors with subsequent fixes to identify:
- What caused the error (root cause chain)
- What fixed it (fix method)
- How long it took (tool calls between error and fix)
- Whether the fix was effective

Usage:
    python extract_error_fix_chains.py <session.html> [--output-format json|text]
"""

import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Optional

from parse_session import decode_session_html, extract_text_from_content


@dataclass
class ErrorFixChain:
    """A chain linking an error to its fix."""
    error_entry: int
    error_message: str
    error_category: str
    error_context: str  # What was happening when error occurred
    error_message_field: str = ""  # From toolResult.errorMessage

    # Chain analysis
    fix_entry: Optional[int] = None
    fix_method: str = ""  # edit, write, bash, manual, unresolved
    fix_description: str = ""  # What was changed
    fix_file: str = ""  # Which file was fixed
    fix_edit_changes: Optional[List[dict]] = None  # Full oldText/newText diffs
    steps_to_fix: int = 0  # Tool calls between error and fix
    time_to_fix_entries: int = 0  # Entries between error and fix

    # Classification
    root_cause: str = ""  # API misuse, missing import, wrong format, etc.
    prevention: str = ""  # What would have prevented this
    anti_pattern: str = ""  # The wrong approach that caused this

    is_resolved: bool = False


# Root cause patterns based on error messages
ROOT_CAUSE_PATTERNS = {
    r'Cannot find module': {
        'cause': 'Module not installed or import path wrong',
        'prevention': 'Check module resolution: install dependency or use @ts-expect-error for pi internals',
        'anti_pattern': 'Assuming LSP module resolution matches runtime resolution'
    },
    r'Rendered line exceeds terminal width': {
        'cause': 'TUI rendering without width truncation',
        'prevention': 'Always truncate lines to terminal width before rendering',
        'anti_pattern': 'Using Unicode box-drawing with ANSI codes without width calculation'
    },
    r'object-template|\[object Object\]': {
        'cause': 'Passed object to API expecting string',
        'prevention': 'Check API parameter types before passing complex objects',
        'anti_pattern': 'Assuming API accepts {value, label} objects when it only accepts strings'
    },
    r'Unused.*@ts-expect-error': {
        'cause': 'TypeScript suppression no longer needed',
        'prevention': 'Remove @ts-expect-error after fixing underlying issue',
        'anti_pattern': 'Adding @ts-expect-error without removing when no longer needed'
    },
    r'no-any-type': {
        'cause': 'Using any type instead of specific type',
        'prevention': 'Define proper types or use unknown with type guards',
        'anti_pattern': 'Using any to avoid type errors'
    },
    r'JSONDecodeError|Expecting value': {
        'cause': 'Empty or malformed JSON input',
        'prevention': 'Validate JSON input before parsing',
        'anti_pattern': 'Assuming subprocess output is valid JSON'
    },
    r'NameError|KeyError|TypeError': {
        'cause': 'Python runtime error - wrong variable name or missing key',
        'prevention': 'Test code paths; use .get() for dict access',
        'anti_pattern': 'Assuming variable exists without checking'
    },
    r'hardcoded secret|potential secret': {
        'cause': 'API key or secret in source code',
        'prevention': 'Use environment variables for secrets',
        'anti_pattern': 'Hardcoding placeholder API keys'
    },
}


def classify_root_cause(error_message: str) -> dict:
    """Classify root cause based on error message patterns."""
    for pattern, info in ROOT_CAUSE_PATTERNS.items():
        if re.search(pattern, error_message, re.IGNORECASE):
            return info
    return {
        'cause': 'Unknown',
        'prevention': 'Review error context and fix approach',
        'anti_pattern': ''
    }


def find_fix_for_error(error_entry_idx: int, error_file: str, entries: list,
                       error_message: str) -> Optional[dict]:
    """Find the fix that resolved this error by looking at subsequent edits/writes."""
    # Look at entries after the error for fixes
    search_window = min(len(entries), error_entry_idx + 30)
    tool_calls_since_error = 0

    for i in range(error_entry_idx + 1, search_window):
        entry = entries[i]
        msg = entry.get('message', {})
        role = msg.get('role', '')
        content = msg.get('content', '')

        # Only look at tool results (which follow tool calls)
        if role != 'toolResult':
            continue

        tool_calls_since_error += 1
        tool_name = msg.get('toolName', '')
        is_error = msg.get('isError', False)
        result_text = extract_text_from_content(content)

        # Check if this is a successful edit/write to the same file
        if not is_error and tool_name in ('edit', 'write'):
            tool_call_id = msg.get('toolCallId', '')
            for j in range(max(0, i - 15), i):
                prev_entry = entries[j]
                prev_content = prev_entry.get('message', {}).get('content', [])
                if isinstance(prev_content, list):
                    for item in prev_content:
                        if isinstance(item, dict) and item.get('type') == 'toolCall':
                            if item.get('id') == tool_call_id:
                                args = item.get('arguments', {})
                                target_file = args.get('path', '')
                                # Extract full edit diffs
                                edits = args.get('edits', [])
                                edit_desc = ""
                                if edits:
                                    # Get the full newText (the fix content)
                                    edit_desc = str(edits[0].get('newText', ''))[:300]
                                elif args.get('content'):
                                    edit_desc = str(args.get('content', ''))[:300]

                                return {
                                    'entry': i,
                                    'method': tool_name,
                                    'description': edit_desc,
                                    'file': target_file,
                                    'steps': tool_calls_since_error,
                                    'edit_changes': [
                                        {
                                            'oldText': e.get('oldText', ''),
                                            'newText': e.get('newText', '')
                                        }
                                        for e in edits
                                    ]
                                }

        # Check if this is a successful bash command that fixed something
        if not is_error and tool_name == 'bash':
            if 'Successfully' in result_text or 'fixed' in result_text.lower():
                tool_call_id = msg.get('toolCallId', '')
                for j in range(max(0, i - 5), i):
                    prev_entry = entries[j]
                    prev_content = prev_entry.get('message', {}).get('content', [])
                    if isinstance(prev_content, list):
                        for item in prev_content:
                            if isinstance(item, dict) and item.get('type') == 'toolCall':
                                if item.get('id') == tool_call_id:
                                    args = item.get('arguments', {})
                                    return {
                                        'entry': i,
                                        'method': 'bash',
                                        'description': args.get('command', '')[:200],
                                        'file': '',
                                        'steps': tool_calls_since_error
                                    }

    return None


def is_real_error(entry: dict, entry_index: int, skill_entries: set) -> bool:
    """Distinguish real runtime errors from skill content noise.

    Returns True if this entry contains a real error, False if it's just
    skill content that mentions error patterns.
    """
    msg = entry.get('message', {})
    role = msg.get('role', '')
    content = extract_text_from_content(msg.get('content', ''))

    # If this entry loaded skill content, it's likely noise
    if entry_index in skill_entries:
        return False

    # If the content is very long and contains skill markdown patterns,
    # it's likely skill content
    if len(content) > 2000 and ('## ' in content or '| ' in content):
        return False

    # If it's a toolResult that read a .md file, skip error patterns in it
    if role == 'toolResult':
        tool_name = msg.get('toolName', '')
        if tool_name == 'read':
            # Check if the result looks like markdown content
            if content.count('\n') > 10 and ('# ' in content or '- ' in content):
                return False

    return True


def find_skill_loading_entries(entries: list) -> set:
    """Find entries that loaded skill content (to exclude from error detection)."""
    skill_entries = set()

    for i, entry in enumerate(entries):
        msg = entry.get('message', {})
        content = extract_text_from_content(msg.get('content', ''))

        # Skill loading patterns
        if '<skill name=' in content:
            skill_entries.add(i)
        if re.search(r'SKILL\.md', content) and len(content) > 500:
            skill_entries.add(i)
        # Adjacent entries that are part of skill loading
        if i > 0 and (i - 1) in skill_entries:
            prev = entries[i - 1]
            prev_msg = prev.get('message', {})
            if prev_msg.get('role') == msg.get('role'):
                skill_entries.add(i)

    return skill_entries


def extract_error_fix_chains(html_path: str) -> List[ErrorFixChain]:
    """Extract all error-fix chains from session file."""
    data = decode_session_html(html_path)
    entries = data.get('entries', [])
    chains = []

    # Find skill loading entries to exclude
    skill_entries = find_skill_loading_entries(entries)

    for i, entry in enumerate(entries):
        # Skip skill content entries
        if not is_real_error(entry, i, skill_entries):
            continue

        msg = entry.get('message', {})
        role = msg.get('role', '')
        content = extract_text_from_content(msg.get('content', ''))

        # Check for errors in tool results
        is_error = msg.get('isError', False)
        if role == 'toolResult' and is_error:
            error_msg = content[:300] if content else "Tool error"
            tool_name = msg.get('toolName', '')

            # Get context from the tool call
            context = f"Tool: {tool_name}"

            # Classify root cause
            cause_info = classify_root_cause(error_msg)

            # Find the fix
            fix = find_fix_for_error(i, '', entries, error_msg)

            error_msg_field = msg.get('errorMessage', '')

            chain = ErrorFixChain(
                error_entry=i,
                error_message=error_msg[:200],
                error_category='tool_error',
                error_context=context,
                error_message_field=error_msg_field,
                root_cause=cause_info['cause'],
                prevention=cause_info['prevention'],
                anti_pattern=cause_info['anti_pattern']
            )

            if fix:
                chain.fix_entry = fix['entry']
                chain.fix_method = fix['method']
                chain.fix_description = fix['description']
                chain.fix_file = fix['file']
                chain.steps_to_fix = fix['steps']
                chain.time_to_fix_entries = fix['entry'] - i
                chain.fix_edit_changes = fix.get('edit_changes')
                chain.is_resolved = True

            chains.append(chain)

        # Check for errors in user messages (user reporting issues)
        elif role == 'user':
            error_indicators = [
                r'Error:', r'error:', r'Traceback', r'❌', r'🔴',
                r'fails?', r'crash', r'broken', r'doesn\'t work',
                r'报错', r'崩溃', r'出错', r'无效', r'失败',
                r'KeyError', r'NameError', r'TypeError', r'JSONDecodeError'
            ]
            is_error_msg = any(re.search(p, content, re.IGNORECASE) for p in error_indicators)

            if is_error_msg and len(content) > 20:
                cause_info = classify_root_cause(content)
                fix = find_fix_for_error(i, '', entries, content)

                chain = ErrorFixChain(
                    error_entry=i,
                    error_message=content[:200],
                    error_category='user_reported',
                    error_context=content[:300],
                    root_cause=cause_info['cause'],
                    prevention=cause_info['prevention'],
                    anti_pattern=cause_info['anti_pattern']
                )

                if fix:
                    chain.fix_entry = fix['entry']
                    chain.fix_method = fix['method']
                    chain.fix_description = fix['description']
                    chain.fix_file = fix['file']
                    chain.steps_to_fix = fix['steps']
                    chain.time_to_fix_entries = fix['entry'] - i
                    chain.is_resolved = True

                chains.append(chain)

    return chains


def analyze_chains(chains: List[ErrorFixChain]) -> dict:
    """Analyze error-fix chain patterns."""
    if not chains:
        return {"total": 0, "resolved": 0, "unresolved": 0, "by_cause": {}, "anti_patterns": []}

    resolved = [c for c in chains if c.is_resolved]
    unresolved = [c for c in chains if not c.is_resolved]

    by_cause = {}
    anti_patterns = []
    seen_patterns = set()  # Deduplicate
    fix_methods = {}

    for chain in chains:
        by_cause[chain.root_cause] = by_cause.get(chain.root_cause, 0) + 1
        if chain.anti_pattern and chain.anti_pattern not in seen_patterns:
            seen_patterns.add(chain.anti_pattern)
            anti_patterns.append({
                'pattern': chain.anti_pattern,
                'cause': chain.root_cause,
                'example': chain.error_message[:100]
            })
        if chain.fix_method:
            fix_methods[chain.fix_method] = fix_methods.get(chain.fix_method, 0) + 1

    avg_steps = sum(c.steps_to_fix for c in resolved) / len(resolved) if resolved else 0

    return {
        "total": len(chains),
        "resolved": len(resolved),
        "unresolved": len(unresolved),
        "resolution_rate": len(resolved) / len(chains) if chains else 0,
        "avg_steps_to_fix": round(avg_steps, 1),
        "by_cause": by_cause,
        "fix_methods": fix_methods,
        "anti_patterns": anti_patterns
    }


def format_text_output(chains: List[ErrorFixChain], analysis: dict) -> str:
    """Format error-fix chains as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("ERROR-FIX CHAIN ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(f"  Total errors: {analysis['total']}")
    lines.append(f"  Resolved: {analysis['resolved']}")
    lines.append(f"  Unresolved: {analysis['unresolved']}")
    lines.append(f"  Resolution rate: {analysis.get('resolution_rate', 0):.1%}")
    lines.append(f"  Avg steps to fix: {analysis.get('avg_steps_to_fix', 0)}")
    lines.append("")

    if analysis['by_cause']:
        lines.append("BY ROOT CAUSE:")
        for cause, count in sorted(analysis['by_cause'].items(), key=lambda x: -x[1]):
            lines.append(f"  {cause}: {count}")
        lines.append("")

    if analysis.get('anti_patterns'):
        lines.append("ANTI-PATTERNS IDENTIFIED:")
        for ap in analysis['anti_patterns']:
            lines.append(f"  ❌ {ap['pattern']}")
            lines.append(f"     Cause: {ap['cause']}")
            lines.append(f"     Example: {ap['example']}")
        lines.append("")

    if analysis.get('fix_methods'):
        lines.append("FIX METHODS USED:")
        for method, count in sorted(analysis['fix_methods'].items(), key=lambda x: -x[1]):
            lines.append(f"  {method}: {count}")
        lines.append("")

    lines.append("DETAILED CHAINS:")
    lines.append("-" * 40)
    for chain in chains:
        status = "✓" if chain.is_resolved else "✗"
        lines.append(f"  [{status}] Error at entry {chain.error_entry}:")
        lines.append(f"    Message: {chain.error_message[:100]}")
        if chain.error_message_field:
            lines.append(f"    ErrorField: {chain.error_message_field[:100]}")
        lines.append(f"    Root cause: {chain.root_cause}")
        if chain.anti_pattern:
            lines.append(f"    Anti-pattern: {chain.anti_pattern}")
        if chain.is_resolved:
            lines.append(f"    Fix: {chain.fix_method} at entry {chain.fix_entry} ({chain.steps_to_fix} steps)")
            if chain.fix_description:
                lines.append(f"    Fix detail: {chain.fix_description[:100]}")
            if chain.fix_edit_changes:
                lines.append(f"    Edit changes: {len(chain.fix_edit_changes)} edit(s)")
                for ec in chain.fix_edit_changes[:2]:
                    old_preview = ec.get('oldText', '')[:80].replace('\n', ' ')
                    new_preview = ec.get('newText', '')[:80].replace('\n', ' ')
                    lines.append(f"      old: '{old_preview}'")
                    lines.append(f"      new: '{new_preview}'")
            if chain.prevention:
                lines.append(f"    Prevention: {chain.prevention}")
        else:
            lines.append(f"    Status: UNRESOLVED")
        lines.append("")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_error_fix_chains.py <session.html> [--output-format json|text]")
        sys.exit(1)

    html_path = sys.argv[1]
    output_format = 'text'

    if '--output-format' in sys.argv:
        idx = sys.argv.index('--output-format')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not Path(html_path).exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)

    try:
        chains = extract_error_fix_chains(html_path)
        analysis = analyze_chains(chains)

        if output_format == 'json':
            result = {
                'analysis': analysis,
                'chains': [asdict(c) for c in chains]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(chains, analysis))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
