---
name: unit-operations-chemeng
description: "《化工单元操作》(McCabe, Smith & Harriott, Unit Operations of Chemical Engineering, 6e) 全书知识库：29 章结构化摘要，覆盖流体力学、传热、传质与分离、颗粒固体四大板块与 6 条通用框架。用于解答单元操作与传递过程问题（管流压降、泵与流量计、搅拌、换热器、蒸发、精馏、吸收、萃取、干燥、结晶、膜分离、过滤离心等）、查设计判据与经验值、按原书方法推演工程计算。当问题涉及化工单元操作、传递过程原理或设备设计估算时使用。"
---

# Unit Operations of Chemical Engineering — 工作知识库

来源：McCabe, Smith & Harriott, *Unit Operations of Chemical Engineering*, 6th ed.（1132 页扫描版，MinerU OCR 抽取后按章提炼；BOOK_TYPE=technical，DEPTH=study）。

## 使用方式

- **快速查决策规则、经验值、临界判据** → 读 `cheatsheet.md`（≤1200 tokens，先查这个）
- **查术语定义** → `glossary.md`；**查命名方程与通用解题套路** → `patterns.md`
- **深入某个单元操作** → 读对应 `chapters/chNN-*.md`（每章 2000–3000 tokens：关键术语、命名方程、决策规则、例题要点、章节连接）
- **附录图表** → `appendix.md`（无因次数群、钢管尺寸、Tyler 筛、导热系数表）

## 全书架构（5 篇 29 章）

- **Section I 导论**（ch1）：单位、量纲、衡算语言
- **Section II 流体力学**（ch2–9）：静力学 → 黏性与流态 → 管流 → 可压缩流 → 绕流与床层 → 输送计量 → 搅拌
- **Section III 传热**（ch10–16）：导热 → 对流传热原理 → 相变 → 辐射 → 换热设备 → 蒸发
- **Section IV 传质与分离**（ch17–27）：扩散原理 → 吸收 → 增湿 → 级联理论 → 精馏（二元/多组分）→ 浸取萃取 → 干燥 → 固定床 → 膜
- **Section V 颗粒固体**（ch28–29）：散体性质与处理 → 机械分离

## 核心框架（贯穿全书的 6 条主线）

1. **衡算优先**：任何单元操作先做物料/能量/动量衡算（ch4）；机械能衡算的 Bernoulli 工作式（含损失项 $\eta W_p - \Sigma h_f$）是流体问题的万能起点。
2. **摩擦系数统一阻力**：管流 Fanning $f$（ch5）、绕流 $C_D$（ch7）、固定床 Ergun（ch7）、搅拌功率数 $N_P$（ch9）同属"应力/惯性归一化"；Colburn 类比 $j_H = j_M = f/2$ 打通动量–热量–质量三传（ch12/17）。
3. **传热 = 阻力串联 × 对数平均推动力**：$q = UA\overline{\Delta T_L}$（ch11）；分系数 $h$ 按流态分流域求（ch12），相变单独处理（ch13 Nusselt 膜状冷凝、沸腾四区曲线），辐射用 $\sigma T^4$ + 视角因子 + 灰体互换因子（ch14）。
4. **级联操作统一理论**：操作线 + 平衡线 + 夹紧点（ch20）；解析解 Kremser（吸收/汽提/浸取）、图解 McCabe–Thiele（二元精馏）、传质单元 $Z_T = H_{Oy}N_{Oy}$（填料塔）三种算法按体系选择。
5. **传质两膜阻力分解**：$1/K_y = m/k_x + 1/k_y$（ch17）；控制阻力判据决定强化方向——m≫1 液膜控制（CO₂-水）、m≪1 气膜控制（NH₃），加错方向的流速是无效功（ch18）。
6. **颗粒过程两大量 + 两大放大参数**：沉降速度 $u_t$ 与最小流化速度 $\bar V_{0M}$（ch7）；过滤按比滤阻 $\alpha$–$\Delta p$ 数据放大、离心按 $\Sigma$ 等效面积放大、旋流按分离因子 $u^2/(rg)$ 折算（ch29）。

## 章节索引

| 文件 | 章 | 一句话核心 |
|---|---|---|
| `ch01-definitions-principles.md` | 1 定义与原理 | 单位制与量纲分析、气体 PVT、物料/能量衡算入门 |
| `ch02-fluid-statics.md` | 2 流体静力学 | 静水平衡与压差计；离心场中的等压面与中性区 |
| `ch03-fluid-flow-phenomena.md` | 3 流动现象 | Newton 黏性定律、层流/湍流与 Re 判据、湍流应力与边界层 |
| `ch04-basic-equations-fluid-flow.md` | 4 流动基本方程 | 质量/能量/动量三大衡算 + Bernoulli 机械能衡算工作式 |
| `ch05-incompressible-pipes-channels.md` | 5 不可压缩管渠流 | Fanning 摩擦系数串起速度分布、沿程与局部损失、非圆/非牛顿流 |
| `ch06-compressible-flow.md` | 6 可压缩流 | 马赫数统一喷管等熵流、Fanno 绝热摩擦流与等温摩擦流；核心现象是壅塞 |
| `ch07-flow-past-immersed-bodies.md` | 7 绕流 | $C_D$–$Re_p$ 曲线统一绕流、沉降、固定床 Ergun 与流化 |
| `ch08-transportation-metering-fluids.md` | 8 输送与计量 | 泵/风机/压缩机选型（NPSH、相似定律）与压差/面积/插入式流量计 |
| `ch09-agitation-mixing.md` | 9 搅拌与混合 | 功率数–雷诺数曲线、混合时间、悬浮临界转速与放大权衡 |
| `ch10-heat-transfer-conduction.md` | 10 导热 | Fourier 定律 + 热阻串联；Fo/Bi 体系解非稳态冷却与半无限穿透 |
| `ch11-heat-flow-in-fluids.md` | 11 流体间传热原理 | 焓平衡定负荷 → LMTD 定推动力 → 阻力串联合成 U |
| `ch12-heat-transfer-no-phase-change.md` | 12 无相变对流传热 | 层流 Graetz / 过渡查图 / 湍流 Sieder–Tate 分流域求膜系数 |
| `ch13-heat-transfer-phase-change.md` | 13 有相变传热 | Nusselt 冷凝液膜理论 + 沸腾四区曲线，绝不越过临界温差 |
| `ch14-radiation-heat-transfer.md` | 14 辐射传热 | $\sigma T^4$ 发射、视角因子几何路由、灰体互换因子修正 |
| `ch15-heat-exchange-equipment.md` | 15 换热设备 | 壳管/板式/翅片/刮面的 U 值与结构选型；ε–N_H 法定出口温度 |
| `ch16-evaporation.md` | 16 蒸发 | 多效与 MVR 两条经济性路线；BPE 吃掉有效温差 |
| `ch17-diffusion-mass-transfer.md` | 17 扩散与相际传质原理 | Fick 定律 + 膜/边界层/渗透理论谱系 + 两膜阻力串联 |
| `ch18-gas-absorption.md` | 18 气体吸收 | 塔径走水力学（Eckert 半泛点）、塔高走传质（$H_{Oy} \cdot N_{Oy}$） |
| `ch19-humidification.md` | 19 增湿操作 | 湿度图、绝热饱和与湿球温度、凉水塔设计 |
| `ch20-equilibrium-stage-operations.md` | 20 平衡级操作 | 操作线 + 平衡线统一级联操作；Kremser 解析解 |
| `ch21-distillation.md` | 21 精馏 | McCabe–Thiele 全流程图解设计（q 线、Fenske、Gilliland） |
| `ch22-multicomponent-distillation.md` | 22 多组分精馏 | LK/HK 关键组分语言 + Fenske–Underwood–Gilliland 群法链 |
| `ch23-leaching-extraction.md` | 23 浸取与萃取 | 底流/溢流决定浸取操作线；三元相图与萃取级数 |
| `ch24-drying-solids.md` | 24 固体干燥 | 恒速/降速两段机制、临界湿含量与干燥器选型 |
| `ch25-fixed-bed-separations.md` | 25 固定床分离 | 穿透曲线与 LUB 统摄吸附/离子交换/色谱 |
| `ch26-membrane-separations.md` | 26 膜分离 | 溶解扩散、Knudsen、渗析、RO 四机理与驱动力 |
| `ch27-crystallization.md` | 27 结晶 | 过饱和驱动成核+生长；MSMPR 总体衡算定粒度分布 |
| `ch28-particulate-solids-handling.md` | 28 颗粒固体性质与处理 | 粒径表征、Bond 粉碎能耗、仓斗流型与混合 |
| `ch29-mechanical-separations.md` | 29 机械分离 | 筛/滤/沉降/离心/旋流的机理与放大（α–Δp、Σ、分离因子） |

## 主题索引（按英文字母序）

- Absorption 气体吸收 → ch18 ｜ Agitation 搅拌 → ch9
- Boiling & condensation 沸腾与冷凝 → ch13 ｜ Boundary layer 边界层 → ch3/ch7/ch12
- Compressible flow 可压缩流 → ch6 ｜ Conduction 导热 → ch10
- Crystallization 结晶 → ch27 ｜ Cyclone 旋风分离 → ch29
- Drying 干燥 → ch24 ｜ Dimensional analysis 量纲分析 → ch1
- Energy/material balances 衡算 → ch1/ch4 ｜ Evaporation 蒸发 → ch16
- Extraction & leaching 萃取与浸取 → ch23 ｜ Filtration 过滤 → ch29
- Fluid statics 流体静力学 → ch2 ｜ Fluidization 流化 → ch7
- Heat exchangers 换热器 → ch15 ｜ Humidification & cooling towers 增湿与凉水塔 → ch19
- Membranes 膜分离 → ch26 ｜ Metering 流量计量 → ch8
- Mixing & agitation → ch9 ｜ Non-Newtonian fluids 非牛顿流 → ch5
- Pumps & compressors 泵与压缩机 → ch8 ｜ Radiation 辐射 → ch14
- Sedimentation & centrifugation 沉降与离心 → ch7/ch29 ｜ Settling velocity 沉降速度 → ch7
- Stage operations 级联操作 → ch20 ｜ Steady/unsteady conduction → ch10
- Transport properties 传递性质 → ch17 ｜ Fixed-bed adsorption/ion exchange/chromatography → ch25
- Distillation 精馏 → ch21（二元）/ ch22（多组分）｜ Particulate solids 颗粒固体 → ch28

## 配套文件

| 文件 | 内容 |
|---|---|
| `cheatsheet.md` | 全书决策规则与经验值速查（先查） |
| `glossary.md` | 关键术语定义（按篇章分组） |
| `patterns.md` | 命名方程速查 + 通用解题套路 + 跨章连接 |
| `appendix.md` | 附录 5 张数据表索引（无因次数群、钢管、Tyler 筛、导热系数） |
| `chapters/` | 29 个章节摘要文件 |

## 范围与限制

- 基于 OCR 全文（~581K tokens）提炼；正文、公式、表格文字已抽取，但**原书约 520 处图片引用未读**——图解法图表（Heisler 图、湿度图、Eckert 图、McCabe–Thiele 例图等）未数字化，需要图解时按 `patterns.md` 的解析替代法或查原书。
- 各章 Worked Example 为浓缩重构（保留条件、关键步骤与结果数字），非原文照抄。
- 原书为英制/工程单位制混用，例题数值保留原书单位；符号遵循原书记法（如 $N_{Re}$、$N_P$、$H_{Oy}$、$F_p$）。
- 版权提示：本书为第三方版权书籍，此技能包仅供个人学习研究使用，请勿再分发。
