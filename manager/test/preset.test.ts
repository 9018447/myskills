import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setPreset, deletePreset, applyPreset, loadManifest } from '../src/core.ts';

function makeRepo(skills: string[], manifest: object = { agents: {} }) {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-preset-'));
  for (const s of skills) {
    mkdirSync(join(repo, s), { recursive: true });
    writeFileSync(join(repo, s, 'SKILL.md'), `---\nname: ${s}\n---\n`);
  }
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify(manifest, null, 2));
  return repo;
}

test('setPreset: 新建预设，去重并排序', () => {
  const repo = makeRepo(['a', 'b', 'c']);
  setPreset(repo, 'web', ['c', 'a', 'a', 'b']);
  const m = loadManifest(repo);
  assert.deepEqual(m.presets, { web: ['a', 'b', 'c'] });
});

test('setPreset: 同名覆盖', () => {
  const repo = makeRepo(['a', 'b'], { agents: {}, presets: { web: ['a'] } });
  setPreset(repo, 'web', ['b']);
  assert.deepEqual(loadManifest(repo).presets, { web: ['b'] });
});

test('deletePreset: 删除存在的预设', () => {
  const repo = makeRepo(['a'], { agents: {}, presets: { web: ['a'], cli: ['a'] } });
  deletePreset(repo, 'web');
  assert.deepEqual(loadManifest(repo).presets, { cli: ['a'] });
});

test('applyPreset: 并集追加，已有技能不重复，返回新增数', () => {
  const repo = makeRepo(['a', 'b', 'c'], {
    agents: { claude: ['a'] },
    presets: { web: ['a', 'b'] },
  });
  const r = applyPreset(repo, 'web', ['claude', 'cursor']);
  assert.deepEqual(r.added, { claude: 1, cursor: 2 });
  assert.deepEqual(r.missing, []);
  const m = loadManifest(repo);
  assert.deepEqual(m.agents.claude, ['a', 'b']);
  assert.deepEqual(m.agents.cursor, ['a', 'b']);
});

test('applyPreset: 预设中仓库不存在的技能跳过并计入 missing', () => {
  const repo = makeRepo(['a'], { agents: {}, presets: { web: ['a', 'ghost'] } });
  const r = applyPreset(repo, 'web', ['claude']);
  assert.deepEqual(r.added, { claude: 1 });
  assert.deepEqual(r.missing, ['ghost']);
  assert.deepEqual(loadManifest(repo).agents.claude, ['a']);
});

test('applyPreset: 预设不存在时抛错', () => {
  const repo = makeRepo(['a']);
  assert.throws(() => applyPreset(repo, 'nope', ['claude']), /不存在/);
});
