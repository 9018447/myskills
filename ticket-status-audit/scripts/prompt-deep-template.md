# 票状态深查 — 第 {{ROUND}} 轮（查无可查协议）

仓库根目录 = 当前工作目录。本任务**只读**：除 `{{OUT}}/deep-round{{ROUND}}.json` 外不得写任何文件。
上一轮把下列 {{N}} 张票判为 unfinished 且证据不足。本轮对每张票**穷尽检索通道**，直到查无可查。

## 待深查清单

{{PENDING_TABLE}}

## 查无可查协议（每张票按序穷尽，通道缺一不可）

1. `zg query "<关键词>" --limit 5` 语义：至少 2 组不同关键词（票标题词 / 交付物组件名 / 验收标准关键词）
2. `zg query --fts "<确切符号|文件名|slug|tNN或NN票号>" --limit 5` 精确锚
3. `git log --all --oneline -i --grep=<关键词>`：slug、票号、组件名、中文标题词，多组都试；**`--all` 必须加**——完成证据常在未合并的 agent 分支上，提交措辞可能是 `merge tNN` 而非 slug
4. `git branch -a`；对名字可疑的分支再 `git log --oneline <branch> -- <相关路径>` 下钻
5. 引用检查：在 `.scratch`、`docs`、`docs/adr`、`CONTEXT.md`、`test` 里 grep 票 slug 关键词——下游票/docs 是否已消费其产出
6. 测试存在性：`test/` 下相关测试文件是否存在、是否被 `test/test_groups.toml` 纳组
7. 纯研究/盘问票：其 `## Answer`/结论被下游引用为依据的证据

## 每张票的判定出口（三选一）

- 任一通道命中交付物证据 → 改判 `done_unmarked` / `done` / `obsolete`，evidence 附具体路径或提交哈希；
- 全部 7 通道穷尽且无命中 → 保持 `unfinished`，`basis: "confirmed"`，reason 写明各通道查询词与结果摘要；
- 找到证据表明确实未做/被冻结 → `unfinished` + `basis: "confirmed"`，reason 给具体证据。

**不要**留 `basis: "insufficient_evidence"`——那是"没查完"，本轮就要穷尽；实在被工具故障卡住的通道除外（reason 里说明）。

## 硬性禁令

- 禁止复制模板句：每张票的 reason 必须含至少一个**具体查询词**或具体路径/提交哈希。
- 票面自述完成不算证据。
- `tickets` 数组只准含待查清单里的文件，一张不许多。

## deep-round{{ROUND}}.json schema（严格遵守）

```json
{
  "tickets": [
    {
      "file": ".scratch/<effort>/issues/NN-<slug>.md",
      "status": "unfinished|done_unmarked|done|obsolete",
      "basis": "confirmed|insufficient_evidence",
      "reason": "含具体查询词/路径/提交的裁定依据",
      "evidence": [{"kind": "file|commit|zg", "path": "…", "commit": "…", "note": "…"}],
      "channels": [
        {"channel": "zg语义|zg-fts|git-log-all|branch|refs|tests|research", "query": "实际查询词", "result": "一句命中摘要或无命中"}
      ]
    }
  ]
}
```

- 待查清单每张**恰好一条**；`channels` 列全你实际试过的通道（≥7 条为满分穷尽，确实不可用的通道也要列出并注明原因）。
{{ERRORS_BLOCK}}
