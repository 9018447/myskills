#!/usr/bin/env python3
"""
Extract and analyze errors from pi session HTML exports.

Usage:
    python extract_errors.py <session.html> [--output-format json|text|csv]

Output includes:
- All error messages with context
- Error categories (API, rendering, type/lsp, logic, ux, unknown)
- Error locations (entry indices)
- Suggested fixes (if patterns match)
"""

import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List

from parse_session import decode_session_html, extract_text_from_content


@dataclass
class DetailedError:
    message: str
    category: str
    entry_index: int
    role: str  # user, assistant, tool
    context: str
    file_mentioned: str = ""
    line_number: str = ""
    severity: str = "error"  # error, warning, info
    suggested_fix: str = ""
    related_tool: str = ""


# Error pattern definitions with categories and suggested fixes
ERROR_PATTERNS = [
    {
        'pattern': r'Cannot find module \'(@?[\w/-]+)\'',
        'category': 'type/lsp',
        'severity': 'warning',
        'fix_template': 'Add // @ts-expect-error before import or check module resolution'
    },
    {
        'pattern': r'Rendered line (\d+) exceeds terminal width \((\d+) > (\d+)\)',
        'category': 'rendering',
        'severity': 'error',
        'fix_template': 'Use ASCII borders and truncateToWidth() for TUI elements'
    },
    {
        'pattern': r'Unused \'@ts-expect-error\' directive',
        'category': 'type/lsp',
        'severity': 'info',
        'fix_template': 'Remove unused @ts-expect-error directive'
    },
    {
        'pattern': r'String literal "(.+?)" repeated (\d+) times',
        'category': 'lint',
        'severity': 'warning',
        'fix_template': 'Extract repeated string to a named constant'
    },
    {
        'pattern': r'🔴 STOP.+?Potential secret.+?in (.+?):(\d+)',
        'category': 'security',
        'severity': 'error',
        'fix_template': 'Move secrets to environment variables'
    },
    {
        'pattern': r'▲ L\d+ no-any-type\s+Avoid \'any\' type',
        'category': 'lint',
        'severity': 'warning',
        'fix_template': 'Use specific types instead of any'
    },
    {
        'pattern': r'\[object Object\]',
        'category': 'API',
        'severity': 'error',
        'fix_template': 'Check API parameter format - may need string instead of object'
    },
    {
        'pattern': r'object-template',
        'category': 'API',
        'severity': 'error',
        'fix_template': 'Verify template data structure matches expected format'
    },
    {
        'pattern': r'Error:\s*(.+?)(?:\n|$)',
        'category': 'unknown',
        'severity': 'error',
        'fix_template': ''
    },
    {
        'pattern': r'●\s+L(\d+)\s+(\w+:\d+)\s+(.+)',
        'category': 'lsp',
        'severity': 'warning',
        'fix_template': 'Fix the diagnostic issue reported by LSP'
    },
]


def extract_file_and_line(text: str) -> tuple:
    """Extract filename and line number from error context."""
    patterns = [
        r'(\w+\.ts):(\d+)',
        r'in (\w+\.py):(\d+)',
        r'at (\w+\.\w+):(\d+)',
        r'L(\d+) (\w+\.ts)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if groups[0].isdigit():
                return groups[1], groups[0]
            return groups[0], groups[1]
    return "", ""


def is_skill_content(text: str, msg: dict) -> bool:
    """Detect if text is skill content being loaded, not runtime output.
    
    Skill content contains error keywords in documentation/examples,
    not actual runtime errors. We filter these to avoid false positives.
    """
    role = msg.get('role', 'user')
    
    # Skill loading: <skill> tags or SKILL.md content
    if '<skill name=' in text:
        return True
    if re.search(r'SKILL\.md', text) and len(text) > 1000:
        return True
    
    # Long markdown content with table cells mentioning errors
    # (likely documentation, not runtime output)
    if len(text) > 2000 and text.count('| ') > 5 and 'error' in text.lower():
        return True
    
    # Content that looks like reference docs (headers + tables + code blocks)
    if '## ' in text and '| ' in text and '```' in text and len(text) > 1000:
        return True
    
    # Tool result that read a markdown file (error patterns in docs)
    if role == 'toolResult' and msg.get('toolName') == 'read':
        if text.count('\n') > 20 and ('# ' in text or '| ' in text):
            # It's a markdown file being read, skip error patterns in it
            return True
    
    return False


def find_errors_in_entry(entry: dict, entry_index: int) -> List[DetailedError]:
    """Extract all errors from a single session entry."""
    errors = []
    msg = entry.get('message', {})
    role = msg.get('role', '')
    content = msg.get('content', '')
    text = extract_text_from_content(content)

    if not text:
        return errors
    
    # Filter out skill content to avoid false positives
    if is_skill_content(text, msg):
        return errors

    # Check each error pattern
    for pattern_info in ERROR_PATTERNS:
        pattern = pattern_info['pattern']
        for match in re.finditer(pattern, text):
            error_msg = match.group(0)

            # Get full message if available
            if match.lastindex:
                error_msg = match.group(match.lastindex)

            file_name, line_num = extract_file_and_line(text)

            errors.append(DetailedError(
                message=error_msg,
                category=pattern_info['category'],
                entry_index=entry_index,
                role=role,
                context=text[:300],
                file_mentioned=file_name,
                line_number=line_num,
                severity=pattern_info['severity'],
                suggested_fix=pattern_info['fix_template']
            ))

    # Check for tool errors
    if role == 'tool' and msg.get('isError'):
        tool_name = msg.get('toolName', '')
        errors.append(DetailedError(
            message=text[:200],
            category='tool',
            entry_index=entry_index,
            role='tool',
            context=f"Tool: {tool_name}",
            related_tool=tool_name,
            severity='error'
        ))

    return errors


def analyze_error_patterns(errors: List[DetailedError]) -> dict:
    """Analyze error patterns and provide statistics."""
    if not errors:
        return {"total": 0, "by_category": {}, "by_severity": {}, "most_common": []}

    by_category = {}
    by_severity = {}
    message_counts = {}

    for error in errors:
        by_category[error.category] = by_category.get(error.category, 0) + 1
        by_severity[error.severity] = by_severity.get(error.severity, 0) + 1

        # Normalize message for counting
        normalized = re.sub(r'[Ll]\d+', 'L...', error.message[:50])
        message_counts[normalized] = message_counts.get(normalized, 0) + 1

    # Find most common error patterns
    most_common = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total": len(errors),
        "by_category": by_category,
        "by_severity": by_severity,
        "most_common": [{"pattern": p, "count": c} for p, c in most_common],
        "files_affected": list(set(e.file_mentioned for e in errors if e.file_mentioned))
    }


def extract_errors(html_path: str) -> tuple:
    """Extract all errors from session file."""
    data = decode_session_html(html_path)
    entries = data.get('entries', [])
    all_errors = []

    for i, entry in enumerate(entries):
        errors = find_errors_in_entry(entry, i)
        all_errors.extend(errors)

    return all_errors, analyze_error_patterns(all_errors)


def format_text_output(errors: List[DetailedError], analysis: dict) -> str:
    """Format errors as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("ERROR ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("SUMMARY:")
    lines.append(f"  Total errors: {analysis['total']}")
    lines.append(f"  Files affected: {', '.join(analysis.get('files_affected', []))}")
    lines.append("")

    # By category
    if analysis['by_category']:
        lines.append("BY CATEGORY:")
        for cat, count in sorted(analysis['by_category'].items()):
            lines.append(f"  {cat}: {count}")
        lines.append("")

    # By severity
    if analysis['by_severity']:
        lines.append("BY SEVERITY:")
        for sev, count in sorted(analysis['by_severity'].items()):
            lines.append(f"  {sev}: {count}")
        lines.append("")

    # Most common
    if analysis.get('most_common'):
        lines.append("MOST COMMON PATTERNS:")
        for item in analysis['most_common']:
            lines.append(f"  [{item['count']}x] {item['pattern']}")
        lines.append("")

    # Detailed errors
    if errors:
        lines.append("DETAILED ERRORS:")
        lines.append("-" * 40)
        for error in errors:
            lines.append(f"  Entry {error.entry_index} [{error.severity}] [{error.category}]")
            lines.append(f"    Role: {error.role}")
            lines.append(f"    Message: {error.message[:150]}")
            if error.file_mentioned:
                lines.append(f"    File: {error.file_mentioned}:{error.line_number}")
            if error.suggested_fix:
                lines.append(f"    Fix: {error.suggested_fix}")
            if error.related_tool:
                lines.append(f"    Tool: {error.related_tool}")
            lines.append("")

    return '\n'.join(lines)


def format_csv_output(errors: List[DetailedError]) -> str:
    """Format errors as CSV."""
    lines = ["entry_index,category,severity,role,message,file,line,suggested_fix"]
    for error in errors:
        msg = error.message.replace('"', '""')[:100]
        fix = error.suggested_fix.replace('"', '""')
        lines.append(f'{error.entry_index},"{error.category}","{error.severity}","{error.role}","{msg}","{error.file_mentioned}","{error.line_number}","{fix}"')
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_errors.py <session.html> [--output-format json|text|csv]")
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
        errors, analysis = extract_errors(html_path)

        if output_format == 'json':
            result = {
                'analysis': analysis,
                'errors': [asdict(e) for e in errors]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif output_format == 'csv':
            print(format_csv_output(errors))
        else:
            print(format_text_output(errors, analysis))

    except Exception as e:
        print(f"Error extracting errors: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
