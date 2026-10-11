# 02 — presets/ 布局核心与启动 reconcile

**构建内容：** 建立预设的文件夹事实模型：`presets/<预设名>/` 下存放技能真身，成员识别递归下探——凡自身不含 SKILL.md 的中间目录继续向下，直到找到含 SKILL.md 的目录即认定为一个成员。每次 CLI/TUI 启动先执行 reconcile：为每个成员在顶层建立（或确认已存在）相对符号链接；顶层链接指向已被删除的成员时清除；顶层真身与预设成员重名时报错拒绝；整个操作幂等。提供带拒绝语义的「技能移入预设」核心操作：真身已归属其他预设时直接报错，不静默搬家。

**运行预算：** `离线`

**被以下阻塞：** 01

**状态：已完成**（omp 实现，jev 评审四问通过，启动回归风险一问 jev 弃权、编排者判定通过）

## 验收标准

- [x] 手工 `mv` 一个顶层技能进 `presets/foo/`，运行任意 CLI 命令后顶层出现指向真身的相对符号链接；重复运行无变化
- [x] 嵌套一层中间目录（`presets/foo/skills/bar/SKILL.md`）也能识别 bar 为成员并在顶层建链
- [x] 删除预设成员后，顶层残留的断链在下次启动时被清除
- [x] 顶层已有同名真身与预设成员冲突时报错，信息说明双方位置
- [x] 真身已在预设 A 时尝试移入预设 B：报错拒绝；移回顶层后可再移入
- [x] 测试使用 fixture 文件系统，覆盖上述全部情形

## 实现记录

- `manager/src/core.ts:856-982` 新增预设文件夹模型段：`PRESETS_DIR`、`PresetMember`、`collectMembers`（递归下探，`isSkillDir` 命中即止）、`listPresets`、`presetMembers`、`reconcilePresets`、`moveSkillToPreset`
- `reconcilePresets` 顺序：成员重名抛错 → 顶层非链接条目冲突抛错（双方原样保留）→ 建相对符号链接（resolve 相等的正确链接跳过，含绝对形式）→ 清除顶层指向仓库内且目标不存在的断链（外部目标链接不动）
- `moveSkillToPreset`：`validateSkillName` 校验两段目录名（拦截路径逃逸）→ 归属检查已归属即抛错 → rename 真身 + 原地留相对链接
- `validateSkillName(name, label?)` 加可选 label，预设名共用同一约束
- 启动接线：`manager/src/cli.ts` try 块首行 reconcile（全部子命令生效），`manager/src/tui.ts` 的 `start()` 入口在定位 root 后 reconcile
- 设计取舍（omp 披露）：跨预设同名成员与顶层真身重名同为抛错——同一不变量（一层顶层无法各建两链），票面只显式写了后者

## 验证凭证

- 测试：`cd manager && npm test` → 107 pass / 0 fail（原 93 + 新 14，编排者复跑确认）。新测试 `manager/test/preset-folders.test.ts`，含幂等证明（readlink 快照 + ctimeMs）与 CLI 接线测试（spawnSync 真实 `cli.ts link`/`status`）
- 真仓冒烟（编排者执行）：无 `presets/` 时 reconcile 为空操作，现存顶层符号链接原样保留
- jev 评审：成员识别 0.92、reconcile 安全幂等 0.91、移入拒绝 0.89、验收覆盖 0.81（均为真）；启动回归风险 0.23 弃权，编排者判定不成立（冲突阻塞是票面要求，reconcile 不碰 manifest 与 agent 目录）。评审请求存档 `.agent-results/t02-review.json`

## 被以下阻塞

- 01
