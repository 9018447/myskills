# 任务：myskills manager 预设集文件夹化 — 票 02（共 6 票）

## 整体目标与当前主要矛盾

把 myskills 仓库的管理工具 manager（/home/smh/myskills/manager/src）的预设集功能从「JSON 字段」改为「文件夹事实模型」：仓库顶层新增 presets/ 根，presets/<预设名>/<技能名>/ 存放技能真身，不在任何预设里的技能真身留在顶层。

票 01（已完成，commit 76a864b）已把技能判别统一为 `isSkillDir(dir)`（manager/src/core.ts:75，导出函数，statSync 跟随符号链接 + 含 SKILL.md 判定）。当前主要矛盾是：判别函数有了，但 presets/ 布局本身还不存在——预设与文件夹之间没有任何对应关系。票 02 建立这个核心模型；票 03/04/05（TUI 操作、存量迁移、启动确认）全部压在它上面。

## 本票

Ticket 文件：/home/smh/myskills/.scratch/preset-folders/issues/02-preset-layout-core.md —— 先读它。三块内容：

1. **成员识别**：`presets/<预设名>/` 下的成员识别递归下探——目录自身含 SKILL.md 即为一个成员；不含则继续向下递归，直到找到含 SKILL.md 的目录。预设文件夹内可以存在残留的非技能文件（CHANGELOG、docs 等），它们不参与成员识别。
2. **启动 reconcile**：每次 CLI/TUI 启动先执行，幂等：
   - 为每个预设成员在仓库顶层建立（或确认已存在）**相对**符号链接，指向真身；
   - 顶层残留的断链（readlink 后目标不存在）清除——现有孤儿断链清理逻辑在 core.ts:180-187 一带，可以复用或扩展；
   - 顶层真身目录与预设成员重名时：报错拒绝（不覆盖、不删除任何一方），错误信息说明双方位置；
   - 顶层已有的指向仓库内技能目录的正确链接不重复创建。
3. **「技能移入预设」核心操作**（core.ts 层函数，TUI 接线在票 03）：把顶层技能真身 `git`-free 地 `mv` 进 `presets/<预设名>/` 并在原地留符号链接（reconcile 也会补）；真身已归属其他预设时**直接报错拒绝**，不自动搬家，错误信息说明当前归属。移回顶层后再移入新预设是允许的。

本票不接线 TUI/CLI 的预设管理界面（票 03）、不做存量数据迁移（票 04）、不做启动交互确认（票 05）、不动 skills-manifest.json 的 presets 字段读写逻辑（字段废弃在票 03）——但 reconcile 和移入操作要保证仓库在任何时刻一致。

## 验收标准

以票面为准，概括：

- 手工 `mv` 一个顶层技能进 `presets/foo/`，运行任意 CLI 命令后顶层出现指向真身的相对符号链接；重复运行无变化
- 嵌套一层中间目录（`presets/foo/skills/bar/SKILL.md`）也能识别 bar 为成员并在顶层建链
- 删除预设成员后，顶层残留的断链在下次启动时被清除
- 顶层已有同名真身与预设成员冲突时报错，信息说明双方位置
- 真身已在预设 A 时尝试移入预设 B：报错拒绝；移回顶层后可再移入
- 测试使用 fixture 文件系统，覆盖上述全部情形

## 工作方式（硬约束）

- 用 /tdd 流程完成实现：先写失败测试，再实现到测试绿
- 测试命令：cd /home/smh/myskills/manager && npm test（node:test，fixture 文件系统）
- 遵守 Ticket 范围，不扩大范围、不做无关重构、不过度设计
- 不得使用 /acpx 或 subagent 向下派发
- 不跑 code-review（open-code-review-delegate、ocr、/code-review 一律不执行）——评审由编排者在提交后统一进行
- 不做任何 git 提交（add/commit/push 都不做）——工作区已有的未提交改动与你无关，不要动它们
- 完成后交付：改动文件与关键函数清单、测试结果
