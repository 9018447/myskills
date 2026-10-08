// 票 04：存量迁移——JSON 预设成员落地 presets/、顶层集合目录归位（嵌套集合平铺）、清空废弃的 presets 字段。
// 覆盖：三类迁移对象、失效成员剔除、同名重复真身剔除、豁免目录、幂等、迁移前后 link 链接守恒
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readdirSync, readFileSync, existsSync, lstatSync, readlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { migratePresetFolders } from '../src/migrate-preset-folders.ts';
import { link, listPresets, presetMembers } from '../src/core.ts';

function makeRepo(skills: string[]) {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-migpreset-'));
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

function writeManifest(repo: string, manifest: Record<string, unknown>) {
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
}

// 顶层全部符号链接的 readlink 原始目标（幂等性对比用）
function topLinks(repo: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const e of readdirSync(repo, { withFileTypes: true })) {
    if (e.isSymbolicLink()) out[e.name] = readlinkSync(join(repo, e.name));
  }
  return out;
}

test('成员已被手工移进预设文件夹时不再误报剔除', () => {
  const repo = makeRepo([]);
  mkdirSync(join(repo, 'presets/foo/x'), { recursive: true });
  writeFileSync(join(repo, 'presets/foo/x/SKILL.md'), '---\nname: x\n---\n');
  writeManifest(repo, {
    agents: { claude: [] },
    presets: { foo: ['x'] },
    presetApplied: { foo: ['claude'] },
  });
  const report = migratePresetFolders(repo);

  assert.ok(existsSync(join(repo, 'presets/foo/x/SKILL.md')));
  assert.ok(lstatSync(join(repo, 'x')).isSymbolicLink());
  assert.deepEqual(report.droppedMembers, {});
  assert.deepEqual(report.movedMembers, {});
  assert.deepEqual(report.memberCounts, { foo: 1 });
});

test('JSON 预设成员移入 presets/；失效成员剔除进报告；presets 字段清空、presetApplied 原样', () => {
  const repo = makeRepo(['a', 'b']);
  writeManifest(repo, {
    agents: { claude: [] },
    presets: { foo: ['a', 'b', 'gone-x'] },
    sources: { a: 'owner/repo' },
    presetApplied: { foo: ['claude'] },
  });
  const report = migratePresetFolders(repo);

  // 真身移入预设文件夹，顶层变相对符号链接
  assert.ok(existsSync(join(repo, 'presets/foo/a/SKILL.md')));
  assert.ok(lstatSync(join(repo, 'a')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'a')), 'presets/foo/a');
  assert.ok(lstatSync(join(repo, 'b')).isSymbolicLink());

  // 清单：presets 字段消失，其余键原样带过
  const manifest = JSON.parse(readFileSync(join(repo, 'skills-manifest.json'), 'utf8'));
  assert.ok(!('presets' in manifest));
  assert.deepEqual(manifest.presetApplied, { foo: ['claude'] });
  assert.deepEqual(manifest.agents, { claude: [] });
  assert.deepEqual(manifest.sources, { a: 'owner/repo' });

  // 报告
  assert.deepEqual(report.movedMembers, { foo: ['a', 'b'] });
  assert.deepEqual(report.droppedMembers, { foo: ['gone-x'] });
  assert.ok(report.clearedPresetsField);
  assert.deepEqual(report.memberCounts, { foo: 2 });
});

test('普通集合目录整体移入 presets/ 成为预设，子技能在顶层获得符号链接', () => {
  const repo = makeRepo(['solo']);
  makeSkill(repo, 'coll/s1');
  makeSkill(repo, 'coll/s2');
  const report = migratePresetFolders(repo);

  assert.ok(existsSync(join(repo, 'presets/coll/s1/SKILL.md')));
  assert.ok(existsSync(join(repo, 'presets/coll/s2/SKILL.md')));
  assert.ok(!existsSync(join(repo, 'coll'))); // 顶层集合目录消失
  assert.equal(readlinkSync(join(repo, 's1')), 'presets/coll/s1');
  assert.equal(readlinkSync(join(repo, 's2')), 'presets/coll/s2');
  assert.ok(lstatSync(join(repo, 'solo')).isDirectory()); // 未入预设的顶层技能真身不动
  assert.deepEqual(report.movedCollections, { coll: ['s1', 's2'] });
  assert.deepEqual(report.memberCounts, { coll: 2 });
  assert.deepEqual(listPresets(repo), ['coll']);
});

test('嵌套集合拆除中间层平铺到第一层；残留文件留在预设文件夹内且不是成员', () => {
  const repo = makeRepo([]);
  makeSkill(repo, 'nest/skills/deep1');
  makeSkill(repo, 'nest/skills/cat/deep2');
  writeFileSync(join(repo, 'nest/CHANGELOG.md'), 'x');
  mkdirSync(join(repo, 'nest/docs'), { recursive: true });
  writeFileSync(join(repo, 'nest/docs/guide.md'), 'x');
  writeFileSync(join(repo, 'nest/.hidden'), 'x');
  mkdirSync(join(repo, 'nest/.github'), { recursive: true });
  writeFileSync(join(repo, 'nest/.github/wf.yaml'), 'x');
  writeFileSync(join(repo, 'nest/skills/NOTES.md'), 'x'); // 中间层残留：skills/ 因此保留
  const report = migratePresetFolders(repo);

  // 子技能平铺到第一层并建链
  assert.ok(existsSync(join(repo, 'presets/nest/deep1/SKILL.md')));
  assert.ok(existsSync(join(repo, 'presets/nest/deep2/SKILL.md')));
  assert.equal(readlinkSync(join(repo, 'deep1')), 'presets/nest/deep1');
  assert.equal(readlinkSync(join(repo, 'deep2')), 'presets/nest/deep2');
  assert.ok(!existsSync(join(repo, 'presets/nest/skills/cat'))); // 技能搬空的中间层被拆除
  assert.ok(existsSync(join(repo, 'presets/nest/skills/NOTES.md'))); // 有残留的中间层保留

  // 残留文件留在预设文件夹内，不被识别为成员、不在顶层出现
  assert.ok(existsSync(join(repo, 'presets/nest/CHANGELOG.md')));
  assert.ok(existsSync(join(repo, 'presets/nest/docs/guide.md')));
  assert.ok(existsSync(join(repo, 'presets/nest/.github/wf.yaml')));
  assert.ok(!existsSync(join(repo, 'CHANGELOG.md')));
  assert.deepEqual(presetMembers(repo).map((m) => m.name), ['deep1', 'deep2']);
  assert.deepEqual(report.movedCollections, { nest: ['deep1', 'deep2'] });
});

test('集合子技能与顶层真身/其他预设成员同名：剔除集合副本并记入报告', () => {
  const repo = makeRepo(['dup']);
  writeManifest(repo, { agents: {}, presets: { foo: ['dup'] } });
  makeSkill(repo, 'coll/x/dup'); // 与 JSON 预设成员同名（另一场景：与顶层未入预设技能同名）
  makeSkill(repo, 'coll/x/keep');
  makeSkill(repo, 'coll/y/top-free'); // 与顶层未入预设的真身同名
  makeSkill(repo, 'top-free'); // 顶层真身，不属于任何预设
  const report = migratePresetFolders(repo);

  // 与预设 foo 的成员同名 → 集合副本被剔除
  assert.ok(!existsSync(join(repo, 'presets/coll/x/dup')));
  assert.ok(existsSync(join(repo, 'presets/coll/keep/SKILL.md')));
  assert.ok(!existsSync(join(repo, 'presets/coll/y/top-free'))); // 与顶层真身同名 → 剔除
  assert.deepEqual(presetMembers(repo).map((m) => m.name).sort(), ['dup', 'keep']);
  const removed = report.removedDuplicates.map((d) => `${d.preset}:${d.name}`).sort();
  assert.deepEqual(removed, ['coll:dup', 'coll:top-free']);
  assert.ok(report.removedDuplicates.every((d) => d.from.startsWith('presets/coll/') && d.reason.length > 0));
});

test('豁免目录、点开头目录、无子技能目录与普通文件不动', () => {
  const repo = makeRepo(['plain']);
  makeSkill(repo, 'testdir/sub/s'); // 豁免目录内的技能不迁移
  makeSkill(repo, '.dotdir/s');
  makeSkill(repo, 'empty-target'); // 自身是技能 → 顶层真身不动
  mkdirSync(join(repo, 'justadir')); // 空目录（无子技能）不动
  writeFileSync(join(repo, 'notes.txt'), 'x');
  const report = migratePresetFolders(repo);

  assert.ok(existsSync(join(repo, 'testdir/sub/s/SKILL.md')));
  assert.ok(existsSync(join(repo, '.dotdir/s/SKILL.md')));
  assert.ok(existsSync(join(repo, 'justadir')));
  assert.ok(existsSync(join(repo, 'notes.txt')));
  assert.ok(lstatSync(join(repo, 'empty-target')).isDirectory());
  assert.deepEqual(report.movedMembers, {});
  assert.deepEqual(report.movedCollections, {});
  assert.deepEqual(report.removedDuplicates, []);
  assert.deepEqual(listPresets(repo), []);
});

test('幂等：重复执行无任何改动，报告为空操作', () => {
  const repo = makeRepo(['a', 'free']);
  writeManifest(repo, { agents: {}, presets: { foo: ['a', 'gone'] }, presetApplied: { foo: ['claude'] } });
  makeSkill(repo, 'coll/s1');
  makeSkill(repo, 'nest/skills/deep');
  const first = migratePresetFolders(repo);

  const linksBefore = topLinks(repo);
  const manifestBefore = readFileSync(join(repo, 'skills-manifest.json'), 'utf8');
  const second = migratePresetFolders(repo);

  assert.deepEqual(topLinks(repo), linksBefore);
  assert.equal(readFileSync(join(repo, 'skills-manifest.json'), 'utf8'), manifestBefore);
  assert.deepEqual(second.movedMembers, {});
  assert.deepEqual(second.droppedMembers, {});
  assert.deepEqual(second.movedCollections, {});
  assert.deepEqual(second.removedDuplicates, []);
  assert.ok(!second.clearedPresetsField);
  assert.deepEqual(second.reconcileLines, []);
  assert.deepEqual(second.memberCounts, first.memberCounts);
});

test('link 守恒：迁移前 link → 迁移 → 迁移后 link，各 agent 链接集合不减', () => {
  const repo = makeRepo(['a', 'b']);
  const skillsDir = mkdtempSync(join(tmpdir(), 'myskills-migagent-'));
  writeFileSync(
    join(repo, 'agents.json'),
    JSON.stringify({ agents: [{ id: 'claude', name: 'Claude', skillsPath: join(skillsDir, 'skills') }] }, null, 2),
  );
  writeManifest(repo, { agents: { claude: ['b'] }, presets: { foo: ['a', 'b'] }, presetApplied: { foo: ['claude'] } });

  link(repo); // 迁移前：presets/ 文件夹不存在，claude 只装个人清单 b
  const before = readdirSync(join(skillsDir, 'skills')).sort();

  migratePresetFolders(repo);
  link(repo); // 迁移后：已应用预设 foo 的文件夹成员并入
  const after = readdirSync(join(skillsDir, 'skills')).sort();

  assert.deepEqual(before, ['b']);
  assert.deepEqual(after, ['a', 'b']);
  for (const name of before) assert.ok(after.includes(name), `迁移后缺少 ${name}`);
});
