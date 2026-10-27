---
name: use-acpx-subagent
description: 将其他 plugin 仓库中的 subagent、skill 或工作流提取为独立的 acpx 派发型 skill。用于生成 worktree 独立工作区、精简 AGENTS.md、显式指向关键 skills 的 prompts 和多阶段 acpx 原生 flow。产出可重复执行的技能包；执行器由调用方提供。
---

# use-acpx-subagent

生成专用派发 skill。读取来源 plugin 的实际文件，提取方法与依赖，把工作区准备、prompt 装配、acpx 派发和产物校验写成固定流程。生成完成不等于执行；用户只要求产出时，交付文件后停止。

不选择、不限制、不安装、不配置 agent、模型、提供商或 ACP 适配器。调用方传入 acpx 已配置的任意名称或 ACP command。不得把来源 agent 中的 model、tools、permissionMode 或宿主专用参数照搬为执行器配置。

先读 [生成约定](references/generation-contract.md) 和 [acpx 用法](references/acpx-contract.md)。填写规格时读 [规格说明](references/spec-format.md)。提取 review 机制时参考 [ECC 提取说明](references/ecc-extraction.md) 和 assets/examples/ecc/ 可重建样例。

## 1. 确认对象

确认来源仓库、目标 subagent/skill/command 文件和希望保留的职责。区分来源 plugin 仓库与任务目标仓库。目标仓库、任务、commit 范围与执行器是生成后每次调用的输入，不写死到可复用产物。

优先使用用户指定的对象。没有指定源对象时检查仓库结构，提出具体候选；不要从文件名猜职责。只在缺失信息会改变生成结果时询问。

## 2. 固定来源并提取方法

读取相关 agent、command、SKILL.md、引用文件和 LICENSE。固定完整 commit SHA，记录所选文件的 Git blob SHA；本地可用 git show <commit>:<path> 导出，远程读取须绑定同一 commit。不得只根据 README 或搜索摘要改写。

列出职责、输入、阶段、上下文、关键技能、引用闭包、产物和验收。检查技能引用的 references、scripts、assets 及相对路径。完整带入需要的依赖，移除无用依赖时记录理由。

区分可直接保留的方法、需改写为文件路径和 prompt 的宿主调用、依赖 hooks/MCP/凭证/远程操作的外部能力。最后一类必须声明为前提或排除出范围，不静默假装可迁移。

保留源许可。来源命令的自动发评论、发布、合并、安装和递归 Task 调用不能自动进入新技能。确实需要这些动作时，写成独立阶段与调用方授权条件，不顺带执行。

## 3. 设计专用 skill

只保留任务所需的角色、方法和上下文。新建精简 AGENTS.md，写清职责、工作区、输入边界、必须读取的 skills、产物位置及完成条件。保留项目适用规则，不覆盖项目 AGENTS.md、CLAUDE.md 或清空约束。

每个 prompt 写清当前阶段、输入文件、关键技能的绝对路径、读取顺序、输出契约和失败条件。使用 {{SKILL_PATHS}} 展开路径，并说明怎样使用。不要依赖 $skill-name、/command、自动发现或继承原会话。

将需要的来源 skill 完整目录放入 payload/skills/。来源只有 subagent/command 时，把提取方法整理成 payload/skills/<method>/SKILL.md，并保留上游快照及提取记录。不要把整个 plugin 的提示、设置和 hooks 复制进工作区。

单阶段用 exec --file；有中间产物、验证或阶段依赖时生成 acpx/flows TypeScript flow。确定性操作用 action/shell/compute，模型工作用 acp。内置模板生成固定线性图，首阶段后插入调用方指定的 checks，末阶段后校验并交付。需要分支、checkpoint 或独立角色会话时按官方 API 扩展模板并验证，不用未实现的 spec 字段伪装支持。

“确定性”覆盖布局、来源锁定、参数解析、步骤顺序、命令构造、失败处理和验收。不能声称模型判断和语义正确性确定。

## 4. 生成

按 references/spec-format.md 创建 spec.json 和 payload/。不留 TODO、悬空路径和未解释的占位符。执行：

python3 scripts/build_skill.py --spec /absolute/spec.json --source-root /absolute/pinned-source --payload /absolute/payload --output /absolute/<new-skill>

生成器核验源 blob，输出 SKILL.md、dispatch.json、AGENTS.md、prompts、skills、contracts、scripts/run.py、来源快照和散列锁。多阶段另生成 workflows/task.flow.ts。运行器不依赖本元技能的安装位置。

prepare 解析 base/head 为 commit，创建唯一分支与 git worktree。运行目录位于目标 checkout 与 Git 元数据之外。运行指令和依赖在独立 control 目录；派发 cwd 始终指向 worktree。

默认处理明确的已提交范围 base..head；dirty 工作区会停止。不得偷偷 stash、提交或遗漏未提交修改后宣称完成。需要未提交内容时先约定准确快照策略，再实现和验证扩展。

review 模式验证 tracked 与非忽略 untracked 文件未变化；edit 保留修改供审查。worktree 隔离目录，不等于进程沙箱。不要声称控制执行器全部原生工具、全局设置或凭证。

## 5. 验证并交付

校验 frontmatter、来源哈希、依赖闭包、模板变量和输出 schema。在临时 Git 仓库验证 worktree、commit 范围、空格路径、冲突目录、失败保留和拒绝脏清理。至少生成一个实际专用 skill，执行 prepare，确认每个 prompt 的关键技能路径存在。

用替身 acpx 检查参数透传、单步结果及多步 flow 调用。真实 ACP 联调只在调用方已提供执行器且要求运行时进行。分别报告静态校验、替身集成和真实 ACP 联调，不混称成功。

保存并提交技能代码到专用 Git 仓库；存在技能同步仓库时遵循其保存流程。用户只要下载时提供 ZIP，排除 .git、缓存、测试运行目录、凭证和本机路径。交付元技能与样例，简短说明验证范围。

失败时停止后续阶段、保留现场，不自动重放完整任务。清理 worktree 必须显式调用且工作区干净，保留分支和产物。不自动合并、push 或发布 review。
