// 票 05：启动交互确认顶层未知非技能文件夹——同意移入 presets/ 成为预设、拒绝记持久化名单、
// 豁免名单（manager/machines/testdir/presets）、非交互环境只提示不动手。
// 交互用注入的 confirm 函数模拟（不等真 stdin），非交互分支用 tty:false 模拟 stdin 非 TTY
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, readFileSync, lstatSync, readlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { promptUnknownTopDirs, reconcilePresets, PRESET_PROMPT_FILE } from '../src/core.ts';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

function makeRepo() {
  const repo = mkdtempSync(join(tmpdir(), 'myskills-startupprompt-'));
  writeFileSync(join(repo, 'skills-manifest.json'), JSON.stringify({ agents: {} }, null, 2));
  writeFileSync(join(repo, 'agents.json'), JSON.stringify({ agents: [] }, null, 2));
  return repo;
}

// 在仓库内相对路径 rel 处造一个技能真身
function makeSkill(repo: string, rel: string) {
  mkdirSync(join(repo, rel), { recursive: true });
  writeFileSync(join(repo, rel, 'SKILL.md'), `---\nname: ${rel.split('/').pop()}\n---\n`);
}

// 不应被调用的 confirm：被调即抛错
function never() {
  return () => {
    throw new Error('confirm 不应被调用');
  };
}

test('同意：文件夹移入 presets/ 成为预设，随后 reconcile 成员获得顶层链接，不写拒绝名单', async () => {
  const repo = makeRepo();
  makeSkill(repo, 'real-skill'); // 顶层技能：不该被询问
  makeSkill(repo, 'stuff/alpha');
  makeSkill(repo, 'stuff/sub/beta');
  const asked: string[] = [];
  const lines = await promptUnknownTopDirs(repo, { tty: true, confirm: (d) => (asked.push(d), true) });
  assert.deepEqual(asked, ['stuff']);
  assert.ok(!existsSync(join(repo, 'stuff')), '顶层原文件夹应已移走');
  assert.ok(existsSync(join(repo, 'presets/stuff/alpha/SKILL.md')));
  assert.match(lines.join('\n'), /stuff/);
  // 接线语义：确认发生在 reconcile 之前，移动后的文件夹立即被 reconcile 建链
  reconcilePresets(repo);
  assert.ok(lstatSync(join(repo, 'alpha')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'alpha')), 'presets/stuff/alpha');
  assert.ok(lstatSync(join(repo, 'beta')).isSymbolicLink());
  assert.equal(readlinkSync(join(repo, 'beta')), 'presets/stuff/sub/beta');
  assert.ok(!existsSync(join(repo, PRESET_PROMPT_FILE)), '同意不写拒绝名单');
});

test('拒绝：写入持久化名单，文件夹不动，连续启动不再询问；手工清空名单后重新询问', async () => {
  const repo = makeRepo();
  makeSkill(repo, 'stuff/alpha');
  const lines = await promptUnknownTopDirs(repo, { tty: true, confirm: () => false });
  assert.ok(existsSync(join(repo, 'stuff/alpha/SKILL.md')), '拒绝后文件夹留在原地');
  const saved = JSON.parse(readFileSync(join(repo, PRESET_PROMPT_FILE), 'utf8'));
  assert.deepEqual(saved.dismissed, ['stuff']);
  assert.match(lines.join('\n'), new RegExp(PRESET_PROMPT_FILE));
  // 第二次启动：不再询问、无输出、不动手
  let called = 0;
  const lines2 = await promptUnknownTopDirs(repo, { tty: true, confirm: () => (called++, true) });
  assert.equal(called, 0);
  assert.deepEqual(lines2, []);
  assert.ok(existsSync(join(repo, 'stuff/alpha/SKILL.md')));
  // 用户手工清空名单（跨进程持久的可编辑文件）→ 重新询问
  writeFileSync(join(repo, PRESET_PROMPT_FILE), JSON.stringify({ dismissed: [] }, null, 2));
  await promptUnknownTopDirs(repo, { tty: true, confirm: () => true });
  assert.ok(existsSync(join(repo, 'presets/stuff/alpha/SKILL.md')));
});

test('豁免：manager/machines/testdir/presets、空目录、技能目录、隐藏目录与普通文件从不触发询问', async () => {
  const repo = makeRepo();
  for (const d of ['manager', 'machines', 'testdir']) {
    mkdirSync(join(repo, d), { recursive: true });
    writeFileSync(join(repo, d, 'x.txt'), 'x');
  }
  makeSkill(repo, 'presets/foo/bar'); // presets 自身豁免（里面的预设照常工作）
  mkdirSync(join(repo, 'empty')); // 空目录不询问
  makeSkill(repo, 'real'); // 顶层技能不询问
  mkdirSync(join(repo, '.hidden'), { recursive: true });
  writeFileSync(join(repo, '.hidden/x'), 'x');
  writeFileSync(join(repo, 'notes.txt'), 'x');
  const lines = await promptUnknownTopDirs(repo, { tty: true, confirm: never() });
  assert.deepEqual(lines, []);
});

test('非交互（stdin 非 TTY）：不询问、不移动，输出一行提示列出待确认文件夹', async () => {
  const repo = makeRepo();
  makeSkill(repo, 'stuff/alpha');
  makeSkill(repo, 'other/gamma');
  const lines = await promptUnknownTopDirs(repo, { tty: false, confirm: never() });
  assert.equal(lines.length, 1);
  assert.match(lines[0], /stuff/);
  assert.match(lines[0], /other/);
  assert.match(lines[0], /presets/);
  assert.ok(existsSync(join(repo, 'stuff/alpha/SKILL.md')));
  assert.ok(!existsSync(join(repo, 'presets')), '不移动');
  assert.ok(!existsSync(join(repo, PRESET_PROMPT_FILE)), '不写名单');
  // 完全缺省 opts 同样走非交互
  const lines2 = await promptUnknownTopDirs(repo);
  assert.equal(lines2.length, 1);
});

test('同意但 presets/ 下同名预设已存在：提示后留在原地且不记名单（下次启动仍会询问）', async () => {
  const repo = makeRepo();
  makeSkill(repo, 'presets/stuff/old');
  makeSkill(repo, 'stuff/alpha');
  const lines = await promptUnknownTopDirs(repo, { tty: true, confirm: () => true });
  assert.match(lines.join('\n'), /已存在/);
  assert.ok(existsSync(join(repo, 'stuff/alpha/SKILL.md')), '留在原地');
  assert.ok(existsSync(join(repo, 'presets/stuff/old/SKILL.md')), '既有预设不动');
  assert.ok(!existsSync(join(repo, 'presets/stuff/alpha')), '不并入既有预设');
  assert.ok(!existsSync(join(repo, PRESET_PROMPT_FILE)), '重名不是拒绝，不记名单');
});

test('同意但文件夹名不是合法预设名：提示后留在原地', async () => {
  const repo = makeRepo();
  makeSkill(repo, 'my stuff/alpha'); // 带空格，过不了 validateSkillName
  const lines = await promptUnknownTopDirs(repo, { tty: true, confirm: () => true });
  assert.match(lines.join('\n'), /非法/);
  assert.ok(existsSync(join(repo, 'my stuff/alpha/SKILL.md')));
  assert.ok(!existsSync(join(repo, 'presets')));
});

test('cli: 非交互启动（spawnSync 下 stdin 非 TTY）输出提示行且不动仓库', () => {
  const repo = makeRepo();
  makeSkill(repo, 'stuff/alpha');
  const r = spawnSync('node', [CLI, 'link'], { encoding: 'utf8', env: { ...process.env, MYSKILLS_ROOT: repo } });
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /stuff/);
  assert.match(r.stdout, /presets/);
  assert.ok(existsSync(join(repo, 'stuff/alpha/SKILL.md')));
  assert.ok(!existsSync(join(repo, 'presets')));
  assert.ok(!existsSync(join(repo, PRESET_PROMPT_FILE)));
});

test('cli: 没有待确认文件夹时不输出提示', () => {
  const repo = makeRepo();
  makeSkill(repo, 'real');
  const r = spawnSync('node', [CLI, 'link'], { encoding: 'utf8', env: { ...process.env, MYSKILLS_ROOT: repo } });
  assert.equal(r.status, 0, r.stderr);
  assert.doesNotMatch(r.stdout, /待确认/);
});
