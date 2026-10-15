# Patterns — 命名方程速查与通用解题套路

## Part A 命名方程/原理速查（按主题）

### 流体力学
- **Hagen–Poiseuille**（ch5）：层流管流 $f = 16/Re$，压降 ∝ $\bar V$。
- **von Kármán 湍流方程**（ch5）：光滑管湍流 $f$–Re 关系。
- **Blasius 简化式 $f = 0.0014 + 0.125Re^{-0.32}$**（ch5）：湍流光滑管试差用。
- **Metzner–Dodge $Re_n$**（ch5）：幂律流体流态判据；Bingham 塞流（ch5）。
- **面积–速度关系 $du/u(Ma^2-1) = dS/S$**（ch6）：亚声收敛、超声扩张才加速。
- **Stokes / Newton 定律**（ch7）：$C_D = 24/Re_p$（爬流）；$C_D = 0.44$（湍流绕流）。
- **判据 $K = D_p[g\rho\Delta\rho/\mu^2]^{1/3}$**（ch7）：K<2.6 Stokes、2.6–68.9 过渡、68.9–2360 Newton。
- **Ergun 方程**（ch7）：固定床压降层流+湍流叠加。
- **Kozeny–Carman / Burke–Plummer**（ch7）：Ergun 的两个极限。
- **NPSH 定义式**（ch8）：吸入防气蚀校核。
- **孔板/文丘里/Pitot 流量方程**（ch8）：$u_0 = C_o\sqrt{2\Delta p/\rho(1-\beta^4)}/\sqrt{1-\beta^4}$ 家族。
- **Zwietering 式 9.35**（ch9）：悬浮临界转速。
- **液滴尺寸式 $\bar D_s/D_a = 0.058(1+5.4\Psi)We^{-0.6}$**（ch9）。

### 传热
- **平壁/圆筒导热**（ch10）：$q = k\bar A_L\Delta T/(r_o-r_i)$。
- **平板/圆柱/球冷却指数式**（ch10）：$(8/\pi^2)e^{-(\pi/2)^2Fo}$ 家族，Fo>0.1 才可取首项。
- **集总法**（ch10）：Bi<0.1，球 $1/U = 1/h + r_m/5k$。
- **半无限解 $Z = x/2\sqrt{\alpha t}$**（ch10）：土壤冻结、淬火表面。
- **阻力串联式**（ch11）：$1/U_o = D_o/(D_ih_i) + (x_w/k_m)(D_o/\bar D_L) + 1/h_o$ (+污垢)。
- **Dittus–Boelter / Sieder–Tate**（ch12）：$0.023Re^{0.8}Pr^n$ 与 $0.023Re^{0.8}Pr^{1/3}\phi_v$。
- **管内层流 $Nu = 2Gz^{1/3}\phi_v$**（ch12）：长管极限 3.66。
- **Nusselt 冷凝式**（ch13）：竖管 0.943 / 水平管束 0.729 系数族。
- **Zuber 峰值热流式**（ch13）：$(q/A)_{max} = 0.15\lambda\rho_V^{1/2}[\sigma g(\rho_L-\rho_V)]^{1/4}$。
- **Stefan–Boltzmann / Planck / Wien / Kirchhoff**（ch14）：辐射四基石。
- **灰体互换 $\mathcal{F}$**（ch14）：平行大平面、完全包围两个封闭解。
- **Donohue 壳程式**（ch15）：$G_e = \sqrt{G_bG_c}$ 折算壳程流速。
- **ε–N_H 法**（ch15）：不定温差时定出口温度。
- **多效焓平衡 + 等面积分配**（ch16）：$A_iU_i\Delta T_i$ 相等。

### 传质与分离
- **Fick 第一定律**（ch17）：分子扩散骨架。
- **Chapman–Enskog / Wilke–Chang**（ch17）：气/液扩散系数估算（T^1.75 外推规则；ψ_B=2.6 水）。
- **Chilton–Colburn 类比 $j_M = j_H = f/2$**（ch17）。
- **Froessling $Sh = 2+0.6Re^{1/2}Sc^{1/3}$**（ch17）。
- **Eckert 泛点图 / 泛点压降 $\Delta P_{flood} = 0.115F_p^{0.7}$**（ch18）。
- **HTU 加和 $H_{Oy} = H_y + (mG_M/L_M)H_x$**（ch18）。
- **绝热饱和线 $(H_s-H)/(T-T_s) = c_s/\lambda_s$**（ch19）。
- **凉水塔操作线**（ch19）：斜率 $G_xc_L/G_y'$。
- **Kremser 方程**（ch20/23）：恒 A/S 级联解析解（吸收/汽提/浸取通吃）。
- **McCabe–Thiele / q 线 $y = -\frac{q}{1-q}x + \frac{x_F}{1-q}$**（ch21）。
- **Fenske $N_{\min} = \ln\frac{x_D(1-x_B)}{x_B(1-x_D)}/\ln\alpha - 1$**（ch21/22）。
- **Underwood 方程**（ch22）：$\phi$ 根取在两关键 α 之间。
- **填料萃取塔液泛式 23.4**（ch23）。
- **干燥时间积分 $t_T = \frac{m_s}{A}\int dX/R$**（ch24）：恒速+降速分段。
- **Langmuir / Freundlich / 吸附势理论**（ch25）。
- **穿透时间 $t_b = t^*(1-LUB/L)$，$t^* = L\rho_b(W_{sat}-W_0)/(u_0c_0)$**（ch25）。
- **van Deemter $H = A+B/u+Cu$**（ch25）：色谱板高。
- **溶解扩散 $J_A = Q_A\Delta p/z$**（ch26）。
- **渗析三阻力 $1/K = 1/k_1 + 1/k_m + 1/k_2$**（ch26）。
- **RO $J_w = (\Delta P - \Delta\pi)\times$ 水力渗透**（ch26）。
- **Kelvin 方程**（ch27）：临界晶核 nm 级。
- **MSMPR $n = n^\circ e^{-z}$，$z = L/G\tau$ + 矩方程**（ch27）。
- **Bond 定律 $P/\dot m = 0.3162W_i(1/\sqrt{D_{pb}} - 1/\sqrt{D_{pa}})$**（ch28）。
- **恒压过滤 $t/V = (K_c/2)V + 1/q_0$**（ch29）：α–Δp 回归。
- **Kynch / Coe–Clevenger 通量法**（ch29）：增浓器面积。
- **Σ 放大 $q = 2\Sigma u_g$**（ch29）：离心机。

## Part B 通用解题套路（全书反复出现的方法论）

1. **衡算先行**：画控制体 → 物料/能量/动量衡算（ch4）→ 未知量是否闭合；流体问题落到 Bernoulli 工作式 + 损失项清单（直管 $4fL/D\times$ 速度头 + 管件 K）。
2. **无量纲数分区，再选关联式**：先算 Re（流态）、Bi/Fo（非稳态选解）、Gz（入口区）、Gr（自然对流）、Sc/Pr（类比适用性）、K（沉降分区）——判据不确认就套公式是全书反复警告的错误源。
3. **试差法**：h=f(Re)→U→q 链条中速度未知时，设初值→迭代到闭合（ch5 流速、ch8 出口压力、ch12 壁温、ch13 冷凝 h 均为标准试差场景）。
4. **对数平均无处不在**：换热器 LMTD（ch11）、传热对数平均面积（ch10）、单向扩散对数浓度梯度（ch17）、直线操作线的对数平均推动力（ch18）——同一数学结构。
5. **阻力串联/并联合成**：热阻 1/U（ch11）、传质 1/K_y（ch17/18）、渗析三阻力（ch26）、过滤滤饼+介质（ch29）；先找控制阻力再谈强化。
6. **级联三件套选择逻辑**：恒 A/S 且线性平衡 → Kremser 解析；二元精馏恒摩尔溢流 → McCabe–Thiele 图解；填料塔微分接触 → HTU–NTU 积分。多组分精馏走 Fenske→Underwood→Gilliland 群法链。
7. **放大三问**：几何相似下哪个无量纲数守恒？——搅拌恒 P/V vs 恒混合时间不可兼得（ch9）、泵相似定律（ch8）、离心 Σ 值（ch29）、悬浮颗粒单位体积功率（ch17）、混合 Froude 数（ch28）。
8. **经济最优化经验锚点**：最优管内流速、R_D = 1.1–1.3 R_Dm、多效等面积、凉水塔 approach 5–15°F、MVR ΔT≈5°C、设计气速半泛点——先查 cheatsheet 再细算。

## Part C 跨章连接（章节间的接口）

- **ch5 ↔ ch7**：管流 $f$ 与绕流 $C_D$ 同源；Ergun 可视为"内含固体的管流"。
- **ch5 ↔ ch12**：f–Re 关系（式 5.53/5.54）支撑 Colburn 传热类比。
- **ch10 ↔ ch11**：对数平均半径 ↔ LMTD，同一数学工具。
- **ch11 ↔ ch12/13/14**：U 的合成需要分系数 h——ch12（无相变）、ch13（相变）、ch14（辐射附加 $h_r$）是 h 的三处来源。
- **ch13 ↔ ch15/16/18**：管束排布与冷凝（ch15）、再沸器与临界温差（ch16）、不凝气放空（ch18）。
- **ch16 ↔ ch19**：蒸发二次汽与增湿操作同属"水蒸气-不凝气"体系；湿度图共用。
- **ch17 ↔ ch18/23/25/26**：k 系数与 D 幂次谱系（1.0 膜 / 2/3 边界层 / 1/2 渗透）决定所有设备关联式的选型与外推。
- **ch18 ↔ ch20**：填料塔 HTU–NTU 与板式塔理论级是同一传质任务的两种离散化。
- **ch21 ↔ ch22**：二元图解 → 多组分群法；反常精馏（夹紧区洗脱非关键）只在多组分出现。
- **ch20 ↔ ch23/25**：Kremser 参数（A/S/E/N）在浸取、离子交换中反复变形出现。
- **ch7 ↔ ch9/28/29**：$u_t$ 是搅拌悬浮（Zwietering）、流化窗口、沉降离心（Σ 法）的共同输入。
- **ch13 ↔ ch18**：Zuber 泛点与填料塔液泛同属"两相逆流水力学上限"。
