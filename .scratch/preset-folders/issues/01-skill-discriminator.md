# 01 — 技能判别统一为 SKILL.md 规则

**构建内容：** 技能的判别标准从「顶层目录名」统一为「目录内含 SKILL.md」。顶层技能枚举（TUI 列表、CLI 各处）、安装落位检查、应用预设时的存在性校验全部改用同一判别；没有 SKILL.md 的顶层目录（集合目录、基础设施目录）从技能列表中消失。这是后续所有预设文件夹改造的地基。

**运行预算：** `离线`

**状态：已完成**（omp 实现，jev 评审四问通过）

## 验收标准

- [x] 顶层枚举结果 = 含 SKILL.md 的顶层目录；集合目录（data-processing、molecular-* 等）与 manager/、machines/ 不再出现在技能列表
- [x] 技能存在性校验（应用预设时）与枚举使用同一判别函数
- [x] 测试覆盖：含 SKILL.md / 不含 / 符号链接指向含 SKILL.md 目录三种情形

## 实现记录

- `manager/src/core.ts:75` 新增导出 `isSkillDir(dir)`：`statSync`（跟随符号链接）确认是目录且目录内含 `SKILL.md`，异常返回 `false`。断链、普通文件、不可访问路径都不是技能
- `listRepoSkills`（`manager/src/core.ts:85`）改用 `isSkillDir`，顶层符号链接按解析目标判定
- `install`（`manager/src/core.ts:549`）tarball 源检查、`applyPreset`（`manager/src/core.ts:794`）成员存在性校验均收敛到 `isSkillDir`
- 范围内未动 `migrate` 里对 agent 目录实体的 SKILL.md 检查（`manager/src/core.ts:642`、`manager/src/core.ts:666`）：那是 agent skills 目录里的实体判别，不是仓库顶层枚举，且对普通目录行为与 `isSkillDir` 等价

## 验证凭证

- 测试：`cd manager && npm test` → 93 pass / 0 fail（编排者复跑确认）。新增 3 个测试：列表只含含 SKILL.md 的目录、符号链接三态（指向技能目录 / 指向非技能目录 / 断链）、预设成员无 SKILL.md 计入 `missing`
- 真实仓库冒烟：枚举 268 个技能，13 个集合目录与 `manager/`、`machines/`、`testdir/` 零泄漏
- jev 评审：判别统一 0.89、符号链接语义 0.97、验收覆盖 0.90（均为真），回归风险 0.15（自信为假）。评审请求存档 `.agent-results/t01-review.json`
