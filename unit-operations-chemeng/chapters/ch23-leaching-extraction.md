# Chapter 23: Leaching and Extraction

## Core Idea
用液体溶剂从固/液混合物中取出目标组分：浸取针对不溶性固体中的可溶物，液液萃取针对难于蒸馏的互溶液体；两者共用逆流级联 + 操作线/平衡线框架，但萃取因两相密度接近而更依赖外加机械能与专用设备。

## Frameworks Introduced
- **Leaching（浸取/固液萃取）**：percolation（固定床渗滤：extraction battery / Shanks process、加压 diffusion battery）vs 移动床（Bollman 提斗式、Rotocel 转格式）vs 分散固体（搅拌槽+增稠器串联/离心机）。
- **Countercurrent leaching stage model**：V 相（溢流液）逆固体流向流动；平衡线即 $x_e = y$（固体持液浓度=溢流浓度）；操作线 $y_{n+1} = (L_n/V_{n+1})x_n + (V_a y_a - L_a x_a)/V_{n+1}$ 恒过 $(x_a,y_a)$、$(x_b,y_b)$。
- **Constant vs variable underflow**：持液量随溶液浓度变（Lₙ 变 → 操作线弯、需试差修正）或恒定（直线操作线，可直接套用 Kremser 式 Eq. 20.24，且 $y_a^* = x_a$、$y_b^* = x_b$）。
- **Liquid-liquid extraction**：extract（萃取相，溶剂+溶质）/ raffinate（萃余相）；选择溶剂改变"化学相似性"而非蒸气压差异；溶剂回收（精馏/汽提）常占成本大头——能用蒸馏就优先蒸馏。
- **Extraction factor E**：$E \equiv K_D V/L$（等价汽提因子 S）；稀溶液单级回收率 $E/(1+E)$，多级错流 $(1+E)^{-N}$，逆流用 Kremser 式。
- **Ternary phase diagrams（三角形相图）**：type I（溶剂只与稀释剂部分互溶，如丙酮-MIK-水，有褶点 plait point）vs type II（溶剂与两者都部分互溶，如苯胺-庚烷-MCH）；tie line 连接共轭两相组成。
- **Modified McCabe-Thiele method**：直角坐标 $y_A$（萃取相）对 $x_A$（萃余相），平衡线止于褶点；操作线因 L 减 V 增而弯曲，需中间点试差。
- **Extraction with reflux（type II 体系）**：溶剂分隔器↔冷凝器、溶剂↔热量的对偶（Table 23.3）；实际工业多用 backwash/countersolvent 变体（Sulfolane 芳烃抽提）。
- **Supercritical fluid extraction（SFE）**：CO₂ 临界点 31.06°C/73.8 bar；高扩散率（~100× 液体）、低黏度、降压/升温即脱溶；咖啡脱咖啡因至 <0.02%。

## Key Concepts
- **Miscella（混合油）**：浸取得到的油-溶剂溶液；half miscella 为中间浓度循环液（Bollman 上行侧喷淋）。
- **Underflow（底流持液）**：固体孔隙携带的溶液，其浓度=该级平衡浓度、其流量决定操作线斜率——浸取设计的核心变量。
- **Stage efficiency in leaching**：溶质在多孔固体内部扩散控制 → 实际级数远多于理想级；不透性固体表面液膜洗涤则效率可取 1。
- **Dispersed phase choice**：流量大者分散以增界面；黏度高者分散以利沉降；无普适规则，按经验定。
- **Redispersion principle**：喷雾塔的传质集中在液滴生成区，加高不增级数——填料/筛板/脉冲的作用是让液滴反复聚并-再分散。
- **Flooding in packed extractors**：式 23.4，$\bar V_{s,c}(1+R^{0.5})^2$ 对给定体系为常数；操作点须低于液泛。
- **Pulse column**：往复脉冲强化分散，无降液管；理想条件下级效率 ~70%（两相体积近等时），通常 ~30%；所需高度不足未脉冲塔的 1/3；主要用于强腐蚀放射性料液。
- **Centrifugal extractor（Podbielniak）**：3–12 atm 下单机 3–10（至多 20）理论级、持液 ~4 s——维生素/抗生素等敏感产品首选。
- **Aqueous two-phase extraction**：PEG/葡聚糖或磷酸盐双水相，各相含水 80–90%，蛋白质不变性；$K_D$ 随 pH 从 0.01 到 >100；缺点是密度差小、沉降慢。

## Key Equations
- 浸取物料衡算：$V_{n+1} + L_a = V_a + L_n$；$V_{n+1}y_{n+1} + L_a x_a = L_n x_n + V_a y_a$
- 浸取操作线：$y_{n+1} = \left(\dfrac{L_n}{V_{n+1}}\right)x_n + \dfrac{V_a y_a - L_a x_a}{V_{n+1}}$
- 浸取平衡：$x_e = y$（溶质全溶、无吸附时固体持液与溢流同浓）
- **Extraction factor**：$E = \dfrac{K_D V}{L}$；单级残余分数 $\dfrac{x_1}{x_0} = \dfrac{1}{1+E}$；N 级错流 $\left(\dfrac{1}{1+E}\right)^N$
- 逆流级数（Kremser 汽提式）：$N = \dfrac{\ln[(x_a - x_a^*)/(x_b - x_b^*)]}{\ln E}$，$x_a^* = y_a/K_D$
- **填料萃取塔液泛**（式 23.4）：$\bar V_{s,c}(1 + R^{1/2})^2 (a_v/g)^{1/2} = \alpha C_1 \varepsilon^{1.54}\left(\dfrac{\Delta\rho}{\rho_d}\right)^{0.41}\left[\dfrac{1}{a_v}\left(\dfrac{\Delta\rho^2 g}{\mu_c^2}\right)^{1/3}\right]^{0.3}\left[\dfrac{\mu_c}{(\Delta\rho\sigma/a_v)^{1/2}}\right]^{0.15}$；$C_1 = 0.28$（Raschig 环/Intalox 鞍），α=1.0（连续相润湿）或 1.2（分散相润湿）
- 三角相图杠杆规则：溶剂加入后混合点位于纯溶剂点与原料点的连线上，过 M 点的 tie line 定两相组成

## Reference Tables
| 设备 | 总处理能力 ft³/ft²·h | HTU, ft | 级效率 % | 典型应用 |
|---|---|---|---|---|
| Mixer-settler | — | — | 75–100 | 润滑油 Duo-Sol |
| Spray column | 50–250 | 10–20 | — | 苛性碱脱盐 |
| Packed column | 20–150 | 5–20 | — | 酚回收 |
| Perforated-plate | 10–200 | 1–20 | 6–24 | 糠醛精制润滑油 |
| Baffle column | 60–105 | 4–6 | 5–10 | 乙酸回收 |
| Agitated tower | 50–100 | 1–2 | 80–100 | 医药/有机品 |
| 脉冲筛板柱 | — | 高度<1/3 未脉冲 | 30（理想 70） | 放射性料液 |
| 离心机 | — | — | 单机 3–10 级 | 抗生素（4 s 停留） |

| 浸取设备 | 固体形态 | 流型 |
|---|---|---|
| Extraction battery (Shanks) | 开放渗透床，固定 | 逆流换罐 |
| Bollman/Rotocel | 片状（大豆） | 移动床逆流 |
| 增稠器+搅拌槽串联 | 分散细粒 | 逆流，恒/变底流 |

## Worked Example
**Ex. 23.1（浸取设计，苯-油粕）**：1000 kg/h 无油干粕，含 400 kg 油、25 kg 苯；新溶剂 655 kg 苯+10 kg 油；要求废粕含油 60 kg。持液量随浓度变化（0.50→0.62 kg/kg）。解法：先试差定废粕底流（$x_b = 0.118$、$L_b = 507$ kg/h）；物料衡算得强溶液 $V_a = 583$ kg/h、$y_a = 0.60$；因 $L_a \ne L$（425 vs ~530–595），第 1 级单独衡算（$x_1 = y_a = 0.60$ → $y_2 = 0.408$），再取中间点 $x_n = 0.30$ → $y_{n+1} = 0.158$ 画微弯操作线；阶梯作图得 **4 个理想级**。

（Ex. 23.2 青霉素：$E = 6\times80/100 = 4.8$；单级回收 82.8%，两级错流 97.0%，逆流级联 N = ln[(100−20.2)/3]/ln4.8 = 2.09 级——逆流用一半溶剂达到同等回收。Ex. 23.3 丙酮-MIK-水：F=100、S=100，99% 回收经 n、m 互试差（水入萃取相 7.1、MIK 入萃余相 1.1）定端点 (0.0074, 0) 与 (0.40, 0.272)，中间点 (0.20, 0.12)，图解得 N = 3.4 级。）

## Anti-patterns
- **忽略底流持液量随浓度的变化**：浓溶液黏度大→持液多→操作线弯曲；按恒 L 作图会低估级数，须按 Table 23.1 类实测数据试差修正。
- **饱和浸取体系中溶剂用量过少**：若饱和出现在第 1 级以外的级，那些级全部失效且釜液残油升高；溶剂投量应使饱和只出现在第 1 级溢流。
- **把喷雾塔加高当作增加级数**：传质集中在液滴生成区；应通过填料/筛板/搅拌实现反复再分散，而非单纯增加高度。
- **能用蒸馏却选萃取而不算总账**：萃取后必须回收溶剂（常靠精馏），组合流程通常比直接精馏更贵；蒸馏不可行（共沸、热敏、沸点重叠）才是萃取主战场。
- **把 backwash 称作 reflux**：回流是与产品同组成的料流；Sulfolane 的反洗剂是低沸（或重石蜡）烃，作用是置换萃取相中的石蜡，概念不同于精馏回流。
- **脉冲柱期待理想级效率**：两相体积不等或萃取体积变化明显时效率从 70% 掉到 ~30%，设计按 30% 取。
- **SFE 忽略高压成本与平衡数据缺口**：溶解度-压力-温度关系复杂、公开数据少，放大前必须实测相平衡。

## Key Takeaways
1. 浸取 = "洗涤的强化版"：平衡条件极简单（$x_e = y$），设计难点全在底流持液与固体内部扩散速率（级效率）上。
2. 恒底流浸取可直接用 Kremser 解析式（$y^* = x$）；变底流则端点+一个中间点画弯操作线，通常够准。
3. 萃取的经济性判据先于设备设计：溶剂回收系统常比萃取器本身贵，流程必须闭合（Sulfolane 水/溶剂循环即为范例）。
4. 稀溶液用 E = K_D V/L 一把抓：单级回收 E/(1+E)，错流乘方，逆流 Kremser；逆流的优势是省溶剂且萃取相更浓（Ex. 23.2 半溶剂同回收）。
5. 三角相图上 tie line 斜率决定溶剂经济性：type I 系统中萃取相 $y_A/y_{H_2O}$ 存在极大值（MIK-丙酮体系在 ~27% 丙酮处），过浓不如适中。
6. 萃取设备选型梯度：干净料液用填料/筛板柱；易乳化用 baffle 塔；需级数多/持液短用搅拌塔或离心机；脏料/含固用 baffle 或 mixer-settler。
7. SFE 三优点（低黏、高扩散、降压脱溶）对应一缺点（高压）；近临界点操作牺牲溶解度换高选择性，适合脱挥发性异味物。

## Connects To
- **Ch. 20**：级联通用理论——操作线、Kremser 式、级效率概念的源头。
- **Ch. 22**：萃取精馏与恒沸精馏共享"第三组分改变分配"逻辑；Sulfolane 流程内含恒沸精馏塔。
- **Ch. 17**：浸取速率由固体内部扩散控制（Fick 定律应用）。
- **Ch. 26**：膜萃取是该章"难分离"路线的延伸。
- **Ch. 30**：溶剂回收精馏塔与多级汽提的设备设计。
