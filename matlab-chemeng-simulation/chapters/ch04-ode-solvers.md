# Chapter 4: 化工中的常微分方程及其求解

## Core Idea
化工常微分方程模型分两大类——**一维分布参数过程稳态模型**（自变量为一维空间位置 x 或 r，非等温反应器一维稳态模拟常导致一组非线性 ODE-IVP）与**集中参数过程动态模型**（自变量为时间 t，用于开停车非稳态研究、间歇过程分析、控制系统设计与分析）；扩散-反应系统主要是 ODE-BVP 问题。求解器主线：非刚性 IVP 用 ode45()，刚性 IVP 用 ode23s()，两点边值用 bvp4c()。

## Frameworks Introduced
- **动态模拟 + 稳态模拟一体化**（例4-2、4-21）: "令 dC_A/dt=0 和 dT/dt=0，则得到稳态模型"
  - When to use: 同一设备既需要开车/扰动动态响应，又需要定态工作点
  - How: 动态模型导数置零→代数方程组用 fsolve() 求稳态；动态方程组用 ode45() 沿 t 积分
- **相平面图**（例4-2）: "用循环语句可以在一定范围内改变浓度和温度的初值，并计算不同初值下 CSTR 的动态数据，由此可绘出 CSTR 反应器的相平面图"，据此判断定态点个数（该例只有一个定态点）
- **bvp4c 两点边值求解流程**（例4-11~4-16）: 二阶 ODE 降阶为一阶方程组（y₁=C, y₂=dC/dx）→ `bvpinit(linspace(a,b,100), [猜测值])` → `bvp4c(@ODEs,@BCfun,solinit)` → `deval()` 输出。作者称条件分属两端的情形为 split boundary conditions，并指出："这是 ODE-BVPs 问题，C_A 初始值未知，可用打靶法（Shooting technique）确定……过去的文献多介绍这种方法。本程序直接使用 MATLAB 的配置法函数 bvp4c() 进行求解"
- **有效因子并入 ODE 方程组**（例4-14、4-15）: 将 η 的积分定义式对 r 求导化为微分方程（dη/dr = 3C_A r²/(C_AS R³)，η|_{r=0}=0），与物料衡算、Fick 扩散方程构成 ODE-BVPs 联立求解，η 即边界处的值——免去事后数值积分
- **Stefan-Maxwell 扩散 + 优化打靶**（例4-9）: 以末端浓度误差 |ε(C_A)|+|ε(C_B)| 为目标函数，ObjFunc() 内嵌 ode45()，fminsearch() 同步搜索通量 N_A、N_B
- **控制器方程化为附加 ODE**（例4-24、4-25）: PI 控制中定义 E_I=∫E dt，则 dE_I/dt=E，与过程 ODE 组联立积分；间歇精馏回流比控制用逻辑变量 flag 切换全回流/控制模式

## Key Concepts
- **ODE-IVP / ODE-BVP**: 初值问题（条件全部在起点给定，ode45/ode23s）；边值问题（条件分属区间两端，bvp4c）
- **split boundary conditions**: "一个微分方程的边界条件是初始条件 (x=0)，另一个微分方程的边界条件是最终条件 (x=1)"的 BVP
- **刚性方程组**: ode45() 长时间算不出结果或输出异常即应怀疑刚性，改用 ode23s()（例4-18 化学热泵、例4-23 非等温 CSTR）
- **Thiele 模数**: φ = r_p√(k/D)，内扩散阻力与反应速率之比的无量纲准数，决定颗粒内浓度分布陡峭程度
- **有效因子（等温内部效率因子）η**: "催化剂颗粒内的平均反应速率与催化剂颗粒表面处的反应速率"之比；片状 η=∫₀¹C dx，球形 η=∫₀¹f(C)r²dr / ∫₀¹f(C_S)r²dr
- **一维稳态拟均相模型**: 固定床反应器将气相与催化剂视为一体，沿轴向 z 列物料/热量衡算 ODE（例4-5）
- **Monod / Substrate inhibition 动力学**: μ=μ_max·x₂/(k_m+x₂)；带底物抑制 μ=μ_max·x₂/(k_m+x₂+k₁x₂²)（例4-21 CSTF）
- **IMRCF 膜反应器**: 产物 B 以 R_B=k_c·C_B 透过膜离开反应区，使转化率高于热力学平衡转化率（例4-22）

## Mental Models
- Use 动态模型+导数置零 when 需要同时获得开车曲线与稳态工作点——两者是同一组方程的两种用法
- Use ode45() 默认开场 when 求任何 IVP；Use ode23s() when ode45() 迟迟不出结果或输出异常（刚性征兆）
- Use bvp4c()+spline()+quadl() when 扩散-反应问题求有效因子；当 η 定义式易写成微分方程时，改为把 η 作为附加因变量并入 BVP
- Use if r==0 置 y₂'=0 when 球/柱对称方程含 2/r 奇异项，避免 r=0 处除零

## Anti-patterns
- **对刚性系统坚持用 ode45()**: 例4-18 "先用 ode45() 求解，发现很久不能算出结果，说明很可能是刚性方程组……再将 ode45() 改为 ode23s() 即求得结果"；例4-23 "若用 ode45()，则发现 TJ~t 图形有些异样（最后一个 TJ 值突然变小）"
- **bvpinit() 初始猜测值不当**: 例4-16 注："若为 bvpinit() 提供的解的初值（初始猜测值）不当，则会得出错误的结果。如本例中，若 bvpinit() 的解的初值取为 [1 0]，则结果 y 值出现负数，没有物理意义"
- **在 r=0 处不保护除零**: 例4-12、4-14、4-16 均用 if 语句令 r=0 时二阶导数为 0
- **忽视输入阶跃造成的初值矛盾**: 例4-8 中 t=0 时初始条件 y₀=0 与进料浓度 y₀=0.05 矛盾，作者取算术平均 0.025 过渡（并验证取 0.05 结果基本不变）
- **溶解/相变过程用单一速率方程**: 例4-6 对 Cl₂ 溶解设上限判断（nC>0.12·nB0 时 dnCdt=0）；例4-17 药丸溶解分外层/药芯/全溶解三段用 if...else...end 切换方程

## Code Examples
```matlab
function BatchReactor
clear all; clc
T = 224.6 + 273.15; R = 8.31434; % T: 反应器温度(K), R: 理想气体常数(kJ/kmol K)
k0 = [5.78052E+10 3.92317E+12 1.64254E+4 6.264E+8]; % 指前因子, 1/s
Ea = [124670 150386 77954 111528]; % 活化能, kJ/kmol
C0 = [1 0 0 0 0]; tspan = [0 1e4]; % C0: 初始浓度 C0(i), kmol/m^3
[t, C] = ode45(@MassEquations, tspan, C0, [], k0, Ea, R, T)
% 绘图
plot(t, C(:,1), 'r-', t, C(:,2), 'k:', t, C(:,3), 'b-', t, C(:,4), 'k--');
xlabel('Time (s)'); ylabel('Concentration (kmol/m^3)'); legend('A', 'B', 'C', 'D')
CBmax = max(C(:,2)); % CBmax: the maximum concentration of B, kmol/m^3
yBmax = CBmax/C0(1) % yBmax: the maximum yield of B
index = find(C(:,2)==CBmax);
t_opt = t(index) % t_opt: the optimum batch time, s
%----
function dCdt = MassEquations(t, C, k0, Ea, R, T)
k = k0.*exp(-Ea/(R*T)); k(5) = 2.16667E-04; % Reaction rate constants, 1/s
% Reaction rates, kmoles/m3 s
rA = -(k(1)+k(2))*C(1); rB = k(1)*C(1)-k(3)*C(2); rC = k(2)*C(1)-k(4)*C(3);
rD = k(3)*C(2)-k(5)*C(4); rE = k(4)*C(3)+k(5)*C(4);
dCdt = [rA; rB; rC; rD; rE]; % Mass balances
```
- **What it demonstrates**: 连串-平行复杂反应 IVP 的 ode45 标准用法：参数经函数句柄附加参数传入，动态数据直接用 max()/find() 求最优反应时间（t_opt=740 s，收率 0.8129）

```matlab
function PorousSphereCat_1Ord % 球形催化剂中的一级不可逆等温反应的模拟计算
clear all; clc
global fai Cs
Cs = 1; rp = 5e-3/2; k = 4; D = 0.05e-4; fai = rp * sqrt(k/D); % fai: Thiele 模数
a = 0; b = 1; % 积分区间[a, b]
solinit = bvpinit(linspace(a, b, 100), [0 0]); % 以猜测值 y1(r) = 0, y2(r) = 0 对解进行初始化
sol = bvp4c(@ODEs, @BCfun, solinit); % 求解 ODE-BVP 问题
% 绘制浓度分布图
plot(sol.x, sol.y(1,:), 'b-')
xlabel('Dimensionless Radius'), ylabel('Dimensionless Concentration')
% 计算催化剂的有效因子
I1 = quadl(@IntFunc1, a, b, [], [], sol.x, sol.y(1,:)), I2 = quadl(@IntFunc2, a, b), eta = I1/I2
fprintf('\t 催化剂的有效因子为: η = %.4f', eta)
% ----
function dydr = ODEs(r, y)
global fai Cs
dy1dr = y(2);
if r == 0 % 避免除数为零
dy2dr = 0;
else
dy2dr = fai^2*y(1)/Cs - 2/r*y(2);
end
dydr = [dy1dr; dy2dr];
%----
function bc = BCfun(ya, yb)
bc = [yb(1)-1; ya(2)];
%----
function f = IntFunc1(r, ri, yi)
f = spline(ri, yi, r) .* r.^2;
%----
function f = IntFunc2(r)
global Cs
f = Cs * r.^2;
```
- **What it demonstrates**: 扩散-反应 ODE-BVP 全流程：降阶→bvpinit/bvp4c→r=0 奇点保护→样条+quadl 积分求 η=0.7726

## Reference Tables
ODE 求解器选择（据本章 25 例归纳）：

| 问题类型 | 典型模型 | 求解器 | 本章例题 |
|---|---|---|---|
| 非刚性 IVP（动态/沿程积分） | 间歇/半连续/CSTR/管式反应器、精馏、吸收、膜反应器 | ode45() | 4-1~4-10, 4-17, 4-20~4-22, 4-24, 4-25 |
| 刚性 IVP | 化学热泵、带控制的非等温 CSTR | ode23s() | 4-18, 4-23 |
| 边值问题 | 催化剂颗粒、酶催化、管内层流 | bvp4c()（+bvpinit/deval） | 4-11~4-16, 4-19 |
| 稳态点 | 导数置零的代数方程组 | fsolve() | 4-21（与 ode45 联用） |
| BVP 含未知通量 | Stefan-Maxwell 多组分扩散 | ode45()+fminsearch() 打靶 | 4-9 |

程序化技巧对照：

| 需求 | 作者手法 | 出处 |
|---|---|---|
| 求最优反应时间/浓度峰值 | max() + find() 定位 | 例4-1、4-6 |
| 求达到指定指标的时间/体积 | spline(指标, t, 目标值) 反插值 | 例4-4、4-8 |
| 参数在主函数与 ODE 函数间共享 | global 变量或句柄附加参数 | 例4-4 等 |
| 分段/饱和速率 | if...else...end 切换方程 | 例4-6、4-17 |
| PI 控制积分作用 | 定义 EI 状态，dEI/dt=E | 例4-24 |

## Worked Example
**例4-2 CSTR 开车过程的动态模拟及稳态模拟**（夹套冷却 CSTR，一级放热反应 A→P+ΔH_r，-r_A=kC_A）：
- **问题**: (a) 模拟开车动态行为并绘相平面图；(b) 计算稳态。
- **模型方程**: 质量衡算 dC_A/dt=(C_A0−C_A)/τ−kC_A（τ=V/F）；热量衡算 dT/dt=(Q_g−Q_r)/(Vρc_p)，其中 Q_g=kC_A·V(−ΔH)，Q_r=Fρc_p(T−T₀)+UA(T−T_J)。
- **数值方法**: 动态——DynamicModel() 定义式(2)(4)，ode45() 在 tspan=[0 5000] 积分，循环改变初值绘相平面图；稳态——令 dC_A/dt=0、dT/dt=0 得 Q_g−Q_r=0 的代数方程组。
- **MATLAB 要点**: 同一组方程两种用法；相平面图上比较 Q_g(Q_r)−T 关系曲线与动态轨迹。
- **结果**: 该 CSTR 反应器只有一个定态点；Q_g(Q_r)−T 关系与相平面图如图 4-4、4-5。

## Key Takeaways
1. 先分类再选求解器：自变量为时间或单一位移的 IVP → ode45()；算不动或输出异常 → ode23s()；两端给条件 → bvp4c()。
2. 动态与稳态同源：稳态=导数置零的代数方程组（fsolve()），不必为稳态另建模型。
3. 扩散-反应 BVP 用 bvp4c() 直接配置求解，不必打靶；η 可事后 spline+quadl 积分，也可化为 dη/dr 并入方程组一次解出。
4. 控制系统模拟只是多写方程：控制律代入 ODE 函数，PI 积分作用补一个 dEI/dt=E 状态即可。
5. 对称奇点（r=0）必须 if 保护；bvpinit 猜测值需检查解的物理合理性（浓度非负）。
6. 最优反应时间/最优温度形成"优化（第6章）—模拟（本章）"闭环：max()+find() 直接从动态数据提取。

## Connects To
- **Ch3**: ode45/ode23s/bvp4c 的算法原理与调用格式在 3.4 节引入，本章是其化工应用全集
- **Ch5**: 催化剂颗粒稳态 BVP（本章）在例5-8 升级为动态 PDE（pdepe）；固定床二维拟均相模型由例4-5 的一维 ODE 扩展为例5-3 的二维 PDE
- **Ch6**: 例4-1 的最优反应温度 224.6℃ 来自例6-15 的优化；管式反应器最优温度分布见例6-16
- **Ch7**: 本章所有 ODE 模型是动力学参数估计（例7-5、7-6、7-9）的仿真内核
