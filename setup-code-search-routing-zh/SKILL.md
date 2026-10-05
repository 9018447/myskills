---
name: setup-code-search-routing
description: 为当前仓库安装代码搜索路由——细则写进 .claude/rules/code-search.md，概要写进 CLAUDE.md/AGENTS.md 的 Tool Routing 块。当用户说"装搜索路由/配置代码搜索规则/安装 code search routing"时使用。
tags: [user]
disable-model-invocation: true
---

# 安装代码搜索路由

给当前仓库装两套规则：代码搜索路由 + 编码分工原则。写三个地方，内容分工不同：

- **搜索路由细则** — `.claude/rules/code-search.md`：完整的路由表、升级流程、工具边界。种子模板是本技能目录里的 [ADD_RULES.md](./ADD_RULES.md)。
- **编码原则细则** — `.claude/rules/coding-principle.md`：主 agent 不做编码，只写文档、编排任务、把握全局；所有编码工作（修 bug、写测试、写新代码、重构）派发给实现 agent。种子模板是 [CODING_RULES.md](./CODING_RULES.md)。
- **概要** — `CLAUDE.md`（没有就用 `AGENTS.md`）末尾追加一块，内容用 [APPEND_CLAUDE.md](./APPEND_CLAUDE.md) 原文：`## Tool Routing` 一节是工具到用途的一行映射加升级顺序，`## Division of Labor` 一节是编码分工的几句话，各自指向对应细则文件。

三处都写。宁可概要与细则在仓库里重复出现，也不要缺任何一处。

这是一个提示驱动的技能，不是确定性脚本。探索、展示写入内容、与用户确认，然后写入。本技能可重复运行：已有的块就地更新，不追加重复的。

## 流程

### 1. 探索

查看当前仓库的起始状态。读一切存在的东西；不要假设：

- 仓库根目录的 `CLAUDE.md` 和 `AGENTS.md` — 存在吗？里面是否已有 `## Tool Routing` 块？
- `.claude/rules/` 目录 — 是否存在？里面是否已有 `code-search.md` 或 `coding-principle.md`？内容是否与模板不同？
- 工具可用性 — 运行本技能目录下的 `check-tools.sh`（`bash <技能目录>/check-tools.sh`），得到 `rg`、`zg`、`ast-grep`、`gitnexus`、`aider`、`acpx` 六个命令各自的存在状态。

### 2. 展示写入内容并确认

向用户展示五样东西：

- 工具检查结果。有 `MISSING` 时明确告诉用户缺了哪个，并说明：规则文件会照常写入（缺工具不阻断），但 agent 执行时会遇到不存在的命令；用户也可以选择先装工具再重跑本技能
- 将写入 `.claude/rules/code-search.md` 的内容（[ADD_RULES.md](./ADD_RULES.md) 原文）
- 将写入 `.claude/rules/coding-principle.md` 的内容（[CODING_RULES.md](./CODING_RULES.md) 原文）
- 将追加的块内容（[APPEND_CLAUDE.md](./APPEND_CLAUDE.md) 原文，含 `## Tool Routing` 和 `## Division of Labor` 两节）
- 块会落在哪个文件里（选择规则见步骤 3）

写入前让他们编辑。没有需要调整的就直接进入写入。

### 3. 写入

**选择概要落点：**

- 如果 `CLAUDE.md` 存在，编辑它。
- 否则如果 `AGENTS.md` 存在，编辑它。
- 如果都不存在，问用户要创建哪一个——不要替他们选。

当 `CLAUDE.md` 已存在时绝不创建 `AGENTS.md`（反之亦然）——总是编辑已经存在的那个。

**写细则：** 写 `.claude/rules/code-search.md` 和 `.claude/rules/coding-principle.md`，内容分别用 [ADD_RULES.md](./ADD_RULES.md) 和 [CODING_RULES.md](./CODING_RULES.md) 原文；目录不存在就先创建。任一文件已存在且内容与模板不同时，问用户是覆盖还是保留。

**写概要：** 在选定的文件末尾追加 `## Tool Routing` 块，内容用 [APPEND_CLAUDE.md](./APPEND_CLAUDE.md) 原文。该文件里已有 `## Tool Routing` 块时就地更新其内容，不追加重复的；不要动用户对周围章节的编辑。

### 4. 完成条件与收尾

三个写入都满足才算完成：`.claude/rules/code-search.md` 和 `.claude/rules/coding-principle.md` 都存在且内容与确认稿一致；选定文件里的追加块内容与确认稿一致，且没有重复的 `## Tool Routing` 或 `## Division of Labor` 章节。

告诉用户规则已装好、落在哪三个文件里，以及之后可以直接编辑这些文件调整规则；工具或路由本身变化时重跑本技能即可更新。
