---
name: ticket-status-audit
description: 用 zg 语义搜索审计 .scratch/ 票状态，四态判定（unfinished/done_unmarked/done/obsolete），Spec Kit 工作流 + 可信验收。当用户要「盘点票/维护票信息/审计 .scratch/确认哪些票完成未标记/该归档」时使用；写代码、跑测试不适用。
---

# ticket-status-audit

对 `.scratch/<effort>/` 下所有票（含 `Status:` 行或位于 `issues/` 目录的 markdown）做只读审计：`zg index` 增量更新索引 → 派发 codex（gpt-6-luna）逐票用 zg 语义/精确检索 + git log 取证 → 四态判定 → 可信验证器独立验收（覆盖全票、枚举合法、证据真实、写入不越界）→ **deepdive 深查步**：对 `basis=insufficient_evidence` 的票迭代派发（默认 ≤3 轮，契约 `deep_max_rounds`），每轮按"查无可查协议"穷尽 7 条检索通道（zg 语义×2、zg-fts、`git log --all` 多关键词、分支下钻、引用检查、测试存在性、研究票结论消费），留下 channels 检索轨迹；全通道无命中才终判 `basis=confirmed` → 产出 `report.json`。

**工作流不写 `.scratch/`**——报告是提案；按报告翻转票的 `Status:` 由编排者/用户裁定后另行执行。

## 运行步骤

1. **填/复核契约** `.agent/workflow/task.json`（schema 见下）。要缩范围就改 `inputs.efforts`（如只审 `["live-test-fixes"]`）。
2. 在**仓库根目录**运行：
   ```bash
   specify workflow run "<本技能目录>/workflow.yml" --json
   ```
3. 查进度/恢复（`<run_id>` 取自运行输出）：
   ```bash
   specify workflow status <run_id> --json
   specify workflow resume <run_id> --json
   ```
4. 验收结果：工作流结束态 `succeeded` 即验收通过；报告在 `.agent-results/ticket-status-audit/report.json`，运行摘要在 `SUCCESS.json`，派发日志 `dispatch-attemptN.log`。

## 契约 schema（.agent/workflow/task.json）

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | str | 本次任务名 |
| `objective` | str | 目标描述 |
| `inputs.scan_root` | str | 扫描根，相对仓库根（默认 `.scratch`） |
| `inputs.efforts` | str[] | 可选，只审这些 `.scratch` 子目录 |
| `acpx_args` | str[] | acpx 派发参数（`--approve-all` 与 `exec -f` 之间），如 `["--model","gpt-6-luna","codex"]`；换 omp 即 `["--agent","omp acp"]` |
| `allowed_write_paths` | str[] | 允许写入的前缀（报告/状态/`.zvec-grep/`/`.specify/workflows/`） |
| `protected_paths` | str[] | 声明性保护清单（实际执法=白名单，见 verify） |
| `max_attempts` | int | 派发上限（默认 2：首派 + 一次 repair） |
| `timeout_seconds` | int | 单次派发超时（默认 5400） |

## verify 退出码语义

- `0` 通过；`1` 可修复失败（报告缺失/非法/漏票/证据不实 → repair-once 重派一次）；`2` 越界写入（致命）；其余致命。
- 第二次验收失败 → 工作流终态失败，不会靠 `continue_on_error` 混过。

## 判定判据

判据全文在 `scripts/prompt-template.md`（版本化）：closed 词 → `done`；open/frozen 词但交付物在代码库有实证 → `done_unmarked`；证据不足 → `unfinished`；superseded/被裁定取代 → `obsolete`。票面自述完成不算证据；`done_unmarked` 强制至少一条证据。

## 修复与恢复

- repair 走同一派发通道，prompt 附上一轮验收器驳回清单（`state.json` 的 `validator_errors`）。
- zg index 失败不直接终止：本轮不派发 → verify 判 1 → repair 重试 zg + 派发。
- 派发静默死亡（无 report、无 rc）：按原契约重跑 `resume`，或直接重跑 step 2。
