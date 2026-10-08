# 04 — 存量迁移：JSON 预设落地 + 集合目录归位

**构建内容：** 一次性迁移把现有仓库收敛到 presets/ 布局：7 个 JSON 预设的成员真身移入 `presets/<预设名>/`（成员均为顶层技能，唯一失效引用 `backup_retro-zh` 剔除并在报告中说明）；含子技能的集合目录原样移入 `presets/<集合名>/`；嵌套集合（mattpocock-skills-zh、matlab-skills-catalog，子技能在中间层下）拆除中间文件夹层，子技能平铺到 `presets/<集合名>/` 第一层；平铺后残留的非技能文件（CHANGELOG、docs、点文件等）留在预设文件夹内，不参与成员识别。`manager/`、`machines/` 等无子技能的基础设施目录不动。迁移后各 agent 已装链接数不减少。与 03 无依赖，可并行。

**运行预算：** `离线`

**被以下阻塞：** 02

## 验收标准

- [x] 迁移在测试 fixture 上完整跑通：预设成员、平铺集合、普通集合三类都有覆盖
- [x] 迁移后 JSON `presets` 字段清空；`presetApplied` 键名不变（预设名未改）
- [x] `backup_retro-zh` 被剔除且出现在迁移报告中
- [x] 迁移后运行 link：各 agent 目录符号链接数量不少于迁移前（校验：迁移前后各跑一次 link 对比）
- [x] 嵌套集合平铺后其子技能在顶层获得符号链接；mattpocock-skills-zh 的 CHANGELOG 等残留文件不被识别为成员
- [x] 迁移幂等：重复执行无副作用

## 实现记录（2026-10-08）

- 实现：`manager/src/migrate-preset-folders.ts`（收 repoRoot 的 `migratePresetFolders` 函数 + node 直跑入口），测试 `manager/test/migrate-preset-folders.test.ts` 8 例。实现 agent omp 完成主体（commit 93ecdbf），编排者补两处修复：`sep` 未导入（migrate-preset-folders.ts:126）、顶层成员已被手工移进预设文件夹时不再误记 droppedMembers。
- 与票面前提的差异：
  - mattpocock-skills-zh 下已无 SKILL.md 子技能（其技能早已并入 orch-skills），迁移正确地将其留作顶层（未强行平铺）；「mattpocock 嵌套平铺」前提对当前仓库状态失效。
  - 用户在迁移前手工新建顶层 `gitnexus/` 集合目录（10 个 gitnexus-* 技能，含 4 个新技能 gitnexus-lfg/plan/review/work），gitnexus 归位后 10 成员全部识别。
  - manifest 的 presets.orch-skills 名单仍含 6 个 gitnexus-*（用户加 gitnexus 预设时未从 orch-skills 移除）；这些条目因顶层真身已不在而进剔除报告，最终状态正确（gitnexus 预设 10 成员由文件夹实况决定）。
- 真仓迁移结果：15 个预设文件夹（orch-skills 47、gitnexus 10、matlab-skills-catalog 111、matlab 11、github 5、knowledge 2、academic 1 + 9 个集合目录预设）；幂等重跑输出「布局已收敛」；link 后 7 个 agent 目录零断链（claude 64 条链接，6 个非 claude agent 各 10-14 条）。
- 额外数据修复（超出票面范围，已披露）：各 agent 个人清单剔除早已删除的 backup_retro-zh 残留条目（该条目使 link 保留/重建 6 条断链，剔除后重跑 link 断链清零）。
- 验证：干净副本（/tmp/mig-verify）全链路先行验证通过后再在真仓执行；副本内 7 agent 链接全解析、幂等重跑无操作。
- 提交：代码 93ecdbf，数据迁移 c510c9a（993 重命名 + 291 新增 + manifest）。

## 被以下阻塞

- 02
