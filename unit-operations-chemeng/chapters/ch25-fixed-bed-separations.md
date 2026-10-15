# Chapter 25: Fixed-Bed Separations

## Core Idea
固定床吸附、离子交换与色谱共用同一套核心逻辑：多孔固体选择性保留流体中某些组分，床层内形成随时间下移的传质区（mass-transfer zone），出口浓度曲线（breakthrough curve）与"未用床层长度 LUB"是设计与放大的中心工具。

## Frameworks Introduced
- **吸附等温线分类**：线性 / favorable（凸向上，如 Langmuir、Freundlich）/ unfavorable（凹向上，罕见）——"Use favorable-isotherm analysis when designing purification beds; use linear-isotherm analogy (Furnas heat-wave) when regeneration or weak adsorption dominates."
- **Langmuir 等温线**：W = W_max[Kc/(1+Kc)]，均匀表面假设（虽不严格成立）但对弱吸附气体可用；多组分时在分母加 K_i·c_i 项。
- **Freundlich 方程**：W = bc^m（m<1），强 favorable 体系（尤其液相吸附）的经验拟合更好。
- **推广吸附关联（Grant–Manes / adsorption potential）**：W 仅取决于 (T/V)·log(f_s/f)，T=吸附温度(K)，V=正常沸点液体摩尔体积，f_s=饱和液体逸度，f=蒸气逸度；同类化合物落在同一曲线上。
- **穿透曲线物料衡算 + LUB 放大原理**：favorable 等温线下传质区形状恒定，LUB 不随床长改变，可从小柱直接放大。
- **不可逆吸附解**：床内浓度分布指数衰减，穿透曲线 ln(c/c₀) = N(τ−1) − 1。
- **线性等温线 ↔ 固定床传热波动类比（Furnas）**：吸附方程与填充床蓄热式换热器方程同构，N ↔ N_H。
- **离子交换选择平衡**：浓度基平衡常数 K' 表征树脂对不同反离子的选择性；二价离子在稀溶液中被强烈优先。
- **色谱保留理论**：GLC 保留时间由分配系数决定；van Deemter 方程 H = A + B/u + Cu 描述板高与气速关系。
- **连续逆流 / 模拟移动床（Sorbex）**：以旋转阀周期切换进/出口位置，模拟固体逆流，用于二甲苯异构体等大规模分离。

## Key Concepts
- **Adsorbate / adsorbent**：被吸附组分 / 多孔吸附固体；内表面积常达 500–1000 m²/g，吸附主要发生在孔壁。
- **Mass-transfer zone（MTZ）**：床内浓度从 c₀ 降到≈0 的 S 形区域，边界常取 c/c₀=0.95–0.05；随时间向床出口移动。
- **Breakthrough curve / break point**：出口 c/c₀ 随时间曲线；break point 常取 c/c₀=0.05 或 0.10，到达即切换/再生。
- **LUB（length of unused bed）**：穿透时床层未被利用部分的等效长度，favorable 体系下与床长无关，是放大核心量。
- **PSA（pressure-swing adsorption）**：高压吸附、低压（1 atm 或真空）再生的主体分离工艺（空分制氧/氮、提氢）；吸附时间短，须计入床内气体滞留量。
- **Kinetic separation**：利用扩散速率差而非平衡差的分离（碳分子筛分离 O₂/N₂，D_e(O₂)≈100×D_e(N₂)）。
- **Surface diffusion**：吸附分子沿孔壁扩散，常主导总通量（水-硅胶、烃-活性炭），使内阻远小于气相孔扩散预测值。
- **Ion-exchange resin capacity**：可交换基团数/干树脂质量（meq/g H⁺）；苯乙烯-二乙烯苯磺酸树脂理论容量≈5.4 meq/g，床容量≈2.5 eq/L。
- **Swelling**：树脂在水溶胀程度由交联度、固定电荷浓度与外液电解质浓度决定；溶胀提高扩散速率但降低单位体积容量。
- **Retention time / partition coefficient K_A**：色谱组分脉冲中点流出时间；K_A≫ε 时 t*∝K_A。
- **HETP / number of plates N**：理论板当量高度与板数，N=16(t*/Δt)²，表征柱效与峰展宽。

## Key Equations
- 理想穿透时间（物料衡算）：$t^* = \dfrac{L\rho_b(W_{sat}-W_0)}{u_0 c_0}$
  （L=床长，ρ_b=床层堆密度，W_sat/W_0=平衡/初始吸附量，u_0=表观流速，c_0=进料浓度）
- 穿透点时间与 LUB：$t_b = t^*\left(1-\dfrac{LUB}{L}\right)$
- 床内溶质衡算（忽略流体积累项）：$\varepsilon\dfrac{\partial c}{\partial t}+(1-\varepsilon)\rho_p\dfrac{\partial W}{\partial t} = -u_0\dfrac{\partial c}{\partial L}$
- 总传质速率：$\rho_p(1-\varepsilon)\dfrac{\partial W}{\partial t}=K_c a(c-c^*)$（c* 与固体平均浓度 W 平衡的流体浓度；a=6(1−ε)/D_p）
- 总传质系数分解：$\dfrac{1}{K_c}\approx\dfrac{1}{k_{c,ext}}+\dfrac{D_p}{10D_e}$（D_e=有效扩散系数；内阻按扩散距离 D_p/10 近似）
- 无量纲参数：$\tau=\dfrac{u_0c_0(t-L\varepsilon/u_0)}{\rho_p(1-\varepsilon)L(W_{sat}-W_0)}=t/t^*$，$N=\dfrac{K_c a L}{u_0}$
- 不可逆吸附穿透：$\ln\dfrac{c}{c_0}=N(\tau-1)-1$；复合阻力 $\dfrac{1}{N}=\dfrac{1}{N_f}+\dfrac{1}{N_p}$
- 传质区移动速度：$v_z=\dfrac{u_0 c_0}{\rho_p(1-\varepsilon)W_{sat}}$
- 离子交换平衡（一价）：$\mathrm{A^+ + NaR \rightleftharpoons AR + Na^+}$，$K'=\dfrac{c_{Na^+}c_{AR}}{c_{A^+}c_{NaR}}$；二价 $K'=\dfrac{(c_{Na^+})^2c_{BR_2}}{c_{B^{2+}}(c_{NaR})^2}$（稀溶液中单价离子浓度平方项使交换几乎完全）
- 离子交换速率：$r=K_c a(c-c^*)$，$\dfrac{1}{K_c}=\dfrac{1}{k_{c,ext}}+\dfrac{1}{mk_{c,int}}$（m=内/外浓度比，稀溶液 m 很大→外膜控制）
- GLC 保留时间：$t_A^*=\dfrac{L(\varepsilon+K_A)}{u_0}$；保留比 $\dfrac{t_A^*}{t_B^*}=\dfrac{K_A}{K_B}=\dfrac{\gamma_B P_B'}{\gamma_A P_A'}$
- 板数与分离：$N=16\left(\dfrac{t^*}{\Delta t}\right)^2$；最少板数 $N_{min}=4\left(\dfrac{1+\alpha}{\alpha-1}\right)^2$（α=保留时间比）
- van Deemter：$H=A+\dfrac{B}{u}+Cu$（A=流道不均匀展宽；B/u=轴向分子扩散；Cu=两相间传质）

## Reference Tables
- **等温线形状对比**：线性（过原点）→ favorable（低浓度高负载；Langmuir/Freundlich）→ 极限=不可逆吸附（脱附需高温）→ unfavorable（负载低、MTZ 极长，罕见）。
- **干燥剂对比（水/空气）**：硅胶近线性至 50% RH、极限容量约大一倍（毛细凝聚填孔）；分子筛吸附最强、几乎不可逆、可制 −75°C 露点；除分子筛外容量随温度升高显著下降。
- **离子交换选择系数 K'（8% DVB，Perry 7e）**：阳离子 Li⁺ 1.00（基准）< H⁺ 1.27 < Na⁺ 1.98 < NH₄⁺ 2.55 < K⁺ 2.90 < Mg²⁺ 3.29 < Cu²⁺ 3.47 < Ca²⁺ 5.16 < Ba²⁺ 11.5；阴离子 Cl⁻ 1.0（基准），I⁻ 8.7 > NO₃⁻ 3.8 > Br⁻ 2.8 > CN⁻ 1.6 > HCO₃⁻ 0.3 > OH⁻ 0.05–0.07。
- **设计典型值**：气相炭床深 0.3–1.2 m，u₀=0.15–0.45 m/s，循环 2–24 h；液相 20×50 目炭，u₀≈0.3 cm/s（≈4 gal/min·ft²），LUB 可达 10–20 cm；蒸汽再生耗汽 0.2–0.4 lb steam/lb carbon（130–150°C）。

## Worked Example
**Ex 25.2–25.3（正丁醇/炭床穿透与传质系数反演）**：8 cm 与 16 cm 床的穿透数据积分得 W_sat≈0.291 g/g；c/c₀=0.05 时利用率分别为 0.50 与 0.74，LUB≈4.0 与 4.2 cm（恒定，验证放大原理）；预测 32 cm 床 t_b=16.7 h。再由 c/c₀=0.05 处 τ−1=−0.505 反求 N≈3.17、K_c a≈23 s⁻¹；与外膜预测 k_c a=52.5 s⁻¹ 比较得内阻≈一半；实测 k_c,int 比气相孔扩散上限大一个数量级 → 表面扩散主导。
**Ex 25.4（MEK 吸附器设计）**：用 (T/V)log(f_s/f)=7.11 查图得 W_sat=0.18 g/g；再生停留在 W₀=W_sat/3 → 工作容量 0.12 lb/lb；选 u₀=1 ft/s 得 10×27 ft 矩形床、L=3–4 ft，t_b≈11–16 h，核算 ΔP≈3.3 in H₂O/ft < 12 in 限值。
**Ex 25.5（TCE 水处理）**：Ambersorb 563，W_sat=0.2 lb/lb、蒸汽再生后 W₀=0.03；L=2 ft、u₀=36.1 ft/h → t*=4160 h，LUB=0.6 ft → t_b≈2900 h，处理量 5.2×10⁴ 倍床体积。
**Ex 25.6（Cu²⁺/Na⁺ 选择性）**：K'=3.47/1.98=1.75，结合树脂当量守恒解二次方程；总当量浓度从 0.5 N 降到 0.01 N 时平衡曲线变得强 favorable——解释稀溶液软化/除重金属的完全性。
**Ex 25.7（离子交换柱放大）**：小柱 LUB=10.4 cm → 1.5 m 工业柱利用率 0.931、t_b=27.4 h；降速使 N 增大 √2、LUB 缩短；2 M NaCl 再生用 2 倍最小量仅需 15 min。

## Anti-patterns
- **忽略湿度对炭床的影响**：RH>80% 时有机蒸气容量可降 50–70%（RH<30% 几乎无影响）；适度升温 10–20°C 反而有利。
- **用高浓度小试直接外推**：浓度差过大改变传质系数并引入热效应；吸附放热可使大床升温 10–50°C，小床散热而大床近绝热——必须用大直径中试或含热衡算的模型。
- **盲目缩短床深**：浅床（<0.3 m）压降低、投资小，但穿透快、利用率低、再生更频繁，总能耗更高。
- **把 LUB 当常数外推到不同流速/粒径**：LUB 恒定仅在"同颗粒、同表观流速"下成立；k_c a ∝ D_p^(−1.5~−2.0)，改粒径会大幅改变穿透陡度。
- **假设再生=完全再生**：完全再生常不经济，设计必须按残余 W₀>0 的工作容量计算；好在再生后床底最"干净"，下一周期仍能高去除率。
- **放大色谱柱时只放大直径**：不均匀布流与壁效应使 HETP 增大数倍；需窄粒径分布、振动装柱、定期加挡板。

## Key Takeaways
- 穿透曲线是吸附/离子交换设计的通用"数据语言"：由积分面积得 W_sat 与利用率，由 LUB 恒定性外推任意床长的 t_b。
- favorable 等温线→MTZ 恒宽→床越长利用率越高；线性等温线→MTZ 随 L^1/2 增长→长床也难高产率（N=100 才利用 80%）。
- k_c a 随粒径约 −1.5~−2.0 次幂变化：减粒径是最有效的陡化穿透手段（压降允许时）。
- 容量估计首选 Grant–Manes 关联 (T/V)log(f_s/f)，多组分与湿气干扰须逐项修正。
- 离子交换中二价离子在稀溶液占绝对优势（浓度平方项），浓再生液则把平衡拉回——这是再生省时的根源。
- 色谱分离度由 α 与板数共同决定，N∝[(1+α)/(α−1)]²：α<1.1 时板数暴涨，不如精馏（对照 Fenske）。
- 大规模连续化路线：移动床（水处理炭塔）→ 模拟移动床 Sorbex（异构体分离主力）。

## Connects To
- Ch 17（相间传质系数、颗粒内扩散、Sh-Re-Sc 关联）提供本章全部速率工具。
- Ch 18（气体吸收）的 HTU/NTU 概念对应 N=K_c aL/u₀；本章 H_Og≈2.5 cm 远小于吸收塔的 30–60 cm。
- Ch 7（填充床流动）的 Ergun 式用于吸附器 ΔP 核算。
- Ch 21（精馏 Fenske 方程）用于色谱-精馏板数对比；Sorbex 是"分离最难共沸/近沸物"时精馏的替代路线。
- Ch 28–29 的颗粒性质（堆密度 ρ_b、粒径分布）直接进入本章设计方程。
