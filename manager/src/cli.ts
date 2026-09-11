#!/usr/bin/env node
// myskills 管理 CLI：link / status / sync / install / init / migrate（薄封装，逻辑在 core.ts）
// link 在含 .myskills.json 的目录下自动切项目模式，--global 强制全局
import { hostname } from 'node:os';
import { findRepoRoot, findProjectRoot, link, linkProject, initProject, status, sync, install, migrate } from './core.ts';

function resolveRemote(): string {
  const idx = process.argv.indexOf('--remote');
  return idx > -1 ? process.argv[idx + 1] : (process.env.MYSKILLS_REMOTE ?? 'aliyun');
}

const command = process.argv[2];

async function launchTui(): Promise<void> {
  if (!process.stdout.isTTY) {
    console.log('用法: myskills [link|status|sync|install|init|migrate|tui]（直接敲 myskills 进 TUI）');
    return;
  }
  const { start } = await import('./tui.ts');
  start(resolveRemote());
}

try {
  switch (command) {
    case 'tui':
      await launchTui();
      break;
    case 'link': {
      const repoRoot = findRepoRoot();
      const project = process.argv.includes('--global') ? null : findProjectRoot();
      if (project) {
        console.log(`项目模式：${project.root}`);
        for (const line of linkProject(project.root, repoRoot).lines) console.log(line);
      } else {
        for (const line of link(repoRoot).lines) console.log(line);
      }
      break;
    }
    case 'init': {
      const repoRoot = findRepoRoot();
      const skillsArg = process.argv.indexOf('--skills');
      const skills = skillsArg > -1 ? (process.argv[skillsArg + 1] ?? '').split(',').map((s) => s.trim()) : [];
      for (const line of initProject(process.cwd(), repoRoot, skills)) console.log(line);
      break;
    }
    case 'status':
      status(findRepoRoot());
      console.log(`已写入 machines/${hostname()}.json`);
      break;
    case 'sync':
      for (const line of sync(findRepoRoot(), resolveRemote())) console.log(line);
      break;
    case 'install': {
      const url = process.argv[3];
      if (!url) throw new Error('用法: myskills install <github-url> [--name <n>] [--remote <r>]');
      const nameIdx = process.argv.indexOf('--name');
      console.log(install(findRepoRoot(), url, nameIdx > -1 ? process.argv[nameIdx + 1] : undefined, resolveRemote()));
      break;
    }
    case 'migrate':
      for (const line of migrate(findRepoRoot(), process.argv.includes('--apply')).lines) console.log(line);
      break;
    case undefined:
      await launchTui();
      break;
    default:
      console.error('用法: myskills [link|status|sync|install|init|migrate|tui]（直接敲 myskills 进 TUI）');
      process.exit(1);
  }
} catch (err) {
  console.error((err as Error).message);
  process.exit(1);
}
