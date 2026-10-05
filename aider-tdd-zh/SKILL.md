---
name: aider-tdd-zh
description: 用 aider headless 快速派发单文件和零碎编码请求。网关配置由脚本从 Claude Code 的 settings.json 一次性提取（密钥不进对话），一条命令派发，完成后看日志和 git diff 验证。不写正式 SPEC，要求快速完成。
tags: [user]
---

# aider 快速派发（单文件 / 零碎编码）

把 aider 当成一个无状态的写文件工头：一条命令派出去，它改文件、自动 git commit、退出；回来后看日志和 diff 验收。目标是快——零碎编码请求不设确认门槛、不写正式 SPEC。

## 事实（已确认）

- **网关配置走脚本**：`~/.claude/skills/aider-tdd-zh/aider-env.sh`（仓库内为 `aider-tdd-zh/aider-env.sh`）。它从 `~/.claude/settings.json` 的 `env` 块一次提取 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_MODEL`，导出成 litellm 认的变量（`ANTHROPIC_API_BASE` / `ANTHROPIC_API_KEY`），并自动加 `--model anthropic/<模型>`。密钥只落在环境变量里，**Agent 不需要也不应该读 settings.json**。
- 原 `~/.aider.conf.yml` 指向的 glm 网关已弃用（2026-10-05 实测连不上），一律通过脚本派发，不要直接调 `aider`。
- `aider -f <prompt.md> --yes-always` 是无状态一次调用：读 prompt 文件 → 改文件 → 退出。
- **`~/.aider.conf.yml` 设了 `auto-commits: false`，aider 不会自己 commit**。验收通过后由派发方（你）来 `git commit`——这也是验收环节的一部分：先看 diff，再提交。
- 模型是自建网关的 `glm-5.3-flash[1m]`，litellm 不认识这个名字，脚本已通过 `aider-model-metadata.json` 补上真实上限（输入 1M、输出 32K）。换模型名时同步改这个文件。
- **网关会截断过长回复**：一次产出大文件时文件可能被写一半（表现为测试文件只剩函数名、pytest 0 collected）。修复方式是补一条"文件被截断了，重写完整文件"的 fix 派发；prompt 里写明"回复保持简短"能显著降低截断概率。
- **模型可能把闲聊文本当成文件名**：曾出现 aider 创建了名为"完成后请执行提交："的杂物文件。验收时 `git status` 扫一眼，发现无关文件直接删。
- `--read <file>` 把文件标为只读；有现成的长上下文文件（接口文档、已有 SPEC）就用它加载，没有就不加。

## 硬约束（违反即任务错误）

- **只派发，不代写**。本技能的产出方式是 aider 改文件、你验收后 commit；发现自己在直接写目标文件的代码，就是走错了流程（除非 aider 不可用，此时直接普通编码并告知用户）。
- **单文件范围**。一次派发只允许动一个生产文件（外加最多一个测试文件）。`git show --stat HEAD` 看到其他生产文件被改就是越界，回滚重派。
- **prompt 必须自足**。aider 每次调用都是新鲜上下文，看不到本对话——prompt 里要写清目标文件路径、要做什么、期望值（用字面量）、不要做什么。
- **验证靠日志和 diff**。派发后看两样：日志末尾有没有测试/报错输出；`git show --stat HEAD` 动了哪些文件。仓库有测试入口就传 `--test-cmd "<命令>" --auto-test` 让 aider 自己迭代到绿。

## 快速流程

1. **判范围**：请求是否落在一个文件里？不是就停（见停止条件）。
2. **写 prompt**：短请求直接写进 `.aider-prompts/<任务名>.md`（先 `mkdir -p .aider-prompts .agent-results`）。一段话即可：做什么、改哪个文件、期望是什么、别动什么。
3. **派发**（在仓库根目录）：

```bash
~/.claude/skills/aider-tdd-zh/aider-env.sh \
  --yes-always \
  --test-cmd "<TEST_CMD>" --auto-test \
  -f .aider-prompts/<任务名>.md \
  <目标文件路径> \
  > .agent-results/<任务名>.log 2>&1
```

（仓库没有测试设施就去掉 `--test-cmd` 和 `--auto-test` 两行。）

4. **验收**：日志末尾测试输出全绿（有测试设施时）；`git status` / `git show --stat` 只应看到目标文件（外加最多一个测试文件），发现无关杂物文件直接删；期望值抽查一两个（跑一次性 REPL/CLI 检查）。有问题就补一条修正 prompt 再派一次。
5. **提交**：验收通过后由你自己 `git add <目标文件> <测试文件> && git commit`（aider 配置关闭了自动 commit，见"事实"）。

## 停止条件

- **任务要动多个生产文件**（跨文件重构、schema/协议迁移、改共享常量）：本技能不适用，告诉用户换方式。
- **两次派发后仍不对**：停下，把日志尾部和 diff 贴给用户，不要让 aider 无限循环——它会开始改测试断言来"通过"。
- **网关连不上或 401**（日志出现 `Connection error` / `InternalServerError` / 认证失败）：停下报告用户，不要自行换模型、不要反复重试。
- **SPEC 级需求**（需要用户确认行为和验收标准才敢动手的）：告诉用户这超出快速派发，先确认再派。

## 完成条件

- 目标文件的改动已 commit（`git show --stat` 可见，且只含目标文件）。
- 日志在 `.agent-results/` 里留档。
- 验收结果已向用户汇报：改了什么、怎么验证的。
