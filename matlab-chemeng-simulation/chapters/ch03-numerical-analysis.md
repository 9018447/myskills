# Chapter 3: MATLAB 在数值分析中的应用

## Core Idea
化工数值计算的四大件——插值/拟合、数值积分/微分、代数方程（组）、常微分方程 IVP/BVP——在 MATLAB 中全部有现成函数，本章的任务是建立"问题类型 → 正确函数"的选择判据。核心分界线：数据含实验误差用最小二乘拟合（不要求过点，"只要求残差平方和最小"），无噪声数据用插值；方程求解器都是 function function，第一参数传 @fun。

## Frameworks Introduced
- **最小二乘法拟合**: 作者原话——"其基本思路是，在给定点 $x_i$ 上使残差平方和 $\Sigma(f(x_i)-y_i)^2$ 最小。由于观测数据往往带有实验误差，而最小二乘拟合方法并不要求拟合函数 $y=f(x)$ 经过所有的实验点 $(x_i,y_i)$，只要求残差平方和最小，因此，用最小二乘法来拟合实验数据是非常合适的"。
  - When to use: 实验数据/工业数据需要连续光滑曲线时
  - How: 多项式拟合 polyfit(x,y,n)+polyval(p,x)（n=1 即线性回归）；样条拟合三函数 csaps（三次样条，平滑参数 p∈[0,1]，p=0 相当于最小二乘直线拟合，p=1 相当于 csapi()/spline() 插值）、spap2（B样条，可调参数 knots 与样条阶数 K 两个）、spaps（B样条，平滑处理）；拟合结果用 fnval(f,x) 取值
- **数值微分四方法**: ①有限差分法 dy=diff(y)/diff(x)，"此方法用一阶差分，精度较差"；②多项式拟合法 离散数据→polyfit()→多项式 p→polyder()→导函数 pp→polyval()→pp 在 xi 的导数值；③三次样条插值法 csapi()→fnder()→fnval()，"使用这种插值方法一般不如使用最小二乘拟合方法（2）、（4）好"；④样条拟合法（最小二乘）csaps()或spap2()或spaps()→fnder()→fnval()。作者结论——"上述四种方法中，方法（2）和方法（4）较好"。
  - When to use: 只有离散数据要求导数（干燥速率、动力学初始速率等）
  - How: fnder(f,dorder) 默认 dorder=1；"对拟合多项式求高阶导数时，阶数越高计算误差就越大。因此，通常仅限于低阶数值微分"
- **数值积分函数体系**（Newton-Cotes 系列）: trapz（梯形，对离散数据）、quad（自适应 Simpson，低阶）、quadl（自适应 Lobatto，高阶）。作者原话——"在定义 fun 时，被积函数表达式必须是向量形式，即表达式必须使用点运算符（.*、./和.^）以支持向量"；"建议优先采用自适应高阶求积函数 quadl()"。
  - When to use: 精馏理论板数、填料塔传质单元数、反应器体积/空时、逸度系数、停留时间分布等积分式（式3-5~3-15）
  - How: q=quadl(@fun,a,b,tol,trace,p1,p2,...)；被积函数可为复合函数（先 fnval 样条得平衡关系，再代入被积函数）；"若为非向量形式……则用 quad() 和 quadl() 求积时将出错"
- **非线性方程求解器选择**: fzero() 求单变量方程，"该函数结合使用二分法、割线法（secant）和可逆二次内插法（inverse quadratic interpolation）"；roots() 求多项式全部根；fsolve() 求方程组，"其算法是最小二乘法"。作者注——"若某个问题有多个解，则实际获得的解将取决于给定的初值。许多化工过程有'多解'，即有一些稳态点。实际上，稳态的获得将取决于动态考虑，例如开车的过程。对单变量系统，建议画出 f(x)，以观察计算结果是否合理"。
  - When to use: 状态方程 p-V-T、简单蒸馏、泡点/露点/闪蒸（"这些问题都是单变量非线性方程的求解问题"）、CSTR 转化率、化学平衡等
  - How: 初值策略——范德华方程初值"根据理想气体状态方程确定"；泡点"以纯苯的沸点作为其计算的初值。因为混合液中苯含量最多"；闪蒸初值"应该避免出现过热或过冷状态"；化学平衡初值"必须满足约束条件：xe1+xe2+xe3<1"
- **刚性问题判据与求解器切换**: 作者原话——如果系数矩阵 A 的特征值满足"$Re\lambda_i<0$ 且 $\max|Re\lambda_i|/\min|Re\lambda_i|$ 是个大数，则称为刚性方程组。其中 $\max|Re\lambda_i|/\min|Re\lambda_i|$ 称为刚性比"（非线性问题 $\lambda_i$ 取 $\partial f/\partial y$ 的特征值）。
  - When to use: 化学反应和自动控制领域的病态方程组
  - How: "一般的做法是，优先用 ode45() 求解，若能顺利解出即大功告成，否则，若长时间没解完（或者感觉像死循环或死机），可能就是刚性问题，这时，可中断程序改用刚性求积函数（如 ode23s）"
- **BVP 标准化与 bvp4c 三步流程**: 高阶方程降阶（y₁=y, y₂=y′,…, yₘ=y⁽ᵐ⁻¹⁾）；特征值问题引入 y_{N+1}≡λ 与 dy_{N+1}/dx=0；自由边界问题引入 y_{N+1}≡b-a。求解步骤——"调用函数 bvpinit() 以生成在 [a,b] 内的给定初始网格 x 上的初始猜测解（结构）；调用函数 bvp4c() 利用配置法得到解 sol（结构）；调用函数 deval() 计算在 [a,b] 内任意点 xint 处的解"。BVP 数值解法两大类：打靶法（先把 BVP 化为 IVP，用 Newton-Raphson 寻 V 使残差 F=0）与松弛法（有限差分法和配置法）；"MATLAB 提供的 ODE-BVPs 求解器，是采用配置法进行求解的，其算法非常有效，几乎可以解决所有的 ODE-BVPs 问题"。

## Key Concepts
- **插值 vs 拟合**: 插值曲线经过全部离散点（适用于已平滑/无噪声数据）；"与样条插值不同，样条拟合并不要求曲线通过全部的数据点"，故"样条拟合比样条插值应用更广泛"
- **spline()**: 三次样条插值，yi=spline(x,y,xi) 等同于 interp1(x,y,xi,'spline')；pp=spline(x,y) 返回分段多项式，用 ppval(pp,xi) 求值
- **csaps(x,y,p)**: 平滑生成三次样条（最小二乘准则，式3-2），平滑参数 p∈[0,1]
- **spap2(knots,k,x,y)**: 最小二乘 B 样条拟合（式3-3），knots 与 K 两个可调参数，"前者更灵活，这也是由 B 样条本身的性质所决定的"
- **polyfit/polyder/polyval**: 多项式最小二乘拟合 → 求导 → 求值链；"线性回归是 n=1 时的特例"
- **trapz/quad/quadl**: 分别为梯形（低精度）、自适应 Simpson 低阶、自适应 Lobatto 高阶求积
- **奇异积分**: "分为反常积分（被积函数在某一点上无界）与无穷积分"；例3-10 中"若用 trapz() 进行此奇异积分，结果将是 Inf（无穷大），显然不正确"
- **fzero/roots/fsolve**: 单变量非线性方程（二分+割线+逆二次内插）／多项式全部根／非线性方程组（最小二乘法算法）
- **刚性比**: $\max|Re\lambda_i|/\min|Re\lambda_i|$，例中 y₁′=-0.01y₁-99.99y₂、y₂′=-100y₂ 的刚性比为 100/0.01=10000
- **ode45/ode23s**: 四五阶 Runge-Kutta（非刚性首选，"最常用的是 ode45() 和 ode23s()"）与二阶改进 Rosenbrock（刚性）
- **bvpinit/bvp4c/deval**: BVP 初始猜测结构 → 配置法求解 → 任意点取值；sol 结构含 sol.x、sol.y、sol.yp、sol.solver 四个域
- **打靶法**: "即先把 ODE 边界问题转化为初值问题，然后按初值问题的解法求解"，终点残差向量 F 满足边界条件时 F=0
- **ODE 方程组的列向量要求**: "在定义微分方程组的函数 f() 中，函数返回值必须是列向量：dydx=[f1; f2]，若为行向量 dydx=[f1 f2] 则出错"（ode45/ode23/bvp4c 同）

## Mental Models
- **Use 拟合 when 数据含实验误差; use 插值 when 数据无噪声**: 例3-7 用 spline 插值青霉素发酵数据得 Ci 第一个值为负（-0.0274×10⁴），"不符合实际物理意义，这是由插值误差造成的"；作者注——"因存在实验误差，用拟合应更符合实际"；例3-11 注——无噪声数据用三次样条插值很满意，"对于实际科学研究与工程应用，由于实验数据一般包含噪声（误差），必须改用三次样条拟合方法"
- **Use quadl() when 做数值积分**（奇异积分绝不用 trapz）: 例3-10 中 quadl 得 0.84111708263095，quad 得 0.84113024315845，准确值 0.84111692——"显然，自适应高阶求积函数 quadl 得到的结果更接近准确值"
- **Use ode45() first; switch to ode23s() when 卡死**: 例3-30 中"用 ode45() 导致发散，而用 ode23s() 会很快收敛"
- **Use 初值物理背景 when 调 fzero/fsolve**: fzero "一般得到靠近给定初值的根"（例3-18：x0=0 得根 -1，x0=2 得根 3）；多项式方程用 roots() 求全部根，"而用 fzero() 则很难得到全部的根"

## Anti-patterns
- **对含噪声实验数据用插值（spline/csapi）**: 插值强制过点会放大误差，出现负浓度等非物理结果（例3-7）
- **用 trapz() 算奇异积分**: 结果为 Inf；且对无穷积分不适用
- **有限差分法做数值微分**: "所用的差分公式只有1阶精度"（例3-11 中"有限差分法得到的曲线很差"）；改中心差分可改善"但编程比较麻烦"
- **多项式拟合不试阶数**: "多项式拟合求导方法必须选用合适的阶数，否则插值效果会很差，如阶数取3时效果较差。因此需要尝试不同的阶数，这里阶数取5是经过尝试后确定的"
- **用 fzero() 求多项式方程的根**: 难以得到全部根，应该用 roots()
- **线性化后做线性拟合求动力学参数**: "这种方法由于将原来的非线性模型进行线性化，最终得到的结果从统计方面来说，是不严格的，只能算是近似的。因此，应尽量使用最优化方法（如非线性最小二乘法）直接由非线性模型估计其参数"（见第7章例7-1）
- **用微分法分析动力学数据而不优先用积分法**: "数值微分从本质上精度要比数值积分差，所以动力学数据应尽量使用积分法分析"
- **闪蒸目标函数用 Σxi=1 与 Σyi=1 两个方程**: "若直接应用式（4）和式（5），则收敛很慢。而把式（4）和式（5）结合成如下一个函数，会得到较好的收敛特性：f(T)=Σy−Σx=0"，即 f(T)=Σ(Kᵢ-1)zᵢ/[1+β(Kᵢ-1)]=0
- **fzero/fsolve 初值随意取**: 解取决于初值；闪蒸初值不当会"使混合物处于过热或过冷状态，因此不发生闪蒸"；化学平衡初值必须满足 xe1+xe2+xe3<1

## Code Examples
```matlab
function KineticDataFit
clear all; clc
% 动力学数据
t = [0 20 40 60 120 180 300]; % t -- vector of reaction time
CA = [10 8 6 5 3 2 1]; % CA -- concentration vector for reactant A
% 用最小二乘样条拟合法计算微分 dCA/dt--使用不经过实验点的 B 样条插值函数
knots = 3; K = 3; % 三次 B 样条
sp = spap2(knots, K, t, CA)
sp = spap2(newknt(sp), K, t, CA);
pp = fnder(sp)
dCAdt = fnval(pp, t) % 计算 B 样条函数的导函数 pp 及其在 t 处的导函数值
% 绘制图形
ti = linspace(t(1), t(end), 200); CAi = fnval(sp, ti)
plot(t, CA, 'ro', ti, CAi, 'b-', xlabel('t'), ylabel('C_A')
figure, fnplt(pp), xlabel('t'), ylabel('dC/dt')
% 线性拟合
rA = dCAdt; y = log(-rA); x = log(CA);
p = polyfit(x, y, 1);
k = exp(p(2)), n = p(1)
```
- **What it demonstrates**: 例3-17 微分法动力学数据分析完整链——spap2 拟合 → fnder 求导 → fnval 取 dCA/dt → ln(-rA)=n·lnCA+lnk 线性拟合得 k=0.0053, n=1.39；"通过反复调整参数 knots 和 K，可使函数 spap2() 对数据拟合得更好"

```matlab
function xBVP1
clear all; clc, format long e, a = 0; b = 1;
% solution is obtained using an initial guess of y1(x)=1, y2(x)=0
solinit = bvpinit(linspace(a, b, 10), [1 0]);
sol = bvp4c(@ODEfun, @BCfun, solinit);
x = [0:0.1:0.5];
y = deval(sol, x);
DispResult_xBVP % 调用 DispResult_xBVP.m（见光盘）以显示结果
% ----
function dydx = ODEfun(x, y)
dydx = [y(2); y(1)+10];
% ----
function bc = BCfun(ya, yb)
bc = [ya(1); yb(1)];
```
- **What it demonstrates**: 例3-31 两点边值问题 y″-y=10, y(0)=y(1)=0 的标准解法——降阶为方程组（y₁′=y₂, y₂′=y₁+10）、bvpinit 生成初猜、bvp4c 配置法求解、deval 取值；数值解与精确解在 6 位内一致（如 x=0.5: -1.13181425 对 -1.13181116）

```matlab
% 去掉重复解即得到多稳态解
for i=1:n, sy(i) = sum(y{i}); end
[sy, i1] = sort(sy); dsy = diff(sy); i2 = find(abs(dsy)>1e-6); i2 = [1, i2+1];
fprintf('\n有%d%s', length(i1(i2)), '个稳态解(CA,T,TJ0):'), y{i1(i2)}
```
- **What it demonstrates**: 例3-27 多稳态解自动去重技巧——初值扫描的解存单元数组 y{i}，各单元求和得 sy(i)，sort 排序并记录原下标 i1，diff 找相邻差值，find(abs(dsy)>1e-6) 定位非重复元素，不同稳态解即 y{i1(i2)}

## Reference Tables
表 3-8/3-9 MATLAB 的 ODE-IVP 积分函数（作者注："精度较高者，其速度较慢，反之亦然"；"上述各 MATLAB 积分函数都是变步长积分，且自动选择步长，计算稳定可靠"）：

| 类别 | 函数 | 算法 | 精度 |
|---|---|---|---|
| 非刚性 | ode45 | 四五阶 Runge-Kutta 法 | 较高 |
| 非刚性 | ode23 | 二三阶 Runge-Kutta 法 | 低 |
| 非刚性 | ode113 | 可变阶 Adams-Bashforth-Moulton 法 | — |
| 刚性 | ode15s | 基于数值差分的可变阶方法 (BDFs, Gear) | 低~中 |
| 刚性 | ode23s | 二阶改进的 Rosenbrock 法 | 低 |
| 刚性 | ode23t | 使用梯形规则 | 适中 |
| 刚性 | ode23tb | TR-BDF2（隐式 Runge-Kutta 法） | 低 |

插值与拟合函数选择（表 3-1、3-2 及 3.5 节小结）：

| 任务 | 函数 | 要点 |
|---|---|---|
| 一维/快速一维插值 | interp1 / interp1q | method: nearest、linear(默认)、spline、pchip、cubic；'extrap' 外插；x 须单调 |
| 二维/三维/N维插值 | interp2 / interp3 / interpn | 用法与 interp1 相似 |
| FFT 一维插值 | interpft | — |
| 分段三次 Hermite 插值 | pchip | — |
| 三次样条插值 | spline（+ppval） | 等同于 interp1(...,'spline')；插值精度最高（例3-1） |
| 多项式最小二乘拟合 | polyfit + polyval | 单变量；线性回归为 n=1 特例 |
| 三次样条拟合（最小二乘，平滑） | csaps(x,y,p) | p∈[0,1]；p=0 直线拟合，p=1 等于 csapi/spline 插值 |
| B 样条拟合（最小二乘，不平滑） | spap2(knots,k,x,y) | knots 与 K 两个可调参数，比 polyfit 更灵活 |
| B 样条拟合（最小二乘，平滑） | spaps | 拟合准则同 spap2 |
| 样条/多项式取值 | fnval / polyval | 拟合结果 sp、p 的通用取值函数 |

## Worked Example
**例3-27 非等温 CSTR（夹套换热）的多稳态解**：
- **问题**: CSTR 中进行 A→k B，流量 F₀=F=40 ft³/h、持液量 V=48 ft³ 恒定，夹套冷却水流量 F_J=49.9 ft³/h 恒定且混合完全；C_A0=0.55 lbmol/ft³、T₀=T_J0=530°R、k₀=7.08×10¹⁰ h⁻¹、E=30000 Btu/lbmol、ΔH=-30000 Btu/lbmol、UA_H=150×250 等，求全部稳态解
- **模型**: 稳态物料衡算 F₀C_A0-FC_A-VkC_A=0；反应器热量衡算 F₀T₀-FT-[(-ΔH)VkC_A+Q]/(ρc_p)=0；夹套热量衡算 F_J(T_J0-T_J)+Q/(ρ_J c_pJ)=0；其中 Q=U·A_H·(T-T_J)，k=k₀exp(-E/RT)——三个方程构成非线性代数方程组
- **数值方法**: fsolve（最小二乘法算法）求方程组
- **MATLAB 要点**: ①多稳态→初值扫描：循环让 T 初值 Ti 以 10°R 为增量从 530°R 变到 730°R（CA0=0.55、TJ0=530 固定），`sol = fsolve(@Equations, [CA0,Ti(i),TJ0]); y{i} = sol;` 把全部解存入单元数组；②自动去重：sum→sort→diff→find(|dsy|>1e-6) 得不同稳态解 y{i1(i2)}；③参数用 global 传递，Equations() 返回列向量 f=[f1;f2;f3]
- **结果**: 共 3 个稳态解（三个状态）：(C_A, T, T_J) = (0.5214, 537.85, 537.25)、(0.3302, 590.35, 585.73)、(0.0354, 671.28, 660.46)。印证作者注——"许多化工过程有'多解'，即有一些稳态点"

## Key Takeaways
1. 先判数据性质再选工具：含误差→拟合（spap2/csaps/spaps/polyfit），无噪声→插值（spline/csapi）；插值精度以三次样条最高（例3-1），但对噪声数据会产生非物理负值（例3-7）。
2. 数值积分优先 quadl()；被积函数必须写成向量形式（点运算）；奇异积分禁用 trapz（结果 Inf）。
3. 数值微分走"拟合→求导→求值"链：polyfit→polyder→polyval 或 spap2/csaps→fnder→fnval；diff() 一阶差分精度差；多项式拟合阶数要试（例3-11 试出 5 阶）。
4. 方程求解器分工：多项式方程→roots()（全部根）；单变量非线性→fzero()（根靠近初值，先画 f(x) 检验）；方程组→fsolve()；线性方程组→A\b 或 inv(A)*b。
5. 初值是化学问题不是数值问题：按理想气体状态方程、纯组分沸点、进料组成等物理背景给初值；闪蒸合并 Σy-Σx 为单一目标函数以改善收敛。
6. ODE-IVP：先 ode45()，长时间未解完或发散→刚性问题→改 ode23s()；判据是刚性比 max|Reλ|/min|Reλ| 为大数；方程组函数必须返回列向量。
7. ODE-BVP 三步流程 bvpinit→bvp4c→deval；高阶方程先降阶，特征值/自由边界问题加一个 dy/dx=0 的辅助变量标准化。
8. 多稳态问题的通用流程：循环扫初值 + fsolve + 单元数组存解 + sort/diff/find 自动去重。
9. 动力学数据尽量用积分法分析（微分法本质精度低）；线性化拟合只算近似，严格参数估计用非线性最小二乘（第7章）。

## Connects To
- **Ch 2 (MATLAB编程基础)**: 本章所有求解函数（quadl、fzero、fsolve、ode45、bvp4c）都是 function function，第一参数 @fun 的机制在例2-4 建立
- **Ch 1**: 落实"模型→解法→MATLAB函数"的编写框架，本章是全书数值方法的总纲
- **Ch 4 (常微分方程化工应用)**: 本章给出 IVP/BVP 解法，"由于化工方面的 ODE 问题很多，有关应用实例将在第四章中专门介绍"
- **Ch 5 (偏微分方程)**: BVP 的有限差分法与配置法（正交配置法）"第5章将介绍如何使用该方法来求解 PDE 方程"；奇异 BVP 对应柱形/球形对称 PDE
- **Ch 7 (参数估计和模型辨识)**: 线性化拟合的动力学参数只作初值，严格估计用非线性最小二乘（例7-1）；初始速率法回归结果同样"最好以此为初值，再利用非线性回归方法进行估计"
