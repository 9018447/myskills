# 第3章: 建立一个稳态精馏模拟

## 核心思想
在 Aspen Plus 中用 RadFrac 严格塔模块从零搭建一个稳态精馏模拟（本章以丙烷/异丁烷二元分离为例），核心方法论是"两步走"：先用**猜定的设计变量**（馏出量 D、回流比 RR）让塔收敛，再用 **Design Spec/Vary** 让程序反解设计变量以精确满足产品规格。为兼顾后续动态模拟，流程从一开始就包含泵和控制阀（压力驱动动态模拟所必需）。

## 关键框架与原理
- **自由度分析（操作规定）**: 进料、压力、板数、进料位置定死后，塔只剩 2 个自由度 → 必须且只需规定 2 个变量（初期常用 D 和 RR；收敛后改为产品规格）。
- **Design Spec/Vary（设计规定/调整变量）**: 指定"控制变量"的目标值与"调整变量"（操纵变量）的搜索区间，程序迭代求解。要点：**一次只解一个**——先调 D 收敛塔顶规格（D 对全塔组成影响最强），保持其生效，再调 RR 收敛塔底规格。操纵变量必须给合理上下限。
- **压力选择逻辑**: 冷凝器优先用冷却水（305 K）而非制冷系统；取传热温差 20 K → 回流罐温度 325 K → 由轻组分蒸气压反推所需塔压。塔压应尽可能低（压力升高 → 相对挥发度下降 → RR 上升 → 能耗上升）。
- **校核法 vs 设计法**: RadFrac 属"校核"法（给定板数/进料位置/RR，验证产品），第 3.9 节的 Conceptual Design（ConSep）属"设计"法——给定两端产品规格与 RR，逐板作组成轨迹，两轨迹相交即 RR > R_min，直接给出板数与进料位置（限一股进料三元体系）。
- **探索极限值**: 最小回流比 = 不断增板直至 RR 不再下降；最少板数 = 不断减板直至 RR 猛增。二者是第 4 章经济优化的输入。
- **同步设计思想**: 稳态流程图里预留泵/阀及 Flash Options 的 Valid Phases=Liquid-Only 设置，为第 7 章压力驱动动态模拟铺路。

## 关键概念
- **RadFrac**: 严格逐板精馏模块，有完全塔/汽提塔/精馏塔/吸收塔四种图标；冷凝器可选 Total 或 Partial-Vapor（汽相馏出物）；釜式与热虹吸再沸器均为部分再沸器，选哪种对稳态无影响。
- **Aspen 塔板编号**: 回流罐 = 第 1 块理论板，顶塔板 = 第 2 块，向下递增，再沸器 = 第 N_T 块；板数 N_T 时塔内实际板为 N_T−2。
- **Design Spec（设计规定）**: Type 选 mole purity，Target 填目标值；Components 页选关键杂质组分（用 ">" 从 Available 移到 Selected），Feed/Product Streams 页选物流。
- **Vary（调整变量）**: Type 选 Distillate rate 或 Molar reflux ratio，并给上下限。
- **收敛算法**: 烃类体系用 Standard 即可；高度非理想体系需换其他选项。
- **多重解问题**: 方程组高度非线性，可能收敛到不同解（依赖初值）；且若板数小于最少板数，任何 Vary 都无解——数值收敛不能替代工程判断。
- **塔板压降**: 经验值约 0.1 psia/板（≈0.0068 atm）。
- **F 因子**: 汽相负荷判据 F = V_max·√ρ_V ≈ 1（英制），用于核算塔径。
- **液泛/流道数**: 大塔径单流道会造成板上液面梯度过大，需多流道塔板。

## Aspen 操作要点
1. **新建**: 开始 → Aspen Tech → Aspen Plus User Interface → 选 Blank Simulation → OK。
2. **搭流程**: 底部 Columns 标签 → RadFrac 箭头 → 选完全塔图标 → 点击画布放置；Pressure Changers 标签 → Valve（3 个）、Pump（2 个）放置；Material STREAMS → Material 连接物流；点 Material STREAMS 左上方箭头退出插入模式。注意：物流接冷凝器**下部**箭头为液相馏出物（全凝器），接上部则变部分冷凝器。左键图标 → Rename 重命名（F1/D1/B1，泵阀命名关联 C1）。
3. **单位与报告**: Data → Setup → 单位选 SI（本书压力例外地用 atm）；Setup → Report Options → Stream 页 → Fraction basis 勾选 Mole（否则物流报告不含摩尔分数）。
4. **组分**: Data Browser → Components → Find → 输入 PROPANE → Find now → Add；同法加 ISOBUTANE → Close；在 Component ID 列改名为 C3/IC4（点击别处 → Rename 确认）。
5. **物性包**: Properties → Specifications → Base Method 下拉选 CHAO-SEA（多数烃类 VLE 适用）。同一流程不同单元可用不同物性包（塔用 VLE，倾析器用 LLE）。
6. **进料**: Streams → F1 → Input → 1 kmol/s、322 K、20 atm（含进料阀 5 atm 压降），基准下拉选 Mole-Frac，C3=0.4、IC4=0.6。
7. **塔 C1 → Setup**：
   - Configuration 页：Total stages=32；Condenser=Total；Reboiler=Kettle（或 Thermosiphon）；Convergence=Standard；操作规定选 Distillate rate=0.4 kmol/s、Molar reflux ratio=2。全部输入后红点变蓝钩。
   - Stream 页：进料板=16（先猜中部）。
   - Pressure 页：回流罐压力=14 atm（初版），板压降 0.0068 atm。
8. **泵/阀**: P11、P12 Setup → 选 Pressure increase=6 atm；V1 → 出口压力 14.2 atm（猜值，收敛后回改）+ Valid Phases=Liquid-Only；V11/V12 → 压降 3 atm + Liquid-Only。
9. **运行**: 点蓝色 N（Next）按钮；缺输入处自动标红。收敛信息显示在 Control Panel。
10. **Design Spec/Vary**: C1 → Design Spec → New → OK；Specifications 页：Type=mole purity，Target=0.02；Components 页选 IC4；Feed/Product Streams 页选 D1。C1 → Vary → New → Type=Distillate rate，下限 0.2、上限 0.6。运行收敛后再建第 2 组：Spec=B1 中 C3 mole purity=0.01，Vary=Molar reflux ratio，限 1–5。运行 → Result Summary 查 RR 及冷凝器负荷，Reboiler/Column base 查再沸器负荷与塔底温度。
11. **压力复核**: 若回流罐温度 ≠ 325 K，上调压力重跑（14 → 16.8 atm）。
12. **剖面与绘图**: C1 → Profile → Compositions 页 → View 选 Liquid 查液相组成分布；Plot → Plot Wizard → Temp/Comp 图标生成曲线。
13. **塔径**: C1 → Tray Sizing → New → 输入板段（2–31）与塔板型（筛板）→ 运行 → Results 读塔径；大塔在 Specification 页把通道数改 2 重算。
14. **水力学**: C1 → Report → Property Options 勾 Include Hydraulic Parameters → 运行 → Profile → Hydraulic 页读汽/液流量与密度。
15. **概念设计**: 工具箱 Conceptual Design 页 → ConSep 图标拖入流程 → 接 3 股物流 → 输入组分/压力/物性 → Mode 选 Design → Specifications 页设轻/重关键组分不纯度（最多 3 个规定）→ Calculate。

## 公式与方程
塔高估算（板间距 0.61 m = 2 ft，20% 裕量，塔板数 = N_T − 2）：
$$L = 1.2 \times 0.61 \times (N_T - 2)$$

F 因子校核塔径（英制单位，取 F ≈ 1）：
$$F = V_{\max}\sqrt{\rho_V}$$
其中 $V_{\max}$ 为最大汽相流速（ft/s），$\rho_V$ 为汽相密度（lb/ft³）。由最大汽相体积流量 ÷ $V_{\max}$ 得截面积，再得直径。非恒摩尔流时取汽相流量最大的塔板定径。

## 反模式
- **同时启用两个 Design Spec/Vary 一步求解**: 大型非线性方程组不保证有解、可能多重解；应按"D 先（影响强）、RR 后（影响弱）"顺序串行收敛。
- **操纵变量上下限随手设**: 区间不含真解则不收敛；应基于工程初猜（如 RR≈3 附近给 1–5）。
- **板数低于最少板数就加 Design Spec**: 数学上无解，调任何变量都得不到合格产品。
- **压力随手定/默认高**: 压力偏高 → 相对挥发度降 → RR 与能耗升；应由冷却水温度+温差反推最低可行压力。本例 14→16.8 atm 使 RR 从 3.095 升到 3.511。
- **进料压力/阀后压力拍脑袋且不复核**: V1 出口压力须等于进料板实际压力，首次收敛后必须回改。
- **忘记 Report Options 勾 Mole**: 物流结果不显示摩尔分数，精馏计算的核心数据看不到。
- **大塔径用单流道塔板**: 液面梯度过大、堰上液高高，应增加流道数（7.75→5.91 m）。

## 实例演练
**体系**: 丙烷(C3)/异丁烷(IC4) 二元分离，Chao-Sea 物性包。（注意：DME/甲醇/水在后续章节。）
**进料 F1**: 1 kmol/s，322 K，20 atm（进料阀压降 5 atm），z_C3=0.40、z_IC4=0.60。
**塔 C1**: 32 块理论板（罐=1、再沸器=32，塔内 30 板），全凝器+部分再沸器，进料板先设 16，板压降 0.0068 atm。
**压力推导**: 冷却水 305 K + 温差 20 K → 回流罐 325 K → C3 蒸气压 ≈14 atm → 初设 14 atm；实际收敛后罐温仅 317.06 K，上调至 **16.8 atm** 得 325 K。
**产品规格**: D1 中 IC4 ≤ 2 mol%，B1 中 C3 ≤ 1 mol%。
**手调过程**: D=0.4、RR=2 时塔顶 IC4≈12%、塔底 C3≈8%（远不达标）；RR=3 时顶部≈2%、底部≈1.5%。
**Design Spec/Vary**: ① Spec: D1 中 IC4 mole purity=0.02，Vary: D ∈ [0.2, 0.6]（3 次迭代收敛，D=0.39754）；② Spec: B1 中 C3=0.01，Vary: RR ∈ [1, 5]（3 次迭代收敛）。
**结果（16.8 atm）**: D1=0.4021 kmol/s，RR=3.511，x_D,IC4=0.0200027，x_B,C3=0.0100008；冷凝器 −22.29 MW（14 atm 数据），再沸器 27.163 MW，塔底 366.11 K（93℃）→ 温差 40 K 对应 3 atm 饱和蒸气 406 K（133℃），故 6 atm 蒸气扣除 3 atm 阀压降即可用。
**最优进料板**: 固定两端纯度扫板位，第 14 板再沸器负荷最小（27.17 MW，RR=3.463；12/13/15/16 板均更高）。
**极限值**: R_min≈2.9（板数 32→96 时 RR 3.463→2.908 饱和）；最少板数≈15（N_T=15 时 RR 飙至 160.8，16 板为 21.35）。
**塔径**: Tray Sizing（2–31 板，筛板）单流道 7.75 m → 双流道 5.91 m；F 因子核算：最大汽相流量 9.23 ft³/s（第 32 板）、ρ_V=2.82 lb/ft³、F=1 → V_max=0.595 ft/s → 截面积 155 ft² → 直径 14.0 ft（4.28 m），比 Aspen 略小。
**概念设计算例**: nC4/nC5/nC6（30/30/40 mol%），100 kmol/h，4 atm，Chao-Sea；规定 D 中 nC5=1%、B 中 nC4=1%、D 中 nC6=0.01%，RR=3 → 轨迹相交，15.8 块板、进料板 5.9；RR 降至 2.64 以下提示分离不可行。

## 关键要点
1. 建塔流程固定为：流程图 → 单位/报告选项 → 组分 → 物性包 → 进料 → 塔配置（板数/冷凝器/规定）→ 泵阀 → 运行，缺项以红色标记逐个补齐。
2. 塔压不是猜的：由"冷源温度 + 合理温差 → 回流罐温度 → 关键组分蒸气压"反推，且总取满足冷凝的最低压力。
3. 先用 D+RR 粗收敛看差距，再串行启用 Design Spec/Vary：D 收塔顶、RR 收塔底，并给足搜索区间。
4. 收敛成功 ≠ 设计合理：板数 < N_min 时无解，还须警惕多重解；数值交给 Aspen，判断留给自己。
5. R_min（增板法）与 N_min（减板法）用两三次扫描模拟即可锁定，是第 4 章经济优化的必备输入。
6. 最优进料板 = 固定产品纯度下再沸器负荷最小的板位，通常需逐板扫描。
7. 塔径用 Tray Sizing 但要用 F 因子独立核算；大塔径必须考虑多流道塔板。

## 关联章节
- **第1章**: 物性包选择依据在此直接使用（CHAO-SEA）。
- **第2章**: 塔的 2 个剩余自由度（操作规定）思想来自该章。
- **第4章**: 本章求出的 R_min、N_min、最优进料板、塔径/塔高是经济优化与板数-RR 权衡的输入；ConSep 概念设计也服务于此。
- **第7章**: 泵、控制阀及 Valid Phases=Liquid-Only 的设置是为压力驱动动态模拟预埋的；V1 阀后压力需与进料板压力一致。
- **后续各章**: 高度非理想体系（如醇/水）需更换收敛算法与物性包，方法框架与本章程式化步骤一致。
