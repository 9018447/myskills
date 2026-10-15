# Cheatsheet — MATLAB 化工模拟速查

## 任务 → MATLAB 函数速查（全书程序一览表浓缩）

| 化工任务 | 用什么 | 关键函数 |
|---|---|---|
| 实验数据插值（1D/2D） | 样条或线性插值 | `interp1` `interp2` `spline` `ppval` |
| 数据拟合（多项式/样条最小二乘） | 最小二乘拟合 | `polyfit` `polyval` `spap2` `csaps` `spaps` |
| 数值积分（含精馏理论板、PFR管长、传质单元数N_OG） | 自适应求积 | `trapz` `quad` `quadl`（高阶首选） |
| 离散数据数值微分 | 拟合后求导 | `diff` `polyder` `csapi`+`fnder` |
| 单变量非线性方程（泡点、闪蒸、单批蒸馏、绝热CSTR转化率、管径） | 求根 | `fzero` |
| 非线性方程组（化学平衡、CSTR多稳态、2维稳态PDE差分离散化） | 求根 | `fsolve` |
| ODE 初值问题（反应器/精馏/吸收动态模拟） | 显式Runge-Kutta | `ode45`（默认）`ode23` |
| 刚性 ODE（化学热泵、非等温CSTR） | 刚性求解器 | `ode23s`（低精度快速）|
| ODE 边值问题（催化剂颗粒有效因子、管流速度分布） | 有限差分BVP | `bvp4c` + `bvpinit` |
| 1维动态 PDE（热传导、催化剂颗粒热质传递） | MOL法 | `pdepe`（内置）或自写Crank-Nicolson+TDMA |
| 2维稳态/动态 PDE（固定床、管道流、圆柱催化剂） | 有限元 | `pdetool` 或 `assempde` `parabolic` `pdenonlin` |
| 单变量最优化 | 黄金分割/抛物线 | `fminbnd` |
| 线性规划（生产规划） | 单纯形 | `linprog` |
| 无约束多变量最优化 | Nelder-Mead单纯形 | `fminsearch` |
| 二次规划 | — | `quadprog` |
| 有约束非线性最优化（反应器/换热器最优设计、最优温度分布） | SQP等 | `fmincon` |
| 多目标最优化 | 目标达到法 | `fgoalattain` |
| 动力学参数估计（代数模型） | 非线性最小二乘 | `lsqnonlin`（配 `regress` 初值） |
| ODE 模型参数估计（复杂反应/青霉素发酵） | 非线性最小二乘+模拟 | `lsqnonlin` + `ode45`（或 `fmincon`） |
| 模型适定性/辨识 | 参数两两比较 | `regress` + `lsqnonlin` |
| 正交实验设计极差/方差分析 | 自编脚本 | `sum` `find` `max` `min` |
| D-最优试验设计（参数估计用） | 交换算法 | `cordexch` + `nlinfit` |
| 神经网络（函数逼近/预测） | BP/RBF/GRNN | `newff` `newrb` `newgrnn` `sim`；线性网络 `newlind` `newlin`+`adapt` |

## 求解器选择决策规则

- **ODE先试 `ode45`**；若求解慢、步长极小或报错，改刚性求解器（书中用 `ode23s`），因为强放热耦合传热的CSTR、化学热泵等系统刚性显著。
- **两点边值问题一律 `bvp4c`**：催化剂颗粒（平板/球/圆柱）、管内层流速度分布；初值猜测用 `bvpinit` 给出，配合 `spline`+`quadl` 算有效因子。
- **1维动态PDE两条路**：想控制格式细节→自写 Crank-Nicolson（无条件稳定，配TDMA解三对角）；求快→`pdepe`。
- **2维PDE直接上 PDE 工具箱**：稳态椭圆型用 `pdetool`/`assempde`/`pdenonlin`；动态抛物型用 `parabolic`。
- **有约束优化用 `fmincon`**；无约束低维问题 `fminsearch` 更省事（不要求导数）；单变量闭区间用 `fminbnd`。
- **管式反应器最优温度分布三解法**（例6-16）：A 纯 `ode45`；B `ode45`+`fmincon` 外层优化；C `bvp4c`+`fmincon`——维度高时优先控制变量参数化。

## 参数估计决策规则

- **先微分法还是积分法**：数据噪声大、可直接数值微分→微分法（样条拟合+`fnder`）；模型含ODE必须积分→积分法（`lsqnonlin` 内嵌 `ode45`）。
- **有线性结构的模型先用 `regress` 得初值**，再 `lsqnonlin` 精估，避免陷入局部极小。
- **数据精度不一时用加权最小二乘**（例7-9 青霉素发酵按测量误差定权重）。
- **判断模型适定**：对参数做两两灵敏度比较（例7-12），参数无法分辨则改实验设计（第8章 D-最优 `cordexch`）。

## 关键阈值与经验

- MATLAB编程提速（第2章）：避免循环→向量化；循环不可避免时**先预分配数组**；内置函数优先于自写。
- Crank-Nicolson：无条件稳定但时间步过大仍有振荡，激进初值时配合半隐式处理。
- 正交实验设计：先无交互作用表做极差分析快速筛选，确认交互作用显著再上方差分析。
- 神经网络选型（第9章）：函数逼近平滑数据→BP `newff`；高维/快速训练→RBF `newrb`；小样本回归→GRNN `newgrnn`；线性关系→`newlind`。
