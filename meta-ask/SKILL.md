---
name: meta-ask
description: 用 metaso 内置的搜索问答模型直接提问（模型联网检索后作答）。需要一个自带网络知识的快速第二意见、或不想自己搜+读时使用。
---

# meta-ask — metaso 联网问答

密钥从环境变量 `METASO_API_KEY` 读。`content` 换成问题；响应是 SSE 流（每行 `data: ` 前缀的 JSON chunk，`data: [DONE]` 结束），`curl -N` 关闭缓冲逐段输出：

```bash
curl -sN https://metaso.cn/api/v1/chat/completions \
  -H "Authorization: Bearer $METASO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "fast", "stream": true, "messages": [{"role": "user", "content": "<问题>"}]}'
```

每个 chunk 的答案文本在 `choices[0].delta.content`（流开头的几个 chunk 是 `delta.citations`，携带引用来源列表）。只要最终回答时，把输出管道给 `grep -o '"content":"[^"]*"'` 之类的过滤器拼接即可；`model` 字段目前用 `fast`，其他取值以 metaso 文档为准。
