import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, symlinkSync, existsSync, lstatSync, realpathSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

function makeSkill(repoRoot: string, name: string) {
  mkdirSync(join(repoRoot, name), { recursive: true });
  writeFileSync(join(repoRoot, name, 'SKILL.md'), `---\nname: ${name}\n---\n`);
}

function makeFixture(opts: {
  skills?: string[];
  manifest?: object;
  agents?: object[];
  installedAgents?: string[];
}) {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  mkdirSync(repo, { recursive: true });
  mkdirSync(home, { recursive: true });
  for (const s of opts.skills ?? []) makeSkill(repo, s);
  for (const a of opts.installedAgents ?? []) {
    // 模拟 agent 已安装：其 skills 目录的父目录存在
    mkdirSync(join(home, `.${a}`), { recursive: true });
  }
  const agents = (opts.agents ?? []).map((a: any) => ({
    ...a,
    skillsPath: a.skillsPath.replace('$HOME', home),
  }));
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents }, null, 2));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify(opts.manifest ?? { agents: {} }, null, 2));
  return { tmp, repo, home };
}

function run(args: string[], cwd: string, env: Record<string, string> = {}) {
  return spawnSync('node', [CLI, ...args], {
    cwd,
    env: { ...process.env, MYSKILLS_ROOT: cwd, ...env },
    encoding: 'utf8',
  });
}

test('link: 按清单为已安装的 agent 创建指向仓库的符号链接', () => {
  const { repo, home } = makeFixture({
    skills: ['alpha', 'beta'],
    manifest: { agents: { claude: ['alpha'] } },
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: '$HOME/.claude/skills' }],
    installedAgents: ['claude'],
  });

  const r = run(['link'], repo);
  assert.equal(r.status, 0, r.stderr);

  const link = join(home, '.claude', 'skills', 'alpha');
  assert.ok(lstatSync(link).isSymbolicLink(), 'alpha 应是符号链接');
  assert.equal(realpathSync(link), realpathSync(join(repo, 'alpha')));
  assert.ok(!existsSync(join(home, '.claude', 'skills', 'beta')), '未列入清单的 beta 不应被链接');
});

test('link: 未安装的 agent 被跳过，不影响其他 agent', () => {
  const { repo, home } = makeFixture({
    skills: ['alpha'],
    manifest: { agents: { claude: ['alpha'], cursor: ['alpha'] } },
    agents: [
      { id: 'claude', name: 'Claude Code', skillsPath: '$HOME/.claude/skills' },
      { id: 'cursor', name: 'Cursor', skillsPath: '$HOME/.cursor/skills' },
    ],
    installedAgents: ['claude'], // cursor 未安装
  });

  const r = run(['link'], repo);
  assert.equal(r.status, 0, r.stderr);
  assert.ok(lstatSync(join(home, '.claude', 'skills', 'alpha')).isSymbolicLink());
  assert.ok(!existsSync(join(home, '.cursor', 'skills')), '未安装的 agent 不应创建任何目录');
});

test('link: 移除指向仓库但已不在清单中的孤儿链接和断链，不动真实目录', () => {
  const { repo, home } = makeFixture({
    skills: ['alpha', 'orphan'],
    manifest: { agents: { claude: ['alpha'] } },
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: '$HOME/.claude/skills' }],
    installedAgents: ['claude'],
  });
  const skillsDir = join(home, '.claude', 'skills');
  mkdirSync(skillsDir, { recursive: true });
  // 孤儿：指向仓库但不在清单
  symlinkSync(join(repo, 'orphan'), join(skillsDir, 'orphan'), 'dir');
  // 断链：指向仓库里已不存在的目录
  symlinkSync(join(repo, 'gone'), join(skillsDir, 'gone'), 'dir');
  // 真实目录：不动
  mkdirSync(join(skillsDir, 'local-only'));
  // 指向仓库外的符号链接：不动
  mkdirSync(join(home, 'external-skill'), { recursive: true });
  symlinkSync(join(home, 'external-skill'), join(skillsDir, 'external'), 'dir');

  const r = run(['link'], repo);
  assert.equal(r.status, 0, r.stderr);

  assert.ok(!existsSync(join(skillsDir, 'orphan')), '孤儿链接应被移除');
  assert.throws(() => lstatSync(join(skillsDir, 'gone')), '断链应被移除');
  assert.ok(lstatSync(join(skillsDir, 'local-only')).isDirectory() && !lstatSync(join(skillsDir, 'local-only')).isSymbolicLink(), '真实目录不动');
  assert.equal(realpathSync(join(skillsDir, 'external')), realpathSync(join(home, 'external-skill')), '外部链接不动');
});

test('link: 在仓库外的任意目录运行，经 MYSKILLS_ROOT 仍作用于指定仓库', () => {
  const { tmp, repo, home } = makeFixture({
    skills: ['alpha'],
    manifest: { agents: { claude: ['alpha'] } },
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: '$HOME/.claude/skills' }],
    installedAgents: ['claude'],
  });

  const r = run(['link'], tmp, { MYSKILLS_ROOT: repo });
  assert.equal(r.status, 0, r.stderr);
  assert.ok(lstatSync(join(home, '.claude', 'skills', 'alpha')).isSymbolicLink());
});

test('link: 清单中的技能在仓库不存在时警告并跳过，退出码仍为 0', () => {
  const { repo, home } = makeFixture({
    skills: ['alpha'],
    manifest: { agents: { claude: ['alpha', 'ghost'] } },
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: '$HOME/.claude/skills' }],
    installedAgents: ['claude'],
  });

  const r = run(['link'], repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout + r.stderr, /ghost/);
  assert.ok(!existsSync(join(home, '.claude', 'skills', 'ghost')));
  assert.ok(lstatSync(join(home, '.claude', 'skills', 'alpha')).isSymbolicLink());
});
