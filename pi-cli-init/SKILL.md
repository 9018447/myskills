---
name: pi-cli-init
description: >
  从现有的 skills 自动生成 pi-cli-tools 的 cli.json 配置。
  当用户说"注册 CLI 工具"、"配置 cli.json"、"把 skill 变成 pi 工具"、"初始化 cli 工具"时触发。
  扫描 ~/.agents/skills/ 目录，识别包含 scripts/ 子目录的 CLI tool skills，
  读取 SKILL.md 提取信息，为每个脚本生成包含功能映射、触发词、替代关系的 description，写入 cli.json。
  排除 mcp2cli 本身（它是元 wrapper，不是独立的 CLI 工具 skill）。
---

# pi-cli-init

帮用户把现有的 CLI skills 自动注册到 pi-cli-tools 的 cli.json 中。

## 识别 CLI Tool Skills

一个 skill 是 CLI 工具，当且仅当：
1. 它是 `~/.agents/skills/` 下的一个子目录
2. 目录内有 `SKILL.md`
3. 目录内有 `scripts/` 子目录，且里面有非 .md 的可执行文件
4. **排除** `mcp2cli` 本身（它只是 wrapper，scripts 指向 `mcp2cli @xxx`）

## 执行步骤（严格按顺序执行）

### 1. 扫描所有 skills 目录

列出 `~/.agents/skills/` 下的所有子目录：

```bash
ls -1 ~/.agents/skills/
```

### 2. 逐一检查是否有 scripts/ 目录

对每个子目录执行：

```bash
ls ~/.agents/skills/<skill_name>/scripts/ 2>/dev/null && echo "HAS_SCRIPTS" || echo "NO_SCRIPTS"
```

记录所有 `HAS_SCRIPTS` 的 skill（排除 `mcp2cli`）。

### 3. 提取每个 skill 的 name + description

读取每个候选 skill 的 `SKILL.md` 前 30 行：

```bash
head -30 ~/.agents/skills/<skill_name>/SKILL.md
```

解析 YAML frontmatter：
- `name:` 后的值为 skill 的标识名
- `description:` 后的值为工具描述（支持 `>` 或 `|` 多行 YAML 块，取第一行即可）

### 4. 收集脚本文件名

对每个 skill 的 `scripts/` 目录：

```bash
ls -1 ~/.agents/skills/<skill_name>/scripts/
```

排除 `.md` 文件，剩下的即为可执行脚本。

### 5. 生成 cli.json 条目

对每个脚本生成一个条目。注意：**description 绝不能原样复制 SKILL.md，必须按下方规则主动构建**。

```json
{
  "name": "<script_name>",
  "label": "<ScriptName>",
  "description": "<主动构建的功能描述>",
  "command": "/home/smh/.agents/skills/<skill_name>/scripts/<script_name>",
  "skill": "<skill_name>"
}
```

#### 5.1 naming 规则
- 如果 skill 内只有一个脚本，直接用脚本名作为 `name`
- 如果 skill 内有多个脚本，用 `<skill_name>_<script_name>` 作为 `name`
- `label`: 脚本名的首字母大写驼峰形式

#### 5.2 description 构建规则（强制执行）

description 必须包含以下四部分，缺一不可：

**A. 一句话功能定位**（首句）
- 说明这个工具是做什么的，不要抽象术语
- 示例：`Search symbols and call chains in a codebase.` 而不是 `Context-efficient knowledge processing.`

**B. Use for: 具体场景**（第二句）
- 列举 3-5 个该工具适合解决的具体问题
- 用引号包裹示例 query，让 LLM 一眼匹配
- 示例：`Use for: "how does X work", "who calls Y", "find all usages of Z".`

**C. Triggers: 关键词列表**（第三句）
- 列举 LLM 何时应该想到用这个工具
- 示例：`Triggers: search symbol, call chain, impact analysis, trace flow, find definition.`

**D. 替代映射（如适用）**（第四句）
- 如果该工具能替代被禁用的系统工具，必须显式声明
- 示例：`Primary substitute when ctx_shell, ctx_read, ctx_grep are disabled or unavailable.`
- 示例：`Primary substitute when iflow_web_fetch is disabled.`

**E. @skill-name 后缀**（最后）
- 必须以 `@<skill_name>` 结尾
- pi-cli-tools 扩展运行时会拆分出 skill 引用注入 promptGuidelines

#### 5.3 description 构建示例

**反例（禁止原样复制 SKILL.md）：**
```
Context-efficient data processing — sandboxed code execution, unified knowledge-base search...
```

**正例（按规则主动构建）：**
```
Multi-purpose workspace for shell commands, file reading, text search, and web fetching. Use for: "run a command", "read a file", "search text in files", "download a webpage", "batch process data". Triggers: shell, read file, grep, web fetch, batch execute. Primary substitute when ctx_shell, ctx_read, ctx_grep, or iflow_web_fetch are disabled or unavailable. @mcp2cli-context-mode
```

### 6. 读取现有 cli.json 并去重

目标路径（优先级）：
1. 用户指定的路径
2. `~/.pi/agent/extensions/pi-cli-tools/cli.json`
3. `./pi-cli-tools/cli.json`

读取现有文件，按 `name` 字段去重。已存在的条目**不覆盖**，只追加新条目。

### 7. 预览并写入

将合并后的完整 json 展示给用户，说明：
- 新增了几个条目
- 每个条目的 name 和构建后的 description
- 写入的目标路径

用户确认后，使用 `write` 工具写入文件。

### 8. 提醒重启

写入成功后提醒用户：
> CLI 工具已注册到 cli.json，但 pi-cli-tools 扩展在 pi 启动时才加载配置。请重启 pi 使新工具生效。

## 注意事项

- **description 绝不能原样复制 SKILL.md**：SKILL.md 的描述是给人类看的，cli.json 的 description 是给 LLM 看的，必须按规则重构。
- **@skill-name 后缀不能漏**：扩展靠这个后缀生成 promptGuidelines。
- **替代映射必须显式声明**：不要暗示，要直说 `Primary substitute when...`。
- **触发词要具体**：不要用"数据处理"这种抽象词，要用"run shell command"这种动作词。
