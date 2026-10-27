---
name: ecc-code-review
description: 从 ECC code-reviewer 与 code-review 命令提取的本地提交范围审查方法；用于基于上下文和可复现证据过滤问题、复核严重程度并形成审查结果。
---

# ECC code review 方法

先读运行 prompt 提供的范围与 AGENTS.md，再读 diff 和完整修改文件，追踪 imports、调用方、类型、测试与已有防护。通过 base/head SHA 获取准确内容；不要使用无变更 worktree 的默认 git diff 作为审查范围。

涉及认证、授权、用户输入、秘密、API、上传、支付或数据访问时，读取相邻 ../security-review/SKILL.md 的相关段落。解释验证结果时读取 ../verification-loop/SKILL.md。它们只提供方法；本任务是否运行、运行什么检查以调用方 requested-checks 为准。不要照抄框架特定示例命令或自动修复。

先判断具体错误行为，再应用分类。检查逻辑边界、错误传播、并发、输入与信任边界、秘密泄漏、查询范围、性能路径和测试遗漏。严重程度根据触发概率与实际影响决定，不按代码形状机械判定。

每条最终发现必须满足四个条件：能指向准确文件和行；能说明输入/状态与错误结果；已读上下文和已有防护；严重程度与影响相符。confidence 必须大于 0.8。HIGH/CRITICAL 还必须提供准确片段和防护不足的理由。不能满足就删除或降低；若整个审查受阻则 status=blocked。

过滤常见误报：调用方已处理错误的内部函数、已经类型收窄的空值、固定数量的循环、明确的 fire-and-forget、测试常量、生成配置体积、非密码用途随机数。函数长度、文档缺失和“建议使用某技术”本身不构成 HIGH。

合并同根因发现。非变更代码只报告确证的 CRITICAL 安全问题。允许零发现，不为显得严格制造问题。删除文件使用 base 侧准确行和片段，其他问题使用 head 侧。密钥证据用不含秘密的周边准确片段和文字说明，避免泄露。

最终输出遵循任务提供的 JSON schema。status=complete 表示范围已完成审查；blocked 表示证据或能力不足。提供 reviewed_files 和 limitations，不声称未运行的测试通过。

运行器采用明确适配门槛：CRITICAL→BLOCK；HIGH 或指定检查失败→REQUEST_CHANGES；完整审查且无上述问题→APPROVE；blocked→INCOMPLETE。只提供建议，不操作真实提交或远程 review。

来源为 ECC commit 07971588f8ac7a60080ba8c1b7920c9e8e733e7d 的 agents/code-reviewer.md 与 commands/code-review.md，按 MIT 许可改写。原文位于运行目录 control/upstream/；生成包 references/upstream/ 保留 LICENSE。
