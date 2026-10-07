import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, lstatSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setPreset, deletePreset, applyPreset, loadManifest, link } from '../src/core.ts';

function makeRepo(skills: string[], manifest: object = { agents: {} }) {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-preset-'));
  for (const s of skills) {
    mkdirSync(join(repo, s), { recursive: true });
    writeFileSync(join(repo, s, 'SKILL.md'), `---\nname: ${s}\n---\n`);
  }
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify(manifest, null, 2));
  return repo;
}

// 带 agent 注册表与已安装 skills 目录的 fixture，供 link 传播测试用
function makeLinkedRepo(skills: string[], manifest: object) {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-preset-link-'));
  const repo = join(tmp, 'repo');
  mkdirSync(repo, { recursive: true });
  for (const s of skills) {
    mkdirSync(join(repo, s), { recursive: true });
    writeFileSync(join(repo, s, 'SKILL.md'), `---\nname: ${s}\n---\n`);
  }
  const skillsDir = join(tmp, 'claude-skills');
  mkdirSync(skillsDir, { recursive: true }); // 父目录存在 = agent 已安装
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents: [{ id: 'claude', name: 'Claude', skillsPath: skillsDir }] }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify(manifest, null, 2));
  return { repo, skillsDir };
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

test('applyPreset: 只记录应用关系，不并入 agents 清单（预设是独立单元）', () => {
  const repo = makeRepo(['a', 'b', 'c'], {
    agents: { claude: ['a'] },
    presets: { web: ['a', 'b'] },
  });
  const r = applyPreset(repo, 'web', ['claude', 'cursor']);
  // claude 已有 a，新增计 1；cursor 全新，计 2
  assert.deepEqual(r.added, { claude: 1, cursor: 2 });
  assert.deepEqual(r.missing, []);
  const m = loadManifest(repo);
  assert.deepEqual(m.agents.claude, ['a']); // 不烘焙进 agent 清单
  assert.equal(m.agents.cursor, undefined);
  assert.deepEqual(m.presetApplied, { web: ['claude', 'cursor'] });
});

test('applyPreset: 预设中仓库不存在的技能跳过并计入 missing', () => {
  const repo = makeRepo(['a'], { agents: {}, presets: { web: ['a', 'ghost'] } });
  const r = applyPreset(repo, 'web', ['claude']);
  assert.deepEqual(r.added, { claude: 1 });
  assert.deepEqual(r.missing, ['ghost']);
  assert.equal(loadManifest(repo).agents.claude, undefined); // 不并入 agent 清单
});

test('applyPreset: 预设不存在时抛错', () => {
  const repo = makeRepo(['a']);
  assert.throws(() => applyPreset(repo, 'nope', ['claude']), /不存在/);
});

test('applyPreset: 记录 presetApplied，重复应用不重复记录', () => {
  const repo = makeRepo(['a'], { agents: {}, presets: { web: ['a'] } });
  applyPreset(repo, 'web', ['claude']);
  applyPreset(repo, 'web', ['claude', 'cursor']);
  assert.deepEqual(loadManifest(repo).presetApplied, { web: ['claude', 'cursor'] });
});

test('applyPreset: 取消勾选即撤销应用，link 移除该预设的链接，其他预设不受影响', () => {
  const { repo, skillsDir } = makeLinkedRepo(['a', 'b', 'c'], {
    agents: { claude: [] },
    presets: { web: ['a', 'b'], cli: ['c'] },
  });
  applyPreset(repo, 'web', ['claude']);
  applyPreset(repo, 'cli', ['claude']);
  link(repo);
  assert.equal(existsSync(join(skillsDir, 'b')), true);
  assert.equal(existsSync(join(skillsDir, 'c')), true);
  applyPreset(repo, 'web', []); // 撤销 web，保留 cli
  link(repo);
  assert.equal(existsSync(join(skillsDir, 'a')), false);
  assert.equal(existsSync(join(skillsDir, 'b')), false);
  assert.equal(existsSync(join(skillsDir, 'c')), true);
  assert.deepEqual(loadManifest(repo).presetApplied, { web: [], cli: ['claude'] });
});

test('deletePreset: 同时清除 presetApplied 记录', () => {
  const repo = makeRepo(['a'], { agents: {}, presets: { web: ['a'] }, presetApplied: { web: ['claude'] } });
  deletePreset(repo, 'web');
  const m = loadManifest(repo);
  assert.equal(m.presets?.web, undefined);
  assert.equal(m.presetApplied?.web, undefined);
});

test('link: 预设应用到 agent 后，新增预设成员随 link 传播', () => {
  const { repo, skillsDir } = makeLinkedRepo(['a', 'b', 'c'], {
    agents: { claude: ['a'] },
    presets: { web: ['a', 'b'] },
    presetApplied: { web: ['claude'] },
  });
  link(repo);
  // link 只按清单并集建链，不回写 manifest.agents
  assert.deepEqual(loadManifest(repo).agents.claude, ['a']);
  assert.equal(existsSync(join(skillsDir, 'b')), true);
  // 编辑预设加 c，再 link：传播到已应用的 agent
  setPreset(repo, 'web', ['a', 'b', 'c']);
  link(repo);
  assert.equal(existsSync(join(skillsDir, 'c')), true);
  assert.equal(lstatSync(join(skillsDir, 'c')).isSymbolicLink(), true);
});
