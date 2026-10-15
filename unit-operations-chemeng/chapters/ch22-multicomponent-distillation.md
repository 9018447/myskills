# Chapter 22: Introduction to Multicomponent Distillation

## Core Idea
多组分精馏没有 McCabe-Thiele 那样的通用图解法，转而用 K 因子描述相平衡，用"轻/重关键组分"定义分离任务，以群法（Fenske、Underwood、Gilliland）做初步设计，用逐板计算（Lewis–Matheson / 计算机矩阵法）做精确解；核心新现象是两组夹紧区不重合、非关键组分的分布与浓度剖面的反常。

## Frameworks Introduced
- **K factor（分配系数）**：$K_i \equiv y_{ie}/x_{ie}$；Raoult-Dalton 下 $K_i = P_i'/P$；相对挥发度 $\alpha_{ij} = K_i/K_j$（K 随温度变化大，比值变化小）。
- **Bubble/dew-point calculation**：泡点 $\sum K_i x_i = 1$，露点 $\sum y_i/K_i = 1$，试差求 T；$\sum$≈1 时 $y_i = K_i x_i/\sum K_j x_j$。
- **Multicomponent flash**：$\sum \dfrac{x_{Fi}}{f(K_i - 1) + 1} = 1$ 试差求 T，再定两相组成；进料预热温度由焓衡算反推。
- **Key components（关键组分）**：轻关键 LK / 重关键 HK 按挥发度相邻优先（sharp separation）；规定 LK 在塔顶、HK 在塔底的浓度或回收率；比 LK 轻的几乎全进馏出液，比 HK 重的几乎全进釜液。
- **Fenske equation（多组分形式）**：$N_{\min} = \dfrac{\ln[(x_{Di}/x_{Bi})/(x_{Dj}/x_{Bj})]}{\ln \bar\alpha_{ij}} - 1$，$\bar\alpha$ 取 D、F、B 三点温度值的立方根几何平均。
- **Distributed vs undistributed components**：分布组分同时出现在两股产品中（两关键必分布）；最小回流下，重非关键组分若 $K$ 比重关键低 ≥10%（即 $\alpha_{HK\text{-}i} < 0.9$）即不分布，轻非关键类似（K 高于轻关键 10%）。
- **Invariant zones（两组夹紧区）**：多组分中上、下夹紧区温度与组成不同（非关键组分在其中被"洗掉"），夹紧区不再骑跨进料板——这是与二元体系的本质区别。
- **Underwood method**：最小回流比的近似群法；先求根 $\phi$（$1 - q = \sum \dfrac{\alpha_i x_{Fi}}{\alpha_i - \phi}$，正确根位于两关键 α 之间），再 $R_{Dm} + 1 = \sum \dfrac{\alpha_i x_{Di}}{\alpha_i - \phi}$。
- **Lewis–Matheson method**：逐板交替使用相平衡（露点/泡点）与物料衡算，自塔顶/塔底向进料板推进并迭代吻合。
- **Gilliland correlation**：由 $N_{\min}$ 与 $R_{Dm}$ 经验内插操作回流下的板数 $N$（仅适用于近恒 α 体系；非理想体系误差大）。
- **Extractive & azeotropic distillation**：加第三组分改 α；萃取精馏（高沸溶剂、如糠醛改变丁二烯/丁烯相对挥发度）vs 恒沸精馏（夹带剂成低沸恒沸物带出，如苯/环己烷破乙醇-水恒沸）。

## Key Concepts
- **Sharp separation**：关键组分取挥发序相邻两个，仅这两个在两产品中显著共存；规定四、五个浓度通常无解，只能指定两个关键指标。
- **Fractional recovery（回收率）**：多组分规格常用"98% LK 回收进馏出液、99% HK 回收进釜液"而非具体摩尔分数——产品组成随进料中非关键组分变化。
- **Reverse fractionation（反常精馏）**：近最小回流时，关键组分浓度剖面出现极大值甚至局部反向——夹紧区之间塔段的作用是清洗非关键组分，不是增浓关键组分。
- **Pseudobinary shortcut**：把两关键当伪二元体系，$\alpha_{LK-HK}$ 代入二元式；$\dfrac{L_{\min}}{F} = \dfrac{(Dx_{DA}/Fx_{FA}) - \alpha_{AB}(Dx_{DB}/Fx_{FB})}{\alpha_{AB} - 1}$，对关键组分占 90%+ 的进料够准、略偏保守。
- **Depropanizer profiles 的物理图像**：K 随温度逐板变化 → 平衡线是逐板移动的直线族；某组分可在上段 K>1 富集、塔顶几板 K<1 后被乙烷"顶掉"，故塔顶板主要富集更轻组分。

## Key Equations
- $K_i = y_{ie}/x_{ie}$；理想体系 $K_i = P_i'/P$；$\alpha_{ij} = K_i/K_j = P_i'/P_j'$
- 泡点：$\sum_{i=1}^{N_c} K_i x_i = 1.0$；露点：$\sum_{i=1}^{N_c} y_i/K_i = 1.0$；归一 $y_i = \dfrac{K_i x_i}{\sum_j K_j x_j}$
- 多组分闪蒸：$\sum_i \dfrac{x_{Fi}}{f(K_i - 1) + 1} = 1.0$
- **Fenske（多组分）**：$N_{\min} = \dfrac{\ln\left[(x_{Di}/x_{Bi})/(x_{Dj}/x_{Bj})\right]}{\ln \bar\alpha_{ij}} - 1$，$\bar\alpha_{ij} = \sqrt[3]{\alpha_{Dij}\alpha_{Fij}\alpha_{Bij}}$
- 伪二元最小液流：$\dfrac{L_{\min}}{F} = \dfrac{(Dx_{DA}/Fx_{FA}) - \alpha_{AB}(Dx_{DB}/Fx_{FB})}{\alpha_{AB} - 1}$
- 夹紧区组分流量（上段）：$y_{\infty i} = \dfrac{D}{V_\infty}\left(\dfrac{x_{Di}}{1 - L_\infty/(V_\infty K_{\infty i})}\right)$；下段：$y_{\infty i} = -\dfrac{B}{\bar V_\infty}\left(\dfrac{x_{Bi}}{\bar L_\infty/(\bar V_\infty \bar K_{\infty i}) - 1}\right)$，各自对产品中组分求和=1、各项须为正
- **Underwood equations**：$1 - q = \sum_i \dfrac{\alpha_i x_{Fi}}{\alpha_i - \phi}$（根 $\phi$ 取两关键 α 之间），$R_{Dm} + 1 = \sum_{i \in D} \dfrac{\alpha_i x_{Di}}{\alpha_i - \phi}$
- 逐板衡算（精馏段）：$y_{2i} V_2 = L_1 x_{1i} + D x_{Di}$

## Reference Tables
| 方法 | 类型 | 需要输入 | 适用/局限 |
|---|---|---|---|
| 泡点/露点试差 | 相平衡 | 组成、P、K(T) | 一切逐板计算的基本单元 |
| 多组分闪蒸式 | 群法 | $x_F$、f、K | 试差定闪蒸温度 |
| Fenske | 群法 | 产品组成、$\bar\alpha$ | 最小板数；α 近似恒定 |
| Underwood | 群法 | $x_F$、$x_D$、q、α | $R_{Dm}$；根须取两关键之间 |
| Gilliland | 经验关联 | $N_{\min}$、$R_{Dm}$、$R_D$ | 初估 N；非理想体系误差大 |
| Lewis–Matheson | 逐板 | 产品全组成、K 表 | 精确；收敛难时用矩阵法 |

## Worked Example
**Ex. 22.3+22.5（C6/C7/C8 三元，模板链）**：33/37/30 mol% 己烷/庚烷/辛烷，1.2 atm、60% 汽化进料；定己烷=LK、庚烷=HK（辛烷=HNK 归釜液）。塔顶 $x_{DH}=0.01$、釜液 $x_{BL}=0.01$ → 物料衡算 D=32.65 mol、B=67.35 mol，辛烷全进釜液。Fenske：$\alpha_{LK-HK}=2.21$，$N_{\min} = \ln[(0.99/0.01)/(0.01/0.544)]/\ln 2.21 - 1 = 9.8$（+再沸器）；用顶/中/底三点 α 立方根均值 2.29 得 $N_{\min}=9.4$；再用 HK-HNK 对校核 $x_{D3} = 2.4\times10^{-6}$，证实"辛烷不进馏出液"假设成立。Ex. 22.5 取 $R_D = 1.5R_{Dm}$：Underwood 求得 $\phi=1.45$、$R_{Dm}=1.86$ → 横坐标 0.245 查 Gilliland 得 N≈18.3 块（或备选关联 $N/N_{\min}=1.8$ → 18.7 块）。（Ex. 22.1/22.2 同一物系演示泡点 97°C、露点 110.5°C 与 60% 闪蒸 T=105°C、预热 167°C。Ex. 22.4 四元系展示 Underwood 全流程与上下夹紧区 81.1°C/83.3°C 的求法。）

## Anti-patterns
- **取根 $\phi$ 不在两关键 α 之间**：Eq. 22.29 有多个数学根，只有位于 $\alpha_{LK}$ 与 $\alpha_{HK}$ 之间的根有物理意义；关键间还有中间组分时须联立 22.29/22.30 定根。
- **假设任意两个组分为关键即方便**：非相邻关键（sharp separation 被破坏）会让中间组分在两产品中大量共现，群法全部失效或大幅失真。
- **把 Underwood/伪二元 $R_{Dm}$ 用到非理想体系而不校核**：Gilliland 与这些群法都基于近恒 α；像甲醇-水（α 从 7.5 变到 2.7）这类体系 N/Nmin 远大于理想关联值，因平衡线上段与操作线近平行。
- **期待两组分夹紧区重合于进料板**：多组分最小回流时上下夹紧区温度不同（Ex. 22.4 中差 2.2°C），精确 $R_{Dm}$ 需夹紧区之间逐板计算。
- **用塔顶几块板去追求主产品纯度**：顶板的作用常是除更轻组分（如乙烷）；若要高纯丙烷应另设脱乙烷塔或侧线，而不是简单删掉这几块板。
- **高压下仍用 $K_i = P_i'/P$**：高压压缩性效应使 K 不再严格反比于总压，需查 K 图或状态方程。

## Key Takeaways
1. 多组分设计的规格语言是"两个关键组分 + 回收率"，不是完整产品组成——后者随进料波动，不可先验指定。
2. 初步设计链：物料衡算（假设 sharp separation）→ Fenske $N_{\min}$ → Underwood $R_{Dm}$ → Gilliland N → 乘板效率；严格解交给逐板/矩阵程序。
3. K 因子是温度的强函数而 α 近似不变，所以所有群法都建立在恒相对挥发度上；$\bar\alpha$ 用顶、进料、底三点几何平均。
4. 非关键组分的"分布/不分布"判据：与相邻关键相比相对挥发度差 10% 以上的几乎完全单边分布；介于其间的组分必须显式计算分布。
5. 多组分夹紧区不重合且含"洗脱非关键"功能，导致关键组分剖面极大值与反常精馏——近 $R_{Dm}$ 操作的塔内观察到的这类现象是原理性而非故障。
6. 萃取精馏用高沸溶剂降低"与溶剂相似"组分的活度系数（糠醛-丁二烯）；恒沸精馏用夹带剂形成低沸恒沸物从塔顶带出（苯-乙醇-水三元恒沸+分层回流），两者都要配溶剂回收塔。

## Connects To
- **Ch. 21**：Fenske/最小回流/夹紧区概念的直接推广；q 值与焓衡算沿用。
- **Ch. 20**：露点/泡点试差是闪蒸与逐板计算共享的平衡工具。
- **Ch. 19**：同属"相平衡 + 衡算"框架，但那里是汽液两元、这里是多组分。
- **Ch. 23**：液液萃取与萃取精馏共享"溶剂改变分配"思想。
- **Ch. 12/13**：非理想体系活度系数与汽液平衡的热力学基础。
