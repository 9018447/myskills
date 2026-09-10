---
name: graph-risk-review
description: >
  Deep code review that fuses git-diff engineering (via the `ocr` CLI in
  delegate mode) with the codebase-memory-mcp knowledge graph to assess
  real-world risk of every change. Goes far beyond line-level linting: for
  each changed symbol it traces inbound callers, computes blast radius and
  graph centrality, pulls complexity hot-path metrics, and weighs every
  finding by how much of the codebase it can actually break. Produces a
  risk-graded Chinese Markdown report saved to disk. Use whenever the user
  asks to review code, review changes/commits/branches, do 代码审查,
  评估改动风险, 影响面分析, or wants to know "how risky is this diff" —
  even if they just say "帮我看看这次改动" or "这个 commit 有没有问题".
license: Apache-2.0
compatibility: >
  Requires the `ocr` CLI (delegate mode only — no LLM endpoint needed) and
  the codebase-memory-mcp MCP server with the target repo indexed.
metadata:
  version: "1.1.0"
  tags: [code-review, risk, knowledge-graph, impact-analysis]
---

# Graph Risk Review

A code review has two independent questions: *is this change correct?* and
*how much damage can it do if it's wrong?* A diff alone can only answer the
first. This skill answers both by running a conventional diff review (ocr
delegate mode handles file selection and rule resolution deterministically)
**and** lifting every changed symbol into the codebase knowledge graph, where
caller counts, transitive dependents, route reachability, and complexity
metrics tell you the blast radius. A mediocre bug in a leaf utility is Low
risk; the same bug in a function with 40 inbound callers on a hot path is
Critical. Review effort and report ordering should follow that logic.

## Prerequisites

```bash
which ocr || npm install -g @alibaba-group/open-code-review
```

Check the repo is indexed in the knowledge graph: run `search_graph` for any
known symbol. If results look absent or the repo was never indexed, run
`index_repository` (prefer `mode="fast"` for large repos). If the working
tree has drifted far from the last index (many files changed since), re-index
first — impact analysis on a stale graph produces confidently wrong caller
lists, which is worse than no graph at all. State in the report which index
the analysis is based on.

🔴 CHECKPOINT · 🛑 STOP — a full re-index is expensive (minutes on a large
repo). Before running `index_repository`, tell the user how stale the index
is (files changed since last index) and the expected cost, and wait for
confirmation. Skipping this stops the review until the user decides.

Delegate mode never calls an LLM on the ocr side; no `ocr llm test` needed.

## Workflow

### Step 1: Scope the review with ocr delegate

```bash
ocr delegate preview --format json                  # workspace changes (default)
ocr delegate preview --format json -c <hash>        # single commit
ocr delegate preview --format json --from main --to feature   # branch range
```

The preview output splits files into `reviewable_files` and `excluded_files`
(each with an exclusion reason). Only **reviewable** files need individual
accounting: every one must end the review as **reviewed** or **skipped with
a concrete reason** — never silently dropped. Excluded files need no
per-file attention; in the report just give the count and a one-line summary
of what was excluded (e.g. "75 个文档/批跑产物数据文件").

Within the reviewable set, use judgment about depth: source code files get
full review; generated data files, runtime state dumps, lockfile-style YAML
and similar non-logic artifacts may be skimmed and skipped with a reason —
but if such a file feeds program behavior (config schemas, state consumed by
a solver), say so and check the fields that changed.

🔴 CHECKPOINT · 🛑 STOP — if the reviewable set is large (>20 reviewable
files, or >3000 diff lines), do NOT dive in. Present the user a scope
summary first: file count, diff size, your planned batches, and proposed
depth trade-offs (which files get full review vs skim). Wait for
confirmation before continuing to Step 2.

### Step 2: Fetch rules and diffs

```bash
ocr delegate rule --format json <path1> <path2> ...
```

The rule output groups files by rule content. If the terminal truncates long
JSON output, re-run with output redirected to a file and `Read` that file
instead. Files whose extension matches no rule (e.g. `.sh` under a Python
project's rules) simply get no group — review them with general engineering
judgment; that's expected, not an error.

Get diffs with git, using the mode metadata from Step 1 (`git diff HEAD --
<path>` for tracked workspace files, `git diff <merge_base>..<to>` for range
mode, `git show <commit>` for commit mode; read untracked files whole). For
**newly added files** the diff is the entire file — skip the diff view and
just read the file directly.

### Step 3: Graph impact analysis — the core of this skill

Before reviewing line-by-line, map the change onto the graph. For each
changed file, identify the changed symbols (diff `@@` hunk headers name the
enclosing function; fall back to reading the file around changed lines).

For each changed symbol:

1. **Locate it**: `search_graph(name_pattern=".*symbol.*")` or a BM25 query.
   Note overloads/same-name symbols — match by file path.
2. **Blast radius**: `trace_path(function_name=..., direction="inbound",
   risk_labels=true, depth=3)`. Record: direct caller count, transitive
   dependents, and whether any caller is an entry point / Route (externally
   visible behavior) or a hot loop.
3. **Complexity / hot-path check**: `query_graph` for the changed functions'
   metrics — `complexity`, `transitive_loop_depth`, `linear_scan_in_loop`,
   `alloc_in_loop`, `unguarded_recursion`. A change inside a function already
   flagged as a hot-path candidate deserves extra scrutiny.
4. **Cross-service reach** (multi-repo setups): if the changed symbol sits
   behind a Route/Channel, use `trace_path(mode="cross_service")` to see
   which other services consume it. Skip this step for single-repo reviews.

Build a **centrality tier** per changed symbol — this drives everything later:

- **T1 枢纽**: ≥10 direct callers, or reachable from a Route/entry point within 2 hops
- **T2 骨干**: 3–9 direct callers, or on a flagged hot path
- **T3 边缘**: 0–2 callers, internal-only

Thresholds are starting points, not law. Override with judgment when the
numbers mislead, and always state the reason. Example: a batch-engine
function with only 4 direct callers is still T1 if two of those callers are
the drivers that run it over every candidate in a fleet-wide batch — blast
radius is measured in affected *outcomes*, not just caller cardinality.
Conversely, a 10-caller function whose callers are all dead code is T3.

### Step 4: Review each file, graph context in hand

For every reviewable file, review the diff against its rule group (Step 2)
**and** its impact context (Step 3). The graph changes what you look for:

- Changed function signature or return-contract on a T1/T2 symbol → check
  the actual callers from `trace_path` output for broken assumptions, don't
  just eyeball the diff. Use `get_code_snippet` on both sides of a contract
  (caller and callee) to verify status enums, argument names, and return
  shapes actually match — a callee's docstring revealing a legal state the
  caller rejects is a real finding, not a nit.
- New branch/early-return in a high-complexity function → reason about which
  caller-visible states it can now produce.
- Changed behavior reachable from a Route → treat as API-visible; flag
  backward-compat risk explicitly.
- Pure T3 leaf changes with no findings → one line in the report, move on.
  Don't manufacture issues to justify the review.

Work in bounded batches for large changes — a good batch is one rule group
or ~5 related files, whichever is smaller. Do not stop at the first
high-severity finding. Track coverage in a checklist.

**Verify data-processing logic empirically.** For scripts that compute over
data (monitors, statistics, report generators), don't reason about formats
in your head — open a real data file in the repo (or a fixture/test output)
and check the script's assumptions against actual contents. Off-by-one and
format-assumption bugs in glue scripts only surface this way, and they
matter because people make decisions from those numbers.

### Step 5: Fuse findings into risk grades

Final risk = **finding severity × centrality tier**. A High bug in a T1
symbol is Critical; a Medium style concern in T3 stays Low. When a finding
and the graph disagree (e.g. scary-looking diff in a truly dead function),
trust the graph and downgrade — but note the downgrade reasoning in the
report so the user can challenge it.

The `risk_labels` from `trace_path` (CRITICAL/HIGH/MEDIUM by hop distance)
mean only *"this caller is N hops from the symbol"* — they are a proximity
signal, not a severity. Use them as evidence when assigning the centrality
tier (a hop-1 caller that is an entry point strengthens T1), never multiply
them into the grade directly.

### Step 6: Write the report to disk

Write the full report (Chinese) to:

- `.scratch/code-review/review-<YYYYMMDD-HHMMSS>.md` when the repo has a
  `.scratch/` directory, otherwise `code-review-<YYYYMMDD-HHMMSS>.md` in the
  repo root.

In chat, return only a short summary (risk grade, top findings, report path).

**Report template — use exactly this structure:**

```markdown
# 代码审查与风险评估报告

- 范围：<workspace / commit / from..to> | 审查时间 | 图索引版本说明
- 覆盖：reviewed N / skipped M（coverage %），skipped 附原因；
  excluded K（ocr 排除的文件，一句话概括类别）

## 风险总览

| 等级 | 数量 | 说明 |
|------|------|------|
| Critical / High / Medium / Low | ... | 一句话 |

整体风险评级：<Critical/High/Medium/Low> + 一句话理由

## 影响面分析（图工具）

| 改动符号 | 文件 | 中心性层级 | 直接调用方 | 是否触达入口/Route | 热路径标记 |
|---------|------|-----------|-----------|-------------------|-----------|

(随后用 1–3 句话指出本次改动中爆炸半径最大的符号及原因；
若有 override 中心性层级的判断，在此说明理由)

## 详细发现（按风险等级排序）

### Critical / High
- **`path/to/file.py:42`** — 问题描述
  - 图上下文：该符号被 X 个函数调用，触达 <入口/Route 名称>
  - 建议：修复方式

### Medium / Low
- 同上格式，Low 可只列一行

## 覆盖与跳过
- skipped 文件清单 + 原因；excluded 文件只给数量与类别

## 结论与建议行动
- 合并前必须处理 / 可以合并但建议跟进 / 无需行动
```

## Failure Modes & Recovery

每一步都可能失败。按下表处理——先一线修复，仍失败走兜底路径；
兜底路径全部允许审查继续，但必须在报告中注明降级点。

| 触发条件 | 一线修复 | 仍失败兜底 |
|---|---|---|
| `which ocr` 失败 / ocr 不在 PATH | `npm install -g @alibaba-group/open-code-review` | 退回手工圈定：`git status` + `git diff --stat` 自行划分 reviewable/excluded，报告注明「ocr 缺失，范围为手工圈定」 |
| 图索引不存在，或已知符号 `search_graph` 查不到 | `index_repository`（大仓库 `mode="fast"`；先过 Prerequisites 的 re-index 检查点） | 用户拒绝或索引失败 → 降级为纯 diff 审查，报告标注「未入图，无影响面分析」 |
| 索引陈旧：diff 新增/改名的符号查不到 | 重索引（同样过检查点） | 不重索引 → 查不到的符号逐个标「未入图」，仅对可查符号做图分析，报告注明索引版本 |
| `search_graph` 返回多个同名符号 | 按文件路径过滤匹配项再 `trace_path` | 路径也区分不了 → `get_code_snippet` 逐个比对签名，人工确认 |
| ocr JSON 输出被终端截断 | 重跑并重定向到文件，用 `Read` 读 | 文件仍过大 → `Read` 分页或 `jq` 只取 `reviewable_files`/`excluded_files` 字段 |
| jj-colocated 仓库 workspace 模式 preview 异常 | 改用显式 `--from`/`--to` git refs | 仍异常 → `git diff` 手工圈定，报告注明 ocr bypass |
| diff hunk header 定位不到改动符号（模板/配置/裸脚本改动） | 读文件改动行附近上下文，确定归属函数 | 不属于任何函数 → 按文件粒度做影响面，中心性层级记 N/A |

## 评审反例黑名单

评审时**不要做**以下任何事。每条都是真实反模式；命中任意一条，
停下来重写该部分再继续。

| # | 不要做什么 | 为什么 | 替代做法 |
|---|---|---|---|
| 1 | 为「凑够发现」编造问题 | 技能的价值是校准不是告警；T3 无发现就一行带过 | 无发现就写无发现，直接给 Low |
| 2 | 把 `risk_labels` 的跳距（CRITICAL/HIGH/MEDIUM）乘进最终评级 | 跳距只度量图上的距离，不度量业务严重度 | 跳距仅作中心性分层证据；最终评级 = finding 严重度 × 中心性层级（Step 5） |
| 3 | 只看 diff 就判定签名/契约问题 | diff 看不到调用方一侧的假设 | `trace_path` 拉真实调用方 + `get_code_snippet` 核对两侧的状态枚举、参数名、返回结构 |
| 4 | 凭脑子推断数据格式与统计口径 | 胶水脚本的 off-by-one/格式假设 bug 只会在真实数据上现形 | 打开仓库里的真实数据文件（或测试 fixture）逐条核对脚本假设 |
| 5 | 报告未验证可达性的疑似 bug | 死代码里的「高危」是假警报 | 上报前先 trace 实际调用路径确认可达；杀掉自己的误报是职责 |
| 6 | 静默丢弃任何 reviewable 文件 | 覆盖度缺口 = 审查结论不可信 | 每个 reviewable 文件必须 reviewed 或 skipped+具体原因，报告记账 |
| 7 | 图显示改动隔离时仍夸大风险「以防万一」 | 虚高评级稀释真正高危发现的注意力 | 信任图证据降级，并在报告写明降级理由供用户质疑 |
| 8 | 降级/兜底后不吭声 | 用户会把降级结论当全量结论用 | 走了 Failure Modes 表的兜底路径，必须在报告注明降级点 |
| 9 | 越过 🔴 CHECKPOINT 继续执行 | 检查点是用户的钱（re-index 耗时）与方向（大范围深度取舍） | 停下输出要求的内容，等确认 |

