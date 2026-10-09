---
name: acpxtodo
description: "基于 Spec 和 Tickets 用 acpx 派发多 agent 实现：worktree 波次并发、候补链降级、分级测试与合并闭环。"
tags: [user]
disable-model-invocation: true
---

基于当前 Spec、ADR 和 Tickets 执行实现工作。**派发 prompt 一律从 `templates/` 填模板产出**（实现票 / 运行票 / 全量测试票三张），不得凭记忆重写——漏段就是漏规则。

## 路由判据（派发前第一件事）

准备派发实现任务时先判规模，别因会话惯性默认本技能（2026-10-09 t07r 教训：单票修复误走本技能，worktree 里 GitNexus 不可用）：

- **长程复杂任务**（多切片强依赖、需要波次并发、含真实运行票）→ 本技能（/acpxtodo，worktree 波次闭环）。
- **中等任务**（单票或少量弱依赖票，一个会话能可靠吃完）→ 建议用户走 `/acp_gitnexus` 快速闭环：主检出一站派发，GitNexus 流水线下放执行者。
- 判不清 → 问用户，不硬选。

## Agent 分发

使用 `/acpx` 派发。实现 Agent 由用户指定，可作为参数传入：

```text
/acpxtodo kimi
/acpxtodo kimi 1-5 codex 6-7
/acpxtodo dsh->kimi->codex
```

第一种表示全部 Tickets 依次交给 `kimi`；第二种表示 Tickets 1–5 给 `kimi`，6–7 给 `codex`；第三种表示先交给 `dsh` 完成，dsh 报错 kimi 候补，kimi 出问题 codex 候补。

Agent 选择规则：

1. 用户明确指定 → 用用户指定（含票号段与候补链参数形式）；
2. 用户未指定 → **按路由表选**：查票面 `**类型/难度：**` 字段对照下表；运行票除外；
3. 真实运行票一律默认 `codex`，派发命令带 `--model gpt-6-luna`；
4. 路由表查不到匹配（类型不在表内、难度存疑）→ 必须询问，不得自行选择。

### 派发路由表

票类型×难度 → 首选 agent。agent 能力依据见 `/acpx` 的「能力对照表」；表按实测迭代，用错就改表。

| 票类型 | 轻 | 重 |
|---|---|---|
| bug-fix | omp | omp（失败降 kimi） |
| refactor | omp | 询问用户 |
| feature | omp | kimi |
| perf | codex | codex |
| docs / chore | kimi | kimi |
| 运行票（任何类型） | codex | 同左 |

候补链 `omp -> kimi -> dsh` 只处理「首选 agent 不可用」：agent 额度耗尽、不可用、启动/执行失败时才降级；代码有 bug、测试失败或 Review 发现问题不属于 Agent 不可用，应继续本票修复。**路由表未命中 ≠ 候补链触发条件**——类型不在表内、难度存疑时按上面第 4 条询问用户。额度撞限降级协议见 `references/recovery.md`。

`kimi,omp,dsh` 都原生支持 acp 协议：`acpx` + `--agent 'kimi acp'` / `--agent 'omp acp'` / `--agent 'dsh --profile acp'` + `exec`。`codex` 是 acpx 内置 agent，`acpx codex exec`。

## Worktree 并发闭环（默认模式）

默认按**波次并发**执行：每张就绪票一个独立 git worktree，多票同时在飞，合并回主干时才串行。

每张票的核心循环（走完才闭环）：

```text
派发实现（/tdd，只跑目标测试）→ gitnexus-impact-analysis → jev-code-review
→ 编排者 commit → 按分级派测试（仅全量票）→ 绿 → 维护票面/文档 → 合并回主干
```

### 调度

1. 从票面 blocking edges 建依赖图（无票面边时按 ticket 编号 + Spec 的接口依赖人工判边，判不清就问用户，不猜）。票面由 split-tickets 产出，两技能的契约就是四个字段：**阻塞边**（本节调度输入）、**类型/难度**（派发路由与原则注入输入）、**改动范围**（合并冲突预测输入）、**运行预算**（实现票 `目标测试约 X 分钟/轮，预期 Y 轮`；写 `含 N 次真实运行` 的为运行票）。
2. **本波就绪集** = 所有前置票已合并的票。就绪集内所有票同时派发，不等彼此。
3. 每张就绪票在派发前建独立 worktree（在仓库根执行）：

```bash
git worktree add .worktrees/tNN -b ticket/tNN
```

worktree 从当前 main HEAD 建立，工作树天然干净——**基线即 worktree HEAD，status 恒空**，不需要派发前记 `git status` 基线。`.worktrees/` 不在 .gitignore 就先补一行。**建树前先提交派发依赖的全部文件**（prompt、票面、ADR、prompt 引用的任何文件）——worktree 基线取的是 HEAD，晚提交的文件在树里看不见。建树后自检：`.worktrees/tNN/` 下逐个确认依赖文件在场，缺一个就补提交重建。

4. 并发度默认 ≤4 票同时在飞；一个派发 tab 最多 8 pane（acpx 规则），满了开 `<adr>-2` tab。
5. **运行票（含真实运行）默认串行**，不与其他运行票并发——pueue 队列和机器算力会互相拖慢，benchmark 计时互相污染。用户明确要求才并行运行票。
6. 每波全部票合并回主干后，重算就绪集进入下一波，直到所有票合并。

### 派发

每票 `/acpx` 派发，`--cwd` 指向该票的 worktree，每票独立 pane、prompt 文件、日志、watcher。**命令形式按 agent 二分**（对 overlay agent 用内置形式会卡 initialize 或静默 exit 0）：

```bash
# 内置 agent（codex）：位置参数形式；运行票必须带 --model gpt-6-luna
herdr pane run <pane-id> "env -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy -u ALL_PROXY -u all_proxy acpx --cwd <repo根>/.worktrees/tNN --approve-all --ttl 60 --model gpt-6-luna codex exec -f prompts/tNN.md 2>&1 | tee .agent-results/codex-tNN.log"

# overlay agent（omp/kimi/dsh 等）：必须 --agent '主命令' 形式，不再带位置 agent 名
herdr pane run <pane-id> "env -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy -u ALL_PROXY -u all_proxy acpx --cwd <repo根>/.worktrees/tNN --approve-all --ttl 60 --agent 'omp acp' exec -f prompts/tNN.md 2>&1 | tee .agent-results/omp-tNN.log"
```

剥代理 `env -u …` 是固定前缀：bili 往 pane 注入假 HTTPS_PROXY（动态端口），不剥会卡 initialize。`tee` 必须内嵌在 pane 命令里——外层重定向捕获的是 `pane run` 自身的空流，日志永远 0 字节。

**Prompt 按模板填写**，写入 `prompts/tNN.md` 后再派发：实现票 → `templates/prompt-implement.md`；运行票 → `templates/prompt-run.md`；全量测试票 → `templates/prompt-test.md`。

派发前验证 pane 存活、派发同一步布 watcher——要点见下节。

### 单票闭环（在 worktree 内完成）

每票独立走完闭环，互相不阻塞：

确认票无误 → `/acpx` 派发进 worktree → agent 按 `/tdd` 完成（只跑目标测试，不跑全量）→ 编排者在 worktree 内审 diff（`git -C .worktrees/tNN diff` 对照 worktree HEAD）→ 按 `/jev-code-review` 评审 → 有修复则修复后重验受影响部分 → 编排者在 `ticket/tNN` 分支上 commit（有修复才提交第二次 commit，不创建空 commit）→ **按测试分级派测试 agent（全量票跑全量，目标票不跑）** → 绿后维护票面与相关文档（勾选验收项、handoff、受影响的 ADR）→ 进合并回主干。

纯文档 / 纯 tracker / 纯 markdown 提交（staged diff 无代码路径）可豁免评审轮；豁免必须在 commit message 或会话记录中显式声明，不得静默跳过。

评审请求一律从上一票已通过的请求文件复制改写（留档 `.agent-results/tNN-review.json`），只换 state、证据和问题内容，形状与字段照抄。请求字段契约见仓库 `VERIFY_RULES.md`。

如果 Spec、ADR、Ticket 存在无法解释的实质冲突，停止本票并报告，不得自行改写设计。

### 合并回主干（串行点）

并发只隔离写冲突，**合并必须按依赖顺序逐票串行**，在主检出执行：

```bash
git merge --no-ff ticket/tNN
```

- 合并顺序 = 依赖边的拓扑序；无边的票按编号序。
- 两票改了同一文件且语义相交 → 冲突在 merge-back 暴露，这是本模式的预期行为，不是事故。编排者按 `/pstack:fix-merge-conflicts` 解决冲突（最小正确编辑，优先保双方，不留冲突标记，解决期间不 push 不 tag）；解决涉及语义判断时派回该票 agent 复核，冲突解决后的受影响部分重新验证。
- 合并完成后清理：`git worktree remove .worktrees/tNN && git branch -d ticket/tNN`。有未提交残留先审计保留，不静默丢弃。
- 合并后本票才算闭环，其下游票才进入就绪集。

### 串行回退

仅两种情况退回逐票串行（旧模式）：用户明确要求；仓库不适合 worktree（非 git 项目、单分支强制等）。串行时每票新开 `/acpx` 会话，上一票闭环前不派下一票。

## Headless 派发要点

- 派发 Prompt 写入文件后后台启动，日志写入文件。**不设 `--timeout`**——总时限会杀死仍在健康工作的 agent；`--ttl` 的语义是「任务结束后 acpx 进程空闲多久才退出」，不限制运行中的任务，长票不需要调大。
- **派发前先验证 pane 存活**：票与票之间 pane 会被回收，`herdr pane get <pane-id>` 确认存活后才发命令；不存在就先 `herdr tab create` 重建取新 pane_id。
- **派发的同一步里立即布完成 watcher**（`run_in_background`，长超时，盯日志直到完成判据命中）。launcher 退出只代表命令已送进 pane，不代表任务完成。
- **完成判据 = `[done] end_turn` 且日志尾部无 `AccountQuotaExceeded`，`RUNTIME:` 不作判据**；匹配窗口用 `tail -20`（全日志匹配会撞历史行）。
- 命中异常——额度撞限、静默死亡、进程死活存疑、中断续作——先读 `references/recovery.md` 再动作。

## 测试分级（实现票 / 全量票 / 运行票分离）

实现 agent 全程不跑全量测试——全量不属于任何票，由编排者单独派发。三类票严格分离：

| 票类 | 全量测试 | 处理 |
|---|---|---|
| 目标票 | 不跑 | 评审通过直接进合并；风险由目标测试、评审轮和合并波定向核验兜底 |
| 全量票 | 单独派测试 agent（`templates/prompt-test.md`） | 时机：评审通过、编排者 commit 之后、合并之前；绿后进合并 |
| 运行票 | 不在此列 | 按 `templates/prompt-run.md` 派发，真实运行进 pueue |

分级判据（GitNexus 影响面分析 + 票面「改动范围」判）：改动跨模块、动共享接口/配置/公共常量、或被多个下游票依赖 → **全量票**；影响面封闭在本模块内（调用方全在本模块内）→ **目标票**。判不清一律按全量票处理，分级结论记入决策日志 close 行。

全量票有失败 → 把失败测试清单派回实现 agent 修复（新派发，编排者不代写），修复后重跑全量。环境对齐、长套件 pueue、退出码直取的执行细节在 `templates/prompt-test.md` 固定段。

## 决策日志

开跑时建 `.scratch/<feature>/decisions.tsv`（跟 feature 走，随票目录归档，不落 /tmp）。格式沿用 pstack show-me-your-work：TSV 一决策一行，列 `ts / phase / decision / why / evidence / result`，evidence 必须是指针（commit SHA、`file:line`、日志路径）不是段落，append-only，错了用新行 supersede 不改历史。

必记的决策行（phase 标注）：

- `start`：开跑，记录 Spec/ADR 来源与拆票总数——每个 run 的第一行；
- `dispatch`：每票派发一行——为什么选这个 agent（路由表命中 / 用户指定 / 候补链降级）；
- `close`：每票闭环一行——评审结论与证据指针；
- `merge`：每波合并一行——冲突与解决方式（有冲突时）；
- `accept`：最终验收一行——整体核验结果。

这份日志是"为什么这么做"的档案：票面和 commit 记录做了什么，决策日志补上理由。**结果类行（close/accept）必须带结果证据才落行**——命令还在跑时不写"顺利"语气的行；运行中状态单独记，结论等证据。

## 事实核验

不要因为实现 Agent 声称完成、测试通过或 Review 无报错，就直接认定 Ticket 正确。至少抽查关键 diff、Ticket 验收项、Agent 声称的关键测试/运行结果；必要时检查 Spec、ADR、日志、测试、生成物和 handoff。自述与盘上证据冲突时，以盘上证据为准。

编排者无法跑 `git diff` / `git show` 时（worktree 守卫拦截），关键 diff 以「直读文件 + 对照建树时的 HEAD 基线」替代。

实现 Agent 负责把定向目标测试和 `pnpm run check` 或项目等价快速检查跑绿；全量测试套件不在其职责内。编排者默认不重复跑完整 check；只有结果可疑、发生修复、缺少验收证据或 Ticket 明确要求时才定向复跑。

**合并后核验**：单票在 worktree 里测试通过，不代表合并进主干后仍通过——其他票的改动可能与它相互作用。每波合并完成后对合并集做一次定向核验（跑测试或 check），失败则定位到引入票派回修复。

## 最终验收

全部 Tickets 完成并合并后，再从整体 Spec 和 ADR 检查一次：

```text
局部 Tickets 全部完成
≠
整个任务一定完成
```

必须确认各 Ticket 组合后真正实现了整体目标、接口闭合且最终实际路径成立。不得用 `completed` 状态代替最终事实验证。
