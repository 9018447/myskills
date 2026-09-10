import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, lstatSync, realpathSync } from 'node:fs';
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

function git(cwd: string, args: string[]) {
  const r = spawnSync('git', args, { cwd, env: { ...process.env, ...GIT_ENV }, encoding: 'utf8' });
  assert.equal(r.status, 0, `git ${args.join(' ')}: ${r.stderr}`);
  return r.stdout.trim();
}

// work 仓库 + origin 裸远程 + other 克隆（模拟另一台机器推送）
function makeRemoteFixture() {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const home = join(tmp, 'home');
  const remote = join(tmp, 'remote.git');
  const repo = join(tmp, 'repo');
  const other = join(tmp, 'other');
  git(tmp, ['init', '--bare', '-b', 'main', 'remote.git']);
  git(tmp, ['clone', 'remote.git', 'repo']);
  git(tmp, ['clone', 'remote.git', 'other']);

  mkdirSync(join(repo, 'alpha'), { recursive: true });
  writeFileSync(join(repo, 'alpha', 'SKILL.md'), '---\nname: alpha\n---\n');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }],
  }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: { claude: ['alpha'] } }));
  git(repo, ['add', '-A']);
  git(repo, ['commit', '-m', 'init']);
  git(repo, ['push', 'origin', 'main']);
  git(other, ['pull', 'origin', 'main']);
  mkdirSync(join(home, '.claude'), { recursive: true });
  return { tmp, repo, home, remote, other };
}

function run(args: string[], cwd: string) {
  return spawnSync('node', [CLI, ...args], { cwd, env: { ...process.env, ...GIT_ENV }, encoding: 'utf8' });
}

test('sync: pull 远端新提交，重建链接，状态文件提交并推送', () => {
  const { repo, home, remote, other } = makeRemoteFixture();

  // 另一台机器推了一个新技能 beta 并更新了清单
  mkdirSync(join(other, 'beta'), { recursive: true });
  writeFileSync(join(other, 'beta', 'SKILL.md'), '---\nname: beta\n---\n');
  writeFileSync(join(other, 'skills-manifest.json'), JSON.stringify({ agents: { claude: ['alpha', 'beta'] } }));
  git(other, ['add', '-A']);
  git(other, ['commit', '-m', 'add beta']);
  git(other, ['push', 'origin', 'main']);

  const before = git(repo, ['rev-parse', 'HEAD']);
  const r = run(['sync', '--remote', 'origin'], repo);
  assert.equal(r.status, 0, r.stderr);

  // pull 生效：HEAD 追上远端（sync 自己又推了状态提交，所以 HEAD == 远端最新）
  assert.equal(git(repo, ['rev-parse', 'HEAD']), git(remote, ['rev-parse', 'main']));
  assert.notEqual(git(repo, ['rev-parse', 'HEAD']), before);
  // link 生效：pull 下来的 beta 被链接
  const betaLink = join(home, '.claude', 'skills', 'beta');
  assert.ok(lstatSync(betaLink).isSymbolicLink());
  assert.equal(realpathSync(betaLink), realpathSync(join(repo, 'beta')));
  // status 提交并推送：远端能读到本机状态文件
  const remoteStatus = git(remote, ['show', `main:machines/${hostname()}.json`]);
  assert.equal(JSON.parse(remoteStatus).host, hostname());
});

test('sync: 本地无变化时不产生空提交', () => {
  const { repo, remote } = makeRemoteFixture();
  // 先跑一次 sync 建立状态文件
  assert.equal(run(['sync', '--remote', 'origin'], repo).status, 0);
  // 再跑一次：不允许失败
  const r = run(['sync', '--remote', 'origin'], repo);
  assert.equal(r.status, 0, r.stderr);
  // 远端与工作区一致
  assert.equal(git(repo, ['rev-parse', 'HEAD']), git(remote, ['rev-parse', 'main']));
});
