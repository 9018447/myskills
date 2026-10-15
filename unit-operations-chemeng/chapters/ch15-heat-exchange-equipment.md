# Chapter 15: Heat-Exchange Equipment

## Core Idea
本章把 Ch11–14 的原理落成设备：以 $q=UA\overline{\Delta T}$ 为骨架，讨论管壳式/板式/翅片/刮面/冷凝蒸发/搅拌槽/填料床等结构的选型逻辑——核心矛盾始终是"高流速→高系数小面积"与"高压降高泵耗"的权衡，且 LMTD 在多程/错流设备中必须乘修正因子 $F_G$。

## Frameworks Introduced
- **Shell-and-tube（TEMA 标准）**：1-1、1-2、2-4 程数组合；25% 圆缺挡板（cut = 壳径 1/4），挡板间距取壳径 1/5～1 倍；三角形排列面积密（不可机械清洗）、正方形排列可清洗且壳程压降低（TEMA：三角 pitch ≥1.25 D_o，方排清洗道 ≥1/4 in）。
- **LMTD correction factor $F_G$**：多程/错流设备真实平均温差 = F_G × 逆流 LMTD；由 Z（热流体温降/冷流体温升）与 η_H（加热有效度）查图。**Use F_G when exchanger has mixed parallel-counterflow sections.**
- **Donohue equation（壳程系数）**：以加权平均质量流速 $G_e=\sqrt{G_bG_c}$（错流与窗口流几何平均）关联 h_o，结果偏保守低。
- **Number of heat-transfer units $N_H$ + effectiveness ε**：$N_H=UA/(\dot m c_p)$，ε=实际温变/最大可能温变；1-1 逆流可免试差直接查 ε–N_H 图（参数 R_c）。
- **Fin efficiency $\eta_F$**：翅片面平均温压与裸管温压之比；参数 $a_Fx_F$（$a_F=\sqrt{h_oP/S/k_m}$），$a_Fx_F<0.5$ 时 η_F≈1。
- **Scraped-surface coefficient**：把刮削周期视为对半无限固体的非稳态导热，$h_i=2\sqrt{k\rho c_p nB/\pi}$——h 取决于热物性与转速×叶片数，近似与黏度无关。
- **Agitated-vessel correlations**：涡轮桨盘管式 Eq. 15.25、夹套式 Eq. 15.26（$h_jD_t/k=0.76N_{Re,a}^{2/3}Pr^{1/3}(\mu/\mu_w)^{0.24}$）、锚式分段 Eq. 15.27。
- **Packed-bed coefficients**：管内系数分解为床层 $h_{bed}=4k_e/r$（$k_e/k_g\approx5+0.1Re_pPr$）与近壁 $h_w$（$\mathrm{Nu}_w=1.94Re_p^{0.5}Pr^{0.33}$）两阻力串联。
- **Regenerator analysis**：有效 U 由两侧膜系数串联，性能由 $N_H=UA/C$ 与容量比 $R_R=C_R/C$（$C_R=mc_s/t$）决定。

## Key Concepts
- **1-2 exchanger（1-2 换热器）**：单壳程+双管程，首程并流末程逆流；保证标准管长下高流速，但并流段限制接近温度、热回收先天不足。
- **2-4 exchanger**：双壳程+四管程（加纵向挡板），性能逼近真逆流，同流量下 U 更高。
- **Floating head（浮头）**：管板一端与壳体结构解耦，吸收热膨胀差，避免管子失稳或拉脱；高压换热器常用。
- **Baffle window（挡板窗口）**：壳截面未被挡板遮挡的部分，窗口流面积 $S_b$ 决定平行流质量流速 G_b。
- **ROD baffle exchanger**：用 1/4 in 杆代替板式挡板（四向支承每根管），壳流以轴向为主——低压降、抗振动，湍流系数 ≈ Dittus-Boelter 预测的 1.5 倍。
- **Plate exchanger（板式换热器）**：波纹板+垫片夹紧，板距 2–5 mm；波纹使 Re≈100–400 即呈湍流特性；水-水清洁 U 达 3000–6000 W/m²·K，污垢低（设计仅加 10% 面积），易拆洗；上限约 200 °C、25 atm。
- **Extended surface（扩展表面）**：当一侧系数远低（如空气 vs 冷凝蒸汽，h 比 100–200 倍）时用翅片扩大该侧面积，把 $A_i/A_oh_o$ 阻力项压小。
- **Contact condenser（接触式冷凝器）**：冷却水与蒸气直接混合冷凝，小而便宜，但产物是混合液（不能回收纯净冷凝液）。
- **Barometric leg（大气腿）**：约 10 m 竖管靠液柱静压平衡真空，使冷凝液自流排出而不破坏真空。
- **Regenerator（蓄热器）**：冷热流体交替通过蓄热固体床传热；单位体积面积大、便宜、易清理；不适合液体（孔隙液体热容与固体相当）；旋转式广泛用于电厂空气预热。
- **Runaway（飞温）**：放热反应填料管总系数过低导致床温失控——填料管传热设计的首要风险。

## Key Equations
- LMTD 修正：$\overline{\Delta T}=F_G\cdot\overline{\Delta T}_L$，其中
$$Z=\frac{T_{ha}-T_{hb}}{T_{cb}-T_{ca}},\qquad \eta_H=\frac{T_{cb}-T_{ca}}{T_{ha}-T_{ca}}$$
Z：热流温降/冷流温升之比；η_H：冷流实际温升/逆流最大可能温升。
- 多程判据：$F_G<0.8$ 须重设计（增加壳程数或加大温差）；$F_G<0.75$ 后曲线陡降，操作极敏感。
- Donohue 壳程方程：
$$\frac{h_oD_o}{k}=0.2\left(\frac{D_oG_e}{\mu}\right)^{0.6}\left(\frac{c_p\mu}{k}\right)^{0.33}\left(\frac{\mu}{\mu_w}\right)^{0.14},\quad G_e=\sqrt{G_bG_c}$$
h_o：壳程系数；D_o：管外径；G_e：加权质量流速。
- 传热单元数与有效度：
$$N_H=\frac{T_{cb}-T_{ca}}{\overline{\Delta T}_L}=\frac{UA}{\dot m_cc_{pc}},\qquad \varepsilon=\frac{T_{cb}-T_{ca}}{T_{ha}-T_{ca}}$$
- 两个极限：一侧恒温（蒸汽加热）$\varepsilon=1-e^{-N_H}$；两侧容量相等 $\varepsilon=N_H/(1+N_H)$。
- 翅片管总系数（基于内表面积）：
$$U_i=\frac{1}{A_i/[h_o(\eta_FA_F+A_b)]+x_wD_i/(k_m\bar D_L)+1/h_i}$$
A_F：翅片面积；A_b：裸管面积；η_F：翅片效率；x_w：壁厚；$\bar D_L$：对数平均直径。
- 刮面式：$h_i=2\sqrt{k\rho c_pnB/\pi}$（k 导热系数，ρ 密度，c_p 比热，n 转速，B 叶片数）。
- 搅拌槽夹套（标准涡轮）：$\frac{h_jD_t}{k}=0.76\left(\frac{D_a^2n\rho}{\mu}\right)^{2/3}\left(\frac{c_p\mu}{k}\right)^{1/3}\left(\frac{\mu}{\mu_w}\right)^{0.24}$
- 批式瞬态加热（恒温热介质）：
$$\ln\frac{T_s-T_a}{T_s-T_b}=\frac{UAt_T}{mc_p}$$
T_s：介质温度；T_a→T_b：液温初末值；t_T：时间。
- 填料管：$\frac1{h_i}=\frac1{h_{bed}}+\frac1{h_w}$；$h_{bed}=4k_e/r$（r：管半径）；$k_e/k_g\approx5+0.1Re_pPr$；$\mathrm{Nu}_w=h_wD_p/k_g=1.94Re_p^{0.5}Pr^{0.33}$。

## Reference Tables
| 设计量 | 经验值/规则 |
|---|---|
| 挡板间距（baffle pitch） | 壳内径的 1/5 ～ 1 倍 |
| 三角形排列最小管心距 | 1.25 × 管外径 |
| 四程 vs 单程（同管数同流量） | 流速 ×4，h ×4^0.8≈3.03，总摩擦 ×4^2.8≈48.5 |
| 板式换热器 U（水-水清洁） | 3000–6000 W/m²·K |
| 板式污垢裕量 | 计算面积 +10% |
| 翅片管空气冷却极限 | 冷至高于空气干球温度约 20 °C；翅片面积倍数 7–20 |
| 填料管最佳粒径比 | $D_p/D_i\approx0.15$–0.2（h_i 峰值）；裸管的 5–10 倍 |
| 再生器容量比 | $R_R=1.5$–5 |
| $F_G$ 设计红线 | <0.8 重设计；<0.75 操作敏感区 |

## Worked Example
**例 15.1–15.2（LMTD 修正）**：1-2 换热器，T_ca=70、T_cb=120、T_ha=240、T_hb=120 °C。η_H=(120−70)/(240−70)=0.294，Z=(240−120)/(120−70)=2.4，查图 F_G=0.82；两端温差 120/50 °C → 逆流 LMTD=80 °C；真实平均 ΔT=0.82×80=**66 °C**。同工况换 2-4：F_G=0.96 → 77 °C。教训：程数越多越接近真逆流，F_G 越接近 1。
**例 15.4（N_H–ε 法免试差）**：油 110 °C 在 1-1 逆流换热器中回收热量，UA=1.65×10⁷ W/°C，热流容量率 6.9×10⁶ W/K，R_c=0.688 → N_H=2.39，查图 ε≈0.78 → 油出口 110−0.78×85=43.7 °C；再校核 Q=UAΔT_L 一致。

## Anti-patterns
- **多程换热器直接用逆流 LMTD**：必须乘 F_G；忽略修正会高估 10–35% 的平均温差，设备面积严重不足。
- **把 F_G 压到 0.7 以下硬凑面积**：该区 η_H 微小波动引起 F_G 陡降，且挡板泄漏使"均匀热历史"假设失效，设备可能不可操作。
- **壳程系数用管内公式（Dittus-Boelter）硬算**：壳程流向混合、截面变化、挡板泄漏短路，必须用 Donohue/ Bell-Delaware 类专门关联式。
- **在高 h_o 一侧加翅片**：翅片应加在系数低的一侧；h_o 大时翅片既无必要又增大压降。同时核查 η_F——细高翅片 ($a_Fx_F$>1) 面积虚增而效率大跌。
- **刮面式公式当万能式用**：Eq. 15.23 忽略了叶片后再沉积与纵向流速影响，对高黏液体预测偏高；大型低速机组用经验式 15.24 或实验数据。
- **敞口夹套按对数平均温差算**：敞口夹套流速 <0.1 ft/s，近自然对流且夹套内充分混合，ΔT 应用出口温差而非 LMTD。
- **忽略填料床的粒径比优化**：D_p/D_i 太小则床芯阻力控制（似层流剖面），太大则近壁大空隙率区控制；约 0.15–0.2 最优。

## Key Takeaways
- 换热器设计的普适流程：能量平衡定 Q → 算 U 与修正 LMTD → 定面积；最终设计是面积投资与泵送能耗的折中，且应在换热网络层面优化而非单台。
- 管壳式选型口诀：要清洗用方排、要紧凑用三角排；振动/压降敏感选 ROD baffle；需要高回收温度选 2-4。
- $N_H$ 与 ε 是比 LMTD 更直接的绩效语言：N_H=3 时一侧恒温介质可消去 95% 温差，等容量介质达 75%。
- 多程损失用 F_G 量化；壳程数增加（管程=2×壳程）单调逼近真逆流。
- 刮面式把传热变成"转速问题"：h ∝ √(nB)，是处理热敏、高黏物料的默认答案。
- 批式搅拌槽加热用 $\ln[(T_s-T_a)/(T_s-T_b)]=UAt/mc_p$ 即可反算 U 或预测加热时间——最常用的现场标定方程。
- 填料反应管传热：先算 k_e→h_bed，再加壁膜 h_w，串联得 h_i；>200 °C 时颗粒间辐射不可忽略。

## Connects To
- **Ch11–12**：q=UAΔT 框架与 LMTD、Dittus-Boelter 管内系数是本章公式模块的输入；F_G 图源自 Bowman-Mueller-Nagle。
- **Ch13**：kettle 再沸器、热虹吸/自然循环 calandria 与膜态沸腾细节在本章只作结构描述。
- **Ch16**：刮面式与搅拌传热方法延伸到蒸发器设计。
- **Ch17/Ch25**：填料床气-固传热/传质类比（j 因子）；蓄热器结构与吸附-脱附双床系统同构。
- **外部**：TEMA 标准、ASME 压力容器规范是制造与机械设计的权威依据。
