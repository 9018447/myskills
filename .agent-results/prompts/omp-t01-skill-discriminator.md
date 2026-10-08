# 任务：myskills manager 预设集文件夹化 — 票 01（共 6 票）

## 整体目标与当前主要矛盾

把 myskills 仓库的管理工具 manager（/home/smh/myskills/manager/src）的预设集功能从「JSON 字段」改为「文件夹事实模型」：仓库顶层新增 presets/ 根，presets/<预设名>/<技能名>/ 存放技能真身，不在任何预设里的技能真身留在顶层；成员识别走文件夹、启动时 reconcile 补符号链接。

当前主要矛盾是一切后续改造的地基：「什么是一个技能」的判别标准不统一。技能的判别标准定为「目录内含 SKILL.md」，但代码里各处的技能判定分散且不一致，导致顶层无 SKILL.md 的集合目录（data-processing/、molecular-* 等）被当成技能列出。票 01 负责把这个地基打平；票 02–05（presets/ 布局、TUI 操作、存量迁移、启动确认）全部压在它上面，所以本票只做判别统一，不碰 presets/。

## 本票

Ticket 文件：/home/smh/myskills/.scratch/preset-folders/issues/01-skill-discriminator.md —— 先读它。内容：把技能判别统一为「目录内含 SKILL.md」。顶层技能枚举（TUI 列表、CLI 各处）、安装落位检查、应用预设时的存在性校验，全部改用同一个判别函数；没有 SKILL.md 的顶层目录从技能列表中消失。

生产代码在 manager/src/：core.ts（37.7K，核心逻辑）、tui.ts（34.1K）、cli.ts（3.3K）。本票不引入 presets/ 布局、不动 skills-manifest.json 的 presets/presetApplied 字段——那是后续票的范围。

## 验收标准

- 顶层枚举结果 = 含 SKILL.md 的顶层目录；集合目录（agent-workflow、atomistic-workflows、data-processing、machine-learning-potentials、matlab-skills-catalog、mattpocock-skills-zh、molecular-conformer、molecular-dynamics、molecular-representation、tools）与 manager/、machines/、testdir/ 不再出现在技能列表
- 技能存在性校验（应用预设时）与枚举使用同一判别函数
- 测试覆盖三种情形：目录含 SKILL.md、目录不含 SKILL.md、符号链接指向含 SKILL.md 的目录

## 背景事实

仓库顶层当前有 13 个无 SKILL.md 的目录，它们从技能列表消失是预期行为，不是回归。注意符号链接判别时的 lstat/stat 语义：符号链接本身不是技能，但它指向的目录若含 SKILL.md，应按该链接解析后的目标判定（测试要覆盖这一点）。

## 工作方式（硬约束）

- 用 /tdd 流程完成实现：先写失败测试，再实现到测试绿
- 测试命令：cd /home/smh/myskills/manager && npm test（node:test，fixture 文件系统）
- 遵守 Ticket 范围，不扩大范围、不做无关重构、不过度设计
- 不得使用 /acpx 或 subagent 向下派发
- 不跑 code-review（open-code-review-delegate、ocr、/code-review 一律不执行）——评审由编排者在提交后统一进行
- 不做任何 git 提交（add/commit/push 都不做）——工作区已有的未提交改动与你无关，不要动它们
- 完成后交付：改动文件与关键函数清单、测试结果
