# Anthropic 兼容提供商参考表

各厂商官方 Anthropic 兼容端点。端点可能变动，配置前可 `curl -I` 验证连通性。

| 提供商 | base_url | 典型模型 | 获取 key |
|---|---|---|---|
| 智谱 Z.AI | `https://api.z.ai/api/anthropic` | glm-4.5, glm-4.6 | https://z.ai/manage-apikey/apikey-list |
| 智谱开放平台 BigModel | `https://open.bigmodel.cn/api/anthropic` | glm-4.5, glm-4.6 | https://open.bigmodel.cn/usercenter/apikeys |
| DeepSeek | `https://api.deepseek.com/anthropic` | deepseek-chat, deepseek-reasoner | https://platform.deepseek.com/api_keys |
| Kimi / Moonshot | `https://api.moonshot.cn/anthropic` | kimi-k2, kimi-latest | https://platform.moonshot.cn/console/api-keys |
| 通义千问 DashScope | `https://dashscope.aliyuncs.com/api/v2/apps/anthropic-compatible` | qwen-max, qwen-plus | https://bailian.console.aliyun.com/ |
| 硅基流动 SiliconFlow | `https://api.siliconflow.cn/v1` | deepseek-ai/DeepSeek-V3, Qwen/Qwen2.5 | https://cloud.siliconflow.cn/account/ak |
| 火山方舟 Ark | `https://ark.cn-beijing.volces.com/api/v3` | doubao-1-5-pro, deepseek-v3 | https://console.volcengine.com/ark |
| MiniMax | `https://api.minimax.io/anthropic` | MiniMax-M2.7 | https://platform.minimaxi.com/ |
| 腾讯混元 | `https://api.hunyuan.cloud.tencent.com/v1/anthropic` | hunyuan-turbo | https://console.cloud.tencent.com/hunyuan |
| GLM (open.bigmodel) | 同上 BigModel | glm-4.5-air | https://open.bigmodel.cn/ |

## 协议说明

- **Anthropic 原生端点**（`/api/anthropic`、`/anthropic`、`/v1/anthropic` 结尾）：直接填 `ANTHROPIC_BASE_URL` 即可
- **OpenAI 兼容端点**（如 SiliconFlow `/v1`、Ark `/api/v3`）：Claude Code 需要设置 `ANTHROPIC_BASE_URL` 指向厂商提供的 Anthropic 兼容子路径；若厂商只提供 OpenAI 兼容口，则必须经转换代理（如 `claude-code-router`）才能用
- 不确定时优先用厂商文档标注的 `anthropic` 路径

## 验证端点

```bash
curl -sS -o /dev/null -w "%{http_code}" https://api.deepseek.com/anthropic
```

返回 200/401/404 任一说明可达（401 说明路径存在但缺 key；404 说明路径不对）。
