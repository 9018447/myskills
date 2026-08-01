#!/usr/bin/env python3
"""
Parse pi session HTML export files and extract structured data.

Supports the complete Pi session format (v3) including:
- All entry types: message, model_change, thinking_level_change, compaction,
  branch_summary, custom, custom_message, label, session_info
- All message roles: user, assistant, toolResult, bashExecution, custom,
  branchSummary, compactionSummary
- All content blocks: text, thinking, toolCall, image
- Full tree structure with parentId analysis

Usage:
    python parse_session.py <session.html> [--output-format json|text] [--full]

With --full: includes complete tool results, edit diffs, thinking content,
             bash execution output, and compaction summaries
"""

import sys
import json
import re
import base64
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────

@dataclass
class EditChange:
    """A single edit operation (oldText → newText)."""
    old_text: str = ""
    new_text: str = ""
    old_text_preview: str = ""
    new_text_preview: str = ""


@dataclass
class SkillInvocation:
    name: str
    location: str
    entry_index: int
    context: str = ""


@dataclass
class Error:
    message: str
    category: str  # API, rendering, type/lsp, logic, ux, security, lint, unknown
    entry_index: int
    context: str = ""
    fix: str = ""
    error_message_field: str = ""  # From toolResult.errorMessage or assistant.errorMessage


@dataclass
class BashExecution:
    """Bash command execution details (from bashExecution role)."""
    command: str = ""
    output: str = ""            # Truncated preview
    output_full: str = ""       # Full output
    exit_code: Optional[int] = None
    cancelled: bool = False
    truncated: bool = False
    full_output_path: str = ""  # Path to full output file if truncated
    exclude_from_context: bool = False  # !! prefix commands
    entry_index: int = 0
    timestamp: str = ""


@dataclass
class ToolCall:
    name: str
    arguments: dict
    entry_index: int
    result: Optional[str] = None          # Truncated preview (500 chars)
    result_full: Optional[str] = None     # Complete result
    is_error: bool = False
    error_message: str = ""               # From toolResult.errorMessage
    details: Optional[dict] = None        # From toolResult.details
    edit_changes: Optional[List[EditChange]] = None  # For edit operations
    timestamp: str = ""
    tool_call_id: str = ""


@dataclass
class UserMessage:
    content: str
    entry_index: int
    timestamp: str = ""
    is_feedback: bool = False
    has_image: bool = False  # Contains image content


@dataclass
class AssistantMessage:
    content: str
    entry_index: int
    timestamp: str = ""
    has_thinking: bool = False
    thinking_content: str = ""             # Truncated preview (500 chars)
    thinking_content_full: str = ""        # Complete thinking chain
    model: str = ""                        # Model used for this response
    provider: str = ""                     # API provider
    api: str = ""                          # API endpoint name
    usage: Optional[dict] = None           # Token usage stats
    stop_reason: str = ""                  # Why generation stopped
    error_message: str = ""                # Error if stop_reason == "error"
    response_id: str = ""                  # API response ID


@dataclass
class CompactionEntry:
    """Context compaction entry."""
    entry_index: int
    summary: str = ""
    summary_full: str = ""
    tokens_before: int = 0
    first_kept_entry_id: str = ""
    details: Optional[dict] = None
    from_hook: bool = False
    timestamp: str = ""


@dataclass
class BranchSummaryEntry:
    """Branch summary entry (alternative approach abandoned)."""
    entry_index: int
    summary: str = ""
    summary_full: str = ""
    from_id: str = ""  # Entry we branched from
    details: Optional[dict] = None
    from_hook: bool = False
    timestamp: str = ""


@dataclass
class LabelEntry:
    """User-defined bookmark/marker."""
    entry_index: int
    target_id: str = ""
    label: str = ""
    timestamp: str = ""


@dataclass
class SessionInfoEntry:
    """Session display name."""
    entry_index: int
    name: str = ""
    timestamp: str = ""


@dataclass
class TreeBranchPoint:
    """A point in the tree where branching occurred."""
    parent_id: str
    children_ids: List[str] = field(default_factory=list)
    entry_index: int = 0


@dataclass
class SessionData:
    header: dict = field(default_factory=dict)
    skills: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    tool_calls: list = field(default_factory=list)
    bash_executions: list = field(default_factory=list)
    user_messages: list = field(default_factory=list)
    assistant_messages: list = field(default_factory=list)
    model_changes: list = field(default_factory=list)
    thinking_level_changes: list = field(default_factory=list)
    compactions: list = field(default_factory=list)
    branch_summaries: list = field(default_factory=list)
    labels: list = field(default_factory=list)
    session_info: list = field(default_factory=list)
    branch_points: list = field(default_factory=list)
    total_entries: int = 0
    has_branching: bool = False
    has_compaction: bool = False


# ─────────────────────────────────────────────────────────────
# Parsing functions
# ─────────────────────────────────────────────────────────────

def decode_session_html(html_path: str) -> dict:
    """Extract and decode session data from HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    pattern = r'id="session-data" type="application/json">([^<]+)'
    match = re.search(pattern, html_content)

    if not match:
        raise ValueError("Could not find session-data in HTML file")

    base64_data = match.group(1)
    json_data = base64.b64decode(base64_data).decode('utf-8')
    return json.loads(json_data)


def classify_error(message: str) -> str:
    """Classify error message into category."""
    message_lower = message.lower()

    if any(kw in message_lower for kw in ['hardcoded secret', 'potential secret']):
        return 'security'
    if any(kw in message_lower for kw in ['cannot find module', 'ts-expect-error', 'typescript:', 'no-any-type']):
        return 'type/lsp'
    if any(kw in message_lower for kw in ['rendered line exceeds', 'terminal width', 'ansi', 'box-drawing']):
        return 'rendering'
    if any(kw in message_lower for kw in ['api', 'parameter', 'format', 'invalid', 'required field']):
        return 'API'
    if any(kw in message_lower for kw in ['not working', 'no effect', 'doesn\'t work', 'missing']):
        return 'logic'
    if any(kw in message_lower for kw in ['can\'t copy', 'confusing', 'no feedback', 'ux']):
        return 'ux'
    return 'unknown'


def extract_text_from_content(content, include_thinking: bool = False) -> str:
    """Extract text from message content (string or array)."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif include_thinking and item.get('type') == 'thinking':
                    texts.append(item.get('thinking', ''))
        return '\n'.join(texts)
    return str(content)


def has_image_content(content) -> bool:
    """Check if content contains image blocks."""
    if isinstance(content, list):
        return any(isinstance(item, dict) and item.get('type') == 'image' for item in content)
    return False


def find_skills_in_text(text: str) -> list:
    """Find skill invocations in text content."""
    skills = []
    pattern = r'<skill\s+name="([^"]+)"\s+location="([^"]+)">'
    for match in re.finditer(pattern, text):
        skills.append({
            'name': match.group(1),
            'location': match.group(2)
        })
    return skills


def find_errors_in_text(text: str, entry_index: int) -> list:
    """Find error messages in text content."""
    errors = []

    error_patterns = [
        (r'Error:\s*(.+?)(?:\n|$)', 'error'),
        (r'🔴 STOP.+?Potential secret.+?(\w+\.ts:\d+)', 'security'),
        (r'●\s+L\d+\s+\w+:\d+\s+(.+)', 'lsp'),
        (r'▲\s+L\d+\s+[\w-]+\s+(.+)', 'lint'),
        (r'Cannot find module \'(.+?)\'', 'module'),
        (r'Rendered line \d+ exceeds terminal width', 'rendering'),
    ]

    for pattern, pattern_type in error_patterns:
        for match in re.finditer(pattern, text):
            error_msg = match.group(1) if match.lastindex else match.group(0)
            errors.append(Error(
                message=error_msg,
                category=classify_error(error_msg),
                entry_index=entry_index,
                context=text[:200]
            ))

    return errors


def extract_edit_changes(tool_call_entry: dict) -> List[EditChange]:
    """Extract full edit diffs from a toolCall entry."""
    changes = []
    args = tool_call_entry.get('arguments', {})
    edits = args.get('edits', [])

    for edit in edits:
        old_text = edit.get('oldText', '')
        new_text = edit.get('newText', '')
        changes.append(EditChange(
            old_text=old_text,
            new_text=new_text,
            old_text_preview=old_text[:200] if old_text else '',
            new_text_preview=new_text[:200] if new_text else '',
        ))

    return changes


def find_matching_tool_call(entries: list, current_index: int, tool_call_id: str) -> Optional[dict]:
    """Find the toolCall entry that matches a given toolCallId."""
    for j in range(max(0, current_index - 15), current_index):
        prev_entry = entries[j]
        prev_msg = prev_entry.get('message', {})
        prev_content = prev_msg.get('content', [])
        if isinstance(prev_content, list):
            for item in prev_content:
                if isinstance(item, dict) and item.get('type') == 'toolCall':
                    if item.get('id') == tool_call_id:
                        return item
    return None


def analyze_tree_structure(entries: list) -> tuple:
    """Analyze parentId tree structure for branching.

    Returns:
        branch_points: List of TreeBranchPoint where branching occurred
        has_branching: bool indicating if any branching exists
    """
    # Build id -> entry index map
    id_to_index = {}
    for i, entry in enumerate(entries):
        eid = entry.get('id', '')
        if eid:
            id_to_index[eid] = i

    # Build parent -> children map
    children_of: Dict[str, List[str]] = {}
    for entry in entries:
        eid = entry.get('id', '')
        pid = entry.get('parentId', '')
        if eid and pid:
            children_of.setdefault(pid, []).append(eid)

    # Find branch points (parent with >1 child)
    branch_points = []
    for pid, kids in children_of.items():
        if len(kids) > 1:
            bp = TreeBranchPoint(
                parent_id=pid,
                children_ids=kids,
                entry_index=id_to_index.get(pid, 0)
            )
            branch_points.append(bp)

    return branch_points, len(branch_points) > 0


def parse_session(html_path: str) -> SessionData:
    """Parse session HTML and extract all structured data."""
    data = decode_session_html(html_path)
    session = SessionData()

    session.header = data.get('header', {})
    entries = data.get('entries', [])
    session.total_entries = len(entries)

    # Analyze tree structure
    session.branch_points, session.has_branching = analyze_tree_structure(entries)

    for i, entry in enumerate(entries):
        entry_type = entry.get('type', '')
        msg = entry.get('message', {})
        role = msg.get('role', '')
        content = msg.get('content', '')

        # ─────────────────────────────────────────────────
        # Non-message entry types
        # ─────────────────────────────────────────────────

        if entry_type == 'model_change':
            session.model_changes.append({
                'entry_index': i,
                'provider': msg.get('provider', entry.get('provider', '')),
                'model': msg.get('model', entry.get('modelId', '')),
                'timestamp': entry.get('timestamp', '')
            })
            continue

        if entry_type == 'thinking_level_change':
            session.thinking_level_changes.append({
                'entry_index': i,
                'level': msg.get('level', entry.get('thinkingLevel', '')),
                'timestamp': entry.get('timestamp', '')
            })
            continue

        if entry_type == 'compaction':
            summary = entry.get('summary', '')
            session.has_compaction = True
            session.compactions.append(CompactionEntry(
                entry_index=i,
                summary=summary[:500],
                summary_full=summary,
                tokens_before=entry.get('tokensBefore', 0),
                first_kept_entry_id=entry.get('firstKeptEntryId', ''),
                details=entry.get('details'),
                from_hook=entry.get('fromHook', False),
                timestamp=entry.get('timestamp', ''),
            ))
            continue

        if entry_type == 'branch_summary':
            summary = entry.get('summary', '')
            session.branch_summaries.append(BranchSummaryEntry(
                entry_index=i,
                summary=summary[:500],
                summary_full=summary,
                from_id=entry.get('fromId', ''),
                details=entry.get('details'),
                from_hook=entry.get('fromHook', False),
                timestamp=entry.get('timestamp', ''),
            ))
            continue

        if entry_type == 'label':
            session.labels.append(LabelEntry(
                entry_index=i,
                target_id=entry.get('targetId', ''),
                label=entry.get('label', ''),
                timestamp=entry.get('timestamp', ''),
            ))
            continue

        if entry_type == 'session_info':
            session.session_info.append(SessionInfoEntry(
                entry_index=i,
                name=entry.get('name', ''),
                timestamp=entry.get('timestamp', ''),
            ))
            continue

        # Skip custom / custom_message entries (extension state)
        if entry_type in ('custom', 'custom_message'):
            continue

        # ─────────────────────────────────────────────────
        # Message entries (various roles)
        # ─────────────────────────────────────────────────

        if role == 'user':
            text = extract_text_from_content(content)
            if text.strip():
                # Check for skill invocations
                skills = find_skills_in_text(text)
                for skill in skills:
                    session.skills.append(SkillInvocation(
                        name=skill['name'],
                        location=skill['location'],
                        entry_index=i,
                        context=text[:300]
                    ))

                is_feedback = any(kw in text.lower() for kw in [
                    'doesn\'t work', 'not working', 'error', 'crash', 'bug',
                    'fix', 'wrong', 'issue', 'problem', 'can\'t', '无法',
                    '没有效果', '看不到', '无效', '报错', '崩溃'
                ])

                session.user_messages.append(UserMessage(
                    content=text,
                    entry_index=i,
                    timestamp=entry.get('timestamp', ''),
                    is_feedback=is_feedback,
                    has_image=has_image_content(content),
                ))

        elif role == 'assistant':
            text = extract_text_from_content(content)
            has_thinking = False
            thinking_content = ""

            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'thinking':
                        has_thinking = True
                        thinking_content = item.get('thinking', '')

            if text.strip() or has_thinking:
                session.assistant_messages.append(AssistantMessage(
                    content=text,
                    entry_index=i,
                    timestamp=entry.get('timestamp', ''),
                    has_thinking=has_thinking,
                    thinking_content=thinking_content[:500] if thinking_content else "",
                    thinking_content_full=thinking_content if thinking_content else "",
                    model=msg.get('model', ''),
                    provider=msg.get('provider', ''),
                    api=msg.get('api', ''),
                    usage=msg.get('usage'),
                    stop_reason=msg.get('stopReason', ''),
                    error_message=msg.get('errorMessage', ''),
                    response_id=msg.get('responseId', ''),
                ))

            errors = find_errors_in_text(text, i)
            session.errors.extend(errors)

        elif role == 'toolResult':
            tool_name = msg.get('toolName', '')
            is_error = msg.get('isError', False)
            error_message = msg.get('errorMessage', '')
            details = msg.get('details')
            result_text = extract_text_from_content(content)

            # Find matching tool call
            tool_call_id = msg.get('toolCallId', '')
            tool_call_entry = find_matching_tool_call(entries, i, tool_call_id)

            # Extract edit changes if this is an edit tool
            edit_changes = None
            if tool_call_entry and tool_call_entry.get('name') == 'edit':
                edit_changes = extract_edit_changes(tool_call_entry)

            session.tool_calls.append(ToolCall(
                name=tool_name or (tool_call_entry.get('name', '') if tool_call_entry else ''),
                arguments=tool_call_entry.get('arguments', {}) if tool_call_entry else {},
                entry_index=i,
                result=result_text[:500] if result_text else None,
                result_full=result_text if result_text else None,
                is_error=is_error,
                error_message=error_message,
                details=details,
                edit_changes=edit_changes,
                timestamp=entry.get('timestamp', ''),
                tool_call_id=tool_call_id,
            ))

            # Check for errors in tool results
            if is_error:
                error_text = error_message or result_text or "Tool error"
                session.errors.append(Error(
                    message=error_text[:200],
                    category=classify_error(error_text),
                    entry_index=i,
                    context=f"Tool: {tool_name}",
                    error_message_field=error_message,
                ))

        elif role == 'bashExecution':
            # Rich bash execution data (separate from toolResult)
            output = msg.get('output', '')
            session.bash_executions.append(BashExecution(
                command=msg.get('command', ''),
                output=output[:500],
                output_full=output,
                exit_code=msg.get('exitCode'),
                cancelled=msg.get('cancelled', False),
                truncated=msg.get('truncated', False),
                full_output_path=msg.get('fullOutputPath', ''),
                exclude_from_context=msg.get('excludeFromContext', False),
                entry_index=i,
                timestamp=entry.get('timestamp', ''),
            ))

        elif role == 'branchSummary':
            summary = msg.get('summary', '')
            session.branch_summaries.append(BranchSummaryEntry(
                entry_index=i,
                summary=summary[:500],
                summary_full=summary,
                from_id=msg.get('fromId', ''),
                timestamp=entry.get('timestamp', ''),
            ))

        elif role == 'compactionSummary':
            summary = msg.get('summary', '')
            session.compactions.append(CompactionEntry(
                entry_index=i,
                summary=summary[:500],
                summary_full=summary,
                timestamp=entry.get('timestamp', ''),
            ))

    return session


def session_to_dict(session: SessionData, full: bool = False) -> dict:
    """Convert SessionData to dictionary for JSON serialization."""

    def serialize_tool_call(tc):
        d = {
            'name': tc.name,
            'arguments': tc.arguments,
            'entry_index': tc.entry_index,
            'result': tc.result,
            'is_error': tc.is_error,
            'error_message': tc.error_message,
            'tool_call_id': tc.tool_call_id,
            'timestamp': tc.timestamp,
        }
        if full:
            d['result_full'] = tc.result_full
            d['details'] = tc.details
            if tc.edit_changes:
                d['edit_changes'] = [
                    {'old_text': ec.old_text, 'new_text': ec.new_text}
                    for ec in tc.edit_changes
                ]
        return d

    def serialize_assistant_message(am):
        d = {
            'content': am.content,
            'entry_index': am.entry_index,
            'timestamp': am.timestamp,
            'has_thinking': am.has_thinking,
            'thinking_content': am.thinking_content,
            'model': am.model,
            'provider': am.provider,
            'api': am.api,
            'usage': am.usage,
            'stop_reason': am.stop_reason,
            'error_message': am.error_message,
        }
        if full:
            d['thinking_content_full'] = am.thinking_content_full
            d['response_id'] = am.response_id
        return d

    def serialize_bash_execution(be):
        d = {
            'command': be.command,
            'output': be.output,
            'exit_code': be.exit_code,
            'cancelled': be.cancelled,
            'truncated': be.truncated,
            'entry_index': be.entry_index,
            'timestamp': be.timestamp,
        }
        if full:
            d['output_full'] = be.output_full
            d['full_output_path'] = be.full_output_path
            d['exclude_from_context'] = be.exclude_from_context
        return d

    def serialize_compaction(c):
        d = {
            'entry_index': c.entry_index,
            'summary': c.summary,
            'tokens_before': c.tokens_before,
            'first_kept_entry_id': c.first_kept_entry_id,
            'from_hook': c.from_hook,
            'timestamp': c.timestamp,
        }
        if full:
            d['summary_full'] = c.summary_full
            d['details'] = c.details
        return d

    def serialize_branch_summary(bs):
        d = {
            'entry_index': bs.entry_index,
            'summary': bs.summary,
            'from_id': bs.from_id,
            'from_hook': bs.from_hook,
            'timestamp': bs.timestamp,
        }
        if full:
            d['summary_full'] = bs.summary_full
            d['details'] = bs.details
        return d

    return {
        'header': session.header,
        'total_entries': session.total_entries,
        'has_branching': session.has_branching,
        'has_compaction': session.has_compaction,
        'skills': [asdict(s) for s in session.skills],
        'errors': [asdict(e) for e in session.errors],
        'tool_calls': [serialize_tool_call(t) for t in session.tool_calls],
        'bash_executions': [serialize_bash_execution(b) for b in session.bash_executions],
        'user_messages': [asdict(u) for u in session.user_messages],
        'assistant_messages': [serialize_assistant_message(a) for a in session.assistant_messages],
        'model_changes': session.model_changes,
        'thinking_level_changes': session.thinking_level_changes,
        'compactions': [serialize_compaction(c) for c in session.compactions],
        'branch_summaries': [serialize_branch_summary(bs) for bs in session.branch_summaries],
        'labels': [asdict(l) for l in session.labels],
        'session_info': [asdict(si) for si in session.session_info],
        'branch_points': [asdict(bp) for bp in session.branch_points],
        'summary': {
            'skills_count': len(session.skills),
            'errors_count': len(session.errors),
            'tool_calls_count': len(session.tool_calls),
            'bash_executions_count': len(session.bash_executions),
            'user_messages_count': len(session.user_messages),
            'feedback_messages_count': sum(1 for u in session.user_messages if u.is_feedback),
            'edit_operations_count': sum(1 for t in session.tool_calls if t.edit_changes),
            'compaction_count': len(session.compactions),
            'branch_summary_count': len(session.branch_summaries),
            'branch_point_count': len(session.branch_points),
            'total_edit_diff_chars': sum(
                len(ec.old_text) + len(ec.new_text)
                for t in session.tool_calls if t.edit_changes
                for ec in t.edit_changes
            ),
            'total_thinking_chars': sum(
                len(am.thinking_content_full) for am in session.assistant_messages
            ),
            'total_tool_result_chars': sum(
                len(t.result_full or '') for t in session.tool_calls
            ),
            'total_bash_output_chars': sum(
                len(b.output_full or '') for b in session.bash_executions
            ),
            'compaction_tokens_saved': sum(
                c.tokens_before for c in session.compactions if c.tokens_before
            ),
            'stop_reasons': dict(
                (sr, sum(1 for a in session.assistant_messages if a.stop_reason == sr))
                for sr in set(a.stop_reason for a in session.assistant_messages if a.stop_reason)
            ),
            'models_used': list(set(
                a.model for a in session.assistant_messages if a.model
            )),
            'providers_used': list(set(
                a.provider for a in session.assistant_messages if a.provider
            )),
        }
    }


def format_text_report(session: SessionData) -> str:
    """Format session data as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("SESSION ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append("SESSION METADATA:")
    lines.append(f"  ID: {session.header.get('id', 'unknown')}")
    lines.append(f"  Version: {session.header.get('version', 'unknown')}")
    lines.append(f"  Timestamp: {session.header.get('timestamp', 'unknown')}")
    lines.append(f"  CWD: {session.header.get('cwd', 'unknown')}")
    lines.append(f"  Total entries: {session.total_entries}")
    lines.append(f"  Has branching: {session.has_branching}")
    lines.append(f"  Has compaction: {session.has_compaction}")
    if session.session_info:
        lines.append(f"  Display name: {session.session_info[-1].name}")
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(f"  Skills invoked: {len(session.skills)}")
    lines.append(f"  Errors found: {len(session.errors)}")
    lines.append(f"  Tool calls: {len(session.tool_calls)}")
    lines.append(f"  Bash executions: {len(session.bash_executions)}")
    lines.append(f"  Edit operations: {sum(1 for t in session.tool_calls if t.edit_changes)}")
    lines.append(f"  User messages: {len(session.user_messages)}")
    lines.append(f"  Compactions: {len(session.compactions)}")
    lines.append(f"  Branch summaries: {len(session.branch_summaries)}")
    lines.append(f"  Branch points: {len(session.branch_points)}")
    lines.append("")

    # Stop reasons
    stop_reasons = {}
    for a in session.assistant_messages:
        sr = a.stop_reason
        if sr:
            stop_reasons[sr] = stop_reasons.get(sr, 0) + 1
    if stop_reasons:
        lines.append("STOP REASONS:")
        for sr, count in sorted(stop_reasons.items(), key=lambda x: -x[1]):
            lines.append(f"  {sr}: {count}")
        lines.append("")

    if session.skills:
        lines.append("SKILLS INVOKED:")
        for skill in session.skills:
            lines.append(f"  - {skill.name} (entry {skill.entry_index})")
            lines.append(f"    Location: {skill.location}")
        lines.append("")

    if session.errors:
        lines.append("ERRORS:")
        for error in session.errors:
            lines.append(f"  [{error.category}] Entry {error.entry_index}:")
            lines.append(f"    {error.message[:100]}")
            if error.error_message_field:
                lines.append(f"    errorMessage: {error.error_message_field[:100]}")
        lines.append("")

    if session.compactions:
        lines.append("COMPACTIONS:")
        for c in session.compactions:
            lines.append(f"  Entry {c.entry_index}: {c.tokens_before} tokens compacted")
            lines.append(f"    Summary: {c.summary[:150]}")
        lines.append("")

    if session.branch_summaries:
        lines.append("BRANCH SUMMARIES (abandoned approaches):")
        for bs in session.branch_summaries:
            lines.append(f"  Entry {bs.entry_index}: from {bs.from_id}")
            lines.append(f"    Summary: {bs.summary[:150]}")
        lines.append("")

    if session.tool_calls:
        lines.append("TOOL CALLS:")
        for tc in session.tool_calls:
            status = "ERROR" if tc.is_error else "OK"
            lines.append(f"  [{status}] {tc.name} (entry {tc.entry_index})")
            if tc.edit_changes:
                for ec in tc.edit_changes:
                    lines.append(f"    EDIT: '{ec.old_text_preview}' → '{ec.new_text_preview}'")
            if tc.result:
                lines.append(f"    Result: {tc.result[:100]}...")
            if tc.error_message:
                lines.append(f"    Error: {tc.error_message[:100]}")
        lines.append("")

    if session.user_messages:
        lines.append("USER MESSAGES:")
        for um in session.user_messages:
            feedback_tag = " [FEEDBACK]" if um.is_feedback else ""
            image_tag = " [IMAGE]" if um.has_image else ""
            lines.append(f"  Entry {um.entry_index}{feedback_tag}{image_tag}:")
            lines.append(f"    {um.content[:200]}")
        lines.append("")

    if session.model_changes:
        lines.append("MODEL CHANGES:")
        for mc in session.model_changes:
            lines.append(f"  Entry {mc['entry_index']}: {mc.get('provider', '')}/{mc.get('model', '')}")
        lines.append("")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_session.py <session.html> [--output-format json|text] [--full]")
        sys.exit(1)

    html_path = sys.argv[1]
    output_format = 'text'
    full = '--full' in sys.argv

    if '--output-format' in sys.argv:
        idx = sys.argv.index('--output-format')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not Path(html_path).exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)

    try:
        session = parse_session(html_path)

        if output_format == 'json':
            print(json.dumps(session_to_dict(session, full=full), indent=2, ensure_ascii=False))
        else:
            print(format_text_report(session))

    except Exception as e:
        print(f"Error parsing session: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
