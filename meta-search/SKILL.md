---
name: meta-search
description: 用 metaso 搜索网页知识：返回带摘要和 URL 的结果条目。需要查资料、验证事实、补充上下文，或 WebSearch 不可用/结果不佳时使用。
---

# meta-search — metaso 网页搜索

密钥从环境变量 `METASO_API_KEY` 读。`q` 写具体问题（中文即可），`size` 一般 10：

```bash
curl -s https://metaso.cn/api/v1/search \
  -H "Authorization: Bearer $METASO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "<问题>", "scope": "webpage", "includeSummary": true, "size": "10", "includeRawContent": false, "conciseSnippet": true}'
```

`scope` 可选：`webpage`（默认）、`news`、`wechat`、`arxiv`、`github`。

响应 JSON 里 `webpages[]` 每条有 `title`、`link`、`summary`、`snippet`、`date`。需要某条的全文，用 meta-fetch 按 `link` 取原文。
