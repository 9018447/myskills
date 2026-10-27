# 收集并审查候选问题

任务：{{TASK}}

先显式读取以下关键技能：
{{SKILL_PATHS}}

按 ecc-code-review 的步骤读取 {{DIFF_FILE}}，确认 base={{BASE}}、head={{HEAD}}。读取每个修改文件的完整上下文，追踪至少一个相关调用方及已有防护。被删除文件从 base 提交读取，不猜测其在 head 的内容。

按正确性、安全、性能、测试覆盖和项目约定寻找实际问题。不要用函数长度、缺文档、风格偏好或通用安全模式直接判定严重问题。应用置信度大于 0.8 的门槛；不确定的候选可暂留待下一阶段核验，最终必须删除或明确 blocked。

本阶段不要写最终 verdict。返回一个 JSON 对象，包含 status（complete 或 blocked）、summary、reviewed_files 数组、candidates 数组、limitations 数组。每个 candidate 至少记录 file、side（head/base）、line、snippet、触发条件、已有防护检查和初步严重程度。零候选合法。不得自行运行验证命令。
