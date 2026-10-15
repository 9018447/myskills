# 第11章: 石油分馏的控制

## 核心思想
石油体系含成千上万组分，不能用摩尔分数组成描述，而要用馏程（boiling ranges）表征；石油分馏塔的控制目标因此从"产品纯度"转为"ASTM 馏点规格"。本章以预闪蒸塔和常压塔（CDU）两个 Aspen Plus/Aspen Dynamics 案例，建立从原油 Assay 数据生成虚拟组分、稳态设计到 28 回路动态控制的完整流程。

## 关键框架与原理
- **馏程表征体系**：用初馏点（IBP）、5%/50%/95% 馏点、终馏点（FBP）刻画馏分；分离效果用相邻产品"95%点−下一产品5%点"的**空隙（gap）**与**重叠（overlap）**度量，而非不纯物组成。
- **三种沸点分析法**：ASTM D-86 (Engler)、ASTM D-158 (Saybolt)≈单理论板分离（快、简）；TBP 法带填料柱、有回流，给出更真实的组成细节（曲线两端更宽，50% 点两者接近）。TBP 曲线可读出各馏分切割产量（如 280~460°F 航空油对应 17%~40% 体积，约 22% 收率）。
- **虚拟组分（pseudocomponents）**：把 TBP 曲线切成若干"切割馏分"，各赋平均沸点/密度/分子量；由原油 Assay 数据（TBP 曲线 + API 重度曲线 + 轻端组分分析）在 Aspen 中自动生成。
- **预闪蒸塔**：无再沸器、部分冷凝器、加热炉进料部分汽化 + 釜部直接蒸汽提馏；只有一个自由度（塔内全部气体来自加热炉汽化），用于在常压塔前移除最轻组分。
- **常压塔（CDU）**：带加热炉（overflash 规格）、3 个侧线汽提塔（煤油/柴油/AGO）、2 个中段回流（pumparound 回收高温位热量预热进料）。中段回流是"能耗 vs 分离精度"的折中：热量被回收则加热炉燃料省、但塔上部 L/V 降、分离变差。
- **设计三定律（Luyben 归纳）**：
  1. 相邻馏分的 95% 与 5% 点不能独立设置——减一个产品流量会同时抬它自己的 95% 点与下一个更重产品的 5% 点；
  2. 中段回流反向影响分离与能耗——减少移热量改善其上方分离、提高加热炉负荷；
  3. 汽提蒸汽量影响初馏点/闪点，对 5%、95% 点和产品量几乎无影响。
- **控制结构选择**：回流比小（0.344）的预闪蒸塔用馏出液流量控回流罐液位；回流比大（3.71）的常压塔回流罐液位用回流量控。石油塔用**侧线流量定产品规格**（95%/5% 点控制器操纵对应产品流量），而非温度组成。

## 关键概念
- **Assay（原油化验）**：TBP 曲线 + 比重（API）曲线 + 轻端组分（light ends，溶解的 C1~nC5 摩尔分数）三件套数据。
- **°API**：石油重度单位，°API = 141.5/比重 − 131.5，与比重反向变化。
- **虚拟组分**：每个具有平均沸点、密度、分子量的假想烃，集合代表整股石油物流。
- **过汽化量（overflash）**：闪蒸区产生的气体中部分冷凝后从上方塔板返回闪蒸区的液体"洗涤"流，防止重组分夹带导致 AGO 变色、金属污染下游催化剂；本章取 0.03。
- **空隙/重叠**：轻产品 95% 点与相邻重产品 5% 点之差；正为 gap，负为 overlap。
- **b/d（桶/天）**：1 桶 = 42 美加仑；Setup 中流量为实际工况体积，Streams Results 的 Liq. vol. 60F 为 60°F/1atm 标准体积——两者不可混淆。
- **Stream Sensor**：Aspen Dynamics 中获取物流 ASTM 馏点 PV 的工具（缺省物性不含沸点）。
- **Tyreus-Luyben 调谐**：配合继电-反馈测试（KU、PU）设定 Kc、τI，本章全部温度/馏点回路使用。

## Aspen 操作要点
1. **模板**：New→Template→Simulation 标签→选 *Petroleum with English Units*→右下选 **Assay Data Analysis**→OK。
2. **组分**：Components|Specification 逐行输入常规组分（水~正戊烷）；新增一行输入 OIL-1，第二列下拉选 **Assay**，再切 **Petroleum** 标签页。
3. **Assay 数据**：Assay|Blend|OIL-1|Basic Data：Distillation Curve Type 选 *True boiling point (liquid volume basis)*，Bulk gravity value 输 31.4（°API）；依次填 TBP 表、**Light Ends** 页、**Gravity/UOPK** 页（类型 API gravity）。
4. **生成虚拟组分**：点蓝色 N → 选 *Specify options for generating pseudocomponents* → Components|Petro Characterization|Generation → New 命名（如 Crude1）→ 下拉加 OIL-1 → N → 一路 OK。结果在 Petro Characterization|Results（NBP、密度、分子量、临界性质）。
5. **石油塔设备**：Model Library→Columns→**PetroFrac**；预闪蒸塔选带加热炉的精馏塔图标；常压塔选 **CDU10F**（加热炉+多汽提塔+多中段回流）。进料连加热炉：把塔底红色输入箭头**拖到加热炉**再点击。汽提塔蒸汽/产品接口：把蓝色箭头拖到对应汽提塔侧释放。
6. **中段回流**：Blocks|CDU|**Pumparounds**|New；P-1 第8板采出/第6板返回、49000 b/d、40 MM Btu/h；P-2 第14板采出/第13板返回、11000 b/d、15 MM Btu/h。
7. **汽提塔**：Blocks|CDU|**Stripper**|New|Configuration 页：S-1 4 块板、KERO、主塔第6板抽出、气相第5板返回、釜液 11700 b/d；Pressure 页设各板压力。
8. **主塔设置**：CDU|Setup：Configuration（25 块理论板、全冷凝器、馏出液估计流量）；Streams 页（加热炉进料第 22 板、蒸汽第 25 板）；Pressure 页；**Furnace** 页 Furnace Specification 选 *Fraction overflash* = 0.03。
9. **设计规定**：塔下 Design Specs|New：Type 选 *ASTM D86 temperature (dry, liquid volume basis)*，Target 填 95% 点温度；Feed/Product Streams 选产品；Vary 选 Distillate flow rate（柴油则选 S-2 bottoms flowrate）。
10. **画馏分曲线**：Results Summary|Streams|Vol.%Curve 标签→Plot|Plot Wizard→Dist Curve；或选 Vol% 列 + Ctrl 多选→Plot|X-Axis/Y-Axis Variable|Display Plot。
11. **动态单位**：Aspen Dynamics 无石油英制单位，先在稳态里切公制再导出。
12. **Stream Sensor**：右击产品物流→Forms→**Configure Sensor**→勾 Sensor On、Calculate Phase Properties，Valid Phase = Liquid-Only，把 ASTM D-86 Temperature 移入 Selected Properties，Liquid Volume % Distilled 填 95（或 5）。
13. **wash 流量 PV**：塔内流量不在可控变量中，需写 **Flowsheet Equation**（第 19 板液相 Fml_out 质量→FCwash 的 PV），并把该变量 fixes 改 **free** 消除过设定。
14. **阀尺寸**：进料 +20% 时 V14/V25/V22 饱和，尺寸加倍后稳态开度约 25%。

## 公式与方程
$$ {}^{\circ}\mathrm{API} = \frac{141.5}{\text{比重}} - 131.5 $$
分离量度（gap 为正、overlap 为负）：
$$ \text{Gap} = T_{95\%}^{\text{轻产品}} - T_{5\%}^{\text{相邻重产品}} $$
预闪蒸塔蒸汽/进料摩尔比（串级乘数器）：125.9/2272 = 0.04625；常压塔：302.1/1654 = 0.1827。

## 反模式
- **混淆 Setup b/d 与 Streams Results 的 Liq. vol. 60F bbl/day**：前者是工况实际体积，后者是标准态（60°F）体积，数值不同，当成 bug 是误判。
- **加热炉出口压力设得比塔釜压力高**：稳态能算通，但导出压力驱动动态文件时报错。
- **在预闪蒸塔用回流量控回流罐液位**：回流比仅 0.344，太小；应改用 NAPHTHA 流量控液位。
- **想独立设定相邻两产品的 95%/5% 点**：违反定律 1，两规格经产品流量耦合，不可同时指定。
- **加热炉温度回路用 1 min 死时间**：加热炉响应比蒸汽再沸器慢，需 3 min 死时间再继电-反馈调谐，否则调谐失真。
- **FCwash 用正作用/反作用搞反**：第 19 板液体太多应加大 AGO 采出，控制器须正作用；方向装反会把过汽化量推向夹带。
- **把 95% 点控制当成万能方案**：3~4 h 才恢复；若第 2 板温度对扰动基本不变，改用板温控制（τI=5.3 min vs 26 min）响应快一个量级，代价是规格点略漂移（191→189.3°C）。

## 实例演练
- **原油**：OIL-1（31.4°API，50% 点 650°F）、OIL-2（34.8°API，50% 点 450°F，更轻），各 5000 b/d，共 100000 b/d，200°F 进料。
- **预闪蒸塔 PREFLASH**：10 块理论板、无再沸器、部分冷凝器（170°F，39.7 psia）；加热炉 450°F（203×10⁶ Btu/h，约 30% 质量汽化）；釜部蒸汽 5000 lb/h（400°F）；倾析水 244 lb/h。Design Spec 使石脑油 ASTM 95%=375°F → 石脑油 21040 b/d；塔径 11.1 ft；LIGHTS 气相 575 lb·mol/h 带走大部分轻烃。优化版（文献[2]）：回流罐 130°F/47 psia、炉出口 400°F，LIGHTS 降至 251 lb·mol/h。
- **预闪蒸塔控制**：液位 P 控制器增益 2；炉温回路（3 min 死时间）Kc=0.465、τI=13 min；95% 点回路（3 min 死时间）Kc=0.821、τI=26 min。±20% 进料扰动时 95% 点偏离约 12°C；改控第 2 板温度 171.6°C（Kc=0.90、τI=5.3 min）约 90 min 稳定。
- **常压塔 CDU**：塔径 20.3 ft、25 块理论板、塔顶 15.7 psia；加热炉 684°F（201 MM Btu/h），3644 lb·mol/h 进料汽化 2278；闪蒸段下 3 块板 + 12000 lb/h 蒸汽；R=3.71；产品：重石脑油 6830 b/d（5%/95%=195/375°F）、煤油 11700 b/d（396/502°F）、柴油 14363 b/d（489/640°F）、AGO 8500 b/d（589/782°F）、渣油 37647 b/d。分离：HNAPH-煤油 gap 21°F；煤油-柴油 overlap 13°F；柴油-AGO overlap 51°F（塔下部 L/V 低所致）。水倾析量大（17180 lb/h）源于大量直接蒸汽。
- **常压塔控制**：共 28 个控制器（炉温 2、流量 8、压力 5、液位 9、ASTM 馏点 4）。馏点回路调谐（表 11.6）：轻石脑油 95%（Kc=0.46/τI=13）、重石脑油 95%（Kc=2.1/τI=46）、柴油 5%（Kc=2/τI=51）、柴油 95%（Kc=1.2/τI=51），均 3 min 死时间。±20% 双原油扰动：石脑油 95% 点最大偏离 6°C，柴油 5%/95% 点约 20°C。

## 关键要点
1. 石油体系先做 Assay → 虚拟组分（Petro Characterization Generation），之后所有计算对象是馏程而非组成。
2. 产品切割位置由 Design Spec（ASTM D86 temperature 类型）+ 产品流量 Vary 闭环求出，95% 点是最常用规格。
3. 相邻产品规格不独立（定律 1）：调一个产品流量同时移动其自身 95% 点与下侧产品 5% 点——控制结构设计的前提。
4. 中段回流 = 能量回收与分馏精度的权衡（定律 2）；汽提蒸汽只移动初馏点/闪点（定律 3），不要用它调 95% 点。
5. 石油塔控制的核心回路是"产品流量 → 自身 ASTM 馏点"，PV 用 Stream Sensor 的 Configure Sensor 获取。
6. 无再沸器的预闪蒸塔只有 1 个自由度；小回流比塔液位控馏出液、大回流比塔液位控回流。
7. 过汽化量（0.03）保护 AGO 颜色与下游催化剂；用 Flowsheet Equation 把塔内液体流量引为 wash 流量控制器 PV（fixes→free）。
8. 动态化前切公制单位；加大可能饱和的阀（V14/V25/V22），加热炉回路死时间 3 min。

## 关联章节
- **第 8 章（反应器/塔的动态控制基础）**：继电-反馈 + Tyreus-Luyben 调谐方法在本章所有回路复用。
- **第 10 章（复杂塔控制）**：侧线塔、多产品的控制结构思想延伸到石油塔。
- **第 12 章（催化裂化主分馏塔）**：同一石油分馏框架应用于反应流出物体系（饱和+不饱和烃）。
- **文献[2] Luyben, Energy Fuels 2012**：预闪蒸塔设计的经济优化（预闪蒸塔本例非优化设计）。
