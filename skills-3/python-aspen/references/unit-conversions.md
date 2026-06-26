# Aspen 单位制与换算参考

## Aspen 默认单位集

### MET (公制单位集) - 推荐
这是最常用的单位集，化工计算中的标准配置。

| 物理量 | Aspen 单位 | 常见替代单位 | 换算关系 |
|--------|-----------|-------------|---------|
| 温度 | °C | K, °F | K = °C + 273.15 |
| 压力 | bar | kPa, MPa, atm, mmHg | 1 bar = 100 kPa = 0.1 MPa |
| 质量流量 | kg/h | kg/s, t/h | 1 t/h = 1000 kg/h |
| 摩尔流量 | kmol/h | mol/s, lbmol/h | 1 kmol/h = 0.2778 mol/s |
| 体积流量 | m³/h | L/h, ft³/h | 1 m³/h = 1000 L/h |
| 焓 | kJ/kmol | kJ/kg, Btu/lbmol | 1 kJ/kmol = 0.001 kJ/mol |
| 热负荷 | kW | kcal/h, Btu/h | 1 kW = 3600 kJ/h = 860 kcal/h |

### SI (国际单位制)
| 物理量 | Aspen SI 单位 | 与 MET 差异 |
|--------|--------------|----------|
| 温度 | K | SI 用开尔文，MET 用摄氏度 |
| 压力 | Pa | SI 用帕斯卡，MET 用 bar |
| 质量 | kg | 相同 |
| 摩尔 | mol | SI 用 mol，MET 用 kmol |

### ENG (英制单位集)
| 物理量 | Aspen ENG 单位 | 与 MET 换算 |
|--------|--------------|----------|
| 温度 | °F | °C = (°F - 32) × 5/9 |
| 压力 | psi | 1 bar = 14.504 psi |
| 质量 | lb | 1 kg = 2.205 lb |
| 流量 | lbmol/h | 1 kmol/h ≈ 2.205 lbmol/h |

## 常见单位换算函数

```python
def convert_pressure_to_bar(value, from_unit='kPa'):
    """
    将压力值从指定单位转换为 bar（Aspen MET 单位）
    支持的单位：kPa, MPa, atm, mmHg, psi, Pa
    """
    conversions = {
        'kPa': 0.01,      # 1 kPa = 0.01 bar
        'MPa': 10,        # 1 MPa = 10 bar
        'atm': 1.01325,   # 1 atm = 1.01325 bar
        'mmHg': 0.001333, # 1 mmHg ≈ 0.001333 bar
        'psi': 0.06895,   # 1 psi ≈ 0.06895 bar
        'Pa': 1e-5,       # 1 Pa = 1e-5 bar
        'bar': 1          # 已经是 bar
    }

    if from_unit not in conversions:
        raise ValueError(f"不支持的单位: {from_unit}")

    return value * conversions[from_unit]


def convert_temperature_to_celsius(value, from_unit='K'):
    """
    将温度值从指定单位转换为 °C（Aspen MET 单位）
    支持的单位：K, F
    """
    if from_unit == 'K':
        return value - 273.15
    elif from_unit == 'F':
        return (value - 32) * 5 / 9
    elif from_unit == 'C':
        return value
    else:
        raise ValueError(f"不支持的温度单位: {from_unit}")


def convert_flow_to_kmol_per_h(value, from_unit):
    """
    将流量值转换为 kmol/h（Aspen MET 单位）
    """
    conversions = {
        'mol/s': 3600,     # 1 mol/s × 3600 = 3600 mol/h = 3.6 kmol/h
        'kmol/s': 3600,    # 1 kmol/s × 3600 = 3600 kmol/h
        'lbmol/h': 0.4536, # 1 lbmol/h ≈ 0.4536 kmol/h
        'kmol/h': 1        # 已经是目标单位
    }

    if from_unit not in conversions:
        raise ValueError(f"不支持的流量单位: {from_unit}")

    # 特殊处理 mol/s
    if from_unit == 'mol/s':
        return value * 3600 / 1000  # 转换为 kmol/h

    return value * conversions[from_unit]
```

## 使用示例

### 设置压力（常见问题：实验数据用 kPa）

```python
# 错误示例：直接使用 kPa 值
experimental_pressure_kpa = 150.0  # 实验测得 150 kPa
# node.Value = experimental_pressure_kpa  # 错！Aspen 期望 bar

# 正确示例：先转换
pressure_bar = convert_pressure_to_bar(experimental_pressure_kpa, 'kPa')
node.Value = pressure_bar  # 1.5 bar

# 或者内联计算
node.Value = experimental_pressure_kpa / 100.0  # 150 kPa → 1.5 bar
```

### 读取压力并转换为 kPa

```python
# Aspen 中读取的值是 bar
pressure_bar = aspen.Tree.FindNode(r"\Data\Streams\S1\Output\PRES\MIXED").Value

# 转换为 kPa 用于报告
pressure_kpa = pressure_bar * 100
print(f"系统压力: {pressure_kpa:.1f} kPa")
```

### 批量单位转换

```python
# 假设有一组实验数据需要输入 Aspen
experimental_data = [
    {'temp_k': 473.15, 'pres_kpa': 200, 'flow_kmol_h': 100},
    {'temp_k': 493.15, 'pres_kpa': 250, 'flow_kmol_h': 120},
    {'temp_k': 513.15, 'pres_kpa': 300, 'flow_kmol_h': 150},
]

for data in experimental_data:
    # 转换单位
    temp_c = convert_temperature_to_celsius(data['temp_k'], 'K')
    pres_bar = convert_pressure_to_bar(data['pres_kpa'], 'kPa')

    # 设置到 Aspen
    temp_node.Value = temp_c
    pres_node.Value = pres_bar
    flow_node.Value = data['flow_kmol_h']  # 已经是 kmol/h

    aspen.Run2()
```

## 全局单位集设置

### 在脚本开头统一设置单位集

```python
import win32com.client as win32

aspen = win32.Dispatch('Apwn.Document.40.0')
aspen.InitFromArchive2(r"D:\path\to\file.bkp")

# 【强烈推荐】在所有操作前设置单位集
aspen.Tree.Elements('Data').Elements("Setup").Elements("Global").Elements("Input").Elements("INSET").Value = "MET"

# 运行一次以应用单位集
aspen.SuppressDialogs = 1
aspen.Run2()

# 此后所有读写操作都使用 MET 单位
```

### 验证当前单位集

```python
current_unit_set = aspen.Tree.Elements('Data').Elements("Setup").Elements("Global").Elements("Input").Elements("INSET").Value
print(f"当前单位集: {current_unit_set}")
# 输出：MET, SI, 或 ENG
```

## 警告：单位不一致导致的问题

### 问题 1：模拟结果数量级错误

**症状**：计算出的流量/焓值数量级完全不对

**原因**：输入数据使用了错误的单位，如将 kPa 当作 bar 输入（差 100 倍）

**解决**：
```python
# 在关键输入后打印验证
print(f"输入压力: {pressure_node.Value} bar")  # 确认单位正确
```

### 问题 2：目标函数优化方向错误

**症状**：优化算法往错误方向搜索（如最大化压力而非最小化）

**原因**：目标函数中未考虑单位换算

**解决**：
```python
# 错误：直接比较不同单位
score = product_yield - pressure  # pressure 单位？

# 正确：统一单位或归一化
pressure_bar = pressure_node.Value
score = product_yield * 1000 - pressure_bar * 10  # 权重考虑单位
```

### 问题 3：组分浓度不等于 1

**症状**：Aspen 报错 "Component fractions do not sum to 1"

**原因**：输入的摩尔分数使用了不同单位（如质量分数而非摩尔分数）

**解决**：
```python
# 确保使用 FRAC（摩尔分数）而非 MASSFRAC（质量分数）
# 路径：...Input\FRAC\MIXED\COMPONENT  ✓
# 路径：...Input\MASSFRAC\MIXED\COMPONENT  ✗（如果目标是摩尔分数）
```

## 推荐工作流程

```python
def configure_aspen_units(aspen, target_unit_set="MET"):
    """配置 Aspen 单位集并返回常用单位换算函数"""

    # 设置单位集
    aspen.Tree.Elements('Data').Elements("Setup").Elements("Global").Elements("Input").Elements("INSET").Value = target_unit_set
    aspen.SuppressDialogs = 1
    aspen.Run2()

    # 根据单位集返回对应的换算函数
    if target_unit_set == "MET":
        return {
            'to_pressure': lambda v, u: convert_pressure_to_bar(v, u),
            'to_temperature': lambda v, u: convert_temperature_to_celsius(v, u),
            'to_flow': lambda v, u: v if u == 'kmol/h' else convert_flow_to_kmol_per_h(v, u)
        }
    else:
        raise NotImplementedError(f"单位集 {target_unit_set} 的换算函数尚未实现")

# 使用示例
convert = configure_aspen_units(aspen, "MET")

# 设置实验数据（原始单位：K, kPa, mol/s）
temp = convert['to_temperature'](473.15, 'K')
pres = convert['to_pressure'](200, 'kPa')
flow = convert['to_flow'](50, 'mol/s')
```
