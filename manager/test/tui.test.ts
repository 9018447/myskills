import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
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
