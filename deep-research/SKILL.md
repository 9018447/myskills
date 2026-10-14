---
name: deep-research
description: 编排者给出计划的网络深入研究：按「计划→广域搜索→逐子方向深潜→综合闭环」产出引用可核验的调研报告。适用于先写子方向计划、最终交付带闭环引用报告的研究任务；搜索由可信脚本确定性调用 metaso API，AI 不触网。无计划、随问随答的一次性查询不适用。
---

# deep-research：机制化闭环的网络深度研究

在**目标仓库根目录**操作。编排者（主 agent）运行前写好任务契约 `.agent/luna/task.json`（研究主题 + 子方向计划），产物固定在 `.agent/luna/research/<task_id>/`。工作流 YAML 与可信驱动位于本技能目录（`workflow.yml`、`scripts/driver.py`）。

## 1. 写任务契约

按下列 schema 写 `.agent/luna/task.json`（相对路径按仓库根解析）：

```json
{
  "task_id": "research-<slug>-001",
  "topic": "研究主题（一句话）",
  "objective": "研究要回答的核心问题",
  "plan_file": null,
  "directions": [
    {"id": "D1", "title": "子方向标题", "questions": ["要回答的问题 1", "要回答的问题 2"]},
    {"id": "D2", "title": "另一个子方向", "questions": ["要回答的问题"]}
  ],
  "scopes": ["webpage"],
  "broad_queries": 4,
  "queries_per_direction": 3,
  "size_per_query": 10,
  "max_searches": 24,
  "max_fetches": 8,
  "fulltext_max_chars": 40000,
  "allowed_write_paths": [],
  "constraints": [],
  "max_attempts": 2,
  "step_timeout_seconds": 1200,
  "timeout_seconds": 5400
}
```

- `directions` 1..12 个；`id` 唯一（字母数字开头，可含 `_`/`-`，≤16 字符）；每个 1..8 条非空 `questions`。
- `scopes` 取 {webpage, news, wechat, arxiv, github} 的非空子集；`max_searches` 必须 ≥ `broad_queries` + 方向数×`queries_per_direction`——计划超预算 preflight 直接失败，改计划再跑。
- `plan_file` 可选：给了就须为仓库相对路径且文件存在（可留 `null`）。
- 数值域：broad_queries 1..6（默认 4）、queries_per_direction 1..6（默认 3）、size_per_query 1..10（默认 10）、max_fetches 0..30（默认 8）、max_attempts ≥1（默认 2）。

完成标准：第 2 步 preflight 通过。

## 2. 运行

```bash
specify workflow run <技能基目录>/workflow.yml --json
```

`<技能基目录>` 是本技能的安装目录，Claude Code 调用技能时会给出基目录（Base directory）；源库位于 `~/myskills/deep-research`，与安装位内容一致。workflow 以本地文件路径传入，可在 Spec Kit 项目外的 git 仓库中运行（版本要求见参考资料）。`METASO_API_KEY` 必须已在环境里（缺失时 preflight 直接失败）；密钥只从环境读取、绝不落盘。

边界声明：搜索/抓取由可信脚本（`scripts/driver.py`）用 python 标准库确定性调用 metaso HTTP API，AI（codex）只提查询、读结果、写产出，从不接触网络，也不把 AI 输出拼进 shell 命令（全部经文件传递）。「逻辑闭环」是**机制校验**（引用可解析 + 方向全覆盖 + 搜索预算守恒 + 写入不越界），不是语义正确性担保。

完成标准：stdout 拿到单个 JSON 对象，`status` 为 `completed`。步骤失败时对象带 `error` 字段。

## 3. 失败恢复

```bash
specify workflow status <run_id> --json
specify workflow resume <run_id> --json
```

仅 `paused`/`failed` 可恢复。注意：引擎 `resume` 用的是运行开始时冻结的旧 workflow 定义，修过 workflow.yml 后的改进不生效——**超时/中断类失败建议直接重跑一次 run**：驱动是幂等的（已完成的查询提案、搜索记账、笔记、findings、综合报告自动跳过，重跑只补缺的部分，不重复花搜索预算），重跑前不必清空产物目录。

## 4. 判读结果

读 `.agent/luna/research/<task_id>/verify.json` 的 `verdict`：

- `pass` —— 产物齐全、report 固定章节逐字合规、所有 `[S#]` 引用可解析到 sources.json、report 引用来源数 ≥ 方向数、搜索预算守恒、写入全部落在白名单内
- `repairable` —— 存在可修复失败（如悬空引用、章节顺序、字节不足），工作流已自动重试一次；`failures` 数组列出明细
- `fatal` —— sources.json 结构性损坏或写入越界，升级人工处理

`report.md` 是交付物（固定章节：`# ` 标题 → `## 执行摘要` → 各 `## <方向id>` → `## 交叉对比与矛盾` → `## 证据缺口` → `## 结论`）；`sources.json` 是引用唯一事实源（sid、searches、budget、fetches 都在此）；`notes/broad.md` 与 `findings/*.md` 是过程留档；`prompts/`、`logs/` 是每次 codex 调用的审计留档（关联 `run_id`）。

## 5. 汇报字段

`task_id`、`run_id`、`verdict`、报告绝对路径、搜索预算 `used/max`、修复尝试次数、实际模型（`gpt-6-luna`）。

## 参考资料

- 裁决语义：`verify` 恒以 0 退出，`verify.json`（`{verdict, failures, attempt}`）是唯一裁决来源；`assert-passed` 步骤强制终态为 `pass`，绕过即失败。
- 搜索预算：每次搜索发起前检查 `budget.used < max_searches`，超限查询丢弃并记录 `search_dropped`（不报错）；搜索失败重试 1 次、仍失败记 `search_failures` 与 `raw/<qid>.json={"ok":false}`，**不计入预算**（`budget.used == len(searches)` 只含成功搜索）。全文抓取受 `max_fetches` 预算，超限记 `fetch_dropped`，单条失败记日志继续。
- 提案重提：codex 的 JSON 提案（queries/fetch-requests）校验失败时，同一次调用允许附错误说明重提 1 次，再失败 fatal；**不算** repair attempt。
- 修复上限：`max_attempts`（默认 2）次修复后仍 `repairable` 按失败终止；repair 只许改 `report.md`、`notes/broad.md`、`findings/*.md` 三个位置，不提供任何搜索能力。
- 超时语义：**specify 引擎对每个 shell 步骤有默认 300 秒上限**（实测行为，文档未写明），本工作流已在 workflow.yml 为各 shell 步骤显式声明 `timeout: 7200` 兜底；`timeout_seconds` 仍是 driver 内部每个研究阶段（broad-search / deep-dive / synthesize）的进程内墙钟上限（每次 codex 调用与每次搜索前检查，超时 fatal）；`step_timeout_seconds` 是单次 codex 调用的超时。驱动支持幂等续跑：查询提案、搜索记账、笔记/findings（含大小阈值与 fetch 完成标记）、综合报告均以既有产物为准跳过重做。
- 写入边界：产物目录、`.specify/`（引擎运行态目录）、契约 `allowed_write_paths` 之外的写入判 fatal；baseline 与复核都用 `git status --porcelain -z`（NUL 分隔，重命名条目取新路径）解析，白名单根的祖先折叠条目不算越界。
- 版本要求：`workflow.yml` 声明 `requires: speckit_version: ">=1.2.0"`——脚本经 `SPECKIT_WORKFLOW_DIR` 定位、本地文件需可在 Spec Kit 项目外运行，两项行为 1.2.0 起才可靠。
- metaso 用法：搜索 `POST https://metaso.cn/api/v1/search`（Bearer `$METASO_API_KEY`，body `{q, scope, includeSummary, size, includeRawContent, conciseSnippet}`）；全文 `POST https://metaso.cn/api/v1/reader`（Accept: text/plain）。
- 引擎状态在当前工作目录 `.specify/workflows/runs/<run_id>/`，与业务产物分开放。

## 自测

`python3 <技能基目录>/scripts/driver.py selftest`：离线断言契约校验拒绝路径、查询 schema、URL 归一化去重与 sid 分配、`[S#]` 引用抽取与悬空检测、报告章节顺序、预算记账、`violates()` 越界判定（无网络、无 codex）。
