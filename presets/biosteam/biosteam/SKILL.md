---
name: biosteam
description: "用 BioSTEAM（Python）做生物炼制流程模拟、单元操作建模、技术经济分析（TEA）与生命周期评估（LCA）。当用户要求搭建/模拟化工或生物炼制流程、创建 Stream/Unit/System、做精馏设计与计算、设置热力学物性包、或进行 TEA/LCA 分析时使用。触发词：BioSTEAM、生物炼制、流程模拟、精馏塔设计、McCabe-Thiele、MESH 蒸馏、TEA、LCA。"
---

# BioSTEAM 流程模拟

BioSTEAM 是用于生物炼制设计与技术经济分析的 Python 平台，覆盖流程模拟、单元操作、TEA 与 LCA。本技能提供建模流程与非显而易见的 API 约定；详细语法查 `references/`。

## 前置检查

```python
import biosteam as bst
```

未安装时先 `pip install biosteam`。写实际代码用 `bst.preferences.light_mode(save=True)`，不要用 `bst.nbtutorial()`（仅限教程环境）。

## 建模主流程

按此顺序构建，缺哪步查对应 reference：

1. **物性包**：`bst.settings.set_thermo(['Water', 'Ethanol', ...])`（默认理想混合 + Dortmund UNIFAC）。自定义化学品、状态方程见 [references/thermo.md](references/thermo.md)。
2. **Stream**：`feed = bst.Stream(Water=50, Ethanol=20)`（默认 kmol/hr，可用 `units='kg/hr'`）。详见 [references/streams-and-units.md](references/streams-and-units.md)。
3. **Unit**：`M1 = bst.units.Mixer(ins=(a, b), outs='mixed')`。单元间连接优先用管线标记法 `F1 = bst.units.Flash(ins=M1-0, ...)`（`M1-0` 即 `M1.outs[0]`）。
4. **System**：`sys = bst.main_flowsheet.create_system(); sys.simulate()`。含循环的流程、收敛容差与求解器见 [references/systems-and-specs.md](references/systems-and-specs.md)。
5. **结果与成本**：`unit.results()`、`sys.results()`、`sys.save_report('report.xlsx')`。
6. **TEA / LCA**：见 [references/tea-lca.md](references/tea-lca.md)。

精馏建模（BinaryDistillation / ShortcutColumn / MESHDistillation）单独见 [references/distillation.md](references/distillation.md)。端到端示例见 [references/example-sugarcane-ethanol.md](references/example-sugarcane-ethanol.md)。

## 最小可运行骨架

```python
import biosteam as bst

bst.settings.set_thermo(['Water', 'Ethanol'])
feed = bst.Stream(Water=1000, Ethanol=200, units='kg/hr')
D1 = bst.BinaryDistillation(ins=feed, outs=('distillate', 'bottoms'),
                            LHK=('Ethanol', 'Water'),
                            y_top=0.80, x_bot=0.001, k=1.25, is_divided=True)
sys = bst.main_flowsheet.create_system()
sys.simulate()
sys.results()
```

## 关键约定（易错点）

- **ID 自动推断**：`feed = Stream()` 会按变量名推断 ID；未命名时单元按区域字母编号（M=Mixer、D=蒸馏塔、F=闪蒸、P=泵、R=反应器、S=Splitter 等）。
- **公用工程优先级**：只识别 `settings.cooling_agents` / `settings.heating_agents` 列表内的介质；冷却剂应从最热到最冷排序，加热剂从最冷到最热。
- **工艺规格**：用 `@unit.add_specification(run=True)` 在单元运行前调整进料；影响其他单元时传 `impacted_units=[...]`；需要重跑上游的规格设 `sys.N_runs = 2`。见 [references/systems-and-specs.md](references/systems-and-specs.md)。
- **循环收敛失败**：先调 `sys.set_tolerance(mol=..., rmol=..., T=..., rT=...)`，再换求解器 `sys.set_solver('wegstein')` 等（可用列表见 `bst.System.available_methods`）。
- **切换流程图**：`bst.main_flowsheet.set_flowsheet(...)` 后原流程图对象不可再访问。

## References

- [streams-and-units.md](references/streams-and-units.md) — Stream 创建/显示/属性、Unit 创建、内置单元操作、管线标记法、流程图管理
- [systems-and-specs.md](references/systems-and-specs.md) — System 收敛、求解器、解析/数值工艺规格、单元结果与成本
- [distillation.md](references/distillation.md) — 二元/简捷/严格蒸馏、求解器选择
- [thermo.md](references/thermo.md) — 化学品定义、混合物、状态方程、Thermo 对象
- [tea-lca.md](references/tea-lca.md) — 技术经济分析、生命周期评估、偏好设置
- [example-sugarcane-ethanol.md](references/example-sugarcane-ethanol.md) — 从零构建甘蔗乙醇流程的完整示例
