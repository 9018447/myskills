# 任务：myskills manager 预设集文件夹化 — 票 03（共 6 票）

## 整体目标与当前主要矛盾

把 myskills 仓库的管理工具 manager（/home/smh/myskills/manager/src）的预设集功能从「JSON 字段」改为「文件夹事实模型」：仓库顶层 presets/<预设名>/<技能名>/ 存放技能真身，不在任何预设里的技能真身留在顶层，每次启动 reconcile 补顶层符号链接。

已完成地基：票 01 统一技能判别为 `isSkillDir`（manager/src/core.ts:75）；票 02 建立文件夹模型段（manager/src/core.ts:856-982）：`listPresets(repoRoot)`、`presetMembers(repoRoot)`（递归下探识别成员）、`reconcilePresets(repoRoot)`（启动幂等 reconcile）、`moveSkillToPreset(repoRoot, preset, skill)`（归属拒绝语义），并已接线 CLI/TUI 启动。

当前主要矛盾：预设的「管理」和「分发」两条通路还在读写 skills-manifest.json 的 `presets` 字段，与新的文件夹事实脱节——界面上建预设改的是 JSON，而真实成员在文件夹里。票 03 把这两条通路切换到文件夹。

## 本票

Ticket 文件：/home/smh/myskills/.scratch/preset-folders/issues/03-tui-folder-ops.md —— 先读它。

**管理通路（TUI 为主，预设管理目前只有 TUI 的 p 面板）：**
- 新建预设 = 在 presets/ 下建文件夹（mkdir）
- 添加成员 = 顶层技能真身经 `moveSkillToPreset` 移入文件夹
- 移除成员 = 真身移回顶层（reconcile 语义下真身回顶层即可，preset 文件夹里那个成员目录移出）
- 删除预设 = 成员全部移回顶层后删除文件夹
- 界面展示的成员列表一律来自 `presetMembers()`，不再读 JSON

**分发通路（core.ts 的 link）：**
- `link()` 目前用 Set 合并 manifest.presets 的成员（在 link 函数内的 presetSkills 合并段，用符号名定位，行号已漂移）——改为按 `presetMembers()` 现读文件夹，只对 `presetApplied` 里已应用的预设取成员
- `applyPreset` / 取消应用：应用关系（presetApplied）仍在 JSON，语义不变（互斥接管：应用时成员从 agent 个人清单移出、改由预设管）

**JSON 清理：**
- Manifest 类型的 `presets` 字段删除（manager/src/core.ts 的 Manifest 定义，presets?: Record<string,string[]>）；所有读写该字段的代码移除或改走文件夹
- `presetApplied` 字段保留，行为与此前一致
- 旧版烘焙收敛函数 migrateBakedPresets（读 presets 字段的遗留收敛逻辑）随字段一并处理：删除或改为无操作均可，但不得留下会因缺字段而崩溃的路径。真实 manifest 里现存的 presets 数据票 04 才迁移，本票只需保证缺字段/旧字段共存时代码不崩
- TUI 分组浏览（按预设集分组，g 键）的数据源同样切换到文件夹

## 验收标准

以票面为准，概括：

- TUI 内新建预设、加减成员、删除预设，每步操作后 presets/ 下文件夹状态与界面显示一致
- 应用预设到 agent 并 link 后，agent 目录内符号链接齐全且最终解析到真身
- 改动预设成员后再次 link，已应用 agent 的链接随之增减
- skills-manifest.json 不再含 presets 字段；presetApplied 行为与此前一致
- 同名技能试图加入第二个预设时，界面给出拒绝提示（复用 moveSkillToPreset 的报错）

## 工作方式（硬约束）

- 用 /tdd 流程完成实现：先写失败测试，再实现到测试绿
- 测试命令：cd /home/smh/myskills/manager && npm test（node:test，fixture 文件系统）。现有 preset-folders.test.ts 与 preset.test.ts 必须保持或按新事实更新（preset.test.ts 里针对旧 presets 字段的测试改写为文件夹语义，不是删掉了事）
- TUI 交互本身难以自动化，用 core.ts 层函数测试覆盖文件夹操作与 link 合并逻辑；TUI 面板代码以编译通过 + 现有 TUI 测试不回归为准
- 遵守 Ticket 范围，不扩大范围、不做无关重构、不过度设计
- 不得使用 /acpx 或 subagent 向下派发
- 不跑 code-review（open-code-review-delegate、ocr、/code-review 一律不执行）——评审由编排者在提交后统一进行
- 不做任何 git 提交（add/commit/push 都不做）——工作区已有的未提交改动与你无关，不要动它们
- 完成后交付：改动文件与关键函数清单、测试结果
