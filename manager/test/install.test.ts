import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, chmodSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
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

// 构造 GitHub tarball：顶层一层目录（owner-repo-sha/），里面放给定的文件树
function makeTarball(tmp: string, topDir: string, files: Record<string, string>): string {
  const srcRoot = join(tmp, 'tar-src');
  for (const [rel, content] of Object.entries(files)) {
    const p = join(srcRoot, topDir, rel);
    mkdirSync(dirname(p), { recursive: true });
    writeFileSync(p, content);
  }
  const tarball = join(tmp, 'fixture.tar.gz');
  const r = spawnSync('tar', ['-czf', tarball, '-C', srcRoot, topDir], { encoding: 'utf8' });
  assert.equal(r.status, 0, r.stderr);
  return tarball;
}

// 桩 gh：对 `gh api ...` 把预制 tarball 写到 stdout
function makeGhStub(tmp: string, tarball: string): string {
  const binDir = join(tmp, 'bin');
  mkdirSync(binDir, { recursive: true });
  const stub = join(binDir, 'gh');
  writeFileSync(stub, '#!/usr/bin/env bash\nset -e\nif [ "$1" = "api" ]; then cat "$FIXTURE_TARBALL"; else echo "unexpected gh args: $*" >&2; exit 1; fi\n');
  chmodSync(stub, 0o755);
  return binDir;
}

function makeGitRepo(tmp: string) {
  const repo = join(tmp, 'repo');
  const remote = join(tmp, 'remote.git');
  git(tmp, ['init', '--bare', '-b', 'main', 'remote.git']);
  git(tmp, ['clone', 'remote.git', 'repo']);
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents: [] }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }));
  git(repo, ['add', '-A']);
  git(repo, ['commit', '-m', 'init']);
  git(repo, ['push', 'origin', 'main']);
  return { repo, remote };
}

test('install: 从 GitHub 整仓抓取技能，入仓、提交并推送', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const tarball = makeTarball(tmp, 'o-cool-skill-deadbeef', { 'SKILL.md': '---\nname: cool-skill\n---\n' });
  const binDir = makeGhStub(tmp, tarball);
  const { repo, remote } = makeGitRepo(tmp);

  const r = spawnSync('node', [CLI, 'install', 'o/cool-skill'], {
    cwd: repo,
    env: { ...process.env, ...GIT_ENV, MYSKILLS_ROOT: repo, PATH: `${binDir}:${process.env.PATH}`, FIXTURE_TARBALL: tarball, MYSKILLS_REMOTE: 'origin' },
    encoding: 'utf8',
  });
  assert.equal(r.status, 0, r.stderr);

  // 入仓：以 repo 名为目录名
  assert.ok(existsSync(join(repo, 'cool-skill', 'SKILL.md')));
  // 提交并推送：远端可读
  const remoteFile = git(remote, ['show', 'main:cool-skill/SKILL.md']);
  assert.match(remoteFile, /name: cool-skill/);
});

test('install: 支持集合仓的子目录提取（/tree/ref/subdir 形式）', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const tarball = makeTarball(tmp, 'o-skills-deadbeef', {
    'skills/pdf/SKILL.md': '---\nname: pdf\n---\n',
    'skills/docx/SKILL.md': '---\nname: docx\n---\n',
  });
  const binDir = makeGhStub(tmp, tarball);
  const { repo } = makeGitRepo(tmp);

  const r = spawnSync('node', [CLI, 'install', 'https://github.com/o/skills/tree/main/skills/pdf'], {
    cwd: repo,
    env: { ...process.env, ...GIT_ENV, MYSKILLS_ROOT: repo, PATH: `${binDir}:${process.env.PATH}`, FIXTURE_TARBALL: tarball, MYSKILLS_REMOTE: 'origin' },
    encoding: 'utf8',
  });
  assert.equal(r.status, 0, r.stderr);

  assert.ok(existsSync(join(repo, 'pdf', 'SKILL.md')), '子目录应以 basename 入仓');
  assert.ok(!existsSync(join(repo, 'docx')), '未选择的子目录不应入仓');
  assert.ok(!existsSync(join(repo, 'skills')), '不应保留集合仓的目录层级');
});

test('install: 同名技能已存在时拒绝覆盖', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const tarball = makeTarball(tmp, 'o-alpha-deadbeef', { 'SKILL.md': '---\nname: alpha\n---\n' });
  const binDir = makeGhStub(tmp, tarball);
  const { repo } = makeGitRepo(tmp);
  mkdirSync(join(repo, 'alpha'), { recursive: true });
  writeFileSync(join(repo, 'alpha', 'SKILL.md'), '---\nname: alpha\nexisting\n---\n');

  const r = spawnSync('node', [CLI, 'install', 'o/alpha'], {
    cwd: repo,
    env: { ...process.env, ...GIT_ENV, MYSKILLS_ROOT: repo, PATH: `${binDir}:${process.env.PATH}`, FIXTURE_TARBALL: tarball, MYSKILLS_REMOTE: 'origin' },
    encoding: 'utf8',
  });
  assert.notEqual(r.status, 0, '应拒绝覆盖');
  assert.match(readFileSync(join(repo, 'alpha', 'SKILL.md'), 'utf8'), /existing/, '原内容不被破坏');
});

test('install: --name 含 ../ 等非法技能名时拒绝，不在仓库外写文件', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const tarball = makeTarball(tmp, 'o-evil-deadbeef', { 'SKILL.md': '---\nname: evil\n---\n' });
  const binDir = makeGhStub(tmp, tarball);
  const { repo } = makeGitRepo(tmp);

  for (const bad of ['../evil', 'a/b', '.hidden', '..']) {
    const r = spawnSync('node', [CLI, 'install', 'o/evil', '--name', bad], {
      cwd: repo,
      env: { ...process.env, ...GIT_ENV, PATH: `${binDir}:${process.env.PATH}`, FIXTURE_TARBALL: tarball, MYSKILLS_REMOTE: 'origin' },
      encoding: 'utf8',
    });
    assert.notEqual(r.status, 0, `--name ${bad} 应被拒绝`);
    assert.match(r.stderr, /非法技能名/);
  }
  assert.ok(!existsSync(join(tmp, 'evil')), '仓库父目录不应出现逃逸目录');
});

test('install: subdir 含 ../ 逃逸 tarball 顶层目录时拒绝', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const tarball = makeTarball(tmp, 'o-skills-deadbeef', { 'skills/pdf/SKILL.md': '---\nname: pdf\n---\n' });
  const binDir = makeGhStub(tmp, tarball);
  const { repo } = makeGitRepo(tmp);

  const r = spawnSync('node', [CLI, 'install', 'https://github.com/o/skills/tree/main/../repo.tar.gz'], {
    cwd: repo,
    env: { ...process.env, ...GIT_ENV, PATH: `${binDir}:${process.env.PATH}`, FIXTURE_TARBALL: tarball, MYSKILLS_REMOTE: 'origin' },
    encoding: 'utf8',
  });
  assert.notEqual(r.status, 0, '越界 subdir 应被拒绝');
  assert.match(r.stderr, /子目录越界/);
  assert.ok(!existsSync(join(repo, 'repo.tar.gz')), '不应把 tarball 当技能拷入仓库');
});
