# 01 — 仓库根定位改为脚本位置

**构建内容：** 在任意目录下运行 `myskills link`/`status`/`sync`/`install`/`migrate`/TUI 都作用于中心仓库，不再依赖 cwd。定位优先级：`MYSKILLS_ROOT` 环境变量 → 命令脚本自身真实位置上溯到仓库根。彻底移除 cwd 向上查找，消除"在另一个含 `skills-manifest.json` 的目录下静默操作错仓库"的风险。

**被以下阻塞：** 无——可立即开始。

## 验收标准

- [ ] `findRepoRoot()` 不再接受 start 参数，改为：env `MYSKILLS_ROOT` 优先（目录不存在则报错），否则由模块真实路径解析出仓库根
- [ ] cli.ts 与 tui.ts 全部调用点改用新签名；用法提示不变
- [ ] 在仓库外的任意目录（如 /tmp）运行 `myskills link`，配合 `MYSKILLS_ROOT` 指向 fixture 仓库，行为与在仓库内运行一致
- [ ] 直接导入 `findRepoRoot()` 单测：env 覆盖生效；未设 env 时返回脚本所在仓库的真实根
- [ ] 既有 CLI 测试全部改用 `MYSKILLS_ROOT` 注入 fixture 仓库根，`npm test` 全绿
- [ ] 提交并推送 aliyun

## 被以下阻塞

- 无——可立即开始
