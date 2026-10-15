# Workflow 编写规范

Workflow 用 `.yml`/`.yaml` 定义，描述执行顺序与控制逻辑；Skill 通过 `SKILL.md` 定义能力与操作规则。只有当集成已把某能力注册为可调用命令时，workflow 才能用 `command` 引用它。

## YAML 结构

```yaml
schema_version: "1.0"

workflow:
  id: feature-development
  name: Feature Development
  version: "1.0.0"
  description: "Feature development workflow"

requires:
  speckit_version: ">=0.8.5"

inputs:
  spec:
    type: string
    required: true

steps:
  - id: specify
    type: command
    command: speckit.specify
    input:
      args: "{{ inputs.spec }}"
```

| 字段             | 作用                         |
| ---------------- | ---------------------------- |
| `schema_version` | 定义格式版本                 |
| `workflow`       | 元数据：ID、名称、版本       |
| `requires`       | 声明 Spec Kit 版本与集成要求 |
| `inputs`         | 输入参数                     |
| `steps`          | 有序执行步骤                 |
| `outputs`        | 对外输出，主要用于工作流组合 |

- `workflow.id` 稳定且唯一；`workflow.version` 形如 `"1.0.0"`。
- 每个步骤有可识别 `id`，同一作用域内不冲突，且不含 `:`（保留给引擎）。
- 不发明未注册的步骤类型。

## Step 类型

`id` 只是标识符，不代表 Skill、Markdown 文件或脚本路径。

| 类型                 | 用途                         |
| -------------------- | ---------------------------- |
| `command`            | 调用已注册的 Spec Kit 命令   |
| `prompt`             | 向 AI Agent 发送 Prompt      |
| `shell`              | 执行本地 Shell 命令          |
| `github`             | 操作 GitHub Issue 或 PR 标签 |
| `init`               | 初始化项目                   |
| `slot`               | 声明可扩展的步骤占位符       |
| `gate`               | 人工审批                     |
| `if` / `switch`      | 条件分支 / 多分支            |
| `while` / `do-while` | 循环                         |
| `fan-out` / `fan-in` | 对集合元素执行并汇总         |
| `workflow`           | 调用已安装的其他 Workflow    |

**command**：`command` 是 Spec Kit 可识别的命令名，不是文件路径。已注册命令可省略 `type: command`。

```yaml
- id: generate-plan
  type: command
  command: speckit.plan
  integration: claude
  input:
    args: "{{ inputs.spec }}"
```

**prompt**：直接提交提示词，不绑定 Markdown 文件。

```yaml
- id: security-review
  type: prompt
  integration: claude
  prompt: "Review the project for security vulnerabilities."
```

**shell**：`run` 是实际执行的命令，不是 Skill 名。

```yaml
- id: run-tests
  type: shell
  run: "python -m pytest tests/"
```

**gate**：暂停等待人工审批。需求确认、方案审核、有重要副作用的操作优先设置。

```yaml
- id: review-plan
  type: gate
  message: "Approve the implementation plan?"
  options: [approve, reject]
  on_reject: abort
```

## 输入与表达式

基础类型 `string`、`number`、`boolean`，可用 `required`、`default`、`prompt`、`enum` 约束。

表达式用 `{{ ... }}`，命名空间：

- `inputs`：当前工作流输入
- `steps`：已执行步骤的输出，如 `{{ steps.analyze.output.stdout }}`
- `item`：fan-out 中的当前元素
- `context`：执行上下文，如 `{{ context.run_id }}`、`{{ context.workflow_dir }}`

过滤器：`default`、`join`、`contains`、`map`、`from_json`、`to_json`、`upper`、`lower`、`split`、`length`。

只引用当前作用域可访问的变量与已产生的输出，不假设任意步骤都返回相同输出字段。

## 执行与安全约束

1. 按依赖顺序排列步骤，不在输入尚未产生时引用输出。
2. 用 `command` 调用已注册命令，不把普通 Skill 文件路径当作命令。
3. `prompt` 执行 Agent 指令，`shell` 执行系统命令，不混淆职责。
4. 危险或破坏性操作设人工审批节点。
5. 不把未约束的用户输入或 AI 输出直接插入 `run`；表达式替换不做 Shell 转义。
6. `requires` 不提供沙箱或权限隔离。
7. `gate` 不自动展示或审计后续 Shell 命令。
8. 用 `workflow` 调子工作流时显式映射输入，子工作流不继承父上下文。
9. 修改已安装 Workflow 优先用 Overlay，不直接改安装文件。
10. 生成 YAML 后做 Schema 校验，检查步骤类型、字段引用、命令名与执行依赖。

## 示例：Specify → Review → Plan → Tasks → Implement

```yaml
schema_version: "1.0"

workflow:
  id: feature-cycle
  name: Feature Development Cycle
  version: "1.0.0"
  description: "Automated SDD workflow"

requires:
  speckit_version: ">=0.8.5"

inputs:
  spec:
    type: string
    required: true
    prompt: "Describe the feature"
  integration:
    type: string
    default: "auto"

steps:
  - id: specify
    type: command
    command: speckit.specify
    integration: "{{ inputs.integration }}"
    input:
      args: "{{ inputs.spec }}"

  - id: review-spec
    type: gate
    message: "Approve specification?"
    options: [approve, reject]
    on_reject: abort

  - id: plan
    type: command
    command: speckit.plan
    integration: "{{ inputs.integration }}"

  - id: review-plan
    type: gate
    message: "Approve implementation plan?"
    options: [approve, reject]
    on_reject: abort

  - id: tasks
    type: command
    command: speckit.tasks
    integration: "{{ inputs.integration }}"

  - id: implement
    type: command
    command: speckit.implement
    integration: "{{ inputs.integration }}"
```

以当前安装版本支持的 Schema、Step 类型和命令定义为准，不把示例当作所有版本都支持的固定接口。
