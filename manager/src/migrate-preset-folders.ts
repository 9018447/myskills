#!/usr/bin/env node
// 票 04：一次性存量迁移——把旧布局仓库收敛到 presets/ 文件夹事实模型：
//   1. skills-manifest.json 里废弃的 presets 字段：成员真身从顶层移入 presets/<预设>/<技能>/
//      （成员名指向不存在目录的剔除并记入报告，不中断）；字段本身清空，presetApplied 原样
//   2. 顶层含子技能的集合目录整体移入 presets/<集合名>/；嵌套集合（子技能在 skills/ 等中间层下）
//      拆除中间层，子技能平铺到第一层；非技能残留（CHANGELOG、docs、点文件等）原地不动
//   3. manager/、machines/、testdir/、点开头条目不动；末尾 reconcilePresets 为所有成员建顶层链接
// 幂等：对已收敛布局重复执行无任何改动。
// 直接执行即迁移真仓并打印报告：node manager/src/migrate-preset-folders.ts（仓库根取 findRepoRoot）
import { existsSync, lstatSync, mkdirSync, readdirSync, readlinkSync, renameSync, rmSync, rmdirSync } from 'node:fs';
import { join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  PRESETS_DIR,
  TOP_DIR_EXEMPTIONS,
  findRepoRoot,
  isSkillDir,
  listPresets,
  moveSkillToPreset,
  presetMembers,
  readJson,
  reconcilePresets,
  saveManifest,
  validateSkillName,
  type Manifest,
} from './core.ts';

export interface RemovedDuplicate {
  preset: string; // 重复真身所在的集合（预设文件夹）名
  name: string; // 技能名
  from: string; // 被剔除副本的原始位置（相对仓库根）
  reason: string;
}

export interface MigratePresetFoldersReport {
  movedMembers: Record<string, string[]>; // JSON 预设 → 移入 presets/ 的成员
  droppedMembers: Record<string, string[]>; // JSON 预设 → 剔除的失效成员（顶层不存在）
  takenMembers: Record<string, Record<string, string>>; // JSON 预设 → 成员 → 已归属的其他预设（旧数据多预设共享成员）
  movedCollections: Record<string, string[]>; // 集合目录 → 平铺后的子技能名
  removedDuplicates: RemovedDuplicate[]; // 与既有真身同名而被剔除的集合内副本
  clearedPresetsField: boolean; // 本次运行是否清空了清单 presets 字段
  memberCounts: Record<string, number>; // 迁移后各预设成员数
  reconcileLines: string[];
}

// 目录下（含嵌套）是否存在技能真身；点开头条目与 collectMembers 同步跳过——
// 只有能成为成员的技能才让目录算作集合
function containsSkill(dir: string): boolean {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const abs = join(dir, entry.name);
    if (isSkillDir(abs)) return true;
    if (entry.isDirectory() && containsSkill(abs)) return true;
  }
  return false;
}

// 把 base 的后代技能目录搬到 base 第一层。中间层只搬技能：残留文件与点开头条目不动，
// 技能搬空后空目录拆除；与既有真身同名的集合副本被剔除（一个名字只留一处真身，否则 reconcile 拒绝）
function hoistInto(repoRoot: string, preset: string, base: string, dir: string, report: MigratePresetFoldersReport): void {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const abs = join(dir, entry.name);
    if (isSkillDir(abs)) {
      const dest = join(base, entry.name);
      if (existsSync(dest)) throw new Error(`平铺目标已存在: ${dest} 与 ${abs}，请手动取舍`);
      // owner 排除自身（此时它还位于原嵌套位置，presetMembers 能看到自己）
      const owner = presetMembers(repoRoot).find((m) => m.name === entry.name && resolve(repoRoot, m.dir) !== resolve(abs));
      if (owner) {
        rmSync(abs, { recursive: true });
        report.removedDuplicates.push({ preset, name: entry.name, from: relative(repoRoot, abs), reason: `与预设 ${owner.preset} 的成员同名` });
        continue;
      }
      const top = join(repoRoot, entry.name);
      let topSt = undefined;
      try {
        topSt = lstatSync(top);
      } catch {
        // 顶层无同名条目
      }
      if (topSt && !topSt.isSymbolicLink()) {
        rmSync(abs, { recursive: true });
        report.removedDuplicates.push({ preset, name: entry.name, from: relative(repoRoot, abs), reason: `与顶层 ${top} 同名` });
        continue;
      }
      renameSync(abs, dest);
      continue;
    }
    if (entry.isDirectory()) hoistInto(repoRoot, preset, base, abs, report);
  }
  try {
    rmdirSync(dir); // 技能搬空、无残留时拆除中间层
  } catch {
    // 仍有残留文件，保留
  }
}

export function migratePresetFolders(repoRoot: string): MigratePresetFoldersReport {
  const report: MigratePresetFoldersReport = {
    movedMembers: {},
    droppedMembers: {},
    takenMembers: {},
    movedCollections: {},
    removedDuplicates: [],
    clearedPresetsField: false,
    memberCounts: {},
    reconcileLines: [],
  };
  const raw = readJson<Manifest & { presets?: Record<string, string[]> }>(join(repoRoot, 'skills-manifest.json'));
  const legacy = raw.presets ?? {};

  // 1. JSON 预设成员落地。顶层已是指向本预设真身的链接（上次运行中断后重跑）则跳过保证幂等
  for (const [preset, members] of Object.entries(legacy)) {
    for (const skill of members) {
      const top = join(repoRoot, skill);
      let st = undefined;
      try {
        st = lstatSync(top);
      } catch {
        // 条目不存在
      }
      if (st?.isSymbolicLink()) {
        const target = resolve(repoRoot, readlinkSync(top));
        if (target === join(repoRoot, PRESETS_DIR, preset, skill)) continue; // 本预设已迁移（中断重跑）
        // 顶层链接指向别的预设真身：多个 JSON 预设共享同一成员，先到先得，后到的从名单剔除
        const parts = relative(repoRoot, target).split(sep);
        if (parts[0] === PRESETS_DIR && parts.length >= 3) {
          (report.takenMembers[preset] ??= {})[skill] = parts[1];
          continue;
        }
      }
      // 成员已在预设文件夹里（用户已手工移入集合目录，或中断重跑）：不剔除不报错
      if (!st && existsSync(join(repoRoot, PRESETS_DIR, preset, skill))) continue;
      if (!st?.isDirectory()) {
        (report.droppedMembers[preset] ??= []).push(skill);
        continue;
      }
      moveSkillToPreset(repoRoot, preset, skill);
      (report.movedMembers[preset] ??= []).push(skill);
    }
  }

  // 2. 顶层集合目录归位：真实目录、非技能、含子技能、不在豁免名单（点开头天然跳过）
  const collections = readdirSync(repoRoot, { withFileTypes: true })
    .filter((e) => !e.name.startsWith('.') && !TOP_DIR_EXEMPTIONS[e.name] && e.isDirectory())
    .map((e) => e.name)
    .filter((name) => !isSkillDir(join(repoRoot, name)) && containsSkill(join(repoRoot, name)));
  for (const name of collections) {
    validateSkillName(name, '预设名');
    const dest = join(repoRoot, PRESETS_DIR, name);
    if (existsSync(dest)) throw new Error(`预设 ${name} 已存在: ${dest}，请手动取舍`);
    mkdirSync(join(repoRoot, PRESETS_DIR), { recursive: true });
    renameSync(join(repoRoot, name), dest);
    for (const entry of readdirSync(dest, { withFileTypes: true })) {
      const abs = join(dest, entry.name);
      if (entry.name.startsWith('.') || isSkillDir(abs) || !entry.isDirectory()) continue; // 第一层技能已平铺；残留不动
      hoistInto(repoRoot, name, dest, abs, report);
    }
  }

  // 3. 清空废弃的 presets 字段（放在文件搬移之后：中断重跑时成员移入仍可幂等续跑）
  if ('presets' in raw) {
    delete raw.presets;
    saveManifest(repoRoot, raw);
    report.clearedPresetsField = true;
  }

  // 4. 末尾 reconcile：为所有预设成员建立（或确认）顶层相对符号链接
  report.reconcileLines = reconcilePresets(repoRoot);

  const members = presetMembers(repoRoot);
  for (const m of members) {
    report.memberCounts[m.preset] = (report.memberCounts[m.preset] ?? 0) + 1;
    if (collections.includes(m.preset)) (report.movedCollections[m.preset] ??= []).push(m.name);
  }
  for (const p of listPresets(repoRoot)) report.memberCounts[p] ??= 0;
  return report;
}

export function formatReport(report: MigratePresetFoldersReport): string[] {
  const lines: string[] = [];
  for (const [preset, skills] of Object.entries(report.movedMembers)) lines.push(`JSON 预设成员移入 presets/${preset}/（${skills.length} 个）: ${skills.join(', ')}`);
  for (const [preset, skills] of Object.entries(report.droppedMembers)) lines.push(`剔除失效成员（顶层不存在） ${preset}: ${skills.join(', ')}`);
  for (const [preset, skills] of Object.entries(report.movedCollections)) lines.push(`集合目录移入 presets/${preset}/（${skills.length} 个技能）: ${skills.join(', ')}`);
  for (const d of report.removedDuplicates) lines.push(`剔除同名重复真身 ${d.preset}/${d.name} ← ${d.from}（${d.reason}）`);
  if (report.clearedPresetsField) lines.push('清单 presets 字段已清空（presetApplied 原样保留）');
  lines.push(...report.reconcileLines);
  const counts = Object.entries(report.memberCounts).map(([p, n]) => `${p}=${n}`);
  lines.push(counts.length ? `各预设成员数: ${counts.join(', ')}` : 'presets/ 下暂无预设');
  if (!lines.some((l) => !l.startsWith('各预设成员数') && !l.startsWith('presets/ 下暂无'))) return ['无可迁移内容（布局已收敛）'];
  return lines;
}

// 直接执行入口：迁移 findRepoRoot() 定位的仓库并打印报告
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    for (const line of formatReport(migratePresetFolders(findRepoRoot()))) console.log(line);
  } catch (err) {
    console.error(`迁移失败: ${(err as Error).message}`);
    process.exitCode = 1;
  }
}
