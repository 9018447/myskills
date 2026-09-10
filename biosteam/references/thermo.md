# 热力学属性包

## 1. 基本设置

```python
# 简单方式：直接传入化学品名称（自动使用理想混合+UNIFAC活度系数）
settings.set_thermo(['Water', 'Methanol'])
settings.set_thermo(['Water', 'Ethanol', 'Glycerol', 'Yeast'], db='BioSTEAM')

# 使用 Peng-Robinson 状态方程
settings.set_thermo(hydrocarbons, pkg='Peng Robinson')
```

## 2. 创建化学品

```python
import biosteam as bst

# 从数据库直接获取
chemicals = bst.Chemicals(['Water', 'Ethanol', 'Octane'])

# 指定相态
chemicals = bst.Chemicals([
    'Water',                                # 液相（默认）
    'Ethanol',
    bst.Chemical('Glucose', phase='s'),     # 始终为固体
    bst.Chemical('CO2', phase='g'),         # 始终为气体
    bst.Chemical('O2', phase='g'),
])

# 定义不在数据库中的化学品
Cellulose = bst.Chemical(
    'Cellulose',
    Cp=1.364,           # 热容 [kJ/kg]
    rho=1540,           # 密度 [kg/m³]
    default=True,       # 其他性质取水的默认值
    search_db=False,    # 不搜索数据库
    phase='s',
    formula="C6H10O5",  # 分子式（自动计算分子量）
    Hf=-975708.8,       # 生成热 [J/mol]
)

# 为化学品设置别名
DryYeast = bst.Chemical(
    'DryYeast', rho=1540, default=True,
    search_db=False, phase='s', MW=1.,
    aliases={'Yeast'}   # 别名，后续可用 'Yeast' 引用
)

# 编译（顺序变为不可变）
chemicals.compile()
chemicals.show()
```

## 3. 混合物与状态方程

```python
# 理想混合物（默认）
ideal_mixture = bst.IdealMixture.from_chemicals(chemicals)
# IdealMixture(... include_excess_energies=False) - 默认忽略超额能量

# Peng-Robinson 状态方程
PR_mixture = bst.mixture.PRMixture.from_chemicals(chemicals)

# Soave-Redlich-Kwong 状态方程
SRK_mixture = bst.SRKMixture.from_chemicals(chemicals)

# 全部可用混合物类
bst.mixture.mixture_classes
# IdealMixture, PRMixture, SRKMixture, PR78Mixture, ...
```

混合物性质计算示例：

```python
# 单相性质
mol = chemicals.array(['Water', 'Ethanol'], [2, 2])        # [kmol/hr]
H = ideal_mixture.H('l', mol, T=300, P=101325)             # 焓 [kJ/hr]
Cn = ideal_mixture.Cn('l', mol/mol.sum(), T=300)           # 热容 [J/kmol/K]

# 多相性质
mol_liquid = chemicals.array(['Water', 'Ethanol'], [2, 2])
mol_vapor = chemicals.array(['Water', 'Ethanol'], [2, 2])
phase_data = [('l', mol_liquid), ('g', mol_vapor)]
H = ideal_mixture.xH(phase_data, T=300, P=101325)
```

## 4. 编译为 Thermo 对象

```python
# 完整方式
thermo = bst.Thermo(chemicals, mixture=ideal_mixture)
bst.settings.set_thermo(chemicals, mixture=ideal_mixture)

# 快速方式（使用默认 IdealMixture + Dortmund UNIFAC）
bst.settings.set_thermo(chemicals)
```

Thermo 对象包含三个子类：

- **ActivityCoefficients**：活度系数（默认 Dortmund modified UNIFAC）
- **FugacityCoefficients**：逸度系数（默认 Ideal，即 =1）
- **PoyintingCorrectionFactors**：Poyinting 校正因子（默认 Mock，即 =1）

使用状态方程设置物性：

```python
# 设置 SRK 状态方程
bst.settings.set_thermo(chemicals, mixture=SRK_mixture, Phi=bst.SRKFugacityCoefficients)

# 使用 CoolProp 计算热容
N2 = Chemical('N2')
N2.Cn.l.method = N2.Cn.g.method = "COOLPROP"  # 可能需要 pip install coolprop
N2.reset_free_energies()
```

## 5. 过程经济设置

```python
# CEPCI（化学工程工厂成本指数）
settings.CEPCI = 603.1  # 默认 567.5（2017年）

# 电力价格
settings.electricity_price = 0.065  # USD/kWhr（默认 0.0782）

# 公用工程（UtilityAgent）
lps = settings.get_heating_agent('low_pressure_steam')
lps.show()
# UtilityAgent: low_pressure_steam
# price: 0.238 USD/kmol at 95% efficiency
# phase: 'g', T: 412.19 K, P: 344738 Pa
# composition: 100% Water

# 冷却剂列表
settings.cooling_agents  # cooling_water, chilled_water, chilled_brine, propane, propylene, ethylene

# 加热剂列表
settings.heating_agents   # low_pressure_steam, medium_pressure_steam, high_pressure_steam, natural_gas

# 修改冷却剂
settings.cooling_agents = settings.cooling_agents[:-3]  # 移除丙烷、丙烯、乙烯制冷剂

# 添加自定义制冷剂
Ammonia = bst.Chemical('Ammonia')
P = 101325 * 1.2
T = Ammonia.Tsat(P)
ammonia = bst.UtilityAgent(
    Ammonia=1, P=P, T=T, phase='l',
    thermo=bst.Thermo([Ammonia]),
    heat_transfer_price=13.17e-6,
)
settings.cooling_agents.append(ammonia)
```

**优先级规则**：BioSTEAM 只识别 `settings.cooling_agents` 和 `settings.heating_agents` 中的公用工程。顺序决定优先级——冷却水优先于冷冻水（因其在列表中靠前）。加热剂应从最冷到最热排序，冷却剂应从最热到最冷排序。
