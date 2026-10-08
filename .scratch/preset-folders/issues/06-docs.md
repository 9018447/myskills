# 06 — 文档与分发约定更新

**构建内容：** 把「集合目录即预设文件夹」的新事实写进仓库约定：AGENTS.md 目录布局一节（集合目录并入 presets/ 说明）、行为约定第 4 条改写（集合子技能经预设应用分发，不再是「不参与分发」）、skills-manifest.json 字段说明（presets 字段废弃、presetApplied 含义不变）。核对新机器 bootstrap 流程（clone → npm link → sync）在新布局下不变。

**运行预算：** `离线`

**被以下阻塞：** 03、04

## 验收标准

- [x] AGENTS.md 目录布局与第 4 条按新事实改写，无残留旧口径（「集合子技能不参与分发」）
- [x] 文档描述与实际行为一致：枚举规则、reconcile 时机、同名拒绝、豁免名单
- [x] bootstrap 流程小节核对后在文档中确认有效（或同步修正）

## 实现记录（2026-10-08）

主 agent 直接完成（文档任务不派发）。AGENTS.md 改写：目录布局一节新增 `presets/<预设名>/<技能名>/` 布局、SKILL.md 统一判别、递归成员识别、启动 reconcile 与交互确认（`.preset-prompt.json` 持久化名单、豁免 manager/machines/testdir/presets、同名归属拒绝报错）；行为约定第 4 条改写为「集合/预设子技能真身放 presets/ 经预设应用分发」；skills-manifest.json 字段说明删除 presets 字段（成员 readdir 现读），presetApplied 含义不变；工具用法删除 `migrate --presets` 行（CLI 分支已随 t03 移除），补充 TUI 预设操作与 `node manager/src/migrate-preset-folders.ts` 迁移入口；bootstrap 小节核对后确认有效，补一句说明新布局对流程透明。rg 核对无残留旧口径（不参与分发/JSON presets 字段/migrate --presets/烘焙 零匹配）；npm test 128/128。

## 被以下阻塞

- 03、04
