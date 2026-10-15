# Chapter 19: Humidification Operations

## Core Idea
气相与纯液体（典型为空气-水）之间的传热与传质是耦合的：液体是单组分，液相无传质阻力，全部阻力在气相，但显热与潜热同时交换、温度与浓度同时变化。本章给出湿度学定义体系、湿度图、湿球温度理论（Lewis 关系）和逆流凉水塔的熵（焓）设计法。

## Frameworks Introduced
- **Humidity chart（Grosvenor 湿度图）**：以 T 为横轴、湿度 $\mathscr{H}$ 为纵轴；饱和线、等百分比湿度线、绝热冷却线、湿容积线、湿热线合一——"Use it when 需要由两个性质定出空气-水状态及其余全部性质"。
- **Adiabatic saturation temperature $T_s$（绝热饱和温度）**：绝热喷淋使气体饱和且水循环回到 $T_s$ 时的出口温度，是真平衡终点，由焓平衡 Eq. (19.11) 试差求出。
- **Wet-bulb temperature $T_w$（湿球温度）**：小量液体在连续气流中达到的稳态非平衡温度，由气相传热/传质速率平衡决定（动态稳态，非平衡态）。
- **Lewis relation**：$h_y/(M_B k_y) \cong c_s$（Eq. 19.21）——对空气-水成立，此时psychrometric line 与绝热冷却线重合，$T_w \approx T_s$；对空气-有机蒸气不成立，psychrometric 线更陡，$T_w > T_s$。
- **Psychrometric ratio / Chilton-Colburn 类比**：$h_y/(M_B k_y) = c_p (\mathrm{Sc}/\mathrm{Pr})^m$，$m \approx 2/3$（Eq. 19.20）。
- **Cooling-tower enthalpy method**：以气体焓 $H_y$ 对水温 $T_x$ 作操作线-平衡线图，用总焓推动力求 $N_{Oy}$、$H_{Oy}$（Eq. 19.39–19.40）；连接线（tie line）斜率 $-h_x a/(k_y a M_B)$。

## Key Concepts
- **Humidity $\mathscr{H}$**：单位质量无蒸气气体（干气）携带的蒸气质量，1 atm 下仅取决于蒸气分压。
- **Saturation humidity $\mathscr{H}_s$**：气体在自身温度下与液体平衡时的湿度（蒸气分压=该温度蒸气压）。
- **Relative humidity $\mathscr{H}_R$**：$100\,p_A/P_A'$；**percentage humidity $\mathscr{H}_A$**：$100\,\mathscr{H}/\mathscr{H}_s$——除 0/100% 外恒有 $\mathscr{H}_A < \mathscr{H}_R$。
- **Humid heat $c_s$**：1 lb 干气+所含蒸气升温 1°F 所需热量，$c_s = c_{pB} + c_{pA}\mathscr{H}$。
- **Humid volume $v_H$**：1 lb 干气+所含蒸气在 1 atm、气温下的总体积。
- **Dew point**：恒湿度冷却至饱和的温度；饱和气体的露点=气温。
- **Adiabatic cooling lines**：湿度图上 Eq. (19.11) 的等 $T_s$ 线族，斜率 $-c_s/\lambda_s$。
- **Psychrometric line**：Eq. (19.19) 对应的等 $T_w$ 线，交 100% 线于 $T_w$。
- **Approach / Range**（凉水塔）：出水温度高出进口空气湿球温度之差（approach，典型 5–15°F，不低于 ~5°F）；水进出塔温差（range，典型 10–30°F）。
- **Film fill vs splash fill**：波纹塑料膜式填料（cellular fill）单位容积传质面大、$H_{Oy}$ 小；旧式木条溅水填料 $H_{Oy}$ 大。

## Key Equations
- 湿度定义：$\mathscr{H} = \dfrac{M_A p_A}{M_B (P - p_A)}$（$p_A$=蒸气分压，$P$=总压，$M_A/M_B$=蒸气/干气分子量）
- 饱和湿度：$\mathscr{H}_s = \dfrac{M_A P_A'}{M_B(P-P_A')}$（$P_A'$=液体蒸气压）
- 湿热：$c_s = c_{pB} + c_{pA}\mathscr{H}$
- 湿体积：$v_H = \dfrac{359\,T}{492}\left(\dfrac{1}{M_B} + \dfrac{\mathscr{H}}{M_A}\right)$（fps 单位，T 为 °R）
- 总焓：$H_y = c_s(T - T_0) + \mathscr{H}\lambda_0$（$T_0$=基准温度，$\lambda_0$=基准温度汽化潜热）
- 绝热饱和：$\dfrac{\mathscr{H}_s - \mathscr{H}}{T - T_s} = \dfrac{c_s}{\lambda_s}$（Eq. 19.11，试差求解）
- 湿球：$\dfrac{\mathscr{H} - \mathscr{H}_w}{T - T_w} = -\dfrac{h_y}{M_B k_y \lambda_w}$（Eq. 19.16；$\mathscr{H}_w$、$\lambda_w$ 为 $T_w$ 下饱和湿度与潜热）
- 塔操作线（焓-温图）：$G_y'(H_a - H_y) = G_x c_L (T_{xa} - T_x)$，斜率 $G_x c_L / G_y'$
- 传质速率（焓基准）：$G_y' dH_y = K_y a (H_y^* - H_y) dZ$，$\dfrac{1}{K_y a} = \dfrac{1}{k_y a M_B} + \dfrac{m}{h_x a}$（$m$=平衡线斜率 $dH^*/dT$；$H_y^*$=与 $T_x$ 水平衡的气体焓）
- 传质单元：$N_{Oy} = \displaystyle\int \frac{dH_y}{H_y^* - H_y} = \dfrac{Z_T}{H_{Oy}}$，$H_{Oy} = G_y'/K_y a$

## Reference Tables
| 对比项 | Adiabatic saturation $T_s$ | Wet-bulb $T_w$ |
|---|---|---|
| 性质 | 真平衡终点 | 稳态非平衡（速率决定） |
| 过程中气体的 T、H | 变化 | 不变（连续气流，按进口取值） |
| 空气-水 | $T_w \approx T_s$（巧合，因 Lewis 关系） | $T_w \approx T_s$ |
| 空气-有机蒸气 | — | $T_w > T_s$，psychrometric 线更陡 |

| 凉水塔典型值 | 数值 |
|---|---|
| Approach（出水−进风湿球） | 5–15°F，设计下限 ~5°F |
| Range（水进出温差） | 10–30°F |
| 蒸发损失 | 每 20°F range 约 2% |
| 风吹损失 drift | 良设计约 0.2% |
| $H_{Oy}$（cellular fill） | 2–3 ft（0.6–1 m） |
| $H_{Oy}$（木条溅水填料） | 10–20 ft（3–6 m） |
| 实际风量/最小风量 | 1.2–2.0 |

## Worked Example
**Ex. 19.3（凉水塔性能外推）**：逆流塔，水 105→85°F，空气干球/湿球 90/76°F，$G_y'=2000$、$G_x=2200$ lb/h·ft²，填料高 4 ft。(a) 由湿度图查 $\mathscr{H}_b=0.017$、$c_s=0.248$，算 $H_b=32.7$ Btu/lb；总焓平衡得 $H_a=54.7$。在焓-温图上作操作线，分两段取对数平均推动力求得 $N_{Oy}=1.82$，故 $H_{Oy}=4/1.82=2.2$ ft；approach = 85−76 = 9°F。(b) 冷却负荷不变、空气变为 70/60°F（干/湿球）：新 $H_b=18.9$、$H_a=40.9$；试差移动操作线使 $N_{Oy}$ 保持 1.82 → 出水约 95/75°F，approach 增大到 75−60 = 15°F（平衡线弯曲所致）。结论：性能由进口风**湿球温度**主导，干球几乎无影响。

（Ex. 19.1：烟道气绝热饱和温度需用摩尔热容做热平衡+相图试差；Ex. 19.2：由 T=150°F、露点 60°F 读出 $\mathscr{H}$、%湿度、$T_s$、$c_s$、$v_H$——湿度图联读。）

## Anti-patterns
- **把 $T_w$ 当 $T_s$ 用于非空气-水体系**：二者相等只是空气-水的巧合；有机蒸气体系 psychrometric 线更陡，$T_w > T_s$，用错会算错传质推动力。
- **混用 relative humidity 与 percentage humidity**：中间湿度下 $\mathscr{H}_A < \mathscr{H}_R$，两者不可互换。
- **认为塔内水冷必须气温低于水温**：错——只要水温高于湿球温度，蒸发冷却即可进行；塔底气温可高于水温。
- **湿球测量不规范**：湿纱布有干斑、风速 <5 m/s（辐射误差显著）、补水温度不等于 $T_w$，都会使读数偏高；规范操作下读数与气速无关。
- **凉水塔用总系数过度外推**：$K_y a$ 公式里平衡线斜率 m 随温度每 10°F 变化 30–40%，大幅变工况时应重作焓图而非套用旧 $N_{Oy}$。
- **膜式填料不做顶部布水设计**：cellular fill 无自然再分布，布水不均直接损失有效面积。

## Key Takeaways
1. 湿度计算一律以**单位质量干气**为基准，且固定总压（默认 1 atm）。
2. 液相是纯组分 → 液相零传质阻力，全部阻力在气膜；传热传质由同一边界层控制，通过 Lewis 关系耦合。
3. 空气-水体系一张湿度图（psychrometric line = adiabatic cooling line）可读出全部性质；其他体系需另作 psychrometric 线。
4. 凉水塔设计用**焓推动力**：操作线斜率 $G_x c_L/G_y'$，平衡线是饱和空气焓曲线；最小风量由操作线与平衡线相切确定，实际取 1.2–2.0 倍。
5. 塔性能对进口风**湿球温度**极敏感、对干球几乎不敏感；湿球降低→出水温度降低但 approach 反而增大。
6. 蒸发水量很小（每 20°F range ≈2%），补水量 = 蒸发 + drift(≈0.2%) + 排污（控盐）。
7. 湿度测量三法：露点法（镜面起雾/消雾平均）、干湿球法、直接吸收法。

## Connects To
- **Ch. 17**：传质系数 $k_y$、$(1-y)_L$ 因子与传质-传热类比（Sc/Pr）的来源。
- **Ch. 12**：气相对流给热系数关联式（Re、Pr）。
- **Ch. 18**：$N_{Oy}$/$H_{Oy}$ 与吸收塔 NTU/HTU 完全同构，只是推动力由浓度换成焓。
- **Ch. 24**：干燥中同样的热-质耦合（恒速段即湿球机制）。
- **Ch. 15**：逆流 vs 错流的温度逼近效率对比迁移到塔型选择。
