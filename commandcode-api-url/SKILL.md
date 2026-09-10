---
name: commandcode-api-url
description: 配置 Command Code 的 API 接入。GOAT/Go 订阅真正走的接口是 https://api.commandcode.ai/alpha/generate，不是官方文档写的 /provider/v1（后者需额外 Provider 订阅，订阅用户调用报 403 upgrade_required）。使用场景：在 pi 或其他 agent 中接入 commandcode 订阅、配置 commandcode provider、遇到 "No API key found for commandcode"、"upgrade_required"、"/provider/v1" 无法调用等问题时。
---
# Command Code API 接入配置

## 关键背景（先读）

Command Code 暴露两个 API 面：

| 接口 | 协议 | 需要的套餐 |
|---|---|---|
| `https://api.commandcode.ai/provider/v1/chat/completions` | OpenAI 兼容 | **Provider 套餐**（$15/月 附加订阅）；GOAT/Go 订阅调用返回 `403 upgrade_required` |
| `https://api.commandcode.ai/alpha/generate` | 自定义 Vercel AI SDK 流式协议 | 标准订阅（GOAT $10 / Go $1）真正使用的口子 |

模型列表可从 `https://api.commandcode.ai/provider/v1/models` 拉取（GET 不要求 Provider 订阅），返回 `{"object":"list","data":[{id,name,context_length}...]}`，模型 id 形如 `deepseek/deepseek-v4-flash`、`zai-org/GLM-5.2`、`claude-sonnet-5`。

## 在 pi 中接入（推荐）

### 1. 安装扩展

```bash
pi install npm:pi-commandcode-provider
```

该扩展上游调用 `/alpha/generate`，自动拉取模型列表并缓存到 `~/.pi/agent/commandcode-models.json`。

### 2. 配置认证

API key 在 `~/.commandcode/auth.json`（Command Code CLI 登录生成）的 `apiKey` 字段：
```json
{ "apiKey": "user_...", "userId": "...", "userName": "..." }
```

写入 `~/.pi/agent/auth.json`，**必须是 oauth 形态**才能被 pi 的 `hasConfiguredAuth` 识别：
```json
{
  "commandcode": {
    "type": "oauth",
    "access": "user_...",
    "refresh": "user_...",
    "expires": 1817535453007
  }
}
```

注意：
- `{"type":"api","key":"..."}` 或 `{"type":"api_key","key":"..."}` 不会被 pi 识别，报 "No API key found for commandcode"
- 兜底：环境变量 `COMMANDCODE_API_KEY=user_...` 一定有效，适合先验证再落盘
- 扩展自身也读 `~/.commandcode/auth.json`（顶层 `apiKey`）和 `~/.pi/agent/auth.json` 的 `commandcode`/`command-code` 条目

### 3. 设置默认 provider

`~/.pi/agent/settings.json`：
```json
{
  "defaultProvider": "commandcode",
  "defaultModel": "deepseek/deepseek-v4-flash"
}
```

### 4. 清理 models.json 冲突

`~/.pi/agent/models.json` 的 `providers` 中**不要**保留指向 `/provider/v1` 的 `command-code` 条目——它会与扩展注册的 `commandcode` provider 冲突。直接删除该条目，其他自定义 provider 保留。

### 5. 验证

```bash
pi -p "hi" --model "commandcode/deepseek/deepseek-v4-flash"
```

返回中文回复即打通。常用模型 id：`deepseek/deepseek-v4-flash`、`zai-org/GLM-5.2`、`MiniMaxAI/MiniMax-M3`、`meta/muse-spark-1.2-contributor`、`moonshotai/Kimi-K3`。

## 在任意 OpenAI 兼容 agent 中接入

用 commandcode-api-proxy 把 `/alpha/generate` 转成 OpenAI 兼容口：

```bash
npx commandcode-api-proxy --api-key user_...
# 本地端点：http://127.0.0.1:8787/v1
```

- 提供 `GET /v1/models`、`POST /v1/chat/completions`、`POST /v1/messages`（Anthropic）
- 客户端 base_url 填 `http://127.0.0.1:8787/v1`，api_key 任意填（proxy 注入真实 key）
- 只监听 127.0.0.1，勿绑 0.0.0.0（会暴露付费 key）

## 直接 curl /alpha/generate

```bash
curl -N https://api.commandcode.ai/alpha/generate \
  -H "Authorization: Bearer user_..." \
  -H "Content-Type: application/json" \
  -H "x-command-code-version: 0.29.0" \
  -H "x-cli-environment: production" \
  -d '{"config":{"workingDir":"/tmp","date":"2026-08-06","environment":"linux-x64","structure":[],"isGitRepo":false,"currentBranch":"","mainBranch":"","gitStatus":"","recentCommits":[]},"memory":null,"taste":null,"skills":null,"params":{"model":"deepseek/deepseek-v4-flash","messages":[{"role":"user","content":"hi"}],"tools":[],"system":"","max_tokens":64000,"temperature":0.3,"stream":true},"threadId":"00000000-0000-0000-0000-000000000000"}'
```

返回 Vercel AI SDK 流式事件：`text-delta`、`reasoning-delta`、`tool-call`、`finish`（含 `totalUsage`）。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| `403 upgrade_required` | 用订阅调 `/provider/v1` | 改用 `/alpha/generate` 或 proxy |
| `No API key found for commandcode` | auth.json 形态不对 | 改 oauth 形态或设环境变量 |
| `Service temporarily unavailable` | 模型临时不可用 | 换模型重试（如 deepseek-v4-flash）|
| 模型上下文显示 128K | 扩展缓存了旧列表 | 删 `~/.pi/agent/commandcode-models.json` 后重载 |
