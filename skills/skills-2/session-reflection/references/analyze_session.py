#!/usr/bin/env python3
"""
Comprehensive session analysis - runs all extraction scripts and produces a unified report.

Usage:
    python analyze_session.py <session.html> [--output-dir <dir>] [--format json|text|html]

This is the main entry point for session analysis. It runs all extractors
and produces a unified report with all findings.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Import all extractors
from parse_session import parse_session, session_to_dict
from extract_errors import extract_errors, format_text_output as errors_text
from extract_tool_calls import extract_tool_calls, analyze_tool_usage, format_text_output as tools_text
from extract_user_feedback import extract_feedback, analyze_feedback, format_text_output as feedback_text
from extract_skills import extract_skills, analyze_skills, format_text_output as skills_text
from extract_error_fix_chains import extract_error_fix_chains, analyze_chains, format_text_output as chains_text
from extract_workflow import extract_workflows, format_text_output as workflow_text


def run_full_analysis(html_path: str) -> dict:
    """Run all analysis scripts and return unified results."""
    results = {
        'session_file': html_path,
        'analysis_timestamp': datetime.now().isoformat(),
        'summary': {}
    }

    # 1. Parse full session (with full content for detailed analysis)
    print("  Parsing session...", file=sys.stderr)
    session = parse_session(html_path)
    results['session'] = session_to_dict(session, full=True)

    # 2. Extract errors
    print("  Extracting errors...", file=sys.stderr)
    errors, error_analysis = extract_errors(html_path)
    results['errors'] = {
        'analysis': error_analysis,
        'items': [asdict(e) for e in errors]
    }

    # 3. Extract tool calls
    print("  Extracting tool calls...", file=sys.stderr)
    tool_calls = extract_tool_calls(html_path)
    tool_analysis = analyze_tool_usage(tool_calls)
    results['tool_calls'] = {
        'analysis': tool_analysis,
        'items': [asdict(t) for t in tool_calls]
    }

    # 4. Extract user feedback
    print("  Extracting user feedback...", file=sys.stderr)
    feedback = extract_feedback(html_path)
    feedback_analysis = analyze_feedback(feedback)
    results['user_feedback'] = {
        'analysis': feedback_analysis,
        'items': [asdict(f) for f in feedback]
    }

    # 5. Extract skills
    print("  Extracting skills...", file=sys.stderr)
    skills = extract_skills(html_path)
    skill_analysis = analyze_skills(skills)
    results['skills'] = {
        'analysis': skill_analysis,
        'items': [asdict(s) for s in skills]
    }

    # 6. Extract error-fix chains
    print("  Analyzing error-fix chains...", file=sys.stderr)
    chains = extract_error_fix_chains(html_path)
    chain_analysis = analyze_chains(chains)
    results['error_fix_chains'] = {
        'analysis': chain_analysis,
        'items': [asdict(c) for c in chains]
    }

    # 7. Extract workflow sequences
    print("  Extracting workflow sequences...", file=sys.stderr)
    workflows = extract_workflows(html_path)
    results['workflows'] = {
        'items': [asdict(w) for w in workflows]
    }

    # 8. Generate summary
    results['summary'] = generate_summary(results)

    return results


def generate_summary(results: dict) -> dict:
    """Generate high-level summary from all analyses."""
    chain_analysis = results.get('error_fix_chains', {}).get('analysis', {})
    workflows = results.get('workflows', {}).get('items', [])
    
    return {
        'session_id': results['session']['header'].get('id', 'unknown'),
        'timestamp': results['session']['header'].get('timestamp', 'unknown'),
        'session_version': results['session']['header'].get('version', 1),
        'cwd': results['session']['header'].get('cwd', ''),
        'total_entries': results['session']['total_entries'],
        'has_branching': results['session'].get('has_branching', False),
        'has_compaction': results['session'].get('has_compaction', False),
        # Skills
        'skills_used': results['skills']['analysis'].get('unique_skills', 0),
        'skill_names': results['skills']['analysis'].get('skills_used', []),
        # Errors
        'errors_found': results['errors']['analysis'].get('total', 0),
        'error_categories': results['errors']['analysis'].get('by_category', {}),
        # Tool calls
        'tool_calls_made': results['tool_calls']['analysis'].get('total', 0),
        'tool_success_rate': (
            results['tool_calls']['analysis'].get('successful', 0) /
            max(results['tool_calls']['analysis'].get('total', 1), 1)
        ),
        # Bash executions (separate from tool calls)
        'bash_executions': len(results['session'].get('bash_executions', [])),
        # User feedback
        'user_messages': results['user_feedback']['analysis'].get('total', 0),
        'feedback_types': results['user_feedback']['analysis'].get('by_type', {}),
        'has_bug_reports': results['user_feedback']['analysis'].get('has_bug_reports', False),
        'has_feature_requests': results['user_feedback']['analysis'].get('has_feature_requests', False),
        'initial_requirements': results['user_feedback']['analysis'].get('requirements', []),
        # Files and tools
        'files_affected': results['errors']['analysis'].get('files_affected', []),
        'tools_used': list(results['tool_calls']['analysis'].get('by_tool', {}).keys()),
        # Error-fix chains
        'errors_resolved': chain_analysis.get('resolved', 0),
        'errors_unresolved': chain_analysis.get('unresolved', 0),
        'anti_patterns_found': len(chain_analysis.get('anti_patterns', [])),
        'avg_steps_to_fix': chain_analysis.get('avg_steps_to_fix', 0),
        # Workflow
        'workflow_domains': [w.get('domain', '') for w in workflows],
        'workflow_success': any(w.get('success', False) for w in workflows),
        # New: official doc fields
        'stop_reasons': results['session']['summary'].get('stop_reasons', {}),
        'models_used': results['session']['summary'].get('models_used', []),
        'providers_used': results['session']['summary'].get('providers_used', []),
        'compaction_count': results['session']['summary'].get('compaction_count', 0),
        'branch_summary_count': results['session']['summary'].get('branch_summary_count', 0),
        'branch_point_count': results['session']['summary'].get('branch_point_count', 0),
        'compaction_tokens_saved': results['session']['summary'].get('compaction_tokens_saved', 0),
        'edit_operations_count': results['session']['summary'].get('edit_operations_count', 0),
        'total_edit_diff_chars': results['session']['summary'].get('total_edit_diff_chars', 0),
        'total_thinking_chars': results['session']['summary'].get('total_thinking_chars', 0),
        'total_tool_result_chars': results['session']['summary'].get('total_tool_result_chars', 0),
        'total_bash_output_chars': results['session']['summary'].get('total_bash_output_chars', 0),
    }


def format_unified_text(results: dict) -> str:
    """Format all results as a unified text report."""
    lines = []
    summary = results['summary']

    lines.append("╔" + "═" * 58 + "╗")
    lines.append("║" + " SESSION ANALYSIS REPORT".center(58) + "║")
    lines.append("╚" + "═" * 58 + "╝")
    lines.append("")

    # Session info
    lines.append("SESSION INFO:")
    lines.append(f"  ID:        {summary['session_id']}")
    lines.append(f"  Timestamp: {summary['timestamp']}")
    lines.append(f"  Entries:   {summary['total_entries']}")
    lines.append("")

    # High-level summary
    lines.append("SUMMARY:")
    lines.append(f"  Skills invoked:      {summary['skills_used']} ({', '.join(summary['skill_names']) or 'none'})")
    lines.append(f"  Errors found:        {summary['errors_found']}")
    lines.append(f"  Tool calls made:     {summary['tool_calls_made']}")
    lines.append(f"  Tool success rate:   {summary['tool_success_rate']:.1%}")
    lines.append(f"  User messages:       {summary['user_messages']}")
    lines.append(f"  Bug reports:         {'Yes' if summary['has_bug_reports'] else 'No'}")
    lines.append(f"  Feature requests:    {'Yes' if summary['has_feature_requests'] else 'No'}")
    lines.append("")

    # Initial requirements
    if summary['initial_requirements']:
        lines.append("INITIAL REQUIREMENTS:")
        for i, req in enumerate(summary['initial_requirements'], 1):
            lines.append(f"  {i}. {req[:200]}")
        lines.append("")

    # Error categories
    if summary['error_categories']:
        lines.append("ERROR CATEGORIES:")
        for cat, count in sorted(summary['error_categories'].items()):
            lines.append(f"  {cat}: {count}")
        lines.append("")

    # Tools used
    if summary['tools_used']:
        lines.append("TOOLS USED:")
        for tool in sorted(summary['tools_used']):
            count = results['tool_calls']['analysis'].get('by_tool', {}).get(tool, 0)
            lines.append(f"  - {tool} ({count}x)")
        lines.append("")

    # Files affected
    if summary['files_affected']:
        lines.append("FILES AFFECTED:")
        for f in sorted(summary['files_affected'])[:20]:
            lines.append(f"  - {f}")
        if len(summary['files_affected']) > 20:
            lines.append(f"  ... and {len(summary['files_affected']) - 20} more")
        lines.append("")

    # Detailed sections
    lines.append("=" * 60)
    lines.append("DETAILED ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    # Skills section
    lines.append("-" * 60)
    lines.append("SKILLS")
    lines.append("-" * 60)
    lines.append(skills_text(
        [type('obj', (object,), s)() for s in results['skills']['items']],
        results['skills']['analysis']
    ))
    lines.append("")

    # Errors section
    lines.append("-" * 60)
    lines.append("ERRORS")
    lines.append("-" * 60)
    lines.append(errors_text(
        [type('obj', (object,), e)() for e in results['errors']['items']],
        results['errors']['analysis']
    ))
    lines.append("")

    # Tool calls section
    lines.append("-" * 60)
    lines.append("TOOL CALLS")
    lines.append("-" * 60)
    lines.append(tools_text(
        [type('obj', (object,), t)() for t in results['tool_calls']['items']],
        results['tool_calls']['analysis']
    ))
    lines.append("")

    # User feedback section
    lines.append("-" * 60)
    lines.append("USER FEEDBACK")
    lines.append("-" * 60)
    lines.append(feedback_text(
        [type('obj', (object,), f)() for f in results['user_feedback']['items']],
        results['user_feedback']['analysis']
    ))

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_session.py <session.html> [--output-dir <dir>] [--format json|text]")
        print("\nThis script runs all analysis scripts and produces a comprehensive report.")
        sys.exit(1)

    html_path = sys.argv[1]
    output_dir = None
    output_format = 'text'

    # Parse arguments
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--output-dir' and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == '--format' and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        else:
            i += 1

    if not Path(html_path).exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)

    try:
        print(f"Analyzing session: {html_path}", file=sys.stderr)
        results = run_full_analysis(html_path)

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

            # Save JSON
            json_path = os.path.join(output_dir, 'session_analysis.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Saved JSON: {json_path}", file=sys.stderr)

            # Save text report
            text_path = os.path.join(output_dir, 'session_analysis.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(format_unified_text(results))
            print(f"  Saved text: {text_path}", file=sys.stderr)

            # Save summary
            summary_path = os.path.join(output_dir, 'summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(results['summary'], f, indent=2, ensure_ascii=False)
            print(f"  Saved summary: {summary_path}", file=sys.stderr)

            print(f"\nAnalysis complete! Results saved to: {output_dir}", file=sys.stderr)
        else:
            if output_format == 'json':
                print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
            else:
                print(format_unified_text(results))

    except Exception as e:
        print(f"Error analyzing session: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
