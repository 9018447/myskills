---
name: create-workflow
description: 创建或修改 Spec Kit Workflow，并在通过校验后打包为独立技能。用于设计新的工作流类型、调整现有工作流、修复工作流结构或安装已验证的工作流技能。
argument-hint: "<要创建或修改的工作流>"
disable-model-invocation: true
---

# 创建 Spec Kit Workflow

Workflow 是 YAML 定义的编排：它决定**什么时候执行、执行什么、步骤间如何传值、何时暂停或分支**。Skill 定义能力与操作规则；Workflow 只通过已注册命令引用 Skill。

本技能只产出可检查的 workflow 技能目录，不运行 workflow 执行业务任务。

## 工作步骤

1. **界定工作流。** 提取触发场景、输入、输出、副作用、权限边界、失败处理和独立验收方式。查 `references/workflow-authoring.md`、`references/workflows.md` 与 `specify workflow --help`，确认字段和命令符合本机安装版本。完成标准：适用范围与验收条件明确，每项依赖的 CLI 能力都有版本依据。
2. **检查现有资产。** 读 `templates/workflow-template.yml` 与目标安装位置的同名技能。模板只给结构参考。完成标准：目标名称、版本处理、所需脚本、兼容性影响均已确定。
3. **实现工作流及依赖。** 在独立技能目录写 `workflow.yml`、`SKILL.md` 和全部被引用的 `scripts/`。节点 ID 唯一；shell 调用固定可审计，输入经文件或可信脚本读取；`requires` 不是安全边界，权限由沙箱、文件权限或外部隔离提供。完成标准：每个被引用的脚本、验证器、输入路径都真实存在，没有占位实现，也没有「缺依赖时自动放行」。
4. **校验候选版本。** 在临时目录备齐完整候选技能，先跑 `specify workflow --help` 探测本机可用子命令、按版本选校验路径（新版若有 `validate` 子命令则直接用它做结构校验）。本机 1.2.0 无 `validate`，实际路径为：YAML 解析器查语法 + 结构自检（节点 ID 唯一、步骤引用可解析、被引用脚本存在）+ 核对 frontmatter 与脚本依赖；必要时在隔离目录用 `specify workflow run <候选 workflow.yml> --json` 做无副作用冒烟（本地 YAML 文件可在 Spec Kit 项目外运行，此行为需按本机版本实测确认）。完成标准：所有适用的静态校验通过，依赖齐全，无未解释的校验错误。校验失败时保留已安装版本，只改候选版本。
5. **打包并安装（用户要求时）。** 候选通过校验后，用 `writing-for-agents` 规范写 `SKILL.md`，按用途安装到 `~/.claude/skills/<name>/`（跨仓库）或 `<项目根>/.claude/skills/<name>/`（项目专用）。双位置规则：源库 `~/myskills/<name>/` 是唯一编辑入口（git 管理），校验通过后才同步到安装位，同步后 `diff -r` 确认两侧一致。技能名用 kebab-case，与 `workflow.id` 相同。完成标准：目标目录含 `SKILL.md`、`workflow.yml`、全部脚本，元数据可解析，已安装内容与通过校验的候选一致。用户只要求创建或修改时，交付候选目录与校验结果。
6. **报告结果。** 报告技能名、workflow ID、文件位置、Spec Kit 版本、执行过的校验、依赖状态、遗留限制。明确区分静态校验与实际执行验证。

## 硬性约束

- AI 执行步骤没有独立步骤类型，一律经 `shell` 固定调用 `acpx --model gpt-6-luna codex exec -f <prompt 文件>`；时长与沙箱经 acpx 参数约束，prompt 一律经文件传入。
- `verify` 独立检查结果、文件范围、业务不变量并留存证据；退出码 `0` 通过、`1` 可修复失败、其余致命。
- 修复最多一次，且只处理已判定可修复的失败；最终校验失败必须让整个 workflow 失败，不靠 `continue_on_error` 掩盖。
- 不将表达式中的自由文本直接拼进 `shell.run`。

## 参考资料

- `references/workflow-authoring.md`：写 YAML 的规范——结构、Step 类型、输入与表达式、执行与安全约束。
- `references/workflows.md`：运行引擎的 CLI 用法——`run`/`status`/`resume`，以及 Overlay、安装与更新。
- `templates/workflow-template.yml`：结构参考。
- 版本偏差：`references/workflows.md` 可能超前于本机安装的二进制版本，以 `specify workflow --help` 实测输出为准。
- 官方文档：https://github.com/github/spec-kit/blob/main/docs/reference/workflows.md
