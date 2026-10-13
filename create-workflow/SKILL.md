---
name: create-workflow
description: 根据任务类型创建、选择或复用 Spec Kit Workflow Engine YAML，把验证通过的工作流打包为可安装技能（SKILL.md + workflow.yml + scripts/）安装到 ~/.claude/skills 或项目 .claude/skills，并以 JSON 任务契约调度 Codex 执行可独立验收的任务。适用于仓库探索、批量变更、迁移和重复性处理。
argument-hint: "<要创建的工作流或要执行的任务>"
disable-model-invocation: true
---

# create Workflow：先生成工作流，再执行

本 Skill 通过 `/create-workflow $ARGUMENTS` 启动。**此 Skill 负责按任务类型创建、校验、选择和复用多个 Spec Kit 工作流 YAML，并把每个验证通过的工作流打包为独立技能（SKILL.md + workflow.yml + scripts/）安装到 `~/.claude/skills/`（跨仓库）或项目 `.claude/skills/`（项目专用）；`specify workflow run` 只负责运行选中的 YAML。** 技能的 `description` 就是它的登记条目：会话里装了哪些工作流技能，当前可用的工作流清单就是哪些；不再向 CLAUDE.md 写入或维护任何登记项。不存在唯一的全局默认工作流。Claude 负责规划与异常处理，Codex 负责执行，Spec Kit 管理流程状态，可信验证程序判断结果是否通过。

## 1. 决定是“创建/修改工作流”，还是“执行任务”

1. 分析 `$ARGUMENTS`。用户要求「创建、配置、改变流程」时，主要产物是可复用的 YAML、依赖的可信脚本和打包好的技能，不擅自执行实际任务；用户明确要求「运行、处理、修改仓库」时，先检查工作流是否已打包，随后创建本次 JSON 契约并运行。完成标准：本次会话结束后，可复用工作流一律以已安装技能的形式存在，而不是 CLAUDE.md 条目。
2. 盘点已安装的工作流技能：列出 `~/.claude/skills/` 和当前项目 `.claude/skills/`（或仓库内 `.claude/skills/`）下的技能目录，工作流技能的判别标准是**目录含 `SKILL.md` 且含 `workflow.yml`**；逐一核实 SKILL.md、workflow.yml 及其引用的 scripts/ 依赖真实存在。确认执行位置是用户指定的仓库根目录，而不是误在 `$HOME` 执行。
3. 根据任务类型、写入范围、验证方式和执行权限选择匹配的工作流技能；匹配且有效就**复用**，本次只更新 JSON 任务契约。没有匹配项时，创建独立命名的新工作流，验证后按第 4 节打包安装。不同类型并存，不能把一个公共 YAML 当作所有任务的默认执行器，也不能为执行某个任务覆盖其他类型的 YAML。
4. `specify workflow run <path>` 不生成 YAML；`--json` 仅改变 CLI 输出格式。Spec Kit 对从本地 `.yml`/`.yaml` 运行的工作流允许在未初始化的目录运行，但状态保存在**当前工作目录**的 `.specify/workflows/runs/<run_id>/`。

## 2. 生成 JSON 任务契约（供运行时读取）

Claude 先研究目标仓库：通过只读索引/搜索定位有关文件、代码关系和现有验证方式；排除无关路径。把每次任务写为仓库内 `.agent/luna/task.json`（单任务/单工作区；并行任务使用隔离的 worktree）。示意：

```json
{
  "task_id": "config-normalize-001",
  "objective": "规范化指定配置，保持行为不变",
  "inputs": ["config/input.json"],
  "allowed_write_paths": ["config/output.json"],
  "protected_paths": [".claude", ".agent/luna/task.json"],
  "constraints": ["不得变更其他业务文件", "不得访问网络"],
  "validator_id": "该技能 scripts/ 内已审核的验证器",
  "acceptance": ["schema", "semantic-equivalence", "write-path-check"],
  "max_attempts": 2
}
```

明确输入、输出、副作用、允许/禁止修改的路径、验收标准和失败退出条件。路径均按仓库根目录解析，拒绝 `..`、绝对路径和符号链接逃逸。`validator_id` 必须指向**预先审核、位于 Codex 可写目录之外**的可信验证器；不允许任务 JSON 提供任意 Shell 命令替代验证器。仓库里已存在未提交改动时须先记录和隔离，不能把别人的改动当作本次执行产物。

开放式探索若没有客观验收标准，可只生成报告并交回 Claude；不能伪称已完成独立验收。

## 3. 创建符合规范的可复用 Workflow YAML

1. 检查 `specify workflow --help` 和（若提供）`specify workflow validate --help`，阅读对应当前安装版本的 [Spec Kit Workflow 官方参考](https://github.com/github/spec-kit/blob/main/docs/reference/workflows.md)。不要臆造 CLI 参数或 YAML 字段。
2. 新建工作流时，以 `references/workflow-template.yml`（本技能目录内）为**结构参考**，根据真实环境编写可执行 YAML。最低要求：`schema_version: "1.0"`、`workflow.id/name/version`、合法的 preflight → execute → verify → repair-once → finalize 结构和唯一节点 ID。参考模板包含占位的可信脚本，**不能直接作为可执行成品**。
3. 工作流按以下顺序组织：
   - **preflight（shell）**：验证任务契约、所需文件/权限、`codex` 可调用性、指定模型可用性、可信验证器存在、工作区隔离；失败立即退出。
   - **execute（prompt/codex 或 shell→codex exec）**：只从 JSON 契约读取任务；优先 `gpt-6-luna`，不默默降级其他模型。若使用 `shell` 启动 Codex，则通过受信脚本传入参数、限制沙箱和最大时长；不要把模型输出拼入 Shell 命令。
   - **verify（shell）**：独立验收文件范围、业务不变量、测试结果和 diff。把退出码、报告和证据写入独立位置。
   - **repair-once（if → execute → verify）**：仅可修复且未越界的失败允许重新执行一次；其余失败立即终止/升级给 Claude。第二次校验失败必须使最终状态为失败，不能依赖 `continue_on_error: true` 把任务判成成功。
   - **finalize（shell）**：仅在最终验收通过后保存成功标记及产物摘要。
4. 每个 `shell.run` 必须是固定且可审计的调用，读取输入文件或调用 `$SPECKIT_WORKFLOW_DIR/scripts/` 内的可信脚本；不把 `{{ inputs.* }}` 或 `{{ steps.*.output }}` 之类的自由文本直接插入 `shell.run`。`requires` 不是安全沙箱；实际权限由 Codex 沙箱、文件权限和外部隔离承担。
5. 运行引擎前，必须把引用的辅助脚本、验证器一并生成或指向真实存在的文件。每种工作流的辅助脚本放在技能目录自己的 `scripts/`，通过 `$SPECKIT_WORKFLOW_DIR` 相对定位；项目特有验证器要明确版本和来源。不得通过“缺少验证器时自动通过”的方式补齐依赖。
6. 先在临时文件写 YAML；用 YAML 解析器检查语法/结构，并使用安装版本支持的 `specify workflow validate` 等机制验证（先查 `--help`）；必要时在隔离测试目录做无副作用冒烟测试。**校验不通过时保持旧版本不变，绝不安装或更新技能。** 原文件已存在时先进行差异审查，有兼容性风险则保留旧版并创建独立版本。

## 4. 打包为技能并安装（登记条目 = 技能 description）

**仅在 YAML 已写入磁盘、依赖齐全且静态校验通过后，才打包安装或更新对应技能。** 不得安装引用不存在文件的技能，也不得把测试用 `echo` YAML 打包成正式执行技能。

1. 一个工作流类型对应一个稳定的技能名（kebab-case，与 `workflow.id` 一致）和自己的目录。跨仓库可复用装在 `~/.claude/skills/<name>/`，项目专用装在 `<项目根>/.claude/skills/<name>/`。旧布局（`~/.claude/workflows/*.yml` + CLAUDE.md 登记条目）已废弃：遇到时把 YAML 迁入技能目录并删除对应 CLAUDE.md 条目。

   技能目录布局：
   ```
   <name>/
   ├── SKILL.md       # 运行、校验、修复、恢复的步骤 + 契约 schema 等参考资料
   ├── workflow.yml   # Spec Kit 工作流 YAML
   └── scripts/       # driver、验证器等可信脚本
   ```
2. 按 writing-for-agents 的规范写 SKILL.md（有 `mattpocock-skills:writing-for-agents` 技能时先加载它；没有则按下列要点）：
   - 前置元数据：`name`（= 技能名 = `workflow.id`）和 `description`。**description 是上下文指针**：写明工作流做什么 + 触发分支（哪些任务类型/场景该用它），一分支一触发词，引导词前移。**模型调用技能**：省略 `disable-model-invocation`，让 agent 在匹配任务出现时能自主发现它——发现机制取代了旧的 CLAUDE.md 登记。
   - 正文只写运行该工作流需要的步骤，每步带完成标准：填写/复核 JSON 契约 → `specify workflow run <workflow.yml 绝对路径> --json` → `status`/`resume` → 按退出码语义判断验收 → 报告字段。契约 schema、verify 退出码语义（0=通过，1=可修复失败，其余=致命）等参考资料与 workflow.yml、scripts/ 同目录共置。
3. 安装完成标准：目录落位、SKILL.md 前置元数据可解析、workflow.yml 通过第 3.6 节校验、scripts/ 齐全。完成后报告：技能名、安装位置、`workflow.id`、Spec Kit 版本、静态校验结果和依赖状态，并指出「尚未验证 Codex 实际执行」。
4. 更新已有技能时走同样校验门：先差异审查，保留其他技能与用户目录中的无关内容，同一技能名不重复安装两份。

## 5. 选择工作流、执行与恢复

执行前先在 `~/.claude/skills/` 与项目 `.claude/skills/` 里按本次任务类型选择匹配的工作流技能，确认其 workflow.yml 和依赖仍然有效；有已安装技能时**按该技能 SKILL.md 的运行步骤执行（它是该工作流的权威说明）**；如无合适技能，则先用本 Skill 创建并按第 4 节打包安装，**绝不能随便选择另一类工作流代替**。

在目标仓库根目录运行（变量必须替换为本次实际选中的 workflow.yml 绝对路径）：

```bash
SELECTED_WORKFLOW_YAML="<技能目录内 workflow.yml 的绝对路径>"
specify workflow run "$SELECTED_WORKFLOW_YAML" --json
specify workflow status <run_id> --json
specify workflow resume <run_id> --json
```

后两条中的 `<run_id>` 用真实运行输出替换；仅在引擎允许且检查副作用后恢复失败/暂停的运行，不要为了恢复直接重新运行整个工作流。

引擎维护 `.specify/workflows/runs/<run_id>/` 内的运行状态和日志，但**不会自动生成所有业务证据**。还需保存并关联 `run_id`：本次 JSON 契约、Codex 实际输出、验收报告、Git diff 摘要和必要的人工审批记录。最终报告必须同时标出**所用技能名与 workflow.yml 路径**，便于复现。

## 6. 验收及失败升级

成功仅由可信验证器决定，Codex 的“已完成”声明不能代替验收。执行越界、受保护文件被修改、无测试手段、模型不可用、命令失败、外部副作用或需求歧义时停止自动执行并交给 Claude；不得为了通过而降低验收要求。最后报告 `task_id`、`run_id`、技能名、YAML 路径、实际模型、尝试次数、变更文件及明确的通过/失败/待审批状态。

参考：
- https://github.com/github/spec-kit/blob/main/docs/reference/workflows.md
- https://code.claude.com/docs/en/skills
