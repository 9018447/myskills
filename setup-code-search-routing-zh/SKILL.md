---
name: setup-code-search-routing
description: 为当前仓库安装代码搜索路由——细则写进 .claude/rules/code-search.md，概要写进 CLAUDE.md/AGENTS.md 的 Tool Routing 块。当用户说"装搜索路由/配置代码搜索规则/安装 code search routing"时使用。
tags: [user]
disable-model-invocation: true
---

# 安装代码搜索路由

给当前仓库装上代码搜索工具层（`zg`、`ast-grep`、LSP、`GitNexus`）的路由规则，让 agent 不再默认用 shell 的 `grep`/`find` 搜代码。写两个地方，内容分工不同：

- **细则** — `.claude/rules/code-search.md`：完整的路由表、升级流程、工具边界。种子模板是本技能目录里的 [ADD_RULES.md](./ADD_RULES.md)。
- **概要** — `CLAUDE.md`（没有就用 `AGENTS.md`）末尾追加一个 `## Tool Routing` 块：只有工具到用途的一行映射和升级顺序，并指向细则文件。种子模板是 [APPEND_CLAUDE.md](./APPEND_CLAUDE.md)。

两处都写。宁可概要与细则在仓库里重复出现，也不要缺任何一处。

这是一个提示驱动的技能，不是确定性脚本。探索、展示写入内容、与用户确认，然后写入。本技能可重复运行：已有的块就地更新，不追加重复的。

## 流程

### 1. 探索

查看当前仓库的起始状态。读一切存在的东西；不要假设：

- 仓库根目录的 `CLAUDE.md` 和 `AGENTS.md` — 存在吗？里面是否已有 `## Tool Routing` 块？
- `.claude/rules/` 目录 — 是否存在？里面是否已有 `code-search.md` 或内容不同的路由规则？

### 2. 展示写入内容并确认

向用户展示三样东西：

- 将写入 `.claude/rules/code-search.md` 的内容（[ADD_RULES.md](./ADD_RULES.md) 原文）
- 将追加的 `## Tool Routing` 块内容（[APPEND_CLAUDE.md](./APPEND_CLAUDE.md) 原文）
- 块会落在哪个文件里（选择规则见步骤 3）

写入前让他们编辑。没有需要调整的就直接进入写入。

### 3. 写入

**选择概要落点：**

- 如果 `CLAUDE.md` 存在，编辑它。
- 否则如果 `AGENTS.md` 存在，编辑它。
- 如果都不存在，问用户要创建哪一个——不要替他们选。

当 `CLAUDE.md` 已存在时绝不创建 `AGENTS.md`（反之亦然）——总是编辑已经存在的那个。

**写细则：** 写 `.claude/rules/code-search.md`，内容用 [ADD_RULES.md](./ADD_RULES.md) 原文；目录不存在就先创建。该文件已存在且内容与模板不同时，问用户是覆盖还是保留。

**写概要：** 在选定的文件末尾追加 `## Tool Routing` 块，内容用 [APPEND_CLAUDE.md](./APPEND_CLAUDE.md) 原文。该文件里已有 `## Tool Routing` 块时就地更新其内容，不追加重复的；不要动用户对周围章节的编辑。

### 4. 完成条件与收尾

两个写入都满足才算完成：`.claude/rules/code-search.md` 存在且内容与确认稿一致；选定文件里恰好有一个 `## Tool Routing` 块且内容与确认稿一致。

告诉用户路由已装好、落在哪两个文件里，以及之后可以直接编辑这两个文件调整规则；工具或路由本身变化时重跑本技能即可更新。
