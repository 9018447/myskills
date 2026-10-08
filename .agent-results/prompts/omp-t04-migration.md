# 任务：myskills manager 预设集文件夹化 — 票 04（共 6 票，最后的实现票）

## 整体目标与当前主要矛盾

把 myskills 仓库的管理工具 manager（/home/smh/myskills/manager/src）的预设集功能收敛到「文件夹事实模型」：仓库顶层 presets/<预设名>/<技能名>/ 存放技能真身，不在任何预设里的技能真身留在顶层。

已完成：票 01 技能判别统一 `isSkillDir`（manager/src/core.ts:75）；票 02 文件夹模型（manager/src/core.ts:856-982：`listPresets`/`presetMembers`/`reconcilePresets`/`moveSkillToPreset`）；票 03 预设管理走文件夹、JSON presets 字段废弃（读原样带过、写不增不改）；票 05 启动确认（core.ts:1000-1091）。

当前主要矛盾：真实仓库的数据还是旧布局——skills-manifest.json 里躺着 7 个 JSON 预设的成员名单（全部是顶层真身技能），顶层还有约 10 个含子技能的集合目录。票 04 写一次性迁移，把真实仓库收敛到 presets/ 布局。

## 本票

Ticket 文件：/home/smh/myskills/.scratch/preset-folders/issues/04-migration.md —— 先读它。

**迁移内容（对任意仓库根可用，函数收 repoRoot 参数）：**
1. 读 skills-manifest.json 的 `presets` 字段：把每个预设成员的真身从顶层移入 `presets/<预设名>/<技能名>/`；成员名指向不存在目录的（已知一例 `backup_retro-zh`）从名单剔除并记入迁移报告，不报错中断
2. 清空 JSON `presets` 字段；`presetApplied` 键名与值不动（预设名未改）
3. 顶层含子技能的集合目录整体移入 `presets/<集合名>/`；集合目录名即预设名
4. 嵌套集合（已知名例 mattpocock-skills-zh、matlab-skills-catalog，子技能在中间层如 skills/ 下）：拆除中间层，子技能平铺到 `presets/<集合名>/` 第一层；平铺后残留的非技能文件（CHANGELOG、docs、点文件等）留在预设文件夹内不动——成员识别由既有 `presetMembers()` 的递归下探负责，迁移只负责搬平
5. `manager/`、`machines/`、`testdir/`、点开头文件/目录不动
6. 迁移末尾调用既有 `reconcilePresets(repoRoot)`，为所有预设成员建立顶层相对符号链接
7. 幂等：对已迁移布局重复执行，无任何改动

**实现形态：** 迁移逻辑做成可测试的函数（建议 manager/src/migrate-preset-folders.ts 或并入 core.ts，看现有代码组织），返回迁移报告（移动了什么、剔除了什么、各预设成员数）；另给一个可直接 `node manager/src/migrate-preset-folders.ts` 执行真仓迁移的入口（打印报告）。

## 验收标准

以票面为准，概括：

- 迁移在测试 fixture 上完整跑通：JSON 预设成员、平铺嵌套集合、普通集合三类都有覆盖
- 迁移后 JSON `presets` 字段清空；`presetApplied` 键名不变
- `backup_retro-zh` 被剔除且出现在迁移报告中
- link 数量守恒：迁移前后各建一次「agent 目录 → 链接集合」的对照（fixture 上做），迁移后各 agent 链接不少于迁移前
- 嵌套集合平铺后子技能经 reconcile 在顶层获得符号链接；mattpocock-skills-zh 的 CHANGELOG 等残留文件不被识别为成员
- 迁移幂等：重复执行无副作用

## 工作方式（硬约束）

- 用 /tdd 流程完成实现：先写失败测试，再实现到测试绿
- 测试命令：cd /home/smh/myskills/manager && npm test（node:test，fixture 文件系统）
- **在临时副本上做全链路验证，禁止直接动真仓**：把 /home/smh/myskills 复制（或 git worktree/clone）到 /tmp 下一个目录，构造临时 agents.json（agent 目录指向 /tmp 下自建目录），在副本上跑：迁移前 link → 迁移 → reconcile → 迁移后 link → 对比链接集合。副本验证完删除。真仓的最终迁移执行与真 link 由编排者完成，你不要碰 /home/smh/myskills 的任何真实目录与 ~/.claude/skills 等 agent 目录
- 遵守 Ticket 范围，不扩大范围、不做无关重构、不过度设计
- 不得使用 /acpx 或 subagent 向下派发
- 不跑 code-review（open-code-review-delegate、ocr、/code-review 一律不执行）
- 不做任何 git 提交（add/commit/push 都不做）——工作区已有约 408 条未提交改动与你无关，不要动它们
- 完成后交付：改动文件与关键函数清单、fixture 测试结果、副本全链路验证的链接对比结论
