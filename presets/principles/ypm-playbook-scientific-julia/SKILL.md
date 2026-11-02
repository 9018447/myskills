---
name: ypm-playbook-scientific-julia
description: Julia 科学计算工序 playbook：以基线先行、逐单元实测为纪律，降低编译负载（TTFP、特化实例数）与测试负荷，守住数值正确性。用于新增或重构数值代码（求解器、状态方程、自动微分、微分方程、数据管线），或当任务提出"编译太慢""TTFP 太高""测试太重"时。写法规则本体在 principle-better-performance-julia；既有性能回归的诊断另走 perf 类流程。
---

# 科学 Julia 计算 · 低编译压力工作流

## 分工

本 playbook 只管三件事：工序顺序、量测口径、验收判据。类型稳定、预分配、广播、性能宏等写法规则一律出自 `principle-better-performance-julia`，正文按其章节号引用（§1–§6）。

## 开始所需输入（参数化，逐项向任务索取）

| 参数 | 含义 | 缺省处理 |
| --- | --- | --- |
| `<module>` | 目标模块/包路径 | 必须提供 |
| `<workloads>` | 1–3 个代表性真实调用（脚本或 `include` 片段） | 必须提供；没有先确认一个最小可运行调用 |
| `<julia>` | Julia 版本 | `julia --version` 实测 |
| `<tolerance>` | 数值容差（相对/绝对） | 须给出精度依据；无依据不算通过 |
| `<budgets>` | 冷启动 TTFP 上限、特化实例增量上限 | 无既定预算时先测基线，改动后要求"不升" |
| 可选依赖 | BenchmarkTools、StaticArrays、TimerOutputs 等 | 默认 stdlib 走完全部量测；加依赖写明理由并入决策日志 |

## 量测口径（stdlib-only）

编译负载 = 冷启动代价 + 已编译特化数；测试负荷 = 每次改动被迫跑的测试量。两者先于任何改动量出基线。

```julia
# 冷启动/热态分离（VERIFIED on Julia 1.11）：首次调用减热态最小值 = 编译代价
function ttfp_and_warm(f, args...)
    t_cold = @elapsed f(args...)                          # 首次：含 JIT 编译
    t_warm = minimum((@elapsed f(args...)) for _ in 1:5)  # 热态：纯执行（minimum，非 min）
    return (cold = t_cold, warm = t_warm, compile_like = t_cold - t_warm)
end
# 全进程冷启动（含包加载与预编译）交给 shell：
#   time julia -e 'using <module>; <workload 首次调用>'
# 坑：-J "" / -J /dev/null 在 1.11 均报错，配置不会告诉你

# 已编译特化实例计数（VERIFIED）：方法定义不计数，真实调用后才出现——编译负载的直接代理
# 坑：Method.specializations 单特化时是 MethodInstance，多特化时是 SimpleVector，须分支处理
n_specs(sp::Core.MethodInstance) = 1
n_specs(sp::Core.SimpleVector) = count(!isnothing, sp)
n_specs(sp) = count(!isnothing, collect(sp))             # 其他版本 Dict 口径兜底
spec_count(f) = sum(n_specs(m.specializations) for m in methods(f); init = 0)
function specialization_report(mod::Module)  # names(all=true) 才含未导出函数；跳 # 前缀合成名
    rows = []
    for n in names(mod; all=true)
        startswith(String(n), "#") && continue
        fn = try getfield(mod, n) catch; continue end
        fn isa Function || continue
        total = spec_count(fn)
        total > 0 && push!(rows, (fname = n, instances = total))
    end
    return rows
end

# 分配：@time / @allocated，热态后重复调用（VERIFIED）

# 类型检查（VERIFIED 用法）：写文件用函数形式；宏的 report= kwarg 在 1.11 不受支持
using InteractiveUtils
open("warntype.txt", "w") do io
    code_warntype(io, f, Tuple{参数类型...})   # 显式类型元组，避免方法匹配歧义
end
# 判读只看关键路径的 Any/Union（原则 §5）：高亮≠错误
```

量测一经跑通就固化为 `<module>` 内一个脚本（如 `ops/measure_loads.jl`），此后每单元重跑脚本、重写量测（`principle-build-the-lever`）。

## 阶段表

每行一个可独立交付、可单独验证的单元；上一行判据不绿，不进下一行。推进纪律见「验证与回退」一节。

| # | 阶段 | 动作 | 产物 | 完成判据 | 回退/停止 |
| --- | --- | --- | --- | --- | --- |
| S0 | 基线 | 建量测脚本，在未改动现状上量：冷启动 TTFP、热态耗时、分配、特化实例数、现有测试全量耗时 | 基线数字表 + `ops/measure_loads.jl` | 脚本在真实 `<workloads>` 跑通，重跑一次同量级 | 量不出即 NOT VERIFIED：先修工具，凭数据说话 |
| S1 | 类型地基 | 具体元素类型容器、参数化 struct、`zero/oneunit/oftype` 语义（原则 §1） | 类型骨架 + warntype 检查记录 | 关键路径无意外 `Any`/抽象字段；同一输入返回类型可推断 | 多个补丁后 warntype 仍红 = 假设错了：回 S1 重选表示，停止叠 guard（`principle-attack-the-premise`） |
| S2 | 正确性闸门 | 对参考值、守恒量、解析极限写行为测试：只断言输入→输出与副作用（原则 §6）；边界语义先查后断——浮点除零得 `Inf` 而非 `DivideError`（实测） | `test/` 最小集 + 容差依据 | 边界值、空数组、`Float32`/对偶数等泛型输入过 `<tolerance>` | 结果差异缺容差依据 = 不合入 |
| S3 | 计算内核 | 热点进函数、函数屏障隔离动态数据准备；先写正确，宏留到 S7（原则 §1.4、§4） | 内核函数 | S2 全绿；热态耗时 ≥ 基线 | "看似更快"但 S2 变红的改动一律回退 |
| S4 | 内存与循环 | 预分配复用（`!` 版本）、广播融合或拆开缓存、列优先、视图/副本语义明确、小定长才 StaticArrays（原则 §2） | 就地版本 + 分配记录 | `@allocated` 相对基线降或持平；结果经 S2 复验 | 省复制引入别名 bug = 回退副本版，教训写进结构 |
| S5 | 编译负载专项 | 热点入口限定具体类型或 `nospecialize` 止扩散；1.11 原生 `Base.precompile` 只用于确有 TTFP 痛点的热路径 | 实例数与 TTFP 对比表 | `compile_like` 与实例增量相对 S0 不升；StaticArrays 仅小尺寸（原则 §2.6） | 超 `<budgets>`：用 `spec_count` 定位膨胀函数（宽签名被 3 类元素调用即生多实例，实测），据点修 |
| S6 | 测试负荷收口 | 快速行为集与性能/长回归集分文件（stdlib `Test` 无 tag 过滤），各配单命令入口 | `test/quick.jl` + `test/long.jl` | 开发环只跑 `julia --project -e 'include("test/quick.jl")'` 即绿；全量集交付前跑一次且通过 | "改 A 必重跑全量" = 测试耦合了实现：拆测试，非加机器 |
| S7 | 性能宏（证据门） | 仅当 S0–S6 实测显示热点仍在，才逐项评估 `@inbounds`/`@simd`；数值求解、相平衡、收敛判断、自动微分场景保持 IEEE 语义，`@fastmath`/`set_zero_subnormals` 进入须有专项验证记录（原则 §4） | 逐处标注前提的宏改动 | 每项前提（索引安全、迭代独立、语义差异允许）单独成文并复验 S2 | 实测无收益 = 撤宏恢复原状 |
| S8 | 验收与固化 | 出 S0→S7 差值表；量测脚本与分级测试随代码入库；把反复出现的纠正落成检查（`principle-encode-lessons-in-structure`） | 差值表 + 决策日志 + 汇报 | 每个数字可指到一次真实运行输出 | INCONCLUSIVE 如实列出，与通过项分列 |

## 验证与回退

每单元三段式：假设 → 最小改动 → 在真实产物上测量（运行的 stdout、测试输出、diff）。有改进保留，无改进回退。结论只用 `VERIFIED` / `NOT VERIFIED` / `INCONCLUSIVE`，不确定按未过处理。通过来得太容易时先怀疑观察方法。委派实施配独立审查者；检查本身出错时单独修检查。

## 严格程度分档

- 可逆且影响小（新文件、局部写法）：单元验收即过，免书面审查。
- 改数值语义或不可逆（上 `@fastmath`、删兼容路径、改收敛行为、动共享数组）：改动前须引用 S0 基线与 S2 测试作关口证据。
- 数小时长运行（大规模基准、全量回归）：设一次启动前检查点，等决定再动。可逆的常规量测直接做（`principle-never-block-on-the-human`）。

## 并行与派发

只沿真实独立边界并行（互不写同一文件的算例模块），执行者各占独立 worktree 或分支；共享写入先按所有者拆开再串行。subagent 交大臣派发，所用 Agent 与模型以已任命名单为限。

## 汇报

交付给出：`<module>` 与 `<workloads>`、S0→S8 差值表（冷启动与热态分开报，写明每格测的是什么，`principle-explain-the-number`）、各阶段三态结论、决策日志路径、S7 解禁项及其前提、未验证事项。末行区分"流程走查通过"与"工程数字经真实运行验证"。

## 依据

写法规则全部出自 `principle-better-performance-julia`；工序编排配 `principle-sequence-verifiable-units`，量测纪律配 `principle-explain-the-number`，工具固化配 `principle-build-the-lever` 与 `principle-encode-lessons-in-structure`，假设失效配 `principle-attack-the-premise`，测试口径配 `principle-test-behavior-not-implementation`，关口与检查点配 `principle-never-block-on-the-human`。
