import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, symlinkSync, existsSync, lstatSync, realpathSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { projectCandidateTargets, projectTargetAgents, projectTargetStates, toggleProjectTarget } from '../src/core.ts';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

function makeSkill(repoRoot: string, name: string) {
  mkdirSync(join(repoRoot, name), { recursive: true });
  writeFileSync(join(repoRoot, name, 'SKILL.md'), `---\nname: ${name}\n---\n`);
}

// 中心仓库 fixture + 一个含 .myskills.json 的项目；返回项目内 runs 用的环境
function makeProjectFixture(opts: {
  skills?: string[];
  projectManifest: object;
  installedAgentDirs?: string[]; // 项目内预创建的 agent 目录（相对项目根）
  globalAgents?: object[]; // 写入中心仓库 agents.json 的家目录 agent
}) {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-proj-'));
  const repo = join(tmp, 'repo');
  const project = join(tmp, 'project');
  const runFrom = join(project, 'sub', 'dir');
  mkdirSync(repo, { recursive: true });
  mkdirSync(runFrom, { recursive: true });
  for (const s of opts.skills ?? []) makeSkill(repo, s);
  // 家目录 agent 保持字面 ~/ 前缀：项目模式只用它派生候选目标，不做展开
  const agents = opts.globalAgents ?? [{ id: 'claude', name: 'Claude Code', skillsPath: '~/.claude/skills' }];
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents }, null, 2));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }, null, 2));
  for (const d of opts.installedAgentDirs ?? []) mkdirSync(join(project, d), { recursive: true });
  writeFileSync(join(project, '.myskills.json'), JSON.stringify(opts.projectManifest, null, 2));
  return { tmp, repo, project, runFrom };
}

function run(args: string[], cwd: string, repo: string) {
  return spawnSync('node', [CLI, ...args], {
    cwd,
    env: { ...process.env, MYSKILLS_ROOT: repo },
    encoding: 'utf8',
  });
}

test('项目 link: 子目录运行，探测到 .claude/skills 并建链；清理孤儿与断链，不动真实目录和外部链接', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    skills: ['alpha', 'beta'],
    projectManifest: { skills: ['alpha'] },
    installedAgentDirs: ['.claude/skills'],
  });
  const skillsDir = join(project, '.claude', 'skills');
  // 孤儿：指向仓库但不在清单；断链：指向仓库里不存在的目录；真实目录与外部链接：不动
  symlinkSync(join(repo, 'beta'), join(skillsDir, 'orphan'), 'dir');
  symlinkSync(join(repo, 'gone'), join(skillsDir, 'gone'), 'dir');
  mkdirSync(join(skillsDir, 'local-only'), { recursive: true });
  const external = mkdtempSync(join(tmpdir(), 'myskills-ext-'));
  symlinkSync(external, join(skillsDir, 'external'), 'dir');

  const r = run(['link'], runFrom, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /项目模式/);

  assert.equal(realpathSync(join(skillsDir, 'alpha')), realpathSync(join(repo, 'alpha')), 'alpha 应链接进项目');
  assert.ok(!existsSync(join(skillsDir, 'beta')), '未列入项目清单的 beta 不建链');
  assert.ok(!existsSync(join(skillsDir, 'orphan')), '孤儿链接应被移除');
  assert.throws(() => lstatSync(join(skillsDir, 'gone')), '断链应被移除');
  assert.ok(lstatSync(join(skillsDir, 'local-only')).isDirectory() && !lstatSync(join(skillsDir, 'local-only')).isSymbolicLink());
  assert.equal(realpathSync(join(skillsDir, 'external')), external, '外部链接不动');
});

test('项目 link: 显式 targets 优先于探测，目录不存在则创建', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    skills: ['alpha'],
    projectManifest: { skills: ['alpha'], targets: ['.agents/skills'] },
    installedAgentDirs: ['.claude/skills'], // 存在但不在 targets 里，不应建链
  });

  const r = run(['link'], runFrom, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.ok(lstatSync(join(project, '.agents', 'skills', 'alpha')).isSymbolicLink());
  assert.ok(!existsSync(join(project, '.claude', 'skills', 'alpha')), '不在 targets 里的目录不建链');
});

test('项目 link: 无 targets 时默认开启全部项目级 agent（注册表去 ~/ 派生），目录不存在则创建', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    skills: ['alpha'],
    projectManifest: { skills: ['alpha'] },
    // 项目里没有任何已存在的 agent 目录，也应按默认开启的候选全部创建
    globalAgents: [
      { id: 'claude', name: 'Claude Code', skillsPath: '~/.claude/skills' },
      { id: 'kimi', name: 'Kimi Code', skillsPath: '~/.kimi-code/skills' },
    ],
  });

  const r = run(['link'], runFrom, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.ok(lstatSync(join(project, '.claude', 'skills', 'alpha')).isSymbolicLink());
  assert.ok(lstatSync(join(project, '.kimi-code', 'skills', 'alpha')).isSymbolicLink());
});

test('项目 link: 显式 targets 为空数组 = 全部关闭，不建链', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    skills: ['alpha'],
    projectManifest: { skills: ['alpha'], targets: [] },
  });

  const r = run(['link'], runFrom, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /已全部关闭/);
  assert.ok(!existsSync(join(project, '.claude', 'skills', 'alpha')));
});

test('项目 link: 注册表没有家目录 agent 时提示并退出 0', () => {
  const { repo, runFrom } = makeProjectFixture({
    skills: ['alpha'],
    projectManifest: { skills: ['alpha'] },
    globalAgents: [{ id: 'proj', name: 'Project Agent', skillsPath: '/opt/proj/.claude/skills' }],
  });

  const r = run(['link'], runFrom, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /未派生出项目级 agent/);
});

test('项目 link: 清单里仓库不存在的技能警告跳过，退出码 0', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    skills: ['alpha'],
    projectManifest: { skills: ['alpha', 'ghost'] },
    installedAgentDirs: ['.claude/skills'],
  });

  const r = run(['link'], runFrom, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout + r.stderr, /ghost/);
  assert.ok(!existsSync(join(project, '.claude', 'skills', 'ghost')));
  assert.ok(lstatSync(join(project, '.claude', 'skills', 'alpha')).isSymbolicLink());
});

test('项目 link: --global 在项目内强制走全局模式', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-proj-'));
  const repo = join(tmp, 'repo');
  const project = join(tmp, 'project');
  const home = join(tmp, 'home');
  mkdirSync(join(repo, 'alpha'), { recursive: true });
  writeFileSync(join(repo, 'alpha', 'SKILL.md'), '---\nname: alpha\n---\n');
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents: [{ id: 'claude', name: 'Claude', skillsPath: join(home, '.claude', 'skills') }] }, null, 2));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: { claude: ['alpha'] } }, null, 2));
  mkdirSync(join(home, '.claude', 'skills'), { recursive: true });
  mkdirSync(join(project, '.claude', 'skills'), { recursive: true });
  writeFileSync(join(project, '.myskills.json'), JSON.stringify({ skills: ['alpha'] }, null, 2));

  const r = run(['link', '--global'], project, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.doesNotMatch(r.stdout, /项目模式/);
  assert.ok(lstatSync(join(home, '.claude', 'skills', 'alpha')).isSymbolicLink(), '全局链接建到家目录 agent');
  assert.ok(!existsSync(join(project, '.claude', 'skills', 'alpha')), '项目目录不动');
});

test('项目 link: 坏格式清单报错退出码 1；targets 含 .. 或绝对路径被拒绝', () => {
  const bad = makeProjectFixture({ skills: ['alpha'], projectManifest: { skills: 'alpha' }, installedAgentDirs: ['.claude/skills'] });
  const r1 = run(['link'], bad.runFrom, bad.repo);
  assert.notEqual(r1.status, 0);
  assert.match(r1.stderr, /skills 必须是字符串数组/);

  const evil = makeProjectFixture({ skills: ['alpha'], projectManifest: { skills: [], targets: ['../outside'] } });
  const r2 = run(['link'], evil.runFrom, evil.repo);
  assert.notEqual(r2.status, 0);
  assert.match(r2.stderr, /项目内相对路径/);
});

test('projectCandidateTargets: 家目录 agent 的 skillsPath 去 ~/ 得候选，去重且忽略非家目录 agent', () => {
  const targets = projectCandidateTargets([
    { id: 'claude', name: 'Claude Code', skillsPath: '~/.claude/skills' },
    { id: 'agents', name: 'Universal', skillsPath: '~/.agents/skills' },
    { id: 'pi', name: 'Pi', skillsPath: '~/.pi/agent/skills' },
    { id: 'proj', name: 'Project Agent', skillsPath: '/opt/proj/.claude/skills' },
    { id: 'dup', name: 'Dup', skillsPath: '~/.claude/skills' },
  ]);
  assert.deepEqual(targets, ['.claude/skills', '.agents/skills', '.pi/agent/skills']);
});

test('projectTargetAgents: 与注册表同一批家目录 agent，路径去 ~/，同一 target 取第一个 agent', () => {
  const rows = projectTargetAgents([
    { id: 'claude', name: 'Claude Code', skillsPath: '~/.claude/skills' },
    { id: 'kimi', name: 'Kimi Code', skillsPath: '~/.kimi-code/skills' },
    { id: 'proj', name: 'Project Agent', skillsPath: '/opt/proj/.claude/skills' },
    { id: 'dup', name: 'Dup', skillsPath: '~/.claude/skills' },
  ]);
  assert.deepEqual(rows, [
    { id: 'claude', target: '.claude/skills' },
    { id: 'kimi', target: '.kimi-code/skills' },
  ]);
});

test('toggleProjectTarget: 省略 targets 时默认全开，关闭后固化显式 targets，再开恢复', () => {
  const { repo, project } = makeProjectFixture({
    projectManifest: { skills: [] },
    globalAgents: [
      { id: 'claude', name: 'Claude Code', skillsPath: '~/.claude/skills' },
      { id: 'kimi', name: 'Kimi Code', skillsPath: '~/.kimi-code/skills' },
    ],
  });

  assert.deepEqual(
    projectTargetStates(project, repo).map((r) => [r.id, r.enabled]),
    [['claude', true], ['kimi', true]],
    '无显式 targets 时全部默认开启',
  );

  const on = toggleProjectTarget(project, repo, '.kimi-code/skills');
  assert.equal(on, false);
  assert.deepEqual(JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8')), {
    skills: [],
    targets: ['.claude/skills'],
  });
  assert.deepEqual(
    projectTargetStates(project, repo).map((r) => [r.id, r.enabled]),
    [['claude', true], ['kimi', false]],
  );

  assert.equal(toggleProjectTarget(project, repo, '.kimi-code/skills'), true);
  assert.deepEqual(JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8')).targets, [
    '.claude/skills',
    '.kimi-code/skills',
  ]);
});

test('项目 init: 默认生成空 skills，并把已存在的候选 agent 目录写入 targets', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    projectManifest: {},
    installedAgentDirs: ['.claude/skills'],
  });
  rmSync(join(project, '.myskills.json'));

  const r = run(['init'], project, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.deepEqual(JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8')), {
    skills: [],
    targets: ['.claude/skills'],
  });
});

test('项目 init: --skills 去重排序；没有候选目录时省略 targets', () => {
  const { repo, project, runFrom } = makeProjectFixture({ projectManifest: {} });
  rmSync(join(project, '.myskills.json'));

  const r = run(['init', '--skills', 'zeta, alpha, zeta, beta'], project, repo);
  assert.equal(r.status, 0, r.stderr);
  assert.deepEqual(JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8')), {
    skills: ['alpha', 'beta', 'zeta'],
  });
});

test('项目 init: 已存在 .myskills.json 时拒绝覆盖', () => {
  const { repo, project, runFrom } = makeProjectFixture({ projectManifest: { skills: ['keep'] } });

  const r = run(['init'], project, repo);
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /已存在/);
  assert.deepEqual(JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8')), { skills: ['keep'] });
});

test('项目 init → link: 生成清单后可立即分发技能', () => {
  const { repo, project, runFrom } = makeProjectFixture({
    skills: ['alpha'],
    projectManifest: {},
    installedAgentDirs: ['.claude/skills'],
  });
  rmSync(join(project, '.myskills.json'));

  const init = run(['init', '--skills', 'alpha'], project, repo);
  assert.equal(init.status, 0, init.stderr);
  const link = run(['link'], runFrom, repo);
  assert.equal(link.status, 0, link.stderr);
  assert.ok(lstatSync(join(project, '.claude', 'skills', 'alpha')).isSymbolicLink());
});
