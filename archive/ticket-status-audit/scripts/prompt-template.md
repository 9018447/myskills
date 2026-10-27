# 票状态审计 — 第 {{ATTEMPT}} 轮

仓库根目录 = 当前工作目录。`.scratch/` 下是 markdown 票（约定见 docs/agents/issue-tracker.md）。
本任务是**只读审计**：除 `{{OUT}}/report.json` 外不得写任何文件。

## 输入
- 待审计票清单（共 {{TOTAL}} 张）：下方表格；明细含原始 Status 行的扫描件在 `{{STATE}}`。
- 产出：`{{OUT}}/report.json`（写文件，不要把全文贴在对话里）。
{{ERRORS_BLOCK}}
## 票清单

{{TICKET_TABLE}}

## 四态（最终枚举，不允许第五个值）
- `done`：Status 已标 closed 词（resolved/done/completed/merged），且没有被替代/作废的标注。
- `done_unmarked`：Status 是 open 词（pending/ready-for-agent/claimed/open/缺失）或 frozen，但代码库证据表明工作**实际已完成**——应翻牌而未翻。这正是本审计要抓的目标（历史上票 18/19 出过：证据已被下游引用、Status 仍停在 pending）。
- `unfinished`：证据不能证明完成。含：确实没做、进行中、frozen/paused（reason 里标注 frozen）。
- `obsolete`：票面有 superseded 指针、或被用户裁定/roadmap 冻结取代、或交付物对当前主线已无意义——该归档。

## 每张票的判定流程
1. 读票面全文，提取**交付物**：要写的组件/测试/文档/修复/结论。
2. 纯研究/盘问票（无代码交付物）：看其 Answer/结论是否已被下游票、docs/adr、实现引用为基础。
3. 证据渠道（都用，别只挑一个）：
   - `zg query "<票标题+交付物关键词>" --limit 5`（语义）
   - `zg query --fts "<确切符号|文件名|票号slug>" --limit 5`（精确锚）
   - `git log --oneline -i --grep=<slug关键词>`
   - 语义命中若落在 `agent/verification/runs/`、`.agent-results/` 等运行日志里，只能当**线索**，须下钻到它指向的真实源码/测试/票文件再定论，不得直接拿日志当完成证据。
4. 比对：
   - Status 是 closed 词 → `done`；
   - Status 是 open/frozen 词但交付物在代码库真实存在（实现+测试，或产出被下游引用为已解决）→ `done_unmarked`；
   - superseded 指针/裁定取代 → `obsolete`；
   - 其余 → `unfinished`。
5. 证据找不足 → `unfinished`，reason 注明"证据不足"（宁缺勿滥，不许凭票面自述定 done_unmarked）。

## 硬性禁令
- **票面说自己完成了不算证据**——只认代码库文件、git 提交、下游票/docs 引用。
- evidence 必须指向真实存在的路径或提交哈希，验收器会逐条核验，虚构 = 整轮驳回。
- 不修改 `.scratch/` 任何文件。
- **tickets 里只准出现下方表格列出的文件**，一张不许少、一张不许多（包括你自己在文件系统里发现的其他疑似票）。表外疑似票写进顶层 `"notes"` 数组（一行一个，附一句理由），验收器不核它，留给编排者定夺。

## report.json schema（严格遵守）
```json
{
  "tickets": [
    {
      "file": ".scratch/<effort>/issues/NN-<slug>.md",
      "status": "unfinished|done_unmarked|done|obsolete",
      "basis": "confirmed|insufficient_evidence",
      "skip": false,
      "reason": "一句到三句中文裁定依据",
      "evidence": [
        {"kind": "file", "path": "src/fluid_handling/valve.jl", "note": "实现了票里要的 Valve 组件"},
        {"kind": "commit", "commit": "abc1234", "note": "合并提交"},
        {"kind": "zg", "path": "test/valve.jl", "note": "zg 命中"}
      ]
    }
  ],
  "summary": {"unfinished": 0, "done_unmarked": 0, "done": 0, "obsolete": 0}
}
```
- 表格中每张票**必须恰好出现一次**，不能漏（含 Status 缺失或写法怪异的）。确非票的表格条目（map/spec/closure 汇总类）用 `"skip": true` + reason。
- `skip:true` 不需要 status/evidence，但必须给 reason。
- `done_unmarked` 至少要 1 条 evidence（正向断言须正向证据）；`unfinished` 的 evidence 可以为空数组。
- summary 四个数必须与 tickets 逐条统计一致。
- unfinished 的票加 `"basis"` 字段：有具体证据表明未做/被冻结 → `"confirmed"`（reason 引证据）；只是没查到 → `"insufficient_evidence"`（后续深查轮会再来穷尽）。done/done_unmarked/obsolete 一律 `"confirmed"`。
- 顶层可加 `"notes": ["表外发现：…（一句理由）", …]`，只收表格之外的疑似票线索。
