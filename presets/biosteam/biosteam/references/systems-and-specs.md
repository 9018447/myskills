# System、工艺规格与结果

## 1. System 系统与循环收敛

### 创建与模拟系统

```python
# 推荐方式：通过 flowsheet 创建
sys = bst.main_flowsheet.create_system()
sys.simulate()
sys.show()
sys.diagram()

# 系统级结果：总采购成本、安装设备成本、公用工程成本、物料成本、销售收入
sys.results()
```

### 收敛设置

默认容差：

| 参数 | 默认值 |
|---|---|
| `System.default_maxiter` | 200 |
| `System.default_molar_tolerance` | 1.0 kmol/hr |
| `System.default_relative_molar_tolerance` | 0.01 |
| `System.default_temperature_tolerance` | 0.10 K |
| `System.default_relative_temperature_tolerance` | 0.001 |
| `System.default_methods['Sequential modular']` | 'Aitken' |

自定义容差：

```python
# 对整个系统设置更严格的容差
sys.set_tolerance(mol=1e-9, rmol=1e-9, T=1e-5, rT=1e-5)

# 更改全局默认值（影响之后创建的所有系统）
System.default_molar_tolerance = 0.01
System.default_relative_molar_tolerance = 1e-4
```

### 求解器

```python
# 可用求解器
bst.System.available_methods
# ['aitken', 'wegstein', 'fixedpoint', 'anderson', 'diagbroyden',
#  'excitingmixing', 'linearmixing', 'broyden1', 'broyden2']

sys.set_solver('diagbroyden')

# 注册自定义求解器（scipy）
from scipy.optimize import root
bst.System.register_method(
    name='hybr', solver=root,
    options=dict(xtol=1e-24, maxfev=int(1e6), method='hybr')
)
sys.set_solver('hybr')
```

### 处理复杂过程规格（N_runs）

当过程规格需要重跑上游单元时：

```python
@mixer.add_specification
def adjust_fresh_flow():
    feed_a.imol['Water'] = target - feed_b.imol['Water']
    mixer.run()

sys.N_runs = 2    # 模拟时运行两次
sys.empty_recycles()
sys.simulate()
```

## 2. 工艺规格

两类规格：

- **解析规格**：在系统单循环内直接求解
- **数值规格**：通过数值方法迭代求解

### 解析规格

示例：变性乙醇燃料调配（目标：2 wt.% 变性剂）

```python
dehydrated_ethanol = Stream(T=340, Water=0.1, Ethanol=99.9, units='kg/hr')
denaturant = Stream(Octane=1)
M1 = units.Mixer('M1', ins=(dehydrated_ethanol, denaturant), outs='denatured_ethanol')

@M1.add_specification(run=True)  # 规格函数执行后运行质量能量平衡
def adjust_denaturant_flow():
    denaturant_over_ethanol_flow = 0.02 / 0.98  # 质量比
    denaturant.imass['Octane'] = denaturant_over_ethanol_flow * dehydrated_ethanol.F_mass

M1.simulate()
```

示例：玉米浆固含量控制（目标：32 wt.% 固含量）

```python
@M1.add_specification(
    run=True,
    args=[0.32],  # 传递参数给规格函数
)
def adjust_water_flow(solids_content):
    F_mass_moisture = corn_feed.imass['Water']
    F_mass_solids = corn_feed.F_mass - F_mass_moisture
    water_solids_ratio = (1 - solids_content) / solids_content
    dilution_water.imass['Water'] = F_mass_solids * water_solids_ratio
```

使用 impacted_units（确保受影响单元按正确顺序重跑）：

```python
P1 = units.Pump(ins=dilution_water, P=5 * 101325)
H1 = units.HXutility(ins=P1-0, T=350)
M1.ins.append(H1-0)

M1.specifications.clear()
M1.add_specification(
    adjust_water_flow,
    args=[0.32],
    run=True,
    impacted_units=[P1],  # 稀释水连接到 P1
)
```

### 数值规格

示例：闪蒸 50 wt.% 的液体

```python
mixture = Stream(T=340, Water=1000, Ethanol=1000, Propanol=1000, units='kg/hr')
F1 = units.Flash(ins=mixture, outs=('vapor', 'liquid'), T=373, P=101325)

@F1.add_bounded_numerical_specification(x0=351.4, x1=373, xtol=1e-9, ytol=1e-3)
def f(x):
    F1.T = x
    F1.run()
    feed = F1.ins[0]
    vapor = F1.outs[0]
    V = vapor.F_mass / feed.F_mass
    return V - 0.5

system = main_flowsheet.create_system()
system.simulate()
```

## 3. 单元操作结果与成本

### 模拟后的结果存储

```python
# 模拟前为空
D1.design_results    # -> {}
D1.purchase_costs    # -> {}
D1.heat_utilities    # -> []
D1.power_utility     # -> PowerUtility 对象

# 模拟后填充
D1.simulate()
D1.design_results    # 设计结果字典
D1.purchase_costs    # 采购成本字典
D1.heat_utilities    # HeatUtility 对象列表
```

### 统一查看结果

```python
D1.results()          # 以 DataFrame 返回全部结果
D1.results(basis='SI')  # SI 单位制

# 获取特定设计结果及单位
D1.get_design_result('Rectifier height', 'meter')  # 返回米为单位的值

# 设计结果单位字典
D1._units
```

### Flash 示例结果

| 类别 | 项目 | 数值 |
|---|---|---|
| Utility | Low pressure steam Duty | 5.92e+05 kJ/hr |
| | Low pressure steam Cost | 3.06 USD/hr |
| Design | Vessel type | Horizontal |
| | Length | 1.96 m |
| | Diameter | 1.22 m |
| | Weight | 624 kg |
| | Wall thickness | 0.00794 m |
| | Vessel material | Carbon steel |
| Purchase cost | Horizontal pressure vessel | 1.12e+04 USD |
| | Platform and ladders | 3.21e+03 USD |
| | Heat exchanger - Double pipe | 4.3e+03 USD |
| **Total purchase cost** | | **1.87e+04 USD** |
| **Utility cost** | | **3.06 USD/hr** |

### 精馏塔结果示例（部分）

| 设计项目 | 数值 |
|---|---|
| Theoretical feed stage | 26 |
| Theoretical stages | 31 |
| Minimum reflux | 0.771 |
| Reflux | 0.964 |
| Rectifier height | 78.9 ft |
| Rectifier diameter | 9.96 ft |
| Rectifier weight | 4.18e+04 lb |

| 采购成本项目 | USD |
|---|---|
| Rectifier trays | 9.02e+04 |
| Rectifier tower | 1.54e+05 |
| Condenser - Floating head | 6.58e+04 |
| Reboiler - Floating head | 6.67e+04 |
| **Total purchase cost** | **5.88e+05** |
| **Utility cost** | **390 USD/hr** |
