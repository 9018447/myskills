# Chapter 7: 参数估计和模型辨识

## Core Idea
参数估计本质上是最优化问题——以（多响应加权）最小二乘为准则搜索参数，使模型计算值与实验测量值尽量一致；模型辨识则是"参数估计 + 统计检验"的结合：用决定性指标 $\rho^2$、F 比、$F_E$ 比和残差分析，从竞争模型中筛选出既拟合数据、参数又具物理意义的最佳模型。

## Frameworks Introduced
- **参数估计 = 最优化（原话）**: "参数估计本质上是最优化问题，即搜索未知参数的最优值，使得模型计算值与试验测量值尽量一致"；本书最优参数估计"均基于最小二乘准则"。
- **模型结构两大类**: 代数方程模型 $\mathbf{y}=\mathbf{f}(\mathbf{x},\boldsymbol\beta)$（式7-1）；微分方程模型 $\frac{d\mathbf{x}}{dt}=\mathbf{f}(t,\mathbf{x},\boldsymbol\beta,\mathbf{u}),\ \mathbf{x}(t_0)=\mathbf{x}_0$（式7-4）。PDE 模型先用 MOL 法离散成 ODE 组再估计（直接逐步迭代解 PDE "速度可能会很慢"）。
- **导数法与 积分法**: "利用这两种方法——导数法和积分法，使 ODE 系统的参数估计问题降为代数方程组的参数估计问题"。微分法直接近似求 $d\mathbf{x}/dt$；积分法对候选参数积分 ODE 得模拟值。
- **多响应加权最小二乘法（式7-11）**: $\min_{\boldsymbol\beta}S(\boldsymbol\beta)=\sum_{j=1}^{\nu}w_j[\hat{\mathbf{y}}_j-\mathbf{y}_j(\mathbf{t},\boldsymbol\beta)]^T[\hat{\mathbf{y}}_j-\mathbf{y}_j(\mathbf{t},\boldsymbol\beta)]$，权值（式7-12）$w_j\propto 1/\sigma_j^2$（$\sigma_j^2$ 为每条曲线方差，由重复实验误差分析确定）。
  - When to use: 多响应误差不同时；权全为1即普通最小二乘，单响应是特例，故"多响应加权最小二乘法具有通用性"
  - How: ①参数初值→②算各时刻模拟值（代数显式直接算/隐式解方程，ODE 用龙格-库塔积分）→③定权→④算 $S^{(r+1)}$→⑤收敛判断 $\left|\frac{S^{(r+1)}-S^{(r)}}{S^{(r+1)}}\right|\le\varepsilon$。"由于每次迭代计算目标函数需要积分微分方程，比较耗时，所以更应使用二次收敛算法"（G-N/L-M，即 lsqnonlin/lsqcurvefit）。
- **多元线性回归 regress()**: 模型 $\mathbf{y}=\mathbf{X}\boldsymbol\beta+\boldsymbol\varepsilon$；输出 b、bint（置信区间）、r、rint、stats（$R^2$、F 值、p 值）。"X 矩阵应该包含元素全为 1 的一列……若模型不包含常数项，则 F 值和 p 值不正确"；`b = X\y` 等价。
- **非线性回归三件套**: nlinfit()（G-N 拟合，返回 beta、r、j）→ nlparci()（参数 95% 置信区间）→ nlpredci()（预测置信区间）；nlintool() 为集成 GUI。也可用 lsqnonlin/lsqcurvefit 算出 beta/残差/Jacobian 后调 nlparci/nlpredci。
- **参数估计实际指南（Englezos & Kalogerakis）**: (1) 先检查数据——视觉检查 + 统计："如果一个残差比标准差大 3~4 倍，则它可视为 outlier，因为此数据出现的概率只有 0.1%"；(2) 初值四法：模型结构与本质、方程渐进行为（Michaelis-Menten 在 $x\to0$ 得斜率 $k_1/k_2$、$x\to\infty$ 得渐进值 $k_1$）、变换后线性回归、直接搜索法（LJ 优化技术）；(3) 数据平滑——"平滑数据和多项式拟合的最好和最容易的方法是使用平滑三次样条函数"。
- **Arrhenius 参数的 Kittrell 变换（1970）**: $k_0\exp(-\frac{E}{RT})=k_0^*\exp[-\frac{E}{R}(\frac{1}{T}-\frac{1}{\bar T})]$，以平均温度 $\bar T$ 重参数化，"减少计算时由于频率因子和活化能之间的强相关性而引起的困难"。
- **fmincon + lsqnonlin 串联策略（例7-5）**: "fmincon() 并不计算参数的置信区间，即缺乏统计信息。而函数 lsqnonlin() 虽然可计算出参数的置信区间，但其参数估值不如 fmincon() 好。因此，结合两种算法较佳"——先 fmincon 求最优值，再以其为初值跑 lsqnonlin 得参数与置信区间。
- **模型辨识统计量**: 决定性指标 $\rho^2=1-\frac{\sum(y_{ei}-y_{ci})^2}{\sum y_{ei}^2}$（式7-15，越大越好）；F 比（式7-16，回归均方和/模型误差均方和）；$F_E$ 比（式7-17，模型误差方差/实验误差方差，给出"模型的绝对优劣"）；后验概率 $\pi_i$。Drapper & Smith 安全系数："线性回归的安全系数取为 4，非线性回归的安全系数取为 10"。
- **残差随机性检验**: 正负残差个数 $n_1,n_2$，符号改变次数 $r$ 近似正态，均值 $\bar r=\frac{2n_1n_2}{n_1+n_2}+1$（式7-18）。
- **模型辨识简便方法（原话）**: "如果 $\rho^2>0.9$、$F>10F_\alpha(N_p,N_e-N_p)$，且残差均匀地分布在对角线两侧，或均匀地分布在零线的上下侧，则可以认为所选模型和参数估值是可靠的"。

## Key Concepts
- **参数估计（data regression）**: 用最优化和统计方法从实验数据获得模型未知参数估计值。
- **模型辨识**: 用统计方法从多个竞争模型中剔除、判别，筛选出拟合最好的最佳模型。
- **导数法/积分法**: ODE 模型估计的两条路径：前者对状态变量求导化为代数问题，后者对每个候选参数积分 ODE。
- **多响应加权最小二乘**: 各响应按 $1/\sigma_j^2$ 加权合并的残差平方和最小化。
- **outlier**: 残差超过标准差 3~4 倍的数据点（出现概率约 0.1%），需统计确认并检查非统计理由后处理。
- **决定性指标 $\rho^2$**: 度量对回归均值总偏离的大小，给出模型间相对比较信息。
- **F 比 / $F_E$ 比**: 回归均方与误差均方之比（判据 $F>10F_t$）与模型误差方差对实验误差方差之比（绝对优劣）。
- **nlparci/nlpredci**: 分别计算参数与预测值的 95% 置信区间，需 beta/resid/Jacobian。
- **Langmuir-Hinshelwood 模型**: 多相催化速率模型，如 $r=\frac{kK_{H_2}K_{NO}p_{H_2}p_{NO}}{(1+K_{NO}p_{NO}+K_{H_2}p_{H_2})^2}$（例7-4）。
- **van Laar 模型**: 二元活度系数模型 $\ln\gamma_1=A_{12}(\frac{A_{21}x_2}{A_{12}x_1+A_{21}x_2})^2$，由 VLE 数据回归 $A_{12},A_{21}$（例7-11）。

## Mental Models
- **Use 积分法 when 需要最窄的参数置信区间**: 例7-1 实测——积分法 $k=0.0047\pm0.0016$、$n=1.46\pm0.19$；"由积分法得到的参数置信区间要比微分法的窄，从这点看，积分法较佳"。
- **Use "线性回归出初值 → 非线性回归出终值" when 处理任何非线性模型**（Michaelis-Menten、L-H、Monod、van Laar 均按此管线）：线性化结果"只能得到近似的结果，因而常作为非线性回归的初值"。
- **Use 加权最小二乘 when 多响应且误差不同**: 目标函数内把残差写成 $f=[\sqrt{w_1}f_1;\sqrt{w_2}f_2]$。
- **Use "$\rho^2$ + 10$F_\alpha$ + 残差图"三件套 when 判断模型适定性**——"不能简单地根据最小的残差平方和来筛选模型！"

## Anti-patterns
- **只按最小残差平方和选模型**: 例7-13 中模型(b)残差平方和最小（0.030），但 $K_A=0.043\pm0.071$——置信区间比参数本身还大、下限为负，"这从物理意义来说是不可能的。故该模型不可取"。判别基础是参数为正 + 拟合优度。
- **对非线性模型线性化后用线性回归出最终参数**: "这在统计上是不严格的（往往得到错误的参数估计的置信区间）"；且 Michaelis-Menten 三种线性化（式2/3/4）"估计得到的结果是不同的"。
- **微分法不做平滑直接求导**: 数据含噪音，"强烈建议通过多项式拟合对数据平滑处理"；例7-1 用不经过实验点的最小二乘 B 样条（spap2）求导。
- **用 ode45 直接处理含重复时间点/未排序数据**: "ode45 只处理上升或下降的自变量向量，故用插值方法"——例7-9 先 sort 再 spline 插值到实验点。
- **PDE 模型逐步迭代直接解 PDE**: 每次迭代解一次 PDE 速度慢——先 MOL 离散为 ODE 组。
- **Arrhenius 回归不处理 $k_0$—$E$ 强相关**: 应用 Kittrell 变换或分温度估计后再汇总。

## Code Examples
```matlab
function KineticsEst1_Diff % 用微分法进行反应速率分析得到速率常数 k 和反应级数 n
clear all; clc
t = [0 20 40 60 120 180 300]; CAm = [10 8 6 5 3 2 1]; % 动力学数据
% 用最小二乘样条拟合法计算微分 dCA/dt--使用不经过实验点的 B 样条插值函数
knots = 3; K = 3; % 三次 B 样条
sp = spap2(knots, K, t, CAm);
pp = fnder(sp); dCAdt = fnval(pp, t); % 计算 B 样条函数的导函数及其在 t 处的导函数值
rAm = dCAdt;
% 绘制浓度拟合曲线
ti = linspace(t(1), t(end), 200); CAi = fnval(sp, ti);
plot(t, CAm, 'ro', ti, CAi, 'b-'), xlabel('t'), ylabel('C_A'), legend('实验值', 'B 样条拟合')
beta0 = [0.0053 1.39]; % 参数初值
[beta, resnorm, residual, exitflag, output, lambda, jacobian] = ...
lsqnonlin(@OptObjFunc, beta0, [], [], [], rAm, CAm) % 非线性拟合
ci = nlparci(beta, residual, jacobian) % 参数的置信区间
% 显示参数辨识结果
fprintf('Estimated Parameters:\n'), fprintf('\tk = %.4f ± %.4f\n', beta(1), ci(1, 2) - beta(1))
fprintf('\tn = %.2f ± %.2f\n', beta(2), ci(2, 2) - beta(2))
% 绘制反应速率拟合曲线
figure, plot(t, rAm, 'ro', t, Rate(CAm, beta), 'b*')
xlabel('t'), ylabel('dC_Adt'), legend('Experiment', 'Kinetic Model')
% ----
function f = OptObjFunc(beta, rAm, CAm)
rAc = Rate(CAm, beta);
f = rAc - rAm;
% ----
function rA = Rate(CA, beta)
rA = -beta(1)*CA.^beta(2); % -rA = -dCAdt = k*CA^n，其中 k=beta(1), n=beta(2)
```
- **What it demonstrates**: 微分法全流程——B 样条平滑求导得速率 → lsqnonlin 直接拟合非线性速率模型 → nlparci 出参数置信区间。

```matlab
function FermKineticsEst
clear all; clc
load FermKineticsData    % 装载实验数据
% 排序
for i = 1:length(n);
    [x(1:n(i), i), index] = sort(x(1:n(i), i));
    y(1:n(i), i) = y(index, i);
end
w = Weights(x, y, n)
% 用 lsqnonlin()进行非线性最小二乘参数估计(非线性数据拟合)
beta0 = [0.1 4.0 0.02 0.02]; y0 = [0.29 0.0];
lb = [0 0.01 0 0]; ub = [inf inf inf inf];
[beta, resnorm, residual, exitflag, output, lambda, jacobian] = ...
lsqnonlin(@Func, beta0, lb, ub, [], x, y, n, y0, w);
ci = nlparci(beta, residual, jacobian);

% 参数辨识结果
fprintf('\nEstimated Parameters by Lsqnonlin):\n')
fprintf('\tk1 = %.4f ± %.4f\n', beta(1), ci(1, 2) - beta(1))
fprintf('\tk2 = %.2f ± %.2f\n', beta(2), ci(2, 2) - beta(2))
fprintf('\tk3 = %.4f ± %.4f\n', beta(3), ci(3, 2) - beta(3))
fprintf('\tk4 = %.2f ± %.2f\n', beta(4), ci(4, 2) - beta(4))
fprintf(' The sum of the squares is: %.1e\n\n', sum(residual.^2))

% ----
function f = Func(beta, x, y, n, y0, w)
tspan = [0 max(max(x))];
[tt yy] = ode45(@ModelEqs, tspan, y0, [], beta);
for col = 1:length(n)
    yc(1:n(col), col) = spline(tt, yy(:, col), x(1:n(col), col));
end
f1 = y(:, 1) - yc(:, 1);    f2 = y(:, 2) - yc(:, 2);
f = [sqrt(w(1))*f1; sqrt(w(2))*f2];

% ----
function dydt = ModelEqs(t, y, beta)    % 模型方程
dydt = [beta(1)*y(1)*(1 - y(1)/beta(2));    beta(3)*y(1) - beta(4)*y(2)];
```
- **What it demonstrates**: 多响应加权最小二乘估计 ODE 模型（青霉素发酵）：目标函数内 ode45 积分 + spline 插值到实验点，残差按 $\sqrt{w_j}$ 加权拼接，参数加非负下限。

## Reference Tables
微分法 vs 积分法（例7-1，模型 $-r_A=kC_A^n$，7 个时间点）:

| 方法 | 原理 | k | n | 评价 |
|---|---|---|---|---|
| 微分法 + 非线性回归 | spap2 样条平滑求导，lsqnonlin 拟合速率式 | $0.0055\pm0.0025$ | $1.37\pm0.22$ | 快速，需平滑，置信区间较宽 |
| 积分法 + 非线性回归 | 每次迭代 ode45 积分，浓度残差为目标 | $0.0047\pm0.0016$ | $1.46\pm0.19$ | 置信区间更窄，"积分法较佳" |

模型辨识统计量:

| 统计量 | 定义 | 判据 |
|---|---|---|
| $\rho^2$ | $1-\sum(y_e-y_c)^2/\sum y_e^2$ | 越大越好；简便判据 $\rho^2>0.9$ |
| F 比 | 回归均方和 / 模型误差均方和 | $F>10F_t$（非线性安全系数10、线性4）方可较好预示实验 |
| $F_E$ 比 | $\sigma^2/\sigma_E^2$（模型/实验误差方差） | 与 F 表值比较（安全系数10），给出绝对优劣 |
| 后验概率 $\pi_i$ | 第 i 个模型的后验概率 | 估计模型预示附加实验的能力 |
| 残差分析图 | $(y_e-y_c)$ 对 $y_e$ 标绘 | 均匀分布零线上下侧/对角线两侧为佳 |

## Worked Example
**例7-1 微分法与积分法确定速率方程**：等温间歇反应器中 A→产物，测得 $t=[0\ 20\ 40\ 60\ 120\ 180\ 300]$ s、$C_A=[10\ 8\ 6\ 5\ 3\ 2\ 1]$ mol/L，确定 $-r_A=kC_A^n$ 中的 k 与 n。
- **微分法**（KineticsEst1_Diff.m）: 三次 B 样条最小二乘拟合 spap2(knots=3, K=3)（"使用不经过实验点的 B 样条插值函数"），fnder 求导、fnval 取值得各时刻速率 $r_{Am}$；以 beta0=[0.0053 1.39] 调 lsqnonlin 拟合速率式，nlparci 给置信区间。结果 $k=0.0055\pm0.0025$，$n=1.37\pm0.22$。
- **积分法**（KineticsEst1_Int.m）: 对给定 (k, n) 用 ode45 积分 $\frac{dC_A}{dt}=-kC_A^n$ 得实验点浓度计算值，lsqnonlin 以浓度残差平方和为目标，"每搜索一步(迭代一次)，即调用一次 ode45()"。结果 $k=0.0047\pm0.0016$，$n=1.46\pm0.19$。
- **结论与检验**: "由积分法得到的参数置信区间要比微分法的窄，从这点看，积分法较佳"；残差图显示"各次实验的残差均匀地分布在零线的上下侧，比较满意"。与例3-17 不同之处：用非线性最小二乘直接估计非线性模型参数并给出置信区间，"实际上是最优化方法和统计学的综合运用"。

## Key Takeaways
1. 参数估计目标函数 = 加权残差平方和；ODE 模型每次迭代都要积分，"更应使用二次收敛算法"（lsqnonlin/lsqcurvefit 的 G-N/L-M）。
2. 固定管线：线性化回归（regress 或 X\y）给初值 → lsqnonlin/nlinfit 非线性精修 → nlparci 置信区间 → 残差图检验；初值还可取自模型渐进行为或 LJ 直接搜索。
3. 多响应按 $w_j\propto1/\sigma_j^2$（重复实验方差）加权，代码上用 $[\sqrt{w_1}f_1;\sqrt{w_2}f_2]$ 拼接残差。
4. ODE 估计的目标函数内：ode45 积分 → spline 插值到实验时间点；重复/乱序数据先 sort 再插值。
5. 模型辨识四件套：$\rho^2$、F 比（$F>10F_\alpha(N_p,N_e-N_p)$）、$F_E$ 比、后验概率 + 残差图；绝不只看残差平方和最小——须检查每个参数置信区间是否物理合理。
6. lsqnonlin 与 fmincon 互补（例7-5）：fmincon 收敛更低目标值（$10^{-6}$ 量级）但无置信区间；"先用 fmincon() 计算最优参数值，再把此参数值作为 lsqnonlin() 的初值"，结果不理想时可尝试。
7. 耦合模型（例7-10）可分别辨识：先由实测径向温度积分动力学方程估动力学参数，再解热量平衡方程估传热参数。

## Connects To
- **Ch 3**: 微分法复用例3-17 的样条拟合求导（spap2/fnder/fnval）；平滑用三次样条 csaps。
- **Ch 4**: ODE 模型（间歇反应器、发酵、复杂反应网络）由 ode45 求解，是估计目标函数的内层模拟器（例7-5/7-6/7-9）。
- **Ch 6**: lsqnonlin/lsqcurvefit 即 6.1.8 最小二乘函数；例7-5 用 fmincon 做参数估计器。
- **Ch 8**: 序贯实验法"能节省大量实验，大大提高模型的适定性和参数估计精度"；实验设计（含 D-最优设计）在第8章展开。
