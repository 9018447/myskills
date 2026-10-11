---
name: cc-connect-setup
description: 安装并配置 cc-connect（本地 Claude Code ←→ 微信/飞书等消息平台桥接），含微信扫码登录、systemd 常驻。用户要求安装/配置 cc-connect 或"微信里用 Claude Code"时使用。
---

# cc-connect 安装配置

桥接本地 AI agent 与消息平台。上游文档：https://github.com/chenhg5/cc-connect（INSTALL.md 可 curl 获取，版本可能演进，冲突时以 `cc-connect <cmd> --help` 与实测为准）。

## Fact（本机已验证，2026-09-21，v1.5.0）

- npm 全局安装即可：`npm install -g cc-connect`。
- 配置文件 `~/.cc-connect/config.toml`，最小结构：

  ```toml
  [log]
  level = "info"

  [[projects]]
  name = "<项目名>"

  [projects.agent]
  type = "claudecode"

  [projects.agent.options]
  work_dir = "<绝对路径>"
  mode = "yolo"   # default | acceptEdits | plan | yolo
  ```

- 微信（个人，ilink）平台：`cc-connect weixin setup --project <名> --config ~/.cc-connect/config.toml` 会打印二维码 + URL，扫码成功后自动把 token 写进 config.toml。已有 token 用 `cc-connect weixin bind --project <名> --token '<token>'`。
- 在 Claude Code 会话内启动 cc-connect 前**必须** `unset CLAUDECODE`，否则子进程 Claude Code 拒绝启动。
- 常驻：`cc-connect daemon install --config ~/.cc-connect/config.toml`（systemd 用户服务），然后 `daemon start`。`cc-connect web` 只配置不开服务。

## Invariant

- 扫码必须由用户完成。生成二维码后把 URL 给用户并停下等待，不得代替扫码，不得在无用户交互的情况下无限重试刷码。
- 改 config.toml 后必须 `cc-connect daemon restart` 才生效（或前台进程重启）。
- 每步改动的验证以命令实际输出为准（版本号、daemon status=Running、日志出现 "cc-connect is running"），不以"应该成功了"为准。

## 流程（按执行顺序）

### 1. 前置确认

- `which cc-connect claude npm` — 已装则跳过安装；npm 缺失先装 node。
- 向用户确认三件事（AskUserQuestion）：消息平台（微信/飞书/Telegram/钉钉…）、agent（默认 claudecode）、work_dir。
- 一个 project 只能绑一个 work_dir；多目录 = 多 project，但同一微信账号挂多个 project 可能抢消息——默认先建一个主项目。

### 2. 安装 + 写配置

1. `npm install -g cc-connect && cc-connect --version` — 有版本号即完成。
2. 按 Fact 中模板写 `~/.cc-connect/config.toml`（Write 工具；目录 `mkdir -p ~/.cc-connect`）。
3. 完成条件：`cc-connect --version` 成功且 config 文件存在、内容与用户选择一致。

### 3. 平台接入（微信为例）

1. 后台运行 setup 并把输出重定向到文件：

   ```bash
   cc-connect weixin setup --project <名> --config ~/.cc-connect/config.toml > /tmp/cc-weixin-setup.log 2>&1 &
   ```

   **坑：不要用管道接 `tail`/`grep` 再输出**——管道会缓冲，二维码出不来。重定向到文件后轮询读文件。
2. 从日志提取 `URL: https://liteapp.weixin.qq.com/q/...` 给用户，要求立即扫码。二维码有效期短，setup 内部自动刷新 3 次，全过期则报"二维码多次过期"退出。
3. 完成条件：日志出现 `✅ Weixin (ilink) configured`，且 config.toml 出现 `[projects.platforms]` + token。失败（多次过期）→ 告知用户后重新生成，一轮失败即停、等用户就绪再刷，不要连续空转刷码。

### 4. 启动 + 消息绑定

1. `unset CLAUDECODE` 后前台试跑：日志应出现 `cc-connect is running` 与 `platform started`。
2. 让用户在微信里给 bot 发一条消息——日志应出现 `message received`，随后 `session spawned`。这一步缓存 context_token，必须在**重启服务之前**完成一次。
3. 完成条件：日志中有 message received 且无 error 级输出。

### 5. 常驻

1. 先停前台进程（占实例锁，不停则 daemon start 失败），再 `cc-connect daemon install --config ~/.cc-connect/config.toml && cc-connect daemon start`。
2. `cc-connect daemon status` 显示 Running 即完成。日志路径 `~/.cc-connect/logs/cc-connect.log`。
3. 停机常驻需用户自己跑（要 sudo 密码）：`sudo loginctl enable-linger $USER`。
4. 重启会打断进行中的微信会话；重启后让用户再发一条消息验证恢复。

## 权限与停止条件

- 允许：安装 npm 包、写 `~/.cc-connect/` 下配置、启停 cc-connect 服务。
- 禁止：代替用户扫码；把 token 打进聊天记录之外的地方（token 已在 config 里，日志文件可留）。
- 停止并问用户：平台凭据/项目路径缺失；扫码连续失败；daemon start 报实例锁被占（先确认旧进程归属再杀）。
- mode 选择（default/acceptEdits/yolo）是用户决策——yolo 等于给 agent 完全操作权，默认问一次。
