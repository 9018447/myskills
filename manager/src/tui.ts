#!/usr/bin/env node
// myskills 管理 TUI：浏览/搜索技能、勾选分发、分组浏览、预设集、同步状态、机器仪表盘、agent 管理、GitHub 安装
// 启动目录向上找到 .myskills.json 时进入项目模式（勾选写入项目清单；项目级 agent 与注册表相同、路径去 ~/，默认全开，空格切换），o 切换项目/全局
// 不用 JSX（node 直接运行 TS 不支持），全部 createElement
import { createElement as h, useState, useMemo, useEffect } from 'react';
import { render, Box, Text, useApp, useInput } from 'ink';
import { join } from 'node:path';
import * as core from './core.ts';

type View = 'skills' | 'machines' | 'agents' | 'install' | 'presets';
type Focus = 'list' | 'dist';
type GroupMode = 'none' | 'agent' | 'source' | 'project' | 'preset';
type Scope = 'global' | 'project';

const GROUP_ORDER: GroupMode[] = ['none', 'agent', 'source', 'project', 'preset'];
const GROUP_LABEL: Record<GroupMode, string> = {
  none: '',
  agent: '按agent',
  source: '按来源',
  project: '按项目路径',
  preset: '按预设集',
};

interface AppProps {
  root: string;
  remote: string;
  // 检测到的项目根（含 .myskills.json）；null/缺省 = 纯全局模式。由 start() 探测传入，测试可显式指定
  project?: { root: string } | null;
}

const HELP: Record<View, string> = {
  skills: '↑↓ 移动  / 搜索  g=分组  Tab 切到分发  空格 勾选  l=link  s=sync  f=fetch  o=项目/全局  p=预设  m=机器  a=agent  i=安装  q=退出',
  machines: 'm/esc 返回  q=退出',
  agents: '↑↓ 移动  n=新增  e=改路径  d=删除  esc 返回  q=退出',
  install: '输入 URL 回车安装（集合仓用 /tree/ref/子目录）  esc 返回',
  presets: '↑↓ 移动  n=新建  e=编辑成员  d=删除  a=应用到agent  esc 返回  q=退出',
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

interface Row {
  header?: string;
  skill?: string;
}

function SkillsView({
  root, agents, manifest, onNotice, bumpTick, tick, searching, setSearching, scope, project, projectSkills,
}: {
  root: string;
  agents: core.AgentDef[];
  manifest: Record<string, Set<string>>;
  onNotice: (s: string) => void;
  bumpTick: () => void;
  tick: number;
  searching: boolean;
  setSearching: (b: boolean) => void;
  scope: Scope;
  project: { root: string } | null;
  projectSkills: Set<string>;
}) {
  const [filter, setFilter] = useState('');
  const [pos, setPos] = useState(0); // 在「可选中的技能行」序列中的位置（分组模式下同一技能可出现多次，按行实例导航）
  const [focus, setFocus] = useState<Focus>('list');
  const [agentCursor, setAgentCursor] = useState(0);
  const [groupMode, setGroupMode] = useState<GroupMode>('none');

  const skills = useMemo(() => core.listRepoSkills(root), [root]);
  const shown = useMemo(
    () => (filter ? skills.filter((s) => s.toLowerCase().includes(filter.toLowerCase())) : skills),
    [skills, filter],
  );

  const presets = useMemo(() => core.loadManifest(root).presets ?? {}, [root, tick]);
  const sources = useMemo(() => (groupMode === 'source' ? core.skillSources(root) : {}), [root, tick, groupMode]);
  // 项目级 agent（注册表家目录 agent 去 ~/ 派生）及开启状态；显式 targets 优先，省略时默认全开
  const projAgentRows = useMemo(
    () => (scope === 'project' && project ? core.projectTargetStates(project.root, root) : []),
    [scope, project, root, tick],
  );

  // 分组浏览：把技能列表渲染成「分组头 + 技能」行序列；同一技能可出现在多个组下
  const rows = useMemo<Row[]>(() => {
    if (groupMode === 'none') return shown.map((s) => ({ skill: s }));
    const shownSet = new Set(shown);
    const skillSet = new Set(skills);
    const assigned = new Set<string>();
    const groups: [string, string[]][] = [];
    if (groupMode === 'agent') {
      const sorted = [...agents].sort(
        (a, b) => core.agentProjectGroup(a).localeCompare(core.agentProjectGroup(b)) || a.id.localeCompare(b.id),
      );
      for (const a of sorted) {
        const members = [...(manifest[a.id] ?? [])].filter((s) => skillSet.has(s)).sort();
        groups.push([`${core.agentProjectGroup(a)} / ${a.id}`, members]);
        members.forEach((m) => assigned.add(m));
      }
      const rest = skills.filter((s) => !assigned.has(s));
      if (rest.length) groups.push(['未分发', rest]);
    } else if (groupMode === 'source') {
      const bySource = new Map<string, string[]>();
      for (const s of skills) {
        const src = sources[s] ?? 'local';
        const label = src === 'local' ? '本地/未知' : `github.com/${src}`;
        const list = bySource.get(label) ?? [];
        list.push(s);
        bySource.set(label, list);
      }
      for (const [label, members] of [...bySource.entries()].sort((a, b) => a[0].localeCompare(b[0]))) groups.push([label, members]);
    } else if (groupMode === 'project') {
      const byProject = new Map<string, Set<string>>();
      for (const a of agents) {
        const g = core.agentProjectGroup(a);
        const set = byProject.get(g) ?? new Set<string>();
        byProject.set(g, set);
        for (const s of manifest[a.id] ?? []) if (skillSet.has(s)) set.add(s);
      }
      for (const [label, set] of [...byProject.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
        groups.push([label, [...set].sort()]);
        set.forEach((s) => assigned.add(s));
      }
      const rest = skills.filter((s) => !assigned.has(s));
      if (rest.length) groups.push(['未分发', rest]);
    } else {
      for (const [name, members] of Object.entries(presets).sort((a, b) => a[0].localeCompare(b[0]))) {
        const valid = members.filter((s) => skillSet.has(s));
        groups.push([`预设: ${name}`, valid]);
        valid.forEach((s) => assigned.add(s));
      }
      const rest = skills.filter((s) => !assigned.has(s));
      if (rest.length) groups.push(['不在任何预设', rest]);
    }
    const out: Row[] = [];
    for (const [label, members] of groups) {
      const visible = members.filter((s) => shownSet.has(s));
      if (!visible.length) continue;
      out.push({ header: label });
      for (const m of visible) out.push({ skill: m });
    }
    return out;
  }, [groupMode, shown, skills, agents, manifest, sources, presets]);

  // 光标落在技能行实例上（分组头不可选中）；同一技能出现在多个组时各是独立行，互不串扰
  const skillRowIdx = useMemo(() => rows.flatMap((r, i) => (r.skill !== undefined ? [i] : [])), [rows]);
  const clampedPos = Math.min(pos, Math.max(0, skillRowIdx.length - 1));
  const currentRowIdx = skillRowIdx.length ? skillRowIdx[clampedPos] : -1;
  const current = currentRowIdx >= 0 ? rows[currentRowIdx].skill : undefined;

  useInput((input, key) => {
    if (searching) {
      if (key.escape) setSearching(false);
      else if (key.return) setSearching(false);
      else if (key.backspace || key.delete) setFilter((f) => f.slice(0, -1));
      else if (input && !key.ctrl && !key.meta) setFilter((f) => f + input);
      setPos(0);
      return;
    }
    if (input === '/') {
      setSearching(true);
      return;
    }
    if (input === 'g') {
      setGroupMode((m) => GROUP_ORDER[(GROUP_ORDER.indexOf(m) + 1) % GROUP_ORDER.length]);
      setPos(0);
      return;
    }
    if (key.tab) {
      setFocus((f) => (f === 'list' ? 'dist' : 'list'));
      return;
    }
    if (focus === 'list') {
      if (key.upArrow) setPos((p) => Math.max(0, p - 1));
      if (key.downArrow) setPos((p) => Math.min(skillRowIdx.length - 1, p + 1));
      if (input === ' ') onNotice('空格只在右侧分发面板有效：先按 Tab 切过去，再空格勾选');
      return;
    }
    // focus === 'dist'
    if (scope === 'project') {
      // 项目面板：第 0 行勾选技能进项目清单（对所有开启的目标生效），其余行切换各项目级 agent 的开启状态
      if (key.upArrow) setAgentCursor((c) => Math.max(0, c - 1));
      if (key.downArrow) setAgentCursor((c) => Math.min(projAgentRows.length, c + 1));
      if (input === ' ' && project) {
        if (agentCursor === 0) {
          if (!current) return;
          const on = core.toggleProjectSkill(project.root, current);
          onNotice(`${on ? '勾选' : '取消'} ${current} → 项目清单（按 l 生效）`);
        } else {
          const row = projAgentRows[agentCursor - 1];
          if (!row) return;
          const on = core.toggleProjectTarget(project.root, root, row.target);
          onNotice(`${on ? '开启' : '关闭'}项目目标 ${row.id} → ${row.target}（按 l 生效）`);
        }
        bumpTick();
      }
      return;
    }
    if (key.upArrow) setAgentCursor((c) => Math.max(0, c - 1));
    if (key.downArrow) setAgentCursor((c) => Math.min(agents.length - 1, c + 1));
    if (input === ' ' && current && agents[agentCursor]) {
      const agentId = agents[agentCursor].id;
      const on = core.toggleSkill(root, agentId, current);
      onNotice(`${on ? '勾选' : '取消'} ${current} → ${agentId}（按 l 生效，按 s 提交推送）`);
      bumpTick();
    }
  });

  const height = 15;
  const start = Math.max(0, Math.min(currentRowIdx - Math.floor(height / 2), Math.max(0, rows.length - height)));
  const windowRows = rows.slice(start, start + height);

  return h(
    Box, { flexDirection: 'row', gap: 2 },
    h(
      Box, { flexDirection: 'column', width: 34, borderStyle: 'round', borderColor: focus === 'list' ? 'cyan' : 'gray', paddingX: 1 },
      h(
        Text, { bold: true },
        `技能（${shown.length}/${skills.length}）${groupMode !== 'none' ? ` [${GROUP_LABEL[groupMode]}]` : ''}${searching ? ` 搜索: ${filter}▌` : filter ? ` 过滤: ${filter}` : ''}`,
      ),
      ...windowRows.map((r, i) => {
        if (r.header !== undefined) return h(Text, { key: `h${start + i}`, color: 'yellow', bold: true }, `▸ ${r.header}`);
        const active = start + i === currentRowIdx;
        return h(Text, { key: `s${start + i}`, color: active ? 'cyan' : undefined, bold: active }, `${active ? '❯' : ' '} ${r.skill}`);
      }),
    ),
    h(
      Box, { flexDirection: 'column', flexGrow: 1, borderStyle: 'round', borderColor: focus === 'dist' ? 'cyan' : 'gray', paddingX: 1 },
      h(Text, { bold: true }, current ?? '（无匹配）'),
      h(Text, { wrap: 'truncate' }, current ? core.skillDescription(root, current) : ''),
      h(Text, { dimColor: true }, scope === 'project' ? '分发到项目：' : '分发到：'),
      ...(scope === 'project'
        ? [
            h(
              Text,
              { key: 'proj', color: focus === 'dist' && agentCursor === 0 ? 'cyan' : undefined },
              `${focus === 'dist' && agentCursor === 0 ? '❯' : ' '} [${current && projectSkills.has(current) ? 'x' : ' '}] 项目清单（.myskills.json）`,
            ),
            ...(projAgentRows.length
              ? projAgentRows.map((r, i) =>
                  h(
                    Text,
                    { key: r.target, color: focus === 'dist' && agentCursor === i + 1 ? 'cyan' : undefined },
                    `${focus === 'dist' && agentCursor === i + 1 ? '❯' : ' '} [${r.enabled ? 'x' : ' '}] ${r.id} → ${r.target}`,
                  ),
                )
              : [h(Text, { key: 'none', dimColor: true }, '  （agents.json 中没有 ~/ 开头的家目录 agent，可在 .myskills.json 用 targets 指定）')]),
          ]
        : agents.map((a, i) => {
            const on = current ? (manifest[a.id]?.has(current) ?? false) : false;
            const active = focus === 'dist' && i === agentCursor;
            return h(
              Text, { key: a.id, color: active ? 'cyan' : undefined },
              `${active ? '❯' : ' '} [${on ? 'x' : ' '}] ${a.id}${core.agentInstalled(a) ? '' : '（未安装）'}`,
            );
          })),
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

type PresetMode = 'list' | 'new' | 'members' | 'apply';

function PresetsView({
  root, agents, tick, onNotice, bumpTick, setBusy,
}: {
  root: string;
  agents: core.AgentDef[];
  tick: number;
  onNotice: (s: string) => void;
  bumpTick: () => void;
  setBusy: (b: boolean) => void;
}) {
  const [mode, setMode] = useState<PresetMode>('list');
  const [cursor, setCursor] = useState(0);
  const [buffer, setBuffer] = useState('');
  const [editing, setEditing] = useState(''); // members/apply 模式作用的预设名
  const [sel, setSel] = useState<Set<string>>(new Set()); // members 模式的勾选
  const [applySel, setApplySel] = useState<Set<string>>(new Set()); // apply 模式勾选的 agent
  const [mCursor, setMCursor] = useState(0);
  const [mFilter, setMFilter] = useState('');
  const [mSearching, setMSearching] = useState(false);

  const presets = useMemo(() => core.loadManifest(root).presets ?? {}, [root, tick]);
  const names = useMemo(() => Object.keys(presets).sort(), [presets]);
  const skills = useMemo(() => core.listRepoSkills(root), [root]);
  const mShown = useMemo(
    () => (mFilter ? skills.filter((s) => s.toLowerCase().includes(mFilter.toLowerCase())) : skills),
    [skills, mFilter],
  );

  useEffect(() => {
    setBusy(mode !== 'list' || mSearching);
  }, [mode, mSearching, setBusy]);
  useEffect(() => () => setBusy(false), [setBusy]);

  const openMembers = (name: string) => {
    setEditing(name);
    setSel(new Set(presets[name] ?? []));
    setMCursor(0);
    setMFilter('');
    setMSearching(false);
    setMode('members');
  };

  useInput((input, key) => {
    if (mode === 'new') {
      if (key.escape) setMode('list');
      else if (key.return) {
        const name = buffer.trim();
        if (!name) return;
        openMembers(name);
      } else if (key.backspace || key.delete) setBuffer((b) => b.slice(0, -1));
      else if (input && !key.ctrl && !key.meta) setBuffer((b) => b + input);
      return;
    }
    if (mode === 'members') {
      if (mSearching) {
        if (key.escape || key.return) setMSearching(false);
        else if (key.backspace || key.delete) setMFilter((f) => f.slice(0, -1));
        else if (input && !key.ctrl && !key.meta) setMFilter((f) => f + input);
        setMCursor(0);
        return;
      }
      if (key.escape) {
        setMode('list');
        return;
      }
      if (input === '/') {
        setMSearching(true);
        return;
      }
      if (key.upArrow) setMCursor((c) => Math.max(0, c - 1));
      if (key.downArrow) setMCursor((c) => Math.min(mShown.length - 1, c + 1));
      if (input === ' ' && mShown[mCursor]) {
        const s = mShown[mCursor];
        const next = new Set(sel);
        if (next.has(s)) next.delete(s);
        else next.add(s);
        setSel(next);
      }
      if (key.return) {
        core.setPreset(root, editing, [...sel]);
        onNotice(`预设 ${editing} 已保存（${sel.size} 个技能；应用到 agent 后按 l 生效，按 s 提交推送）`);
        bumpTick();
        setMode('list');
      }
      return;
    }
    if (mode === 'apply') {
      if (key.escape) {
        setMode('list');
        return;
      }
      if (key.upArrow) setMCursor((c) => Math.max(0, c - 1));
      if (key.downArrow) setMCursor((c) => Math.min(agents.length - 1, c + 1));
      if (input === ' ' && agents[mCursor]) {
        const id = agents[mCursor].id;
        const next = new Set(applySel);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        setApplySel(next);
      }
      if (key.return) {
        if (applySel.size === 0) {
          onNotice('未勾选任何 agent，应用取消（空格勾选，回车确认）');
          return;
        }
        const r = core.applyPreset(root, editing, [...applySel]);
        const parts = Object.entries(r.added).map(([id, n]) => `${id}+${n}`);
        onNotice(`已应用预设 ${editing}：${parts.join('  ')}${r.missing.length ? `；仓库中不存在已跳过: ${r.missing.join('/')}` : ''}（按 l 生效，按 s 提交推送）`);
        bumpTick();
        setMode('list');
      }
      return;
    }
    // mode === 'list'
    if (key.upArrow) setCursor((c) => Math.max(0, c - 1));
    if (key.downArrow) setCursor((c) => Math.min(names.length - 1, c + 1));
    if (input === 'n') {
      setBuffer('');
      setMode('new');
    }
    if (input === 'e' && names[cursor]) openMembers(names[cursor]);
    if (input === 'd' && names[cursor]) {
      const victim = names[cursor];
      core.deletePreset(root, victim);
      setCursor((c) => Math.max(0, c - 1));
      onNotice(`已删除预设 ${victim}`);
      bumpTick();
    }
    if (input === 'a' && names[cursor]) {
      setEditing(names[cursor]);
      setApplySel(new Set());
      setMCursor(0);
      setMode('apply');
    }
  });

  if (mode === 'members') {
    const height = 15;
    const start = Math.max(0, Math.min(mCursor - Math.floor(height / 2), Math.max(0, mShown.length - height)));
    const windowSkills = mShown.slice(start, start + height);
    return h(
      Box, { flexDirection: 'column', borderStyle: 'round', paddingX: 1 },
      h(Text, { bold: true }, `编辑预设: ${editing}（已选 ${sel.size}）${mSearching ? ` 搜索: ${mFilter}▌` : mFilter ? ` 过滤: ${mFilter}` : ''}`),
      ...windowSkills.map((s, i) => {
        const active = start + i === mCursor;
        return h(Text, { key: s, color: active ? 'cyan' : undefined }, `${active ? '❯' : ' '} [${sel.has(s) ? 'x' : ' '}] ${s}`);
      }),
      h(Text, { dimColor: true }, '↑↓ 移动  空格 勾选  / 搜索  回车 保存  esc 取消'),
    );
  }
  if (mode === 'apply') {
    return h(
      Box, { flexDirection: 'column', borderStyle: 'round', paddingX: 1 },
      h(Text, { bold: true }, `应用预设 ${editing} 到（空格勾选，回车确认）：`),
      ...agents.map((a, i) => {
        const active = i === mCursor;
        return h(
          Text, { key: a.id, color: active ? 'cyan' : undefined },
          `${active ? '❯' : ' '} [${applySel.has(a.id) ? 'x' : ' '}] ${a.id}  ${core.agentProjectGroup(a)}${core.agentInstalled(a) ? '' : '（未安装）'}`,
        );
      }),
      h(Text, { dimColor: true }, '并集追加到所选 agent 的清单；esc 取消'),
    );
  }
  return h(
    Box, { flexDirection: 'column', borderStyle: 'round', paddingX: 1 },
    h(Text, { bold: true }, `预设集（${names.length}）`),
    names.length === 0 && mode === 'list' ? h(Text, { dimColor: true }, '暂无预设，按 n 新建') : null,
    ...names.map((n, i) =>
      h(
        Text, { key: n, color: i === cursor ? 'cyan' : undefined },
        `${i === cursor ? '❯' : ' '} ${n}（${presets[n].length}）: ${presets[n].join(', ')}`,
      ),
    ),
    mode === 'new' ? h(Text, { color: 'yellow' }, `预设名: ${buffer}▌`) : null,
  );
}

function AgentsView({ root, onNotice, bumpTick, setBusy }: { root: string; onNotice: (s: string) => void; bumpTick: () => void; setBusy: (b: boolean) => void }) {
  const [agents, setAgents] = useState<core.AgentDef[]>(() => core.loadAgents(root));
  const [cursor, setCursor] = useState(0);
  // 表单：step 0 不在表单；否则依次问 id → name → path；edit 模式只问 path
  const [form, setForm] = useState<{ mode: 'add' | 'edit'; step: number; draft: Partial<core.AgentDef>; buffer: string } | null>(null);

  useEffect(() => {
    setBusy(form !== null); // 表单输入时屏蔽全局键，否则输入 l/s/f 会触发 link/sync/fetch
  }, [form, setBusy]);
  useEffect(() => () => setBusy(false), [setBusy]);

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
            onNotice(`已添加 agent ${draft.id}（按 s 提交推送）`);
            bumpTick();
            setForm(null);
            return;
          }
          setForm(next);
          return;
        }
        // edit 模式：一步，改 skillsPath；与新增一样拒绝空路径
        const newPath = form.buffer.trim();
        if (!newPath) {
          onNotice('路径不能为空');
          setForm(null);
          return;
        }
        const updated = agents.map((a, i) => (i === cursor ? { ...a, skillsPath: newPath } : a));
        core.saveAgents(root, updated);
        setAgents(updated);
        onNotice(`已更新 ${agents[cursor].id} 的路径（按 s 提交推送）`);
        bumpTick();
        setForm(null);
        return;
      }
      if (key.backspace || key.delete) setForm((f) => (f ? { ...f, buffer: f.buffer.slice(0, -1) } : f));
      else if (input && !key.ctrl && !key.meta) setForm((f) => (f ? { ...f, buffer: f.buffer + input } : f));
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
      ? ['id（如 claude）', '显示名', 'skills 目录路径（支持 ~；项目级 agent 填项目内的绝对路径）'][form.step]
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

export function App({ root, remote, project = null }: AppProps) {
  const { exit } = useApp();
  const [view, setView] = useState<View>('skills');
  const [notice, setNotice] = useState('');
  const [tick, setTick] = useState(0);
  const [searching, setSearching] = useState(false);
  const [viewBusy, setViewBusy] = useState(false); // 子视图处于表单/多选等子模式时屏蔽全局键
  const [scope, setScope] = useState<Scope>(project ? 'project' : 'global');
  const [projectSkills, setProjectSkills] = useState<Set<string>>(new Set());
  const [manifest, setManifest] = useState<Record<string, Set<string>>>(() => {
    const m = core.loadManifest(root);
    return Object.fromEntries(Object.entries(m.agents).map(([k, v]) => [k, new Set(v)]));
  });
  // 清单以磁盘文件为准：任何子视图写入后 bumpTick，这里重新加载，避免勾选状态停留在旧快照
  useEffect(() => {
    const m = core.loadManifest(root);
    setManifest(Object.fromEntries(Object.entries(m.agents).map(([k, v]) => [k, new Set(v)])));
  }, [root, tick]);
  const agents = useMemo(() => {
    try {
      return core.loadAgents(root);
    } catch {
      return [];
    }
  }, [root, tick]);
  // 项目清单同样以磁盘为准：勾选后 bumpTick 重新加载；清单损坏时降级为空集合
  useEffect(() => {
    if (!project) {
      setProjectSkills(new Set());
      return;
    }
    try {
      setProjectSkills(new Set(core.loadProjectManifest(join(project.root, core.PROJECT_MANIFEST_FILE)).skills));
    } catch {
      setProjectSkills(new Set());
    }
  }, [project, tick]);
  const [running, setRunning] = useState(false); // 有耗时操作（link/sync/fetch）在跑时屏蔽全局键

  // 耗时操作先渲染「执行中」帧，再异步执行，避免界面卡住让人以为没按上
  const runAction = (label: string, fn: () => string) => {
    setRunning(true);
    setNotice(`${label} 执行中…`);
    setTimeout(() => {
      try {
        setNotice(fn());
      } catch (err) {
        setNotice(`${label} 失败: ${(err as Error).message}`);
      }
      setRunning(false);
      setTick((t) => t + 1);
    }, 20);
  };

  useInput((input, key) => {
    if (searching || viewBusy || running) return; // 搜索/子模式/耗时操作执行中屏蔽全局键（q/l/s/m/a/i/p）
    if ((input === 'q' && view !== 'install') || (key.ctrl && input === 'c')) {
      exit();
      return;
    }
    // l/s/f/o 全局可用（含预设集等子视图；install 视图是文本输入，除外）
    if (view !== 'install') {
      if (input === 'l') {
        runAction('link', () => {
          if (scope === 'project' && project) {
            const r = core.linkProject(project.root, root);
            return `项目 link 完成：${r.lines.length} 条动作${r.missingSkills.length ? `，缺技能: ${r.missingSkills.join('/')}` : ''}`;
          }
          const r = core.link(root);
          return `link 完成：${r.lines.length} 条动作${r.skippedAgents.length ? `，跳过未安装: ${r.skippedAgents.join('/')}` : ''}${r.missingSkills.length ? `，缺技能: ${r.missingSkills.join('/')}` : ''}`;
        });
        return;
      }
      if (input === 's') {
        runAction('sync', () => `sync 完成：${core.sync(root, remote).at(-1)}`);
        return;
      }
      if (input === 'f') {
        runAction('fetch', () => (core.fetchRemote(root, remote) ? 'fetch 完成' : 'fetch 失败'));
        return;
      }
      if (input === 'o' && project) {
        const next: Scope = scope === 'project' ? 'global' : 'project';
        setScope(next);
        setNotice(next === 'project' ? `已切到项目模式：${project.root}` : '已切到全局模式');
        return;
      }
    }
    if (view !== 'skills') {
      if (view !== 'install' && (key.escape || input === 'm')) setView('skills');
      return; // 子视图自己处理输入
    }
    if (input === 'm') setView('machines');
    if (input === 'a') setView('agents');
    if (input === 'i') setView('install');
    if (input === 'p') setView('presets');
  });

  return h(
    Box, { flexDirection: 'column' },
    h(
      Text, { bold: true, color: 'magenta' },
      scope === 'project' && project ? `myskills 管理（项目模式：${project.root}，o 切回全局）` : 'myskills 管理',
    ),
    view === 'skills'
      ? h(SkillsView, { root, agents, manifest, onNotice: setNotice, bumpTick: () => setTick((t) => t + 1), tick, searching, setSearching, scope, project, projectSkills })
      : view === 'machines'
        ? h(MachinesView, { root, tick })
        : view === 'agents'
          ? h(AgentsView, { root, onNotice: setNotice, bumpTick: () => setTick((t) => t + 1), setBusy: setViewBusy })
          : view === 'presets'
            ? h(PresetsView, { root, agents, tick, onNotice: setNotice, bumpTick: () => setTick((t) => t + 1), setBusy: setViewBusy })
            : h(InstallView, { root, remote, onNotice: setNotice, onDone: () => { setView('skills'); setTick((t) => t + 1); } }),
    h(Text, { color: running ? 'yellow' : 'green' }, notice),
    h(StatusLine, { root, remote, tick }),
    h(Text, { dimColor: true }, HELP[view]),
  );
}

// 直接运行时渲染；也供 cli.ts 的 tui 子命令调用。启动目录向上找到 .myskills.json 时进入项目模式
export function start(remote: string) {
  render(h(App, { root: core.findRepoRoot(), remote, project: core.findProjectRoot() }));
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/^.*\//, ''))) {
  const remoteIdx = process.argv.indexOf('--remote');
  const remote = remoteIdx > -1 ? process.argv[remoteIdx + 1] : (process.env.MYSKILLS_REMOTE ?? 'aliyun');
  start(remote);
}
