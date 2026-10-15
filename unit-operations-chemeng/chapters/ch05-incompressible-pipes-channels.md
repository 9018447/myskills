# Chapter 5: Incompressible Flow in Pipes and Channels

## Core Idea
将管内稳态不可压缩流动的摩阻问题统一为一套核心工具链：壁面剪应力 → Fanning 摩擦系数 f → 压降方程，层流可解析、湍流靠通用速度分布与摩擦系数图；非圆形管道用等效直径 $D_{eq}=4r_H$ 归一化。

## Frameworks Introduced
- **Shear-stress distribution（剪应力线性分布）**：$\tau_w/r_w = \tau/r$，即 $\tau$ 随半径线性变化、管轴处为零——层流/湍流、牛顿/非牛顿流体均成立。Use it to relate wall shear to pressure gradient without knowing the velocity profile.
- **Fanning friction factor**：$f \equiv \tau_w/(\rho\bar V^2/2)$。注意 Fanning 定义（Darcy 系数是其 4 倍），全书用 Fanning。
- **Hydraulic radius / equivalent diameter**：$r_H \equiv S/L_p$（截面积/润湿周边），$D_{eq}=4r_H$；环形空间 $D_{eq}=D_o-D_i$。Use for noncircular channels in turbulent flow (laminar 用之误差较大)。
- **Universal velocity distribution（通用速度分布律）**：以 $u^*, u^+, y^+$ 无量纲化，分区给出 $u^+=y^+$（黏性底层）、$u^+=5.00\ln y^+-3.05$（缓冲层）、$u^+=2.5\ln y^+ +5.5$（湍流核心，Prandtl）。
- **Hagen-Poiseuille equation**：层流压降解析解，也是毛细管测黏度的理论基础。
- **Power-law / Bingham pipe-flow relations**：幂律流体速度分布式与压降式（Eq. 5.23–5.24）；Bingham 塑性体出现中心 plug flow，plug 半径 $r_c=(\tau_0/\tau_w)r_w$。
- **Separation from velocity decrease**：连续扩张通道中近壁流股动能耗尽即分离，锥形扩张器半角 >7° 即可能分离。

## Key Concepts
- **Skin friction（表皮摩擦 $h_{fs}$）**：流体与管壁间黏性剪切造成的摩擦损失，对应压降 $\Delta p_s/\rho=h_{fs}$。
- **Viscous sublayer（黏性底层）**：紧贴壁面、以黏性剪切为主的薄层，无明确上界；缓冲层（buffer layer）内黏性与涡流剪切并存，湍流核心以涡流黏度为主。
- **Friction velocity（摩擦速度 $u^*$）**：$u^*=\bar V\sqrt{f/2}=\sqrt{\tau_w/\rho}$，湍流速度分布的无量纲标尺。
- **Relative roughness（相对粗糙度 k/D）**：粗糙度参数 k 与管径之比，决定湍流摩擦系数偏离光滑管的程度；层流中粗糙度几乎无影响。
- **Hydraulically smooth（水力光滑管）**：继续打磨不再降低摩擦系数的管子；拉制铜/黄铜管可视为水力光滑。
- **Vena contracta（缩流断面）**：突缩后射流最小截面，收缩损失的主要来源。
- **Velocity head（速度头 $\bar V^2/2$）**：局部损失与管路摩擦的统一计量单位；1 速度头 ≈ 50 倍管径长直管（经验值）。
- **Drag reduction（Toms 效应）**：稀聚合物溶液（几十 ppm）使湍流摩擦系数大幅下降（可达 70%），源于大分子抑制近壁小涡、增厚黏性底层。
- **Viscous dissipation（黏性耗散）**：绝热条件下压降全部转化为热：$\Delta T=\Delta p_s/(c_v\rho)$。
- **Kinetic / momentum correction factors（$\alpha,\beta$）**：层流分别为 2.0 与 4/3；湍流接近 1（Re=10⁴ 时 α≈1.08、β≈1.03），一般取 1。

## Key Equations
- 剪应力分布与壁面平衡：
  $$\frac{dp}{dL}+\frac{2\tau}{r}=0 \quad\Rightarrow\quad \tau_w=\frac{D}{4}\left(-\frac{dp}{dL}\right)$$
  （$p$：静压；$\tau,\tau_w$：半径 r 处与壁面剪应力；$D$：管径）
- 四个摩阻量的换算（本章枢纽）：
  $$h_{fs}=\frac{2\tau_w}{\rho r_w}L=\frac{\Delta p_s}{\rho}=4f\frac{L}{D}\frac{\bar V^2}{2},\qquad \frac{\Delta p_s}{L}=\frac{2f\rho\bar V^2}{D}$$
  （$h_{fs}$：单位质量表皮摩擦 J/kg；$\Delta p_s$：表皮摩擦压降；$\bar V$：平均流速；$L$：管长）
- 等效直径：
  $$r_H\equiv\frac{S}{L_p},\quad D_{eq}=4r_H;\qquad \text{环形：}D_{eq}=D_o-D_i$$
  （$S$：流通截面积；$L_p$：润湿周边；$D_o,D_i$：环隙外/内径）
- 层流速度分布与 Hagen-Poiseuille：
  $$\frac{u}{u_{max}}=1-\left(\frac{r}{r_w}\right)^2,\qquad \frac{\bar V}{u_{max}}=0.5$$
  $$\Delta p_s=\frac{32L\bar V\mu}{D^2},\qquad f=\frac{16}{\mathrm{Re}}\ (\mathrm{Re}<2100)$$
  （$u$：局部流速；$u_{max}$：管轴最大流速；$\mu$：黏度）
- 幂律流体层流压降：
  $$\Delta p_s=2K'\left(\frac{3n'+1}{n'}\right)^{n'}\frac{\bar V^{n'}}{r_w^{n'+1}}L$$
  （$K'$：稠度系数；$n'$：流动行为指数）
- 非牛顿 Reynolds 数与层流摩擦系数：
  $$\mathrm{Re}_n=2^{3-n'}\left(\frac{n'}{3n'+1}\right)^{n'}\frac{D^{n'}\rho\bar V^{2-n'}}{K'},\qquad f=\frac{16}{\mathrm{Re}_n}$$
- 湍流速度分布（分区）：
  $$u^+=y^+\ (y^+<5);\quad u^+=5.00\ln y^+-3.05\ (5<y^+<30);\quad u^+=2.5\ln y^++5.5\ (y^+>30)$$
  （$u^+=u/u^*$；$y^+=yu^*\rho/\mu$；$y$：距壁距离）
- von Kármán 光滑管方程（湍流 f–Re 关系，Re 10⁴–10⁶ 内与图偏差 <2%）：
  $$\frac{1}{\sqrt{f/2}}=2.5\ln\!\left(\mathrm{Re}\sqrt{\frac f8}\right)+1.75$$
- 光滑管简便式：
  $$f=0.046\,\mathrm{Re}^{-0.2}\ (5\times10^4\sim10^6);\qquad f=0.0014+\frac{0.125}{\mathrm{Re}^{0.32}}\ (3\times10^3\sim3\times10^6)$$
- 平均/最大速度比（可用于 Pitot 测速）：
  $$\frac{\bar V}{u_{max}}=\frac{1}{1+3.75\sqrt{f/2}}$$
- 突扩（解析）与突缩（经验）损失：
  $$h_{fe}=\frac{(\bar V_a-\bar V_b)^2}{2}=K_e\frac{\bar V_a^2}{2},\ K_e=\left(1-\frac{S_a}{S_b}\right)^2;\qquad h_{fc}=K_c\frac{\bar V_b^2}{2},\ K_c=0.4\left(1-\frac{S_b}{S_a}\right)$$
  （$S_a,S_b$：上/下游截面积；突缩用小管速度头）
- 管系总摩擦（并入 Bernoulli 方程 $h_f$ 项）：
  $$h_f=\left(4f\frac LD+K_c+K_e+\sum K_f\right)\frac{\bar V^2}{2}$$
  （$K_f$：管件/阀门损失系数）
- 非等温修正（Re>2100）：
  $$f=\frac{f_{\text{bulk}}}{\psi},\quad \psi=\left(\frac{\mu}{\mu_w}\right)^{0.17}\text{(加热)},\ \left(\frac{\mu}{\mu_w}\right)^{0.11}\text{(冷却)}$$
  （$\mu,\mu_w$：主体温度/壁温下黏度；粗糙管完全湍流区不作此修正）

## Reference Tables
**管件损失系数 $K_f$（标准螺纹管件，Table 5.1）**

| Fitting | $K_f$ |
|---|---|
| 45° 弯头 | 0.35 |
| 90° 弯头（标准） | 0.75 |
| 三通直通 | 0.4 |
| 三通作弯头用 | 1.0 |
| 180° 回弯头 | 1.5 |
| 闸阀 全开 / 半开 | 0.17 / 4.5 |
| 角阀 全开 | 2.0 |
| 球阀 全开 | 6.0 |

**速度分布分区与典型值**

| 层 | $y^+$ 范围 | 控制机制 |
|---|---|---|
| 黏性底层 | <5 | 纯黏性剪切 |
| 缓冲层 | 5–30 | 黏性+涡流 |
| 湍流核心 | >30 | 涡流黏度为主 |

| 量 | 层流 | 湍流（Re=10⁴） |
|---|---|---|
| $\bar V/u_{max}$ | 0.5 | ~0.82（随 Re 增至 0.87@10⁶） |
| $\alpha$ | 2.0 | ~1.08 |
| $\beta$ | 4/3 | ~1.03 |

其他典型值：锻铁/钢管粗糙度 k=1.5×10⁻⁴ ft（与管径无关）；钢制管系按"50 管径 ≈ 1 速度头"估算；锥形扩张器无分离极限半角 7°，≥35° 时损失反超突扩；渐缩过渡（锥形缩径/喇叭口）可使 $K_c$ 降至约 0.05。

## Worked Example
**例 5.1 型（定管径求压降 / 定压降求流速）**：水以 8 ft/s 流过 3 in 内径塑料长管。(a) 先算 Re=1.4×10⁵，查摩擦系数图得 f=0.0041，代入 $\Delta p_s/L=2f\rho\bar V^2/(Dg_c)$ 得 ≈2.83 psi/100ft。(b) 反向问题（给定压降上限求 $\bar V$）时 Re 未知、f 未知——把 f 写成 $\bar V$ 的函数后试差迭代 2–3 次即收敛（得 6.6 ft/s）。**要点**：湍流区 f 随 Re 变化很弱，试差天然快收敛。

**例 5.2 型（重力排油管流量）**：原油（SG 0.93、μ=4 cP）自罐底经 45 m 3-in 管（1 个弯头+2 个闸阀）重力排入低 9 m 大气。以液面为 a、管口为 b 列 Bernoulli（$p_a=p_b$、$\bar V_a=0$），位差 147.1 m²/s² 全部交给动能+摩擦；进口突缩 $K_c=0.4$、无出口扩张损失（$K_e=0$），管件 $\sum K_f=1.09$。设 V̄ 试差：V̄→Re→查图 f→回代解 V̄，收敛于 4.40 m/s → 75.6 m³/h。**要点**：排入大气不产生射流膨胀损失，$K_e$ 取 0。

## Anti-patterns
- **混淆 Fanning 与 Darcy 摩擦系数**：两者差 4 倍，$f_{Fanning}=16/\mathrm{Re}$ 而非 64/Re；混用导致压降差 4 倍。
- **对 $\Delta p_s$ 与 $p_a-p_b$ 不加区分**：只有纯水平等径管、无泵无其他形阻时二者相等；有高度变化、泵、配件或分离时 $p_a-p_b\ne\Delta p_s$。
- **层流用等效直径硬套**：$D_{eq}$ 法对湍流好用，层流中误差大；环形等截面层流应直接用解析式（含 $\phi_a$ 修正）。
- **突缩损失用大管速度头**：$h_{fc}=K_c\bar V_b^2/2$ 用的是下游小管速度；突扩才是用上游小管速度。
- **黏性底层当"无涡层"**：底层内偶有涡侵入、无锐利边界，只是黏性剪切占优；以此为据做精确设计会失真。
- **锥形扩张器随意选角**：半角 >7° 即分离，≥35° 时损失比突扩还大——"渐扩一定比突扩好"是错觉。
- **完全湍流的粗糙管仍做 $\mu/\mu_w$ 修正**：f 已与 Re 无关，不应再作壁温黏度修正。

## Key Takeaways
- 一切从 $\tau$–r 线性关系出发：无需知道速度剖面即可把压降和壁面剪应力挂上钩。
- 全章核心换算链 $h_{fs}=\Delta p_s/\rho=4f(L/D)(\bar V^2/2)$ 记死；$\Delta p_s/L=2f\rho\bar V^2/D$ 是直管压降的工作方程。
- 层流三件套：抛物线剖面、$\bar V=u_{max}/2$、$f=16/\mathrm{Re}$；$\alpha=2,\beta=4/3$ 不能漏（Bernoulli 动能项此时要用 $\bar V^2$ 配 α=2）。
- 湍流用摩擦系数图（f–Re，参数 k/D）+ 试差；已知压降求流量是天然试差问题，2–3 轮收敛。
- 非圆管湍流用 $D_{eq}=4r_H$（环隙 $=D_o-D_i$）；非牛顿用 $\mathrm{Re}_n$，假塑性流体层流维持到更高 Re。
- 局部损失统一写成速度头倍数：$K_c+K_e+\sum K_f$；粗估时"50 管径 ≈ 1 速度头"。
- 稀聚合物减阻（Toms 效应）可达 70%，适合固定管径扩能，但长管线高分子会剪切降解失效。

## Connects To
- **Ch. 3–4**：f–Re 关系建立在雷诺数与 Bernoulli/机械能衡算（$h_f$ 项、$\alpha,\beta$ 修正因子）之上。
- **Ch. 6**：此处 $\Delta p_s$ 关系限于不可压缩流体；气体高速流动需引入可压缩流处理。
- **Ch. 7**：边界层分离概念在本章仅作引子，绕流形阻（form drag）在浸没物体流动中展开。
- **Ch. 9**：搅拌槽内的流动与耗散沿用同一剪切/湍流框架。
- **外部**：Moody 图即本章摩擦系数图的工程版；毛细管黏度计是 Hagen-Poiseuille 方程的直接仪器化。
