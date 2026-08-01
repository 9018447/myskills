#!/usr/bin/env python3
"""
Extract successful workflow sequences from pi session HTML exports.

Identifies the ordered sequence of actions that led to a successful outcome,
which can be captured as a new skill.

Usage:
    python extract_workflow.py <session.html> [--output-format json|text]
"""

import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Optional

from parse_session import decode_session_html, extract_text_from_content


@dataclass
class WorkflowStep:
    """A single step in a workflow sequence."""
    entry_index: int
    step_number: int
    action: str  # read, write, edit, bash, grep, etc.
    description: str  # What was done
    target: str  # File or resource acted upon
    result: str  # What happened (success/failure)
    is_key_step: bool = False  # Is this a critical step?


@dataclass
class WorkflowSequence:
    """A complete workflow sequence from goal to completion."""
    goal: str
    domain: str  # config, code-gen, debugging, etc.
    start_entry: int
    end_entry: int
    steps: List[WorkflowStep] = field(default_factory=list)
    success: bool = False
    tools_used: List[str] = field(default_factory=list)
    files_acted_on: List[str] = field(default_factory=list)
    errors_encountered: int = 0
    key_patterns: List[str] = field(default_factory=list)  # Reusable patterns


def extract_goal_from_messages(entries: list) -> str:
    """Extract the user's goal from early messages."""
    for entry in entries[:10]:
        msg = entry.get('message', {})
        if msg.get('role') != 'user':
            continue
        content = extract_text_from_content(msg.get('content', ''))
        # Skip skill loading content
        if '<skill name=' in content:
            continue
        if len(content) > 20:
            return content[:300]
    return "Unknown goal"


def detect_domain(entries: list) -> str:
    """Detect the domain of the workflow."""
    content_sample = []
    for entry in entries[:20]:
        msg = entry.get('message', {})
        content = extract_text_from_content(msg.get('content', ''))
        content_sample.append(content[:200])

    full_text = ' '.join(content_sample).lower()

    if any(kw in full_text for kw in ['config', 'provider', 'model', 'settings']):
        return 'configuration'
    if any(kw in full_text for kw in ['debug', 'error', 'fix', 'crash', 'traceback']):
        return 'debugging'
    if any(kw in full_text for kw in ['create', 'write', 'generate', 'build']):
        return 'code-generation'
    if any(kw in full_text for kw in ['test', 'assert', 'verify', 'check']):
        return 'testing'
    if any(kw in full_text for kw in ['refactor', 'rename', 'move', 'reorganize']):
        return 'refactoring'
    return 'general'


def is_success_indicator(text: str) -> bool:
    """Check if text indicates success."""
    indicators = [
        'Successfully', 'complete', 'done', 'fixed', 'works',
        'passed', 'success', '完成', '成功', '好了', '可以了'
    ]
    return any(ind in text for ind in indicators)


def extract_workflow_steps(entries: list, start: int = 0, end: int = None) -> List[WorkflowStep]:
    """Extract ordered workflow steps from entries."""
    if end is None:
        end = len(entries)

    steps = []
    step_num = 0
    tools_used = set()
    files_acted = set()
    error_count = 0
    last_edit_file = ""

    for i in range(start, min(end, len(entries))):
        entry = entries[i]
        msg = entry.get('message', {})
        role = msg.get('role', '')

        if role != 'toolResult':
            continue

        tool_name = msg.get('toolName', '')
        is_error = msg.get('isError', False)
        result = extract_text_from_content(msg.get('content', ''))

        if is_error:
            error_count += 1
            continue

        # Get the tool call arguments
        tool_call_id = msg.get('toolCallId', '')
        args = {}
        for j in range(max(0, i - 5), i):
            prev = entries[j]
            prev_content = prev.get('message', {}).get('content', [])
            if isinstance(prev_content, list):
                for item in prev_content:
                    if isinstance(item, dict) and item.get('type') == 'toolCall':
                        if item.get('id') == tool_call_id:
                            args = item.get('arguments', {})
                            break

        # Build step description
        description = ""
        target = ""
        is_key = False

        if tool_name == 'read':
            target = args.get('path', '')
            description = f"Read {target}"
        elif tool_name == 'write':
            target = args.get('path', '')
            description = f"Write {target}"
            is_key = True
            last_edit_file = target
        elif tool_name == 'edit':
            target = args.get('path', '')
            edits = args.get('edits', [])
            desc = f"Edit {target}"
            if edits:
                desc += f" ({len(edits)} edit(s))"
            description = desc
            is_key = True
            last_edit_file = target
        elif tool_name == 'bash':
            cmd = args.get('command', '')[:100]
            description = f"Run: {cmd}"
            target = cmd
        elif tool_name == 'grep':
            pattern = args.get('pattern', '')
            search_path = args.get('path', '.')
            description = f"Search for '{pattern}' in {search_path}"
            target = search_path
        elif tool_name == 'ls':
            path = args.get('path', '.')
            description = f"List {path}"
            target = path
        else:
            description = f"{tool_name} call"
            target = str(args)[:100]

        # Check if result indicates success
        result_preview = result[:100] if result else ""
        has_success = is_success_indicator(result)

        step = WorkflowStep(
            entry_index=i,
            step_number=step_num,
            action=tool_name,
            description=description,
            target=target,
            result=result_preview,
            is_key_step=is_key
        )

        steps.append(step)
        tools_used.add(tool_name)
        if target and '/' in target:
            files_acted.add(target.split(':')[0])  # Remove line numbers

        step_num += 1

    return steps


def detect_anti_patterns(entries: list, start: int, end: int) -> List[str]:
    """Detect anti-patterns from repeated failed approaches."""
    anti_patterns = []
    seen = set()  # Deduplicate

    # Track repeated edits to same file (sign of iterative fixing)
    edit_counts = {}
    for i in range(start, min(end, len(entries))):
        entry = entries[i]
        msg = entry.get('message', {})
        if msg.get('role') != 'toolResult':
            continue
        if msg.get('toolName') in ('edit', 'write') and not msg.get('isError'):
            tool_call_id = msg.get('toolCallId', '')
            for j in range(max(0, i - 5), i):
                prev = entries[j]
                prev_content = prev.get('message', {}).get('content', [])
                if isinstance(prev_content, list):
                    for item in prev_content:
                        if isinstance(item, dict) and item.get('type') == 'toolCall':
                            if item.get('id') == tool_call_id:
                                path = item.get('arguments', {}).get('path', '')
                                edit_counts[path] = edit_counts.get(path, 0) + 1

    for path, count in edit_counts.items():
        if count > 3:
            key = f"multi-edit:{path}"
            if key not in seen:
                seen.add(key)
                anti_patterns.append(f"Multiple edits to {path} ({count}x) — possible iterative debugging, consider writing once")

    return anti_patterns


def extract_workflows(html_path: str) -> List[WorkflowSequence]:
    """Extract all workflow sequences from session file."""
    data = decode_session_html(html_path)
    entries = data.get('entries', [])
    workflows = []

    # For now, extract the main workflow (whole session)
    # Could be extended to detect multiple workflows
    goal = extract_goal_from_messages(entries)
    domain = detect_domain(entries)

    # Find start (after initial setup)
    start = 0
    for i, entry in enumerate(entries[:10]):
        msg = entry.get('message', {})
        if msg.get('role') == 'user':
            start = i
            break

    steps = extract_workflow_steps(entries, start)
    anti_patterns = detect_anti_patterns(entries, start, len(entries))

    tools_used = list(set(s.action for s in steps))
    files_acted = list(set(s.target for s in steps if s.target and '/' in s.target))

    # Check if session ended successfully (last few entries)
    final_entries = entries[-5:]
    success = any(
        is_success_indicator(extract_text_from_content(e.get('message', {}).get('content', '')))
        for e in final_entries
    )

    workflow = WorkflowSequence(
        goal=goal,
        domain=domain,
        start_entry=start,
        end_entry=len(entries) - 1,
        steps=steps,
        success=success,
        tools_used=tools_used,
        files_acted_on=files_acted,
        errors_encountered=sum(1 for s in steps if 'error' in s.result.lower()),
        key_patterns=anti_patterns
    )

    workflows.append(workflow)
    return workflows


def format_text_output(workflows: List[WorkflowSequence]) -> str:
    """Format workflows as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("WORKFLOW SEQUENCE ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    for wf in workflows:
        lines.append(f"GOAL: {wf.goal[:200]}")
        lines.append(f"DOMAIN: {wf.domain}")
        lines.append(f"SUCCESS: {'Yes' if wf.success else 'No'}")
        lines.append(f"ENTRIES: {wf.start_entry} → {wf.end_entry}")
        lines.append("")

        lines.append("TOOLS USED:")
        for tool in wf.tools_used:
            lines.append(f"  - {tool}")
        lines.append("")

        if wf.files_acted_on:
            lines.append("FILES ACTED ON:")
            for f in wf.files_acted_on[:15]:
                lines.append(f"  - {f}")
            lines.append("")

        if wf.key_patterns:
            lines.append("ANTI-PATTERNS DETECTED:")
            for p in wf.key_patterns:
                lines.append(f"  ⚠ {p}")
            lines.append("")

        lines.append("KEY STEPS (edits/writes only):")
        lines.append("-" * 40)
        key_steps = [s for s in wf.steps if s.is_key_step]
        for step in key_steps[:20]:
            lines.append(f"  Step {step.step_number}: {step.description}")
            if step.result:
                lines.append(f"    Result: {step.result[:80]}")
        lines.append("")

        lines.append(f"TOTAL STEPS: {len(wf.steps)}")
        lines.append(f"ERRORS ENCOUNTERED: {wf.errors_encountered}")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_workflow.py <session.html> [--output-format json|text]")
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
        workflows = extract_workflows(html_path)

        if output_format == 'json':
            result = {
                'workflows': [asdict(w) for w in workflows]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(workflows))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
