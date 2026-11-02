# Julia 科学计算的数值测试参考

执行流程见 [技能入口](SKILL.md)。本页按需查阅，示例以 Julia 1.11 为基线。

## 选择正确性依据

| 依据             | 适用检查                       | 注意事项                     |
| ---------------- | ------------------------------ | ---------------------------- |
| 解析解或独立基准 | 小规模已知解、制造解、文献数据 | 记录来源、单位和适用范围     |
| 数学性质         | 对称性、单调性、极限、收敛阶   | 先确认性质成立的条件         |
| 物理约束         | 守恒、归一化、非负性、相平衡   | 约束成立不代表解唯一或正确   |
| 独立数值方法     | 高精度参考、AD 与有限差分      | 检查参考方法误差及步长敏感性 |
| 回归样例         | 极端输入、初值变化、历史缺陷   | 同时说明预期结果为何正确     |

对离散化算法，在适用的渐近区间检查网格或步长细化后的误差趋势。对随机算法，明确统计误差和失败概率；固定种子只能复现一次抽样，不能证明统计正确性。

## 写浮点与求解器断言

数量、形状和离散状态使用精确比较。浮点量使用有依据的绝对容差、相对容差或显式残差。

```julia
@test isapprox(actual, expected; atol=absolute_budget, rtol=relative_budget)
@test isapprox(residual, 0.0; atol=residual_budget, rtol=0)
```

接近零时显式指定 `atol`。容差来自模型精度、输入误差、求解器设置或量纲分析，不使用全项目统一的任意常数。

多方程残差先按各分量的物理尺度无量纲化，再检查最大分量或适当范数。不要只看均值。分别检查有限值、可行域、守恒误差和方程残差，并记录求解器状态、容差与迭代上限。

随机测试使用局部 RNG，例如 `rng = MersenneTwister(2026)`，并显式 `using Random`。保存失败时的种子和触发输入；跨 Julia 版本需要复现时保存输入数据，不只保存种子。

## 使用项目已有测试环境

小包用 `test/runtests.jl` 和 `@testset` 分组。每个测试文件显式导入所需模块，共享样例显式加载。

若项目尚无测试依赖配置，可在根 `Project.toml` 中加入以下配置；已有测试环境时沿用原方案。

```toml
[extras]
Test = "8dfed614-e22c-5e08-85e1-65c5234f0b40"

[targets]
test = ["Test"]
```

从项目根目录运行：

```bash
# 仅在根环境包含该测试所需依赖时定向运行
julia --project=. -e 'include("test/unit/rr.jl")'

# 使用 Pkg 的测试环境运行正式入口
julia --project=. -e 'using Pkg; Pkg.test()'
```

定向 `include` 不会自动启用测试专用依赖。若缺少依赖，使用项目已有的测试筛选机制或 `Pkg.test()`；不要把测试依赖加入生产 `[deps]` 来绕过问题。

只在具体问题出现后增加工具。作用域污染可用独立模块；包质量检查可用 Aqua；类型诊断可用 JET；性能测量可用 BenchmarkTools。先核实项目版本兼容性，这些工具不能代替行为测试。

## 用可手算的残差检查 Red 与 Green

为 `rr_residual(β, z, K)` 检查 Rachford–Rice 残差：

\[
F(\beta)=\sum_i\frac{z_i(K_i-1)}{1+\beta(K_i-1)}
\]

先把测试接入包的现有入口。以下 `MyPackage` 替换为真实包名；函数可以导出，也可以用模块前缀访问。

```julia
using Test
using MyPackage

@testset "Rachford–Rice residual" begin
	z = [0.5, 0.5]
	K = [2.0, 0.5]
	@test isapprox(rr_residual(0.0, z, K), 0.25; atol=1e-12, rtol=0)
	@test isapprox(rr_residual(0.5, z, K), 0.0; atol=1e-12, rtol=0)
	@test isapprox(rr_residual(1.0, z, K), -0.25; atol=1e-12, rtol=0)
	@test_throws DimensionMismatch rr_residual(0.5, z, [2.0])
end
```

这些期望值由公式手算。`1e-12` 仅用于这个尺度为一、运算次数少的 Float64 样例，不是科学模型的通用容差。

若接口尚不存在，先接入同名占位函数，使测试进入目标调用并因错误行为失败，再实现以下函数。不要把包加载失败当作 Red。

```julia
function rr_residual(β, z, K)
	length(z) == length(K) || throw(DimensionMismatch("z and K must have equal lengths"))
	return sum(z .* (K .- 1) ./ (1 .+ β .* (K .- 1)))
end
```

这是残差函数示例。完整 Flash 求解还需定义输入有效域、分母有效性、无两相解时的行为，并验证相组成、物料衡算和求解残差。

## 查阅官方定义

- [Julia 1.11 Test](https://docs.julialang.org/en/v1.11/stdlib/Test/) 定义测试断言和测试集。
- [Julia 1.11 数学函数](https://docs.julialang.org/en/v1.11/base/math/) 定义 `isapprox` 与容差。
- [Pkg 测试环境](https://pkgdocs.julialang.org/v1/creating-packages/#Adding-tests-to-the-package) 说明包测试和测试依赖配置。
