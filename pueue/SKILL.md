---
name: pueue
description: 用 pueue 把长任务/批量任务丢进后台队列：不占当前 shell、可串行排队、可限并行、会话结束后继续跑、随时取回输出。当任务预计超过一两分钟、需要排队或限并行、或不想让 shell 阻塞在长命令上时使用。
---

# pueue 后台任务队列

pueue = 后台守护进程 + 命令队列。`pueue add` 立即返回，任务由 `pueued` 在后台执行，输出落盘、随时可查。

## 已验证的事实（pueue 4.0.4 实测）

- 命令**经系统 shell 执行**，`&&`、重定向、管道可用；整条命令用单引号包裹避免转义问题：`pueue add 'cmd1 && cmd2'`
- **cwd 和环境变量在 add 那一刻从客户端捕获为快照**。任务与提交时的 shell 会话解耦，之后改目录/改环境不影响已提交任务
- **`pueue wait` 的退出码恒为 0，不反映任务成败**（实测：任务以 exit 3 失败，wait 仍返回 0）。判断成败必须查 `pueue status` 或 `pueue log`
- `pueue add -p` 只输出数字任务 id，脚本用；`-l <标签>` 给任务打标；`-g <组>` 指定队列组；`-a <id>` 声明依赖（依赖失败则本任务失败）
- 组是相互独立的队列，各有并行上限：`pueue parallel <N> -g <组>`（0 = 不限）
- `pueue status -j` 返回 `{"groups":…,"tasks":{"<id>":{"status":{"Running":…}|{"Done":{"result":"Success"|"Failed":N}},…}}}`；`pueue log -j <id>` 返回 `{"<id>":{"task":{…,"path","group"},"output":"…"}}`
- daemon 没跑时所有 pueue 命令连接失败；兜底 `pueued -d` 启动

## 标准流程（按顺序执行）

### 1. 确认 daemon 可达

```bash
pueue status
```

完成条件：能看到组列表。连接失败 → `pueued -d` 后重试；再失败则报告用户，不要继续。

### 2. 用专用组隔离

要把任务加入他人队列前，先确认 default 组现状。凡提交 1 个以上任务，建专用组，不与已有任务混跑：

```bash
pueue group add <任务名>-batch
pueue parallel <N> -g <任务名>-batch   # 需要限并行时；不设则用组默认
```

完成条件：`pueue status` 里出现该组。

### 3. 提交任务

```bash
pueue add -g <组> -l <标签> -p '<命令>'
```

完成条件：拿到数字 id。提交前自查：命令里的相对路径基于 add 时 cwd 解析，所需 env 必须已在当前 shell 中（或写进命令里）。

### 4. 等待完成（限时）

```bash
timeout <秒> pueue wait -q -g <组>
```

wait 没有 timeout 参数，**必须套 `timeout`**，不要无上限阻塞。等待结束不代表成功——进入第 5 步确认。

### 5. 确认结果并取回输出

```bash
pueue status -g <组>
pueue log -f <id>          # 全文输出
```

批量时筛出失败任务：

```bash
pueue status -j | jq -r '.tasks | to_entries[] | select(.value.status.Done.result.Failed) | .key'
```

失败 → `pueue log -f <id>` 读错误，修好后 `pueue restart <id>`。完成条件：每个任务 id 都对应 Success 或已处理失败原因。

### 6. 清理

```bash
pueue clean -g <组> && pueue group remove <组>
```

完成条件：`pueue status` 里不再出现该组。临时跑一次任务的，清理是流程的一部分，不是可选项。

## 禁止事项

- **禁止 `pueue reset`**：会杀掉并清空用户所有任务
- 禁止 kill / remove / restart 不是自己提交的任务 id
- 用户的 default 组和既有组（如有）只读不动；自己只用第 2 步建的组
- `wait` 超时后不要盲目加时长重试：先 `pueue status` 看任务是在跑、排队还是卡死，再决定

## 不确定的事

- daemon 通常由系统服务管理（本机实测常驻）。`pueued -d` 只是连不上时的兜底，不适合作为常驻方案——那是 service manager 的职责
- 其他 pueue 版本的 JSON 形状可能不同：解析前先用一条小任务实测形状，不要照抄本文 jq
