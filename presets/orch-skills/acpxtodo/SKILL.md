---
name: acpxtodo
description: "基于 spec 或一组 tickets 通过acpx派发实现大范围的工作内容。"
tags: [user]
disable-model-invocation: true
---

基于当前 Spec、ADR 和 Tickets 执行实现工作。

## 方法论

* **实事求是**：以 Spec、ADR、代码、测试、日志和实际运行结果为准，不迷信 Agent 或 Review 的文字结论。
* **调查研究**：事实不清先查代码、日志、测试和历史设计，不凭经验补全。
* **具体问题具体分析**：结合当前 Ticket、代码状态和实际约束判断，不机械套模板。
* **抓主要矛盾**：每票都要明确它解决什么核心瓶颈；不能推动主要矛盾的工作不要因为“更完整”而增加。
* **实践检验**：正确性最终由测试和真实运行验证，优先采用成本最低但有判别力的实验。
* **从实际需求出发**：以真实目标而不是代码量、复杂架构或形式完整性判断价值。

## Agent 分发

使用 `/acpx` 逐票分发。实现 Agent 由用户指定，可作为参数传入：

```text
/acpxtodo kimi
/acpxtodo kimi 1-5 codex 6-7
/acpxtodo dsh->kimi->codex
```

第一种表示全部 Tickets 依次交给 `kimi`；第二种表示 Tickets 1–5 给 `kimi`，6–7 给 `codex`。 第三种表示先交给`dsh`完成,dsh报错kimi候补,kimi出问题codex候补

Agent 选择规则：

1. 用户明确指定 → 离线票使用用户指定；
2. 真实运行票一律默认 `codex`, `model` 指定`gpt-6-luna`；
3. 其他情况用户未指定 → 必须询问，不得自行选择。

当前 Agent 只有在额度耗尽、不可用、启动/执行失败时才进入候补链。代码有 bug、测试失败或 Review 发现问题不属于 Agent 不可用，应继续本票修复。

```text
omp -> kimi -> dsh
```


## 一票一闭环

Tickets 原则上依次执行。每个 Ticket 单独开启一个新的 `/acpx` 会话，不得多票共用一个会话。

当前 Ticket 未完成闭环，不得派发下一 Ticket。

派发前记录当前 `HEAD` 和 `git status --short`，用于区分本票改动与已有未提交内容。不得顺手提交无关改动。基线 status 拿不到时（工具被拦、无权限），显式记录"status 未知"，并请用户或实现 agent 补一次真实 status——不得以"刚提交过所以干净"推断（2026-09-26 曾因推断基线漏掉 39 个已删跟踪文件）。

派发 Prompt 必须告诉实现 Agent：

1. 整个任务的目标和当前主要矛盾；
2. 当前 Ticket 对解决主要矛盾的作用；
3. 遵守当前 Spec、ADR 和 Ticket 范围；
4. 使用 `/tdd` 完成实现；
5. 不扩大范围，不做无关重构和过度设计；
7. 不得再次使用 `/acpx` 或 `subagent` 向下派发；
8. 不跑 code-review（`@../open-code-review-delegate/`、`ocr` `/code-review` 命令都不执行）——评审轮由编排者在其提交后进行；
9. 不提交git
9. 提示词中的文件路径必须先在盘上验证存在（ls/grep）；验证不了就让实现 agent 自行定位，不得断言未验证的路径（2026-09-26 票 22 提示词写错 CLI 路径，靠 agent 自行 glob 纠正）。

如果 Spec、ADR、Ticket 存在无法解释的实质冲突，停止本票并报告，不得自行改写设计。

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

任务中断后续作时，先审计盘上现状，保留符合 Ticket 的已有成果，再补完剩余验收，不得默认推倒重来。handoff 中记录中断和续作事实。

**续作分工（2026-09-30 票 04 定案）**：预算耗尽/中断后的续作，编排者只做审计、
环境排障、冻结成果清点；票内实现、长计算、数据回填、提交一律通过**新的派发**回到
实现 agent。编排者不得以"上下文在手"为由自行实现——2026-09-30 票 04 编排者接手
实现与计算后被用户纠正。

### 运行票派发

票面标注 `含 N 次真实运行` 或预计真实运行总时长 ≥20 分钟 → 默认 `codex`, `model` 指定`gpt-6-luna`； 

* 派发运行票时 prompts 必须告诉实现 agent（默认 codex gpt-6-luna）用 `/pueue` skill 执行**票内真实运行任务**——运行任务进 pueue 后台跑，agent 进程被杀/会话中断不会连坐运行任务（这是 pueue 的设计用途，勿用 run_in_background 替代）。pueue 可能不在 agent shell 的 PATH 里——用 `which pueue` 定位（通常 `~/.cargo/bin/pueue`），拿到路径即可用。
* 边界（2026-09-27 定案）：进 pueue 的是**运行任务**（julia 跑 benchmark、批量求解等），不是 **agent 进程本身**——pi/交互式 agent 在 pueue 环境下启动会静默卡死；agent 的派发走 `/acpx`，两者不可混。


## 固定闭环

每票严格按以下顺序编排：

确认票无误-> `/acpx` 派发-> `workeragent` 按照`/tdd` 完成 ->  按`/jev-code-review` 进行code-review -> 按`/pstack:technical-writing` 维护票面和文档信息 -> `git commit` -> 派发下一票 -> 所有票已经完成: `/open-code-review-delegate` 选取本次闭环的commit进行总code-review

纯文档 / 纯 tracker / 纯 markdown 提交（staged diff 无代码路径）可豁免评审轮；豁免必须在 commit message 或会话记录中显式声明，不得静默跳过。

评审请求一律从上一票已通过的请求文件复制改写（留档 `.agent-results/tNN-review.json`），只换 state、证据和问题内容，形状与字段照抄——手搓重建形状会连翻数轮（2026-10-08 t02：`model:"default"` 占位键被 OpenRouter 400，删键后才通过）。请求字段细节以 `jev` skill 的 API 文档为准。

修复后重新验证受影响部分。有修复才提交第二次 commit，不创建空 commit。


## 事实核验

不要因为实现 Agent 声称完成、测试通过或 Review 无报错，就直接认定 Ticket 正确。

至少抽查：

```text
关键 diff
Ticket 验收项
Agent 声称的关键测试/运行结果
```

必要时检查 Spec、ADR、日志、测试、生成物和 handoff。自述与盘上证据冲突时，以盘上证据为准。

编排者无法跑 `git diff` / `git show` 时（worktree 守卫拦截），关键 diff 以「直读文件 + 对照派发前记录的基线」替代——前提是基线已在派发前记录（见一票一闭环的基线条款）。

实现 Agent 负责把 `pnpm run check` 或项目等价检查跑绿。编排者默认不重复跑完整 check；只有结果可疑、发生修复、缺少验收证据或 Ticket 明确要求时才定向复跑。



## 最终验收

全部 Tickets 完成后，再从整体 Spec 和 ADR 检查一次：

```text
局部 Tickets 全部完成
≠
整个任务一定完成
```

必须确认各 Ticket 组合后真正实现了整体目标、接口闭合且最终实际路径成立。不得用 `completed` 状态代替最终事实验证。

