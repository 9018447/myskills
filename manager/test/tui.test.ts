import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, lstatSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { createElement as h } from 'react';
import { render } from 'ink-testing-library';
import { App } from '../src/tui.ts';

function makeFixture() {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-tui-'));
  const repo = join(tmp, 'repo');
  const home = join(tmp, 'home');
  mkdirSync(repo, { recursive: true });
  mkdirSync(join(home, '.claude'), { recursive: true });
  for (const s of ['alpha', 'beta']) {
    mkdirSync(join(repo, s));
    writeFileSync(join(repo, s, 'SKILL.md'), `---\nname: ${s}\ndescription: ${s} 描述\n---\n`);
  }
  writeFileSync(
    join(repo, 'agents.json'),
    JSON.stringify({ agents: [{ id: 'claude', name: 'Claude Code', skillsPath: join(home, '.claude', 'skills') }] }, null, 2),
  );
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }, null, 2));
  return { repo, home };
}

const tick = () => new Promise((r) => setTimeout(r, 60));

test('tui: 渲染技能列表与 agent 分发面板', async () => {
  const { repo } = makeFixture();
  const { lastFrame, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  const frame = lastFrame()!;
  assert.match(frame, /alpha/);
  assert.match(frame, /beta/);
  assert.match(frame, /claude/);
  unmount();
});

test('tui: Tab 切到分发面板后空格勾选，写入 skills-manifest.json', async () => {
  const { repo } = makeFixture();
  const { stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write('\t'); // 切到分发面板
  await tick();
  stdin.write(' '); // 勾选当前技能 alpha → claude
  await tick();
  const manifest = JSON.parse(readFileSync(join(repo, 'skills-manifest.json'), 'utf8'));
  assert.deepEqual(manifest.agents.claude, ['alpha']);
  unmount();
});

test('tui: 搜索模式屏蔽全局键，q 不退出而是进入过滤词', async () => {
  const { repo } = makeFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write('/');
  await tick();
  stdin.write('b');
  await tick();
  assert.match(lastFrame()!, /beta/);
  assert.doesNotMatch(lastFrame()!, /❯ alpha/);
  stdin.write('q'); // 若泄漏到全局键会直接退出
  await tick();
  assert.match(lastFrame()!, /技能（0\/2）/); // 过滤词 bq 无匹配，证明 q 进了搜索框
  unmount();
});

test('tui: 应用预设后返回技能页，分发勾选状态已刷新', async () => {
  const { repo } = makeFixture();
  writeFileSync(
    join(repo, 'skills-manifest.json'),
    JSON.stringify({ agents: {}, presets: { base: ['alpha'] } }, null, 2),
  );
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write('p'); // 预设视图
  await tick();
  stdin.write('a'); // 应用第一个预设
  await tick();
  stdin.write(' '); // 勾选 claude
  await tick();
  stdin.write('\r'); // 确认应用
  await tick();
  stdin.write('\x1b'); // 返回技能页
  await tick();
  assert.match(lastFrame()!, /\[x\] claude/); // 勾选状态必须反映刚应用的预设，而不是旧的空快照
  unmount();
});

test('tui: 焦点在技能列表时按空格给出提示，而不是无反应', async () => {
  const { repo } = makeFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write(' '); // 焦点默认在左侧列表
  await tick();
  assert.match(lastFrame()!, /先按 Tab 切过去/);
  unmount();
});

test('tui: 按 l 有执行反馈，完成后提示动作数', async () => {
  const { repo } = makeFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write('l');
  await tick();
  await tick();
  assert.match(lastFrame()!, /link 完成/);
  unmount();
});

test('tui: 预设集视图里 l/s/f 全局可用', async () => {
  const { repo } = makeFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write('p'); // 进预设集视图
  await tick();
  stdin.write('l'); // 不返回技能页，直接按 l
  await tick();
  await tick();
  assert.match(lastFrame()!, /link 完成/);
  unmount();
});

test('tui: agent 表单输入时 l 进入输入框，不触发全局 link', async () => {
  const { repo } = makeFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin' }));
  await tick();
  stdin.write('a'); // 进 agent 注册表视图
  await tick();
  stdin.write('n'); // 打开新增表单
  await tick();
  stdin.write('l'); // 应进入 id 输入框
  await tick();
  await tick();
  assert.match(lastFrame()!, /id（如 claude）: l/);
  assert.doesNotMatch(lastFrame()!, /link 完成/);
  unmount();
});

// 项目模式 fixture：中心仓库 + 一个含 .myskills.json 与 .claude/skills 的项目目录
function makeProjectTuiFixture() {
  const { repo, home } = makeFixture();
  // 候选目标由 ~/ 前缀的家目录 agent 派生，重写 agents.json 为字面 ~/ 形式
  writeFileSync(
    join(repo, 'agents.json'),
    JSON.stringify({ agents: [{ id: 'claude', name: 'Claude Code', skillsPath: '~/.claude/skills' }] }, null, 2),
  );
  const project = join(dirname(repo), 'project');
  mkdirSync(join(project, '.claude', 'skills'), { recursive: true });
  writeFileSync(join(project, '.myskills.json'), JSON.stringify({ skills: [] }, null, 2));
  return { repo, home, project };
}

test('tui: 项目模式下渲染项目清单面板，空格勾选写入 .myskills.json', async () => {
  const { repo, project } = makeProjectTuiFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin', project: { root: project } }));
  await tick();
  assert.match(lastFrame()!, /项目模式/);
  assert.match(lastFrame()!, /项目清单（\.myskills\.json）/);
  assert.match(lastFrame()!, /\[x\] claude → \.claude\/skills/); // 项目级 agent 与注册表相同、路径去 ~/，默认开启
  stdin.write('\t'); // 切到分发面板
  await tick();
  stdin.write(' '); // 勾选 alpha 进项目清单
  await tick();
  const pm = JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8'));
  assert.deepEqual(pm.skills, ['alpha']);
  unmount();
});

test('tui: 项目模式下空格切换项目级 agent 开关，写入显式 targets', async () => {
  const { repo, project } = makeProjectTuiFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin', project: { root: project } }));
  await tick();
  stdin.write('\t'); // 切到分发面板
  await tick();
  stdin.write('\x1b[B'); // 下移到 claude 行
  await tick();
  stdin.write(' '); // 关闭 claude 目标
  await tick();
  assert.match(lastFrame()!, /\[ \] claude → \.claude\/skills/);
  const pm = JSON.parse(readFileSync(join(project, '.myskills.json'), 'utf8'));
  assert.deepEqual(pm.targets, [], '唯一的 agent 被关闭后 targets 固化为空数组');
  unmount();
});

test('tui: 项目模式下 l 走 linkProject，在项目目录建链', async () => {
  const { repo, project } = makeProjectTuiFixture();
  writeFileSync(join(project, '.myskills.json'), JSON.stringify({ skills: ['alpha'] }, null, 2));
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin', project: { root: project } }));
  await tick();
  stdin.write('l');
  await tick();
  await tick();
  assert.match(lastFrame()!, /项目 link 完成/);
  assert.ok(lstatSync(join(project, '.claude', 'skills', 'alpha')).isSymbolicLink());
  unmount();
});

test('tui: o 键在项目与全局模式间切换', async () => {
  const { repo, project } = makeProjectTuiFixture();
  const { lastFrame, stdin, unmount } = render(h(App, { root: repo, remote: 'origin', project: { root: project } }));
  await tick();
  assert.match(lastFrame()!, /项目模式/);
  stdin.write('o'); // 切回全局
  await tick();
  assert.doesNotMatch(lastFrame()!, /项目模式/);
  assert.match(lastFrame()!, /\[ \] claude/); // 全局面板回到 agent 列表
  stdin.write('o'); // 再切回项目
  await tick();
  assert.match(lastFrame()!, /项目模式/);
  unmount();
});
