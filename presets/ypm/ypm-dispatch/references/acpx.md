# acpx 速查（YPM Dispatch）

以首相指定的 `codex` 为**示例**；实际调用须读取 `~/cabinet.yaml`，原样使用任命的 Agent 参数。其他 ACP Agent 可用 `--agent '<启动命令>'`。始终使用绝对 Prompt 路径，避免 Worktree 中找不到文件。

## 一次性工作

```bash
mkdir -p .agent-results
PROMPT="$PWD/prompts/YPM-012.md"
acpx --cwd "$PWD" --approve-reads codex exec --file "$PROMPT" \
  2>&1 | tee .agent-results/YPM-012.log
```

无头会话里写请求默认被拒（acpx 默认 `nonInteractivePermissions: deny`）：公务员实际干活的命令用 `--approve-all`，写操作边界由 Prompt 的 `SCOPE` 约束。`--approve-reads` 只够只读冒烟，不能用来验收会写文件的任务。

## 同一任务连续工作

```bash
PROMPT="$PWD/prompts/YPM-013-r1.md"
acpx --cwd "$PWD" codex sessions ensure --name ypm-013
acpx --cwd "$PWD" --approve-reads codex prompt --session ypm-013 --file "$PROMPT" \
  2>&1 | tee .agent-results/YPM-013-r1.log

# 下一轮先调用 writing-for-agents，生成新 Prompt 落盘后再派发
PROMPT="$PWD/prompts/YPM-013-r2.md"
acpx --cwd "$PWD" --approve-reads codex prompt --session ypm-013 --file "$PROMPT" \
  2>&1 | tee .agent-results/YPM-013-r2.log
```

命名会话由 Agent 命令、工作目录和会话名称共同识别；换 Worktree 后不能假定复用旧会话。

## 多名公务员并行写入

为每个人创建不同的 Git Worktree，任务 Prompt 用绝对路径。检查 Git 状态，防止工作区混写。派发前确认对应 Agent 已由首相任命；对每人单独调用 `writing-for-agents` 并记录到 YAML。

```bash
# WORKTREE 已存在且独立时
PROMPT="$PROJECT_ROOT/prompts/YPM-014.md"
acpx --cwd "$WORKTREE" <appointed-agent> exec --file "$PROMPT" \
  2>&1 | tee "$PROJECT_ROOT/.agent-results/YPM-014.log"
```

`<appointed-agent>` 为**说明性占位符**，不能原样执行。按已任命的 acpx 调用参数替换；无需写 Shell `eval`。

## 各 Agent 实际启动命令（2026-10-24 实测）

acpx 内置 `codex`、`claude`、`pi` 三个名字，直接写 Agent 名；其余 CLI 用 `--agent '<启动命令>'`。**全局选项（`--approve-reads`、`--format`、`--suppress-reads` 等）必须写在 Agent 名之前**——写在 `exec` 之后会打印帮助。一次性任务用 `exec` 子命令；不带 `exec` 的裸调用进入持久会话管理，不是一次性执行。

```bash
# codex（内置；指令加载已验证，技能发现待复验）
acpx --approve-all --format text --suppress-reads codex exec --file "$PROMPT"
# kimi（指令加载已验证；其读文件工具报内部错误，技能待复验）
acpx --approve-all --format text --suppress-reads --agent "kimi acp" exec --file "$PROMPT"
# dsh（指令加载已验证，文件可读已证；技能发现待复验）
acpx --approve-all --format text --suppress-reads --agent "dsh --profile acp" exec --file "$PROMPT"
# omp（默认模型地区受限，待复验）
acpx --approve-all --format text --suppress-reads --agent "omp acp" exec --file "$PROMPT"
# mcode（需先 mcode login；角色指令经启动参数携带，不落盘、无技能目录）
acpx --approve-all --format text --suppress-reads \
  --agent "mcode acp --append-system-prompt-file <常务次官角色 AGENTS.md 绝对路径>" exec --file "$PROMPT"
```

各家的任职、指令文件与验证状态以 `~/cabinet.yaml` 为准，此处只固化启动命令的写法。mcode 无技能目录，派发给它的 Prompt 须写明所需 SKILL.md 的绝对路径。

## 参考

acpx 官方 CLI 文档：https://github.com/openclaw/acpx/blob/main/docs/CLI.md
