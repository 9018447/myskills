# ECC review 提取记录

来源 affaan-m/ECC（原 everything-claude-code），固定 commit 07971588f8ac7a60080ba8c1b7920c9e8e733e7d。读取 agents/code-reviewer.md、commands/code-review.md、skills/security-review/SKILL.md、skills/verification-loop/SKILL.md 和 LICENSE。快照和 blob 散列随样例保存，按 MIT 保留版权。

保留方法：确认范围；读完整修改文件、调用方与防护；审查安全、正确性、性能和维护性；只报告置信度大于 0.8 的实际问题；严重问题须有触发条件、片段、行号和防护不足的解释；允许零发现，删除重复和纯风格意见。

新建 ecc-code-review 方法 skill，显式引用 security-review 与 verification-loop。后两者提供检查方法，不照搬其中 npm 等命令。实际检查只由调用方 checks.json 指定。不导入 ECC 模型、原生工具清单和 hooks。

原 code-reviewer 对 HIGH 使用 WARNING，commands/code-review 本地模式阻止 CRITICAL/HIGH，PR 模式对 HIGH 要求变更。样例明确选 command 的严格门槛：CRITICAL 为 BLOCK，HIGH 或指定检查失败为 REQUEST_CHANGES；完整审查其余为 APPROVE；上下文不足为 INCOMPLETE。不声称各入口完全一致。

原流程的 PR 获取和发布不进入样例。只处理本地明确提交范围，不联网、不发 review、不自动修复、不阻止真实 Git commit。verdict 仅为报告建议。

阶段为 review_candidates → checks(action) → verify_evidence → validate_and_report(action)。复核在同一 flow 会话内完成，不声称独立审查者交叉验证。需要独立复核时另建独立工作区/会话，并定义固定交接产物。

原 agent 默认看未提交差异；样例改用 base..head 明确快照，避免新 worktree 中 git diff 为空。删除文件允许引用 base 侧，其他发现默认 head 侧。
