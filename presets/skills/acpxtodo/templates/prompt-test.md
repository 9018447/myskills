# 派发 Prompt 模板：全量测试票（tNN）

向该票 worktree（`.worktrees/{{tNN}}`）派发 codex 测试 agent，headless 规则同其他派发（prompt/日志/watcher 带票号）。**派发命令必须带 env 前缀** `HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 INITIAL_AGENT_MODE=agent-full-access`——codex 的 ACP 适配器默认 workspace-write 沙箱且不理会 config.toml，家目录写（juliaup 锁文件等）会报 `Read-only file system`。

---

## 任务

任务只有一件：在 `.worktrees/{{tNN}}` 内跑一次全量测试套件，产出带失败清单的报告。不改实现代码，不向下派发。

## 环境对齐（固定段）

跑测试之前先跑项目的环境对齐检查（如本仓 `agent/envcheck.jl`，比对根环境与嵌套环境 Manifest 的共享包解析版本，退出码非 0 即漂移）。漂移必须先对齐再跑——包预编译缓存按"包版本 + 语言版本"键控，版本漂移意味着整套依赖重编（几十分钟级），且测试结果落在与包 CI 不同的依赖版本上。

对齐策略：**update 落后的一方**（落后环境 `Pkg.update(); Pkg.precompile()` 追平领先一方），不打版本钉子——`=` 精确钉会被传递依赖的版本下界卡死，越钉越打地鼠。

## 执行规则（固定段）

1. 长套件（单轮 ≥20 分钟）用 `/pueue` 执行全量运行（`which pueue` 定位路径）；运行任务进队列，agent 进程中断不连坐。
2. **回归命令的退出码必须直取**：输出重定向到日志文件、`$?` 立即追加进同一日志——`<命令> > <log> 2>&1; echo EXIT=$? >> <log>`。管道会吃掉退出码（`julia ... | tail -15; echo $?` 取到的是 tail 的 0，套件实际失败差点被当绿收官）。结果判定以日志内的 `EXIT=` 行和 Pkg 成功行双证为准。
3. 测试期间不改实现代码；发现环境问题先对齐再跑，不绕过。
