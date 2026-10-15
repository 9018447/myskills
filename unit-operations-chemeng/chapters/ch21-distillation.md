# Chapter 21: Distillation

## Core Idea
二元连续精馏的完整设计法：闪蒸（单级平衡）只是起点，回流才是实现高纯分离的手段；在恒摩尔流假设下用 McCabe-Thiele 图（两条操作线 + q 线 + 平衡线）数出理想板，再用 Fenske/最小回流约束与板效率、塔板水力学把设计落到实际塔。

## Frameworks Introduced
- **Flash distillation（闪蒸）**：进料部分汽化 f，汽液平衡分离；物料平衡线 $y = -\frac{1-f}{f}x + \frac{x_F}{f}$ 恒过对角线 $(x_F, x_F)$，与平衡曲线交点即产品组成。适合沸点差大的体系（炼油管式炉+闪蒸）。
- **McCabe-Thiele method（完整版）**：精馏段操作线（斜率 $R_D/(R_D+1)$，截距 $x_D/(R_D+1)$，恒过对角线 $(x_D,x_D)$）+ q 线（feed line）+ 汽提段操作线（过 $(x_B,x_B)$ 与两线交点）间阶梯作图。
- **q-line（feed line）/q 值**：q=每 mol 进料带入汽提段的液体 mol 数；五类进料统一刻画；q 线方程 $y = -\frac{q}{1-q}x + \frac{x_F}{1-q}$，恒过 $(x_F,x_F)$。
- **Fenske equation**：全回流最小板数（α 恒定的理想体系）。
- **Minimum reflux & pinch point（invariant zone）**：操作线触及平衡线处板数→∞；正常凹形平衡曲线在 q 线与平衡线交点相触，反常上凹曲线（如乙醇-水）由切线决定。
- **Optimum reflux ratio**：总成本（蒸汽约占总年费 2/3）最低点，约 $(1.1\text{–}1.3)\,R_{Dm}$；实际操作常略高于最优值换灵活性。
- **Enthalpy-balance method**：取消恒摩尔流假设，用焓-浓图逐点解出微弯操作线（关键判据：局部斜率≠局部 L/V，L/V 是连接 $(x_D,x_D)$ 的弦斜率）。
- **Sieve-tray hydraulics**：压降 $h_t = h_d + h_l$；漏液下限/液泛上限间约 3–4 倍操作弹性（valve tray 可达 10 倍以上）；Fair 液泛关联式与 F 因子。
- **Plate efficiencies**：全塔效率 $\eta_o$、Murphree 效率 $\eta_M$、点（局部）效率 $\eta'$ 三层结构及换算。
- **Rayleigh equation**：简单Batch蒸馏的微分物料衡算。

## Key Concepts
- **Constant molal overflow（恒摩尔流）**：相邻组分摩尔汽化潜热近似相等 → 各段内 L、V 近似恒定，操作线为直线；这是二元图解法可行的核心假设。
- **Reflux ratio $R_D = L/D$**：回流与塔顶产品摩尔比（本书约定）；决定操作线斜率与能耗。
- **Total condenser vs partial condenser**：全凝器不分级；分凝器中汽液互成平衡，相当于额外一块理论板。
- **Partial reboiler**：釜气与釜液平衡，本身算一块理论板。
- **q（进料热状态）**：冷进料 q>1；泡点液体 q=1；部分汽化 0<q<1（q=液相分率=1−f）；露点蒸气 q=0；过热蒸气 q<0。
- **Optimum feed plate**：进料板阶梯应"骑跨"两操作线交点；错位进料使部分板工作在夹紧区、几乎不分离。
- **Weeping / Entrainment / Flooding**：气速过低液体从孔口漏下；气速过高雾沫夹带降低效率；降液管泡沫高度达板间距即液泛。
- **Murphree efficiency $\eta_M$**：实际气相增浓 / 与离板液体平衡时应有增浓；板间液体完全混合时 $\eta_M = \eta'$；大塔液体存在浓度梯度，$\eta_M$ 可超 100%。
- **F factor**：$F = u\sqrt{\rho_V}$，筛板正常范围 1–3 (m/s)(kg/m³)^0.5；低压操作效率下降（气膜阻力占比更高）。
- **HETP**：填料塔的当量理论板高度；1.5–2 in 散装填料典型 1–2 ft ≈ $H_{Oy}$，每 3–4 m 设液体再分布器。

## Key Equations
- 全塔衡算：$F = D + B$，$F x_F = D x_D + B x_B$ → $\dfrac{D}{F} = \dfrac{x_F - x_B}{x_D - x_B}$
- 精馏段操作线：$y_{n+1} = \dfrac{R_D}{R_D + 1} x_n + \dfrac{x_D}{R_D + 1}$
- 汽提段操作线：$y_{m+1} = \dfrac{\bar L}{\bar V} x_m - \dfrac{B x_B}{\bar V}$（斜率恒 >1）
- q 线：$y = -\dfrac{q}{1-q}x + \dfrac{x_F}{1-q}$；冷液 $q = 1 + \dfrac{c_{pL}(T_b - T_F)}{\lambda}$；过热汽 $q = -\dfrac{c_{pV}(T_F - T_d)}{\lambda}$
- 相对挥发度：$\alpha_{AB} = \dfrac{y_A/x_A}{y_B/x_B} = P_A'/P_B'$（理想体系），$y_e = \dfrac{\alpha_{AB} x_e}{1 + (\alpha_{AB}-1)x_e}$
- **Fenske equation**：$N_{\min} = \dfrac{\ln\left[x_D(1-x_B)/x_B(1-x_D)\right]}{\ln \alpha_{AB}} - 1$（α 变化适中时取两端几何平均）
- **最小回流比**（正常平衡曲线）：$R_{Dm} = \dfrac{x_D - y'}{y' - x'}$，$(x', y')$ 为 q 线与平衡曲线交点
- 冷回流内凝量：$\Delta L = \dfrac{L_c c_{pc}(T_1 - T_c)}{\lambda_c}$
- 再沸器蒸汽/冷凝水：$\dot m_s = \bar V \lambda/\lambda_s$；$\dot m_w = V\lambda/(T_2 - T_1)$
- 筛板压降：$h_t = h_d + h_l$，$h_d = 51.0\,\dfrac{u_0^2}{C_0^2}\dfrac{\rho_V}{\rho_L}$（mm 液柱，$C_0 \approx 0.66\text{–}0.72$）；$h_l = \beta(h_w + h_{ow})$（β≈0.6），Francis 式 $h_{ow} = 43.4(q_L/L_w)^{2/3}$ mm
- 降液管清液高：$Z_c = 2\beta(h_w + h_{ow}) + h_d + h_{f,L}$；泡沫高 $Z = Z_c/\phi_d$（保守取 $\phi_d = 0.5$），Z ≥ 板间距即液泛
- **Fair 液泛关联**：$u_c = K_v\sqrt{\dfrac{\rho_L - \rho_V}{\rho_V}}\left(\dfrac{\sigma}{20}\right)^{0.2}$（$K_v$ 查图，随板间距与 $L/V\sqrt{\rho_V/\rho_L}$ 变化）
- Murphree 效率：$\eta_M = \dfrac{y_n - y_{n+1}}{y_n^* - y_{n+1}}$；等效平衡曲线 $y_e' = y + \eta_M(y_e - y)$
- 直线体系效率换算：$\eta_o = \dfrac{\ln[1 + \eta_M(mV/L - 1)]}{\ln(mV/L)}$
- 点效率与传质单元：$1 - \eta' = e^{-N_{Oy}}$（低黏液体 $N_{Oy} \approx 1.5\text{–}2$）
- **Rayleigh equation**：$\ln\dfrac{n_1}{n_0} = \displaystyle\int_{x_0}^{x_1}\frac{dx}{y - x}$；理想体系捷径 $\ln\dfrac{n_A}{n_{0A}} = \alpha_{AB}\ln\dfrac{n_B}{n_{0B}}$

## Reference Tables
| 进料状态 | q | q 线斜率 $-q/(1-q)$ | q 线方向 |
|---|---|---|---|
| 冷液体 | >1 | >0 | 右上倾 |
| 泡点液体 | 1 | ∞ | 垂直 |
| 部分汽化 | 0<q<1 | <0 | 左上倾 |
| 露点蒸气 | 0 | 0 | 水平 |
| 过热蒸气 | <0 | 0<斜率<... 负 q 使斜率为正小值 | 左下倾 |

| 板型 | 操作弹性（turndown） | 特点 |
|---|---|---|
| 筛板 sieve tray | 3–4 倍 | 便宜、低压降、孔径 5–12 mm |
| 浮阀板 valve tray | ≥10 | 大弹性、稍贵 |
| 填料（1.5–2 in 散装） | 与筛板容量相当 | HETP 1–2 ft，低压降，宜真空 |
| 丝网/规整填料 | 3–4 倍流量范围 HETP 恒定 | HETP 低至 0.1–0.2 m |

## Worked Example
**Ex. 21.2（苯-甲苯塔设计，全书模板题）**：30,000 kg/h、40/60 wt% 苯/甲苯 → 馏出液 97% 苯、釜液 98% 甲苯，$R_D = 3.5$。(a) 换算摩尔分数 $x_F=0.440$、$x_D=0.974$、$x_B=0.0235$，物料衡算 D=153.4、B=196.6 kgmol/h。(b) 泡点进料：q 线垂直，截距 $0.974/4.5=0.216$，得 11 块理想板+再沸器、第 7 板进料；20°C 冷进料 q=1.37（q 线斜率 3.70）→ 10 板+再沸器、第 6 板；2/3 汽化进料 q=1/3 → 12 板、第 7 板——部分汽化进料板数更多，主因是给汽提段的液体少、该段回流比变小。(c) 蒸汽用量 $\dot m_s = 15.25[690 - 350(1-q)]$ kg/h：冷进料 12,500 最多、部分汽化 6,960 最少；三例总能耗接近。(d) 冷却水 366,160 kg/h ≈ 367.5 m³/h，与 q 无关。

（Ex. 21.6 水力学：由 Fair 图定 $u_c = 2.23$ m/s → 塔径 2.27 m；孔速 22.1 m/s、$h_d = 71.7$ mm；$h_l = 0.6(50.8+17.0)=40.7$ mm；降液管泡沫高 326 mm < 板间距 457 mm。Ex. 21.8：渗透理论估计苯-甲苯 1 atm 下气膜占总阻力 ~90%，0.25 atm 时升至 94%、点效率 86%→83%。）

## Anti-patterns
- **把最优进料板位置选在两操作线交点之前/之后很远**：板数明显增多，板工作在夹紧区；设计应让进料板阶梯骑跨交点，实际塔则预留几个备用进料口。
- **对上凹平衡曲线（乙醇-水类）用 q 线交点求 $R_{Dm}$**：此时精馏操作线先在别处切平衡曲线，必须由切线斜率定最小回流。
- **把曲线上任一点的局部斜率当作当地 L/V**：只有直线操作线才有该等式；弯线时 L/V 是弦斜率（Eq. 21.56–21.57）。
- **忽略 q 对两段流量分配的影响**：泡点进料 $\bar L = L + F$、冷进料还要内凝额外蒸汽；用 V 代替 $\bar V$ 算再沸器负荷会错。
- **把再沸器/分凝器也打效率折扣**：部分再沸器与分凝器本身就是理论级，不参与效率折减。
- **$\eta_M$ 与 $\eta_o$ 混用**：二者只在 $mV/L=1$ 或 $\eta_M\approx1$ 时相等；汽提段 $\eta_o > \eta_M$、精馏段 $\eta_o < \eta_M$，验算实际塔应试差求 $\eta_M$。
- **设计点贴着液泛或漏液边界**：夹点区效率骤降（夹带）、漏液区液体短路；筛板正常 F 因子 1–3 之间且远离两端。

## Key Takeaways
1. 无回流得不到超过一次平衡的分离；产品纯度上限由板数与回流比共同决定——$R_{Dm}$（板→∞）与全回流 $N_{\min}$（Fenske）是两个设计锚点。
2. McCabe-Thiele 标准作图顺序：定 $x_D, x_F, x_B$ → q 线 → 精馏线（截距 $x_D/(R_D+1)$）→ 汽提线（过 $(x_B,x_B)$ 与交点）→ 阶梯；进料板取骑跨交点的阶梯。
3. 恒摩尔流假设的物理依据是潜热相近（Trouton 规则）；近 $R_{Dm}$ 操作或潜热差大时需焓衡算法修正（板数可差 20–30%）。
4. 塔径由液泛气速定（Fair 式，$u_c \propto \sqrt{(\rho_L-\rho_V)/\rho_V}$，高压塔因 $\rho_V$ 大而更矮胖）；压降校核防漏液，降液管清液高（$Z_c$ 式中堰高计两次）防液泛。
5. 筛板点效率由 $N_{Oy}\approx1.5\text{–}2$ 支撑（约 80%），气膜控制；降压使 $k_y$ 降、效率降——真空精馏别沿用常压效率数据。
6. q 是进料热状态的单一参数：它同时决定 q 线方向、两段流量比与再沸器负荷；冷进料省板数费蒸汽，部分汽化反之。
7. 间歇蒸馏两种操作策略：恒 $x_D$ 渐增 $R_D$，或恒 $R_D$ 让 $x_D$ 随时间衰减；理想体系用 α 短式直算残余量。

## Connects To
- **Ch. 20**：操作线-平衡线阶梯框架与 Kremser 式的直接推广（近纯端两线皆直时仍可用解析式）。
- **Ch. 22**：多组分无图解法，改用 Fenske-Gilliland-Underwood 或严格逐板计算。
- **Ch. 17 / 18**：点效率的 $N_{Oy}$ 与双膜阻力分配；$H_{Oy}$ 与填料 HETP 的对应。
- **Ch. 8**：筛板孔口压降的孔板系数来源。
- **Ch. 15**：再沸器/冷凝器属换热设备，热负荷计算同源。
