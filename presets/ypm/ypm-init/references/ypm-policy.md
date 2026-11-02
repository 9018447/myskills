# YPM 共享执行约定

## Skills 与资源

先查真实安装路径，完整读取所需 Skill，再执行。只有目标 CLI 实际提供对应命令时才使用该斜杠命令。

外部 Skill 中的派发、固定模型和记录指令同样按本规则适配。没有依赖时，如实记录缺失。可用等价的直接方法达到相同目标时，执行并说明替代方式；不能称为“已调用原 Skill”。缺少独立验证、运行环境或关键证据时，保留 blocked/inconclusive，不能降级成通过。

包内 `scripts/check-plan.mjs` 是适配后的原版计划检查器。`references/bugbot-triage.md` 是原版审查参考，执行涉及角色与工具的部分时仍遵守本规则。源版本、精确替换与逐项差异分别见 `source-lock.json`、`adaptation-rules.json`、`pstack-adaptation.diff`。无需为了日常任务读取这些溯源文件。

核实每种 Agent 实际支持的用户级指令、Skills 发现与软链接行为。不要把某个 CLI 的目录习惯直接套给其他 CLI。目标 CLI 缺少斜杠工具时，可在 Prompt 指向真实 SKILL.md 并要求完整读取执行；以实际读取和执行证据核实，不能只看自报。

会话恢复只读取当前项目、当前任务相关的记录。不扫描其他项目的私人聊天。优先使用本次派发在 `prompts/` 与 `.agent-results/` 保存的 Prompt、日志、分支和结果路径。

