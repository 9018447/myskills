---
name: acpxtodo
description: "基于 spec 或一组 tickets 通过acpx派发实现大范围的工作内容。"
tags: [user]
disable-model-invocation: true
---

基于当前 Spec、ADR 和 Tickets 执行实现工作。

## Agent 分发

使用 `/acpx` 派发。实现 Agent 由用户指定，可作为参数传入：

```text
/acpxtodo kimi
/acpxtodo kimi 1-5 codex 6-7
/acpxtodo dsh->kimi->codex
```

第一种表示全部 Tickets 依次交给 `kimi`；第二种表示 Tickets 1–5 给 `kimi`，6–7 给 `codex`。 第三种表示先交给`dsh`完成,dsh报错kimi候补,kimi出问题codex候补

Agent 选择规则：

1. 用户明确指定 → 用用户指定（含票号段与候补链参数形式）；
2. 用户未指定 → **按路由表选**：查票面 `**类型/难度：**` 字段对照下表；运行票除外；
3. 真实运行票一律默认 `codex`, `model` 指定`gpt-6-luna`；
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
| 运行票（任何类型） | codex + `gpt-6-luna` | 同左 |

路由表未命中时回落**候补链** `omp -> kimi -> dsh`。路由表只决定首选，不改变候补链语义：agent 额度耗尽、不可用、启动/执行失败时才降级；代码有 bug、测试失败或 Review 发现问题不属于 Agent 不可用，应继续本票修复。

`kimi,omp,dsh`都原生支持acp协议, acpx派发用`acpx` + `kimi acp` `omp acp` `dsh --profile acp`  + `exec`
 
`codex`是acpx的内置agent , `acpx codex exec`

当前候补链：

```text
omp -> kimi -> dsh
```

## Worktree 并发闭环（默认模式）

Tickets 不再逐票串行。默认按**波次并发**执行：每张就绪票一个独立 git worktree，多票同时在飞，合并回主干时才串行。

### 调度

1. 从票面 blocking edges 建依赖图（无票面边时按 ticket 编号 + Spec 的接口依赖人工判边，判不清就问用户，不猜）。票面由 split-tickets 产出，两技能的契约就是四个字段：**阻塞边**（本节调度输入）、**类型/难度**（派发路由与原则注入输入）、**改动范围**（合并冲突预测输入）、**运行预算**（实现票 `目标测试约 X 分钟/轮，预期 Y 轮`；写 `含 N 次真实运行` 的为运行票，识别与派发见运行票派发）。
2. **本波就绪集** = 所有前置票已合并的票。就绪集内所有票同时派发，不等彼此。
3. 每张就绪票在派发前建独立 worktree（在仓库根执行）：

```bash
git worktree add .worktrees/tNN -b ticket/tNN
```

worktree 从当前 main HEAD 建立，工作树天然干净——**基线即 worktree HEAD，status 恒空**，不再需要派发前记 `git status` 基线（串行模式曾因推断基线漏掉 39 个已删跟踪文件，此模式从根上消除该风险）。`.worktrees/` 不在 .gitignore 就先补一行。

4. 并发度默认 ≤4 票同时在飞；一个派发 tab 最多 8 pane（acpx 规则），满了开 `<adr>-2` tab。
5. **运行票（含真实运行）默认串行**，不与其他运行票并发——pueue 队列和机器算力会互相拖慢，benchmark 计时互相污染。用户明确要求才并行运行票。
6. 每波全部票合并回主干后，重算就绪集进入下一波，直到所有票合并。

### 派发

每票 `/acpx` 派发，`--cwd` 指向该票的 worktree，每票独立 pane、prompt 文件、日志、watcher：

```bash
herdr pane run <pane-id> "acpx --cwd <repo根>/.worktrees/tNN --approve-all --ttl 60 <agent> exec -f prompts/tNN.md 2>&1 | tee .agent-results/<agentname>-tNN.log"
```

派发 Prompt 必须告诉实现 Agent：

1. 整个任务的目标和当前主要矛盾；
2. 当前 Ticket 对解决主要矛盾的作用；
3. **其工作目录是独立 worktree `.worktrees/tNN`，分支 `ticket/tNN`，只在该目录内工作**；
4. 遵守当前 Spec、ADR 和 Ticket 范围；使用 `/tdd` 完成实现；
5. **全程不跑全量测试套件**（如 `Pkg.test` 整套），一次也不跑——全量由编排者在本票闭环后单独派发测试 agent；只跑与改动直接相关的目标测试（单个 testset 或测试文件），"没改坏别处"由 `/gitnexus-impact-analysis` + `/jev-code-review` 判定（2026-10-08 定案：实现 agent 在调试循环里反复跑全量是票拖到一小时以上的主因）；
6. 不扩大范围，不做无关重构和过度设计；
7. 不得再次使用 `/acpx` 或 `subagent` 向下派发；
8. 不跑 code-review（`@../open-code-review-delegate/`、`ocr` `/code-review` 命令都不执行）——评审轮由编排者在其完成后进行；
9. **不提交 git**（提交由编排者在本票分支上完成）；
10. 提示词中的文件路径必须先在盘上验证存在（ls/grep）；验证不了就让实现 agent 自行定位，不得断言未验证的路径（2026-09-26 票 22 提示词写错 CLI 路径，靠 agent 自行 glob 纠正）；
11. **工作原则**：按票面类型对照下面的原则映射表，把命中原则的中文提炼段写入 prompt 末尾「工作原则」小节（每条一两句，不贴原文全文）；
12. **文风**：prompt 末尾附文风要求段——「输出与代码注释用中文；每句有主语和因果，写清楚谁在做什么、为什么；术语第一次出现时带一句它在当前问题里的实际作用；不用只有作者自己懂的缩写和指代；结论后面跟原因；不把背景、原因、判断挤进一句话」。

其余 headless 规则（pane 存活预检、派发同一步布 watcher、`[done] end_turn` 完成判据、候补链降级、续作分工）按下文 Headless 派发与 `/acpx` skill 执行，对 worktree 模式同样适用——只是每个对象都带票号：`prompts/tNN.md`、`.agent-results/<agent>-tNN.log`、`herdr pane get <该票pane>`。

### 工作原则注入（票类型 → 原则提炼段）

派发 prompt 第 11 条的映射表。提炼段自持中文，不回写 pstack 的 principle 技能原文（`presets/stack/` 下，英文原文按需深读）。全类型必带三条 + 按类型追加：

| 票类型 | 追加原则（提炼段写入 prompt） |
|---|---|
| 全类型 | **test-behavior-not-implementation**：测试对行为断言（输入→输出），不对实现细节断言（内部调用顺序、私有结构）；**prove-it-works**：完工的判据是证据（测试输出、运行结果），不是"应该没问题"；**minimize-reader-load**：代码和注释写给下一个读的人，命名直白、路径写全、不省中间步骤 |
| bug-fix | **fix-root-causes**：先问 why 到根因，不打补丁掩盖症状；**attack-the-premise**：同类修复连续失败两次，先检验共同假设，不再试第三次 |
| refactor | **migrate-callers-then-delete-legacy-apis**：先迁走所有调用方，再删旧接口，两步分开验证；**subtract-before-you-add**：先想能不能删代码解决问题，再想加代码 |
| feature | **sequence-verifiable-units**：把工作排成一串可独立验证的小单元，每步都能确认对错再前进 |
| perf | **explain-the-number**：每个优化前后数字都要有解释，解释不了的收益当作不存在 |
| 并发/共享状态类（任何类型票涉及） | **separate-before-serializing-shared-state**：先分清状态归属再上锁；**make-operations-idempotent**：操作做成可重复执行，重试和中断不产生副作用 |

如果 Spec、ADR、Ticket 存在无法解释的实质冲突，停止本票并报告，不得自行改写设计。

### 单票闭环（在 worktree 内完成）

每票独立走完闭环，互相不阻塞：

确认票无误 → `/acpx` 派发进 worktree → agent 按 `/tdd` 完成（只跑目标测试，不跑全量）→ 编排者在 worktree 内审 diff（`git -C .worktrees/tNN diff` 对照 worktree HEAD）→ 按 `/jev-code-review` 评审 → 有修复则修复后重验受影响部分 → 编排者在 `ticket/tNN` 分支上 commit（有修复才提交第二次 commit，不创建空 commit）→ **按测试分级派测试 agent（见测试派发：全量票跑全量，目标票不跑全量）** → 绿后维护票面与相关文档（勾选验收项、handoff、受影响的 ADR）→ 进合并回主干。

纯文档 / 纯 tracker / 纯 markdown 提交（staged diff 无代码路径）可豁免评审轮；豁免必须在 commit message 或会话记录中显式声明，不得静默跳过。

评审请求一律从上一票已通过的请求文件复制改写（留档 `.agent-results/tNN-review.json`），只换 state、证据和问题内容，形状与字段照抄——手搓重建形状会连翻数轮（2026-10-08 t02：`model:"default"` 占位键被 OpenRouter 400，删键后才通过）。请求字段契约见仓库 `VERIFY_RULES.md`。

### 合并回主干（串行点）

并发只隔离写冲突，**合并必须按依赖顺序逐票串行**，在主检出执行：

```bash
git merge --no-ff ticket/tNN
```

* 合并顺序 = 依赖边的拓扑序；无边的票按编号序。
* 两票改了同一文件且语义相交 → 冲突在 merge-back 暴露，这是本模式的预期行为，不是事故。编排者按 `/pstack:fix-merge-conflicts` 解决冲突（最小正确编辑，优先保双方，不留冲突标记，解决期间不 push 不 tag）；解决涉及语义判断（不是机械合并）时派回该票 agent 复核，冲突解决后的受影响部分重新验证。
* 合并完成后清理：`git worktree remove .worktrees/tNN && git branch -d ticket/tNN`。有未提交残留先审计保留，不静默丢弃。
* 合并后本票才算闭环，其下游票才进入就绪集。

### 串行回退

仅两种情况退回逐票串行（旧模式）：用户明确要求；仓库不适合 worktree（非 git 项目、单分支强制等）。串行时沿用旧规则：每票新开 `/acpx` 会话，上一票闭环前不派下一票。

## Headless 派发

按 `/acpx` headless dispatch pattern 执行：

* 派发 Prompt 写入文件后后台启动，日志写入文件；
* **不设 `--timeout`**（总时限会杀死仍在健康工作的 agent——2026-09-30 票 04 codex 即被
  4h 总时限截断）。会话活性由 `--ttl`（空闲时限，默认 300s，长票传 1800+）与日志监视兜底；
* 不阻塞轮询，只通过任务完成通知或日志中的 `[done] end_turn` 判断结束；
* **派发前先验证 pane 存活**：`herdr pane get <pane-id>` 或 `herdr pane list`。票与票之间 pane 会被回收（agent 会话结束后 pane 随之消失）——2026-10-05 票 T1 结束后 `w1E:p26` 即被回收，向它派发 T3 直接 `pane_not_found`，浪费一次派发。pane 不存在时先 `herdr tab create` 重建（同 label 则复用标签新建 tab），拿到新 pane-id 再派发，不得把命令发进未验证的 pane；
* **派发的同一步里立即布完成 watcher**：一个后台 shell（`run_in_background`，长超时）盯日志直到 `[done] end_turn` 或错误标记出现。launcher（herdr pane run 包装）退出只代表命令已送进 pane，不代表任务完成——2026-10-05 票 T1/T2 都是用户追问"后台 shell 呢"之后才补的 watcher，属反应式补漏，以后派发与布 watcher 必须同一步完成；
* **完成判据 = `[done] end_turn` 且日志尾部无错误块**：`AccountQuotaExceeded`、`RUNTIME:`、`error` 等出现时标记是假完成——agent 视为不可用，按候补链降级重派，并先审计盘上现状保留成果（半成品不是交付）；
* 查看进度仅短暂读取日志；
* `[done] end_turn` 后若包装进程仍存在，用已记录 PID 经 `ps -p <pid>` 确认后清理，不用 `pgrep -f`。
* 进程存活核查一律用 `pgrep -fa 'patter[n]'`（尾字符加括号防自匹配）或直读 `/proc/<pid>/cmdline`；本环境 `ps` 输出可能被 rtk 包装丢 CMD 列，禁止 `ps aux | grep` 判存活——2026-09-18 曾因此误判存活进程已死。

任务中断后续作时，先审计盘上现状（含各 worktree 的分支状态），保留符合 Ticket 的已有成果，再补完剩余验收，不得默认推倒重来。handoff 中记录中断和续作事实。

**续作分工（2026-09-30 票 04 定案）**：预算耗尽/中断后的续作，编排者只做审计、
环境排障、冻结成果清点；票内实现、长计算、数据回填、提交一律通过**新的派发**回到
实现 agent。编排者不得以"上下文在手"为由自行实现——2026-09-30 票 04 编排者接手
实现与计算后被用户纠正。

### 运行票派发

票面标注 `含 N 次真实运行` 或预计真实运行总时长 ≥20 分钟 → 默认 `codex`, `model` 指定`gpt-6-luna`； 

* 派发运行票时 prompts 必须告诉实现 agent（默认 codex gpt-6-luna）用 `/pueue` skill 执行**票内真实运行任务**——运行任务进 pueue 后台跑，agent 进程被杀/会话中断不会连坐运行任务（这是 pueue 的设计用途，勿用 run_in_background 替代）。pueue 可能不在 agent shell 的 PATH 里——用 `which pueue` 定位（通常 `~/.cargo/bin/pueue`），拿到路径即可用。
* 边界（2026-09-27 定案）：进 pueue 的是**运行任务**（julia 跑 benchmark、批量求解等），不是 **agent 进程本身**——pi/交互式 agent 在 pueue 环境下启动会静默卡死；agent 的派发走 `/acpx`，两者不可混。
* 运行票默认与其他运行票串行（见 Worktree 并发闭环·调度第 5 条）。

### 测试派发（按票分级）

实现 agent 全程不跑全量测试（派发 Prompt 第 5 条）——全量测试不属于任何票，由编排者单独派发。派发前先按影响面分级，不是每张实现票都付全量成本：

* **分级判据**（用 GitNexus 影响面分析 + 票面「改动范围」判）：改动跨模块、动共享接口/配置/公共常量、或被多个下游票依赖 → **全量票**；影响面封闭在本模块内（调用方全在本模块内）→ **目标票**，不跑全量，风险由目标测试、评审轮和合并波定向核验兜底。判不清一律按全量票处理，分级结论记入决策日志 close 行。
* **时机**：全量票——实现票完成评审、编排者 commit 之后，合并回主干之前；目标票——无全量派发，评审通过直接进合并回主干。
* **派法**：向该票 worktree（`.worktrees/tNN`）派发一个 codex 测试 agent（headless 规则同上，prompt/日志/watcher 带票号），任务只有一件——跑一次全量测试套件，产出带失败清单的报告；
* **长套件**（单轮 ≥20 分钟）：prompt 要求测试 agent 用 `/pueue` 执行全量运行（规则同运行票）；
* **全绿** → 进合并回主干；**有失败** → 把失败测试清单派回实现 agent 修复（新派发，编排者不代写），修复后重跑全量；
* 运行票的真实运行任务不在此列，仍按运行票派发执行。

## 决策日志

开跑时建 `.scratch/<feature>/decisions.tsv`（跟 feature 走，随票目录归档，不落 /tmp——/tmp 的交接文档链会丢）。格式沿用 pstack show-me-your-work：TSV 一决策一行，列 `ts / phase / decision / why / evidence / result`，evidence 必须是指针（commit SHA、`file:line`、日志路径）不是段落，append-only，错了用新行 supersede 不改历史。

必记的决策行（phase 标注）：

* `start`：开跑，记录 Spec/ADR 来源与拆票总数——每个 run 的第一行；
* `dispatch`：每票派发一行——为什么选这个 agent（路由表命中 / 用户指定 / 候补链降级）；
* `close`：每票闭环一行——评审结论与证据指针；
* `merge`：每波合并一行——冲突与解决方式（有冲突时）；
* `accept`：最终验收一行——整体核验结果。

这一份日志是"为什么这么做"的档案：票面和 commit 记录做了什么，决策日志补上理由，事后审计直接读它，不再考古对话。

## 事实核验

不要因为实现 Agent 声称完成、测试通过或 Review 无报错，就直接认定 Ticket 正确。

至少抽查：

```text
关键 diff
Ticket 验收项
Agent 声称的关键测试/运行结果
```

必要时检查 Spec、ADR、日志、测试、生成物和 handoff。自述与盘上证据冲突时，以盘上证据为准。

编排者无法跑 `git diff` / `git show` 时（worktree 守卫拦截），关键 diff 以「直读文件 + 对照派发前记录的基线」替代——worktree 模式下基线即建树时的 HEAD（见 Worktree 并发闭环·调度）。

实现 Agent 负责把定向目标测试和 `pnpm run check` 或项目等价快速检查跑绿；全量测试套件不在其职责内（见测试派发）。编排者默认不重复跑完整 check；只有结果可疑、发生修复、缺少验收证据或 Ticket 明确要求时才定向复跑。

**合并后核验（本模式新增）**：单票在 worktree 里测试通过，不代表合并进主干后仍通过——其他票的改动可能与它相互作用。每波合并完成后对合并集做一次定向核验（跑测试或 check），失败则定位到引入票派回修复。

## 最终验收

全部 Tickets 完成并合并后，再从整体 Spec 和 ADR 检查一次：

```text
局部 Tickets 全部完成
≠
整个任务一定完成
```

必须确认各 Ticket 组合后真正实现了整体目标、接口闭合且最终实际路径成立。不得用 `completed` 状态代替最终事实验证。
