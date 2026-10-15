# 代码考古（code archaeology：git + 仓库内）

## 该来源包含什么

- commit 历史（message、日期、作者、diff）
- PR 描述、评审评论与讨论串（经 `gh`）
- 行内代码注释、TODO、FIXME、弃用标记
- ADR（架构决策记录），如果仓库有维护的话
- 测试。测试名与断言常常编码了促成某次改动的边界情况
- 同一批 commit 中被修改的相关文件（共同变更信号）
- 仓库里的 CHANGELOG 条目与发布说明
- commit message 与 PR 正文里提到的 issue/工单 ID

最值得信任的来源，直接与代码挂钩，也最完整。凡是经过仓库的东西都应该在这里。

## 如何搜索

扩充种子 commit 列表：

```bash
# Full history of the file through renames
git log --follow --oneline -- <file>

# Pickaxe: commits that added or removed this exact text
git log -S '<exact_string_from_code>' -- <file>

# Or for patterns:
git log -G '<regex>' -- <file>

# Who wrote each line and when
git blame -L <start>,<end> <file>

# The full diff of a specific commit
git show <hash>

# Commits between two points affecting this file
git log <old>..<new> -p -- <file>
```

对每个有实质内容的 commit，拉取 PR 上下文：

```bash
# Find the PR number from the merge commit or branch
git log -1 --format=%B <hash>

# Full PR context: body, review comments, linked issues
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files

# The --json reviews and comments fields are where the real signal is
```

寻找带外文档：

```bash
# ADRs often live in docs/adr/ or similar
rg -l -i 'architecture.decision' --glob '*.md'

# TODOs and FIXMEs near the target
rg -n -C2 '(TODO|FIXME|HACK|XXX|NOTE)' <target_file>

# Related tests. Names often encode the "why"
rg -l '<symbol>' --glob '*test*'
```

## 什么样的证据算好证据

- 解释了所解决问题的 PR 描述，而不只是罗列改动（“这修复了导致 X 的分页 bug”）
- 一条反复争论过各种替代方案的长评审串
- 目标行附近解释某个非显而易见约束的行内注释
- 一个名为 `test_handles_edge_case_when_X` 的测试，揭示了促成这段代码的边界情况
- 引用了工单或事故 ID 的 commit message
- 总结了用户可见缘由的 CHANGELOG 条目

## 常见陷阱

- **Squash 合并抹平历史。**如果仓库对 PR 做 squash 合并，分支历史中的单个 commit 就丢失了。退而求其次，去看 PR 正文和评论。
- **有误导性的 commit message。**“小重构”有时掩盖了有意的行为变更。看 diff，别只看 message。
- **照抄照搬的模式。**作者可能是照搬了一个模式而不理解其缘由。查一下该模式最早出现在代码库的哪里，去调查*那个* commit。
- **机器人 commit 与自动合并。**Dependabot、Renovate 和自动 backport 通常不带动机。寻找意图时跳过它们。
- **把代码当成意图的证据。**代码本身不是“它为何存在”的证据。证据来自 commit message、PR、注释、测试、文档。不要把“函数名叫 X”当作意图的证据来引用。

## 需要返回什么

所有与问题相关的 commit/PR/评论，并附上：
- 确切文本（引用原文）
- 哈希 / PR 编号 / 文件:行号
- 作者与日期
- 它是直接的（明确回应问题）还是旁证性的
