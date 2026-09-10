import { test } from 'node:test';
import assert from 'node:assert/strict';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const CLI = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'cli.ts');

test('cli: 无参数且非 TTY 时打印用法（提示 tui 入口），退出码 0', () => {
  const r = spawnSync('node', [CLI], { encoding: 'utf8' });
  assert.equal(r.status, 0);
  assert.match(r.stdout + r.stderr, /link/);
  assert.match(r.stdout + r.stderr, /tui/);
});
