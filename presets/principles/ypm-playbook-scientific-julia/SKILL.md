---
name: ypm-playbook-scientific-julia
description: 用 Julia 编写或重构科学计算代码的工作流：数值正确性优先，优先降低编译压力（ specialization 扩散、TTFP、预编译负载）与运行负载，测试负荷最小化。适用于新增数值算法/状态方程/求解器/自动微分代码、优化既有 Julia 模块、或说"编译太慢""测试太重""降低 TTFP"的任务。日常编码原则由 principle-better-performance-julia 承担，本 playbook 负责工序、量测与验收。
---

# 科学 Julia 计算 · 低编译压力工作流

## 任务边界

- 输入是一个 Julia 工程任务：新写或重构一段数值代码（求解器、状态方程、微分方程、数据处理管线），性能与编译负载是明确优先项。
- 本 playbook 给出工序顺序、每步产物与验收判据。写法层面的具体规则（类型稳定、预分配、广播、性能宏等）一律以 `principle-better-performance-julia` 为准，此处不重复。
- 不用于：诊断既有性能回归（用 perf 类流程）、纯 API/业务逻辑开发、非 Julia 语言。

## 开始所需输入（参数，逐项向任务索取，禁止写死在一次任务里）

| 参数 | 含义 | 缺省处理 |
| --- | --- | --- |
| `<module>` | 目标模块/包路径 | 必须提供 |
| `<workloads>` | 代表性运行清单：1–3 个真实调用（脚本或 `include` 片段） | 必须提供；没有就先与任务确认一个最小可运行调用 |
| `<julia>` | Julia 版本与可用性 | `julia --version` 实测 |
| `<tolerance>` | 数值容差（相对/绝对） | 由算法精度要求给出；无依据时不算通过 |
| `<budgets>` | 编译负载预算：冷启动 TTFP 上限、方法实例增量上限 | 无既定预算时，先测基线，改动后只要求"不升" |
| 可选依赖 | BenchmarkTools、StaticArrays、TimerOutputs 等 | **默认不加**。stdlib 能完成本流程全部量测；加依赖须写明理由并记入决策日志 |

## 量测手段（全部 stdlib，先建工具再改动）

编译负载 = 冷启动代价 + 特化数量。测试负荷 = 每次改动被迫跑的测试量。二者都必须先在真实产物上量出基线，才谈降低。

```julia
# 冷启动/热态分离（编译压力代理，VERIFIED on Julia 1.11）：
# 热态同一进程内重复调用取最小值 = 纯执行；首次调用减热态 = 编译代价
function ttfp_and_warm(f, args...)
    t_cold = @elapsed f(args...)                       # 首次：含 JIT 编译
    t_warm = minimum((@elapsed f(args...)) for _ in 1:5)  # 热态：纯执行（注意是 minimum 不是 min）
    return (cold = t_cold, warm = t_warm, compile_like = t_cold - t_warm)
end
# 全进程冷启动（含包加载与预编译）用 shell 口径量（VERIFIED）：
#   time julia -e 'using <module>; <workload 首次调用>'
# 注意：-J "" / -J /dev/null 在 1.11 均报错，不存在的 sysimage 路径不可用

# 已编译特化实例计数（VERIFIED on Julia 1.11）：只统计真实生成过代码的实例，
# 定义方法不计数，调用后才出现——正是 编译负载 的直接代理。
# 关键坑：Method.specializations 单特化时是 MethodInstance，多特化时是 SimpleVector，必须分支处理
n_specs(sp::Core.MethodInstance) = 1
n_specs(sp::Core.SimpleVector) = count(!isnothing, sp)
n_specs(sp) = count(!isnothing, collect(sp))          # 其他 Julia 版本的 Dict 口径兜底
spec_count(f) = sum(n_specs(m.specializations) for m in methods(f); init = 0)
function specialization_report(mod::Module)   # 按模块隔离口径，names(all=true) 才含未导出函数
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

# 分配量测（VERIFIED）：@time / @allocated，热态后重复调用

# 类型检查（VERIFIED 用法）：写文件用函数形式，宏的 report= kwarg 在 1.11 不受支持
using InteractiveUtils
open("warntype.txt", "w") do io
    code_warntype(io, f, Tuple{参数类型...})   # 显式类型元组，避免方法匹配歧义
end
# 判读标准见 principle-better-performance-julia §5：只看关键路径的 Any/Union，非所有高亮都是错误
```

## 阶段表

每行是一个可独立交付、可单独验证的单元。上一行验收不过，不进入下一行（sequence-verifiable-units）。

| # | 阶段 | 动作 | 产物 | 验收判据 | 回退/停止 |
| --- | --- | --- | --- | --- | --- |
| S0 | 基线与工具 | 建量测脚本；在**未改动的现状**上量：冷启动 TTFP、热态耗时、分配、特化实例数、现有测试全量耗时 | 基线数字表 + `ops/measure_loads.jl` | 脚本在真实 `<workloads>` 上跑通，数字可复现（重跑一次同量级） | 量不出来 = NOT VERIFIED，先修工具，禁止凭感觉优化 |
| S1 | 类型地基 | 定核心数据结构：具体元素类型容器、参数化 struct、`zero/oneunit/oftype` 语义（原则 §1） | 类型骨架 + `@code_warntype` 关键路径检查记录 | 关键计算路径无意外 `Any`/抽象字段；同一输入下返回类型可推断 | warntype 仍红 → 用 `attack-the-premise`：多个补丁都失效说明假设错了，回到 S1 重选表示，不再叠 guard |
| S2 | 数值正确性闸门 | 对参考值/守恒量/解析极限写出**行为测试**（原则 §6；test-behavior 口径：测输入→输出与副作用，不测内部调用）。边界语义要先查后断：如浮点除零得 `Inf` 而非 `DivideError`（实测确认） | `test/` 最小测试集 + 容差依据 | 边界值、空数组、`Float32`/对偶数等泛型输入通过 `<tolerance>` 判定 | 无容差依据的结果差异 = 不许合入 |
| S3 | 计算内核 | 热点放进函数、函数屏障隔离动态数据准备；先写清正确，不投机上宏（原则 §1.4、§4） | 内核函数 | S2 测试全绿；热态耗时不差于基线 | 任何"看起来更快"但 S2 变红的改动一律回退 |
| S4 | 内存与循环 | 预分配复用（`!` 版本）、广播融合或拆开缓存、列优先、视图/复制语义明确、小定长数组才考虑 StaticArrays（原则 §2） | 就地版本 + 分配记录 | `@time`/`@allocated` 分配数相对基线下降或持平；结果经 S2 复验 | 为省一次复制引入别名 bug → 回退到复制版，把教训写进结构 |
| S5 | 编译负载专项 | 收特化扩散：热点入口按具体类型限定或用 `nospecialize` 止扩散；`precompile`（1.11 原生 `Base.precompile`）只对确有 TTFP 痛点的热路径使用 | 特化实例数与 TTFP 对比表 | `compile_like` 与实例增量相对 S0 不升；StaticArrays 仅用于小尺寸（原则 §2.6 警告） | 超 `<budgets>` → 用 `spec_count` 定位是哪个函数在膨胀（实测：宽签名被 3 类元素调用即产生多实例）再修，不盲目删参数化 |
| S6 | 测试负荷收口 | 分级：快速行为集与性能/长回归集分文件（stdlib `Test` 无原生 tag 过滤，用 `test/quick.jl` + `test/long.jl` 分离），入口命令化 | 两级测试文件 + 单命令入口 | 开发环内只跑 `julia --project -e 'include("test/quick.jl")'` 即绿；全量集仅在交付前跑一次且通过 | 出现"改 A 必重跑全量"→ 说明测试耦合了实现，拆分而非加机器 |
| S7 | 性能宏（仅在证据要求时） | 只有 S0–S6 量测指出热点仍在，才考虑 `@inbounds`/`@simd`；`@fastmath` 与 `set_zero_subnormals` 在数值求解、相平衡、收敛判断、自动微分场景**默认禁用**，解禁须有专项验证记录 | 逐处标注适用前提的宏改动 | 每项前提（索引安全、迭代独立、语义差异允许）单独成文并复验 S2 | 无实测收益 → 撤掉宏，恢复原状 |
| S8 | 验收与固化 | 出 S0→S7 差值表（explain-the-number 口径：冷启动/热态分开报，说清测的是什么）；量测脚本与分级测试结构随代码入库；反复出现的纠正落成检查 | 差值表 + 决策日志 + 汇报 | 全部数字来自真实运行输出，无自报 | 任何 INCONCLUSIVE 项如实列出，不凑数 |

## 严格程度分档

- 可逆、影响小（新文件、局部写法）：走完单元验收即可，不留书面审查。
- 改变数值语义或不可逆（上 `@fastmath`、删兼容路径、改收敛行为、动共享数组语义）：改动前必须引用 S0 基线与 S2 测试作为关口证据；拿不到 = 不动。
- 拟议的数小时长运行（大规模基准、全量回归）：设一次启动前检查点，尊重既有授权，不用沉默代替决定（never-block-on-the-human：可逆的常规量测直接做）。

## 并行与派发

只沿真实独立边界并行（如互不写同一文件的多个算例子模块），执行者用独立 worktree 或分支；共享状态的写入先按所有者拆开再串行。需要 subagent 时交给大臣派发，本 playbook 不指定未经任命的 Agent 或模型。

## 验证与回退总则

- 每个单元三段式：假设 → 最小改动 → 在真实产物上测量。有改进保留，无改进回退，不做"先留下以后再说"。
- 检查实际产物（运行的 stdout、测试输出、diff），不信执行者自报；通过来得太容易时先怀疑观察方法。
- 结论只用 `VERIFIED` / `NOT VERIFIED` / `INCONCLUSIVE`；不确定不算通过，失败不隐藏。
- 委派实施须配独立审查者；执行者为迎合检查绕开真实目标时，回退并修约定，不绕检查。

## 汇报要求

交付时给出：`<module>` 与 `<workloads>`、S0→S8 差值表（冷启动 TTFP、热态耗时、分配、特化实例数、快速测试集耗时）、各阶段 VERIFIED/NOT VERIFIED/INCONCLUSIVE 状态、决策日志路径、解禁过的性能宏及其前提、以及未验证事项。区分"流程走查通过"与"目标工程数字经过真实运行验证"。

## 依据

工序与判据源自 `principle-better-performance-julia`（写法原则）编排，量测纪律配 `principle-explain-the-number`，单元推进配 `principle-sequence-verifiable-units`，工具固化配 `principle-build-the-lever`、`principle-encode-lessons-in-structure`，假设失效处置配 `principle-attack-the-premise`，测试口径配 `principle-test-behavior-not-implementation`，检查点分寸配 `principle-never-block-on-the-human`。
