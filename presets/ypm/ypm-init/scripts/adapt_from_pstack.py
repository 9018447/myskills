#!/usr/bin/env python3
"""Regenerate the bundled YPM adaptation from a verified local pstack snapshot."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def split_skill(raw):
    if raw.startswith('---\n'):
        header, body = raw[4:].split('\n---\n', 1)
        return header, body.lstrip('\n')
    return '', raw

def adapt(body, rules):
    for before, after in rules:
        if before not in body:
            raise ValueError('Adaptation anchor missing: ' + before[:100])
        body = body.replace(before, after)
    return body

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    manifest = json.loads((ROOT/'references/source-lock.json').read_text())
    rules = json.loads((ROOT/'references/adaptation-rules.json').read_text())
    planned, diffs = [], []
    for item in manifest['files']:
        raw = (a.source/item['source']).read_text()
        if sha(raw) != item['sha256']:
            raise ValueError('Source differs from locked snapshot: ' + item['source'])
        _, body = split_skill(raw)
        body = adapt(body, rules.get(item['source'], []))
        if item['kind'] in ('playbook', 'principle'):
            text = ('---\nname: '+item['name']+'\ndescription: '
                    +json.dumps(item['description'], ensure_ascii=False)+'\n---\n\n'
                    +'> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。'
                    +'保留 pstack 工程步骤，仅适配角色、工具和引用。\n\n'+body.rstrip()+'\n')
        else:
            text = body.rstrip()+'\n'
        planned.append((ROOT/item['destination'], text))
        diffs.extend(difflib.unified_diff(raw.splitlines(True), text.splitlines(True),
                     fromfile='pstack/'+item['source'], tofile='ypm-init/'+item['destination'], n=0))
    for dest, text in planned:
        print(('WRITE ' if a.apply else 'PLAN ') + str(dest.relative_to(ROOT)))
        if a.apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
    if a.apply:
        (ROOT/'references/pstack-adaptation.diff').write_text(''.join(diffs))
    print(f'{len(planned)} files; source {manifest["commit"]}; '+('applied' if a.apply else 'preview only'))

if __name__ == '__main__':
    main()
