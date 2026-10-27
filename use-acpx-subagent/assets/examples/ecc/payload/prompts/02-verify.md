# 证据复核与最终结果

再次确认关键技能路径和任务：
{{SKILL_PATHS}}
{{TASK}}

读取 {{CHECKS_FILE}}，结合 flow 提供的上一阶段候选与真实检查结果，按 ecc-code-review 逐条复核。检查源码片段、行号、触发输入和失败结果，解释 types、调用方校验或框架行为为何没有拦住问题。删除不满足门槛、重复、纯风格及上下文已处理的问题。

检查范围是 {{BASE}}..{{HEAD}}。非变更代码只允许报告有明确证据的 CRITICAL 安全问题。允许零发现。不要把未要求的检查写成通过，不把验证失败改成猜测的代码问题。

严格按 {{RESULT_SCHEMA}} 返回直接 JSON 对象，字段为 status、summary、reviewed_files、limitations、findings。每个 finding 包含 severity、confidence、title、file、side、line、snippet、trigger、evidence、guards_checked、fix。snippet 必须是所选提交侧文件中的准确连续片段；不得包含真实密钥。fix 是修复建议，不实际编辑。

完整阅读和复核才能 status=complete。不能完成时 status=blocked，并在 limitations 记录原因。不要输出 verdict、checks 或 severity_counts，这些由确定性校验计算。
