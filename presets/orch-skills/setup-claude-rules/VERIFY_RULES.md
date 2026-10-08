# 验证与复审规则（jev 判定优先）

## 硬约束

代码复审、完成工作的确认、事实核对——这三类判断优先交给 jev 判定服务，不要主 agent 自己逐一通读材料下结论。判定前先把证据摆进 `state`；证据不足时先补齐再问，不要基于空洞 state 拿判定结果。

## 判定接口（按优先级）

1. **MCP 工具**（本机会话已挂载时）：`mcp__jev__jev_judge`，直接传 `state`（字符串或 JSON）和 `questions` 数组，问题字段见下节契约。
2. **CLI**：判定材料在文件里或工具输出很大时，把材料留在外部文件，用 `jev-use judge` 从 shell 管道传入；或按下面的请求 JSON 契约写 `request.json` 后执行：

```bash
python3 <jev技能目录>/scripts/jev.py decide /path/to/request.json --dry-run  # 只校验形状
python3 <jev技能目录>/scripts/jev.py decide /path/to/request.json            # 实际调用
```

CLI 退出码：**0** = 有有效结论，可按结论行动；**2** = 至少一题需要人工复核（abstention），不得把该输出当 go-ahead；**1** = 请求/网络/协议错误，同样不得当 go-ahead。`request.json` 里**不要写 `model` 字段**——CLI 会注入默认值，手填占位符（如 `"default"`）会被上游以 HTTP 400 拒绝。密钥只在进程环境变量里，不写进请求文件、不打印。

## 请求契约（确定性形状）

```json
{
  "state": {
    "goal": "复审 PR #12 的改动是否覆盖所有调用方",
    "facts": ["diff 修改了 lib/hooks.ts:347 的 loadConfig 签名"],
    "evidence": ["测试输出：3 passed, 0 failed"],
    "open_questions": []
  },
  "questions": {
    "covers_callers": {
      "type": "noul",
      "question": "该改动是否覆盖了全部调用方？",
      "criteria": {"true": "每个调用点都有对应更新或验证", "false": "存在未更新的调用点"}
    }
  }
}
```

- `state`：只放已掌握的事实（目标、验收标准、diff 摘要、测试结果、关键报错原文），不整篇贴文件、不含密钥。
- `noul`（真/假）：`criteria` 可选，有则必须是 `{"true": ..., "false": ...}` 两键。
- `choice`（选项）：`criteria` **必须**是对象（标签 → 一行说明）；数组会被请求构建拒绝。每个选项注明"选中意味着什么"。
- `score`（分级）：`criteria` 是 2–10 个**有序**等级描述的数组，索引从 0 起（3 级返回 0–2，含小数属正常）。
- 每题带 `id`，响应按原 id 返回。

## 批量与依赖

同一 state 下的**所有独立问题一次提交**，不要逐题串行调用。问题之间读不到彼此的答案：若问题 B 依赖问题 A 的结论或某操作的执行结果，先执行/先问 A，观察新状态后再发起新请求问 B。

## 结论解释（硬规则）

- `noul` 返回的就是"是"的概率（0–1），没有独立 confidence 字段；可以自信地为假。
- `choice`/`score` 的 `confidence` 描述分布形状，**不是**正确概率；`selected` 表示选了标签，**不等于**行动被批准。
- 置信度低或标记 `escalate` 的问题由主 agent 自己判，不要硬套 jev 的答案。
- 精确规则、正则匹配、算术、日期比较用代码算，不问 jev。
- 同一 state 反复重问同一问题不会变成新证据；状态实质变化后才重新判定。

## 模板复用

周期性检查点（每 ticket 复审、批量分诊）把上次成功的请求 JSON 留在磁盘作模板，下次只改 `state`、证据和问题 id。凭记忆重建请求形状反复出错（占位 `model`、错形 `criteria`）；复制已验证文件是默认做法。

## 边界

- jev 的结论是判定辅助，不是授权或安全边界；要不要改代码、要不要发布，仍由主 agent 决定，宿主确认和确定性检查照常生效。
- 只送必要且已授权的上下文；私有文档不未经同意发往外部 API。
- 用户明确要求主 agent 自己看时，按用户的来。
