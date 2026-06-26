#!/usr/bin/env python3
"""
Extract user feedback and requirements from pi session HTML exports.

Usage:
    python extract_user_feedback.py <session.html> [--output-format json|text] [--feedback-only]

Output includes:
- User requirements (initial task)
- User feedback (corrections, issues, suggestions)
- Feedback classification (bug, feature request, UX issue, clarification)
- Timeline of user messages
"""

import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List

from parse_session import decode_session_html, extract_text_from_content


@dataclass
class UserFeedback:
    content: str
    entry_index: int
    timestamp: str
    is_requirement: bool  # True if initial task description
    is_feedback: bool  # True if contains corrections/issues
    feedback_type: str  # bug, feature, ux, clarification, positive, neutral
    keywords: List[str]
    mentions_tool: bool = False
    mentions_error: bool = False
    mentions_skill: bool = False


# Feedback classification keywords
FEEDBACK_PATTERNS = {
    'bug': [
        'doesn\'t work', 'not working', 'error', 'crash', 'bug', 'broken',
        'fails', 'failing', '报错', '崩溃', '出错', '无效', '失败'
    ],
    'feature': [
        'should', 'could', 'want', 'need', 'wish', 'add', '支持', '希望',
        '应该', '需要', '添加', '新增'
    ],
    'ux': [
        'confusing', 'hard to use', 'can\'t find', 'unclear', 'difficult',
        '不方便', '找不到', '不清晰', '难用', '看不懂'
    ],
    'clarification': [
        'what does', 'how to', 'why', 'explain', '什么意思', '怎么', '为什么',
        '解释', '如何'
    ],
    'positive': [
        'works', 'good', 'great', 'perfect', 'thanks', '可以了', '好了',
        '不错', '完美', '谢谢'
    ]
}


def classify_feedback(text: str) -> str:
    """Classify feedback type based on content."""
    text_lower = text.lower()

    # Check each category
    for category, keywords in FEEDBACK_PATTERNS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category

    return 'neutral'


def extract_keywords(text: str) -> List[str]:
    """Extract significant keywords from text."""
    keywords = []

    # Tool names
    tool_names = ['read', 'write', 'edit', 'bash', 'grep', 'find', 'ls',
                  'context7', 'lsp', 'mcp']
    for tool in tool_names:
        if tool in text.lower():
            keywords.append(f'tool:{tool}')

    # File extensions
    ext_pattern = r'\.(\w{1,4})\b'
    for match in re.finditer(ext_pattern, text):
        keywords.append(f'ext:{match.group(1)}')

    # Skill references
    skill_pattern = r'(?:skill|SKILL)\s*[:=]\s*(\w+)'
    for match in re.finditer(skill_pattern, text):
        keywords.append(f'skill:{match.group(1)}')

    # Error indicators
    error_keywords = ['error', '错误', '报错', 'bug', 'issue', '问题']
    for kw in error_keywords:
        if kw in text.lower():
            keywords.append('has:error')
            break

    return list(set(keywords))


def is_requirement_message(text: str, entry_index: int) -> bool:
    """Determine if message is the initial task requirement."""
    # First substantial message is usually the requirement
    if entry_index <= 5 and len(text) > 50:
        # Check if it's a task description (not diagnostic output)
        if not text.startswith('─') and not text.startswith('LSP'):
            return True
    return False


def extract_feedback(html_path: str, feedback_only: bool = False) -> List[UserFeedback]:
    """Extract all user feedback from session file."""
    data = decode_session_html(html_path)
    entries = data.get('entries', [])
    feedback_list = []

    for i, entry in enumerate(entries):
        entry_type = entry.get('type', '')
        if entry_type != 'message':
            continue

        msg = entry.get('message', {})
        if msg.get('role') != 'user':
            continue

        content = extract_text_from_content(msg.get('content', ''))
        if not content or not content.strip():
            continue

        # Skip diagnostic output
        if content.startswith('─') or content.startswith('LSP'):
            continue

        is_req = is_requirement_message(content, i)
        is_fb = classify_feedback(content) != 'neutral'

        if feedback_only and not is_fb:
            continue

        feedback_list.append(UserFeedback(
            content=content,
            entry_index=i,
            timestamp=entry.get('timestamp', ''),
            is_requirement=is_req,
            is_feedback=is_fb,
            feedback_type=classify_feedback(content),
            keywords=extract_keywords(content),
            mentions_tool=any(t in content.lower() for t in ['read', 'write', 'edit', 'bash']),
            mentions_error='error' in content.lower() or '错误' in content,
            mentions_skill='skill' in content.lower()
        ))

    return feedback_list


def analyze_feedback(feedback_list: List[UserFeedback]) -> dict:
    """Analyze feedback patterns."""
    if not feedback_list:
        return {"total": 0, "requirements": [], "by_type": {}}

    by_type = {}
    requirements = []
    issues = []

    for fb in feedback_list:
        by_type[fb.feedback_type] = by_type.get(fb.feedback_type, 0) + 1

        if fb.is_requirement:
            requirements.append(fb.content[:200])

        if fb.is_feedback and fb.feedback_type in ['bug', 'ux']:
            issues.append({
                'entry': fb.entry_index,
                'type': fb.feedback_type,
                'content': fb.content[:150]
            })

    return {
        "total": len(feedback_list),
        "requirements": requirements,
        "by_type": by_type,
        "issues": issues,
        "has_bug_reports": by_type.get('bug', 0) > 0,
        "has_feature_requests": by_type.get('feature', 0) > 0,
        "tool_mentions": sum(1 for f in feedback_list if f.mentions_tool),
        "error_mentions": sum(1 for f in feedback_list if f.mentions_error)
    }


def format_text_output(feedback_list: List[UserFeedback], analysis: dict) -> str:
    """Format feedback as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("USER FEEDBACK ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("SUMMARY:")
    lines.append(f"  Total messages: {analysis['total']}")
    lines.append(f"  Bug reports: {analysis['by_type'].get('bug', 0)}")
    lines.append(f"  Feature requests: {analysis['by_type'].get('feature', 0)}")
    lines.append(f"  UX issues: {analysis['by_type'].get('ux', 0)}")
    lines.append(f"  Positive feedback: {analysis['by_type'].get('positive', 0)}")
    lines.append("")

    # Requirements
    if analysis['requirements']:
        lines.append("INITIAL REQUIREMENTS:")
        for i, req in enumerate(analysis['requirements'], 1):
            lines.append(f"  {i}. {req}")
        lines.append("")

    # Issues
    if analysis.get('issues'):
        lines.append("ISSUES REPORTED:")
        for issue in analysis['issues']:
            lines.append(f"  [{issue['type']}] Entry {issue['entry']}:")
            lines.append(f"    {issue['content']}")
        lines.append("")

    # Detailed messages
    lines.append("ALL USER MESSAGES:")
    lines.append("-" * 40)
    for fb in feedback_list:
        tags = []
        if fb.is_requirement:
            tags.append("REQUIREMENT")
        if fb.is_feedback:
            tags.append(fb.feedback_type.upper())
        tag_str = f" [{', '.join(tags)}]" if tags else ""

        lines.append(f"  Entry {fb.entry_index}{tag_str}:")
        lines.append(f"    {fb.content[:200]}")
        if fb.keywords:
            lines.append(f"    Keywords: {', '.join(fb.keywords[:5])}")
        lines.append("")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_user_feedback.py <session.html> [--output-format json|text] [--feedback-only]")
        sys.exit(1)

    html_path = sys.argv[1]
    output_format = 'text'
    feedback_only = '--feedback-only' in sys.argv

    if '--output-format' in sys.argv:
        idx = sys.argv.index('--output-format')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not Path(html_path).exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)

    try:
        feedback_list = extract_feedback(html_path, feedback_only)
        analysis = analyze_feedback(feedback_list)

        if output_format == 'json':
            result = {
                'analysis': analysis,
                'feedback': [asdict(f) for f in feedback_list]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(feedback_list, analysis))

    except Exception as e:
        print(f"Error extracting feedback: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
