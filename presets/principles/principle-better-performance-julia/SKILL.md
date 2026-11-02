---
name: principle-better-performance-julia
description: 在编写、修改、审查和重构 Julia 代码时采用的日常编码原则。涵盖类型稳定、函数组织、数组与内存、数值正确性、泛型编程，以及需要时才使用的性能测量和底层优化。适用于 Julia 科学计算、数值算法、状态方程、自动微分和一般项目开发。
---

# Julia 编码原则

## 定位

这是**编写 Julia 代码时使用的原则**，适用于新增功能、修改旧代码、代码审查和重构。写代码时自然遵守相关原则；只在确实需要诊断速度或内存问题时使用性能工具。

优先保持计算正确、行为清楚、容易维护，并尊重项目现有接口、依赖和 Julia 版本。写数值算法时尤其要保护精度、收敛行为、边界条件和自动微分兼容性。不要为了让代码看起来“更快”就牺牲这些性质。

## 1. 类型和数据结构

1. **优先使用具体的容器元素类型和结构体字段类型。** 避免在关键数据结构中随意使用 `Vector{Real}`、`Vector{Number}`、`field::Real`、`field::Any`；需要容纳不同类型时，考虑参数化结构体 `struct Holder{T}; value::T; end`。但 `f(x::Real)`、`f(x::Number)` 这样的泛型方法签名很正常，不要误删。
2. **让同一类输入尽可能得到可推断的返回类型。** 注意 `if ... else ...` 不同分支返回 `0`、`0.0` 或其他类型的情况。需要与输入类型一致的值时，优先考虑 `zero(x)`、`oneunit(x)`、`oftype(x, y)`，根据实际数学含义选择。
3. **避免同一局部变量在循环中无意改变类型。** 例如先赋整数 `1`，之后又存浮点数。初始化时使用符合算法要求的类型；保留对 `Float32`、`BigFloat`、对偶数等数值类型的支持，不要无理由硬编码 `Float64`。
4. **热点计算放进函数中。** 当数据准备阶段难以确定类型时，使用函数屏障（function barrier）：外层准备数据，内层函数接收具体数据并完成计算。按职责拆分函数，但不要为了拆分而拆分。
5. **注意闭包捕获变量（captured variable）。** 内层函数使用外层局部变量时，某些写法可能导致额外装箱或类型推断问题。只有确实存在问题时才考虑 `let` 固定捕获值或使用具体类型声明。

### 具体元素类型与参数化字段

```julia
# 🔴 反例：元素实际有两种类型，使用 Vector{Real} 会增加动态处理的可能性。
x = Real[1, 2.0, 3.0]

# 数据确实需要统一为 Float64 时：
y = Float64[1, 2, 3]

# 对不同具体类型都适用的数据结构：
struct Holder{T}
    value::T
end

# 泛型参数签名是正常的：
squared(x::Real) = x * x
```

🔴 **警告：** 不要机械地把一切转换为 `Float64`。若异构元素是业务要求，也可以选择保留异构数据；先理解目的。

### 分支返回类型与同类型常量

```julia
# 🔴 反例：某些输入下，两个分支的返回类型不同：
nonnegative_bad(x) = x < 0 ? 0 : x

# 需要与 x 相同类型的零时：
nonnegative(x) = x < 0 ? zero(x) : x

# 其他常用形式：
unit_for(x) = oneunit(x)
converted_like_x(x, y) = oftype(x, y)
```

`zero(x)` 表示加法单位元；`oneunit(x)` 返回同类量的乘法单位元（与 `one(x)` 的单位语义可能不同）；`oftype(x, y)` 将 `y` 转为 `x` 的类型。🔴 **警告：** 转换可能失败或损失精度。只有算法需要时才使用。

### 局部变量的类型不要无意跳变

```julia
# 🔴 反例：累加变量从整数变成浮点数
function varying_accumulator()
    a = 1
    for k in 1:10
        a /= k + 0.5
    end
    return a
end

function float_accumulator()
    a = 1.0
    for k in 1:10
        a /= k + 0.5
    end
    return a
end
```

🔴 **警告：** 当代码需要 `Float32`、`BigFloat` 或对偶数时，应根据输入生成初值，例如 `zero(eltype(x))` 或 `oneunit(eltype(x))`，而非始终使用 `1.0`。

### 函数屏障：把数据准备与计算分开

```julia
function scale_kernel!(a, factor)
    for i in eachindex(a)
        a[i] *= factor
    end
    return a
end

function prepare_and_scale(n, use_float)
    a = use_float ? ones(Float64, n) : ones(Int, n)
    return scale_kernel!(a, 2)
end
```

内层函数按 `a` 的具体类型进行编译。函数应按照职责拆分；许多简短函数也可以由编译器内联，过多拆分没有必然收益。

### 闭包捕获变量

```julia
function make_multiplier(r)
    r = abs(r)
    return let r = r
        x -> r * x
    end
end
```

闭包从外层获取变量称为“捕获”。某些重赋值或不明确类型的场景会产生装箱或类型推断问题。新版 Julia 能处理不少简单场景；优先写清晰的代码，确认问题后再改用 `let` 或具体类型声明。

## 2. 数组、内存和循环

1. **普通 Julia 数组按列存储。** 对 `A[i, j]` 的双重循环，通常把第一个索引 `i` 放在最内层；也要考虑算法依赖、数组实际存储方式和可读性。
2. **反复计算时优先考虑预分配并复用输出。** 可以提供 `compute!(out, args...)` 这样的就地修改版本。函数名末尾的 `!` 表示可能修改传入对象，真正减少分配的是内存复用，不是名字本身。
3. **合理使用广播。** `f.(x)`、`.=`, `@.` 能进行逐元素运算，多个带点操作通常能融合，减少中间数组。但如果融合导致昂贵表达式被重复计算，就拆开并缓存结果；常规 `for` 循环也完全可以使用。
4. **明白切片与视图的区别。** `A[:, 1:10]` 通常复制数据；`@view`、`@views` 可避免元素复制，但与原数组共享内存。计算中涉及别名、写入或独立副本时必须明确语义。
5. **不要把“避免复制”当作绝对原则。** 对反复处理的不连续、不规则访问数据，先复制为连续数组有时能提升总体效率；应连复制时间一起衡量。
6. **小型、尺寸固定的向量或矩阵可考虑 `StaticArrays.jl`。** 认识 `SVector`、`SMatrix`、`MVector`、`MMatrix` 和 `SA[...]`。大型或尺寸动态变化的数组继续使用普通 `Array`，避免因过度静态化导致编译成本增加。
7. **避免在高频循环中反复 `println()` 或写日志。** 必需的错误信息和调试信息要保留，可以降低输出频率或在适当位置输出。

### 预分配与 `!` 命名

```julia
# 返回新数组：
result(x) = x .^ 2 .+ 1

# 修改调用方提供的数组：
function result!(out, x)
    out .= x .^ 2 .+ 1
    return out
end

x = rand(1000)
out = similar(x)
result!(out, x)
```

输出数组通常应在需要多次调用的循环外预先分配。`!` 是“可能修改输入对象”的约定，不是性能开关。使用共享数组或视图时，应检查是否存在不期望的原地覆盖。

### 广播与融合

```julia
out .= sin.(x) .+ cos.(x)
@. out = sin(x) + cos(x)
```

带点操作可合并成一次逐元素循环，减少中间结果的分配。`for` 本身并不慢，也可能更清楚、更易控制。若广播融合会让某个昂贵操作多次计算，则先算出中间量再复用。

### Julia 的列优先数组顺序

```julia
function scale_matrix!(A)
    for j in axes(A, 2)
        for i in axes(A, 1)
            A[i, j] *= 2
        end
    end
    return A
end
```

对普通稠密矩阵，先连续访问第一索引通常更符合内存布局。计算依赖必须先得到保证。对特殊数组或不同存储方式，不应照搬循环顺序。

### 切片、视图与连续副本

```julia
copied = A[:, 1:10]       # 通常复制元素
shared = @view A[:, 1:10] # 不复制元素，共享 A 的存储

@views B .= A[:, 1:10] .+ 1
```

🔴 **警告：** `shared` 的写入会影响 `A`。若反复对非连续或不规则数据做运算，`copy(shared)` 有时比反复跨步访问更合适；要把复制开销算入整个工作量。

### 小型静态数组

```julia
using StaticArrays

v = SVector(1.0, 2.0, 3.0)
w = SA[1.0, 2.0, 3.0]
M = @SMatrix [1.0 2.0; 3.0 4.0]

# 需要可变元素时，还可评估 MVector、MMatrix。
```

`StaticArrays.jl` 适用于尺寸很小且编译时已知的数组。🔴 **警告：** 不要把大型矩阵改成静态矩阵，这可能导致编译和代码生成成本变高。

### 循环中 I/O

```julia
# 🔴 反例：大量打印会占用时间：
for i in eachindex(x)
    # 🔴 反例：不要每次无条件 println(i, ": ", x[i])
end

# 如果必须输出进度，可以在有意义的间隔打印。
```

🔴 **警告：** 不要随意删除业务所需的异常报告、检查或日志。

## 3. 数值计算的小规则

1. 只有少数标量相加时，直接写 `x + y + z`，通常无需为了 `sum([x, y, z])` 创建临时数组；但注意浮点数加法顺序可能影响最后几位。
2. 需要复数的模平方时，优先考虑 `abs2(z)`，而非 `abs(z)^2`；对于其他数值类型，也要确认预期语义。
3. 需要整数除法且**向零截断**时，用 `div(x, y)`；需要**向下取整**用 `fld(x, y)`，需要**向上取整**用 `cld(x, y)`。不要把 `/` 和这些运算当作可以随意互换。
4. 遵守输入是否允许被修改的约定，处理好数组别名、边界索引和空数组等情况。使用自定义数值类型或自动微分时，避免不必要的类型转换。

### 几个小运算

```julia
s = x + y + z   # 少量标量相加，无须 sum([x, y, z]) 创建数组
q = abs2(z)     # 复数模平方
k = div(7, 3)   # 2：向零截断
m = fld(-7, 3)  # -3：向下取整
n = cld(7, 3)   # 3：向上取整
```

🔴 **警告：** 浮点加法顺序可能改变结果的末位，不能无条件把表达式替换后宣称数值完全相同。

## 4. 底层性能手段：有条件才使用

- 🔴 **警告 — `@inbounds`**：可省略数组越界检查，但一旦索引错误可能崩溃或损坏数据。只有已证明索引安全时才放在适当的小范围内；不应默认覆盖全部代码。
- 🔴 **警告 — `@simd`**：写在适合的 `for` 循环前，允许编译器向量化及某些迭代重排。先确认迭代间依赖和内存重叠问题；这不是多线程，也不保证提速。含合法归约的循环需单独检查其语义。
- 🔴 **警告 — `@fastmath`**：允许放宽浮点运算规则，可能改变舍入、`Inf`、`NaN` 等行为。科学计算默认不添加；明确允许数值差异、并已验证时才考虑。既可修饰表达式，也可修饰循环或代码块。
- 🔴 **警告 — `set_zero_subnormals`**：`set_zero_subnormals(true)` / `set_zero_subnormals(false)` 控制是否允许把次正规浮点数视作零。会改变数值语义，效果依赖硬件；不要在通用库中擅自改变浮点环境。

### 性能宏的适用前提

#### `@inbounds`：需要先保证索引安全

```julia
function double!(out, x)
    @assert axes(out) == axes(x)
    @inbounds for i in eachindex(out, x)
        out[i] = 2 * x[i]
    end
    return out
end
```

🔴 **警告：** 越界检查被跳过时，索引错误可能崩溃或损坏数据。可把宏限制在一条语句或局部循环内，不要大范围无条件启用。

#### `@simd`：需要考虑迭代间依赖

```julia
function double_independent!(out, x)
    @assert axes(out) == axes(x)
    @inbounds @simd for i in eachindex(out, x)
        out[i] = 2 * x[i]
    end
    return out
end
```

🔴 **反例：** 下面的计算有跨迭代依赖，不可随意重排：

```julia
for i in 2:length(x)
    x[i] = x[i-1] + 1
end
```

合法归约需要另外分析，例如并行化可能改变浮点求和顺序。`@simd` 是允许编译器进一步优化的提示，不保证一定生成向量指令，也不是多线程。

#### `@fastmath`：会改变浮点规则

```julia
# 在精度允许且经过验证时才考虑：
@fastmath y = (a + b) * c
```

🔴 **警告：** `@fastmath` 可放在表达式、循环或语句块之前，可能改变 `Inf`、`NaN` 和浮点结合顺序等行为。数值求解器、相平衡、临界性质、自动微分、收敛判断中默认不使用。

#### 次正规浮点数

🔴 **警告：** `set_zero_subnormals(true)` 允许把极接近零的次正规浮点输入/输出按零处理，可能提高特定硬件上的速度；`set_zero_subnormals(false)` 请求严格处理。改变这些语义可能影响数值关系和结果，不要在通用函数中擅自设定。

## 5. 需要检查性能时，正确使用工具

这部分是**诊断手段**，不是日常编码的强制流程。

- **`@time`**：快速查看耗时、分配；首次调用可能包含编译和初始化开销，先预热再比较重复运行。
- **`@code_warntype`**：查看类型推断情况。重点看关键路径里的 `Any`、抽象字段和无法推断的值，不要把所有醒目显示都认定为错误。
- **`Profile`**：Julia 标准库的采样性能分析工具，用于找耗时位置。
- **`BenchmarkTools.jl`**：`@btime` 显示简明基准结果（通常是样本中的最短耗时及内存分配）；`@benchmark` 提供分布和详细统计，包括中位数。基准重复次数由配置和时间预算决定，不固定为 10,000 次。外部变量用 `$` 插值；对修改输入的函数使用 `setup` 并考虑 `evals=1`，避免不同测量互相影响。长时间运行的函数不要盲目重复大量测量。
- **其他可选工具**：`ProfileView.jl`（性能分析可视化）、`Traceur.jl`（潜在类型/性能问题检查，先确认兼容性）、`TimerOutputs.jl`（分阶段计时）、`Cthulhu.jl`（深入分析类型推断）。没有需要就不要添加依赖。

### `@time`、类型推断、`Profile`

```julia
using InteractiveUtils
using Profile

f(x) = sum(abs2, x)
x = rand(10_000)

f(x)                 # 预热，避免把首次编译全部算进运行成本
@time f(x)          # 粗看时间和分配
@code_warntype f(x) # 检查类型推断

Profile.clear()
@profile for trial in 1:100
    f(x)
end
Profile.print()
```

- `@time` 的首次运行可能含编译和初始化。特别是微小函数，不要用单次 `@time` 做结论。
- `@code_warntype` 重点关注性能关键路径中的 `Any`、动态字段和真正影响优化的推断问题；并非所有显示差异都是错误。
- `Profile` 是 Julia 标准库的采样分析器，用于确定程序耗时的位置。

### `BenchmarkTools.jl`

```julia
using BenchmarkTools

@btime f($x)
trial = @benchmark f($x)
```

- `@btime` 输出简明基准，通常取最短样本时间和分配情况。
- `@benchmark` 提供包括最小值、中位数和最大值在内的统计信息。
- `$x` 将外部变量插入基准表达式，避免全局变量查找干扰。
- 🔴 **警告：** 基准运行次数受默认样本上限、时间预算和参数影响，**不是固定执行 10,000 次**。对运行很慢的代码合理设置 `seconds`、`samples`。
- 这类基准主要测已编译代码的执行，不等同于用户首次启动程序的整体用时。

#### 会修改输入的函数

```julia
function square!(a)
    a .*= a
    return a
end

@benchmark square!(work) setup=(work = copy($x)) evals=1
```

`setup` 给每次测试建立相同的初始数据，`evals=1` 避免一个样本内连续修改同一数组。若真实调用必须包含复制操作，端到端性能测试就必须把复制也算进去。

### 其他诊断工具

| 工具              | 主要用途                   | 使用说明                            |
| ----------------- | -------------------------- | ----------------------------------- |
| `ProfileView.jl`  | 可视化耗时调用栈           | 需要看哪些调用占用时间时使用        |
| `Traceur.jl`      | 检查可能的类型/性能问题    | 先确认对当前 Julia 版本的兼容性     |
| `TimerOutputs.jl` | 计算不同阶段各花多久       | 需要分阶段计时时使用                |
| `Cthulhu.jl`      | 深入查看函数内部的类型推断 | `@code_warntype` 无法说明原因时使用 |

这些工具是可选依赖，不应在每个 Julia 项目中强制安装。

## 6. 代码正确性优先

- 新写或修改数值函数时，考虑普通输入、边界值、异常输入及类型变化。必要时使用 Julia 标准库 `Test`。
- 若更换了计算顺序、广播方式、数组副本、浮点优化或就地修改方式，要确认结果及副作用符合原来的要求。
- 非线性求解、状态方程、相平衡和自动微分程序，还要关注残差、收敛情况、精度及泛型兼容性。
- 不确定哪种实现更快时，先选清楚、正确的写法；确实影响性能的地方再进行测量。

### 验证任何有风险的改动

使用 `Test` 编写针对实际边界条件的测试。优化或重构前后要核查结果、写入副作用、精度、类型兼容性；对于非线性求解或自动微分，还要验证残差与求解行为。确有性能目标时，才在相同输入和运行环境下比较时间及分配。

## 参考资料

- Julia 官方性能指南：https://docs.julialang.org/en/v1/manual/performance-tips/
- Julia 方法与多重派发：https://docs.julialang.org/en/v1/manual/methods/
- Julia 采样性能分析：https://docs.julialang.org/en/v1/stdlib/Profile/
- BenchmarkTools.jl：https://juliaci.github.io/BenchmarkTools.jl/stable/
- StaticArrays.jl：https://github.com/JuliaArrays/StaticArrays.jl
