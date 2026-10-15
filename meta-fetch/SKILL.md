---
name: meta-fetch
description: 用 metaso reader 抓取网页正文：给定 URL 返回提取好的纯文本。WebFetch 拿不到内容（反爬、需要 JS 渲染、微信公众号文章）或想要干净的正文时使用。
---

# meta-fetch — metaso 网页正文抓取

密钥从环境变量 `METASO_API_KEY` 读。`url` 换成目标页面。**经 context-mode 触发**：把下面的 curl 放进 `ctx_batch_execute`（`queries` 写明要读正文的哪些部分）或 `ctx_execute` 里执行——整篇正文只进索引，对话里只出现命中窗口；在 Bash 里裸跑会把整篇文章灌进对话：

```bash
curl -s https://metaso.cn/api/v1/reader \
  -H "Authorization: Bearer $METASO_API_KEY" \
  -H "Accept: text/plain" \
  -H "Content-Type: application/json" \
  -d '{"url": "<目标URL>"}'
```

响应是提取好的正文纯文本（不是 JSON），可能很长——先用 head/jq 截取，或只读需要的部分。配合 meta-search：搜到 `link` 后用它取全文。
