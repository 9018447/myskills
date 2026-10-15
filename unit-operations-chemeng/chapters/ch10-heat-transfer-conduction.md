# Chapter 10: Heat Transfer by Conduction

## Core Idea
导热的基本定律是 Fourier 定律（热通量正比于温度梯度），本章把它应用到三类问题：**平壁/圆筒壁稳态导热（热阻串联）**、**恒壁温或对流边界下的非稳态导热（Fo/Bi 数解）**、**半无限固体的穿透导热**。核心工具是把传热写成"速率 = 推动力/阻力"的一般形式。

## Frameworks Introduced
- **Fourier 定律**：$dq/dA=-k\,dT/dx$；三维各向同性形式 $\vec q/A=-k\nabla T$，热沿温度下降最陡方向流动。Use for any conduction flux calculation.
- **热阻串联（series resistances）**：多层平壁 $q/A=\Delta T/\sum(B_i/\bar k_i)$；温度降按各层热阻比例分配（电网络类比：ΔT ↔ 电压，q ↔ 电流）。
- **对数平均半径 $\bar r_L=(r_o-r_i)/\ln(r_o/r_i)$**：把平壁公式用于厚壁圆筒的等效面积修正。Use when $r_o/r_i>1.4$；比 <1.4 时算术平均误差 <1%。
- **Fourier 数 Fo $=\alpha t_T/s^2$**：无量纲时间，非稳态导热的自变量。
- **Biot 数 Bi $=hs/k$（平板）或 $hr_m/k$（球/柱）**：外部对流阻力与内部导热阻力之比，决定用哪套解（Bi→∞ 退化为恒壁温解）。
- **热扩散率 $\alpha=k/\rho c_p$**：材料内温度扰动的传播速率，量纲 m²/s——导热版的"动量扩散系数"。
- **半无限固体解（概率积分/Gauss error integral）**：$Z=x/2\sqrt{\alpha t}$，穿透距离 $x_p=3.64\sqrt{\alpha t}$（温度变化 1% 处的定义）。

## Key Concepts
- **热导率 k**：输运性质（与黏度 μ 类比）；金属 17–415 W/m·°C（合金低于纯金属、随温度略降），非多孔固体 0.35–3.5，液体 ≈0.17（水例外 0.5–0.7 且有极大值），气体低至 0.007（≈与压力无关至 10 bar）。
- **平均热导率 $\bar k$**：k 随温度线性变化时，取两侧面温度的算术平均温度查 k，公式形式不变且严格成立。
- **接触热阻（contact resistance）**：层间接触不良引入附加热阻（如 0.088 °C·m²/W 量级），串联叠加即可。
- **未完成温度变化分数 $(T_s-\bar T_b)/(T_s-T_a)$**：非稳态导热的无量纲因变量，三种标准形状（无限平板、无限长圆柱、球）各有级数解/图。
- **低 Bi 近似**：Bi 小时外部阻力为主，固体用有效内系数（球 5k/r_m、长圆柱 3k/r_m、平板 2k/s），整体写成集总 U 方程。
- **绝热材料原理**：多孔材料（玻璃纤维、泡沫）靠截留空气消除对流获得低 k；闭孔泡沫充高分子气体可低于空气的 k。

## Key Equations
- 平壁稳态导热（$B$=壁厚，$\bar k$=平均热导率）：
$$\frac{q}{A}=\bar k\,\frac{\Delta T}{B}=\frac{\Delta T}{R},\qquad R=\frac{B}{\bar k}$$
- 多层平壁串联：
$$\frac{q}{A}=\frac{\Delta T}{B_A/\bar k_A+B_B/\bar k_B+B_C/\bar k_C},\qquad \frac{\Delta T}{R}=\frac{\Delta T_A}{R_A}=\frac{\Delta T_B}{R_B}=\cdots$$
- 厚壁圆筒：
$$q=\frac{k(2\pi L)(T_i-T_o)}{\ln(r_o/r_i)}=\frac{k\bar A_L(T_i-T_o)}{r_o-r_i},\qquad \bar A_L=2\pi L\,\bar r_L,\quad \bar r_L=\frac{r_o-r_i}{\ln(r_o/r_i)}$$
- 一维非稳态导热方程（$c_p$=比热容，$\rho$=密度）：
$$\frac{\partial T}{\partial t}=\alpha\frac{\partial^2T}{\partial x^2},\qquad \alpha=\frac{k}{\rho c_p}$$
- 无限平板（半厚 $s$，恒壁温 $T_s$，Fo>0.1 只取首项）：
$$\frac{T_s-\bar T_b}{T_s-T_a}=\frac{8}{\pi^2}e^{-(\pi/2)^2\,\mathrm{Fo}},\qquad t_T=\frac{1}{\alpha}\Big(\frac{2s}{\pi}\Big)^2\ln\frac{8(T_s-T_a)}{\pi^2(T_s-\bar T_b)}$$
- 无限长圆柱（半径 $r_m$）：$(T_s-\bar T_b)/(T_s-T_a)=0.692e^{-5.78\,\mathrm{Fo}}$；球：$=0.608e^{-9.87\,\mathrm{Fo}}$。
- 对流边界（Newton 冷却定律匹配固体内导热，$h$=表面传热系数）：
$$h(T_f-T_s)=-k(\partial T/\partial x)_{x=0},\qquad \mathrm{Bi}=\frac{hs}{k}\ \text{或}\ \frac{hr_m}{k}$$
- 低 Bi 集总解（球）：
$$\frac{1}{U}\cong\frac{1}{h}+\frac{r_m}{5k},\qquad \ln\frac{T_f-\bar T_b}{T_f-T_a}=-\frac{3Ut}{\rho c_p r_m}$$
（长圆柱把 3 换 2、$r_m/5$ 换 $r_m/3$；平板换成 $1/s$ 与 $2k/s$）
- 累计传热量：平板 $Q_T/A=s\rho c_p(\bar T_b-T_a)$；圆柱 $\div2$；球 $\div3$。
- 半无限固体：
$$\frac{T_s-T}{T_s-T_a}=\frac{2}{\sqrt\pi}\int_0^Z e^{-Z^2}dZ,\quad Z=\frac{x}{2\sqrt{\alpha t}};\qquad x_p=3.64\sqrt{\alpha t}$$
$$\Big(\frac{q}{A}\Big)_{x=0}=\frac{k(T_s-T_a)}{\sqrt{\pi\alpha t}},\qquad \frac{Q_T}{A}=2k(T_s-T_a)\sqrt{\frac{t_T}{\pi\alpha}}$$

## Reference Tables
| 导热系数量级 | k, W/m·°C | 温度行为 |
|---|---|---|
| 银/铜 | 415/380 | 随温度略降 |
| 软钢/不锈钢 | 45/17 | 近似恒定或略降 |
| 玻璃等非多孔固体 | 0.35–3.5 | 可升可降 |
| 一般液体 | ≈0.17 | 每升 10°C 降 3–4% |
| 水 | 0.5–0.7 | 有极大值（例外） |
| 空气（0°C） | 0.024 | 单原子 ∝T^0.5 |

| 形状 | 有效内部系数（低 Bi） | 累计热 Q_T/A | Fo 定义 | 首项系数 |
|---|---|---|---|---|
| 平板（半厚 s） | 2k/s | $s\rho c_p\Delta T$ | $\alpha t/s^2$ | $(8/\pi^2)e^{-(\pi/2)^2Fo}$ |
| 长圆柱（r_m） | 3k/r_m | $r_m\rho c_p\Delta T/2$ | $\alpha t/r_m^2$ | $0.692e^{-5.78Fo}$ |
| 球（r_m） | 5k/r_m | $r_m\rho c_p\Delta T/3$ | $\alpha t/r_m^2$ | $0.608e^{-9.87Fo}$ |

## Worked Example
**例 10.2（串联热阻+界面温度）**：4.5 in 硅藻土砖（k=0.08）+9 in 普通砖（k=0.8），内外面 1400/170°F。$R_A=4.687$、$R_B=0.938$（°F·h·ft²/Btu），$q=1230/5.625=219$ Btu/h·ft²；界面温度按电阻分压：$\Delta T_A=1230\times4.687/5.625=1025°F$ → 界面 375°F。若加 0.5 接触热阻，q 降至 201 Btu/h·ft²。要点：最薄但 k 最低的层往往主导总阻力。

**例 10.6（半无限固体）**：寒潮使地表骤降至 −20°C 持续 12 h，土壤 α=0.0011 m²/h。(a) 管道不冻深度：$(T_s-T)/(T_s-T_a)=0.80$ → 查图 Z=0.91 → $x=0.91\times2\sqrt{\alpha t}=0.21$ m；(b) 穿透距离 $x_p=3.64\sqrt{0.0011\times12}=0.42$ m。

## Anti-patterns
- **厚壁圆筒用算术平均面积**：$r_o/r_i=2$ 时误差已达 4%，绝缘层 routinely 超过该比值，必须用对数平均。
- **k 随温度明显变化时仍用单点 k**：应取两侧面算术平均温度下的 $\bar k$（k 线性变化时严格）。
- **Bi<0.1 却用恒壁温级数解**：外部膜阻不可忽略时表面温度随时间变，需用 Heisler 图（Fo+Bi 双参数）或低 Bi 集总法。
- **对 Fo<0.1 只取级数首项**：初期首项不占优，短时结果严重偏差；早期或要用完整级数/半无限解。
- **把"穿透距离"当温度不变的绝对边界**：$x_p$ 只是变化 <1% 的工程约定，不是物理间断。
- **忽略夹层中的薄空气隙**：几 mm 空气隙的热阻可相当于几十 cm 的低 k 砖层（习题 10.1 的要点）。

## Key Takeaways
- 一切稳态导热设计先画热阻网络：串联相加、温度降按电阻分压；识别主导阻力层再决定加/减哪层。
- 圆筒导热用对数平均半径；$r_o/r_i<1.4$ 才可偷懒用算术平均。
- 非稳态问题先算 Bi 决定边界类型，再算 Fo 查图/式：Bi→∞ 用恒壁温解；Bi 小用集总 U 法（球内阻 $r_m/5k$）。
- 三种标准形状冷却快慢排序：同 Fo 下球最快、圆柱次之、平板最慢（表面积/体积比更大）。
- 半无限固体的通用尺度：穿透深度 $\propto\sqrt{\alpha t}$；表面瞬时热流 $\propto1/\sqrt t$。
- 热扩散率 α 而非 k 决定非稳态响应速度——气体 k 小但 α 与金属同量级（密度小补偿）。

## Connects To
- **Ch. 11–13**：对数平均温差（LMTD）思想在换热器中复现；本章的 h 只作为边界条件出现，流体侧 h 的关联在 Ch. 12/13 展开。
- **Ch. 14**：辐射在多孔绝缘材料和气隙中是 k"增大"的隐藏原因。
- **Ch. 15**：换热器管壁热阻与污垢热阻是总传热系数 U 的组成部分。
- **外部概念**：与动量传递的 Newton 黏性定律同构（通量=系数×梯度），是三传类比（Ch. 17 扩散）的第一环。
