---
name: baidu-netdisk-mcp
description: 配置百度网盘 MCP（Claude Code）：SSE 远程服务覆盖列表/搜索/分享，stdio 本地 Python SDK 负责上传本地文件。用户要求接入/配置/连接百度网盘 MCP、解决网盘上传、提到 mcp-pan.baidu.com 或 BAIDU_NETDISK_ACCESS_TOKEN 时使用。
---

# 百度网盘 MCP 接入

两个 Server 分工不同，**不能互相替代**：

| Server | 传输 | 能力 |
|---|---|---|
| `baidu-netdisk` | SSE `https://mcp-pan.baidu.com/sse` | 列表、元信息、复制/移动/删除/重命名、搜索、分享、用户信息、容量；**没有本地上传** |
| `baidu-netdisk-upload` | stdio（官方 Python SDK） | 仅 `upload_file`（本地文件上传） |

前提：Access Token、Python ≥ 3.12、uv（用 `command -v uv` 取绝对路径）。

## 1. 获取 Access Token

个人限时体验走隐式授权（无 refresh token，约 30 天过期）；企业走授权码模式，由服务端托管并刷新。入口以官方文档为准：

- 接入总览：https://pan.baidu.com/union/doc/mcp-server/操作指南/正式接入-agent/
- Python SDK（stdio）：https://pan.baidu.com/union/doc/Cm9si7mfw

**Token 只留在用户自己的终端**：不要要求用户贴进对话，也不要把真实 token 写进技能或仓库。

## 2. 安装 stdio SDK

```bash
SDK="$HOME/.local/share/baidu-netdisk-mcp"
[ -d "$SDK/.git" ] || gh repo clone baidu-netdisk/mcp "$SDK" -- --depth 1
cd "$SDK/src/baidu-netdisk" && uv sync
```

完成标准：启动测试输出 `124`（超时杀进程，说明服务已在等待 stdin 且无报错）：

```bash
cd "$SDK/src/baidu-netdisk" && timeout 8 uv run fileupload_tool.py < /dev/null; echo $?
```

## 3. 注册 stdio Server（上传）

```bash
SDK="$HOME/.local/share/baidu-netdisk-mcp"
UV=$(command -v uv)
claude mcp add --scope user baidu-netdisk-upload \
  -e BAIDU_NETDISK_ACCESS_TOKEN='<TOKEN>' \
  -- "$UV" --directory "$SDK/src/baidu-netdisk" run fileupload_tool.py
```

## 4. 注册 SSE Server（其余能力）

```bash
claude mcp add --scope user --transport sse baidu-netdisk \
  https://mcp-pan.baidu.com/sse \
  --header "Authorization: Bearer <TOKEN>"
```

只做上传可跳过；要完整工具集就两个都装。

## 5. 验证

```bash
claude mcp list
```

完成标准：两个 Server 都显示 `✔ Connected`。重启 Claude Code 或 `/mcp` 重连后，让 Agent 执行一次上传：「把 /path/to/file 上传到网盘」，返回 `status: success` 即通过。

## 参考

`upload_file(local_file_path, remote_path?)`

- `remote_path` 是**目录**（以 `/` 开头），工具自动拼上文件名；不传默认 `/来自：mcp_server`。
- ≤4 MB 直传，>4 MB 按 4 MB 分片；失败自动重试 3 次。
- Token 在进程启动时读取一次；换 token 后更新 `-e` 值并重启。
- Token 明文存于 `~/.claude.json`（权限 600）。
- SSE 鉴权 Header 优先；同时用 Query 时只校验 Query，失败不会回退 Header。
- 官方 SDK 文档中的 `netdisk.py`，在 GitHub 仓库里对应 `fileupload_tool.py`。
- 已存在的同名 Server：先 `claude mcp remove <name> --scope user` 再添加。
- 无害警告：`VIRTUAL_ENV ... does not match the project environment`，忽略。
- `uv` 可能来自 nvim mason 目录；清理 mason 后命令路径失效，重新 `command -v uv` 取路径。
- 官方工具清单与参数：https://github.com/baidu-netdisk/mcp
