# 02 — 项目模式 `link`：`.myskills.json` 项目级分发

**构建内容：** 在含 `.myskills.json` 的项目内（含任意子目录）运行 `myskills link`，会把清单 `skills` 列出的技能符号链接进项目的 agent skills 目录，并清理指向中心仓库的孤儿/断链（与全局 link 同一"清单即真相"语义，不碰真实目录和指向仓库外的链接）。`targets` 省略时自动探测：取 `agents.json` 中家目录 agent 的 `skillsPath` 去掉 `~/` 作为候选相对路径，项目里存在几个链几个。`--global` 强制全局模式；`sync`/`status`/`install` 保持纯全局语义，TUI 不动。

**被以下阻塞：** 01 — 仓库根定位改为脚本位置。

## 验收标准

- [ ] core.ts：`findProjectRoot` 从 cwd 向上找最近的 `.myskills.json`；`loadProjectManifest` 校验格式（skills/targets 必须是字符串数组，targets 禁止绝对路径与 `..`）
- [ ] core.ts：link 的单目录建链+清理逻辑抽为可复用函数，全局 `link()` 与新的 `linkProject()` 共用
- [ ] 项目内子目录运行 `myskills link` → 链接建到项目 `.claude/skills` 等探测到的目录；孤儿链接与断链被清理；真实目录、外部链接不动
- [ ] 显式 `targets` 优先于自动探测，目录不存在则创建
- [ ] 清单里仓库不存在的技能：警告跳过，退出码 0
- [ ] 项目内运行 `myskills link --global` → 走全局模式；坏格式 `.myskills.json` → 明确报错退出码 1
- [ ] `npm test` 全绿（新增项目模式测试）
- [ ] 提交并推送 aliyun

## 被以下阻塞

- 01 — 仓库根定位改为脚本位置
