#!/usr/bin/env python3
"""
Extract and analyze tool calls from pi session HTML exports.

Usage:
    python extract_tool_calls.py <session.html> [--output-format json|text|csv] [--tool-name <name>]

Output includes:
- All tool invocations with arguments
- Tool results (success/error)
- Tool usage statistics
- Duration estimates (based on entry gaps)
"""

import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime

from parse_session import decode_session_html, extract_text_from_content


@dataclass
class DetailedToolCall:
    tool_name: str
    arguments: dict
    entry_index: int
    result: Optional[str] = None
    result_preview: str = ""
    is_error: bool = False
    error_message: str = ""
    timestamp: str = ""
    has_file_operation: bool = False
    file_path: str = ""
    operation_type: str = ""  # read, write, edit, search, execute


# Tool operation patterns
TOOL_PATTERNS = {
    'read': {'args_key': 'path', 'op_type': 'read'},
    'write': {'args_key': 'path', 'op_type': 'write'},
    'edit': {'args_key': 'path', 'op_type': 'edit'},
    'bash': {'args_key': 'command', 'op_type': 'execute'},
    'grep': {'args_key': 'pattern', 'op_type': 'search'},
    'find': {'args_key': 'pattern', 'op_type': 'search'},
    'ls': {'args_key': 'path', 'op_type': 'list'},
    'context7_resolve_library_id': {'args_key': 'libraryName', 'op_type': 'lookup'},
    'context7_get_library_docs': {'args_key': 'libraryName', 'op_type': 'lookup'},
}


def extract_file_path(args: dict, tool_name: str) -> str:
    """Extract file path from tool arguments."""
    if tool_name in TOOL_PATTERNS:
        key = TOOL_PATTERNS[tool_name]['args_key']
        value = args.get(key, '')
        if isinstance(value, str) and ('/' in value or '.' in value):
            return value
    return ""


def classify_operation(tool_name: str, args: dict) -> str:
    """Classify the type of operation."""
    if tool_name in TOOL_PATTERNS:
        return TOOL_PATTERNS[tool_name]['op_type']
    return "unknown"


def find_tool_calls_in_entry(entry: dict, entry_index: int) -> List[dict]:
    """Extract toolCall calls from an entry."""
    tool_calls = []
    msg = entry.get('message', {})
    content = msg.get('content', [])

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'toolCall':
                tool_calls.append({
                    'name': item.get('name', ''),
                    'arguments': item.get('arguments', {}),
                    'tool_use_id': item.get('id', ''),
                    'entry_index': entry_index
                })

    return tool_calls


def find_tool_result(entry: dict) -> Optional[dict]:
    """Extract tool result from an entry."""
    msg = entry.get('message', {})
    if msg.get('role') != 'toolResult':
        return None

    return {
        'tool_call_id': msg.get('toolCallId', ''),
        'tool_name': msg.get('toolName', ''),
        'content': extract_text_from_content(msg.get('content', '')),
        'is_error': msg.get('isError', False),
        'timestamp': entry.get('timestamp', '')
    }


def extract_tool_calls(html_path: str, filter_tool: str = None) -> tuple:
    """Extract all tool calls from session file."""
    data = decode_session_html(html_path)
    entries = data.get('entries', [])

    all_calls = []
    pending_calls = {}  # tool_use_id -> call_info

    for i, entry in enumerate(entries):
        entry_type = entry.get('type', '')
        if entry_type != 'message':
            continue

        msg = entry.get('message', {})
        role = msg.get('role', '')

        # Extract tool_use calls
        if role == 'assistant':
            tool_uses = find_tool_calls_in_entry(entry, i)
            for tu in tool_uses:
                if filter_tool and tu['name'] != filter_tool:
                    continue
                pending_calls[tu['tool_use_id']] = DetailedToolCall(
                    tool_name=tu['name'],
                    arguments=tu['arguments'],
                    entry_index=tu['entry_index'],
                    timestamp=entry.get('timestamp', ''),
                    has_file_operation=tu['name'] in ['read', 'write', 'edit', 'grep', 'find'],
                    file_path=extract_file_path(tu['arguments'], tu['name']),
                    operation_type=classify_operation(tu['name'], tu['arguments'])
                )

        # Extract tool results
        elif role == 'toolResult':
            result = find_tool_result(entry)
            if result and result['tool_call_id'] in pending_calls:
                call = pending_calls[result['tool_call_id']]
                call.result = result['content']
                call.result_preview = result['content'][:200] if result['content'] else ""
                call.is_error = result['is_error']
                if result['is_error']:
                    call.error_message = result['content'][:200] if result['content'] else "Unknown error"
                all_calls.append(call)
                del pending_calls[result['tool_call_id']]

    # Add any calls without results
    for call in pending_calls.values():
        all_calls.append(call)

    # Sort by entry index
    all_calls.sort(key=lambda x: x.entry_index)

    return all_calls


def analyze_tool_usage(calls: List[DetailedToolCall]) -> dict:
    """Analyze tool usage statistics."""
    if not calls:
        return {"total": 0, "successful": 0, "failed": 0, "by_tool": {}, "file_operations": [], "files_touched": []}

    by_tool = {}
    file_ops = []
    errors = []

    for call in calls:
        by_tool[call.tool_name] = by_tool.get(call.tool_name, 0) + 1

        if call.has_file_operation and call.file_path:
            file_ops.append({
                'tool': call.tool_name,
                'path': call.file_path,
                'operation': call.operation_type,
                'entry': call.entry_index
            })

        if call.is_error:
            errors.append({
                'tool': call.tool_name,
                'entry': call.entry_index,
                'error': call.error_message[:100]
            })

    return {
        "total": len(calls),
        "successful": sum(1 for c in calls if not c.is_error),
        "failed": sum(1 for c in calls if c.is_error),
        "by_tool": by_tool,
        "file_operations": file_ops,
        "errors": errors,
        "files_touched": list(set(f['path'] for f in file_ops))
    }


def format_text_output(calls: List[DetailedToolCall], analysis: dict) -> str:
    """Format tool calls as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("TOOL CALLS ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("SUMMARY:")
    lines.append(f"  Total calls: {analysis['total']}")
    lines.append(f"  Successful: {analysis['successful']}")
    lines.append(f"  Failed: {analysis['failed']}")
    lines.append("")

    # By tool
    if analysis['by_tool']:
        lines.append("BY TOOL:")
        for tool, count in sorted(analysis['by_tool'].items()):
            lines.append(f"  {tool}: {count}")
        lines.append("")

    # Files touched
    if analysis.get('files_touched'):
        lines.append("FILES TOUCHED:")
        for f in sorted(analysis['files_touched']):
            lines.append(f"  - {f}")
        lines.append("")

    # Errors
    if analysis.get('errors'):
        lines.append("TOOL ERRORS:")
        for err in analysis['errors']:
            lines.append(f"  [{err['tool']}] Entry {err['entry']}: {err['error']}")
        lines.append("")

    # Detailed calls
    lines.append("DETAILED CALLS:")
    lines.append("-" * 40)
    for call in calls:
        status = "ERROR" if call.is_error else "OK"
        lines.append(f"  Entry {call.entry_index} [{status}] {call.tool_name}")
        lines.append(f"    Operation: {call.operation_type}")

        # Show arguments (abbreviated)
        if call.arguments:
            args_str = json.dumps(call.arguments, ensure_ascii=False)
            if len(args_str) > 150:
                args_str = args_str[:150] + "..."
            lines.append(f"    Args: {args_str}")

        if call.file_path:
            lines.append(f"    File: {call.file_path}")

        if call.result_preview:
            lines.append(f"    Result: {call.result_preview[:100]}...")

        if call.is_error:
            lines.append(f"    Error: {call.error_message[:100]}")

        lines.append("")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_tool_calls.py <session.html> [--output-format json|text|csv] [--tool-name <name>]")
        sys.exit(1)

    html_path = sys.argv[1]
    output_format = 'text'
    filter_tool = None

    # Parse arguments
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--output-format' and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        elif args[i] == '--tool-name' and i + 1 < len(args):
            filter_tool = args[i + 1]
            i += 2
        else:
            i += 1

    if not Path(html_path).exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)

    try:
        calls = extract_tool_calls(html_path, filter_tool)
        analysis = analyze_tool_usage(calls)

        if output_format == 'json':
            result = {
                'analysis': analysis,
                'calls': [asdict(c) for c in calls]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(calls, analysis))

    except Exception as e:
        print(f"Error extracting tool calls: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
