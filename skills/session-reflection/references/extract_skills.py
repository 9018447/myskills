#!/usr/bin/env python3
"""
Extract skill invocations from pi session HTML exports.

Usage:
    python extract_skills.py <session.html> [--output-format json|text]

Output includes:
- Skills loaded/invoked
- Skill locations
- Context around skill invocations
- Skill effectiveness indicators
"""

import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List

from parse_session import decode_session_html, extract_text_from_content


@dataclass
class SkillUsage:
    name: str
    location: str
    entry_index: int
    timestamp: str
    context: str  # Surrounding text
    was_effective: bool = True  # Did it help achieve the goal?
    issues: List[str] = None  # Any issues with the skill


def find_skill_tags(text: str) -> List[dict]:
    """Find skill invocations in <skill> tags."""
    skills = []
    pattern = r'<skill\s+name="([^"]+)"\s+location="([^"]+)"(?:\s+[^>]*)?>'
    for match in re.finditer(pattern, text):
        skills.append({
            'name': match.group(1),
            'location': match.group(2)
        })
    return skills


def find_skill_paths(text: str) -> List[dict]:
    """Find skill references by path patterns."""
    skills = []
    # Pattern for skill paths like ~/.agents/skills/<name>/SKILL.md
    patterns = [
        r'~/\.agents/skills/(\w+)/SKILL\.md',
        r'~/.pi/agent/skills/(\w+)/SKILL\.md',
        r'skills/(\w+)/SKILL\.md',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            skills.append({
                'name': match.group(1),
                'location': match.group(0)
            })
    return skills


def find_skill_mentions(text: str) -> List[str]:
    """Find skill name mentions in text."""
    mentions = []
    # Look for skill names in backticks or quotes
    patterns = [
        r'`(\w+(?:-\w+)*)`',  # kebab-case in backticks
        r'"(\w+(?:-\w+)*skill)"',  # words ending in skill
        r'skill[:\s]+(\w+)',  # skill: <name> or skill <name>
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            # Filter common false positives
            if name not in ['the', 'a', 'an', 'is', 'was', 'this', 'that']:
                mentions.append(name)
    return list(set(mentions))


def check_skill_effectiveness(entry_index: int, entries: list) -> tuple:
    """Check if skill usage led to positive outcomes."""
    # Look for success indicators in subsequent entries
    success_indicators = ['success', 'fixed', 'works', 'done', 'complete', '完成', '成功']
    error_indicators = ['error', 'failed', 'broken', 'doesn\'t work', '失败', '报错']

    context_window = entries[max(0, entry_index-2):entry_index+5]
    has_success = False
    has_errors = False
    issues = []

    for entry in context_window:
        msg = entry.get('message', {})
        content = extract_text_from_content(msg.get('content', ''))
        content_lower = content.lower()

        if any(ind in content_lower for ind in success_indicators):
            has_success = True
        if any(ind in content_lower for ind in error_indicators):
            has_errors = True
            # Extract the error context
            for line in content.split('\n'):
                if any(ind in line.lower() for ind in error_indicators):
                    issues.append(line.strip()[:100])

    if has_success and not has_errors:
        return True, []
    elif has_errors:
        return False, issues
    return True, []  # Default to effective if no clear signal


def extract_skills(html_path: str) -> List[SkillUsage]:
    """Extract all skill invocations from session file."""
    data = decode_session_html(html_path)
    entries = data.get('entries', [])
    skills = []
    seen = set()  # Avoid duplicates

    for i, entry in enumerate(entries):
        entry_type = entry.get('type', '')
        if entry_type != 'message':
            continue

        msg = entry.get('message', {})
        content = extract_text_from_content(msg.get('content', ''))
        if not content:
            continue

        timestamp = entry.get('timestamp', '')

        # Find <skill> tags
        for skill in find_skill_tags(content):
            key = f"{skill['name']}:{i}"
            if key not in seen:
                seen.add(key)
                effective, issues = check_skill_effectiveness(i, entries)
                skills.append(SkillUsage(
                    name=skill['name'],
                    location=skill['location'],
                    entry_index=i,
                    timestamp=timestamp,
                    context=content[:300],
                    was_effective=effective,
                    issues=issues if issues else None
                ))

        # Find skill paths
        for skill in find_skill_paths(content):
            key = f"{skill['name']}:{i}"
            if key not in seen:
                seen.add(key)
                effective, issues = check_skill_effectiveness(i, entries)
                skills.append(SkillUsage(
                    name=skill['name'],
                    location=skill['location'],
                    entry_index=i,
                    timestamp=timestamp,
                    context=content[:300],
                    was_effective=effective,
                    issues=issues if issues else None
                ))

    return skills


def analyze_skills(skills: List[SkillUsage]) -> dict:
    """Analyze skill usage patterns."""
    if not skills:
        return {
            "total": 0,
            "unique_skills": 0,
            "skills_used": [],
            "by_name": {},
            "effective_count": 0,
            "effectiveness_rate": 0,
            "issues": []
        }

    by_name = {}
    effective_count = 0
    issues_found = []

    for skill in skills:
        by_name[skill.name] = by_name.get(skill.name, 0) + 1
        if skill.was_effective:
            effective_count += 1
        if skill.issues:
            issues_found.extend(skill.issues)

    return {
        "total": len(skills),
        "unique_skills": len(by_name),
        "skills_used": list(by_name.keys()),
        "by_name": by_name,
        "effective_count": effective_count,
        "effectiveness_rate": effective_count / len(skills) if skills else 0,
        "issues": issues_found[:10]  # Top 10 issues
    }


def format_text_output(skills: List[SkillUsage], analysis: dict) -> str:
    """Format skill usage as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("SKILL USAGE ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("SUMMARY:")
    lines.append(f"  Total invocations: {analysis['total']}")
    lines.append(f"  Unique skills: {analysis['unique_skills']}")
    lines.append(f"  Effective uses: {analysis['effective_count']}")
    lines.append(f"  Effectiveness rate: {analysis['effectiveness_rate']:.1%}")
    lines.append("")

    # Skills used
    if analysis['skills_used']:
        lines.append("SKILLS USED:")
        for name, count in analysis['by_name'].items():
            lines.append(f"  - {name} ({count}x)")
        lines.append("")

    # Issues
    if analysis.get('issues'):
        lines.append("ISSUES FOUND:")
        for issue in analysis['issues']:
            lines.append(f"  - {issue}")
        lines.append("")

    # Detailed invocations
    if skills:
        lines.append("DETAILED INVOCATIONS:")
        lines.append("-" * 40)
        for skill in skills:
            status = "✓" if skill.was_effective else "✗"
            lines.append(f"  [{status}] Entry {skill.entry_index}: {skill.name}")
            lines.append(f"    Location: {skill.location}")
            if skill.issues:
                for issue in skill.issues:
                    lines.append(f"    Issue: {issue}")
            lines.append("")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_skills.py <session.html> [--output-format json|text]")
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
        skills = extract_skills(html_path)
        analysis = analyze_skills(skills)

        if output_format == 'json':
            result = {
                'analysis': analysis,
                'skills': [asdict(s) for s in skills]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(skills, analysis))

    except Exception as e:
        print(f"Error extracting skills: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
