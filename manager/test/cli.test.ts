import { test } from 'node:test';
import assert from 'node:assert/strict';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { findRepoRoot } from '../src/core.ts';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

test('cli: 无参数且非 TTY 时打印用法（提示 tui 入口），退出码 0', () => {
  const r = spawnSync('node', [CLI], { encoding: 'utf8' });
  assert.equal(r.status, 0);
  assert.match(r.stdout + r.stderr, /link/);
  assert.match(r.stdout + r.stderr, /tui/);
});

test('findRepoRoot: 未设 MYSKILLS_ROOT 时返回脚本所在仓库的真实根，与运行目录无关', () => {
  delete process.env.MYSKILLS_ROOT;
  const expected = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
  const cwd = process.cwd();
  process.chdir('/');
  try {
    assert.equal(findRepoRoot(), join(expected));
  } finally {
    process.chdir(cwd);
  }
});

test('findRepoRoot: MYSKILLS_ROOT 覆盖生效；指向不存在的目录时报错', () => {
  const tmp = mkdtempSync(join(tmpdir(), 'myskills-root-'));
  process.env.MYSKILLS_ROOT = tmp;
  try {
    assert.equal(findRepoRoot(), tmp);
    process.env.MYSKILLS_ROOT = join(tmp, 'nope');
    assert.throws(() => findRepoRoot(), /MYSKILLS_ROOT/);
  } finally {
    delete process.env.MYSKILLS_ROOT;
  }
});
