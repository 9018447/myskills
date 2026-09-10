import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, symlinkSync, lstatSync } from 'node:fs';
import { tmpdir, hostname } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

const GIT_ENV = {
  GIT_AUTHOR_NAME: 'test',
  GIT_AUTHOR_EMAIL: 'test@test',
  GIT_COMMITTER_NAME: 'test',
  GIT_COMMITTER_EMAIL: 'test@test',
};

function git(repo: string, args: string[]) {
  const r = spawnSync('git', args, { cwd: repo, env: { ...process.env, ...GIT_ENV }, encoding: 'utf8' });
  assert.equal(r.status, 0, `git ${args.join(' ')}: ${r.stderr}`);
  return r.stdout.trim();
}

function makeGitRepo() {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  mkdirSync(join(repo, 'alpha'), { recursive: true });
  writeFileSync(join(repo, 'alpha', 'SKILL.md'), '---\nname: alpha\n---\n');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }],
  }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: { claude: ['alpha'] } }));
  mkdirSync(join(home, '.claude'), { recursive: true });
  git(repo, ['init', '-b', 'main']);
  git(repo, ['add', '-A']);
  git(repo, ['commit', '-m', 'init']);
  return { tmp, repo, home };
}

function run(args: string[], cwd: string) {
  return spawnSync('node', [CLI, ...args], { cwd, env: { ...process.env, ...GIT_ENV }, encoding: 'utf8' });
}

test('status: 写入 machines/<hostname>.json，含当前 sha 与分支', () => {
  const { repo } = makeGitRepo();
  const r = run(['status'], repo);
  assert.equal(r.status, 0, r.stderr);

  const file = join(repo, 'machines', `${hostname()}.json`);
  const s = JSON.parse(readFileSync(file, 'utf8'));
  assert.equal(s.host, hostname());
  assert.equal(s.sha, git(repo, ['rev-parse', 'HEAD']));
  assert.equal(s.branch, 'main');
  assert.ok(!Number.isNaN(Date.parse(s.updatedAt)), 'updatedAt 应是 ISO 时间');
});

test('status: 统计指向仓库的有效链接数与断链数', () => {
  const { repo, home } = makeGitRepo();
  const skillsDir = join(home, '.claude', 'skills');
  mkdirSync(skillsDir, { recursive: true });
  symlinkSync(join(repo, 'alpha'), join(skillsDir, 'alpha'), 'dir'); // 有效
  symlinkSync(join(repo, 'gone'), join(skillsDir, 'gone'), 'dir'); // 断链
  mkdirSync(join(skillsDir, 'local-real')); // 真实目录不计入

  const r = run(['status'], repo);
  assert.equal(r.status, 0, r.stderr);

  const s = JSON.parse(readFileSync(join(repo, 'machines', `${hostname()}.json`), 'utf8'));
  assert.equal(s.agents.claude.linked, 1);
  assert.equal(s.brokenLinks, 1);
});
