---
name: project-init-zh
description: 为新项目或缺少 Agent 项目约定的仓库执行通用初始化；先完成 Matt Pocock 工程技能配置，再建立本地 Markdown 跟踪约定并生成 AGENTS.md 与 CLAUDE.md。
---

# 项目通用初始化

用于新建项目，或为现有仓库补齐可执行的 Agent 项目上下文。先调查仓库现状，再仅补缺失内容；保留已有约定，不覆盖用户文档。

## 流程

### 1. 先完成 Matt Pocock 配置

首先调用 `setup-matt-pocock-skills-zh` 技能并完整完成其流程。不要在该步骤完成前创建或编辑本技能后续涉及的项目跟踪文档及 Agent 指令文件。

本项目初始化的跟踪器默认选择**本地 Markdown**（`.scratch/<feature>/`）；在配置技能询问 issue tracker 时选择此项。只有用户明确要求其他跟踪器时才改用其他选项。依照被调用技能的实际流程完成其要求的确认和文件写入。

### 2. 调查仓库

在仓库根目录检查：

- `git status --short`、`git rev-parse --show-toplevel`，确认根目录和已有未提交改动；
- 已有 `AGENTS.md`、`CLAUDE.md`，读取完整内容；
- `.scratch/`、`docs/agents/issue-tracker.md` 是否已存在，以及项目实际使用的语言、构建和测试命令；
- 项目 README、manifest 和 CI 配置中与日常开发直接相关的事实。

将调查确认的事实与未知项分开。不要从项目名称、目录名或常见惯例猜技术栈和命令。找不到验证命令时，在文档中说明待确认，不要编造。

### 3. 设置本地 Markdown 跟踪

确保 `docs/agents/issue-tracker.md` 明确记录本仓库使用本地 Markdown issue，位置为 `.scratch/<feature>/`。优先复用步骤 1 产生的文件；已存在时核对并仅修正与用户选择冲突的内容，不覆盖其他配置。

如果 `.scratch/` 尚不存在且仓库约定允许创建，则创建目录及一个 `.gitkeep`，确保空目录可纳入版本控制。不要擅自新增 ticket 模板、标签体系或自动化脚本。

### 4. 生成两份 Agent 指令

在仓库根目录确保 `AGENTS.md` 和 `CLAUDE.md` 两个路径均可用，并让它们通过**软链接指向同一份规范文件**，避免维护两套互相矛盾的规则。默认以 `AGENTS.md` 为规范文件，`CLAUDE.md -> AGENTS.md`。

- 两个路径都不存在时，创建 `AGENTS.md`，再创建相对软链接 `CLAUDE.md -> AGENTS.md`。
- 仅 `AGENTS.md` 存在且 `CLAUDE.md` 不存在时，为后者创建相对软链接。仅 `CLAUDE.md` 存在时，先检查其内容和引用关系，再将其保留为规范文件并创建 `AGENTS.md -> CLAUDE.md`，不要为统一方向而搬动或覆盖用户文件。
- 如果两者已是互相独立的普通文件，先比较内容：相同则在确认链接替换不会丢失信息后，将 `CLAUDE.md` 替换为指向 `AGENTS.md` 的软链接；不同时保留两者并指出冲突，请用户决定规范内容后再链接。若任一路径是其他类型的文件或链接指向不明，不要覆盖，停止并报告。
- 规范文件中只写从仓库证据确认的技术栈、入口、构建/测试/检查命令、重要目录说明及必要约束。把默认做法标为默认，把未确认事项标为待确认。
- 明确本地 Markdown issue 的位置，并链接 `docs/agents/issue-tracker.md`。
- 不复制长篇 README，不新增空泛的“保证质量”等口号，也不把一次性任务要求固化成项目规则。

### 5. 生成项目级 Claude 规则

在项目仓库的 `.claude/rules/` 下确保存在 `project-communication.md`，内容包含以下要求：

```markdown
# 项目交流与呈现

- 需要把方案、比较、流程或结果以更直观方式呈现时，使用 `/show-me` 技能。
- 与用户交流时使用自然、清楚的中文，避免中英混杂；必要的技术名称、代码、命令和专有名词可以保留原文，并用中文解释。
- 阅读 `CONTEXT.md` 后，用中文向用户转述其中的英文内容；不要因此擅自改写仓库中的原始 `CONTEXT.md`。
```

若规则文件已存在，读取后仅补入缺失要求，保留其他规则；不要覆盖用户内容。若项目内 `.claude/rules/` 不存在则创建。此规则应随项目保存，不要写入用户级 `~/.claude/rules/`。

### 6. 验证并交付

重新读取两份文件、issue-tracker 配置和项目内 `.claude/rules/project-communication.md`，确认：

- `AGENTS.md` 与 `CLAUDE.md` 均可读取，并通过软链接解析到同一规范文件；
- 默认 issue tracker 明确为本地 Markdown，路径是 `.scratch/<feature>/`；
- 项目级 `.claude/rules/project-communication.md` 存在，包含 `/show-me`、自然中文交流和将 `CONTEXT.md` 英文内容译为中文转述的要求；
- 新增规则均有仓库证据，未丢失或覆盖用户原有内容；
- 给出的命令能从项目配置中找到依据。若可安全运行最小的现有检查，运行并报告结果，不因初始化而触发耗时或有破坏性的任务。

交付时列出创建/修改的路径、实际采用的验证结果，以及仍待用户确认的事项。实践是检验真理的唯一标准；后续执行结果若推翻文档中的假设，应依据证据修正规则。
