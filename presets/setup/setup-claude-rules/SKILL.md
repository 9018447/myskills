---
name: setup-claude-rules
description: 用 install.sh 脚本为当前仓库安装 agent 规则集——代码搜索路由（细则 .claude/rules/code-search.md）、编码分工原则（细则 .claude/rules/coding-principle.md）、验证复审规则（细则 .claude/rules/verification.md）和工作原则（细则 .claude/rules/work-principles.md，提炼自 pstack principle-* 系列），概要块写进 CLAUDE.md/AGENTS.md。脚本驱动，agent 只跑脚本并转述结果；转述后对三个配套技能（setup-pre-commit、setup-matt-pocock-skills、show-me-your-work）做一次只读检查，已有就跳过，缺了才建议触发。当用户说"装搜索路由/装编码规则/配置 claude rules"时使用。规则集会持续扩充。
tags: [user]
disable-model-invocation: true
---

# 安装代码搜索路由（脚本驱动）

安装由本技能目录里的 `install.sh` 确定性地完成，agent 不参与写入。所有决定（选概要落点、覆盖已存在的规则文件、就地更新概要块）都由脚本自行处理，agent 不探索、不展示草稿、不询问用户——只跑脚本、把结果转述给用户，然后按「配套技能检查」做一次只读检查。本技能可重复运行：脚本幂等，旧块就地更新，不追加重复的。

## 触发

运行脚本，只传一个可选参数——目标仓库根目录，缺省是当前工作目录：

```bash
bash <技能目录>/install.sh [仓库根目录]
```

技能目录就是本 SKILL.md 所在的目录，脚本与它同级。

## 结果转述

脚本只输出一份结果摘要。agent 把输出原样转述给用户，不额外补写或解释。摘要里如果提到某个工具 `MISSING`，告诉用户缺的是哪个、装好后重跑一遍本脚本即可——规则文件会照常写入，因为缺工具不阻断安装。

脚本做的事（完全确定，agent 不在场）：

- **工具检查** — 调用技能目录里的 `check-tools.sh`，报告 `jg`、`rg`、`zg`、`ast-grep`、`gitnexus` 各自的存在状态（jg 额外验证 auth；含 LSP 宿主提示）。
- **写细则** — 确保 `.claude/rules/` 存在，写 `code-search.md`、`coding-principle.md`、`verification.md` 和 `work-principles.md`，内容分别用 [ADD_RULES.md](./ADD_RULES.md)、[CODING_RULES.md](./CODING_RULES.md)、[VERIFY_RULES.md](./VERIFY_RULES.md) 和 [PRINCIPLES_RULES.md](./PRINCIPLES_RULES.md) 原文。文件已存在就覆盖——安装即覆盖，不询问。
- **选概要落点** — 优先级：`CLAUDE.md` 存在用 `CLAUDE.md`；否则 `AGENTS.md` 存在用 `AGENTS.md`；两个都不存在就创建 `AGENTS.md`。绝不同时操作两个文件。
- **写概要** — 在落点文件末尾追加 `## Tool Routing` + `## Division of Labor` + `## Verification` + `## Work Principles` 块，内容用 [APPEND_CLAUDE.md](./APPEND_CLAUDE.md) 原文。落点文件尾部已有这些标题时就地替换旧块，不追加重复的、不动用户对上方章节的编辑。

## 配套技能检查

脚本跑完并转述后，对三个配套技能在目标仓库的落点做一次只读检查。原则是检查先行、不无脑覆盖：落点已存在的报一句"已有，跳过"，不重装、不动它；只对缺失项建议触发。

- **setup-pre-commit** — 看 `.husky/pre-commit`、package.json 的 `prepare: "husky"` 脚本或 `lint-staged` 配置。任一存在即视为已装钩子，跳过；都没有就提示用户运行 `/setup-pre-commit`（该技能禁止模型自行触发，须用户运行）。
- **setup-matt-pocock-skills** — 看 AGENTS.md/CLAUDE.md 里的 `## Agent skills` 章节、仓库根 `GLOSSARY.md` 或 `docs/agents/`。任一存在即跳过；都没有就提示用户运行 `/setup-matt-pocock-skills`（同样禁止模型自行触发）。
- **show-me-your-work** — 看 `.scratch/`、`.audit/` 或 steering 文件里已有的 decision log 约定。已有即跳过；没有则告知用户：后续长任务、自治运行、或用户说"直到…完成"/建立目标（goal set）时，agent 会直接用这个技能记决策轨迹（它可由 agent 自行触发，不必请示）。

## 完成条件

所有写入都完成才算成功，且都由脚本保证：三个细则文件存在且与模板一致；落点文件的概要块与模板一致、没有重复章节。脚本以退出码或结果行标明写入是否全部落地，agent 依据它判断并把结果转述给用户。配套技能检查也要有结论——三项各标"已有"或"缺"——整轮才算结束。