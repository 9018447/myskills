# Chapter 28: Properties and Handling of Particulate Solids

## Core Idea
散粒固体既非流体也非连续固体：用尺寸/形状/密度表征单粒，用筛析与统计平均径表征粒子群，用侧压系数与休止角描述其"似液非液"的力学行为，而粉碎的能量需求遵循 Bond 经验定律——全章为固体加工（储存、混合、粉碎）提供量化语言。

## Frameworks Introduced
- **Sphericity Φ_s（球形度）**：Φ_s=6v_p/(D_p s_p)，球形=1；破碎物料典型 0.6–0.8，磨圆颗粒可达 0.95。
- **Screen analysis（筛析）**：Tyler 标准筛系以 200 目（0.074 mm）为基准，相邻筛开口比 √2（细分级用 ⁴√2=1.189 中间筛）；14/20 表示"通过 14 目、留在 20 目"。
- **平均粒径家族**：不同用途选不同平均——比表面积/传质用 D̄_s（体积-表面平均），尺寸分布代表用 D̄_w（质量平均），粒子计数用 D̄_V（体积平均）；同一样品四个平均值可差 2–4 倍。
- **Granular solid mechanics（粒状固体力学）**：五条与流体的区别——各向异性压力（侧压系数 K'）、剪应力整体传递、堆积密度可变、流动前必须膨胀（dilation）、堆内摩擦（休止角 α_r）。
- **Mass flow vs tunnel flow（Jenike）**：陡锥/低壁摩擦→整体流（先进先出）；浅锥或平底→漏斗流（中央柱先走、壁面滞留、可能 rathole 与偏析）。
- **Degree of mixing（混合度统计）**：实测点样标准差 s 与两个极限比较：完全随机混合 σ_e=√(μ_p(1−μ_p)/n)，完全分离 σ_0=√(μ(1−μ))；固体混合永远达不到 σ_e（静电力等反混合力始终存在）。
- **Four comminution actions**：压缩（粗碎硬料少细粉）、冲击（粗/中/细通吃）、磨剥 attrition（软料超细）、切割（定尺寸定形状无细粉）。
- **Bond law（邦德定律）**：单位质量粉碎功与产品粒径平方根成反比，以 work index W_i 标定——现代粉磨功率设计的标准方法。
- **Mill simulation**：粉碎速率函数 S_u（该粒级单位时间破碎分数）+ 破碎函数 ΔB_n,u（破碎产物分布），经式 (28.19) 逐级矩量衡算预测产品粒度分布。

## Key Concepts
- **Volume-surface mean diameter D̄_s**：D̄_s=6/(Φ_s A_w ρ_p)=1/Σ(x_i/D̄_pi)——与比表面积直接挂钩，是传质/反应/压降计算用的"有效直径"。
- **Mass mean D̄_w**：Σx_i D̄_pi——按质量加权的分布代表径。
- **Volume mean D̄_V**：[1/Σ(x_i/D̄_pi³)]^{1/3}——与单位质量粒子数挂钩：N_w=1/(aρ_p D̄_V³)。
- **Angle of repose α_r**：自由流动粒料 15°–30°；决定料堆坡度与输送带最大倾角。
- **K'（侧压系数）**：垂直加压产生的水平压力与垂直压力之比；自由流动固体 0.35–0.6，黏性固体趋近 0。
- **Bin pressure saturation**：料柱高超过约 3 倍容器直径后，底压不再随加料增加——多加的重量由壁摩擦传给地基；且加压使粒料更紧密更难流（与液体相反）。
- **Gravity discharge rate**：自由流动固体经底部圆孔的重力排料速率 ∝ D_o³，与料层高度基本无关（Janssen 效应的直接推论）。
- **Arching/bridging**：粒料在排料口上方成拱架桥不落；大仓底部设 archbreaker 浅锥防压实。
- **Mixer scaleup（Froude）**：翻滚混合机按 Froude 数 n²L/g 恒定放大。
- **Axial mixing Pe**：连续桨式混合机轴向扩散系数 E≈0.02UL–0.2UL，Pe=UL/E 为 5–50；反应器用低 E（近活塞流），均质器用高 E（缓冲进料波动）。
- **Work index W_i**：将极大进料磨至 80% 通过 100 μm 所需 kWh/短吨；包括设备摩擦，为总功率（limestone 12.74、quartz 13.57、trap rock 19.32）。
- **Critical speed of ball mill**：n_c=(1/2π)√(g/(R−r))——球被离心力压在壁上随筒旋转的转速；操作转速取 65–80% n_c（湿磨黏浆取低值）。
- **Nip angle & roll capacity**：光辊能咬入的最大粒径 D_p,max=0.08R+d（R=辊半径，d=辊隙）；产品最大径≈d；最经济压缩比 3–4:1。
- **Closed-circuit grinding**：磨机+分级器闭环，粗粒返回再磨；虽付输送/分级能耗，总能耗仍比开路省约 25%（避免过磨）。
- **Energy efficiency of comminution**：不足 1% 的输入能量真正用于产生新表面，其余变热；机械效率（传到固体/总输入）25–60%；粉碎是所有单元操作中能量效率最低者。
- **Cryogenic grinding**：液氮冷至 −75°C 以下使软/韧物料（蜡、热塑性塑料）脆化变可碎。

## Key Equations
- 球形度定义：$\Phi_s=\dfrac{6v_p}{D_p s_p}$（v_p=单粒体积，s_p=单粒表面积）
- 样品总面积：$A=\dfrac{6m}{\Phi_s\rho_pD_p}$（m=样品总质量，ρ_p=颗粒密度）
- 比表面积：$A_w=\dfrac{6}{\Phi_s\rho_p}\sum_{i=1}^{n}\dfrac{x_i}{\bar{D}_{pi}}$（x_i=粒级质量分数，D̄_pi=粒级算术平均径）
- 各平均径：$\bar{D}_s=\dfrac{1}{\sum x_i/\bar{D}_{pi}}$；$\bar{D}_N=\dfrac{\sum N_i\bar{D}_{pi}}{N_T}$；$\bar{D}_w=\sum x_i\bar{D}_{pi}$；$\bar{D}_V=\Big[\dfrac{1}{\sum x_i/\bar{D}_{pi}^3}\Big]^{1/3}$
- 单位质量粒子数：$N_w=\dfrac{1}{a\rho_p}\sum\dfrac{x_i}{\bar{D}_{pi}^3}=\dfrac{1}{a\rho_p\bar{D}_V^3}$（a=体积形状因子）
- 随机混合理论偏差：$\sigma_e=\sqrt{\dfrac{\mu_p(1-\mu_p)}{n}}$（μ_p=A 组分数分数，n=点样粒子数）；完全分离偏差 $\sigma_0=\sqrt{\mu(1-\mu)}$
- Bond 粉碎功率：$\dfrac{P}{\dot{m}}=0.3162\,W_i\Big(\dfrac{1}{\sqrt{D_{pb}}}-\dfrac{1}{\sqrt{D_{pa}}}\Big)$（P=kW，ṁ=短吨/h，D_pa、D_pb=进料/产品 80% 通过粒径 mm；干磨 ×4/3）
- 粉碎速率衡算：$\dfrac{dx_n}{dt}=-S_nx_n+\sum_{u=1}^{n-1}x_uS_u\Delta B_{n,u}$（S_n=粉碎速率函数 s⁻¹，ΔB_n,u=破碎函数）
- 破碎分布经验式：$B_{n,u}=(\bar{D}_n/\bar{D}_u)^{\beta}$
- 光辊咬入极限：$D_{p,\max}=0.08R+d$
- 球磨临界转速：$n_c=\dfrac{1}{2\pi}\sqrt{\dfrac{g}{R-r}}$（R=筒半径，r=球半径）

## Reference Tables
- **粒级测量方法分区**：干筛 >44 μm（325 目）；湿筛至 10 μm；1–100 μm 用光学显微/重力沉降/Coulter counter；更细用光散射、离心/超速离心沉降、光子相关光谱、电镜；超细粉直接报比表面积 m²/g。
- **Bond work index 典型值（kWh/短吨）**：clay 6.30、gypsum 6.73、bauxite 8.78、phosphate 9.92、limestone 12.74、iron ore 12.84、quartz 13.57、coal 13.00、cement clinker 13.45、granite 15.13、shale 15.87、gravel 16.06、trap rock 19.32；干磨 ×4/3。
- **设备能力量级**：primary jaw crusher 单台 1200 ton/h、吃 1.8 m 岩石出 250 mm；gyratory 至 4500 ton/h（连续出料、单位功耗低）；smooth roll 进 12–75 mm 出 1–12 mm；hammer mill 细碎 tip speed 至 110 m/s、0.1–15 ton/h 至 −200 目；attrition mill 0.5–8 ton/h、能耗 8–80 kWh/t；ultrafine 1–50 μm；jet mill 0.5–10 μm、耗汽 1–4 kg 或耗气 6–9 kg/kg 产品；colloid mill <5 μm（主要是打散团聚体）。
- **排料口设计经验**：半开即达全流量为最佳口径——过小易堵、过大难关且调节差。

## Worked Example
**Ex 28.1（筛析统计）**： crushed quartz（ρ_p=2650 kg/m³，a=2，Φ_s=0.571）4–200 目：Σx_i/D̄_pi=0.8284、Σx_i/D̄_pi³=8.8296 → A_w=3309 mm²/g、N_w=1679 粒/g、D̄_V=0.424 mm、D̄_s=1.207 mm、D̄_w=1.677 mm；150/200 目仅占质量 0.31% 却占总粒数 49.8%——小粒级统治粒子计数，大粒级统治质量，任何单一"平均粒径"都失真。
**Ex 28.2（Bond 功率）**：100 ton/h limestone，D_pa=50.8 mm（2 in）→ D_pb=3.175 mm（1/8 in），W_i=12.74：P=0.3162×12.74×(1/√3.175−1/√50.8)×100=169.6 kW（227 hp）——Bond 定律标准用法：查表 W_i+80% 通过粒径代入。

## Anti-patterns
- **用"一个平均粒径"代表全部计算**：D̄_s、D̄_w、D̄_V 可差 2–4 倍；传质用 D̄_s、产品规格用 D̄_w、粒子计数用 D̄_V，选错平均值整个设计偏一个量级。
- **忽略盘底细粉（pan fraction）的表面积与粒数**：150/200 目占 0.3% 质量却是近半粒子数；pan 粒子的表面积/数目远超粗粒，只是筛析无法定量。
- **按液体静压 h·ρ·g 设计仓壁/仓底**：粒料壁摩擦使底压在 h>3D 后饱和；而局部侧压反而因流动升高——按液体算会双重出错（底压过大、侧压不足）。
- **期望完全混合（s→σ_e）**：干粉混合有随机极限与静电反混合，长时间翻滚甚至退混合（segregation）；判断标准是产品性能而非 σ_e。
- **按高径比假设排料速率**：重力排料速率 ∝ D_o³ 与料位无关——加大料仓不加快排料，加大孔口才行（三次方）。
- **开路磨到全合格**：大量能量耗于过磨已合格粒子；加分级器闭路循环，总能耗省 25%。
- **不冷却磨机**：>99% 能量变热，低熔点/热敏物料会熔融、分解甚至爆炸；必要时报水冷、冷风、干冰或液氮（−75°C 低温脆化粉碎）。
- **超速运转球磨"提高产量"**：转速 ≥n_c 时球离心贴壁不再抛落，冲击粉碎停止；上限 80% n_c。

## Key Takeaways
- 粒子群的语言体系：筛析（√2 序列 Tyler 筛）给出 x_i–D̄_pi，四个平均径各司其职（D̄_s 比表面、D̄_w 质量、D̄_V 计数、D̄_N 数均）。
- 散体力学五特征（K' 侧压、剪力传递、密度可变、膨胀才能流、休止角）解释一切仓储现象：底压饱和、成拱、rathole、排料 ∝ D_o³。
- 排料设计三条铁律：底部出料优于侧口；陡锥/低摩擦→质量流先进先出；archbreaker + 振动/气炮对付黏性料。
- 固体混合的判据是统计的（s vs σ_e vs σ_0）且永远不完全；非黏性料用翻滚/ribbon，黏性料用剪切/捏合（Banbury、捏合机、muller），功率大得多。
- 粉碎选择路径：物料性质（硬/韧/热敏/纤维）+ 目标粒径定设备——jaw/gyratory 粗碎 → roll/rod 中碎 → ball/hammer 细磨 → jet/agitated mill 超细 → cutter 定形；功率用 Bond 定律估算。
- 粉碎能效极低（<1% 成表面）反推两条工艺纪律：闭路分级避免过磨、强化排热防热敏变质。

## Connects To
- Ch 7 的 sphericity、形状因子 a、D_p 定义与气力输送在本书首现于第 7 章，本章正式展开统计表征。
- Ch 9（液体搅拌）的功率/放大思想在固体混合中变形为 Froude 放大与 Pe 轴向混合。
- Ch 29 的筛分/分级设备（closed-circuit 的分离环节）、重力沉降与离心分级直接消费本章的粒度分布语言。
- Ch 27 MSMPR 结晶的 L_pr 与筛析输出即本章筛析统计的天然应用场景。
