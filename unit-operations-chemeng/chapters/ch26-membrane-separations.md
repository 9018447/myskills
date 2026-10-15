# Chapter 26: Membrane Separation Processes

## Core Idea
膜分离通过半透膜的溶解度差与扩散速率差实现组分分离：气体分离由渗透系数 Q=D·S 与压力比 R=P₂/P₁ 共同决定局部渗透组成；液相过程（透析、膜萃取、渗透汽化、反渗透）则分别以浓度梯度、活度梯度或 (ΔP−Δπ) 为推动力。

## Frameworks Introduced
- **Knudsen 扩散（多孔膜）**：孔径≪平均自由程时气体独立扩散，D_A = 9700·r·(T/M_A)^0.5——"Use porous-membrane analysis when separation is due to molecular-weight differences (e.g., UF₆ 同位素分离，需千级级联)。"
- **Solution-diffusion 机制（致密聚合物膜）**：气体在高压侧溶解、膜内扩散、低压侧脱附；J_A = q_A(p_{A1}−p_{A2})/z = Q_A(p_{A1}−p_{A2})。
- **膜选择性 α（ideal separation factor）**：α = Q_A/Q_B = (D_A S_A)/(D_B S_B)，由扩散比与溶解度比共同构成；α≥4 才有像样的单级分离。
- **局部渗透组成方程**：y' 由 α、压力比 R=P₂/P₁ 与 x 决定；R→0 得平衡极限 y'=αx/[1+(α−1)x]；分压平衡给出上限 y'_max=x/R。
- **Stage cut（级切割率）**：渗透流/进料流之比，与纯度构成产率-纯度权衡的核心坐标。
- **渗透汽化（pervaporation）修正框架**：以 R_A=P₂/(γ_A P'_A)、修正选择性 α'=Q_Aγ_A P'_A/(Q_Bγ_B P'_B) 替代气体分离的 R 与 α；扩散系数随浓度指数变化 D=D₀e^{βc} 导致强非线性。
- **透析三阻力模型**：1/K = 1/k₁ + 1/k_m + 1/k₂，膜内受阻扩散按 Renkin 式计入分子/孔径比 λ。
- **膜萃取（membrane extractor）**：以非浸润多孔膜固定相界面、无液泛无乳化；总阻力按分配系数 m 决定膜内充哪一相。
- **反渗透（reverse osmosis）**：水通量 ∝ (ΔP−Δπ)/z，盐通量 ∝ Δc_s/z——升压同时提高通量与截留率。
- **浓差极化（concentration polarization）**：Γ=J_w·f/k_c 定量表面/主体浓度差；Γ<0.1 可忽略。

## Key Concepts
- **Permeability Q / permeability coefficient q**：单位压差（梯度）的通量；q=D·S=Q·z，Barrer=10⁻¹⁰ cm³(STP)·cm/(cm²·s·cmHg)；商用膜常给 Q，须核对单位。
- **Asymmetric membrane**：0.1–1 μm 致密皮层 + 多孔支撑（总厚 50–200 μm），Loeb–Sourirajan 法制得，是膜过程工业化的关键。
- **Pinholes / coating**：皮层针孔使渗透流短路、选择性骤降；用高渗透非选择性聚合物封孔是标准对策。
- **Stage cut**：进料中成为渗透产物的分数；低 stage cut 得高纯渗透物，高 stage cut 得高纯渗余物（如 95–99% N₂）。
- **Counterflow vs crossflow/parallel**：并流与错流性能相近且取决于进料侧分压；制高纯渗余物（近纯 N₂）必须逆流。
- **Osmotic pressure π**：使两侧溶剂活度相等所需的压力；反渗透操作压通常高于 π 约 20–50 atm。
- **Concentration polarization**：被膜截留的溶质在膜面积累（表面浓度>主体），降低水通量与截留率。
- **Hindered diffusion (λ)**：分子直径/孔径比 λ 增大时 D_e 急剧下降（λ=0.1 → 0.164D_v；λ=0.5 → 0.022D_v），是透析选择性之源。
- **Electrodialysis**：离子选择性膜+电位梯度迁移离子，交替阴/阳膜室实现盐水淡化或浓缩（定期倒极防垢）。
- **Modified pressure ratio R_A, R_B**：渗透汽化中把活度系数与蒸气压并入压力比，使气体分离方程形式可复用。

## Key Equations
- Knudsen 扩散系数：$D_A = 9700\,r\,(T/M_A)^{0.5}$（r=平均孔半径 cm，T=K；D_A 单位 cm²/s）
- 有效扩散系数：$D_{eA}=\dfrac{D_A\varepsilon}{\tau}\cong\dfrac{1}{4}D_A$（ε=孔隙率，τ=曲折因子）
- 致密膜通量：$J_A=\dfrac{D_A S_A(p_{A1}-p_{A2})}{z}=Q_A(p_{A1}-p_{A2})$（D_A=膜内扩散系数，S_A=溶解度系数=1/亨利系数，z=膜厚）
- 局部渗透组成：$y'=\dfrac{x-Ry}{x-Ry+\dfrac{1-x-R+Ry}{\alpha}}$；闭端处 y=y' 解二次式 $(\alpha-1)(y')^2+\Big[1-\alpha-\dfrac{1}{R}-\dfrac{x(\alpha-1)}{R}\Big]y'+\dfrac{\alpha x}{R}=0$
- 极限与上限：$R\to0:\ y'=\dfrac{\alpha x}{1+(\alpha-1)x}$；分压约束 $y'_{max}=\dfrac{x}{R}$
- 膜面积估算：$A\cong\dfrac{V_{out}y_{out}}{Q_A(P_1x-P_2y)_{ave}}$（V y=渗透组分流量）
- 逆流分离器逐步法衡算：$L_k(x_k-x_j)=\Delta V_j(y_j'-x_j)$
- 透析总阻力：$\dfrac{1}{K_A}=\dfrac{1}{k_{1A}}+\dfrac{1}{k_{mA}}+\dfrac{1}{k_{2A}}$，$k_m=D_e/z$
- Renkin 受阻扩散：$D_e=\dfrac{D_v\varepsilon}{\tau}(1-\lambda)^2(1-2.104\lambda+2.09\lambda^2-0.95\lambda^3)$（λ=分子/孔径比）
- 膜萃取（疏水膜、水相内走管）：$\dfrac{1}{K_w}=\dfrac{1}{k_w}+\dfrac{1}{m}\Big(\dfrac{1}{k_o}+\dfrac{z}{D_{e,o}}\Big)$（m=有机/水分配系数；m≫1 时水相控制）
- 渗透汽化通量：$J_A=Q_A(\gamma_A x_A P_A'-y_A P_2)$；$R_A=\dfrac{P_2}{\gamma_A P_A'}$，$\alpha'=\dfrac{Q_A\gamma_A P_A'}{Q_B\gamma_B P_B'}$
- 浓度依赖扩散：$D=D_0e^{\beta c}$，稳态 $J=\dfrac{D_0}{\beta z}(e^{\beta c_1}-e^{\beta c_2})$
- 反渗透水/盐通量：$J_w=\dfrac{c_wD_wv_w}{RT}\cdot\dfrac{\Delta P-\Delta\pi}{z}$；$J_s=D_sS_s\dfrac{\Delta c_s}{z}$
- 极化因子：$\Gamma=\dfrac{c_{si}-c_s}{c_s}=\dfrac{J_w f}{k_c}$（f=截留率）
- 中空纤维内压降（流量渐增的层流）：$\Delta p_s=\dfrac{128J_w\mu L^2}{2D^3}$，恰为按出口速度恒定计算值的一半

## Reference Tables
- **聚合物内扩散系数（25°C，×10⁹ cm²/s）**：PET（O₂ 3.6/N₂ 1.4）；HDPE 0.964（170/93）；LDPE 0.914（460/320）；天然橡胶（1580/1110）——结晶/玻璃态≫橡胶态差异可达三个数量级。
- **膜选择性实例**：硅橡胶 CO₂/H₂=4.9、CO₂/O₂=5.4（高渗低选）；Kapton CO₂/H₂=0.18（渗低选反转）；聚砜 O₂/N₂≈5、H₂O/N₂≈280；聚二甲基硅氧烷（橡胶态）对 C₃H₆/N₂=10、C₄H₁₀/N₂=30、甲苯/N₂=80。
- **工业气体应用**：氨厂尾气 H₂ 回收（59%→86%，回收 93%，α(H₂/CH₄) 10–100）；天然气脱 CO₂（α 20–30，Kapton>60）；He/CH₄ α=190（0.82% He 单级回收一半）。
- **反渗透膜通量**：醋酸纤维素不对称膜 10–20 gal/ft²·day；芳香聚酰胺中空纤维 1–3 gal/ft²·day；螺旋卷式比表面积比中空纤维低一个量级但渗侧压降可忽略。
- **渗透汽化典型工况**：单级仅移除进料 2–5%；乙醇脱水商品机组≤12 级、级间再热，产品水<100 ppm。

## Worked Example
**Ex 26.1（聚砜中空纤维空分）**：20 L/min 空气→3.1 L/min 40% O₂ 渗透+17% O₂ 渗余；用两端平均 Δp 反求 Q_O₂=0.741、Q_N₂=0.150 L/min·m²·atm，α=4.94；升压至 80 psi（R=0.155）渗透氧升至 45%；R→0 的极限为 57%——说明单级渗透组成受压力比钳制，纯氧靠膜不经济。
**Ex 26.2（H₂/CH₄ α=100、R=0.5）**：从渗余端步进积分，96% H₂ 时回收率 62.5%、stage cut 45.6%；渗透压降到 180 psi（R=0.3）回收率升至 88%——低压渗透侧是提高回收的第一杠杆。
**Ex 26.3（渗透汽化乙醇脱水）**：90 wt% 乙醇、P₂=15 mmHg，由 Margules 式算 γ 得 Q_H₂O=152、Q_EtOH=0.87 gmol/m²·h·atm（α'≈151）；P₂ 升到 30 mmHg 仅 9.6% 酒精渗透，但 99.9% 乙醇时局部渗透物仅 1 wt% 水——纯度越高越要把 P₂ 压到个位数 mmHg。
**Ex 26.4（极化判断）**：10 gal/ft²·day、97% 截留、垂直冲刷流速 0.5 cm/s → Sh=12.6、k_c=6.7×10⁻³ cm/s，Γ=0.068<0.1，极化可忽略；但要防布流不均的死区。
**Ex 26.5（纤维内压降）**：3 m 纤维、内径 200 μm，出口流速 0.425 m/s，Δp_s=5.0 atm（=恒速近似的一半）；两端开口则等效长度减半、压降降为 1/4。

## Anti-patterns
- **用总压差算通量**：各组分管各自分压差；总通量仅在 R→0 时才正比于总压差（Permea 宣称升压增氮产率 2.3 倍而非 2 倍即此因）。
- **忽略 y'_max=x/R 的物理上限**：再高选择性也突破不了分压平衡；x=0.4、R=0.5 时渗透物最高 80%。
- **用纯气渗透数据外推高 CO₂ 工况**：CO₂ 塑化效应增大所有组分有效扩散系数，实际选择性低于纯气数据。
- **渗透汽化按线性浓度梯度设计**：膜溶胀使 D 变化 10–100 倍，降低 c₂（更低 P₂）远不如升高 c₁（进料浓度）有效。
- **膜萃取选错浸润相**：疏水膜孔应充满有机相；若分配系数 m≪1（溶质亲水）而选疏水膜，膜阻被 1/m 放大——应改亲水膜让孔充水。
- **中空纤维只按出口流速校核压降**：渐增流量下 Δp∝L²，纤维过长压降呈平方恶化；闭式纤维已自动减半，两端开口再减 3/4。
- **低负荷时全开并联机组**：单模块流速过低→渗透回收过大→进料侧可能凝液；应轮停部分模块保持单机流量。

## Key Takeaways
- 膜气体分离的设计三角：α（膜）、R=P₂/P₁（流程）、stage cut（操作点）；单级产品纯度 = min[α 极限, x/R 分压极限]。
- 工业定位：膜做"富集不提纯"——95–99% N₂、86% H₂、40–50% O₂ 最经济；更高纯度交给 PSA/低温精馏或催化脱氧组合。
- 渗透压侧降压（真空或低压渗透）通常比升进料压更有效——驱动力的收益集中在快组分。
- 反渗透核心式 J_w∝(ΔP−Δπ)：盐截留率随压力升高（盐通量不依赖 ΔP）；海水一级产饮用水需>99% 截留。
- 极化因子 Γ=J_w f/k_c 是通用判据：Γ<0.1 免议；Γ 大不是坏事，是强化传质（提速、改流道）的机会信号。
- 渗透汽化定位在共沸区附近：精馏到 90–95% 乙醇，膜收尾到 99.9%；别用膜做全程分离。
- 液相三大过程选择性来源不同：透析靠 hindered diffusion（λ）、膜萃取靠分配系数 m 与浸润选择、渗透汽化靠聚合物溶胀选择性。

## Connects To
- Ch 17 的扩散与传质关联（Sh-Re-Sc、受阻扩散）支撑全部阻力计算；Ch 5 的 Hagen–Poiseuille 式给出纤维内压降。
- Ch 21 精馏（共沸、Fenske）与本章渗透汽化构成乙醇脱水的组合流程；连续膜柱的回流思想即精馏回流。
- Ch 29 将超滤作为过滤特例处理，与本章反渗透/透析同属压力驱动膜族谱。
- Ch 25 的 PSA 与膜空分互为替代/组合（膜预富集+PSA 提纯）。
