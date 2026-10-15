# Chapter 1: Definitions and Principles

## Core Idea
化学工程的对象是工业过程，而"单元操作"（unit operations）把千差万别的过程分解为跨行业重复出现、遵循相同科学原理的物理步骤。本章奠定全书的两块基石：三套单位制的严格定义与换算纪律，以及量纲分析这一把多变量问题压缩为少量无量纲群的通用工具。

## Frameworks Introduced
- **Unit operation（单元操作）**：跨越行业与过程界限、具有共同技术与科学原理的操作（流体输送、传热、蒸馏、干燥、蒸发、结晶等）；反应动力学以外的物理步骤统一归入此框架。Use when organizing any process into teachable, transferable steps.
- **四大基本比例关系**（一切单位制的根源）：Newton 第二定律 $F=k_1\,d(mu)/dt$；万有引力定律 $F=k_2\,m_a m_b/r^2$；热力学第一定律循环形式 $Q_c=k_3 W_c$；绝对温度定义 $T=k_4\lim_{p\to0}(pV/m)$。
- **Dimensional analysis（量纲分析）**：利用"物理方程必须量纲齐次"的代数方法，把 $n$ 个变量重组为 $n-r$ 个无量纲群（$r$ 为基本量纲数）。Use when no theoretical equation exists and experimentation is the only route.
- **Dimensionally homogeneous vs dimensional equations（量纲齐次方程与经验方程）**：齐次方程用一致单位（consistent units）即可直接代入任意单位制；经验方程（如式 1.41）系数绑定特定单位，换单位必须改系数。
- **Material & energy balances（物料与能量衡算）**：控制面（control surface）必须是封闭包络；稳态下输入=输出。

## Key Concepts
- **Consistent units（一致单位）**：整个方程只用同一套基本单位，无需换算因子。
- **$g_c$（Newton 重力单位比例因子）**：fps 制中 $g_c=32.174\ \text{lb·ft}/(\text{lb}_f\text{·s}^2)$，用于力学量在 lb 与 lb$_f$ 之间的严格换算。
- **标准重力加速度 $g_n$**：定义值 9.80665 m/s² = 32.174 ft/s²（国际约定，非实测值）。
- **Virial equation（维里方程）**：$z=1+\rho_M B+\rho_M^2 C+\rho_M^3 D+\cdots$，系数只随温度变化，是真实气体状态方程的理论骨架。
- **Compressibility factor $z$（压缩因子）**：$z=p/(\rho_M RT)$，偏离 1 的程度度量气体非理想性。
- **Molar density $\rho_M$（摩尔密度）**：单位体积的摩尔数 $n/V$。
- **Partial pressure $p_A$（分压）**：$p_A\equiv P y_A$，理想与非理想气体混合物中各分压之和恒等于总压。
- **Control surface / control volume（控制面/控制体）**：能量衡算前必须划定的封闭边界，包含设备壁面、进出口截面与轴截面。
- **Shaft work $W_s$（轴功）**：通过转轴跨越控制面传递的机械功；约定设备对外做功为正（泵对流体做功则为负）。
- **Dimensionless group（无量纲群）**：量纲完全消去、数值与所用一致单位无关的变量组合（命名群见附录 2）。

## Key Equations
- 理想气体定律：$z=\dfrac{pV}{nRT}=\dfrac{p}{\rho_M RT}=1$ —— 低压（约 1–2 atm 以下）工程计算的标准形式；$p$=压力，$V$=体积，$n$=摩尔数，$R$=通用气体常数 8.31447 J/(K·mol)，$T$=绝对温度，$\rho_M$=摩尔密度。
- 维里方程：$z=1+\rho_M B+\rho_M^2 C+\rho_M^3 D$ —— $B,C,D$ 为第二、三、四维里系数（仅随温度变），高压真实气体需全部保留。
- 单股流稳态能量衡算（SI）：$m\left[\dfrac{u_b^2-u_a^2}{2}+g(Z_b-Z_a)+H_b-H_a\right]=Q-W_s$ —— $u_a,u_b$=进/出口流速，$Z_a,Z_b$=相对基准面高度，$H_a,H_b$=进/出口焓，$Q$=进入控制面的净热（流入为正），$W_s$=设备对外的净轴功（对外做功为正）。fps 制需在动能与位能项除以 $g_c J$（式 1.60）。摩擦不做单独项——它是控制面内部的机械能→热转化，已隐含在其他项中。
- 开尔文温标定义：$T\equiv 273.16\,\lim_{p\to0}(pV/m)_T / \lim_{p\to0}(pV/m)_0$。
- 摄氏/华氏换算：$T^\circ\text{F}=32+1.8\,T^\circ\text{C}$；温差 $\Delta T^\circ\text{C}=1.8\,\Delta T^\circ\text{F}$。

## Reference Tables
- **气体常数 $R$ 常用取值**：8.31447 J/(K·kg mol)｜82.056×10⁻³ m³·atm/(K·kg mol)｜1.9858 Btu/(°R·lb mol)｜1545.3 ft·lb$_f$/(°R·lb mol)。
- **关键换算因子（由精确定义推出，Example 1.1）**：1 N = 0.224809 lb$_f$；1 Btu = 251.996 cal$_{IT}$；1 atm = 1.01325×10⁵ Pa = 14.6959 lb$_f$/in²；1 hp = 0.74570 kW。
- **能量单位定义**：1 J = 1 N·m；1 cal（热化学）= 4.1840 J；1 cal$_{IT}$ = 4.1868 J；J（热功当量）= 4.1868 J/cal$_{IT}$ = 778.17 ft·lb$_f$/Btu。
- **标准摩尔体积**：1 atm、0 °C 下 22.4 m³/kg mol（= 22.4 L/g mol；fps 制 359 ft³/lb mol）。

## Worked Example
**Example 1.2（量纲分析推导传热关联式骨架）**：湍流液体流经长直加热管，管壁高于液体平均温度恒定值。设 $q/A=\Psi(D,\bar V,\rho,\mu,c_p,k,\Delta T)$（7 个变量、5 个基本量纲 $\bar M,\bar L,\bar t,\bar T,\bar H$）。令各变量指数相等得 5 个线性方程，7 个未知数 → 保留 2 个自由指数（常规选流速与比热的指数 $b,e$），解出其余 5 个，组装成 3 个无量纲群：
$$\frac{qD}{Ak\Delta T}=\Phi\!\left(\frac{D\bar V\rho}{\mu},\frac{c_p\mu}{k}\right)$$
即 Nusselt 数 = Φ(Reynolds 数， Prandtl 数)——第 12 章传热关联式的由来。方法论要点：①各群可自由乘除、取倒数重组（每群至少用一次、总数不变），如左乘 $\frac{\mu}{D\bar V\rho}\frac{k}{\mu c_p}$ 得 Stanthon 数形式 $q/(A\bar V\rho c_p\Delta T)$，以便隔离单个物性；②自由指数的选取只改变群的具体形态，不改变结论；③分析是"推测性"的——变量选错要么被淘汰、要么只在渐近极限下有效。

## Anti-patterns
- **在 fps 计算中遗漏 $g_c$**：lb 与 lb$_f$ 量纲不同，$F=d(mu)/dt/g_c$ 少除 32.174 会得到 32 倍错误；SI/cgs 中 $k_1=1$ 无此因子，切勿把"SI 习惯"带进英制。
- **对经验（dimensional）方程换单位却保留原系数**：式 1.41 的 0.50 只在 Btu/h、ft²、°F、in. 下成立；温差改用 °C 必须乘 $1.8^{1.25}$ 改系数。
- **量纲分析变量选多或选漏**：多余变量通常自动消去（无害但浪费），漏掉关键变量则所得关联只在极限区有效——结果须用实验验证。
- **把摩擦当能量衡算的独立项**：式 1.59 无摩擦项，摩擦是控制面内机械能变热，已被焓与热项吸收；另设"摩擦损失"项会重复计算。
- **忽略 Q 与 W_s 的符号约定**：热流入控制面为正、设备对外做功为正；泵功为负值代入，符号弄反直接翻转结果。

## Key Takeaways
- 任何物理量 = 数值 × 单位，两者缺一不可；三套单位制（SI/cgs/fps）并存是现实，工程师必须都熟练。
- 求换算因子时只用精确定义推导（如 9.80665/0.3048 代替 32.1740 参与运算），可保留最大精度并利用约分。
- 量纲齐次方程 + 一致单位 = 免换算因子；遇到含换算系数的公式先确认其绑定单位。
- 量纲分析的价值：把逐变量实验（7 个变量）压缩为 3 个无量纲群的关联实验；它是设计实验计划的工具，不是理论。
- 能量衡算五要素：划控制面、认全进出口、认全轴、定 Q 与 W_s 符号、记住摩擦内含不单列。
- 低压气体用理想气体律即可（z≈1）；压力升高按需引入维里系数。

## Connects To
- **Ch. 2–9（流体力学篇）**：能量衡算式 1.59 是伯努利/机械能衡算（Ch. 4）的母体；量纲分析产出的 Re 数贯穿 Ch. 3–8。
- **Ch. 12（无相变传热）**：Example 1.2 推出的 Nu = Φ(Re, Pr) 在该章落地为具体关联式（Dittus-Boelter 等）。
- **外部**：热力学（Smith, Van Ness & Abbott）展开焓与第一定律；附录 1 换算因子表、附录 2 命名无量纲群表供全书查阅。
