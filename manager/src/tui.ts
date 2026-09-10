#!/usr/bin/env node
// myskills 管理 TUI：浏览/搜索技能、勾选分发、同步状态、机器仪表盘、agent 管理、GitHub 安装
// 不用 JSX（node 直接运行 TS 不支持），全部 createElement
import { createElement as h, useState, useMemo, useEffect } from 'react';
import { render, Box, Text, useApp, useInput } from 'ink';
import * as core from './core.ts';

type View = 'skills' | 'machines' | 'agents' | 'install';
type Focus = 'list' | 'dist';

interface AppProps {
  root: string;
  remote: string;
}

const HELP: Record<View, string> = {
  skills: '↑↓ 移动  / 搜索  Tab 切到分发  空格 勾选  l=link  s=sync  f=fetch  m=机器  a=agent  i=安装  q=退出',
  machines: 'm/esc 返回  q=退出',
  agents: '↑↓ 移动  n=新增  e=改路径  d=删除  esc 返回  q=退出',
  install: '输入 URL 回车安装（集合仓用 /tree/ref/子目录）  esc 返回',
};

function StatusLine({ root, remote, tick }: { root: string; remote: string; tick: number }) {
  const info = useMemo(() => {
    try {
      const branch = core.git(root, ['rev-parse', '--abbrev-ref', 'HEAD']);
      const sha = core.git(root, ['rev-parse', '--short', 'HEAD']);
      const ab = core.aheadBehind(root, remote);
      const dirty = core.git(root, ['status', '--porcelain']).length > 0;
      return { branch, sha, ab, dirty };
    } catch {
      return null;
    }
  }, [root, remote, tick]);
  if (!info) return h(Text, { color: 'red' }, 'git 状态读取失败');
  const abText = info.ab ? ` ↑${info.ab.ahead}↓${info.ab.behind}` : '（未 fetch）';
  return h(
    Box, { gap: 2 },
    h(Text, { color: 'cyan' }, `${info.branch}@${info.sha}`),
    h(Text, { color: info.dirty ? 'yellow' : 'green' }, info.dirty ? '有未提交改动' : '工作区干净'),
    h(Text, null, `远程 ${remote}${abText}`),
  );
}

function SkillsView({
  root, agents, manifest, setManifest, onNotice, bumpTick, searching, setSearching,
}: {
  root: string;
  agents: core.AgentDef[];
  manifest: Record<string, Set<string>>;
  setManifest: (m: Record<string, Set<string>>) => void;
  onNotice: (s: string) => void;
  bumpTick: () => void;
  searching: boolean;
  setSearching: (b: boolean) => void;
}) {
  const [filter, setFilter] = useState('');
  const [cursor, setCursor] = useState(0);
  const [focus, setFocus] = useState<Focus>('list');
  const [agentCursor, setAgentCursor] = useState(0);

  const skills = useMemo(() => core.listRepoSkills(root), [root]);
  const shown = useMemo(
    () => (filter ? skills.filter((s) => s.toLowerCase().includes(filter.toLowerCase())) : skills),
    [skills, filter],
  );
  const current = shown[Math.min(cursor, Math.max(0, shown.length - 1))];

  useInput((input, key) => {
    if (searching) {
      if (key.escape) setSearching(false);
      else if (key.return) setSearching(false);
      else if (key.backspace || key.delete) setFilter((f) => f.slice(0, -1));
      else if (input && !key.ctrl && !key.meta) setFilter((f) => f + input);
      setCursor(0);
      return;
    }
    if (input === '/') {
      setSearching(true);
      return;
    }
    if (key.tab) {
      setFocus((f) => (f === 'list' ? 'dist' : 'list'));
      return;
    }
    if (focus === 'list') {
      if (key.upArrow) setCursor((c) => Math.max(0, c - 1));
      if (key.downArrow) setCursor((c) => Math.min(shown.length - 1, c + 1));
      return;
    }
    // focus === 'dist'
    if (key.upArrow) setAgentCursor((c) => Math.max(0, c - 1));
    if (key.downArrow) setAgentCursor((c) => Math.min(agents.length - 1, c + 1));
    if (input === ' ' && current && agents[agentCursor]) {
      const agentId = agents[agentCursor].id;
      const on = core.toggleSkill(root, agentId, current);
      setManifest({ ...manifest, [agentId]: new Set(core.loadManifest(root).agents[agentId] ?? []) });
      onNotice(`${on ? '勾选' : '取消'} ${current} → ${agentId}（清单已写，按 l 生效）`);
      bumpTick();
    }
  });

  const height = 15;
  const start = Math.max(0, Math.min(cursor - Math.floor(height / 2), Math.max(0, shown.length - height)));
  const windowRows = shown.slice(start, start + height);

  return h(
    Box, { flexDirection: 'row', gap: 2 },
    h(
      Box, { flexDirection: 'column', width: 34, borderStyle: 'round', borderColor: focus === 'list' ? 'cyan' : 'gray', paddingX: 1 },
      h(Text, { bold: true }, `技能（${shown.length}/${skills.length}）${searching ? ` 搜索: ${filter}▌` : filter ? ` 过滤: ${filter}` : ''}`),
      ...windowRows.map((s, i) => {
        const active = start + i === cursor;
        return h(Text, { key: s, color: active ? 'cyan' : undefined, bold: active }, `${active ? '❯' : ' '} ${s}`);
      }),
    ),
    h(
      Box, { flexDirection: 'column', flexGrow: 1, borderStyle: 'round', borderColor: focus === 'dist' ? 'cyan' : 'gray', paddingX: 1 },
      h(Text, { bold: true }, current ?? '（无匹配）'),
      h(Text, { wrap: 'truncate' }, current ? core.skillDescription(root, current) : ''),
      h(Text, { dimColor: true }, '分发到：'),
      ...agents.map((a, i) => {
        const on = current ? (manifest[a.id]?.has(current) ?? false) : false;
        const active = focus === 'dist' && i === agentCursor;
        return h(
          Text, { key: a.id, color: active ? 'cyan' : undefined },
          `${active ? '❯' : ' '} [${on ? 'x' : ' '}] ${a.id}${core.agentInstalled(a) ? '' : '（未安装）'}`,
        );
      }),
    ),
  );
}

function MachinesView({ root, tick }: { root: string; tick: number }) {
  const machines = useMemo(() => core.machineStatuses(root), [root, tick]);
  return h(
    Box, { flexDirection: 'column', borderStyle: 'round', paddingX: 1 },
    h(Text, { bold: true }, `机器状态（${machines.length}）`),
    machines.length === 0
      ? h(Text, { dimColor: true }, '暂无 machines/*.json，各机器运行 sync 后出现')
      : machines.map((m) =>
          h(
            Text, { key: m.host },
            `${m.host}  ${m.branch}@${m.sha.slice(0, 7)}  断链 ${m.brokenLinks}  ${m.updatedAt}`,
          ),
        ),
  );
}

function AgentsView({ root, onNotice, bumpTick }: { root: string; onNotice: (s: string) => void; bumpTick: () => void }) {
  const [agents, setAgents] = useState<core.AgentDef[]>(() => core.loadAgents(root));
  const [cursor, setCursor] = useState(0);
  // 表单：step 0 不在表单；否则依次问 id → name → path；edit 模式只问 path
  const [form, setForm] = useState<{ mode: 'add' | 'edit'; step: number; draft: Partial<core.AgentDef>; buffer: string } | null>(null);

  useInput((input, key) => {
    if (form) {
      if (key.escape) {
        setForm(null);
        return;
      }
      if (key.return) {
        const next = { ...form, step: form.step + 1, buffer: '' };
        if (form.mode === 'add') {
          if (form.step === 0) next.draft = { ...form.draft, id: form.buffer.trim() };
          if (form.step === 1) next.draft = { ...form.draft, name: form.buffer.trim() };
          if (form.step === 2) {
            const draft = { ...form.draft, skillsPath: form.buffer.trim() } as core.AgentDef;
            if (!draft.id || !draft.skillsPath) {
              onNotice('id 与路径不能为空');
              setForm(null);
              return;
            }
            if (agents.some((a) => a.id === draft.id)) {
              onNotice(`agent id ${draft.id} 已存在`);
              setForm(null);
              return;
            }
            const next_ = [...agents, draft];
            core.saveAgents(root, next_);
            setAgents(next_);
            onNotice(`已添加 agent ${draft.id}（记得提交 agents.json）`);
            bumpTick();
            setForm(null);
            return;
          }
          setForm(next);
          return;
        }
        // edit 模式：一步，改 skillsPath
        const updated = agents.map((a, i) => (i === cursor ? { ...a, skillsPath: form.buffer.trim() } : a));
        core.saveAgents(root, updated);
        setAgents(updated);
        onNotice(`已更新 ${agents[cursor].id} 的路径（记得提交 agents.json）`);
        bumpTick();
        setForm(null);
        return;
      }
      if (key.backspace || key.delete) setForm({ ...form, buffer: form.buffer.slice(0, -1) });
      else if (input && !key.ctrl && !key.meta) setForm({ ...form, buffer: form.buffer + input });
      return;
    }
    if (key.upArrow) setCursor((c) => Math.max(0, c - 1));
    if (key.downArrow) setCursor((c) => Math.min(agents.length - 1, c + 1));
    if (input === 'n') setForm({ mode: 'add', step: 0, draft: {}, buffer: '' });
    if (input === 'e' && agents[cursor]) setForm({ mode: 'edit', step: 0, draft: {}, buffer: agents[cursor].skillsPath });
    if (input === 'd' && agents[cursor]) {
      const victim = agents[cursor];
      const next = agents.filter((_, i) => i !== cursor);
      core.saveAgents(root, next);
      setAgents(next);
      setCursor((c) => Math.max(0, c - 1));
      onNotice(`已删除 agent ${victim.id}（其清单条目仍在，可手工从 skills-manifest.json 移除）`);
      bumpTick();
    }
  });

  const prompt = form
    ? form.mode === 'add'
      ? ['id（如 claude）', '显示名', 'skills 目录路径（支持 ~）'][form.step]
      : `${agents[cursor]?.id} 的新路径`
    : null;

  return h(
    Box, { flexDirection: 'column', borderStyle: 'round', paddingX: 1 },
    h(Text, { bold: true }, `agent 注册表（${agents.length}）`),
    ...agents.map((a, i) =>
      h(
        Text, { key: a.id, color: i === cursor ? 'cyan' : undefined },
        `${i === cursor ? '❯' : ' '} ${a.id}  ${a.name}  ${a.skillsPath}  ${core.agentInstalled(a) ? '已安装' : '未安装'}`,
      ),
    ),
    form ? h(Text, { color: 'yellow' }, `${prompt}: ${form.buffer}▌`) : null,
  );
}

function InstallView({ root, remote, onNotice, onDone }: { root: string; remote: string; onNotice: (s: string) => void; onDone: () => void }) {
  const [buffer, setBuffer] = useState('');
  const [busy, setBusy] = useState(false);

  useInput((input, key) => {
    if (busy) return;
    if (key.escape) {
      onDone();
      return;
    }
    if (key.return) {
      const url = buffer.trim();
      if (!url) return;
      setBusy(true);
      try {
        onNotice(core.install(root, url, undefined, remote));
      } catch (err) {
        onNotice(`安装失败: ${(err as Error).message}`);
      }
      setBusy(false);
      onDone();
      return;
    }
    if (key.backspace || key.delete) setBuffer((b) => b.slice(0, -1));
    else if (input && !key.ctrl && !key.meta) setBuffer((b) => b + input);
  });

  return h(
    Box, { flexDirection: 'column', borderStyle: 'round', paddingX: 1 },
    h(Text, { bold: true }, '从 GitHub 安装技能（经 gh，入仓并推送）'),
    h(Text, null, busy ? '抓取中…' : `URL: ${buffer}▌`),
  );
}

export function App({ root, remote }: AppProps) {
  const { exit } = useApp();
  const [view, setView] = useState<View>('skills');
  const [notice, setNotice] = useState('');
  const [tick, setTick] = useState(0);
  const [searching, setSearching] = useState(false);
  const [manifest, setManifest] = useState<Record<string, Set<string>>>(() => {
    const m = core.loadManifest(root);
    return Object.fromEntries(Object.entries(m.agents).map(([k, v]) => [k, new Set(v)]));
  });
  const agents = useMemo(() => {
    try {
      return core.loadAgents(root);
    } catch {
      return [];
    }
  }, [root, tick]);

  useInput((input, key) => {
    if (searching) return; // 搜索输入时屏蔽全局键（q/l/s/m/a/i）
    if (input === 'q' || (key.ctrl && input === 'c')) {
      exit();
      return;
    }
    if (view !== 'skills') {
      if (view !== 'install' && (key.escape || input === 'm')) setView('skills');
      return; // 子视图自己处理输入
    }
    if (input === 'l') {
      const r = core.link(root);
      setNotice(`link 完成：${r.lines.length} 条动作${r.skippedAgents.length ? `，跳过未安装: ${r.skippedAgents.join('/')}` : ''}${r.missingSkills.length ? `，缺技能: ${r.missingSkills.join('/')}` : ''}`);
      setTick((t) => t + 1);
    }
    if (input === 's') {
      try {
        const lines = core.sync(root, remote);
        setNotice(`sync 完成：${lines[lines.length - 1]}`);
      } catch (err) {
        setNotice(`sync 失败: ${(err as Error).message}`);
      }
      setTick((t) => t + 1);
    }
    if (input === 'f') {
      setNotice(core.fetchRemote(root, remote) ? 'fetch 完成' : 'fetch 失败');
      setTick((t) => t + 1);
    }
    if (input === 'm') setView('machines');
    if (input === 'a') setView('agents');
    if (input === 'i') setView('install');
  });

  return h(
    Box, { flexDirection: 'column' },
    h(Text, { bold: true, color: 'magenta' }, 'myskills 管理'),
    view === 'skills'
      ? h(SkillsView, { root, agents, manifest, setManifest, onNotice: setNotice, bumpTick: () => setTick((t) => t + 1), searching, setSearching })
      : view === 'machines'
        ? h(MachinesView, { root, tick })
        : view === 'agents'
          ? h(AgentsView, { root, onNotice: setNotice, bumpTick: () => setTick((t) => t + 1) })
          : h(InstallView, { root, remote, onNotice: setNotice, onDone: () => { setView('skills'); setTick((t) => t + 1); } }),
    h(Text, { color: 'green' }, notice),
    h(StatusLine, { root, remote, tick }),
    h(Text, { dimColor: true }, HELP[view]),
  );
}

// 直接运行时渲染；也供 cli.ts 的 tui 子命令调用
export function start(remote: string) {
  render(h(App, { root: core.findRepoRoot(process.cwd()), remote }));
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/^.*\//, ''))) {
  const remoteIdx = process.argv.indexOf('--remote');
  const remote = remoteIdx > -1 ? process.argv[remoteIdx + 1] : (process.env.MYSKILLS_REMOTE ?? 'aliyun');
  start(remote);
}
