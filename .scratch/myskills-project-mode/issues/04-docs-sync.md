# 04 — 文档同步：AGENTS.md 与 myskills-bootstrap 技能

**构建内容：** 仓库 `AGENTS.md`（工具用法、行为约定）与 `myskills-bootstrap/SKILL.md` 反映两个新事实：命令可在任意目录运行（含 `MYSKILLS_ROOT`）；项目级分发工作流（项目根 `.myskills.json` + `myskills init` + 项目内 `myskills link`）。读者按文档能完成一次项目级分发。

**被以下阻塞：** 01、02、03。

## 验收标准

- [ ] AGENTS.md 工具用法含 init 与项目模式说明，不再暗示命令只能在仓库内运行
- [ ] myskills-bootstrap/SKILL.md 的流程描述与新行为一致
- [ ] cli.ts / core.ts 顶部注释与用法字符串包含 init
- [ ] 提交并推送 aliyun

## 被以下阻塞

- 01 — 仓库根定位改为脚本位置
- 02 — 项目模式 `link`
- 03 — `myskills init` 项目脚手架
