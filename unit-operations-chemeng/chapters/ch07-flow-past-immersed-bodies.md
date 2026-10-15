# Chapter 7: Flow past Immersed Bodies

## Core Idea
把"流体对固体的作用"量化为阻力系数 $C_D$–颗粒雷诺数 $\mathrm{Re}_p$ 关系，并沿三条主线展开：单一颗粒绕流与沉降、颗粒填充床的压降（Kozeny–Carman → Burke–Plummer → Ergun）、以及床层被流体托起后的流化行为。

## Frameworks Introduced
- **Drag coefficient（曳力系数）**：$C_D\equiv(F_D/A_p)/(\rho u_0^2/2)$，即单位投影面积阻力对速度头密度积之比；给定形状时 $C_D=\phi(\mathrm{Re}_p)$，是 f 在绕流问题中的对应物。
- **Stokes' law（斯托克斯定律）**：爬流（creeping flow, $\mathrm{Re}_p<1$）下的理论曳力 $F_D=3\pi\mu u_0D_p$，即 $C_D=24/\mathrm{Re}_p$。用于小颗粒沉降、气溶胶、高黏液体中的大颗粒。
- **Drag crisis（阻力危机）**：$\mathrm{Re}_p\approx3\times10^5$ 时球前边界层转捩为湍流、分离点后移、尾迹收缩，$C_D$ 从 0.45 骤降至 0.10；来流湍流度越强，临界 Re 越低。
- **Stagnation point / stagnation pressure（驻点与驻点压力）**：物面前缘流速为零处 $p_s-p_0=\rho u_0^2/2$；Ma>0.4 需用等熵滞止压力修正（二项式展开系数 $1+\mathrm{Ma}^2/4+\cdots$）。
- **Sphericity（球形度 $\Phi_s$）**：与颗粒同名义直径的球比表面积除以颗粒比表面积，$\Phi_s=(6/D_p)/(s_p/v_p)$；非球形度通过它进入所有床层压降公式。球/立方体=1，砂 0.65–0.95，云母片 0.28。
- **Channel model of packed bed（填充床沟道模型）**：把床层等效为均匀直圆管束，得等效沟道直径 $D_{eq}=\frac{2}{3}\Phi_sD_p\varepsilon/(1-\varepsilon)$（ε=0.4 时约为粒径一半）；叠加黏性项与动能项得 **Ergun equation**（全范围）。
- **Terminal velocity & settling criterion K（沉降终端速度与判据 K）**：力平衡三力（外力−浮力−曳力）给出 $u_t$；无因次判据 $K=D_p[g\rho(\rho_p-\rho)/\mu^2]^{1/3}$ 决定用哪个公式。
- **Fluidization（流化）**：压降恰好托起床重 $\Delta p=g(1-\varepsilon_M)(\rho_p-\rho)L$ 时的速度为最小流化速度 $\bar V_{0M}$（由 Ergun 方程解出）；此后 Δp 恒定、床层膨胀。
- **Particulate vs bubbling fluidization（散式 vs 聚式流化）**：液体流化床均匀膨胀（particulate）；气体流化床大部分气体以气泡通过（bubbling），气泡几乎不含固体，两相理论描述。

## Key Concepts
- **Wall drag vs form drag（摩擦阻力与形体阻力）**：壁面剪应力沿流向分量之和为 wall drag；压力沿流向分量之和为 form drag（尾迹涡旋耗能所致）。势流中两者积分皆为零。
- **Wake & vortex street（尾迹与涡街）**：$\mathrm{Re}_p\approx20$ 出现回流区，100 时占半球，200–300 起涡规则脱落成涡街（电线风鸣的成因，也是涡街流量计原理）。
- **Bluff body（钝体）**：如垂直于流动的圆盘——分离后流体不回流，尾迹不随边界层转捩收缩，故 $C_D$ 无骤降（Re>2000 时约 1.0）。
- **Superficial velocity（表观/空塔速度 $\bar V_0$）**：按空床截面计算的流速；床内真实平均流速 $\bar V=\bar V_0/\varepsilon$。床层方程全部用 $\bar V_0$ 表达。
- **Darcy's law（达西定律）**：层流渗流的极限形式——流量正比于压降、反比于黏度（Kozeny–Carman 的重述）。
- **Free vs hindered settling（自由沉降与干涉沉降）**：颗粒相距远、不受壁与邻粒影响为 free；浓度高时梯度场与上流置换液体使沉降变慢：$u_s=u_t\varepsilon^n$，n 从 4.6（Stokes 区）到 2.5（Newton 区）。
- **Brownian movement（布朗运动）**：分子碰撞引起的随机运动；粒径 2–3 μm 起可感，≤0.1 μm 压倒重力，沉降不再发生（离心可部分克服）。
- **Minimum fluidization velocity（最小流化速度 $\bar V_{0M}$）**：Ergun 方程与床重平衡的联立解；细粒层流极限 $\propto D_p^2$，粗粒极限 $\propto\sqrt{D_p}$。测量时从流化态缓降后再升速，取 B 点。
- **Slugging（腾涌/节涌）**：小直径深床中气泡长大充满全截面、气固交替上行，压降波动大，通常应避免。

## Key Equations
- 曳力定义与颗粒雷诺数：
  $$C_D\equiv\frac{F_D/A_p}{\rho u_0^2/2};\qquad \mathrm{Re}_p\equiv\frac{D_pG_0}{\mu}=\frac{D_pu_0\rho}{\mu}$$
  （$F_D$：总阻力；$A_p$：迎风投影面积；$u_0$：来流速度）
- Stokes 区（$\mathrm{Re}_p<1$）：
  $$F_D=3\pi\mu u_0D_p,\quad C_D=\frac{24}{\mathrm{Re}_p},\quad u_t=\frac{gD_p^2(\rho_p-\rho)}{18\mu}$$
- Newton 区（$10^3<\mathrm{Re}_p<2\times10^5$）：
  $$C_D=0.44,\qquad u_t=1.75\sqrt{\frac{gD_p(\rho_p-\rho)}{\rho}}$$
  （$u_t$：终端沉降速度；$\rho_p,\rho$：颗粒与流体密度）
- 沉降区判据：
  $$K=D_p\left[\frac{g\rho(\rho_p-\rho)}{\mu^2}\right]^{1/3}:\quad K<2.6\ \text{Stokes};\ 2.6\text{–}68.9\ \text{过渡区试差};\ 68.9\text{–}2360\ \text{Newton 区}$$
- 一般球体终端速度（任意区，配 $C_D$ 试差）：
  $$u_t=\sqrt{\frac{4gD_p(\rho_p-\rho)}{3C_D\rho}}$$
- 球形度与床层等效直径：
  $$\Phi_s=\frac{6/D_p}{s_p/v_p};\qquad D_{eq}=\frac{2}{3}\Phi_sD_p\frac{\varepsilon}{1-\varepsilon}$$
- Kozeny–Carman（层流，$\mathrm{Re}_p\lesssim1$）：
  $$\frac{\Delta p}{L}=\frac{150\bar V_0\mu}{\Phi_s^2D_p^2}\frac{(1-\varepsilon)^2}{\varepsilon^3}$$
- Burke–Plummer（湍流，$\mathrm{Re}_p>1000$）：
  $$\frac{\Delta p}{L}=\frac{1.75\rho\bar V_0^2}{\Phi_sD_p}\frac{1-\varepsilon}{\varepsilon^3}$$
- **Ergun equation（全范围，两项相加）**：
  $$\frac{\Delta p}{L}=\frac{150\bar V_0\mu}{\Phi_s^2D_p^2}\frac{(1-\varepsilon)^2}{\varepsilon^3}+\frac{1.75\rho\bar V_0^2}{\Phi_sD_p}\frac{1-\varepsilon}{\varepsilon^3}$$
  （$\bar V_0$：表观速度；$\varepsilon$：空隙率；混合粒径用表面积平均 $D_s=1/\sum(x_i/D_{pi})$）
- 流化判据与最小流化速度：
  $$\Delta p=g(1-\varepsilon_M)(\rho_p-\rho)L\ \Rightarrow\ \text{代入 Ergun 解 } \bar V_{0M}$$
  层流极限：$\bar V_{0M}\approx\frac{g(\rho_p-\rho)\varepsilon_M^3}{150\mu(1-\varepsilon_M)}\Phi_s^2D_p^2$；湍流极限：$\bar V_{0M}\approx\left[\frac{\Phi_sD_pg(\rho_p-\rho)\varepsilon_M^3}{1.75\rho}\right]^{1/2}$
- 操作窗口：$\dfrac{u_t}{\bar V_{0M}}=\frac{8.33(1-\varepsilon_M)}{\Phi_s^2\varepsilon_M^3}$——细颗粒约 50（$\varepsilon_M=0.45$），粗颗粒约 7.7。
- 干涉沉降与散式膨胀：
  $$u_s=u_t\varepsilon^n;\qquad \frac{\varepsilon^3}{1-\varepsilon}=\frac{150\bar V_0\mu}{g(\rho_p-\rho)\Phi_s^2D_p^2};\qquad \bar V_0\propto\varepsilon^m\ (m\approx3\text{–}4.5)$$
- 鼓泡床膨胀与气泡速度：
  $$\frac{L}{L_M}=\frac{u_b-\bar V_{0M}}{u_b-\bar V_0};\qquad u_b\approx0.7\sqrt{gD_b}$$
  （$u_b$：气泡上升速度；$D_b$：气泡当量直径；鼓泡床膨胀通常仅 20–50%）

## Reference Tables
**典型 $C_D$ 值（固定取向）**

| $\mathrm{Re}_p$ 区间 | 球 $C_D$ | 备注 |
|---|---|---|
| <1 | $24/\mathrm{Re}_p$ | Stokes；Re_p=1 时实测 26.5，误差 ~5% |
| 10³–10⁵ | 0.40–0.45 | 近常数 |
| ≈3×10⁵ | 0.45→0.10 | drag crisis（来流湍流度 2% 时提前至 ~1.4×10⁵） |
| 圆盘 Re>2000 | ≈1.0 | 钝体，无骤降 |

**球形度 $\Phi_s$（Table 7.1 节选）**：球/立方体/短圆柱 1.0；Ottawa 砂 0.95；圆砂 0.83；煤尘 0.73；碎玻璃 0.65；Berl 鞍 0.3；云母片 0.28。

**堆积空隙率（Table 7.2 节选，$D_p/D_t\to0$）**：球与圆柱均 ε≈0.34；$D_p/D_t=0.5$ 时球 0.55、圆柱 0.60。宽粒径分布 ε 更低；振动床略低；粗糙表面略高。

**经验锚点**：ε=0.4 球床中 Burke–Plummer 项相当于**每层颗粒约 5.25 个速度头**损失（沟道缩放处局部速度可达平均 2–3 倍）；ρ 变化小但压降大时 Ergun 用进出口 $\bar V_0$ 的算术平均。

## Worked Example
**例 7.1 型（沉降区判定+试差求 $u_t$+离心强化）**：80–100 目石灰石（ρp=2800 kg/m³，$\bar D_p$=0.161 mm）在 30°C 水中沉降。先算判据 K=4.86——略超 Stokes 区（K<2.6），进入过渡区；假设 Rep=5 查图 $C_D\approx14$ 代入通式得 $u_t$，回算 Rep=3.3，再以更低 Rep 试差收敛得 $u_t\approx0.014$ m/s。改离心场 50g：K 按 $50^{1/3}$ 缩放=17.9 仍在过渡区，同法得 $u_t\approx0.22$ m/s。**要点**：K 判据先行，避免盲目试差；不规则颗粒实际沉降比球形慢，计算值只做上限估计。

**例 7.2 型（干涉沉降）**：闪锌矿（SG 4.0）0.10 mm 颗粒在 CCl₄（SG 1.594）中、体积分数 0.20。自由沉降用 Stokes 得 $u_t$=0.043 ft/s（K=3.34 恰在过渡区上缘，近似可用）；Rep≈2 查 n=4.1，$u_s=u_t(0.8)^{4.1}=0.017$ ft/s。**要点**：浓悬浮液沉降速度按 ε^n 折减，可达自由值一半以下。

**例 7.3 型（最小流化与床膨胀）**：离子交换珠（ρp=1.24 g/cm³，Dp=1.1 mm，Φs=1，εM=0.40）在 20°C 水中反洗。把 Ergun 两项与床重平衡联立成二次方程解得 $\bar V_{0M}$=1.94 mm/s（Rep=2.65）；由 Fig 7.13 查 m=3.9，按 $\bar V_0\propto(\varepsilon/\varepsilon_M)^m$ 反推 25% 膨胀所需速度=5.40 mm/s。**要点**：先解二次方程定 V0M，再用幂律关联从床高比反算速度。

## Anti-patterns
- **不加判定直接套 Stokes 或 Newton 公式**：两者差 5 个数量级的速度-粒径幂次（$D_p^2$ vs $\sqrt{D_p}$）；必须先用 K 判据定位沉降区，过渡区只能试差。
- **忽略空隙率对 Δp 的爆炸性影响**：Ergun 中 $\varepsilon$ 以 $(1-\varepsilon)^2/\varepsilon^3$（黏性项）出现，ε 差 5% 压降可差 30% 以上；重装床后实测值难复现是常态，不是算错。
- **对拉西环、Berl 鞍等高孔隙填料用 Ergun**：预测值显著偏低；应改用填料因子（Ch. 18）或供应商数据。
- **把固定取向的 $C_D$ 曲线用于自由沉降的盘、片**：自由下落时翻滚转向消耗能量，实际 $C_D$ 高于固定取向值（石灰石可达 2–3 倍），沉降速度更慢。
- **用干燥颗粒密度与纯液体物性算浓悬浮液中的大颗粒沉降**：粗粒穿过细粉悬浮液时应用悬浮液的密度与黏度。
- **认为气体流化床均匀膨胀**：气固体系大多是鼓泡流化，床膨胀主要来自气泡相体积而非密相增浓；按散式公式外推会大幅高估床高。
- **加速段按稳态 $C_D$ 算沉降时间**：加速中颗粒的 $C_D$ 高于稳态值，达到终端速度比预测慢（小颗粒通常仍可忽略）。

## Key Takeaways
- 曳力问题的统一语言是 $C_D$–$\mathrm{Re}_p$ 曲线；三个锚点：$24/\mathrm{Re}_p$（<1）、0.44（10³–2×10⁵）、0.10（>3×10⁵，湍流边界层）。
- 沉降计算先算 K：2.6 和 68.9 两个门槛决定闭式公式还是查图试差。
- Ergun = Kozeny–Carman + Burke–Plummer，是填充床压降的默认方程；对 ε 极敏感，且只适用于 ε<0.6 的颗粒床。
- 最小流化速度由"压降=床重"与 Ergun 联立求解；细粒 $\propto D_p^2$、粗粒 $\propto\sqrt{D_p}$。
- 流化操作窗口由 $u_t/\bar V_{0M}$ 决定：细粉约 50 倍空间，粗粒仅约 8 倍，粗粒床易夹带。
- 气固流化的本质缺陷是气泡短路：转化率低于同温度理想接触，放大不确定性大；优点是床层近等温、传热强、固体易输送。
- 水力输送临界速度 1–5 m/s（操作取 1.5–2Vc，≥3Vc 时压降等同单相液体）；气力输送气速 15–30 m/s，压损约 0.5 atm。

## Connects To
- **Ch. 5**：突扩损失（Eq. 5.66）解释了 Burke–Plummer 常数为何远超管流摩擦系数预测；$D_{eq}$ 思想一脉相承。
- **Ch. 6**：驻点压力的等熵修正在 Ma>0.4 后启用，衔接可压缩滞止参数。
- **Ch. 8**：涡街频率测流量（涡街流量计）与节流元件的驻点压力原理直接来自本章。
- **Ch. 18 / 29**：填料塔（气液逆流）与过滤分别是"床层压降"向两相流与滤饼流动的延伸。
- **Ch. 28–29**：颗粒物性（粒径分布、比表面）与离心/沉降分离设备是本章沉降理论的工程落地。
