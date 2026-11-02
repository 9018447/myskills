---
name: officer-mode
description: 仅在首相明确要求时切换项目 officer 模式；用 on/off 管控 Write/Edit 与 Bash 写入审批提醒。
argument-hint: "[on|off]"
---

# Officer 模式

按参数切换当前项目的 officer 模式。标记文件为 `.ypm/officer-mode`。

- 无参数：检查标记文件是否存在并报告 ON 或 OFF。
- `on`：确保 `.ypm/` 存在，然后创建标记文件：`mkdir -p .ypm && touch .ypm/officer-mode`。
- `off`：移除标记文件：`rm -f .ypm/officer-mode`。
- 其他参数：说明只接受 `on`、`off` 或不带参数。

开启后 Write/Edit 仅允许写入 `.ypm/`、`.minister/` 和 `.agent-results/`；Bash 疑似写入操作会要求审批（写 `.agent-results/` 的命令直接放行）。关闭后不受此钩子限制。切换后重新启动会话，确保钩子配置已加载。
