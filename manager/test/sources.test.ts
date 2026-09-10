import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { skillSources, agentProjectGroup } from '../src/core.ts';

function makeGitRepo() {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-sources-'));
  const g = (args: string[]) => {
    const r = spawnSync('git', args, { cwd: repo, encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
  };
  g(['init', '-q']);
  g(['config', 'user.email', 'test@example.com']);
  g(['config', 'user.name', 'test']);
  return { repo, g };
}

function addSkill(repo: string, g: (a: string[]) => void, name: string, message: string) {
  mkdirSync(join(repo, name), { recursive: true });
  writeFileSync(join(repo, name, 'SKILL.md'), `---\nname: ${name}\n---\n`);
  g(['add', name]);
  g(['commit', '-q', '-m', message]);
}

function writeManifest(repo: string, manifest: object) {
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify(manifest, null, 2));
}

test('skillSources: 从 git 历史推断 install 来源（含子目录）', () => {
  const { repo, g } = makeGitRepo();
  writeManifest(repo, { agents: {} });
  addSkill(repo, g, 'whole-repo', 'feat: 安装技能 whole-repo（来自 github.com/alice/tools）');
  addSkill(repo, g, 'sub-dir', 'feat: 安装技能 sub-dir（来自 github.com/bob/collection 的 skills/sub-dir）');
  addSkill(repo, g, 'hand-made', 'feat: 手写技能 hand-made');
  const sources = skillSources(repo);
  assert.equal(sources['whole-repo'], 'alice/tools');
  assert.equal(sources['sub-dir'], 'bob/collection/skills/sub-dir');
  assert.equal(sources['hand-made'], 'local');
});

test('skillSources: manifest.sources 优先于 git 推断', () => {
  const { repo, g } = makeGitRepo();
  addSkill(repo, g, 'whole-repo', 'feat: 安装技能 whole-repo（来自 github.com/alice/tools）');
  writeManifest(repo, { agents: {}, sources: { 'whole-repo': 'override/recorded' } });
  assert.equal(skillSources(repo)['whole-repo'], 'override/recorded');
});

test('agentProjectGroup: 家目录下的路径算「全局」，否则取点开头的段之前的路径', () => {
  assert.equal(agentProjectGroup({ id: 'claude', name: '', skillsPath: '~/.claude/skills' }), '全局');
  const home = process.env.HOME!;
  assert.equal(agentProjectGroup({ id: 'x', name: '', skillsPath: `${home}/proj-a/.claude/skills` }), `${home}/proj-a`);
  assert.equal(agentProjectGroup({ id: 'y', name: '', skillsPath: '/opt/proj/.agents/skills' }), '/opt/proj');
});
