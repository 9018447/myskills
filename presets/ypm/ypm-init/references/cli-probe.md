# CLI 配置目录核实与 acpx 一次性会话配方

两件事同一个原则：别猜，让 CLI 和文件系统自证。

## 核实 CLI 真实配置目录

- 触发：为任一 CLI 链接指令文件/技能前，需要确定它的用户级指令文件与 Skills 发现目录。
- 行为：
  - 优先跑该 CLI 的自报命令（kimi 用 `kimi doctor`；其他 CLI 找 config/status/env 类命令）。家目录名与自报结果冲突时，以自报为准。
  - 检查迁移标记：目录里有 `.migrated-*` 之类文件说明它是旧居所。已知案例：kimi 真实家目录是 `~/.kimi-code`（doctor 可查），旧 `~/.kimi` 已迁移弃用——链接装进旧目录全部不生效。
  - `doctor` 只验证它已知的配置文件存在，不证明 skills 目录被读取；配合技能冒烟交叉确认（见 ypm-cabinet-skill-discovery 技能）。

## acpx 一次性会话调用配方

- 触发：经 acpx 跑一次性验证或冒烟会话。
- 行为：全局旗标（`--approve-all`、`--timeout`、`--cwd`、`--agent`）一律放在 agent 子命令**之前**；一次性跑用 `exec` 子命令；顶层直接给 prompt 走持久会话，没有会话记录时报 "No acpx session found"。模板：
  - `acpx --cwd <中性目录> --approve-all --timeout 240 codex exec "<prompt>"`
  - `acpx --cwd <中性目录> --approve-all --timeout 240 kimi exec "<prompt>"`（kimi 是 acpx 内置 agent，解析为 `kimi acp`）
  - `acpx --cwd <中性目录> --approve-all --timeout 240 --agent '<raw acp 命令>' exec "<prompt>"`（无内置名的 CLI，如 dsh 用 `'dsh --profile acp'`）
- 查自定义 agent 注册与 config 语法：读 acpx 包内 `README.md` 与 `skills/acpx/SKILL.md`。`acpx config init` 会写全局配置文件（连默认权限一起改），只为查 schema 时不要跑它。
