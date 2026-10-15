# Chapter 6: Flow of Compressible Fluids

## Core Idea
当气体流速可与声速相比（Ma→1）时密度变化不可忽略，压降-流量关系由 Mach 数而非 Reynolds 数主导；三类基本过程（等熵变截面、绝热摩阻管流、等温摩阻管流）各有解析方程，共同特征是存在声速壁垒与"壅塞（choking）"。

## Frameworks Introduced
- **Mach number**：$\mathrm{Ma}\equiv u/a$，流速与当地声速之比；<1 亚声速、≈1 声速、>1 超声速。压缩流动的第一参数（Re 退居次要）。
- **Acoustic velocity（声速）**：$a=\sqrt{(dp/d\rho)_S}=\sqrt{\gamma p/\rho}=\sqrt{\gamma TR/M}$，微小压缩波等熵传播的速度；理想气体中只是温度的函数。
- **Asterisk condition（星号条件）**：u=a、Ma=1 的状态，对应 $p^*,T^*,\rho^*,u^*,G^*$；是 nozzle 与绝热管流所有积分式的自然参考态。
- **Stagnation temperature（滞止温度 $T_s$）**：气体绝热无轴功地减速为零时的温度：$T_s=T+u^2/2c_p$；绝热过程中处处恒定，是绝热管流的守衡量。
- **Isentropic nozzle flow（等熵喷管流）**：收敛段只能亚声速加速、喉部至多 Ma=1；发散段亚声速时回收压力、超声速时继续加速。临界压力比以下流量不再随背压下降（壅塞）。
- **Adiabatic friction flow（绝热摩阻流，即 Fanno 流）**：等截面、绝热、有壁摩擦；滞止温度恒定、熵增；亚声速进入时 Ma 沿程升至 1。
- **Isothermal friction flow（等温摩阻流）**：等截面、经管壁传热维持 T 恒定（长小口径裸管近似）；Ma<0.3 时也近似绝热流动的压降。

## Key Concepts
- **Critical pressure ratio（临界压力比 $r_c$）**：$r_c=p^*/p_0=(2/(\gamma+1))^{\gamma/(\gamma-1)}$；空气（γ=1.4）为 0.528。喉部压力低于 $p^*$ 后下游扰动无法上传，流量恒定。
- **Choking（壅塞）**：亚声速/超声速流都无法穿越声速壁垒；管子加长或试图强迫跨越时流量自动下降来阻止。
- **Friction parameter（摩擦参数 $fL/r_H$）**：绝热管流的无量纲长度；f 取两端算术平均即可（气体黏度随温度变化的影响小）。
- **Shock wave（激波）**：超声速流突降为亚声速的不可逆压力跳跃，熵增；等熵方程严禁跨激波使用。
- **Mass velocity（质量流速 G）**：$G=u\rho$，等截面管内沿程恒定，是联接 Ma 与当地物性的桥梁：$G=\mathrm{Ma}\sqrt{\gamma p\rho}$。
- **Reservoir conditions（储器条件）**：零速大容器的 p₀、T₀，即滞止值，作为喷管积分下限。
- **Area–velocity rule**：$(\mathrm{Ma}^2-1)\,du/u=dS/S$——亚声速收敛加速、超声速发散加速，与不可压缩直觉相反。
- **Supersonic friction factor**：超声速摩擦系数约为同 Re 亚声速值的一半（数据不充分，慎用）。

## Key Equations
- 基本微分方程组（连续性 / 总能量 / 机械能）：
  $$\frac{d\rho}{\rho}+\frac{dS}{S}+\frac{du}{u}=0;\qquad \frac{dQ}{m}=dH+d\!\left(\frac{u^2}{2}\right)$$
  $$\frac{dp}{\rho}+d\!\left(\frac{u^2}{2}\right)+\frac{u^2}{2}\frac{fdL}{r_H}=0$$
  （$p,\rho,T,u$：当地压力/密度/温度/流速；$S$：截面积；$f$：Fanning 摩擦系数；$r_H$：水力半径）
- 声速与滞止温度：
  $$a=\sqrt{\gamma p/\rho}=\sqrt{\frac{\gamma TR}{M}};\qquad T_s=T+\frac{u^2}{2c_p}$$
  （$\gamma=c_p/c_v$：比热比；$M$：分子量；$R$：气体常数）
- 等熵流速度–压比与 Mach 数关系：
  $$u^2=\frac{2\gamma p_0}{(\gamma-1)\rho_0}\left[1-\left(\frac{p}{p_0}\right)^{1-1/\gamma}\right];\qquad \mathrm{Ma}^2=\frac{2}{\gamma-1}\left[\left(\frac{p_0}{p}\right)^{1-1/\gamma}-1\right]$$
  （下标 0：储器/滞止条件）
- 临界压力比（喉部声速判据）：
  $$r_c=\frac{p^*}{p_0}=\left(\frac{2}{\gamma+1}\right)^{\gamma/(\gamma-1)}$$
- 质量流速（等熵）：
  $$G=u\rho=\sqrt{\frac{2\gamma\rho_0p_0}{\gamma-1}}\left(\frac{p}{p_0}\right)^{1/\gamma}\sqrt{1-\left(\frac{p}{p_0}\right)^{1-1/\gamma}}$$
  在 Ma=1 处取极大值 $G^*$。
- 截面积–速度关系：
  $$\frac{du}{u}(\mathrm{Ma}^2-1)=\frac{dS}{S}$$
- 绝热摩阻流（Fanno）主积分式（以 Ma 为因变量）：
  $$\frac{\bar fL}{r_H}=\frac{1}{\gamma}\left(\frac{1}{\mathrm{Ma}_a^2}-\frac{1}{\mathrm{Ma}_b^2}-\frac{\gamma+1}{2}\ln\frac{\mathrm{Ma}_b^2\{1+[(\gamma-1)/2]\mathrm{Ma}_a^2\}}{\mathrm{Ma}_a^2\{1+[(\gamma-1)/2]\mathrm{Ma}_b^2\}}\right)$$
  （$\bar f$：两端摩擦系数均值；$L$：管长）
- 最大管长（出口恰为 Ma=1）：
  $$\frac{\bar fL_{\max}}{r_H}=\frac{1}{\gamma}\left(\frac{1}{\mathrm{Ma}_a^2}-1-\frac{\gamma+1}{2}\ln\frac{2\{1+[(\gamma-1)/2]\mathrm{Ma}_a^2\}}{\mathrm{Ma}_a^2(\gamma+1)}\right)$$
- 绝热流物性比（p、T、ρ 沿程变化）：
  $$\frac{p_a}{p_b}=\frac{\mathrm{Ma}_b}{\mathrm{Ma}_a}\sqrt{\frac{1+[(\gamma-1)/2]\mathrm{Ma}_b^2}{1+[(\gamma-1)/2]\mathrm{Ma}_a^2}};\qquad \frac{T_a}{T_b}=\frac{1+[(\gamma-1)/2]\mathrm{Ma}_b^2}{1+[(\gamma-1)/2]\mathrm{Ma}_a^2}$$
  亚声速段沿流动方向：Ma↑、p↓、T↓、ρ↓（ρ 降得更快）。
- 等温摩阻流工作方程（圆管 $r_H=D/4$）：
  $$p_a^2-p_b^2=\frac{G^2RT}{M}\left[2\ln\frac{\rho_a}{\rho_b}+\frac{fL}{r_H}\right]$$
  （Ma<0.3 的绝热流也可近似用它；$Q/m=(u_b^2-u_a^2)/2$ 补齐能量账）

## Reference Tables
**三类过程对比**

| 过程 | 截面 | 热条件 | 守衡量 | 典型应用 |
|---|---|---|---|---|
| 等熵喷管流 | 变截面 | 绝热无摩擦 | $T_s$、熵 | 喷嘴、流量测量、风洞 |
| 绝热摩阻流 | 等截面 | 绝热不可逆 | $T_s$（熵增） | 长绝热气管 |
| 等温摩阻流 | 等截面 | 壁面传热恒温 | T | 裸长小口径气管 |

**典型临界值（γ=1.4 空气）**：$r_c=0.528$；$T^*/T_0=2/(\gamma+1)=0.833$；$u^*/u_0$（对声速比）=1；等温流表观壅塞出口 $\mathrm{Ma}=1/\sqrt{\gamma}\approx0.845$（无物理意义）。

## Worked Example
**例 6.1 型（喷管全套状态点）**：空气自 20 atm、555.6 K 储器进入收敛-发散喷管，喉部 Ma=0.8、喉面积=出口一半。(a) 用压比公式 (6.28) 得喉部 p=0.656p₀，依次套等熵关系得 T、ρ，声速式得 u，乘积得 G；(b) 令 Ma=1 直接得星号条件（p*=10.56 atm、T*=463 K、G*=3476 kg/m²·s）；(c) 连续性给出口 G=G*/2，用式 (6.30) 试差解出 p_r/p₀=0.0939，回代得出口 Ma=2.20。**要点**：给定面积比反推超声速出口 Ma 是"连续性+G(p) 函数"的联立问题。

**例 6.2 型（绝热摩阻流三问）**：入口 Ma=0.05。(a) 直接代 $L_{\max}$ 公式得 $\bar fL_{\max}/r_H=280$；(b) 出口取 Ma=1，用物性比公式求 p*、T*、ρ*；(c) 给定 $\bar fL_{\max}/r_H=400$（管比极限更长），试差反解 $\mathrm{Ma}_a=0.0419$，流量按 G=ρu 重算——管长了，流速和流量自动下调以维持不跨声速。

**例 6.3 型（等温压降）**：2.7 atm 绝压、15°C 空气，0.265 m³/s 进 75 mm 钢管 70 m。由 G=198.5 kg/m²·s → Re=8.6×10⁵ → 查图 f=0.0044；把 $p_a^2-p_b^2=(p_a-p_b)(p_a+p_b)$ 拆开，对平均压力 $\bar p$ 试差，得出口 1.264 atm。**要点**：等温方程中未知量藏在 $\ln(p_a/p_b)$ 和 $\bar p$ 里，一轮试差即收敛。

## Anti-patterns
- **背压低于 $p^*$ 还指望流量继续增大**：喉部声速后下游信息无法上传，流量封顶；降压只会在管外产生波系。
- **等熵方程跨激波使用**：激波是熵增的不可逆跳跃，$p/\rho^\gamma$ 关系失效，必须分激波前后两段处理。
- **绝热管流当作等温算而不查 Ma**：等温式只在 Ma<0.3 时近似绝热流；高压差长管线误用会显著低估压降（反之亦然）。
- **认为绝热摩阻流中气体"减速"**：亚声速进入时摩擦使 p、ρ 下降更快，流速反而沿程升高、Ma→1；直觉"摩擦减速"在这里方向相反。
- **等温流套用表观壅塞条件 Ma=1/√γ**：该状态对应极高流速与剧烈膨胀，等温假设早已不成立，仅为数学极限。
- **沿管用恒定 f 但忽略 Ma 对 f 的影响量级**：亚声速问题用两端平均 f 足够，但超声速 f 约减半，直接套亚声速图会低估管长能力。

## Key Takeaways
- 压缩流动第一判据是 Ma，不是 Re；Ma<0.3 时可整体退回第 5 章不可压缩方法。
- 临界压力比 $r_c=(2/(\gamma+1))^{\gamma/(\gamma-1)}$（空气 0.528）决定 nozzle 是否壅塞；壅塞后流量只由 $p_0,T_0$ 与喉面积决定。
- 变截面加速规则：亚声速要收敛、超声速要发散；超声速喷管的发散段是"加速器"不是"扩压器"。
- 绝热管流的硬约束是 $\bar fL/r_H\le L_{\max}$ 对应值；管子超长不会超音，只会掉流量（choking）。
- 等温管流用 $p_a^2-p_b^2$ 形式最方便，对平均压力试差一轮即解；Ma<0.3 的绝热流也可借用。
- 滞止温度 $T_s=T+u^2/2c_p$ 是绝热过程的不变量，做焓账和测温修正（总温探针）都靠它。

## Connects To
- **Ch. 5**：机械能衡算中的 $h_{fs}$ 项与 Fanning f 直接沿用；本章是"当第 5 章的不可压缩假设失效时"的升级版。
- **Ch. 8**：孔板/文丘里/喷嘴测流量时的气体膨胀因子与临界流（critical flow）计量的理论基础。
- **Ch. 10–11（热）**：绝热/等温假设本质上是传热速率问题——管壁散热能力决定选哪个模型。
- **外部**：Fanno/Rayleigh 流动、激波关系（Rankine-Hugoniot）属于气体动力学教材的延伸；安全阀排放与真空系统设计是本章方程的直接工程应用。
