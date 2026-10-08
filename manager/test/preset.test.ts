// 票 03：预设集管理/分发走文件夹事实模型——presets/<预设>/<技能>/ 存真身，成员一律读文件夹，
// presetApplied（应用关系）仍记在 skills-manifest.json。覆盖：setPreset 增减成员、createPreset、
// deletePreset、moveSkillToTop、applyPreset 互斥接管与 missing、link 传播随成员增减
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, existsSync, lstatSync, readlinkSync, realpathSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  setPreset, createPreset, deletePreset, moveSkillToTop, applyPreset,
  loadManifest, link, listPresets, presetMembers,
} from '../src/core.ts';

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

// 顶层条目是真身目录（非符号链接）
function isRealDir(p: string): boolean {
  const st = lstatSync(p);
  return st.isDirectory() && !st.isSymbolicLink();
}

test('setPreset: 新建预设——成员真身移入 presets/<名>/，顶层留相对符号链接，manifest 不写 presets 字段', () => {
  const repo = makeRepo(['a', 'b', 'c']);
  setPreset(repo, 'web', ['c', 'a', 'a', 'b']); // 去重
  assert.deepEqual(listPresets(repo), ['web']);
  assert.deepEqual(presetMembers(repo).map((m) => m.name), ['a', 'b', 'c']);
  for (const s of ['a', 'b', 'c']) {
    assert.ok(existsSync(join(repo, 'presets/web', s, 'SKILL.md')), `${s} 真身应在预设文件夹`);
    assert.ok(lstatSync(join(repo, s)).isSymbolicLink(), `顶层 ${s} 应是符号链接`);
    assert.equal(readlinkSync(join(repo, s)), join('presets/web', s)); // 相对目标
  }
  assert.equal('presets' in loadManifest(repo), false, '清单不应再有 presets 字段');
});

test('setPreset: 编辑成员——移出的回顶层变真身，新增的从顶层移入', () => {
  const repo = makeRepo(['a', 'b', 'c']);
  setPreset(repo, 'web', ['a', 'b']);
  setPreset(repo, 'web', ['a', 'c']);
  assert.ok(isRealDir(join(repo, 'b')), 'b 移回顶层应变真身');
  assert.ok(existsSync(join(repo, 'presets/web/c/SKILL.md')), 'c 真身应在预设文件夹');
  assert.ok(lstatSync(join(repo, 'c')).isSymbolicLink(), '顶层 c 应是符号链接');
  assert.deepEqual(presetMembers(repo).map((m) => m.name), ['a', 'c']);
});

test('setPreset: 加入已归属其他预设的技能时报错，双方完全不动', () => {
  const repo = makeRepo(['a', 'b']);
  setPreset(repo, 'web', ['a']);
  assert.throws(() => setPreset(repo, 'cli', ['a', 'b']), /已归属预设 web/);
  assert.equal(existsSync(join(repo, 'presets/cli')), false, '失败的预设不应留下文件夹');
  assert.ok(existsSync(join(repo, 'presets/web/a/SKILL.md')), '原预设成员不动');
  assert.ok(isRealDir(join(repo, 'b')), '顶层技能不被卷入');
});

test('setPreset: 勾选了顶层不存在的技能时报错', () => {
  const repo = makeRepo(['a']);
  assert.throws(() => setPreset(repo, 'web', ['ghost']), /仓库顶层没有技能 ghost/);
  assert.equal(existsSync(join(repo, 'presets/web')), false);
});

test('createPreset: 空文件夹即预设；重名与非法名拒绝', () => {
  const repo = makeRepo(['a']);
  createPreset(repo, 'web');
  assert.deepEqual(listPresets(repo), ['web']);
  assert.deepEqual(presetMembers(repo), []);
  assert.throws(() => createPreset(repo, 'web'), /已存在/);
  assert.throws(() => createPreset(repo, '../x'), /非法预设名/);
});

test('moveSkillToTop: 真身回顶层替换符号链接，嵌套成员按真实目录归位', () => {
  const repo = makeRepo([]);
  mkdirSync(join(repo, 'presets/web/sub/x'), { recursive: true }); // 嵌套成员（未 reconcile，顶层无链接）
  writeFileSync(join(repo, 'presets/web/sub/x/SKILL.md'), '---\nname: x\n---\n');
  moveSkillToTop(repo, 'web', 'x');
  assert.ok(isRealDir(join(repo, 'x')), 'x 回顶层变真身');
  assert.equal(existsSync(join(repo, 'presets/web/sub/x')), false);
  assert.deepEqual(presetMembers(repo), []);
});

test('moveSkillToTop: 预设里没有该技能时报错', () => {
  const repo = makeRepo(['a']);
  setPreset(repo, 'web', ['a']);
  assert.throws(() => moveSkillToTop(repo, 'web', 'nope'), /没有技能 nope/);
});

test('deletePreset: 成员全部移回顶层、文件夹删除、presetApplied 清除且不影响其他预设', () => {
  const repo = makeRepo(['a', 'b', 'c'], { agents: {}, presetApplied: { web: ['claude'], cli: ['claude'] } });
  setPreset(repo, 'web', ['a', 'b']);
  setPreset(repo, 'cli', ['c']);
  deletePreset(repo, 'web');
  assert.equal(existsSync(join(repo, 'presets/web')), false, '预设文件夹应删除');
  assert.ok(isRealDir(join(repo, 'a')), '成员 a 回顶层变真身');
  assert.ok(isRealDir(join(repo, 'b')), '成员 b 回顶层变真身');
  assert.deepEqual(presetMembers(repo).map((m) => m.name), ['c'], '其他预设不受影响');
  assert.deepEqual(loadManifest(repo).presetApplied, { cli: ['claude'] });
});

test('deletePreset: 顶层被真实目录占用时拒绝，不动预设成员', () => {
  const repo = makeRepo(['a']);
  setPreset(repo, 'web', ['a']);
  rmSync(join(repo, 'a')); // 模拟未 reconcile 的顶层冲突：真身目录挡在链接位置上
  mkdirSync(join(repo, 'a'));
  writeFileSync(join(repo, 'a/SKILL.md'), '---\nname: a\n---\n');
  assert.throws(() => deletePreset(repo, 'web'), /已被占用/);
  assert.ok(existsSync(join(repo, 'presets/web/a/SKILL.md')), '预设成员不动');
});

test('applyPreset: 互斥接管——应用后预设成员从个人清单移出，改由预设管', () => {
  const repo = makeRepo(['a', 'b', 'c'], { agents: { claude: ['a'] } });
  setPreset(repo, 'web', ['a', 'b']);
  const r = applyPreset(repo, 'web', ['claude', 'cursor']);
  // claude 已有 a（被接管，链接不变），新增计 1；cursor 全新，计 2
  assert.deepEqual(r.added, { claude: 1, cursor: 2 });
  assert.deepEqual(r.missing, []);
  const m = loadManifest(repo);
  assert.deepEqual(m.agents.claude, []); // a 从个人清单移出，由预设管
  assert.equal(m.agents.cursor, undefined);
  assert.deepEqual(m.presetApplied, { web: ['claude', 'cursor'] });
});

test('applyPreset: 未 reconcile 的预设成员（顶层无链接）计入 missing，应用关系照记', () => {
  const repo = makeRepo(['a']);
  setPreset(repo, 'web', ['a']);
  mkdirSync(join(repo, 'presets/web/ghost'), { recursive: true }); // 手工放入、未经 reconcile 建顶层链接
  writeFileSync(join(repo, 'presets/web/ghost/SKILL.md'), '---\nname: ghost\n---\n');
  const r = applyPreset(repo, 'web', ['claude']);
  assert.deepEqual(r.added, { claude: 1 });
  assert.deepEqual(r.missing, ['ghost']);
  assert.deepEqual(loadManifest(repo).presetApplied, { web: ['claude'] });
});

test('applyPreset: 预设文件夹不存在时抛错', () => {
  const repo = makeRepo(['a']);
  assert.throws(() => applyPreset(repo, 'nope', ['claude']), /不存在/);
});

test('applyPreset: 记录 presetApplied，重复应用不重复记录', () => {
  const repo = makeRepo(['a']);
  setPreset(repo, 'web', ['a']);
  applyPreset(repo, 'web', ['claude']);
  applyPreset(repo, 'web', ['claude', 'cursor']);
  assert.deepEqual(loadManifest(repo).presetApplied, { web: ['claude', 'cursor'] });
});

test('applyPreset: 取消勾选即撤销应用，link 移除该预设的链接，其他预设不受影响', () => {
  const { repo, skillsDir } = makeLinkedRepo(['a', 'b', 'c'], { agents: { claude: [] } });
  setPreset(repo, 'web', ['a', 'b']);
  setPreset(repo, 'cli', ['c']);
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

test('link: 已应用预设的成员随 link 传播，成员增减后链接随之增减，最终解析到真身', () => {
  const { repo, skillsDir } = makeLinkedRepo(['a', 'b', 'c'], { agents: { claude: ['a'] } });
  setPreset(repo, 'web', ['a', 'b']);
  applyPreset(repo, 'web', ['claude']); // 互斥接管：a 从个人清单移出
  link(repo);
  assert.deepEqual(loadManifest(repo).agents.claude, [], 'link 只按并集建链，不回写清单');
  assert.ok(existsSync(join(skillsDir, 'b')));
  assert.equal(realpathSync(join(skillsDir, 'b')), join(repo, 'presets/web/b'), 'agent 链接应最终解析到预设内真身');
  setPreset(repo, 'web', ['a', 'b', 'c']); // 编辑预设加 c
  link(repo);
  assert.ok(lstatSync(join(skillsDir, 'c')).isSymbolicLink(), '新增成员随 link 传播');
  setPreset(repo, 'web', ['a']); // 移出 b、c
  link(repo);
  assert.equal(existsSync(join(skillsDir, 'b')), false, '移出的成员链接被清理');
  assert.equal(existsSync(join(skillsDir, 'c')), false);
  assert.ok(existsSync(join(skillsDir, 'a')), '仍在预设中的成员不受影响');
});

test('link: presetApplied 指向已不存在的预设文件夹时不崩，按空成员处理', () => {
  const { repo, skillsDir } = makeLinkedRepo(['a'], { agents: { claude: [] }, presetApplied: { gone: ['claude'] } });
  link(repo);
  assert.equal(existsSync(join(skillsDir, 'a')), false);
});
