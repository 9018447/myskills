# Python Aspen 快速参考卡

## 30 秒快速上手

```python
import win32com.client as win32

# 1. 连接 Aspen
aspen = win32.Dispatch('Apwn.Document.40.0')  # V14
aspen.InitFromArchive2(r"D:\path\file.bkp")
aspen.Visible = 0
aspen.SuppressDialogs = 1

# 2. 设置单位集
aspen.Tree.Elements('Data').Elements("Setup").Elements("Global").Elements("Input").Elements("INSET").Value = "MET"
aspen.Run2()

# 3. 读写数据
aspen.Tree.FindNode(r"\Data\Streams\S1\Input\TEMP\MIXED").Value = 250.0
aspen.Run2()
temp = aspen.Tree.FindNode(r"\Data\Streams\S1\Output\TEMP\MIXED").Value

# 4. 关闭
aspen.Quit()
```

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 找不到节点 | 路径错误 | 使用 `r""` 原始字符串，在 Aspen 变量浏览器中确认 |
| 模拟不收敛 | 初值不当 | 使用 `aspen.Reinit()` 重置，分步运行 |
| 后台残留进程 | 未正确关闭 | 使用 `Quit()` 而非 `Close()` |
| 单位不匹配 | 未设置单位集 | 脚本开头设置 `INSET = "MET"` |
| 组分添加失败 | 使用了 Add() | 改用 `InsertRow()` + `SetLabel()` |

## 已废弃方法（不要使用）

```python
# ❌ 已废弃
aspen.Run()          # → 改用 Run2()
aspen.Close()        # → 改用 Quit()
components.Add()     # → 改用 InsertRow() + SetLabel()

# ✅ 正确方法
aspen.Run2()
aspen.Quit()
elements.InsertRow(0, 0)
elements.SetLabel(0, 0, False, "WATER")
```

## 单位换算速查

| 从 | 到 | 乘以 |
|----|----|----|
| kPa | bar | 0.01 |
| MPa | bar | 10 |
| K | °C | 减 273.15 |
| °F | °C | (°F - 32) × 5/9 |
| mol/s | kmol/h | 3.6 |

## 最常用路径

```python
# 流股输入
\Data\Streams\<name>\Input\TEMP\MIXED      # 温度
\Data\Streams\<name>\Input\PRES\MIXED      # 压力
\Data\Streams\<name>\Input\TOTFLOW\MIXED   # 总流量
\Data\Streams\<name>\Input\FRAC\MIXED\<comp>  # 组分分数

# 流股输出
\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<comp>  # 组分流量
\Data\Streams\<name>\Output\TEMP\MIXED      # 温度

# 模块参数
\Data\Blocks\<name>\Input\REAC_TEMP        # 反应温度
\Data\Blocks\<name>\Input\LENGTH           # 长度
\Data\Blocks\<name>\Input\DIAM             # 直径
```

## 调试技巧

```python
# 1. 探索对象可用方法
print(dir(aspen.Tree))

# 2. 查看详细帮助
help(aspen.Tree.FindNode)

# 3. 逐层排查
try:
    node = aspen.Tree.FindNode(r"\Data\Streams\S1\Output\TEMP\MIXED")
    print(f"值: {node.Value}")
except Exception as e:
    print(f"错误: {e}")
```

## 完整模板：参数优化

```python
import win32com.client as win32
import time

def optimize_temperature(aspen_path, temp_range=(200, 401, 10)):
    """扫描温度范围，找出最优反应温度"""

    # 初始化
    aspen = win32.Dispatch('Apwn.Document.40.0')
    aspen.InitFromArchive2(aspen_path)
    aspen.Visible = 0
    aspen.SuppressDialogs = 1

    # 单位集
    aspen.Tree.Elements('Data').Elements("Setup").Elements("Global").Elements("Input").Elements("INSET").Value = "MET"
    aspen.Run2()

    # 预先获取节点（性能优化）
    temp_node = aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_TEMP")
    prod_node = aspen.Tree.FindNode(r"\Data\Streams\PRODUCT\Output\MOLEFLOW\MIXED\DMS")

    # 扫描
    results = []
    for temp in range(*temp_range):
        temp_node.Value = float(temp)
        aspen.Run2()
        time.sleep(0.5)

        yield_val = prod_node.Value
        results.append((temp, yield_val))
        print(f"温度: {temp}°C, 收率: {yield_val:.6f}")

    # 找最优
    best_temp, best_yield = max(results, key=lambda x: x[1])
    print(f"\n最优温度: {best_temp}°C, 最大收率: {best_yield:.6f}")

    aspen.Quit()
    return best_temp, best_yield

# 使用
# optimize_temperature(r"D:\reactor.bkp")
```

## 添加组分模板

```python
def add_components(aspen, component_list):
    """批量添加组分"""

    # 获取组分表格
    comp_table = aspen.Tree.FindNode(r"\Data\Components\Specifications\Input\TYPE")
    elements = comp_table.Elements

    # 添加
    for comp in component_list:
        elements.InsertRow(0, 0)
        elements.SetLabel(0, 0, False, comp)

    # 运行激活 BIPs
    aspen.SuppressDialogs = 1
    aspen.Run2()

# 使用
# add_components(aspen, ["WATER", "METHANOL", "ETHANOL"])
```

## 何时使用底层 COM

即使使用 CodeLibrary，了解底层 COM 仍然重要：

```python
from CodeLibrary import Simulation

sim = Simulation(AspenFileName="file.bkp", ...)

# CodeLibrary 未封装的功能？直接用 COM
sim.AspenSimulation.Tree.FindNode(r"\Data\...").Value = ...
```

**优势**：
- 更精细的控制
- 调试 COM 层问题
- CodeLibrary 未封装时备用方案

## 获取帮助

- **QQ 群**: 56721026
- **CEPD 社区**: https://bbs.imbhj.com/
- **详细文档**: https://wenxiaoshuo.github.io/AspenWithPython/
- **CodeLibrary**: https://github.com/YouMayCallMeJesus/AspenPlus-Python-Interface
