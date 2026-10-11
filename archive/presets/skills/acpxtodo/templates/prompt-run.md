# 派发 Prompt 模板：运行票（tNN）

判定：票面标注 `含 N 次真实运行` 或预计真实运行总时长 ≥20 分钟。默认 codex，派发命令带 `--model gpt-6-luna`。运行票之间默认串行，不与其他运行票并发（pueue 队列和机器算力互相拖慢，benchmark 计时互相污染）。

**本模板 = 实现票模板（`prompt-implement.md`）的全部固定段（任务背景 / 工作环境 / 工作原则 / 文风）+ 下面这节替换「工作方式」。**

---

## 工作方式（固定段，替换实现票模板同名节）

1. 遵守当前 Spec、ADR 和 Ticket 范围；票面含实现部分时先用 `/gitnexus-plan` 出实现计划（只写计划文档不动实现代码，计划落到本 worktree 的 `docs/plans/` 下），再按该计划用 `/tdd` 完成。
2. **票内真实运行任务必须用 `/pueue` 执行**——运行任务进 pueue 后台队列跑，agent 进程被杀或会话中断不会连坐运行任务，这正是 pueue 的设计用途，`run_in_background` 起的进程没有这层保护。pueue 可能不在 shell 的 PATH 里，先 `which pueue` 定位（通常 `~/.cargo/bin/pueue`），拿到路径即可用。
3. 边界：进 pueue 的是**运行任务**（julia 跑 benchmark、批量求解等），**不是 agent 进程本身**——交互式 agent 在 pueue 环境下启动会静默卡死。agent 自身的派发走 acpx，两者不可混。
4. 不跑全量测试套件（全量由编排者单独派发）；不向下派发；不跑 code-review；不提交 git；文件路径先在盘上验证——同实现票模板固定段第 2、4、5、6、7 条。
