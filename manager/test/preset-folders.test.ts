// 票 02：预设集文件夹事实模型——presets/<预设>/<技能>/ 存真身、顶层留相对符号链接。
// 覆盖：递归成员识别、启动 reconcile 幂等、断链清除、顶层重名冲突拒绝、移入预设的拒绝语义、CLI 启动接线
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, lstatSync, readlinkSync, readdirSync, renameSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { reconcilePresets, moveSkillToPreset, listPresets, presetMembers } from '../src/core.ts';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

function makeRepo(skills: string[]) {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-presetdir-'));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }, null, 2));
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents: [] }, null, 2));
  for (const s of skills) {
    mkdirSync(join(repo, s), { recursive: true });
    writeFileSync(join(repo, s, 'SKILL.md'), `---\nname: ${s}\n---\n`);
  }
  return repo;
}

// 在仓库内相对路径 rel 处造一个技能真身
function makeSkill(repo: string, rel: string) {
  mkdirSync(join(repo, rel), { recursive: true });
  writeFileSync(join(repo, rel, 'SKILL.md'), `---\nname: ${rel.split('/').pop()}\n---\n`);
}

// 顶层全部符号链接的 readlink 原始目标（幂等性对比用）
function topLinks(repo: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const e of readdirSync(repo, { withFileTypes: true })) {
    if (e.isSymbolicLink()) out[e.name] = readlinkSync(join(repo, e.name));
  }
  return out;
}

test('presetMembers: 递归下探识别成员；预设内非技能残留不参与', () => {
  const repo = makeRepo([]);
  makeSkill(repo, 'presets/foo/bar');
  makeSkill(repo, 'presets/foo/skills/baz'); // 嵌套一层中间目录
  writeFileSync(join(repo, 'presets/foo/CHANGELOG.md'), 'x');
  mkdirSync(join(repo, 'presets/foo/docs'), { recursive: true }); // 无 SKILL.md 的空目录
  assert.deepEqual(listPresets(repo), ['foo']);
  assert.deepEqual(
    presetMembers(repo).map((m) => ({ name: m.name, preset: m.preset, dir: m.dir })),
    [
      { name: 'bar', preset: 'foo', dir: 'presets/foo/bar' },
      { name: 'baz', preset: 'foo', dir: 'presets/foo/skills/baz' },
    ],
  );
});

test('presetMembers: 没有 presets/ 目录时返回空', () => {
  const repo = makeRepo(['a']);
  assert.deepEqual(listPresets(repo), []);
  assert.deepEqual(presetMembers(repo), []);
});

test('reconcile: 手工 mv 顶层技能进 presets/foo/ 后，顶层出现指向真身的相对符号链接；重复运行无变化', () => {
  const repo = makeRepo(['a', 'b']);
  mkdirSync(join(repo, 'presets/foo'), { recursive: true });
  renameSync(join(repo, 'b'), join(repo, 'presets/foo', 'b'));
  reconcilePresets(repo);
  assert.ok(lstatSync(join(repo, 'b')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'b')), 'presets/foo/b'); // 相对目标
  assert.ok(existsSync(join(repo, 'b', 'SKILL.md'))); // 经链接可读真身
  assert.ok(existsSync(join(repo, 'presets/foo/b/SKILL.md')));
  const before = topLinks(repo);
  reconcilePresets(repo);
  assert.deepEqual(topLinks(repo), before);
});

test('reconcile: 嵌套一层中间目录也能识别成员并在顶层建链', () => {
  const repo = makeRepo([]);
  makeSkill(repo, 'presets/foo/skills/bar');
  reconcilePresets(repo);
  assert.ok(lstatSync(join(repo, 'bar')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'bar')), 'presets/foo/skills/bar');
});

test('reconcile: 顶层已有指向成员的正确链接时不重复创建（内容不变）', () => {
  const repo = makeRepo([]);
  makeSkill(repo, 'presets/foo/bar');
  reconcilePresets(repo);
  const ctime = lstatSync(join(repo, 'bar')).ctimeMs;
  reconcilePresets(repo);
  assert.equal(lstatSync(join(repo, 'bar')).ctimeMs, ctime); // 未被重建
});

test('reconcile: 删除预设成员后，顶层残留断链在下次启动时被清除', () => {
  const repo = makeRepo([]);
  makeSkill(repo, 'presets/foo/bar');
  reconcilePresets(repo);
  rmSync(join(repo, 'presets/foo/bar'), { recursive: true });
  reconcilePresets(repo);
  assert.throws(() => lstatSync(join(repo, 'bar'))); // 断链条目本身被移除
});

test('reconcile: 顶层真身与预设成员重名时报错，说明双方位置，不动任何一方', () => {
  const repo = makeRepo(['dup']);
  makeSkill(repo, 'presets/foo/dup');
  assert.throws(
    () => reconcilePresets(repo),
    (err) => {
      const msg = (err as Error).message;
      return msg.includes(join(repo, 'dup')) && msg.includes(join(repo, 'presets/foo/dup'));
    },
  );
  // 双方原样保留
  assert.ok(existsSync(join(repo, 'dup/SKILL.md')));
  assert.ok(existsSync(join(repo, 'presets/foo/dup/SKILL.md')));
});

test('reconcile: 两个预设含同名成员时报错说明位置', () => {
  const repo = makeRepo([]);
  makeSkill(repo, 'presets/a/x');
  makeSkill(repo, 'presets/b/x');
  assert.throws(
    () => reconcilePresets(repo),
    (err) => {
      const msg = (err as Error).message;
      return msg.includes(join(repo, 'presets/a/x')) && msg.includes(join(repo, 'presets/b/x'));
    },
  );
});

test('moveSkillToPreset: 顶层真身移入预设，原地留相对符号链接，reconcile 幂等', () => {
  const repo = makeRepo(['x', 'y']);
  moveSkillToPreset(repo, 'foo', 'x');
  assert.ok(existsSync(join(repo, 'presets/foo/x/SKILL.md'))); // 真身
  assert.ok(lstatSync(join(repo, 'x')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'x')), 'presets/foo/x');
  const before = topLinks(repo);
  reconcilePresets(repo);
  assert.deepEqual(topLinks(repo), before);
});

test('moveSkillToPreset: 真身已归属其他预设时直接报错说明归属，不自动搬家', () => {
  const repo = makeRepo(['x']);
  moveSkillToPreset(repo, 'a', 'x');
  assert.throws(
    () => moveSkillToPreset(repo, 'b', 'x'),
    (err) => {
      const msg = (err as Error).message;
      return msg.includes('a') && msg.includes(join(repo, 'presets/a/x'));
    },
  );
  // 状态未变：仍在预设 a，未产生预设 b
  assert.ok(existsSync(join(repo, 'presets/a/x/SKILL.md')));
  assert.ok(!existsSync(join(repo, 'presets/b')));
});

test('moveSkillToPreset: 移回顶层后可再移入新预设', () => {
  const repo = makeRepo(['x']);
  moveSkillToPreset(repo, 'a', 'x');
  // 手工移回顶层：删链 + mv 真身
  rmSync(join(repo, 'x'));
  renameSync(join(repo, 'presets/a/x'), join(repo, 'x'));
  moveSkillToPreset(repo, 'b', 'x');
  assert.ok(existsSync(join(repo, 'presets/b/x/SKILL.md')));
  assert.equal(readlinkSync(join(repo, 'x')), 'presets/b/x');
});

test('moveSkillToPreset: 顶层不存在该技能时报错', () => {
  const repo = makeRepo(['x']);
  assert.throws(() => moveSkillToPreset(repo, 'foo', 'nope'), /顶层/);
  assert.throws(() => moveSkillToPreset(repo, 'foo', '../escape'), /非法/);
});

test('cli: 任意命令启动即执行 reconcile（含断链清除语义由 core 测试覆盖）', () => {
  const repo = makeRepo(['a']);
  mkdirSync(join(repo, 'presets/foo'), { recursive: true });
  renameSync(join(repo, 'a'), join(repo, 'presets/foo', 'a'));
  const r = spawnSync('node', [CLI, 'link'], { encoding: 'utf8', env: { ...process.env, MYSKILLS_ROOT: repo } });
  assert.equal(r.status, 0, r.stderr);
  assert.ok(lstatSync(join(repo, 'a')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'a')), 'presets/foo/a');
});

test('cli: 顶层真身与预设成员冲突时，命令报错退出非 0 并说明位置', () => {
  const repo = makeRepo(['dup']);
  makeSkill(repo, 'presets/foo/dup');
  const r = spawnSync('node', [CLI, 'status'], { encoding: 'utf8', env: { ...process.env, MYSKILLS_ROOT: repo } });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /dup/);
  assert.match(r.stderr, /presets\/foo\/dup/);
  // 双方原样保留
  assert.ok(existsSync(join(repo, 'dup/SKILL.md')));
  assert.ok(existsSync(join(repo, 'presets/foo/dup/SKILL.md')));
});
