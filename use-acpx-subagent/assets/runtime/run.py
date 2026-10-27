#!/usr/bin/env python3
"""Workspace and dispatch runner; executor configuration belongs to the caller.

Checks: [{"name":"unit","argv":["python3","-m","unittest"],"timeout":120}]
Commands run without a shell in the worktree. No implicit install or retry.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parents[1]


def save(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    temp.replace(path)


def read(path):
    return json.loads(Path(path).read_text())


def command(argv, cwd=None, timeout=60):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
    if p.returncode:
        raise ValueError(f'Command failed ({p.returncode}): {argv!r}\n{p.stderr.decode(errors="replace")[-3000:]}')
    return p.stdout


def git(repo, *args):
    return command(['git', '-C', str(repo), *args])


def integrity():
    lock = read(PACKAGE / 'references/source-lock.json')
    for name, expected in lock['files'].items():
        path = (PACKAGE / name).resolve()
        if not path.is_relative_to(PACKAGE) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Package integrity failed: {name}')


def fingerprint(repo):
    paths = git(repo, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0')
    result = {}
    for raw in sorted(set(paths) - {b''}):
        name = os.fsdecode(raw)
        path = Path(repo) / name
        if path.is_symlink():
            value = b'symlink:' + os.fsencode(os.readlink(path))
        elif path.is_file():
            value = b'file:' + str(path.stat().st_mode & 0o777).encode() + b':' + path.read_bytes()
        elif path.is_dir():
            value = b'gitlink:' + git(path, 'rev-parse', 'HEAD').strip()
        else:
            value = b'missing'
        result[name] = hashlib.sha256(value).hexdigest()
    return result


def validate_checks(value):
    if not isinstance(value, list):
        raise ValueError('Checks must be a JSON array')
    for check in value:
        if not isinstance(check, dict) or not isinstance(check.get('name'), str) or not check['name']:
            raise ValueError('Each check needs a name')
        argv = check.get('argv')
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
            raise ValueError('Each check needs a nonempty argv array')
        limit = check.get('timeout', 120)
        if not isinstance(limit, (int, float)) or not 0 < limit <= 3600:
            raise ValueError('Check timeout must be within (0,3600] seconds')
    return value


def render(text, values):
    def substitute(match):
        if match[1] not in values:
            raise ValueError(f'Unknown template token: {match[1]}')
        return str(values[match[1]])
    return re.sub(r'\{\{([A-Z_]+)\}\}', substitute, text)


def prepare(a):
    integrity()
    manifest = read(PACKAGE / 'dispatch.json')
    repo = a.repo.resolve()
    root = Path(os.fsdecode(git(repo, 'rev-parse', '--show-toplevel')).strip()).resolve()
    if root != repo:
        raise ValueError('--repo must be the repository root')
    if git(repo, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Target worktree is dirty; select a committed snapshot first')
    index = git(repo, 'ls-files', '--stage')
    if index.startswith(b'160000 ') or b'\n160000 ' in index:
        raise ValueError('Submodules require an explicit extension; no implicit hydration')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,47}', a.run_id):
        raise ValueError('run-id must be lowercase letters/digits/hyphens, max 48 characters')
    for ref in (a.base, a.head):
        if not ref or ref.startswith('-'):
            raise ValueError('Invalid commit ref')
    base = git(repo, 'rev-parse', '--verify', '--end-of-options', a.base + '^{commit}').decode().strip()
    head = git(repo, 'rev-parse', '--verify', '--end-of-options', a.head + '^{commit}').decode().strip()
    runs = a.runs_dir.resolve()
    common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip())
    if runs.is_relative_to(repo) or runs.is_relative_to(common):
        raise ValueError('runs-dir must be outside the target checkout and Git metadata')
    task = a.task_file.read_text()
    if not task.strip():
        raise ValueError('Task must not be empty')
    checks = validate_checks(read(a.checks_file)) if a.checks_file else []
    run = runs / a.run_id
    run.mkdir(parents=True, exist_ok=False)
    worktree = run / 'workspace'
    branch = f'acpx/{manifest["name"]}/{a.run_id}'
    state = {'schema_version': 1, 'status': 'preparing', 'package': str(PACKAGE),
             'repo': str(repo), 'run_dir': str(run), 'worktree': str(worktree),
             'branch': branch, 'base': base, 'head': head, 'run_id': a.run_id,
             'workspace_mode': manifest['workspace_mode'], 'started_at': time.time()}
    save(run / 'state.json', state)
    try:
        git(repo, 'worktree', 'add', '-b', branch, str(worktree), head)
        control = run / 'control'
        control.mkdir()
        shutil.copytree(PACKAGE / 'skills', control / 'skills')
        shutil.copytree(PACKAGE / 'references/upstream', control / 'upstream')
        shutil.copytree(PACKAGE / 'contracts', control / 'contracts')
        (control / 'changes.diff').write_bytes(
            git(repo, 'diff', '--binary', '--no-ext-diff', '--no-textconv', base, head, '--'))
        save(control / 'requested-checks.json', checks)
        save(control / 'checks.json', [])
        save(control / 'manifest.json', manifest)
        (control / 'task.md').write_text(task)
        paths = '\n'.join(f'- {control / d["path"]} — {d["reason"]}' for d in manifest['dependencies'])
        values = {'TASK': task, 'WORKTREE': worktree, 'RUN_DIR': run,
                  'AGENTS_FILE': run / 'AGENTS.md', 'SKILL_PATHS': paths,
                  'DIFF_FILE': control / 'changes.diff', 'BASE': base, 'HEAD': head,
                  'CHECKS_FILE': control / 'checks.json',
                  'RESULT_SCHEMA': control / 'contracts/result.schema.json'}
        agents = render((PACKAGE / 'AGENTS.md').read_text(), values)
        (run / 'AGENTS.md').write_text(agents)
        prompt_dir = control / 'prompts'
        prompt_dir.mkdir()
        prompts = []
        for stage in manifest['stages']:
            body = render((PACKAGE / stage['prompt']).read_text(), values)
            prefix = f'Read the run instructions at {run / "AGENTS.md"}.\n\n{agents}\n\n'
            prompt = prompt_dir / f'{stage["id"]}.md'
            prompt.write_text(prefix + body + '\n')
            prompts.append(str(prompt))
        state.update(status='prepared', prompts=prompts, control=str(control),
                     initial_fingerprint=fingerprint(worktree), checks=checks,
                     changed_files=[os.fsdecode(x) for x in git(
                         repo, 'diff', '--name-only', '-z', '--no-renames', base, head, '--').split(b'\0') if x],
                     runtime=sys.executable, runner=str(Path(__file__).resolve()))
        save(run / 'state.json', state)
        print(json.dumps({'state': str(run / 'state.json'), 'worktree': str(worktree),
                          'base': base, 'head': head}, ensure_ascii=False))
    except BaseException as e:
        state.update(status='prepare_failed', error=str(e))
        save(run / 'state.json', state)
        raise


def load_state(path):
    state = read(path)
    if Path(state['run_dir']).resolve() != Path(path).resolve().parent:
        raise ValueError('State path and run directory do not match')
    if Path(state['package']).resolve() != PACKAGE:
        raise ValueError('Use the original generated skill runner')
    if Path(state['worktree']).resolve() != Path(state['run_dir']).resolve() / 'workspace':
        raise ValueError('Unexpected worktree path')
    return state


def run_checks(state):
    records = []
    for check in state['checks']:
        started = time.time()
        try:
            p = subprocess.run(check['argv'], cwd=state['worktree'], capture_output=True,
                               timeout=check.get('timeout', 120))
            record = dict(check, status='passed' if p.returncode == 0 else 'failed',
                          exit_code=p.returncode,
                          stdout=p.stdout.decode(errors='replace'), stderr=p.stderr.decode(errors='replace'))
        except subprocess.TimeoutExpired as e:
            record = dict(check, status='timed_out', exit_code=None,
                          stdout=(e.stdout or b'').decode(errors='replace'),
                          stderr=(e.stderr or b'').decode(errors='replace'))
        except OSError as e:
            record = dict(check, status='failed', exit_code=None, stdout='', stderr=str(e))
        record['duration_seconds'] = round(time.time() - started, 3)
        records.append(record)
        save(Path(state['control']) / 'checks.json', records)
    save(Path(state['control']) / 'checks.json', records)
    return records


def validate(value, schema, path='$'):
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'number': (int, float), 'boolean': bool, 'null': type(None)}
    kind = schema.get('type')
    if kind and (kind not in types or not isinstance(value, types[kind]) or
                 kind in ('integer', 'number') and isinstance(value, bool)):
        raise ValueError(f'{path}: expected {kind}')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: invalid enum value')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                raise ValueError(f'{path}: missing {key}')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False and value.keys() - properties.keys():
            raise ValueError(f'{path}: unexpected keys')
        for key, child in properties.items():
            if key in value:
                validate(value[key], child, path + '.' + key)
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise ValueError(f'{path}: too few items')
        for i, child in enumerate(value):
            validate(child, schema.get('items', {}), f'{path}[{i}]')
    if isinstance(value, str) and len(value) < schema.get('minLength', 0):
        raise ValueError(f'{path}: empty/short string')
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        if not schema.get('minimum', float('-inf')) <= value <= schema.get('maximum', float('inf')):
            raise ValueError(f'{path}: out of range')


def finish(state, result):
    control = Path(state['control'])
    validate(result, read(control / 'contracts/result.schema.json'))
    checks = read(control / 'checks.json')
    if len(checks) != len(state['checks']):
        raise ValueError('Requested checks were not all executed')
    manifest = read(control / 'manifest.json')
    report = [f'# {manifest["name"]}', '', result.get('summary', ''), '']
    if manifest['result_kind'] == 'ecc-review':
        counts = {k: 0 for k in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')}
        for finding in result['findings']:
            if finding['confidence'] <= 0.8:
                raise ValueError('Finding confidence must be greater than 0.8')
            if finding['severity'] in ('CRITICAL', 'HIGH') and not finding['guards_checked'].strip():
                raise ValueError('HIGH/CRITICAL need an explanation of existing guards')
            root = Path(state['worktree']).resolve()
            name = finding['file']
            path = (root / name).resolve()
            if Path(name).is_absolute() or '..' in Path(name).parts or not path.is_relative_to(root):
                raise ValueError('Finding path escapes worktree')
            if name not in state['changed_files'] and finding['severity'] != 'CRITICAL':
                raise ValueError('Unchanged files require a CRITICAL issue')
            if finding['side'] == 'base':
                content = git(state['repo'], 'show', state['base'] + ':' + name).decode(errors='replace')
            elif path.is_file():
                content = path.read_text(errors='replace')
            else:
                raise ValueError('Head-side finding file does not exist')
            if finding['line'] > len(content.splitlines()):
                raise ValueError('Finding line is outside the file')
            if finding['snippet'] not in content:
                raise ValueError('Evidence snippet is not present in the selected source')
            counts[finding['severity']] += 1
            report.extend([f'## [{finding["severity"]}] {finding["title"]}',
                           f'{finding["file"]}:{finding["line"]}', '', finding['trigger'],
                           finding['evidence'], finding['guards_checked'], finding['fix'], ''])
        verdict = ('INCOMPLETE' if result['status'] != 'complete' else 'BLOCK' if counts['CRITICAL'] else 'REQUEST_CHANGES'
                   if counts['HIGH'] or any(c['status'] != 'passed' for c in checks) else 'APPROVE')
        result.update(verdict=verdict, severity_counts=counts)
        report.extend(['Verdict: ' + verdict, '', json.dumps(counts), ''])
    result['checks'] = checks
    result['reviewed_range'] = {'base': state['base'], 'head': state['head']}
    after = fingerprint(state['worktree'])
    if state['workspace_mode'] == 'review' and after != state['initial_fingerprint']:
        raise ValueError('Review modified tracked or nonignored untracked files; preserve workspace for inspection')
    if state['workspace_mode'] == 'review' and git(
            state['worktree'], 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Review changed the Git index or worktree; preserve workspace for inspection')
    if git(state['worktree'], 'rev-parse', 'HEAD').decode().strip() != state['head']:
        raise ValueError('Agent changed HEAD; preserve workspace for inspection')
    if git(state['worktree'], 'symbolic-ref', '--short', 'HEAD').decode().strip() != state['branch']:
        raise ValueError('Agent switched the worktree branch; preserve workspace for inspection')
    report.extend(['## Checks', '', 'No checks requested.' if not checks else
                   '\n'.join(f'- {c["name"]}: {c["status"]}' for c in checks)])
    save(control / 'result.json', result)
    (control / 'report.md').write_text('\n'.join(report) + '\n')
    state.update(status='completed' if result['status'] == 'complete' else 'blocked',
                 completed_at=time.time(), result=str(control / 'result.json'),
                 report=str(control / 'report.md'))
    save(Path(state['run_dir']) / 'state.json', state)
    return result


def dispatch(a):
    integrity()
    state = load_state(a.state)
    if state['status'] != 'prepared':
        raise ValueError('Only a prepared run can be dispatched; no implicit replay')
    options = read(a.acpx_options_file) if a.acpx_options_file else []
    if not isinstance(options, list) or not all(isinstance(x, str) for x in options):
        raise ValueError('acpx options must be a JSON string array')
    if not (a.agent or a.agent_command or '').strip():
        raise ValueError('Caller must supply a nonempty executor')
    reserved = ('--cwd', '--agent', '--format', '--file', '-f', '--session', '-s', '--default-agent')
    if any(x.split('=')[0] in reserved for x in options):
        raise ValueError('Do not override runner-owned cwd/agent/output/session options')
    if not shutil.which(a.acpx):
        raise ValueError('acpx is not available; caller must provide its installation')
    version = command([a.acpx, '--version']).decode().strip()
    raw = a.agent_command
    selection = ['--agent', raw] if raw is not None else []
    common = [a.acpx, *options, '--cwd', state['worktree'], '--format', 'quiet', *selection]
    flow = len(state['prompts']) > 1
    if flow:
        command([a.acpx, 'flow', 'run', '--help'])
        argv = common + ['flow', 'run', str(PACKAGE / 'workflows/task.flow.ts'),
                         '--input-file', str(Path(state['control']) / 'flow-input.json')]
        if raw is None:
            argv += ['--default-agent', a.agent]
    else:
        argv = common + ([] if raw is not None else [a.agent]) + ['exec', '--file', state['prompts'][0]]
    # Exclusive claim prevents concurrent dispatches of the same prepared run.
    claim = Path(state['run_dir']) / '.dispatch.lock'
    fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    state.update(status='running', executor={'agent': a.agent, 'command': raw},
                 acpx_version=version, dispatch_argv=argv)
    save(a.state, state)
    data = {k: state[k] for k in ('worktree', 'prompts', 'control', 'runtime', 'runner')}
    data['state_file'] = str(a.state.resolve())
    save(Path(state['control']) / 'flow-input.json', data)
    try:
        control = Path(state['control'])
        with (control / 'dispatch.stdout').open('wb') as out, (control / 'dispatch.stderr').open('wb') as err:
            p = subprocess.run(argv, stdout=out, stderr=err)
        if p.returncode:
            raise ValueError(f'acpx failed with exit {p.returncode}; inspect dispatch.stderr')
        if flow:
            if load_state(a.state)['status'] not in ('completed', 'blocked'):
                raise ValueError('Flow returned without validated completion')
        else:
            response = (control / 'dispatch.stdout').read_text()
            (control / 'raw-response.txt').write_text(response)
            result = json.loads(response)
            run_checks(state)
            finish(state, result)
        if load_state(a.state)['status'] == 'blocked':
            raise ValueError('Agent reported incomplete work; inspect the INCOMPLETE result')
        print(json.dumps({'state': str(a.state), 'report': str(control / 'report.md')}, ensure_ascii=False))
    except BaseException as e:
        current = load_state(a.state)
        state.update(current, error=str(e))
        if isinstance(e, KeyboardInterrupt):
            state['status'] = 'interrupted'
        elif state['status'] != 'blocked':
            state['status'] = 'failed'
        save(a.state, state)
        raise


def cleanup(state):
    if state['status'] not in ('completed', 'blocked', 'failed', 'prepare_failed', 'prepared'):
        raise ValueError('Cannot clean up a potentially active run')
    if git(state['worktree'], 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Dirty worktree: refusing cleanup')
    git(state['repo'], 'worktree', 'remove', state['worktree'])
    state['status'] = 'cleaned'
    save(Path(state['run_dir']) / 'state.json', state)
    print('Worktree removed. Branch and run artifacts retained.')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    prep = sub.add_parser('prepare')
    for key in ('repo', 'runs-dir', 'task-file'):
        prep.add_argument('--' + key, type=Path, required=True)
    for key in ('base', 'head', 'run-id'):
        prep.add_argument('--' + key, required=True)
    prep.add_argument('--checks-file', type=Path)
    disp = sub.add_parser('dispatch')
    disp.add_argument('--state', type=Path, required=True)
    group = disp.add_mutually_exclusive_group(required=True)
    group.add_argument('--agent')
    group.add_argument('--agent-command')
    disp.add_argument('--acpx', default='acpx')
    disp.add_argument('--acpx-options-file', type=Path)
    for name in ('inspect', 'checks', 'finish', 'cleanup'):
        parser = sub.add_parser(name)
        parser.add_argument('--state', type=Path, required=True)
        if name == 'finish':
            parser.add_argument('--result', type=Path, required=True)
    a = p.parse_args()
    try:
        if a.cmd == 'prepare':
            prepare(a)
        elif a.cmd == 'dispatch':
            dispatch(a)
        else:
            state = load_state(a.state)
            if a.cmd == 'inspect':
                print(json.dumps(state, ensure_ascii=False, indent=2))
            elif a.cmd == 'checks':
                print(json.dumps(run_checks(state)))
            elif a.cmd == 'finish':
                print(json.dumps(finish(state, read(a.result))))
            else:
                cleanup(state)
    except (ValueError, OSError, subprocess.SubprocessError, KeyboardInterrupt) as e:
        print(f'Run failed: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
