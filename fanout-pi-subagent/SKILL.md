---
name: fanout-pi-subagent
description: 通过 acpx 派发带角色规范的 pi 子代理：并行 fanout、编码代理、只读审查代理。触发：需要派发子代理执行编码或审查任务、需要多个代理并行工作、需要自定义系统提示词或工具集的 pi 无人值守运行。
---

# fanout-pi-subagent

把 pi-coding-agent 装配成特定角色，经 acpx 派发为无人值守子代理。角色的两根支柱：系统提示词注入（行为规范）与工具启用控制（能力边界）。

## 内置角色

| 角色 | 用途 | 系统提示词 | 工具 | 运行目录 |
|---|---|---|---|---|
| coding-agent | 执行编码任务，可写文件 | 原生默认 | 默认全部 | worktree `.worktrees/tNN` |
| reviewer-agent | 只读审查，产出发现清单 | `templates/reviewer-agent.md` | 仅 read、grep、find、ls | 主仓库目录 |

模板路径相对本技能目录（技能加载时会给出基目录）。

## 步骤

### 1. 选角色，定运行目录

按任务性质从内置角色表选择。编码代理各自独占一个 worktree，写文件互不冲突：

```bash
git worktree add .worktrees/t01 -b fanout/t01
```

审查代理只读，直接用主仓库目录。多个审查代理可以并行读同一目录。

完成标准：运行目录存在；worktree 内 `git status` 干净。

### 2. 装配角色

coding-agent 使用 pi 原生系统提示词，无需装配。reviewer-agent 把角色模板与工具限制复制进运行目录，pi 启动时自动发现：

```bash
mkdir -p <运行目录>/.pi
cp <技能目录>/templates/reviewer-agent.md <运行目录>/.pi/APPEND_SYSTEM.md
cp <技能目录>/templates/settings-reviewer.json <运行目录>/.pi/settings.json
```

完成标准：目标文件存在且内容与模板一致。

### 3. 写任务提示词

用文件编辑工具创建 `prompts/tNN.md`：任务目标、改动边界、验收条件、产出位置。提示词是子代理唯一的需求来源，缺一项子代理就会自行猜测。

完成标准：文件已创建，验收条件可检验。

### 4. 派发

```bash
acpx --cwd "<运行目录>" --approve-all pi exec -f prompts/tNN.md 2>&1 | tee .agent-results/<角色>-tNN.log
```

并行 fanout 时每个代理一条命令，`run_in_background: true`。长任务加 `--timeout <秒>`。

完成标准：进程退出，日志含 `[done] end_turn`，退出码为 0。

### 5. 收割

逐个检查 `.agent-results/` 日志，核对实际产出：编码代理用 `git -C <worktree> status` 与 `git diff` 核对改动；审查代理核对发现清单的证据是否指向真实位置。

完成标准：每个代理的成果已核对并向用户汇报；编码代理的改动按需合并（`git -C .worktrees/tNN merge` 回主分支或由用户决定）。

## 扩展新角色

三步配方，细节见 [`references/pi-mechanics.md`](references/pi-mechanics.md)：写角色正文作为新的 `templates/<角色>.md`；按能力边界配置 `defaultTools`；按读写性质选择运行目录。
