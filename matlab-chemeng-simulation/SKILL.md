---
name: matlab-chemeng-simulation
description: "《实用化工计算机模拟——MATLAB在化学工程中的应用》（黄华江，化工出版社2004）全书知识库：9章结构化摘要覆盖MATLAB编程基础、数值分析、化工ODE/PDE求解、最优化、参数估计与模型辨识、实验设计、神经网络，含130个实例的程序-函数对照与作者决策规则。当用户需要用MATLAB求解化工数值问题（反应器/精馏/吸收/传质模拟、插值拟合、方程求根、ODE/PDE、优化、动力学参数估计、正交实验/D-最优设计、神经网络）、选择数值方法或求解器、排查计算失败原因时使用。"
---

# MATLAB 化工计算机模拟知识库

## 来源

黄华江《实用化工计算机模拟——MATLAB在化学工程中的应用》，化学工业出版社 2004.6，ISBN 7-5025-5658-3。华东理工大学研究生教材，作者为联合化学反应工程研究所博士（壁冷式固定床反应器控制系统方向）。全书约130个亲手编写的MATLAB实例，每个含算法、数学模型、程序清单、计算结果。

作者核心方法论：**"拿来就用"省略法**——不自己实现数值算法（省去传统五步编程法的算法设计与验证步骤），直接组装 MATLAB 内建函数与工具箱求解化工模型。本技能传承这一方法：先正确识别问题类型，再选对函数。

## 使用路径

1. **先查本文件的「问题路由决策树」**确定问题类型和对应函数。
2. **需要函数速查或失败排查** → 读 `cheatsheet.md`（任务→函数表 + 求解器决策规则）。
3. **需要"何时用什么方法"的完整判据** → 读 `patterns.md`（45条 When→do→because 决策规则）。
4. **需要术语定义** → 读 `glossary.md`。
5. **需要某主题的深入细节、代码示例、完整例题** → 读对应 `chapters/chNN-*.md`。

## 问题路由决策树

拿到化工计算问题，依次判断：

```
是微分方程吗？
├─ 是 ODE → 有条件全在起点吗？
│   ├─ 是 → IVP：ode45（默认；长时间无输出/解异常 → ode23s 刚性切换）
│   └─ 否（两端边界：催化剂颗粒、管流分布）→ BVP：bvp4c + bvpinit + deval
├─ 是 PDE → 一维动态？→ pdepe（优先）或自写 Crank-Nicolson+TDMA
│          → 二维？→ pdetool（≤2方程）或 assempde/parabolic/pdenonlin
└─ 否 → 是代数方程吗？
    ├─ 单变量（泡点/闪蒸/蒸馏/转化率/管径）→ fzero
    ├─ 方程组（化学平衡/多稳态/稳态模拟）→ fsolve
    └─ 是优化吗？
        ├─ 有约束/非线性规划 → fmincon（@nonlcon 打包约束）
        ├─ 无约束低维 → fminsearch；单变量闭区间 → fminbnd
        ├─ 线性规划 → linprog；二次规划 → quadprog
        └─ 多目标 → fgoalattain
是数据回归吗？
├─ 参数估计（动力学/van Laar/生化）→ 线性化出初值 → lsqnonlin 精修 → nlparci 出区间
├─ ODE模型参数 → 积分法（lsqnonlin内嵌ode45），比微分法置信区间窄
├─ 模型筛选 → 四统计量（ρ²、F比、置信区间、后验概率），不能只比残差
└─ 实验点怎么选 → 正交表（极差/方差分析）或 D-最优（cordexch+nlinfit）
都不是 → 神经网络（BP:newff / RBF:newrb / GRNN:newgrnn / 线性:newlind）
```

## Chapter Index

| 文件 | 章 | 核心内容 |
|---|---|---|
| `chapters/ch01-overview.md` | 1 化工模拟计算概述 | 模拟策略、商用软件对比（Aspen/Fluent vs MATLAB）、混合编程、"拿来就用"方法 |
| `chapters/ch02-matlab-basics.md` | 2 MATLAB编程基础 | 程序框架、函数句柄@fun+feval、向量化/预分配提速（27倍差距）、调试 |
| `chapters/ch03-numerical-analysis.md` | 3 数值分析 | 插值vs拟合判据、quadl积分、fzero/fsolve分工与初值策略、刚性判据、bvp4c标准化 |
| `chapters/ch04-ode-solvers.md` | 4 常微分方程化工应用 | 25例：间歇/CSTR/管式/半连续反应器、精馏、吸收、催化剂颗粒bvp4c、生化、膜反应器、闭环控制 |
| `chapters/ch05-pde-solvers.md` | 5 偏微分方程 | B²−4AC分类、Crank-Nicolson+TDMA、对称正交配置、MOL、pdepe、PDE工具箱FEM、柱坐标伪装 |
| `chapters/ch06-optimization.md` | 6 最优化方法 | 自由度判定、fminbnd/linprog/fminsearch/quadprog/fmincon(SQP)/fgoalattain、庞特里阿金极大值原理、CSTR/换热器最优设计 |
| `chapters/ch07-parameter-estimation.md` | 7 参数估计与模型辨识 | 微分法vs积分法、多响应加权最小二乘(1/σ²)、Kittrell变换、fmincon+lsqnonlin串联、四统计量模型辨识 |
| `chapters/ch08-doe-data-processing.md` | 8 实验设计及数据处理 | 正交表选择（自由度预算）、极差分析、方差分析、D-最优设计cordexch |
| `chapters/ch09-neural-networks.md` | 9 神经网络 | newlind/newlin+adapt、BP newff（tansig+purelin）、RBF newrb、GRNN newgrnn、HPLC流动相模拟、数学符号→MATLAB映射 |

## Topic Index（问题 → 章节）

- **反应器动态模拟**（间歇/CSTR/PFR/半连续、开车、多稳态）→ ch4；稳态化 → ch3/fsolve
- **催化剂颗粒**（有效因子η、Thiele模数、浓度分布）→ ch4（bvp4c）、ch5（pdepe圆柱/FEM）
- **精馏/吸收/传质**（理论板N_OG、填料高度、多组分扩散）→ ch3（积分）、ch4（动态）
- **传热/热传导**（1维/2维、固定床、裂纹传热）→ ch5
- **流体流动**（管内层流、非牛顿管径）→ ch3（fzero）、ch4（bvp4c）、ch5（FEM）
- **生化过程**（Monod发酵、氧传递）→ ch4；青霉素发酵参数估计 → ch7
- **最优设计/最优控制**（冷却器、换热器系列、CSTR最优设计、最优温度分布）→ ch6
- **动力学参数估计**（速率方程、酶催化、van Laar VLE）→ ch7；实验设计配合 → ch8
- **实验数据处理**（正交表、交互作用、显著性）→ ch8
- **数据插值/拟合/微分/积分**（发酵数据、RTD）→ ch3
- **神经网络预测/函数逼近**（线性预测、HPLC流动相）→ ch9

## 关键原则（全书高频教训）

1. **ode45 先行**：化工IVP多数非刚性；刚性征兆（慢、异常）才切 ode23s。
2. **初值决定成败**：fsolve/bvp4c/优化的初值都不是随手取的（闪蒸须在两相区、bvpinit 猜测须物理合理）。
3. **线性化只当初值发生器**：严格统计靠 lsqnonlin+nlparci。
4. **模型好坏≠残差最小**：置信区间比参数值还大的模型必须淘汰。
5. **MATLAB提快三板斧**：向量化、预分配、内建函数。
