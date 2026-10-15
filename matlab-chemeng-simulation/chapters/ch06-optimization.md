# Chapter 6: 化工最优化方法

## Core Idea
先把化工设计/操作问题整理成标准优化模型（目标函数 + 等式/不等式约束 + 变量边界），按问题类型（线性规划、二次规划、无约束/有约束非线性规划、多目标、最小二乘）选择 MATLAB 优化工具箱中一一对应的求解器；决策变量为时间/空间连续函数（最优温度分布、最优进料速率）时，用庞特里阿金极大值原理化为状态方程 + 伴随方程的两点边值问题求解。

## Frameworks Introduced
- **最优化问题的一般形式（式6-1）**: $\min_{x\in R^n} J=f(x)$, s.t. $G(x_i)=0$（等式约束）、$G(x_i)\le 0$（不等式约束）、$x_l\le x\le x_u$（参数边界）。
  - When to use: 所有优化问题的统一骨架；"若未知变量数等于 $m_e+m_i$，则不管优化准则如何，至少存在一个解"
  - How: 先判断问题属于线性/二次/非线性/多目标哪一类，再选算法——"没有哪种优化算法对所有的优化问题都有效"
- **求解优化问题的六个步骤（Edgar等）**: ①列变量表；②确定优化准则、给定目标函数；③写过程/设备模型并联结输入-输出变量、识别自由度；④问题太大则分解或简化目标函数与模型；⑤选合适优化技术求解；⑥检查答案并做灵敏度分析。
- **系统自由度判定**: "状态变量数 = 状态方程数，变量的总数 - 状态方程数 = 决策变量数"；化工中把易测量控制的变量（压力、温度、流量）取为决策变量。
- **单变量最优化（fminbnd）**: 一维搜索法；"算法基于黄金分割法和二次插值法"。直接法（黄金分割、二次/三次多项式近似）不需导数但收敛慢；间接法（牛顿切线法、割线法、三次插值）收敛快。
- **线性规划（linprog）**: 标准形式 $\min f^Tx$ s.t. $Ax\le b,\ A_{eq}x=b_{eq},\ lb\le x\le ub$。中型问题用投影法，大型问题用 LIPSOL 法（Mehrotra 预测-校正法的变化形式）。
- **无约束多变量优化**: 两大类——直接搜索法（Line Search，适合"目标函数高度非线性、没有导数或导数不易求出"，收敛慢）与梯度法（收敛快）。MATLAB 提供 fminsearch()（Nelder-Mead 单纯形法）和 fminunc()（拟牛顿法）；拟牛顿法用 BFGS/DFP 构造 Hessian 近似矩阵，"成为求解无约束多变量最优化问题最有效的方法之一"。
- **二次规划（quadprog）**: 目标为二次函数、约束为线性函数：$\min \frac{1}{2}x^THx+f^Tx$。
- **有约束非线性规划（fmincon）**: 采用 SQP 法（序贯二次规划法）——"它是无约束极值问题的拟牛顿法在有约束极值问题中的深化和推广，是当今求解光滑的非线性规划问题的最有效的算法之一"。非线性约束经 @nonlcon 返回 $[c, ceq]$（$c(x)\le0$、$ceq(x)=0$）。
- **多目标最优化（fgoalattain）**: 求解 $\min_{x,\gamma}\gamma$ s.t. $F(x)-weight\cdot\gamma\le goal$ + 各类约束；输出 attainfactor（目标达到因子）——"若 attainfactor 为负，则目标已经溢出；若为正，则目标个数还未达到"。weight 常按目标比例确定。
- **最小二乘法（6.1.8）**: 目标 $\min \frac{1}{2}\|F(x)\|_2^2$；解法为 Gauss-Newton 法与 Levenberg-Marquart 法（阻尼最小二乘）——"当阻尼因子为 0 时，L-M 法即为 G-N 法，当阻尼因子趋于 ∞ 时，即为最速下降法"；G-N 快但有时出问题，L-M 稳定。函数：\（线性）、lsqlin（有约束线性）、lsqnonneg（非负线性）、lsqnonlin / lsqcurvefit（非线性）。
- **庞特里阿金（Pontryagin）极大值原理**: 连续变量系统最优控制。引入哈密尔顿函数 $H=Y+\sum_{i=1}^n\lambda_i f_i$；伴随函数 $\frac{d\lambda_i}{dt}=-\frac{\partial Y}{\partial x_i}-\sum_j \lambda_j\frac{\partial f_j}{\partial x_i}$，终端条件 $\lambda(t_f)=0$；最优决策满足 $\partial H/\partial u=0$。联立求解状态方程（正方向积分）、伴随方程（从 $t_f$ 反向积分）与 $\partial H/\partial T=0$ 的代数条件。
- **全局最优化（简介）**: SQP/SLP/GRG 属"局部求解器"，"应用于光滑非凸问题通常收敛于最近的局部极小值"；全局方法有 multistart、遗传算法 GA、模拟退火 SA、蚁群算法（MATLAB 6.5 版工具箱仅提供局部最优化函数）。

## Key Concepts
- **目标函数**: 把最优目标（收率最大、能耗最小等）写成数学形式的表达式，又称利润函数/成本函数。
- **约束条件**: 对变量取值的限制；物料衡算、热量衡算、动量衡算属等式约束，即过程/系统的状态方程。
- **决策变量**: 决策者根据目标和约束确定的变量（又称设计变量、控制变量、操作变量）；决策变量数即系统自由度。
- **SQP 法**: 序贯二次规划法，fmincon 的核心算法，光滑非线性规划最有效算法之一。
- **Nelder-Mead 单纯形法**: 只用目标函数值、不需导数的直接搜索法，fminsearch 的算法。
- **拟牛顿法（Quasi-Newton）**: 用近似矩阵代替 Hessian 及其逆阵的梯度法，BFGS 优于 DFP。
- **Levenberg-Marquart 法**: 阻尼最小二乘法，专用于平方和形式目标，介于 G-N 法与最速下降法之间。
- **哈密尔顿函数/伴随函数**: 极大值原理的辅助函数 $H=Y+\sum\lambda_i f_i$ 与伴随变量方程（边界条件 $\lambda(t_f)=0$）。
- **attainfactor**: fgoalattain 输出的目标达到因子，指示各目标超额/未达成的程度。
- **局部求解器（local solvers）**: SLP、SQP、GRG 等只保证局部极小的算法。

## Mental Models
- **Use linprog when 目标和约束全为线性**——但 max 目标要乘 -1 转 min、"$\ge$"约束两边乘 -1、"$x_3\le5$"型变量以 $(-x_3)$ 替换后才能进标准形式。
- **Use fminsearch when 无约束且目标导数难求**（典型：目标函数内部嵌套 ODE 积分求 $C_{Bmax}$，如例6-15 最优反应温度）。
- **Use fmincon when 出现任何非线性约束**；线性约束给系数矩阵，非线性等式/不等式约束打包进 @nonlcon。
- **Use 庞特里阿金极大值原理 when 决策变量是连续函数**（管式反应器最优温度分布、间歇过程最优进料速度）而非一组离散参数。
- **Use "给决策变量加足实际约束" when 优化迭代易发散**: 例6-16 中 PFRTempOpt_B 在 fmincon 中加入 $0\le k\le1$、$k_1\ge k_2\ge\cdots\ge k_N$、固定 $k_1=1$，使"对 k 的初值选定不再那么苛刻"，比纯迭代公式法（PFRTempOpt_A）容易收敛。

## Anti-patterns
- **对有约束问题调用 fminsearch/fminunc**: 例6-13 明确指出"这里不能用函数 fminsearch 和 fminunc，因为它们是无约束的优化函数，而这里的优化问题是有约束的"。
- **不化标准形式直接调求解器**: linprog/quadprog/fmincon 都要求 min、$\le$、lb/ub 形式；原问题须先做符号变换（例6-2、6-3 均演示了转换过程）。
- **把局部解当全局解**: SQP 等局部求解器用于光滑非凸问题"可能不是全局最小"；可用 multistart（多起点反复调用局部求解器）缓解。
- **庞特里阿金数值解只用迭代公式、不加约束**: PFRTempOpt_A"对 k 的初值要求比较苛刻，若给定的初值与真值相差较大，则容易发散"——换初值 $k=[0.5,\cdots]$ 或微调节点向量 tspan1 即不收敛。
- **忽略目标函数中"平方和"结构**: 平方和形式目标应使用 lsqnonlin/lsqcurvefit（G-N/L-M 二次收敛），而不是普通 fminsearch。

## Code Examples
```matlab
function CSTR_OptDes % 连续搅拌槽式反应器的最优设计
clear all; clc
x0 = [0.5 0.5]; % 给定初值
options = []; % 使用默认参数
xL = [0 0]; xU = [1 1]; % 设定下限 xL 和设定上限 xU
[x, f, flag] = fmincon(@Fee, x0, [], [], [], [], xL, xU)
CA0 = x(1); xA = x(2);
fprintf('优化结果：\n\n'), fprintf('转化率为：%.3f\n', xA)
fprintf('浓度 CA0: %.3f 摩尔/升\n', CA0)
fprintf('进料量 FA0 为：%.3f 升/小时\n', 100/(CA0*xA))
fprintf('反应器体积 V 为：%.2f 升\n', 50/CA0^2/(1-xA)^2)
fprintf('每小时总消耗费用：%.3f 元\n', f)
%----
function f = Fee(x) % Objective function for Optimization
CA0 = x(1); xA = x(2);
f = 400 * CA0^0.4 / xA + 4.183 / CA0^1.2 / (1 - xA)^1.2;
```
- **What it demonstrates**: fmincon 求解两变量有边界约束的 CSTR 最优设计——物料衡算消元后目标函数只剩 $C_{A0}, x_A$ 两个决策变量，SQP 直接搜索。

```matlab
function x1Fmincon
clear all; clc
x0 = [0.8; 0.6];
[x, fval] = fmincon(@func, x0, [], [], [], [], [], [], @NlinCons)
% ----
function f = func(x)
f = -x(1) + 10*x(1)^2 + 10*x(2)^2;
% ----
function [c, ceq] = NlinCons(x)
ceq = x(1)^2 + x(2)^2 - 1;
```
- **What it demonstrates**: fmincon 处理非线性约束的最小模式——@nonlcon 返回 [c, ceq]；无对应约束时以空矩阵占位。

## Reference Tables
表6-1 MATLAB 最小化函数（原书表）:

| 函数 | 描述 | 函数 | 描述 |
|---|---|---|---|
| fgoalattain | 多目标达到问题 | fminsearch, fminunc | 无约束非线性最小化 |
| fminbnd | 有边界的单变量非线性最小化 | fseminf | 半无限问题 |
| fmincon | 有约束的非线性最小化 | linprog | 线性规划 |
| fminimax | 最大最小化 | quadprog | 二次规划 |

问题类型 → 求解器决策表（由 6.1 节归纳）:

| 问题特征 | 求解器 | 算法 |
|---|---|---|
| 单变量、有区间 | fminbnd | 黄金分割+二次插值 |
| 线性目标+线性约束 | linprog | 投影法 / LIPSOL（大型） |
| 二次目标+线性约束 | quadprog | — |
| 无约束多变量 | fminsearch / fminunc | Nelder-Mead / 拟牛顿(BFGS) |
| 非线性约束 | fmincon | SQP |
| 多目标 | fgoalattain | 目标达到法 |
| 平方和目标（拟合） | lsqnonlin / lsqcurvefit | G-N / L-M |

## Worked Example
**例6-14 连续搅拌槽式反应器（CSTR）的最优设计**：反应 2A→B，速率方程 $-r_A=2.0C_A^2=2.0C_{A0}^2(1-x_A)^2$；原料成本 $c_1=4.0C_{A0}^{1.4}$（元/升），反应器折旧等费用 $c_2=0.4V_R^{0.6}$；要求产品 B 产量 $F_B=50$ mol/h，确定进料量 $F_{A0}$、浓度 $C_{A0}$、体积 $V$、转化率 $x_A$ 使每小时总费用最小。
- **模型**: 对 A 物料衡算并代入 $F_B=\frac{1}{2}F_{A0}C_{A0}x_A$，消元得 $V_R=\frac{50}{C_{A0}^2(1-x_A)^2}$、$F_{A0}=\frac{100}{C_{A0}x_A}$；目标函数化为两变量：$\min\limits_{C_{A0},x_A} f=\frac{400C_{A0}^{0.4}}{x_A}+\frac{4.183}{C_{A0}^{1.2}(1-x_A)^{1.2}}$。
- **方法**: fmincon（SQP），初值 $[0.5, 0.5]$，边界 $0\le C_{A0},x_A\le1$，无其他线性/非线性约束。
- **MATLAB 要点**: 状态方程已解析消元，目标函数 Fee() 内直接写两变量表达式；解出后回代计算 $F_{A0}=100/(C_{A0}x_A)$、$V=50/C_{A0}^2/(1-x_A)^2$。
- **结果**: $C_{A0}=0.238$ mol/L、$x_A=0.714$、$F_{A0}=588$ L/h、$V=10789$ L，每小时总消耗费用 420.7 元。

## Key Takeaways
1. 先归类再求解：判定问题属于线性/二次/无约束/有约束非线性/多目标/最小二乘哪一类，套用表6-1 对应函数；"没有哪种优化算法对所有的优化问题都有效"。
2. 建模先做自由度分析："变量总数 - 状态方程数 = 决策变量数"；用状态方程消元可把目标函数压缩到决策变量空间（例6-12/6-14 均如此）。
3. 有约束问题绝不使用 fminsearch/fminunc；非线性约束必须经 @nonlcon 传入 fmincon。
4. "max"与"$\ge$"约束、带上界变量都要先手工变换为 linprog/quadprog 标准形式，再调用函数。
5. 连续变量系统（最优温度分布）按"状态方程正向积分 + 伴随方程从 $t_f$ 反向积分 + $\partial H/\partial T=0$ 代数条件"组织数值解；该方程组本质是 ODE-BVP，也可用 bvp4c()（PFRTempOpt_C），或把代数条件残差作为 fmincon 的目标函数直接搜索最优 k 分布（PFRTempOpt_B，更稳健）。
6. 平方和形式目标（数据拟合、参数估计）交给 lsqnonlin/lsqcurvefit；lsqcurvefit 只要求定义模型表达式 F(x,xdata)，不必自写 sum of squares。
7. MATLAB 工具箱（6.5 版）只有局部优化函数；非凸问题用 multistart 多起点，或了解 GA/SA/蚁群等全局算法。

## Connects To
- **Ch 3**: 例7-1 微分法所用的样条拟合求导（spap2/fnder）来自第3章数值微分；优化目标函数中常调用 fzero/fsolve 内层求解。
- **Ch 4**: 例6-15 基于例4-1 间歇反应器 ODE 模型（对每个候选温度 T 积分求 $\max C_B$）；例6-17 复用例4-18 化学热泵动态模拟——ODE 模拟器是优化目标函数的内层引擎。
- **Ch 7**: 6.1.8 最小二乘法（lsqnonlin/lsqcurvefit）正是参数估计的数学基础；例7-5 还用 fmincon 做参数估计。
- **Ch 8**: 实验方案的最优化在第8章介绍。
