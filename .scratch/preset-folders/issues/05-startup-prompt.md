# 05 — 启动交互确认未知的顶层无 SKILL.md 文件夹

**构建内容：** CLI/TUI 启动时发现顶层存在非空且不含 SKILL.md、也不在豁免名单里的文件夹时，交互式确认是否移入 `presets/` 下成为预设文件夹；同意则移动并完成 reconcile，拒绝则记入持久化拒绝名单，之后不再询问。`manager/`、`machines/`、`testdir/` 预置在默认豁免名单。非交互环境（管道、CI）跳过询问并提示，不做任何移动。

**运行预算：** `离线`

**被以下阻塞：** 02

**状态：已完成**（omp 实现，jev 后端区域封锁不可达，编排者直读代码自判通过）

## 验收标准

- [x] 顶层放置一个新的非空无 SKILL.md 文件夹，启动时出现确认；同意后文件夹位于 `presets/` 下且成员获得顶层链接
- [x] 拒绝后写入名单，连续启动不再询问
- [x] manager/、machines/、testdir/ 从不触发询问
- [x] 非交互环境（stdin 非终端）不询问、不移动、输出提示
- [x] 测试覆盖同意、拒绝、豁免、非交互四种分支

## 实现记录

- `manager/src/core.ts:1000-1091` 启动确认段：`TOP_DIR_EXEMPTIONS = { manager, machines, testdir, presets }`（presets 自身豁免）；`PRESET_PROMPT_FILE = '.preset-prompt.json'`（仓库根 `{dismissed:[...]}`，损坏按空处理不拦截询问，删条目可重新询问）；`listPromptableTopDirs`（非点开头、真实目录、非豁免/已拒绝、无 SKILL.md、非空、排序）；`promptUnknownTopDirs(repoRoot, {tty, confirm})`——同意：`validateSkillName` → `existsSync` 重名检查 → `renameSync` 移入 `presets/<名>/`，重名/非法名提示留原地不记名单下次仍问；拒绝：记名单写盘；非交互（`tty !== true` 或无 confirm）返回一行提示列出候选不移动；`confirmOnTty`（readline，y/yes 同意，空回车拒绝）
- 接线：`manager/src/cli.ts:27` 与 `manager/src/tui.ts:815` 均 `promptUnknownTopDirs(tty: process.stdin.isTTY === true)` → 打印报告行 → `reconcilePresets`，确认严格先于 reconcile，移入后立即建链；`tui start()` 改 async
- 交互用注入 confirm 测试（真实 TTY 端到端需 pty，未模拟；CLI 非交互分支经 spawnSync 真实走通）

## 验证凭证

- 测试：`cd manager && npm test` → 120 pass / 0 fail（编排者复跑确认）。新 `manager/test/startup-prompt.test.ts` 8 例覆盖同意（移入+reconcile 建链+不写名单）、拒绝（写名单二次不再问+手工清空重问）、豁免/隐藏/文件/空目录、非交互、重名/非法名留原地、CLI 非交互接线、无候选无输出
- 编排者直读 core.ts:1000-1091 全段核对四分支与安全路径（符号链接经 Dirent.isDirectory 天然排除，rename 前有存在性检查）
- jev 后端 OpenRouter 403 区域封锁，评审由编排者自行判定通过（证据齐备），请求存档 `.agent-results/t05-review.json`
- 已知行为面：真仓 13 个集合目录在票 04 迁移前每次交互启动都会被询问，迁移后消失；AGENTS.md 文档归票 06

## 被以下阻塞

- 02
