---
name: implement
description: "基于 spec 或一组 tickets 实现工作内容。"
tags: [user]
disable-model-invocation: true
---

基于当前 Spec、ADR 和 Tickets 执行实现工作。实现代码仍由 acpx→外部实现 agent 完成；
编排、判断、评审与验收改由**确定性驱动脚本 + Jev 判断门 + GitNexus 结构证据**负责。

## 驱动入口

```text
implement.sh check  [--repo R]              前置检查，先跑这个
implement.sh status [--repo R] [--dry-run] [--zg]  总览所有 feature 状态；--zg 用语义索引检索实现痕迹
implement.sh list   [--repo R] [<feature>]  列出 feature 的 tickets（拓扑序 + 每票状态/标题/依赖）
implement.sh <feature> [--repo R] [--agent AGENT[:MODEL]|'A->B->C'] [--retries N]
                        [--ttl SEC] [--dry-run] [--resume] [--skip-judge]
implement.sh --help                         用法
```

**总览状态（`implement.sh status`）**：扫 `<repo>/.scratch/*/` 全部 feature，读每个的实现证据
（票数、跑过/卡住/完成的票、有无 `spec`、是否被状态文件接管），打一张确定性表格，再把这些证据
合进**一次** Jev 请求：对每个 feature 让 Jev 从离散状态里挑（从未开始 / 推进中 / 中途暂停 /
接近完成 / 已完成待验收 / 维护中停滞），并给出"下一步优先推进哪一个"的整体建议。低置信或
`needs_review` 的 feature（比如有 `review_pack` 卡住）会主动标出来让你人工再判，不武断替你做决定。

为了判断"该 feature 到底实现到哪了"，status 会用 zg 检索代码里的真实实现痕迹喂给 Jev，避免只看
新驱动的状态文件（旧流程/历史仓库常一条都不写，导致 Jev 拿到空白证据误判"从未开始"）。默认走词表层
`--rg`（无需索引、随处可用）；`--zg` 则用**语义索引**——缺索引时用本地嵌入模型 `potion-code-16m-v2`
自动构建一次（首次需联网下载 16M 模型 + 磁盘），语义对自动提取的泛词（validation/loop 这类）更抗噪声，
该 feature 自己的实现文件能顶到前列，共享脚手架不再抢镜。
**坑（已经踩过）**：zg 语义查询的索引按**运行目录（cwd）**解析，不认尾随路径参数，且 `-e`/`-m` 只对
`--rg` 管用——所以语义分支必须在仓库根内 `cd` 后再调 zg，词表层仍用路径参数；`--semantic` 旧标志因把
`|` 正则串直接喂语义、又用了 rg 专属的 `-m`/行格式解析而根本跑不通，已合并进 `--zg`。

`<feature>` 对应 `<repo>/.scratch/<feature>/issues/NN-<slug>.md` 与 `spec.md`。脚本逐票执行，
把每票作为一个独立闭环：**前置检查 → 基线记录 → agent 选择 → prompt+GitNexus impact →
headless 派发 → 完成判据 → 确定性核验 → 一个 Jev 判断门 → 按值路由 → 下一票 → 整体 Jev 验收门**。

**前置检查（`implement.sh check`）**：任何真实派发前先自检，报告 `[BLOCK]`/`[WARN]` 后退出。
`[BLOCK]`（0 个才放行）包括：`jev-decide`/`herdr`/`git`/`python3` 缺失、real 运行缺
`OPENROUTER_API_KEY`/`TYPESAFE_API_KEY`、仓库不是 git、feature 目录或 tickets 不存在、多个
候选 feature 未指定。`[WARN]`（可带病）包括：`gitnexus`/`zcode-preflight.sh` 不在 PATH、
缺 `spec.md`（用 ticket 标题兜底）、拓扑有环/悬空、已有上次运行状态。`--repo` 未给时自动取
当前目录 git 根；`<feature>` 未给且 `.scratch` 下唯一子目录时自动取，多个会列出并停在 BLOCK。

- `--agent` 显式指定实现 agent（如 `codex:gpt-6-luna`、`kimi`）。未指定且非运行票时，驱动停止询问，不自行选择。也支持链式 `'A->B->C'`：按拓扑顺序给每张**真实**票（doc/跳过票不占位）分配下一个 agent，用尽后从头轮转，适合"交错的 agent 分工"。
- `list` 子命令：只读列出某 feature 的 tickets——按拓扑顺序，含每票状态（todo/done/blocked）、标题与 `Blocked by`。`<feature>` 省略时自动发现，多 feature 则列出可用项。不开前置检查（不要求 jev-decide/herdr）。
- `--dry-run` 只建 prompt/基线/证据桩，不派发真实 agent、不调 Jev，用于接线自检（也过前置检查）。
- `--skip-judge` 跑到证据步停止，不调 Jev。
- `--resume` 从 `.agent-results/.implement-state.json` 续跑。

退出码：`0` 全部通过并整体验收；`3` 停在等待人类决策；`4` dry-run 完成；`1` 出错。
`check` 子命令：`0` 就绪可跑 / `1` 有 `[BLOCK]` 项。

## 状态与产物

驱动把每票的产物写到 `<repo>/.agent-results/`：

```text
.implement-state.json        全 feature 状态（基线、done、escalated、retries）
<tid>.prompt.md              派发提示词
<tid>-evidence.json          Jev 判断门的 state（diff、handoff、gitnexus 证据、receipts）
<tid>.request.json           已合并的 jev-decide 请求
<ticket>-review-pack.md      升级停在人类时打包的证据
<tid>-gnx-{impact,detect,check}.{txt,json}   GitNexus 结构证据
```

## 一票一闭环（脚本内已编码，此处为约定）

1. **基线**：派发前记录 `HEAD` 和 `git status --short`，以区分本票改动与已有未提交内容（2026-09-26 起，绝不以"刚提交过所以干净"推断）。
2. **agent 选择**：用户指定→使用；真实运行票（`含 N 次真实运行`/预计运行时 ≥20min）→默认 `codex` `gpt-6-luna`；否则必须询问。`type: doc` 票免派发免评审（声明豁免）。
3. **派发 prompt 的 9 条**：明确目标与主要矛盾；遵守 Spec/ADR/Ticket 范围；`/tdd` 红绿；不扩范围不做过度设计；结束 `/handoff-for-mattpocock`；禁止再 `/acpx` 或 subagent；不跑 code review（评审归驱动+Jev）；显式路径 `git add` 禁止 `git add -A`；路径先盘上验证。
4. **headless**：不设 `--timeout`（总时限会杀死健康 agent，2026-09-30），用 `--ttl`（默认 300，长票 1800+）；派发前验证 pane 存活，不存在先重建；派发同一步布 watcher；完成判据 = `[done] end_turn` 且日志尾部无 `AccountQuotaExceeded|RUNTIME:|error`（假完成→walk 候补链）。zcode 派发前跑 `~/.claude/scripts/zcode-preflight.sh`，每次重新 glob。
5. **事实核验**：不因 Agent/测试/Jev 声明通过而直接认定正确；关键 diff、票验收项、声称的测试/运行结果至少抽查；自述与盘上证据冲突时以盘上为准。

## 判断门：一个 Jev 请求，按值路由

驱动把每票的证据合并成**一次** `jev-decide` 请求（completion+review+fix-routing 三模板合一，`scripts/judge.sh` 完成合并与调用），按问题**解析出的值**路由——`ask_user`/`unknown`/低置信度/未收敛才升级，`defer` 等原样推进：

```text
completion.claim_supported   ≥0.75 才采信完成声明
review.completion             supported → 通过；unsupported/unknown → 升级
review.weakens_checks / scope_breach   true → 升级
fix_routing.route             fix_now → 票内重派（≤--retries）；defer → 记录并推进；ask_user → 升级
fix_routing.resolved_all      false → 升级
```

升级 = 驱动**停下等人类**：写好 `<ticket>-review-pack.md`，退出 3。人类决断后 `--resume` 继续（改状态、换 agent、或判完成）。

## GitNexus 结构证据（LLM-free）

派发前对票面命中的符号查 `impact`，把影响面写进 prompt 并留档；agent 提交后跑 `detect-changes --scope compare -b <基线>` 与 `check --cycles`，把`风险等级`、受影响流程、新增 import 环等事实并入 Jev 的 state。证据不完整（索引未建、候选被截断、partial）时脚本标记并降级，不硬造结论。

## run 票

票面标注真实运行任务时，prompt 必须要求实现 agent 用 `/pueue` skill 把**运行任务**送后台（`which pueue` 定位），agent 进程被杀连坐不到运行任务；agent 本身的派发走 /acpx，两者不可混。

## 最终验收

全部票绿后，再跑一次**整体 Jev 验收门**（`scripts/judge.sh accept`）从整体 Spec/ADR 复核：局部 ticket 全完成 ≠ 任务完成。确认接口闭合、整体路径成立后通过。确有必要时（驱动无法自行处理）再读手头证据人工定夺。

## 方法论点（保留原 skill 的方法论底色）

实事求是（以盘上证据为准）；调查研究（事实不清先查，不凭经验补全）；抓主要矛盾（每票只推核心瓶颈）；实践检验（正确性由测试/真实运行验证）；从实际需求出发（以真实目标判断价值）。