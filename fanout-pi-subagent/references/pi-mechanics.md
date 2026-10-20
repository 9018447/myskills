# pi 子代理机制参考

编写新角色或排查派发问题时查阅。以下机制均在本机 pi 1.3.0 + acpx 上验证过。

## 派发链路

```bash
acpx --cwd "<运行目录>" --approve-all pi exec -f prompts/tNN.md 2>&1 | tee .agent-results/<角色>-tNN.log
```

- `exec` 是一次性运行：无会话保存，适合无人值守。持久会话用 `acpx pi -s <名字>`。
- `--approve-all` 自动批准权限请求，同时使 pi 信任项目级 `.pi/` 配置文件。
- 正常结束标志：日志末尾 `[done] end_turn`。收割时核对退出码与实际产出。
- `--timeout <秒>` 限定等待时长；并发 fanout 时每条命令配合 `run_in_background: true`。

## 系统提示词注入

pi 按以下位置自动发现提示词文件，受信任的项目文件优先于全局文件，同名文件叠加而非合并：

| 文件 | 作用 | 项目级 | 全局 |
|---|---|---|---|
| `SYSTEM.md` | 完全替换默认系统提示词 | `<运行目录>/.pi/SYSTEM.md` | `~/.pi/agent/SYSTEM.md` |
| `APPEND_SYSTEM.md` | 在默认系统提示词后追加 | `<运行目录>/.pi/APPEND_SYSTEM.md` | `~/.pi/agent/APPEND_SYSTEM.md` |

角色模板一律走 `APPEND_SYSTEM.md`：保留 pi 默认提示词里的工具使用能力，只叠加角色规范。仅当角色需要彻底替换行为时才用 `SYSTEM.md`。

## 工具启用控制

`<运行目录>/.pi/settings.json` 的 `defaultTools` 决定启动时启用的工具：

```json
{ "defaultTools": ["read", "grep", "find", "ls"] }
```

- 普通名称列表：替换默认选择。空数组 `[]`：关闭全部内置工具。
- `+name` / `-name` 条目：在内置工具的选择上增减；实测移除不了扩展注册的工具。
- 内置工具全集：`read`、`bash`、`powershell`、`edit`、`write`、`grep`、`find`、`ls`。
- 项目级 `.pi/settings.json` 覆盖全局 `~/.pi/agent/settings.json`。
- 能力边界（实测）：`defaultTools` 能硬性禁用 bash、edit、write 等内置写入工具；宿主机全局扩展注册的工具（诊断、委托类）仍会加载，靠角色正文的规则约束行为。需要更严格的隔离时，缩减宿主机的全局扩展。

pi 自带的 `-t` / `-xt` 命令行参数无法穿过 `acpx pi` 传递，工具控制只能走 settings 文件。

## 并发与隔离

- 写文件的代理各自独占一个 worktree：`git worktree add .worktrees/tNN -b fanout/tNN`，角色文件与配置复制进 worktree 内的 `.pi/`。
- 只读代理共享主仓库目录。
- 任务提示词 `prompts/tNN.md` 与日志 `.agent-results/` 放在主仓库目录；`-f` 一律使用绝对路径。

## 新角色配方

1. 写 `templates/<角色>.md`：角色定位、工作规则、完成报告格式（模板正文经 `.pi/APPEND_SYSTEM.md` 注入）。
2. 按能力边界决定 `defaultTools`：只读角色给 `read`、`grep`、`find`、`ls`；执行角色用默认全集；需要建角色专属 `templates/settings-<角色>.json`。
3. 按读写性质选运行目录：写文件进 worktree，只读用主仓库。
