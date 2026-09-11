import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, symlinkSync, existsSync, lstatSync, realpathSync, readlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

function makeSkillDir(parent: string, name: string, extra = '') {
  mkdirSync(join(parent, name), { recursive: true });
  writeFileSync(join(parent, name, 'SKILL.md'), `---\nname: ${name}\n---\n${extra}`);
}

// 仓库有 alpha/conflict；agent 目录里有：同内容 same、本地独有 local、冲突 conflict、断链 broken、非技能 notes、外部技能链接 ext
function makeFixture() {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  makeSkillDir(repo, 'alpha');
  makeSkillDir(repo, 'conflict', 'repo-version\n');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }],
  }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }));

  const skillsDir = join(home, '.claude', 'skills');
  mkdirSync(skillsDir, { recursive: true });
  makeSkillDir(repo, 'same');
  makeSkillDir(skillsDir, 'same'); // 与仓库同内容
  makeSkillDir(skillsDir, 'local'); // 仓库没有
  makeSkillDir(skillsDir, 'conflict', 'local-version\n'); // 与仓库冲突
  symlinkSync(join(repo, 'gone'), join(skillsDir, 'broken'), 'dir'); // 断链
  mkdirSync(join(skillsDir, 'notes')); // 非技能目录
  const extSkill = join(home, 'elsewhere', 'ext');
  makeSkillDir(join(home, 'elsewhere'), 'ext');
  symlinkSync(extSkill, join(skillsDir, 'ext'), 'dir'); // 指向仓库外的技能

  return { tmp, repo, home, skillsDir };
}

function run(args: string[], cwd: string) {
  return spawnSync('node', [CLI, ...args], { cwd, env: { ...process.env, MYSKILLS_ROOT: cwd }, encoding: 'utf8' });
}

test('migrate: 默认 dry-run，只报告计划，不改变任何文件', () => {
  const { repo, skillsDir } = makeFixture();

  const r = run(['migrate'], repo);
  assert.equal(r.status, 0, r.stderr);
  const out = r.stdout + r.stderr;
  assert.match(out, /local/, '应报告将拷入 local');
  assert.match(out, /conflict/, '应报告冲突');

  assert.ok(!existsSync(join(repo, 'local')), 'dry-run 不动仓库');
  assert.ok(lstatSync(join(skillsDir, 'local')).isDirectory() && !lstatSync(join(skillsDir, 'local')).isSymbolicLink(), 'dry-run 不动 agent 目录');
  assert.ok(lstatSync(join(skillsDir, 'broken')).isSymbolicLink(), 'dry-run 不删断链');
  assert.equal(JSON.parse(readFileSync(join(repo, 'skills-manifest.json'), 'utf8')).agents.claude, undefined, 'dry-run 不写清单');
});

test('migrate --apply: 独有拷入并换链接，同内容换链接，冲突保留，断链删除，清单更新', () => {
  const { repo, skillsDir } = makeFixture();

  const r = run(['migrate', '--apply'], repo);
  assert.equal(r.status, 0, r.stderr);

  // 本地独有：拷入仓库，原位置变符号链接
  assert.ok(existsSync(join(repo, 'local', 'SKILL.md')));
  assert.equal(realpathSync(join(skillsDir, 'local')), realpathSync(join(repo, 'local')));
  // 同内容：直接换链接
  assert.equal(realpathSync(join(skillsDir, 'same')), realpathSync(join(repo, 'same')));
  // 冲突：保留本地实体，不动
  const c = lstatSync(join(skillsDir, 'conflict'));
  assert.ok(c.isDirectory() && !c.isSymbolicLink(), '冲突目录保持原样');
  assert.match(readFileSync(join(skillsDir, 'conflict', 'SKILL.md'), 'utf8'), /local-version/);
  // 断链：删除
  assert.ok(!existsSync(join(skillsDir, 'broken')));
  // 非技能目录：不动
  assert.ok(lstatSync(join(skillsDir, 'notes')).isDirectory() && !lstatSync(join(skillsDir, 'notes')).isSymbolicLink());
  // 外部技能链接：内容拷入仓库，换成指向仓库的链接
  assert.ok(existsSync(join(repo, 'ext', 'SKILL.md')));
  assert.equal(realpathSync(join(skillsDir, 'ext')), realpathSync(join(repo, 'ext')));
  // 清单更新：含收敛成功的，不含冲突和非技能
  const manifest = JSON.parse(readFileSync(join(repo, 'skills-manifest.json'), 'utf8'));
  assert.deepEqual(manifest.agents.claude, ['ext', 'local', 'same']);
});

test('migrate --apply: 本地技能含符号链接时保守判冲突，不误删本地内容', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  makeSkillDir(repo, 'linkskill');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }],
  }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }));
  const skillsDir = join(home, '.claude', 'skills');
  mkdirSync(skillsDir, { recursive: true });
  // 本地同名技能：SKILL.md 与仓库一致，但多一个指向本地独有数据的符号链接
  makeSkillDir(skillsDir, 'linkskill');
  const dataFile = join(home, 'unique-data.txt');
  writeFileSync(dataFile, '重要数据');
  symlinkSync(dataFile, join(skillsDir, 'linkskill', 'data'), 'file');

  const r = run(['migrate', '--apply'], repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /linkskill.*冲突/);
  // 本地内容原样保留：仍是实体目录，符号链接与其目标都还在
  const st = lstatSync(join(skillsDir, 'linkskill'));
  assert.ok(st.isDirectory() && !st.isSymbolicLink(), '本地目录不应被换成链接');
  assert.ok(lstatSync(join(skillsDir, 'linkskill', 'data')).isSymbolicLink(), '符号链接不应被删除');
  assert.equal(readFileSync(dataFile, 'utf8'), '重要数据');
  // 冲突技能不收入清单
  const manifest = JSON.parse(readFileSync(join(repo, 'skills-manifest.json'), 'utf8'));
  assert.ok(!(manifest.agents.claude ?? []).includes('linkskill'));
});

test('migrate --apply: 符号链接目标不同、特殊文件类型（fifo）均保守判冲突', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  // 两侧都有同名符号链接但目标不同
  makeSkillDir(repo, 'sym');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }],
  }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }));
  const skillsDir = join(home, '.claude', 'skills');
  mkdirSync(skillsDir, { recursive: true });

  makeSkillDir(skillsDir, 'sym');
  symlinkSync(join(home, 'a.txt'), join(repo, 'sym', 'ref'), 'file');
  symlinkSync(join(home, 'b.txt'), join(skillsDir, 'sym', 'ref'), 'file');

  // 两侧内容一样但含 fifo（特殊类型无法安全比较）
  makeSkillDir(repo, 'fifoskill');
  makeSkillDir(skillsDir, 'fifoskill');
  assert.equal(spawnSync('mkfifo', [join(skillsDir, 'fifoskill', 'pipe')]).status, 0);

  const r = run(['migrate', '--apply'], repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /sym.*冲突/);
  assert.match(r.stdout, /fifoskill.*冲突/);
  // 都保留本地实体，不换链接
  for (const name of ['sym', 'fifoskill']) {
    const st = lstatSync(join(skillsDir, name));
    assert.ok(st.isDirectory() && !st.isSymbolicLink(), `${name} 应保持原样`);
  }
  assert.equal(readlinkSync(join(skillsDir, 'sym', 'ref')), join(home, 'b.txt'));
});

test('migrate: 断链指向已消失的嵌套路径，但仓库顶层有同名技能 → 修复链接并收入清单', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-test-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  makeSkillDir(repo, 'top-skill');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({
    agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }],
  }));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }));
  const skillsDir = join(home, '.claude', 'skills');
  mkdirSync(skillsDir, { recursive: true });
  // 断链：指向曾经存在的嵌套路径（如仓库重构前的 skills/top-skill）
  symlinkSync(join(repo, 'skills', 'top-skill'), join(skillsDir, 'top-skill'), 'dir');

  // dry-run：应报告修复计划且不改动
  const dry = run(['migrate'], repo);
  assert.equal(dry.status, 0, dry.stderr);
  assert.match(dry.stdout, /top-skill/);
  assert.ok(lstatSync(join(skillsDir, 'top-skill')).isSymbolicLink());
  assert.ok(!existsSync(join(skillsDir, 'top-skill')), 'dry-run 前仍是断链');

  // apply：修复为指向仓库顶层的链接，收入清单
  const r = run(['migrate', '--apply'], repo);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(realpathSync(join(skillsDir, 'top-skill')), realpathSync(join(repo, 'top-skill')));
  const manifest = JSON.parse(readFileSync(join(repo, 'skills-manifest.json'), 'utf8'));
  assert.deepEqual(manifest.agents.claude, ['top-skill']);
});
