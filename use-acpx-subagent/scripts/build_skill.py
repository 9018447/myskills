#!/usr/bin/env python3
"""Build a self-contained dispatch skill from a reviewed spec and pinned source files."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def relative(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value:
        raise ValueError(f'Unsafe relative path: {value!r}')
    return p


def inside(root, value):
    p = root.joinpath(*relative(value).parts).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes root: {value}')
    return p


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def build(spec_path, source_root, payload_root, output):
    spec = json.loads(spec_path.read_text())
    name = spec['name']
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name):
        raise ValueError('Invalid skill name')
    if output.exists():
        raise ValueError('Output already exists; use a new directory')
    if not re.fullmatch(r'[0-9a-f]{40}', spec['source']['revision']):
        raise ValueError('Source revision must be a full commit SHA')
    if any(k in spec for k in ('agent', 'model', 'provider', 'adapter')):
        raise ValueError('Do not bake executor selection or configuration into the spec')
    if not spec.get('description') or not spec.get('purpose'):
        raise ValueError('description and purpose are required')
    stages = spec['stages']
    if not stages or len({s['id'] for s in stages}) != len(stages):
        raise ValueError('Stage IDs must be nonempty and unique')
    for stage in stages:
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,47}', stage['id']) or stage['id'] in ('run_checks', 'finalize'):
            raise ValueError('Invalid stage ID')
        if not stage['prompt'].startswith('prompts/') or not stage['prompt'].endswith('.md'):
            raise ValueError('Stage prompts must live under prompts/')
    source_files = {}
    for item in spec['source']['files']:
        p = inside(source_root, item['path'])
        data = p.read_bytes()
        if git_blob(data) != item['git_blob']:
            raise ValueError(f'Source blob mismatch: {item["path"]}')
        source_files[item['path']] = data
    if not source_files or 'LICENSE' not in source_files:
        raise ValueError('Include the upstream LICENSE and all referenced source files')
    payload = {}
    for p in sorted(payload_root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'Payload symlink is not allowed: {p}')
        if p.is_file():
            key = p.relative_to(payload_root).as_posix()
            if not (key == 'AGENTS.md' or key.startswith(('prompts/', 'skills/', 'contracts/'))):
                raise ValueError(f'Unsupported payload location: {key}')
            payload[key] = p.read_bytes()
    for key in ['AGENTS.md', 'contracts/result.schema.json'] + [s['prompt'] for s in stages]:
        if key not in payload:
            raise ValueError(f'Missing payload file: {key}')
    allowed_tokens = {'TASK', 'WORKTREE', 'AGENTS_FILE', 'SKILL_PATHS', 'DIFF_FILE',
                      'BASE', 'HEAD', 'CHECKS_FILE', 'RESULT_SCHEMA', 'RUN_DIR'}
    for key, data in payload.items():
        if key == 'AGENTS.md' or key.startswith('prompts/'):
            tokens = set(re.findall(r'\{\{([A-Z_]+)\}\}', data.decode()))
            if tokens - allowed_tokens:
                raise ValueError(f'Unknown prompt tokens in {key}: {tokens - allowed_tokens}')
    dependencies = spec['dependencies']
    if not dependencies:
        raise ValueError('At least one explicit key skill dependency is required')
    for dependency in dependencies:
        key = dependency['path']
        if not key.startswith('skills/') or not key.endswith('/SKILL.md') or key not in payload:
            raise ValueError(f'Key skill is missing: {key}')
        if not dependency.get('reason'):
            raise ValueError('Explain when each key skill must be read')
    contract = json.loads(payload['contracts/result.schema.json'])
    if contract.get('type') != 'object':
        raise ValueError('The final result must be a JSON object')
    schema_check(contract)
    if not {'summary', 'status'} <= set(contract.get('required', [])):
        raise ValueError('The final schema must require summary and status')
    if contract['properties'].get('status', {}).get('enum') != ['complete', 'blocked']:
        raise ValueError('The status enum must be complete, blocked')
    mode = spec.get('workspace_mode', 'review')
    if mode not in ('review', 'edit'):
        raise ValueError('workspace_mode must be review or edit')
    files = dict(payload)
    for path, data in source_files.items():
        files['references/upstream/' + path] = data
    runtime = ROOT / 'assets/runtime'
    files['scripts/run.py'] = (runtime / 'run.py').read_bytes()
    if len(stages) > 1:
        files['workflows/task.flow.ts'] = (runtime / 'task.flow.ts').read_bytes()
    manifest = {'schema_version': 1, 'name': name, 'purpose': spec['purpose'],
                'workspace_mode': mode, 'stages': stages, 'dependencies': dependencies,
                'source': spec['source'], 'result_kind': spec.get('result_kind', 'generic')}
    if manifest['result_kind'] not in ('generic', 'ecc-review'):
        raise ValueError('Unsupported result_kind; use generic with an explicit result schema')
    files['dispatch.json'] = dump(manifest).encode()
    files['package.json'] = dump({'private': True, 'type': 'module'}).encode()
    files['SKILL.md'] = generated_skill(spec).encode()
    lock = {'source': spec['source'], 'files': {
        k: hashlib.sha256(v).hexdigest() for k, v in sorted(files.items())}}
    files['references/source-lock.json'] = dump(lock).encode()
    output.mkdir(parents=True)
    for key, data in sorted(files.items()):
        dest = inside(output, key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return {'name': name, 'files': len(files), 'stages': len(stages), 'output': str(output)}


def schema_check(schema):
    supported = {'type', 'properties', 'required', 'additionalProperties', 'items', 'enum',
                 'minItems', 'minLength', 'minimum', 'maximum', 'description', 'title', '$schema'}
    if not isinstance(schema, dict) or schema.keys() - supported:
        raise ValueError('Unsupported JSON Schema keyword')
    if schema.get('type') not in ('object', 'array', 'string', 'integer', 'number', 'boolean', 'null'):
        raise ValueError('Each schema node needs a supported type')
    for child in schema.get('properties', {}).values():
        schema_check(child)
    if 'items' in schema:
        schema_check(schema['items'])


def generated_skill(spec):
    deps = '\n'.join(f'- `{d["path"]}`：{d["reason"]}' for d in spec['dependencies'])
    stages = ' → '.join(s['id'] for s in spec['stages'])
    return f'''---
name: {spec['name']}
description: {json.dumps(spec['description'], ensure_ascii=False)}
---

# {spec['name']}

{spec['purpose']}

按 `dispatch.json` 执行固定阶段：{stages}。执行器由调用方提供，禁止选择、安装、修改或限制 agent、模型、适配器及其配置。运行器将执行器参数原样交给 acpx。

## 调用

将 `<SKILL_DIR>` 替换为本文件所在目录。`<AGENT>` 是调用方已配置的 acpx 名称；也可改传 `--agent-command '<ACP command>'`。不得凭空填默认执行器。

```bash
python3 <SKILL_DIR>/scripts/run.py prepare \\
  --repo /absolute/target-repo --base <BASE_REF> --head <HEAD_REF> \\
  --runs-dir /absolute/runs-outside-repo --run-id <UNIQUE_ID> \\
  --task-file /absolute/task.md
python3 <SKILL_DIR>/scripts/run.py dispatch \\
  --state /absolute/runs-outside-repo/<UNIQUE_ID>/state.json \\
  --agent '<AGENT>' --acpx-options-file /absolute/acpx-options.json
```

`acpx-options.json` 是调用方提供的 JSON 字符串数组，传递权限、超时等全局选项；不提供时采用 acpx 自身默认值。需要执行测试时，在 prepare 增加 `--checks-file /absolute/checks.json`，格式见 `scripts/run.py --help`。不得自动安装依赖或推断测试命令。

## 固定步骤

先核验来源和文件散列。解析 base/head 为 commit SHA，要求目标工作区干净；未提交内容须由调用方先明确选定提交快照，本技能不会 stash、commit 或复制未跟踪文件。创建独立分支与 worktree，渲染精简 `AGENTS.md` 和 prompts，记录绝对路径。每个 prompt 都显式携带运行约束与关键技能路径，不依赖宿主自动发现。

只有一个阶段时通过 `acpx ... exec --file ...` 执行。多个阶段时通过 `acpx ... flow run workflows/task.flow.ts --input-file ...` 执行；不得改成宿主 Task/subagent 或临时 shell 循环。所有 ACP 节点使用 worktree 作为 cwd，复用同一 flow 会话。

关键技能如下，派发前必须确认文件存在。派发后由工作 agent 按 prompt 中的绝对路径读取。

{deps}

保留目标仓库已有的 `AGENTS.md`、`CLAUDE.md` 和适用项目规则。生成的 `AGENTS.md` 位于运行目录，显式读取，避免覆盖项目文件。worktree 隔离工作目录，不构成进程或凭证沙箱。来源仓库的 hooks、settings、工具声明和模型字段不自动启用。

运行器保存 `state.json`、prompt、diff、原始响应、checks、JSON 结果与 Markdown 报告。以运行器退出状态和最终校验为准；不得把请求已发送、flow 已开始或模型自述当成完成。review 模式验证 tracked 与 untracked 文件均未变化；edit 模式保留修改供调用方审查。

失败时停止后续步骤，保留现场。不得自动重试完整任务、合并、push、发布评论或删除 worktree。用 `inspect --state ...` 查看状态。运行结束后可显式调用 `cleanup --state ...`，仅在工作区干净时移除 worktree；分支和产物保留。
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--payload', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        print(dump(build(a.spec, a.source_root, a.payload, a.output)), end='')
    except (ValueError, KeyError, OSError) as e:
        print(f'Build failed: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
