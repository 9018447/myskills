import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { skillDescription, validateSkillName, listRepoSkills } from '../src/core.ts';

function repoWithSkill(frontmatter: string): string {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-core-'));
  mkdirSync(join(repo, 's'), { recursive: true });
  writeFileSync(join(repo, 's', 'SKILL.md'), `---\n${frontmatter}\n---\n正文\n`);
  return repo;
}

test('skillDescription: 单行无引号', () => {
  assert.equal(skillDescription(repoWithSkill('name: s\ndescription: 简单描述'), 's'), '简单描述');
});

test('skillDescription: 双引号包裹（值内含冒号）', () => {
  assert.equal(skillDescription(repoWithSkill('description: "foo: bar"'), 's'), 'foo: bar');
});

test('skillDescription: 单引号包裹', () => {
  assert.equal(skillDescription(repoWithSkill("description: 'hello world'"), 's'), 'hello world');
});

test('skillDescription: 折叠块标量 >，换行折叠为空格', () => {
  const repo = repoWithSkill('description: >\n  第一行\n  第二行');
  assert.equal(skillDescription(repo, 's'), '第一行 第二行');
});

test('skillDescription: 保留块标量 |，保留换行', () => {
  const repo = repoWithSkill('description: |\n  line1\n  line2');
  assert.equal(skillDescription(repo, 's'), 'line1\nline2');
});

test('skillDescription: 带 chomping 标记的 >-，且不吞掉后续顶级键', () => {
  const repo = repoWithSkill('description: >-\n  描述文字\ntags: [a]');
  assert.equal(skillDescription(repo, 's'), '描述文字');
});

test('skillDescription: 折叠块中的空行分段', () => {
  const repo = repoWithSkill('description: >\n  第一段\n\n  第二段');
  assert.equal(skillDescription(repo, 's'), '第一段\n第二段');
});

test('skillDescription: 无 description 字段返回空串', () => {
  assert.equal(skillDescription(repoWithSkill('name: s'), 's'), '');
});

test('validateSkillName: 拒绝路径逃逸与隐藏目录', () => {
  for (const bad of ['../evil', '..', 'a/b', '.hidden', '']) {
    assert.throws(() => validateSkillName(bad), /非法技能名/);
  }
  for (const ok of ['alpha', 'my-skill', 'skill_v2', 'name.with.dots']) {
    validateSkillName(ok);
  }
});

test('listRepoSkills: 只列含 SKILL.md 的顶层目录，无 SKILL.md 的目录与顶层文件不列', () => {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-core-'));
  mkdirSync(join(repo, 'has-skill'));
  writeFileSync(join(repo, 'has-skill', 'SKILL.md'), '---\nname: has-skill\n---\n');
  mkdirSync(join(repo, 'collection')); // 目录但无 SKILL.md（集合目录/基础设施目录）
  writeFileSync(join(repo, 'plain.md'), 'x'); // 顶层文件
  assert.deepEqual(listRepoSkills(repo), ['has-skill']);
});

test('listRepoSkills: 符号链接按解析后的目标判定——指向含 SKILL.md 目录的链接才算技能', () => {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-core-'));
  const target = mkdtempSync(join(tmpdir(), 'myskills-core-target-'));
  mkdirSync(join(target, 'real-skill'));
  writeFileSync(join(target, 'real-skill', 'SKILL.md'), '---\nname: real-skill\n---\n');
  mkdirSync(join(target, 'not-skill'));
  mkdirSync(join(repo, 'has-skill'));
  writeFileSync(join(repo, 'has-skill', 'SKILL.md'), '---\nname: has-skill\n---\n');
  symlinkSync(join(target, 'real-skill'), join(repo, 'linked-skill')); // 链接 → 含 SKILL.md 目录：是技能
  symlinkSync(join(target, 'not-skill'), join(repo, 'linked-not-skill')); // 链接 → 无 SKILL.md 目录：不是
  symlinkSync(join(target, 'ghost'), join(repo, 'broken-link')); // 断链：不是
  assert.deepEqual(listRepoSkills(repo), ['has-skill', 'linked-skill']);
});
