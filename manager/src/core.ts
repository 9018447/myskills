// myskills 核心逻辑：link / status / sync / install / migrate 及清单、注册表读写
// 所有函数返回结构化结果或报告行，不直接打印——打印由 cli.ts / tui.ts 负责
import { existsSync, mkdirSync, mkdtempSync, cpSync, readFileSync, readdirSync, readlinkSync, rmSync, symlinkSync, lstatSync, writeFileSync } from 'node:fs';
import { homedir, hostname, tmpdir } from 'node:os';
import { join, dirname, resolve, sep } from 'node:path';
import { spawnSync } from 'node:child_process';

export interface AgentDef {
  id: string;
  name: string;
  skillsPath: string; // 支持 ~ 展开
}

export interface Manifest {
  agents: Record<string, string[]>;
  // 技能来源仓库："owner/repo" 或 "owner/repo/subdir"；install 时记录，存量由 skillSources 从 git 历史推断
  sources?: Record<string, string>;
  // 预设集：名字 → 技能列表；应用到 agent 时并集追加
  presets?: Record<string, string[]>;
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

export function loadAgents(repoRoot: string): AgentDef[] {
  return readJson<{ agents: AgentDef[] }>(join(repoRoot, 'agents.json')).agents;
}

export function saveAgents(repoRoot: string, agents: AgentDef[]): void {
  writeFileSync(join(repoRoot, 'agents.json'), JSON.stringify({ agents }, null, 2) + '\n');
}

export function loadManifest(repoRoot: string): Manifest {
  return readJson<Manifest>(join(repoRoot, 'skills-manifest.json'));
}

export function saveManifest(repoRoot: string, manifest: Manifest): void {
  writeFileSync(join(repoRoot, 'skills-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
}

// 仓库里的技能：顶层含 SKILL.md 的目录
export function listRepoSkills(repoRoot: string): string[] {
  return readdirSync(repoRoot, { withFileTypes: true })
    .filter((e) => e.isDirectory() && !e.name.startsWith('.') && existsSync(join(repoRoot, e.name, 'SKILL.md')))
    .map((e) => e.name)
    .sort();
}

// 读技能 frontmatter 的 description（不存在则返回空串）
// 支持单行值（可带单/双引号）与 YAML 块标量（> 折叠、| 保留换行，含 >- / |+ 等 chomping 变体）
export function skillDescription(repoRoot: string, name: string): string {
  const text = readFileSync(join(repoRoot, name, 'SKILL.md'), 'utf8');
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return '';
  const lines = m[1].split('\n');
  for (let i = 0; i < lines.length; i++) {
    const lm = lines[i].match(/^description:\s*(.*)$/);
    if (!lm) continue;
    const rest = lm[1].trim();
    // 块标量：收集后续的缩进内容行，直到下一个顶级键
    const block = rest.match(/^([>|])[+-]?$/);
    if (block) {
      const content: string[] = [];
      for (let j = i + 1; j < lines.length; j++) {
        const l = lines[j];
        if (l.trim() === '') {
          content.push('');
          continue;
        }
        if (!/^\s/.test(l)) break;
        content.push(l.trim());
      }
      // > 折叠：段内换行变空格，空行分段；| 保留换行
      const joined = block[1] === '>' ? content.join('\n').split(/\n{2,}/).map((p) => p.split('\n').filter(Boolean).join(' ')).join('\n') : content.join('\n');
      return joined.trim();
    }
    // 单行：去掉成对的包裹引号
    const q = rest.match(/^(["'])([\s\S]*)\1$/);
    return (q ? q[2] : rest).trim();
  }
  return '';
}

// 切换某技能对某 agent 的分发；返回切换后的状态
export function toggleSkill(repoRoot: string, agentId: string, skill: string): boolean {
  const manifest = loadManifest(repoRoot);
  const list = manifest.agents[agentId] ?? [];
  const idx = list.indexOf(skill);
  const enabled = idx === -1;
  if (enabled) list.push(skill);
  else list.splice(idx, 1);
  manifest.agents[agentId] = list.sort();
  saveManifest(repoRoot, manifest);
  return enabled;
}

// 统计某 agent skills 目录里指向仓库的链接：有效数与断链数
export function countLinks(skillsPath: string, repoRoot: string): { linked: number; broken: number } {
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

export function agentInstalled(agent: AgentDef): boolean {
  return existsSync(dirname(expandHome(agent.skillsPath)));
}

export interface LinkReport {
  lines: string[];
  skippedAgents: string[];
  missingSkills: string[];
}

export function link(repoRoot: string): LinkReport {
  const agents = loadAgents(repoRoot);
  const manifest = loadManifest(repoRoot);
  const report: LinkReport = { lines: [], skippedAgents: [], missingSkills: [] };

  for (const agent of agents) {
    const skillsPath = expandHome(agent.skillsPath);
    // agent 是否安装：skills 目录的父目录存在即视为已安装
    if (!existsSync(dirname(skillsPath))) {
      report.skippedAgents.push(agent.id);
      report.lines.push(`跳过 ${agent.id}（未安装）`);
      continue;
    }
    mkdirSync(skillsPath, { recursive: true });
    const wanted = manifest.agents[agent.id] ?? [];
    for (const name of wanted) {
      const target = join(repoRoot, name);
      if (!existsSync(target)) {
        report.missingSkills.push(name);
        report.lines.push(`警告: 清单中的 ${name} 在仓库中不存在，跳过`);
        continue;
      }
      const linkPath = join(skillsPath, name);
      rmSync(linkPath, { force: true, recursive: false });
      symlinkSync(target, linkPath, 'dir');
      report.lines.push(`链接 ${agent.id}/${name}`);
    }
    // 清理：指向仓库但已不在清单的孤儿链接、指向仓库的断链
    for (const entry of readdirSync(skillsPath)) {
      if (wanted.includes(entry)) continue;
      const entryPath = join(skillsPath, entry);
      if (!lstatSync(entryPath).isSymbolicLink()) continue;
      const target = resolve(skillsPath, readlinkSync(entryPath));
      if (!target.startsWith(repoRoot + '/')) continue;
      rmSync(entryPath, { force: true });
      report.lines.push(`移除 ${agent.id}/${entry}（孤儿或断链）`);
    }
  }
  return report;
}

export interface MachineStatus {
  host: string;
  updatedAt: string;
  sha: string;
  branch: string;
  brokenLinks: number;
  agents: Record<string, { linked: number } | { skipped: true }>;
}

export function status(repoRoot: string): MachineStatus {
  const agents = loadAgents(repoRoot);
  const agentStats: MachineStatus['agents'] = {};
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
  // sha 语义：机器状态所对应的内容提交。sync 会把状态文件本身做成提交（chore: ... 同步清单与状态），
  // 所以 HEAD 恰是上一次 sync 的状态提交时取其父提交——否则每次 sync 记录的 sha 都会因自己的状态提交而变化，
  // 下次 sync 又会因此产生新提交，永不收敛。这样 sha 可能不等于 HEAD，这是定义而非滞后。
  let sha = git(repoRoot, ['rev-parse', 'HEAD']);
  const headSubject = git(repoRoot, ['log', '-1', '--format=%s']);
  if (/^chore: .+ 同步清单与状态$/.test(headSubject)) {
    sha = git(repoRoot, ['rev-parse', 'HEAD~1']);
  }
  const branch = git(repoRoot, ['rev-parse', '--abbrev-ref', 'HEAD']);
  // updatedAt 语义：机器状态最近一次发生实质变化的时间；sha/branch/断链数/各 agent 链接数都没变时
  // 沿用旧值，使重复 sync 不产生文件差异，也就不会每次都制造一个只改时间戳的提交。
  const dir = join(repoRoot, 'machines');
  const file = join(dir, `${hostname()}.json`);
  let updatedAt = new Date().toISOString();
  if (existsSync(file)) {
    try {
      const prev = readJson<MachineStatus>(file);
      const unchanged =
        prev.host === hostname() &&
        prev.sha === sha &&
        prev.branch === branch &&
        prev.brokenLinks === brokenLinks &&
        JSON.stringify(prev.agents) === JSON.stringify(agentStats);
      if (unchanged && typeof prev.updatedAt === 'string') updatedAt = prev.updatedAt;
    } catch {
      // 旧文件损坏则按全新状态重写
    }
  }
  const s: MachineStatus = {
    host: hostname(),
    updatedAt,
    sha,
    branch,
    brokenLinks,
    agents: agentStats,
  };
  mkdirSync(dir, { recursive: true });
  writeFileSync(file, JSON.stringify(s, null, 2) + '\n');
  return s;
}

// sync = pull --ff-only → link → status → 提交并推送清单（skills-manifest.json、agents.json）与 machines/ 变更
export function sync(repoRoot: string, remote: string): string[] {
  const lines: string[] = [];
  const branch = git(repoRoot, ['rev-parse', '--abbrev-ref', 'HEAD']);
  git(repoRoot, ['pull', '--ff-only', remote, branch]);
  lines.push(...link(repoRoot).lines);
  status(repoRoot);
  lines.push(`已写入 machines/${hostname()}.json`);
  git(repoRoot, ['add', 'skills-manifest.json', 'agents.json', 'machines/']);
  const dirty = spawnSync('git', ['diff', '--cached', '--quiet'], { cwd: repoRoot }).status !== 0;
  if (dirty) {
    git(repoRoot, ['commit', '-m', `chore: ${hostname()} 同步清单与状态`]);
    git(repoRoot, ['push', remote, 'HEAD']);
    lines.push('清单与状态已提交并推送');
  } else {
    lines.push('无变化，跳过提交');
  }
  return lines;
}

// install <url>：经 gh 抓取 GitHub tarball，vendor 进仓库并提交推送
export interface GitHubSource {
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

// 技能名必须是一个安全的单目录段：字母数字开头，只含字母数字与 ._-，杜绝 ../ 逃逸与隐藏目录
export function validateSkillName(name: string): void {
  if (!/^[A-Za-z0-9_-][A-Za-z0-9._-]*$/.test(name)) {
    throw new Error(`非法技能名 "${name}"：只能由字母、数字、点、下划线、连字符组成，且不能以点开头`);
  }
}

export function install(repoRoot: string, input: string, nameOverride: string | undefined, remote: string): string {
  const { owner, repo, ref, subdir } = parseGitHubUrl(input);
  const name = nameOverride ?? (subdir ? subdir.replace(/\/+$/, '').split('/').pop()! : repo);
  validateSkillName(name);
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
  const base = resolve(tmp, top[0]);
  const src = subdir ? resolve(base, subdir) : base;
  // subdir 由 URL 传入，可能含 ../：resolve 后必须仍落在 tarball 顶层目录内
  if (src !== base && !src.startsWith(base + sep)) {
    rmSync(tmp, { recursive: true, force: true });
    throw new Error(`子目录越界：${subdir} 逃逸出 tarball 顶层目录`);
  }
  if (!existsSync(join(src, 'SKILL.md'))) throw new Error(`${subdir ?? '仓库根'} 中没有 SKILL.md，不是一个技能`);

  cpSync(src, dest, { recursive: true });
  rmSync(tmp, { recursive: true, force: true });
  const manifest = loadManifest(repoRoot);
  (manifest.sources ??= {})[name] = subdir ? `${owner}/${repo}/${subdir.replace(/\/+$/, '')}` : `${owner}/${repo}`;
  saveManifest(repoRoot, manifest);
  git(repoRoot, ['add', name, 'skills-manifest.json']);
  git(repoRoot, ['commit', '-m', `feat: 安装技能 ${name}（来自 github.com/${owner}/${repo}）`]);
  git(repoRoot, ['push', remote, 'HEAD']);
  return `已安装 ${name}（来自 github.com/${owner}/${repo}${subdir ? ` 的 ${subdir}` : ''}），并推送`;
}

// 目录条目：普通文件、符号链接（记录 readlink 目标）、其他特殊类型（fifo/socket 等）
interface DirEntry {
  rel: string;
  kind: 'file' | 'symlink' | 'other';
  target?: string;
}

// 递归收集目录内条目的相对路径与类型（排除 .git/node_modules；不跟随符号链接）
function listEntries(dir: string, base = dir): DirEntry[] {
  const out: DirEntry[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === '.git' || entry.name === 'node_modules') continue;
    const p = join(dir, entry.name);
    const rel = p.slice(base.length + 1);
    if (entry.isDirectory()) out.push(...listEntries(p, base));
    else if (entry.isFile()) out.push({ rel, kind: 'file' });
    else if (entry.isSymbolicLink()) out.push({ rel, kind: 'symlink', target: readlinkSync(p) });
    else out.push({ rel, kind: 'other' });
  }
  return out.sort((a, b) => (a.rel < b.rel ? -1 : a.rel > b.rel ? 1 : 0));
}

// 两个目录内容是否完全一致（相对路径集合 + 条目类型 + 文件内容/链接目标）
// 特殊类型（fifo/socket 等）无法安全比较，保守判为不同，避免 migrate --apply 误判 identical 后删除本地内容
function dirsIdentical(a: string, b: string): boolean {
  const ea = listEntries(a);
  const eb = listEntries(b);
  if (ea.length !== eb.length) return false;
  return ea.every((x, i) => {
    const y = eb[i];
    if (x.rel !== y.rel || x.kind !== y.kind) return false;
    if (x.kind === 'symlink') return x.target === y.target;
    if (x.kind === 'other') return false;
    return Buffer.compare(readFileSync(join(a, x.rel)), readFileSync(join(b, x.rel))) === 0;
  });
}

export interface MigrateAction {
  agent: string;
  name: string;
  kind: 'copy-in' | 'relink' | 'conflict' | 'remove-broken' | 'fix-broken' | 'skip-not-skill';
  detail?: string;
}

const ACTION_LABELS: Record<MigrateAction['kind'], string> = {
  'copy-in': '拷入仓库并链接',
  relink: '内容相同，换链接',
  conflict: '冲突',
  'remove-broken': '删除断链',
  'fix-broken': '修复断链，指向仓库顶层',
  'skip-not-skill': '非技能目录，跳过',
};

export function formatAction(a: MigrateAction): string {
  return `[${a.kind}] ${a.agent}/${a.name}: ${ACTION_LABELS[a.kind]}${a.detail ? `（${a.detail}）` : ''}`;
}

// migrate: 把各 agent 目录里的存量实体技能收敛进仓库，重建符号链接，生成清单
// 默认 dry-run；apply=true 才执行。不做 git 提交，留给使用者检查后提交。
export function migrate(repoRoot: string, apply: boolean): { actions: MigrateAction[]; lines: string[] } {
  const agents = loadAgents(repoRoot);
  const manifest = loadManifest(repoRoot);
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

  const lines = actions.map(formatAction);
  if (!apply) {
    lines.push('\ndry-run：未做任何改动。确认后运行 myskills migrate --apply');
    return { actions, lines };
  }
  for (const [id, set] of Object.entries(converged)) {
    manifest.agents[id] = [...set].sort();
  }
  saveManifest(repoRoot, manifest);
  lines.push('清单已更新。请检查 git 状态后提交并推送。');
  return { actions, lines };
}

// TUI 用：读取所有机器状态文件
export function machineStatuses(repoRoot: string): MachineStatus[] {
  const dir = join(repoRoot, 'machines');
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => readJson<MachineStatus>(join(dir, f)))
    .sort((a, b) => a.host.localeCompare(b.host));
}

// TUI 用：与远程的领先/落后（需要先 fetch；失败返回 null）
export function aheadBehind(repoRoot: string, remote: string): { ahead: number; behind: number } | null {
  const branch = git(repoRoot, ['rev-parse', '--abbrev-ref', 'HEAD']);
  const r = spawnSync('git', ['rev-list', '--left-right', '--count', `HEAD...${remote}/${branch}`], { cwd: repoRoot, encoding: 'utf8' });
  if (r.status !== 0) return null;
  const [ahead, behind] = r.stdout.trim().split(/\s+/).map(Number);
  return { ahead, behind };
}

export function fetchRemote(repoRoot: string, remote: string): boolean {
  return spawnSync('git', ['fetch', remote], { cwd: repoRoot, encoding: 'utf8' }).status === 0;
}

// 技能来源：manifest.sources 优先；缺失的从 git 历史推断（install 提交 message 含「来自 github.com/...」）；再缺标 'local'
export function skillSources(repoRoot: string): Record<string, string> {
  const manifest = loadManifest(repoRoot);
  const skills = listRepoSkills(repoRoot);
  const result: Record<string, string> = {};
  for (const s of skills) {
    if (manifest.sources?.[s]) result[s] = manifest.sources[s];
  }
  const missing = skills.filter((s) => !result[s]);
  if (missing.length > 0) {
    const r = spawnSync('git', ['log', '--diff-filter=A', '--format=%x00%s', '--name-only', '--', '*/SKILL.md'], {
      cwd: repoRoot,
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
    });
    if (r.status === 0) {
      let subject = '';
      for (const line of r.stdout.split('\n')) {
        if (line.startsWith('\0')) {
          subject = line.slice(1);
          continue;
        }
        const top = line.split('/')[0];
        if (!top || !missing.includes(top) || result[top]) continue;
        const m = subject.match(/来自 github\.com\/([^/\s)]+)\/([^/\s)]+?)(?: 的 (.+?))?）/);
        if (m) result[top] = m[3] ? `${m[1]}/${m[2]}/${m[3]}` : `${m[1]}/${m[2]}`;
      }
    }
  }
  for (const s of skills) {
    if (!result[s]) result[s] = 'local';
  }
  return result;
}

// 预设集 CRUD 与应用
export function setPreset(repoRoot: string, name: string, skills: string[]): void {
  const manifest = loadManifest(repoRoot);
  (manifest.presets ??= {})[name] = [...new Set(skills)].sort();
  saveManifest(repoRoot, manifest);
}

export function deletePreset(repoRoot: string, name: string): void {
  const manifest = loadManifest(repoRoot);
  if (manifest.presets) delete manifest.presets[name];
  saveManifest(repoRoot, manifest);
}

export interface ApplyResult {
  added: Record<string, number>; // 各 agent 新增数量
  missing: string[]; // 预设里但仓库中不存在的技能
}

// 并集追加：预设技能并入目标 agent 清单，已有的不重复
export function applyPreset(repoRoot: string, name: string, agentIds: string[]): ApplyResult {
  const manifest = loadManifest(repoRoot);
  const skills = manifest.presets?.[name];
  if (!skills) throw new Error(`预设集 ${name} 不存在`);
  const missing = skills.filter((s) => !existsSync(join(repoRoot, s)));
  const valid = skills.filter((s) => !missing.includes(s));
  const added: Record<string, number> = {};
  for (const id of agentIds) {
    const list = manifest.agents[id] ?? [];
    const before = list.length;
    manifest.agents[id] = [...new Set([...list, ...valid])].sort();
    added[id] = manifest.agents[id].length - before;
  }
  saveManifest(repoRoot, manifest);
  return { added, missing };
}

// agent 的项目分组键：skillsPath 里第一个点开头的段之前是项目路径；直接在家目录下的算「全局」
export function agentProjectGroup(agent: AgentDef): string {
  const p = expandHome(agent.skillsPath);
  const segments = p.split('/');
  const dotIdx = segments.findIndex((s) => s.startsWith('.'));
  if (dotIdx === -1) return dirname(dirname(p));
  const prefix = segments.slice(0, dotIdx).join('/') || '/';
  return prefix === homedir() ? '全局' : prefix;
}
