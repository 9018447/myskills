# 术语表

**Activity coefficient 活度系数** — 液相非理想性校正因子，理想溶液≈1。(ch01)

**Azeotrope 共沸物** — 汽液组成相等的点，xy 曲线穿越对角线，构成精馏边界。(ch01,ch05)

**Beer still 蒸馏釜** — 乙醇脱水流程的预浓缩共沸塔。(ch17)

**Cascade control 串级控制** — 温度控制器输出作流量控制器设定值的双回路。(ch07)

**Dead time 死时间** — 操纵变量到响应的纯滞后，动态模拟常需显式加入。(ch07)

**Decanter 倾析器** — 塔顶馏出物液液分相的容器。(ch05,ch17)

**Distillation boundary 精馏边界** — 共沸物分割组成空间的分界，进料只得到所在区域产品。(ch01,ch05)

**Dividing-wall column 隔壁塔** — 单壳三产品节能塔，液相分配比是第4控制自由度。(ch12)

**Dual-temperature control 双温度控制** — 两温度回路分别控塔两端。(ch15)

**Entrainer 夹带剂** — 形成非均相共沸、改变相对挥发度的第三组分。(ch05,ch17)

**External reset feedback 外部复位反馈** — 选择器输出经 Lag 反馈到 PI 积分端，防积分饱和、实现无扰超驰。(ch18)

**Extractive distillation 萃取精馏** — 加高沸点溶剂改变相对挥发度的双塔循环流程。(ch05)

**F factor F因子** — u√ρv，表征塔板气速动能，用于塔径与液泛计算。(ch03)

**Feedforward 前馈** — 测进料流量按比值直接调整操纵变量，常配 Lag 滞后。(ch07,ch16)

**Fenske equation 芬斯克方程** — 全回流下由分离要求算最少理论板数 Nmin。(ch02,ch04)

**First Law of Distillation Control 精馏控制第一定律** — 产品纯度只能由产品流量控制，回流等只影响能耗。(ch08)

**Gap/Overlap 空隙/重叠** — 相邻侧线产品馏程95%与5%点的间隔或交叠。(ch11)

**Heat-integrated columns 热耦合双塔** — 一塔塔顶蒸气作另一塔再沸热源的双效结构。(ch05,ch08)

**Heterogeneous azeotropic distillation 非均相共沸精馏** — 借塔顶分相与有机相回流跨过共沸组成。(ch05,ch17)

**High selector (HS) 高选器** — 取多信号最大值的超驰元件，加固定下限防回路饱和。(ch15)

**Holdup 持液量** — 塔板/反应段停留的液体量，反应精馏中即催化剂量。(ch09)

**Hydraulic lag 水力学滞后** — 液体逐板下流的传递滞后，影响控制板选择。(ch06,ch08)

**Lean/rich solvent 贫/富吸收剂** — CO2吸收-汽提循环中再生后与吸收饱和后的溶剂。(ch14)

**Light/Heavy key (LK/HK) 轻/重关键组分** — 决定塔分离任务的相邻挥发度组分。(ch02)

**Liquid split ratio 液相分配比** — DWC/Petlyuk 预分馏段液相占总液量之比。(ch12)

**McCabe-Thiele method 图解法** — 二元恒摩尔流下用操作线与平衡线逐级作图求理论板数。(ch02)

**MEA absorption 醇胺吸收法** — 化学吸收脱CO2的典型溶剂循环。(ch14)

**Minimum reflux 最小回流比** — 出现夹点（无穷多板）的极限回流比，Underwood 方程求出。(ch02)

**Minimum stages 最少板数** — 全回流极限下的理论板数。(ch02)

**Multiple steady states 多重稳态** — 强非理想塔在同一规定下的多个稳态解。(ch05)

**Neat operation 净操作** — 反应热全部由产品汽化带走、无外部换热的反应精馏操作。(ch05,ch09)

**NLP/SQP 非线性规划** — Aspen Optimization 同步优化的算法，用于 TAC 或利润最大化。(ch04)

**Override control 超驰控制** — 多控制器经选择器竞争操纵同一阀门。(ch18)

**Overflash 过汽化量** — 超出产品所需的汽化分率，保证下部塔板润湿。(ch11)

**Payback period 回收期** — 投资额除以年净收益，与 TAC 共同评估方案。(ch04)

**Petlyuk column 热偶精馏塔** — 预分馏塔与主塔以4条汽液物流耦合的三产品结构。(ch12)

**Pinch point 夹点** — 操作线与平衡线相交处，对应最小回流比。(ch02)

**Preflash tower 预闪蒸塔** — 原油进常压塔前脱轻组分的简单塔。(ch11)

**Pressure-compensated temperature control 压力补偿温度控制** — 用 P-T-x 数据把板温换算为组成后控制，消除压力波动影响。(ch16)

**Pressure Checker 压力一致性原则** — 动态化前核对沿流程压力自进料到产品单调递降。(ch07)

**Pressure-swing distillation 变压精馏** — 用两个不同压力塔跨过随压力变化的共沸点。(ch05)

**Pseudocomponents 虚拟组分** — 原油按馏程切割的假组分，用于石油塔模拟。(ch11)

**Pumparound 中段回流** — 塔中部抽出液体冷却后返回，移走中部热量。(ch11)

**q-line q线** — 进料热状况决定的操作线交点轨迹，q 为进料液相分率。(ch02)

**R/F ratio control 回流/进料比** — 回流与进料成比值的结构，适应处理量变化。(ch07,ch16)

**Reactive distillation 反应精馏** — 反应与分离同塔进行，按挥发度排序与净操作设计。(ch09)

**Rectifier 整流器** — 无冷凝器的顶部塔段，用于汽相侧线流程。(ch10)

**Relative volatility 相对挥发度** — 轻/重组分 (y/x) 之比，越大越易分离，恒α可免泡点迭代。(ch01)

**Relay-feedback test 继电反馈测试** — 继电器使回路极限振荡，测出最终增益与周期供整定。(ch07)

**Residue curve 剩余曲线** — 定压下连续移走汽相的残液组成轨迹，与全回流精馏剖面相同。(ch01)

**Reset windup 积分饱和** — 被覆盖控制器的积分持续累积，重新接管时大幅超调。(ch18)

**Safety response time 安全响应时间** — 从故障注入到关键变量越限的时间。(ch13)

**Second Law of Distillation Control 精馏控制第二定律** — 操纵变量选小流量，避免低负荷时控制阀饱和。(ch15)

**Sensitive tray 灵敏板** — 温度对组成最敏感的塔板，由斜率/灵敏度判据选出，避开进料板。(ch06,ch16)

**Sequential tuning 顺序调谐** — 先整内层（液位/流量）再整外层（温度/组成）回路。(ch10)

**Sidestream 侧线** — 塔中部采出的产品流；液相侧线配汽提塔，汽相侧线配整流器。(ch10)

**Sidestream ratio control 侧线比值控制** — 侧线流量与进料成比例的比值回路。(ch10)

**Slope criterion 斜率判据** — 在温度剖面陡峭处选控制板。(ch06)

**Solvent/Feed ratio 溶剂进料比** — 萃取精馏中溶剂与进料之比，关键设计变量。(ch05)

**SVD 奇异值分解** — 对稳态增益矩阵分解，判断可行控制位置与配对；条件数大则不可行。(ch06,ch10,ch15)

**TAC 总年成本** — 年能耗+设备年折旧，设计优化目标函数，曲线往往平坦。(ch04)

**Tear stream 撕裂流** — 循环流程中人为断开再收敛的物流。(ch05)

**Theoretical stage 理论板** — 汽液达到相平衡的理想接触级。(ch02)

**Turndown 降荷** — 塔在低于设计负荷运行的能力，受塔板漏液下限限制。(ch15)

**Tyreus-Luyben tuning 整定** — 由继电反馈结果整定 PI/PID 的规则（Kc≈Ku/3.2，τI≈3.2Pu）。(ch07)

**Valve position control 阀位控制** — 缓慢调整某流量使另一阀维持近全开，用于浮动压力与节能。(ch15)

**Vapor pressure 蒸气压** — 纯组分指定温度下汽液共存的压力，随温度指数增长。(ch01)

**Txy/xy diagram 二元相图** — 恒压下平衡温度-组成或 y-x 关系图，离对角线越远越易分离。(ch01)

**Feed composition sensitivity (ZSA) 进料组成灵敏度分析** — 改变进料组成考察各板温度变化以选控制板。(ch06)

**Average temperature control 平均温度控制** — 取相邻三板温度均值作被控变量，克服陡峭剖面。(ch08)

**Composition controller 组成控制器** — 直接控制产品纯度的分析仪表回路，常与温度串级。(ch07)

**Reboiler dynamic models 再沸器动态模型** — Constant duty/LMTD/Condensing 三档，安全分析须用严格模型。(ch13)

**5-minute holdup rule 5分钟停留时间定径** — 回流罐与塔釜按5分钟液体停留时间设定尺寸。(ch07)
