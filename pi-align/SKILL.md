---
name: pi-align
description: "Align pi agent config across Tailscale hosts. Use when syncing pi settings/skills/models between machines, 发现漂移或让远程主机与本地 pi 配置一致。"
---

# pi-align — 跨 Tailscale 主机对齐 pi 配置

用 pi-backup 扩展的备份机制做安全快照，用 rsync over Tailscale 传输，使两台主机的 pi 配置一致。

## Fact（已确认）

- pi 配置根：`~/.pi/agent/`（本地与对端均为 Linux + 同用户 `smh` + 同 home 路径时可直接镜像）
- pi-backup 扩展：`~/.pi/agent/npm/node_modules/@jamiefutch/pi-backup/`，含 `backup-pi.sh`（外部 .7z 备份到 `~/pi-backups/`）与 `restore-pi.sh`
- 本机是 Omarchy；做系统级操作（诊断 `omarchy debug --no-sudo --print`、改终端配置后 `omarchy restart terminal`）时先读 omarchy skill。pi 配置本身在 `~/.pi`，不在 `~/.config`
- Tailscale：`tailscale status --json` 是唯一的对端来源。MagicDNS 短名可能被本机 hosts 污染（如 `315` 解析成 0.0.1.59）——ssh/rsync 必须用脚本解析出的 Tailscale IP，不要直接用短名
- 对端 `pi` 可能不在非交互 PATH：远端验证用 `bash -lc` 或检查文件本身

## 对齐集（只管 pi 插件与配置，不管 skills）

`settings.json` `auth.json` `models.json` `trust.json` `keybindings.json` + `themes/` + `pi-hermes-memory/{MEMORY.md,USER.md,failures.md}` + `npm/package.json` `npm/package-lock.json`

不管理：`skills/`（归 myskills 体系，per-host 符号链接，永不同步）；永不同步：`sessions/`、`node_modules/`（用 npm manifests + 远端 npm install 代替）、`pi-hermes-memory` 的状态文件（sessions.db、retired-*）、日志与锁文件。

## 流程（按序执行）

1. **发现**：`scripts/pi-align.sh peers` → 列出在线 Linux 对端。目标主机必须让用户选择，不得替用户假定单一主机。
2. **检查**：`scripts/pi-align.sh diff <host>`（只读）→ 展示每文件 SAME/DRIFT/MISSING 与目录差异。
3. **方向确认（停止条件）**：push=本地→远端，pull=远端→本地。方向由用户明确给出；diff 显示双向都有漂移时，必须让用户决定方向或逐文件取舍，不得自行选择。
4. **执行**：`scripts/pi-align.sh push <host>` 或 `pull <host>`。脚本自动：双侧预快照（tar 到 `~/pi-backups/pi-align-*/`）→ rsync（目录 --delete 镜像，单文件覆盖）→ push 时远端 `npm install` → 重跑 diff 验证归零。
5. **验证完成条件**：重跑 `diff` 输出 0 DRIFT；远端 `~/.pi/agent/settings.json` 与本地一致；push 后远端 `npm ls --depth=0` 无 missing。运行中的 pi 会话需重启才加载新配置。

## 权限与安全

- `auth.json` `models.json` 含凭证，仅允许在 tailnet 内传输；备份文件不得发往 tailnet 之外。
- 任何覆盖（push/pull）前脚本必须已完成双侧快照；快照失败即中止。
- `--delete` 仅用于 `skills/` `themes/` `pi-hermes-memory/` 目录镜像；对单文件永不使用。

## 实践检验

若 diff/push 结果与预期不符（如对端路径不同、无 rsync、用户名不同），先记录实际差异再改脚本参数（`PI_ALIGN_REMOTE_USER`、对齐集），不要假设两端同构。
