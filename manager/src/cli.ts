#!/usr/bin/env node
// myskills 管理 CLI：link / status / sync / install / migrate
import { existsSync, mkdirSync, mkdtempSync, cpSync, readFileSync, readdirSync, readlinkSync, rmSync, symlinkSync, lstatSync, writeFileSync } from 'node:fs';
import { homedir, hostname, tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

interface AgentDef {
  id: string;
  name: string;
  skillsPath: string; // 支持 ~ 展开
}

interface Manifest {
  agents: Record<string, string[]>;
}

export function expandHome(p: string): string {
  if (p === '~') return homedir();
  if (p.startsWith('~/')) return join(homedir(), p.slice(2));
  return p;
}

export function findRepoRoot(start: string): string {
  let dir = resolve(start);
  for (;;) {
    if (existsSync(join(dir, 'skills-manifest.json'))) return dir;
    const parent = dirname(dir);
    if (parent === dir) throw new Error('未找到 skills-manifest.json，请在 myskills 仓库内运行');
    dir = parent;
  }
}

export function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}

export function git(repoRoot: string, args: string[]): string {
  const r = spawnSync('git', args, { cwd: repoRoot, encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} 失败: ${r.stderr.trim()}`);
  return r.stdout.trim();
}

// 统计某 agent skills 目录里指向仓库的链接：有效数与断链数
function countLinks(skillsPath: string, repoRoot: string): { linked: number; broken: number } {
  let linked = 0;
  let broken = 0;
  if (!existsSync(skillsPath)) return { linked, broken };
  for (const entry of readdirSync(skillsPath)) {
    const entryPath = join(skillsPath, entry);
    if (!lstatSync(entryPath).isSymbolicLink()) continue;
    const target = resolve(skillsPath, readlinkSync(entryPath));
    if (!target.startsWith(repoRoot + '/')) continue;
    if (existsSync(target)) linked++;
    else broken++;
  }
  return { linked, broken };
}

function link(repoRoot: string): void {
  const { agents } = readJson<{ agents: AgentDef[] }>(join(repoRoot, 'agents.json'));
  const manifest = readJson<Manifest>(join(repoRoot, 'skills-manifest.json'));

  for (const agent of agents) {
    const skillsPath = expandHome(agent.skillsPath);
    // agent 是否安装：skills 目录的父目录存在即视为已安装
    if (!existsSync(dirname(skillsPath))) {
      console.log(`跳过 ${agent.id}（未安装）`);
      continue;
    }
    mkdirSync(skillsPath, { recursive: true });
    const wanted = manifest.agents[agent.id] ?? [];
    for (const name of wanted) {
      const target = join(repoRoot, name);
      if (!existsSync(target)) {
        console.log(`警告: 清单中的 ${name} 在仓库中不存在，跳过`);
        continue;
      }
      const linkPath = join(skillsPath, name);
      rmSync(linkPath, { force: true, recursive: false });
      symlinkSync(target, linkPath, 'dir');
      console.log(`链接 ${agent.id}/${name}`);
    }
    // 清理：指向仓库但已不在清单的孤儿链接、指向仓库的断链
    for (const entry of readdirSync(skillsPath)) {
      if (wanted.includes(entry)) continue;
      const entryPath = join(skillsPath, entry);
      if (!lstatSync(entryPath).isSymbolicLink()) continue;
      const target = resolve(skillsPath, readlinkSync(entryPath));
      if (!target.startsWith(repoRoot + '/')) continue;
      rmSync(entryPath, { force: true });
      console.log(`移除 ${agent.id}/${entry}（孤儿或断链）`);
    }
  }
}

function status(repoRoot: string): void {  const { agents } = readJson<{ agents: AgentDef[] }>(join(repoRoot, 'agents.json'));
  const agentStats: Record<string, { linked: number } | { skipped: true }> = {};
  let brokenLinks = 0;
  for (const agent of agents) {
    const skillsPath = expandHome(agent.skillsPath);
    if (!existsSync(dirname(skillsPath))) {
      agentStats[agent.id] = { skipped: true };
      continue;
    }
    const { linked, broken } = countLinks(skillsPath, repoRoot);
    agentStats[agent.id] = { linked };
    brokenLinks += broken;
  }
  const s = {
    host: hostname(),
    updatedAt: new Date().toISOString(),
    sha: git(repoRoot, ['rev-parse', 'HEAD']),
    branch: git(repoRoot, ['rev-parse', '--abbrev-ref', 'HEAD']),
    brokenLinks,
    agents: agentStats,
  };
  mkdirSync(join(repoRoot, 'machines'), { recursive: true });
  writeFileSync(join(repoRoot, 'machines', `${hostname()}.json`), JSON.stringify(s, null, 2) + '\n');
  console.log(`已写入 machines/${hostname()}.json`);
}

// sync = pull --ff-only → link → status → 提交并推送 machines/ 变更
function sync(repoRoot: string, remote: string): void {
  const branch = git(repoRoot, ['rev-parse', '--abbrev-ref', 'HEAD']);
  git(repoRoot, ['pull', '--ff-only', remote, branch]);
  link(repoRoot);
  status(repoRoot);
  git(repoRoot, ['add', 'machines/']);
  const dirty = spawnSync('git', ['diff', '--cached', '--quiet'], { cwd: repoRoot }).status !== 0;
  if (dirty) {
    git(repoRoot, ['commit', '-m', `chore: ${hostname()} 同步状态`]);
    git(repoRoot, ['push', remote, 'HEAD']);
    console.log('状态已提交并推送');
  } else {
    console.log('状态无变化，跳过提交');
  }
}

// install <url> [--name <n>]：经 gh 抓取 GitHub tarball，vendor 进仓库并提交推送
interface GitHubSource {
  owner: string;
  repo: string;
  ref?: string;
  subdir?: string;
}

export function parseGitHubUrl(input: string): GitHubSource {
  const m = input.match(/^(?:https?:\/\/github\.com\/)?([^/\s]+)\/([^/\s]+?)(?:\.git)?(?:\/tree\/([^/\s]+)(?:\/(.+))?)?\/?$/);
  if (!m) throw new Error(`无法解析 GitHub 地址: ${input}（支持 owner/repo 或 https://github.com/owner/repo[/tree/ref/subdir]）`);
  return { owner: m[1], repo: m[2], ref: m[3], subdir: m[4] };
}

function install(repoRoot: string, input: string, nameOverride: string | undefined, remote: string): void {
  const { owner, repo, ref, subdir } = parseGitHubUrl(input);
  const name = nameOverride ?? (subdir ? subdir.replace(/\/+$/, '').split('/').pop()! : repo);
  const dest = join(repoRoot, name);
  if (existsSync(dest)) throw new Error(`仓库中已存在 ${name}，如需更新请先删除或换 --name`);

  const endpoint = `repos/${owner}/${repo}/tarball${ref ? `/${ref}` : ''}`;
  const gh = spawnSync('gh', ['api', endpoint], { encoding: 'buffer', maxBuffer: 1024 * 1024 * 1024 });
  if (gh.status !== 0) throw new Error(`gh api ${endpoint} 失败: ${gh.stderr?.toString().trim()}`);

  const tmp = mkdtempSync(join(tmpdir(), 'myskills-install-'));
  const tgz = join(tmp, 'repo.tar.gz');
  writeFileSync(tgz, gh.stdout);
  const tar = spawnSync('tar', ['-xzf', tgz, '-C', tmp], { encoding: 'utf8' });
  if (tar.status !== 0) throw new Error(`解压 tarball 失败: ${tar.stderr.trim()}`);

  const top = readdirSync(tmp).filter((e) => e !== 'repo.tar.gz');
  if (top.length !== 1) throw new Error(`tarball 结构异常：顶层条目数为 ${top.length}`);
  const src = subdir ? join(tmp, top[0], subdir) : join(tmp, top[0]);
  if (!existsSync(join(src, 'SKILL.md'))) throw new Error(`${subdir ?? '仓库根'} 中没有 SKILL.md，不是一个技能`);

  cpSync(src, dest, { recursive: true });
  rmSync(tmp, { recursive: true, force: true });
  git(repoRoot, ['add', name]);
  git(repoRoot, ['commit', '-m', `feat: 安装技能 ${name}（来自 github.com/${owner}/${repo}）`]);
  git(repoRoot, ['push', remote, 'HEAD']);
  console.log(`已安装 ${name}（来自 github.com/${owner}/${repo}${subdir ? ` 的 ${subdir}` : ''}），并推送`);
}

// 递归收集目录内文件的相对路径（排除 .git/node_modules）
function listFiles(dir: string, base = dir): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === '.git' || entry.name === 'node_modules') continue;
    const p = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...listFiles(p, base));
    else if (entry.isFile()) out.push(p.slice(base.length + 1));
  }
  return out.sort();
}

// 两个目录内容是否完全一致（相对路径集合 + 文件内容）
function dirsIdentical(a: string, b: string): boolean {
  const fa = listFiles(a);
  const fb = listFiles(b);
  if (fa.length !== fb.length || fa.some((f, i) => f !== fb[i])) return false;
  return fa.every((f) => Buffer.compare(readFileSync(join(a, f)), readFileSync(join(b, f))) === 0);
}

interface MigrateAction {
  agent: string;
  name: string;
  kind: 'copy-in' | 'relink' | 'conflict' | 'remove-broken' | 'fix-broken' | 'skip-not-skill';
  detail?: string;
}

// migrate: 把各 agent 目录里的存量实体技能收敛进仓库，重建符号链接，生成清单
// 默认 dry-run；--apply 才执行。不做 git 提交，留给使用者检查后提交。
function migrate(repoRoot: string, apply: boolean): void {
  const { agents } = readJson<{ agents: AgentDef[] }>(join(repoRoot, 'agents.json'));
  const manifest = readJson<Manifest>(join(repoRoot, 'skills-manifest.json'));
  const actions: MigrateAction[] = [];
  const converged: Record<string, Set<string>> = {};

  for (const agent of agents) {
    const skillsPath = expandHome(agent.skillsPath);
    if (!existsSync(dirname(skillsPath)) || !existsSync(skillsPath)) continue;
    const done = (converged[agent.id] ??= new Set(manifest.agents[agent.id] ?? []));

    for (const entry of readdirSync(skillsPath)) {
      const entryPath = join(skillsPath, entry);
      const st = lstatSync(entryPath);
      let skillDir: string | null = null;

      if (st.isSymbolicLink()) {
        const target = resolve(skillsPath, readlinkSync(entryPath));
        if (!existsSync(target)) {
          // 断链：若仓库顶层有同名技能（如旧链接指向已消失的嵌套路径），修复为指向顶层
          const repoSkill = join(repoRoot, entry);
          if (existsSync(join(repoSkill, 'SKILL.md'))) {
            actions.push({ agent: agent.id, name: entry, kind: 'fix-broken' });
            done.add(entry);
            if (apply) {
              rmSync(entryPath, { force: true });
              symlinkSync(repoSkill, entryPath, 'dir');
            }
          } else {
            actions.push({ agent: agent.id, name: entry, kind: 'remove-broken' });
            if (apply) rmSync(entryPath, { force: true });
          }
          continue;
        }
        if (target.startsWith(repoRoot + '/')) {
          done.add(entry); // 已是指向仓库的链接，保持
          continue;
        }
        skillDir = target; // 指向仓库外的技能，按实体处理
      } else if (st.isDirectory()) {
        skillDir = entryPath;
      } else {
        continue; // 普通文件不管
      }

      if (!existsSync(join(skillDir, 'SKILL.md'))) {
        actions.push({ agent: agent.id, name: entry, kind: 'skip-not-skill' });
        continue;
      }
      const repoDest = join(repoRoot, entry);
      if (existsSync(repoDest) && !dirsIdentical(skillDir, repoDest)) {
        actions.push({ agent: agent.id, name: entry, kind: 'conflict', detail: '与仓库同名但内容不同，保留本地，需人工取舍' });
        continue;
      }
      if (!existsSync(repoDest)) {
        actions.push({ agent: agent.id, name: entry, kind: 'copy-in' });
        if (apply) {
          cpSync(skillDir, repoDest, {
            recursive: true,
            filter: (src) => !src.split('/').includes('.git') && !src.split('/').includes('node_modules'),
          });
        }
      } else {
        actions.push({ agent: agent.id, name: entry, kind: 'relink' });
      }
      done.add(entry);
      if (apply) {
        if (!st.isSymbolicLink()) rmSync(entryPath, { recursive: true, force: true });
        else rmSync(entryPath, { force: true });
        symlinkSync(repoDest, entryPath, 'dir');
      }
    }
  }

  for (const a of actions) {
    const label = { 'copy-in': '拷入仓库并链接', relink: '内容相同，换链接', conflict: '冲突', 'remove-broken': '删除断链', 'fix-broken': '修复断链，指向仓库顶层', 'skip-not-skill': '非技能目录，跳过' }[a.kind];
    console.log(`[${a.kind}] ${a.agent}/${a.name}: ${label}${a.detail ? `（${a.detail}）` : ''}`);
  }
  if (!apply) {
    console.log('\ndry-run：未做任何改动。确认后运行 myskills migrate --apply');
    return;
  }
  for (const [id, set] of Object.entries(converged)) {
    manifest.agents[id] = [...set].sort();
  }
  writeFileSync(join(repoRoot, 'skills-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  console.log('清单已更新。请检查 git 状态后提交并推送。');
}

const command = process.argv[2];
try {
  switch (command) {
    case 'link':
      link(findRepoRoot(process.cwd()));
      break;
    case 'status':
      status(findRepoRoot(process.cwd()));
      break;
    case 'sync': {
      const remoteIdx = process.argv.indexOf('--remote');
      const remote = remoteIdx > -1 ? process.argv[remoteIdx + 1] : (process.env.MYSKILLS_REMOTE ?? 'aliyun');
      sync(findRepoRoot(process.cwd()), remote);
      break;
    }
    case 'install': {
      const url = process.argv[3];
      if (!url) throw new Error('用法: myskills install <github-url> [--name <n>] [--remote <r>]');
      const nameIdx = process.argv.indexOf('--name');
      const remoteIdx = process.argv.indexOf('--remote');
      const remote = remoteIdx > -1 ? process.argv[remoteIdx + 1] : (process.env.MYSKILLS_REMOTE ?? 'aliyun');
      install(findRepoRoot(process.cwd()), url, nameIdx > -1 ? process.argv[nameIdx + 1] : undefined, remote);
      break;
    }
    case 'migrate':
      migrate(findRepoRoot(process.cwd()), process.argv.includes('--apply'));
      break;
    default:
      console.error('用法: myskills <link|status|sync|install|migrate>');
      process.exit(command ? 1 : 0);
  }
} catch (err) {
  console.error((err as Error).message);
  process.exit(1);
}
