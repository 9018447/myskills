# 03 — TUI/CLI 预设操作改走文件夹，JSON presets 字段废弃

**构建内容：** TUI 与 CLI 的预设管理从改 JSON 数组改为操作文件夹：新建预设 = 在 `presets/` 下建文件夹；添加成员 = 把顶层技能真身移入文件夹；移除成员 = 真身移回顶层；删除预设 = 成员全部移回顶层后删除文件夹。`skills-manifest.json` 中的 `presets` 字段删除，成员列表一律读文件夹；`presetApplied`（应用关系）保留在 JSON。整条「管理预设 → 应用到 agent → link 分发」通路端到端生效。

**运行预算：** `离线`

**被以下阻塞：** 02

**状态：已完成**（omp 实现，jev 评审五问通过）

## 验收标准

- [x] TUI 内新建预设、加减成员、删除预设，每步操作后 `presets/` 下文件夹状态与界面显示一致
- [x] 应用预设到 agent 并 link 后，agent 目录内符号链接齐全且指向顶层链接最终解析到真身
- [x] 改动预设成员后再次 link，已应用 agent 的链接随之增减
- [x] `skills-manifest.json` 不再含 `presets` 字段；`presetApplied` 行为与此前一致
- [x] 同名技能试图加入第二个预设时，界面给出拒绝提示（复用 02 的报错）

## 实现记录

- `manager/src/core.ts` 预设管理段重写（core.ts:774-842）：`createPreset`（mkdir，重名/非法名拒绝）、`setPreset`（diff 同步成员：新增移入、去掉移回顶层；`assertSkillMovable` 整体预检，任一失败完全不动）、`deletePreset`（成员全部移回顶层 → 删文件夹含残留 → 清 `presetApplied`）、`applyPreset`（存在性按 `listPresets`、成员按 `presetMembers`，互斥接管语义不变）；新增 `assertSkillMovable`（从 `moveSkillToPreset` 抽出）与 `moveSkillToTop`
- 分发通路：`link()` 预设合并段改为 `presetMembers()` 现读构建 `membersByPreset`（manager/src/core.ts:205-222），只对 `presetApplied` 已应用预设取成员，指向已删文件夹的记录按空成员处理
- `Manifest` 类型删除 `presets` 字段（rg 零匹配），`presetApplied` 保留（manager/src/core.ts:24）；旧字段数据读时原样带过、写时不增不改（票 04 迁移）
- `migrateBakedPresets` 与 `MigratePresetsReport` 删除；`manager/src/cli.ts` 删除 `--presets` 分支，`myskills migrate --presets` 落入常规 migrate 路径不崩。AGENTS.md 中 `migrate --presets` 文档行已失效，票 06 处理
- `manager/src/tui.ts`：分组浏览（g 键预设组）与 PresetsView 数据源全改文件夹；n 建文件夹、保存/删除包 try/catch，失败留在编辑页给拒绝提示

## 验证凭证

- 测试：`cd manager && npm test` → 112 pass / 0 fail（编排者复跑确认）。preset.test.ts 15 个改写为文件夹语义（含 link 传播 realpathSync 解析到真身、旧 presetApplied 指向缺失文件夹不崩）；tui.test.ts 新增 3 个（新建+勾选落盘/重名拒绝、删除预设真身回顶层、跨预设加成员被拒）
- 旧字段共存冒烟：manifest 带遗留 presets 数据 + 无 presets/ 文件夹时 link/applyPreset/deletePreset 均不崩
- jev 评审：管理通路 0.95、link 合并 0.93、原子性 0.84、旧数据共存 0.88、验收覆盖 0.88（均为真）。评审请求存档 `.agent-results/t03-review.json`
- 过渡期约束：票 04 迁移落地前不得对真仓跑 `link`——presetApplied 指向的预设尚无文件夹，其成员链接会被按空成员移除。编排者已将真仓 link 推迟到票 04 完成后

## 被以下阻塞

- 02
