---
name: claude-code-provider
description: 配置 Claude Code 连接各种 Anthropic 兼容提供商（智谱 Z.AI、DeepSeek、Kimi/Moonshot、通义千问、SiliconFlow 等），写入 ~/.claude/settings.json 的 env 字段并跳过首次引导。使用场景：用户说"把 Claude Code 接到 XX"、"配置 claude code 用 XX 的模型"、"切换 claude code 的 API 提供商"、输入 API key 后 claude 报认证错误、需要设置 ANTHROPIC_BASE_URL 时。
argument-hint: "[提供商名] [API key]"
---

# Claude Code 提供商配置

把 Claude Code 指向任意 Anthropic 兼容 API。预设常见国产提供商，也支持任意自定义 base_url。

## 工作流

1. **确定提供商**：用户可能指名（"Z.AI"、"DeepSeek"、"Kimi"等），也可能只给了 base_url。查 `references/providers.md` 找预设表；没有就按自定义处理。
2. **拿 API key**：从用户处获取；key 已存在于 `~/.claude/settings.json` 且用户未要求更换则复用。
3. **写配置**：编辑 `~/.claude/settings.json`（不存在则创建），设置 env 字段（见下）。
4. **跳过引导**：确保 `~/.claude.json` 有 `"hasCompletedOnboarding": true`，否则首次运行会卡在引导界面。
5. **验证**：运行 `claude --version` 确认安装，提示用户 `claude` 后发一句测试消息。

## 配置写入规则

`~/.claude/settings.json` 是 JSON，**合并写入**——保留已有字段，只改 `env`：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<api_key>",
    "ANTHROPIC_BASE_URL": "<base_url>",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

注意：
- 用 Python/Node 读改写，不要手写覆盖整个文件（可能损坏 hooks、plugins 等已有配置）
- `env` 是整体覆盖，切换提供商时旧 base_url 会被替换，无残留
- API key 以明文存盘——这是 Claude Code 的官方机制，提醒用户 key 会持久化到 `~/.claude/settings.json`

## 跳过首次引导

```bash
node -e 'const os=require("os"),fs=require("fs"),p=os.homedir()+"/.claude.json";const f=p;let c={};if(fs.existsSync(f))c=JSON.parse(fs.readFileSync(f,"utf-8"));c.hasCompletedOnboarding=true;fs.writeFileSync(f,JSON.stringify(c,null,2),"utf-8")'
```

## 环境变量替代方案

不想写 settings.json 时，用环境变量同样生效（适合临时/CI）：

```bash
export ANTHROPIC_AUTH_TOKEN="<api_key>"
export ANTHROPIC_BASE_URL="<base_url>"
export API_TIMEOUT_MS="3000000"
claude
```

## 自定义提供商（无预设）

只有 base_url 和 key 也能配：

1. 问清：base_url（Anthropic 兼容端点，通常形如 `https://xxx/api/anthropic` 或 `https://xxx/v1`）、协议（Anthropic `/v1/messages` 或 OpenAI 兼容）、模型名
2. OpenAI 兼容端点需要额外设置 `ANTHROPIC_API_KEY` 走转换层，或确认该端点本身兼容 Anthropic 协议
3. 按"配置写入规则"写入

## 常见错误排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `401 Unauthorized` / auth 错误 | key 无效或格式不对 | 检查 `ANTHROPIC_AUTH_TOKEN` 是否带 `sk-` 前缀的完整 key |
| `404` 端点不存在 | base_url 拼错 | 确认端点路径（`/api/anthropic` 还是 `/v1`） |
| 卡在引导界面 | `hasCompletedOnboarding` 未设 | 运行上方 skip-onboarding 命令 |
| 请求超时 | 服务端慢 | 调大 `API_TIMEOUT_MS` |
| `environment variable ANTHROPIC_API_KEY is not set` | 有些提供商要的是 `ANTHROPIC_API_KEY` 而非 token | 两个 env 都写：`ANTHROPIC_API_KEY` 与 `ANTHROPIC_AUTH_TOKEN` 相同值 |

## 示例

用户："把 claude code 接到 DeepSeek，key 是 sk-abc123"

1. 查 `references/providers.md`：DeepSeek base_url = `https://api.deepseek.com/anthropic`
2. 写 settings.json env：token=sk-abc123，base_url=上面
3. 设 `hasCompletedOnboarding: true`
4. 提示运行 `claude`，用 `deepseek-chat` 模型

## 安全提示

- 不要在命令行明文回显 key；写文件即可
- 切换/弃用提供商时提醒用户：key 仍留在 settings.json，可手动删除
- 本 skill 只是把配置写进用户自己的 Claude Code，不涉及敏感操作
