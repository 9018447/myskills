import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { skillDescription, validateSkillName } from '../src/core.ts';

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
