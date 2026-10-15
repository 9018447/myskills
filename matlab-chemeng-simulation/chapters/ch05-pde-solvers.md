# Chapter 5: 化工中的偏微分方程及其求解

## Core Idea
以"方程分类（B²-4AC 判据）→ 边界条件类型 → 方法选择"为主线介绍四大 PDE 数值方法：有限差分法（FDM）、正交配置法（CM）、MOL 法、有限元法（FEM，MATLAB PDE 工具箱）。作者总结的选择原则："对于一维动态模型，优先使用 MATLAB 函数 pdepe()。对于二维稳态模型和二维动态模型：若是含有 2 个方程以下的标准 PDE 问题，则优先选择 pdetool 方法；若是含有 3 个方程以上的标准 PDE 问题，则优先选择 MATLAB PDE 函数的编程方法；只有当 MATLAB PDE 工具箱不能解决时，才考虑使用正交配置法和有限差分法。"

## Frameworks Introduced
- **偏微分方程分类判据**（5.1.1）: 对 Au_xx+Bu_xy+Cu_yy+Du_x+Eu_y+Fu=f（A,B,C 为常数时称拟线性），"当 B²-4AC<0 时，方程为椭圆型；当 B²-4AC=0 时，为抛物型；当 B²-4AC>0 时，为双曲型"
  - When to use: 拿到任何 PDE 先判型——化工中最普遍的是抛物型（初值问题，时间开域）与椭圆型（边值问题，空间闭域），"双曲型方程则很少见"
- **Crank-Nicolson 隐式差分格式**（例5-2）: 在节点 (x_i, t_{j+1/2}) 处对 ∂T/∂t 与 ∂²T/∂x² 均用中心差分，得 −rT_{i−1,j+1}+(2+2r)T_{i,j+1}−rT_{i+1,j+1}=rT_{i−1,j}+(2−2r)T_{i,j}+rT_{i+1,j}（r=ατ/h²），构成三对角方程组 AX=B 用 TDMA 求解。表5-4 注："显式差分法是不稳定的，而 Crank-Nicholson 方法稳定有效"
- **对称正交配置法**（5.3）: 加权余量法的一种——"选择一多项式作为试函数……令在各配置点试函数代入微分方程后的残差（'余量'）为零"。对称问题试函数 y=y(1)+(1−x²)Σa_iP_i(x²)（P_i 为正交多项式，a=1平板/a=2圆柱/a=3球）；导数近似 dy/dx=Ay、d²y/dx²=By，其中 A=CQ⁻¹、B=DQ⁻¹（配置常数矩阵，圆柱对称 N=3 数值见表5-3）
  - How: ①求 P_N(x²) 的 N 个零点并令 x_{N+1}=1 ②算 Q、C、D→A、B ③各配置点代回原方程得余量方程 ④并入边界方程 ⑤解代数方程组
- **MOL 法（线上法）**（5.4.1）: "将一个自变量当成连续变量，而对其余的自变量用有限差分法或者正交配置法进行离散，从而把偏微分方程转变为常微分方程组，然后用龙格-库塔法积分求解"，适用于一维动态和二维稳态 PDE（例5-5）
- **pdepe() 标准型**（5.4.2）: c(x,t,u,u_x)·u_t = x⁻ᵐ ∂/∂x(xᵐ·f(x,t,u,u_x)) + s，m=0,1,2 分别代表平板、圆柱和球形；"若 c 的元素是零，则为椭圆型方程，若是正数，则为抛物型方程，必须至少有一个方程是抛物型方程才可使用 pdepe() 求解"；边界条件以通量项表示：p(x,t,u)+q(x,t)·f=0，"只有 p(x,t,u) 与 u 有关，而 q(x,t) 与 u 无关"；解为三维数组 sol(j,k,i)（时间,空间,因变量）；pdeval() 计算 xmesh 之外各点的解及偏导数
- **MATLAB PDE 工具箱（有限元法）**（5.5）: 求解四大类方程——椭圆型 −∇·c∇u+au=f（assempde/pdenonlin）、抛物型 d·u_t−∇·c∇u+au=f（parabolic）、双曲型（hyperbolic）、本征值问题（pdeeig）；总装配 (K+M+Q)U=F+G（K 刚度矩阵、M 质量矩阵、Q/G 边界贡献）
  - How: pdetool 七步流程（Options 设模式→Draw 画几何→Boundary 设边界→PDE 定方程→Mesh 划网格→Solve→Plot）；命令行四步流程（问题定义 wgeom/wbound→网格 initmesh/refinemesh/jigglemesh→求解→显示 pdesurf/pdeplot）
- **柱坐标伪装成 x-y 标准形**（5.5.1、例5-15/5-16）: 轴对称 r-z 问题 (1/r)∂/∂r(r·u_r)+u_zz=f(u) 经 x≡r、y≡z 变换为 −∇·x∇u=−x·f(u)；"由于 c、f 与 x、u 有关，程序中 c、f 的表达式要用字符串表示"，用 pdenonlin() 求解

## Key Concepts
- **Dirichlet/Neumann/Robin 边界条件**: 第一类 u|∂Ω=φ；第二类（已知导数）(∂u/∂n)|∂Ω=φ；第三类（混合）(∂u/∂n+qu)|∂Ω=φ
- **虚设点法**: 处理导数边界条件——"考虑边界外面一个外加'虚设'的点上的温度。为保持对称，这个虚设点上的温度必须等于边界内对应点上的温度"，使边界点成为扩充问题的内点（例5-3）
- **罗必塔（L'Hopital）法则处理轴对称奇点**: r→0 时 (∂T/∂r)/r→∂²T/∂r²，柱坐标 1/r·∂T/∂r 项化为 2a₁∂²T/∂r²（例5-3 中心轴方程）
- **TDMA（三对角阵算法/追赶法）**: Crank-Nicolson 每时间层形成的三对角系统 AX=B 的专用直接解法
- **配置点与配置常数**: 正交多项式 P_N(x²) 的根为内配置点（x_{N+1}=1）；矩阵 A、B 把配置点上函数值映射为一、二阶导数值
- **pdepe 系数 c、f、s**: c 对角阵元素零→椭圆型、正→抛物型；f 通量项；s 源项
- **刚度矩阵/质量矩阵**: 有限元装配 (K+M+Q)U=F+G 中的 K 与 M；assema() 计算面积分贡献，assemb() 计算边界条件贡献
- **无因次数群**（例5-8）: Φ²（Thiele 模数平方）、β（Prater 数）、Le（Lewis 数）、Bi_m/Bi_h（传质/传热 Biot 数）共同决定催化剂颗粒动态热质传递行为

## Mental Models
- Use 椭圆型+闭域思维 when 稳态问题（Poisson/拉普拉斯）；Use 抛物型+初值思维 when 动态问题——先判型，方法空间立即缩小
- Use pdepe() 一站式 when 一维动态 PDE（组）：只需写 pdefun（c,f,s）、icfun、bcfun 三个函数
- Use "伪装"思维 when 轴对称/非标准系数方程：通过变量替换与无因次化把方程凑成工具箱标准形，而不是改写工具箱
- Use 正交配置 when 几何对称且解的梯度不陡；Use FD/FEM when 梯度陡——5.6："对于扩散-反应问题，正交配置法远远优于其他方法。如果问题不太困难，其解的梯度不陡，则使用正交配置法是空间近似的优先方法。若解的梯度较陡，则 FD 或 FEM 优先"

## Anti-patterns
- **显式差分格式**: 数值不稳定（表5-4 注），动态问题应采用 Crank-Nicolson 或直接 pdepe()/MOL
- **MOL 步长过大**: 5.6 小结 "必须注意步长要足够小，否则不收敛"（"为了避免数值不稳定性，需要用小步长，这可能耗费较多的计算时间"）
- **无因次化破坏标准形**: 例5-11 注——若按 X=x/B 无因次化，方程多出 (B/W)² 系数、"显然，此方程形式上与标准抛物型 PDE 方程（5-29a）不一致，不能直接用 pdetool 或命令行函数求解"；应按 X=x/H 无因次化
- **用 pdetool 解 3 个以上方程的 PDE 组**: 5.5.4 "用 pdetool 图形用户界面只能求解方程数为 2 以内的 PDE 标准问题，3 个方程以上的 PDE 问题，即使符合标准形式，也无法用它求解"，须改用命令行函数
- **pdepe 边界条件用 ∂u/∂x 而非通量 f 表示**: "注意 边界条件以通量项 f(x,t,u,∂u/∂x) 表示，而不用 ∂u/∂x 表示"
- **网格无节制细化**: "网格越细，计算时间越长，所以网格的精细化次数要适当"

## Code Examples
```matlab
function PDE1Dd_pdepe % 用 MATLAB 函数 pdepe()求解一维动态模型
global alpha ua ub
alpha = 2.0; ua = 100; ub = 0; m = 0; a = 0; b = 10; t0 = 0; tf = 8;
x = linspace(a, b, 6); t = linspace(t0, tf, 17);
sol = pdepe(m, @PDEfun, @ICfun, @BCfun, x, t);

% Extract the first solution component as u. This is not necessary
% for a single equation, but makes a point about the form of the output.
u = sol(:, :, 1), [m, nt] = size(t); nt = [1:1:nt], [m, nx] = size(x);

% analytical solution
n = [1:1000];
for i = 1:length(t)
    for j = 1:1:nx,
    u_analytical(i, j) = 100.0-10.0*x(j)-200/pi*sum(sin(n.*pi*...
    (j)/10).*exp(-n.^2*pi^2*alpha.*t(i)/100)./n)
    end
end
% surface plot of the solution
figure; surf(x, t, u); title('Numerical solution computed with 6 mesh points.');
xlabel('Disuance x'); ylabel('Time t');

% solution profile at t=8
figure; plot(x, u(end, :), 'o', x, u_analytical(end, :)); title('Solutions at t = 8.');
legend('Numerical, 6 mesh points', 'Analytical', 0); xlabel('Distance x'); ylabel('u(x, 8)');
%----
function [c, f, s] = PDEfun(x, t, u, DuDx)
global alpha
c = 1/alpha; f = DuDx; s = 0;
%----
function u0 = ICfun(x)
u0 = 0; % degree centigrade
%----
function [pl, ql, pr, qr] = BCfun(xl, ul, xr, ur, t)
global ua ub
pl = ul-ua; ql = 0; pr = ur-ub; qr = 0;
```
- **What it demonstrates**: pdepe() 三函数标准写法：PDE 方程映射为 c=1/α, f=DuDx, s=0；定值边界条件写成 pl=ul−ua, ql=0 的通量形式；结果与解析解对照（表5-4 中 PDEPE 与解析解非常接近）

```matlab
function U = CrankNicolson(f, c1, c2, a, b, alpha, n, m)
% Initialize parameters and U
h = a/(n-1); k = b/(m-1); r = alpha*k/h^2; s1 = 2+2/r; s2 = 2/r-2; U = zeros(n, m);
% Boundary conditions
U(1, 1:m) = c1; U(n, 1:m) = c2;
% Generate first row (that is, the first column in matrix U)
U(2:n-1, 1) = feval(f, h:h:(n-2)*h)';

% Form the diagonal and off-diagonal elements of A and
% the constant vector B and solve tridiagonal system AX=B

Vd(1, 1:n) = s1*ones(1, n); Vd(1) = 1; Vd(n) = 1;
Va = -ones(1, n-1); Va(n-1) = 0;
Vc = -ones(1, n-1); Vc(1) = 0;
Vb(1) = c1; Vb(n) = c2;
for j=2:m
    for i=2:n-1
    Vb(i) = U(i-1, j-1) + U(i+1, j-1) + s2*U(i, j-1);
    end
    X = TDMA(Va, Vd, Vc, Vb);
    U(1:n, j) = X';
end
U = U'
```
- **What it demonstrates**: Crank-Nicolson 隐式格式逐时间层推进：右端向量 Vb 由上一层解组装，三对角系统交 TDMA（追赶法）求解

## Reference Tables
PDE 类型 → 方法映射：

| PDE 类型 | 判据/典型方程 | 问题性质 | 推荐方法 |
|---|---|---|---|
| 抛物型 | B²-4AC=0；u_t=αu_xx | 初值问题（时间开域） | pdepe()；Crank-Nicolson；MOL |
| 椭圆型 | B²-4AC<0；u_xx+u_yy=0 | 边值问题（空间闭域） | PDE 工具箱 assempde/pdenonlin；FDM 迭代 |
| 双曲型 | B²-4AC>0；u_tt=α²u_xx | 初值问题 | hyperbolic()（化工少见） |

MATLAB PDE 求解函数速查（表5-7 精简）：

| 函数 | 适用方程 | 功能 |
|---|---|---|
| assempde | 椭圆型 (5-28a/b) | 组装刚度矩阵及右端项并求解 |
| pdenonlin | 非线性椭圆型 (5-28c/d) | 非线性椭圆求解器 |
| parabolic | 抛物型 (5-29a/b) | u1=parabolic(u0,tlist,b,p,e,t,c,a,f,d) |
| hyperbolic | 双曲型 (5-30a/b) | 用法同 parabolic，多一初始导数 ut0 |
| pdeeig | 本征值 (5-31a/b) | 特征值问题 |
| adaptmesh | 椭圆型 | 自适应网格生成并求解 |
| poisolv | 矩形网格 | 快速求解泊松方程 |

## Worked Example
**例5-8 用 pdepe() 求解多孔球形催化剂颗粒中的热质传递模型**（苯催化加氢制环己烷，镍基催化剂）：
- **问题**: 模拟催化剂颗粒启动过程中苯（y_B）、氢（y_H）浓度与温度（θ）的时空分布；环境条件 C_B⁰(t) 等随反应器扰动变化。
- **模型方程**: ε∂C_B/∂t=(D_e/r²)∂/∂r(r²∂C_B/∂r)−R_B；ε∂C_H/∂t=(D_e/r²)∂/∂r(r²∂C_H/∂r)−3R_B；ρc_p∂T/∂t=(λ_e/r²)∂/∂r(r²∂T/∂r)+(−ΔH)R_B。边界：r=0 处 ∂/∂r 全为零；r=r_P 处 D_e∂C/∂r=k_g[C⁰(t)−C]、λ_e∂T/∂r=h_g[T⁰(t)−T]（Bi 数型对流传质/传热条件）；动力学为 Langmuir-Hinshelwood 型 R_B。
- **无因次化**: x=r/r_P，得由 Φ²（Thiele）、β（Prater）、Le（Lewis）、Bi_m、Bi_h 五个准数控制的方程组。
- **pdepe 映射**: m=2（球形）；c=[1;1;Le]；f=[DuDx(1);DuDx(2);DuDx(3)]；s=[−Φ²R; −3Φ²(C_B⁰/C_H⁰)R; βΦ²R]；左边界 pl=[0;0;0]、ql=[1;1;1]；右边界 pr=[−Bi_m(1−y_B); −Bi_m(1−y_H); −Bi_h(1−θ)]、qr=[1;1;1]。
- **结果**: τ=0.1 时苯的无因次浓度 y_B 从颗粒中心 0.2677 升到表面 0.9973（h=0.125）；网格加密至 h=0.125/4 时中心值 0.2682，数值收敛；y_B~x 曲线（t=0.01, 0.1, 1）与三维分布 y_B(x,t) 如图 5-6、5-7。

## Key Takeaways
1. 先判型（B²-4AC）再选法；化工 PDE 以抛物型初值问题和椭圆型边值问题为主。
2. 一维动态问题默认 pdepe()：把方程凑成 c·u_t=x⁻ᵐ∂(xᵐf)/∂x+s、边界凑成 p+qf=0（通量形式）就成功了 90%。
3. 手写 FDM 只用 Crank-Nicolson 隐式格式（配 TDMA）；显式格式不稳定，弃用。
4. 轴对称 r=0 奇点：FDM 用罗必塔法则改写中心方程；FEM 用 −∇·x∇u=−xf(u) 伪装成标准形，c、f 用字符串传入。
5. 非标准或 >2 方程的问题用命令行函数；pdetool 还可兼做几何/边界 M 文件生成器（wgeom/wbound），大幅减少编程量。
6. 二维稳态 PDE 组也可只在径向正交配置、轴向保持连续化成 ODE 组（例5-4，管长 0.994 m），与 FDM 结果（例5-3，0.993 m）一致。
7. 源项/边界含 u 的强非线性时优先 pdenonlin()（如例5-15 催化剂有效因子 η=0.8371）。

## Connects To
- **Ch3**: FDM 的差分表达式与 ODE 求解器是本章 MOL 的基础；正交配置解 ODE-BVP 与 3.4 节衔接
- **Ch4**: 例5-8 是例4-11/4-12 催化剂颗粒稳态 BVP 的动态推广；MOL 的产物是第4章的 ODE 组；固定床二维拟均相模型（例5-3/5-4）承接例4-5 的一维版
- **Ch6**: 正交配置/FDM 离散后的代数方程组可嵌入最优设计计算
- **Ch7**: PDE 模型（例5-8 型）的参数估计需要本章求解器作仿真内核
