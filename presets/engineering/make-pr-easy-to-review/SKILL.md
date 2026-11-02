---
name: make-pr-easy-to-review
description: 清理嘈杂历史、改进 PR 描述、添加审查者指引，为 PR 审查做好准备，且不改变代码行为。用于 "make this easy to review"、"tidy this PR"、"clean up commits" 或 "annotate the diff"。
---

# 让 PR 易于审查

准备好 PR，让审查者能快速理解意图、重要文件和风险。默认目标是在不改变行为的前提下提升可审查性。

## 工作流

1. 从用户提供的 URL 或当前分支确定目标 PR。
2. 检查提交、diff 大小、变更路径、生成文件和 PR 描述。
3. 识别可审查性问题：嘈杂的提交、过时的描述、无关的变更、机械性改动与逻辑改动混杂、缺少测试，或审查入口不清晰。
4. 在改写历史或 force-push 之前先提出方案。
5. 应用安全的改进，然后验证 tree 或 diff 仍与预期代码一致。

## 历史清理

只有当用户要求或同意该方案时才改写历史。改写之前：

```bash
gh pr view <PR> --json title,headRefName,baseRefName,state,commits
git fetch origin <headRefName> <baseRefName>
ORIGINAL_TREE=$(git rev-parse origin/<headRefName>^{tree})
```

良好的提交划分通常遵循依赖顺序：

1. Schema/存储或生成的 API 定义。
2. 核心逻辑。
3. 接线与集成。
4. UI 或表层行为。
5. 测试。

改写之后，验证内容一致性：

```bash
echo "Original tree: $ORIGINAL_TREE"
echo "Current tree:  $(git rev-parse HEAD^{tree})"
git diff origin/<headRefName> --stat
```

如果 tree 意外发生了变化，不要推送。

## 审查者指引

当代码行为应保持不动时，优先用 PR 描述和审查备注：

- 添加与实际 diff 相符的 TL;DR。
- 把核心文件与生成文件或机械性文件区分开。
- 点出有风险的行为变更、迁移顺序、上线计划和测试覆盖。
- 当 issue 跟踪器、仪表盘或设计文档能解释意图时，附上链接。

## 护栏

- 绝不把有意义的行为变更藏在"清理"里。
- 除非用户明确要求，否则不绕过 hooks。
- 如果 PR 大到无法靠备注变得可审查，就建议拆分，而不是绕着问题做表面修饰。
