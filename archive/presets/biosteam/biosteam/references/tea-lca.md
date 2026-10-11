# 技术经济分析（TEA）、生命周期评估（LCA）与偏好设置

## 1. 技术经济分析（TEA）

### 系统级结果

```python
sys = bst.main_flowsheet.create_system()
sys.simulate()
sys.results()
# 包含：总采购成本、安装设备成本、公用工程成本、物料成本、销售收入
```

### 保存报告

```python
sys.save_report('Example.xlsx')  # 保存为 Excel 报告（需在本机运行）
```

### TEA 对象（需额外设置）

完整的技术经济分析需要定义 TEA 对象，包含：

- 折旧计划
- 工厂寿命
- 建设计划
- 内部收益率（IRR）
- 最低产品销售价格（MPSP）
- 最大原料采购价格（MFPP）

完整 TEA 流程请参考 BioSTEAM 文档第 11 章：https://biosteam.readthedocs.io/

## 2. 生命周期评估（LCA）

### 基本步骤

```python
### 1. 加载系统
from biorefineries import sugarcane as sc
sc.load(pellet_bagasse=False)
system = sc.sugarcane_sys

### 2. 定义特征化因子（来自 GREET 2020，按 kg 基准）
# 影响指标：GWP 100yr, 单位: kg*CO2e

### 3. 执行 LCA（三种分配方法）
# - 能量分配（Energy based）
# - 收入分配（Revenue based）
# - 替代分配（Displacement allocation / system expansion）
```

### 甘蔗乙醇 GWP 结果

| 分配方法 | GWP [kg CO2e/kg 乙醇] |
|---|---|
| 替代分配（Displacement） | **-0.44** |
| 能量分配（Energy） | **0.39** |
| 收入分配（Revenue） | **0.43** |

排除热电联产时，蔗渣燃烧用于现场蒸汽和发电的 GWP 置换值：**0.45 kg CO2e/kg**

建议：进行生物炼制环境评估时，应结合多种分配方法并关注系统边界设定，以确保结果全面可靠。

## 3. 偏好设置

```python
import biosteam as bst

# 亮色/暗色模式
bst.preferences.light_mode(save=True)   # 亮色模式并保存

# 单位显示
bst.preferences.display_units['T'] = 'degC'    # 温度默认显示°C
bst.preferences.display_units['P'] = 'atm'     # 压力默认显示atm

# 成分显示
bst.preferences.max_elements = 15     # 最多显示15种成分

# 图表工具提示
bst.preferences.tooltips = True       # 开启工具提示

# 自动显示
bst.preferences.autoshow = True       # 自动显示图表

# 保存偏好设置
bst.preferences.save()

# 重置为默认
bst.preferences.reset()
```

## 参考文献

1. Seider, W. D.; Lewin, D. R.; Seader, J. D.; Widagdo, S.; Gani, R.; Ng, M. K. *Product and Process Design Principles*; Wiley, 2017.
2. Cortes-Peña, Y.; Kumar, D.; Singh, V.; Guest, J. S. BioSTEAM: A Fast and Flexible Platform for the Design, Simulation, and Techno-Economic Analysis of Biorefineries under Uncertainty. *ACS Sustainable Chem. Eng.* 2020.
3. Huang, H.; Long, S.; & Singh, V. Techno-economic analysis of biodiesel and ethanol co-production from lipid-producing sugarcane. *Biofuels, Bioproducts and Biorefining*, 2016.
4. Green, D. W. *Perry's Chemical Engineers' Handbook*, 9 ed.; McGraw-Hill Education, 2018.
5. BioSTEAM Development Group. BioSTEAM Documentation. https://biosteam.readthedocs.io/
