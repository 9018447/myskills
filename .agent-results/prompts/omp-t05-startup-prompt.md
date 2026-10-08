# 任务：myskills manager 预设集文件夹化 — 票 05（共 6 票）

## 整体目标与当前主要矛盾

把 myskills 仓库的管理工具 manager（/home/smh/myskills/manager/src）的预设集功能从「JSON 字段」改为「文件夹事实模型」：仓库顶层 presets/<预设名>/<技能名>/ 存放技能真身，不在任何预设里的技能真身留在顶层。

已完成：票 01 技能判别统一 `isSkillDir`（manager/src/core.ts:75）；票 02 文件夹模型（manager/src/core.ts:856-982：`listPresets`/`presetMembers`/`reconcilePresets`/`moveSkillToPreset`）并接线启动；票 03 预设管理全部走文件夹、JSON presets 字段废弃（commit c2ffd6f）。

当前主要矛盾：预设化靠「迁移 + 用户手动 mv」两条路，但仓库顶层的未知文件夹（用户随手放的东西、未来的新集合目录）没有任何进入 presets/ 的引导。票 05 加启动交互确认，把这条路补上。

## 本票

Ticket 文件：/home/smh/myskills/.scratch/preset-folders/issues/05-startup-prompt.md —— 先读它。

**行为：** CLI/TUI 启动时（在票 02 接线的 reconcile 之前或一体执行），发现仓库顶层存在「非空 且 不含 SKILL.md（`isSkillDir` 为假）且 不在豁免名单 且 不在已拒绝名单」的文件夹时，逐个交互确认是否移入 presets/ 成为预设文件夹：

- 同意 → 文件夹 `mv` 进 presets/（文件夹名即预设名，需过 `validateSkillName`；重名时提示并留在原地），随后执行 reconcile 让其子技能获得顶层链接
- 拒绝 → 记入持久化拒绝名单，之后启动不再询问该文件夹（名单位置自选：仓库内一个小 JSON 或 manifest 字段均可，要求跨进程持久、可被用户手工编辑清空）
- 豁免名单预置：`manager`、`machines`、`testdir`（预置常量，用户不可在名单外再配置的范围本票不做）
- 非交互环境（stdin 非 TTY，如管道、CI）→ 不询问、不移动，输出一行提示说明发现了哪些待确认文件夹

**与既有事实的衔接：**
- 票 02 的 reconcilePresets 已在 cli.ts try 块首行与 tui.ts start() 执行——确认流程要与之协同：确认/拒绝发生在 reconcile 之前，移动后的文件夹立即被 reconcile 处理
- 真仓现存的 13 个集合目录由票 04 迁移，本票不迁移它们，也不要在真实仓库上执行任何移动——只在 fixture 上实现与测试
- 空目录不询问（保持原样即可）
- prompts 目录名与既有预设重名：提示后留在原地（下次启动还会问，这是预期）

## 验收标准

以票面为准，概括：

- 顶层放置一个新的非空无 SKILL.md 文件夹，启动时出现确认；同意后文件夹位于 presets/ 下且成员获得顶层链接
- 拒绝后写入名单，连续启动不再询问
- manager/、machines/、testdir/ 从不触发询问
- 非交互环境（stdin 非终端）不询问、不移动、输出提示
- 测试覆盖同意、拒绝、豁免、非交互四种分支

## 工作方式（硬约束）

- 用 /tdd 流程完成实现：先写失败测试，再实现到测试绿
- 测试命令：cd /home/smh/myskills/manager && npm test（node:test，fixture 文件系统）。交互测试用可注入的输入/回答函数（不要真的等 stdin），非交互分支用模拟非 TTY 条件
- 遵守 Ticket 范围，不扩大范围、不做无关重构、不过度设计
- 不得使用 /acpx 或 subagent 向下派发
- 不跑 code-review（open-code-review-delegate、ocr、/code-review 一律不执行）——评审由编排者在提交后统一进行
- 不做任何 git 提交（add/commit/push 都不做）——工作区已有的未提交改动与你无关，不要动它们
- 完成后交付：改动文件与关键函数清单、测试结果
