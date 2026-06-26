---
name: python-aspen
description: 化工流程模拟自动化与 Python 集成。当用户需要操作 Aspen Plus、化工流程模拟、反应器优化、塔板设计、物性配置、遗传算法优化化工过程、Python COM 接口控制 Aspen、自动化水力学校核时使用此 skill。即使使用 CodeLibrary 等第三方库，底层 COM 接口知识也很重要。
compatibility: 需要 win32com.client (Windows)，Aspen Plus V10+ (推荐 V14)，可选 PyTorch、matplotlib
---

# Python Aspen 自动化 Skill

## 快速参考

这个 Skill 帮助你通过 Python 的 COM 接口控制 Aspen Plus，实现化工流程模拟的自动化操作、参数优化和数据分析。

## 核心概念

### Aspen 变量树结构

Aspen 的所有数据都存储在一个层级化的**变量树**中，理解这个结构是自动化的关键：

```
\Data                           # 根节点
├── Components\                 # 组分定义
│   └── Specifications\Input\
├── Properties\                 # 物性方法
│   └── Specifications\Input\
├── Streams\                    # 流股
│   └── <StreamName>\           # 流股名称
│       ├── Input\              # 输入参数
│       └── Output\             # 输出结果
├── Blocks\                     # 单元模块
│   └── <BlockName>\            # 模块名称
│       ├── Input\              # 输入参数
│       └── Output\             # 输出结果
└── Setup\                      # 全局设置
    └── Global\Input\
```

### COM 接口工作原理

**为什么 Python 可以控制 Aspen？**

Aspen Plus 通过 Windows 的 COM (Component Object Model) 接口暴露其内部对象。Python 使用 `win32com` 库作为客户端，可以直接读写 Aspen 变量树中的任何节点。

**关键理解：**
- `aspen = win32.Dispatch('Apwn.Document')` 创建的是 Aspen 文档对象的**引用**
- 所有操作（读写参数、运行模拟）都通过这个引用进行
- Aspen 必须保持运行状态，Python 才能控制它

**版本号很重要：** `'Apwn.Document.40.0'` 中的 `40.0` 对应 Aspen Plus V14，不同版本的号码不同。

## 基础操作

### 启动与连接

```python
import win32com.client as win32
import os

# 方法 1: 直接启动（不指定版本，使用默认安装版本）
aspen = win32.Dispatch('Apwn.Document')

# 方法 2: 指定版本启动（推荐）
aspen = win32.Dispatch('Apwn.Document.40.0')  # V14

# 加载 .bkp 文件（必须使用绝对路径）
bkp_path = r"D:\path\to\your\file.bkp"
aspen.InitFromArchive2(os.path.abspath(bkp_path))

# 控制可见性（0 = 后台运行，1 = 显示窗口）
aspen.Visible = 0

# 抑制对话框（防止弹出确认窗口卡死脚本）
aspen.SuppressDialogs = 1
```

### 运行与关闭

```python
# 运行模拟（使用 Run2()，不是已废弃的 Run()）
aspen.Run2()

# 正确关闭（释放后台进程）
aspen.Quit()  # 推荐：完全退出并释放资源
# aspen.Close()  # 不推荐：只关闭文档，可能残留进程
```

### 读取变量数据

```python
# 方法 1: FindNode - 直接路径访问（推荐用于已知路径）
node = aspen.Tree.FindNode(r"\Data\Streams\S1\Input\TOTFLOW\MIXED")
flow_value = node.Value
print(f"总流量: {flow_value} kmol/h")

# 方法 2: Elements - 逐层访问（推荐用于探索）
streams = aspen.Tree.Elements("Data").Elements("Streams")
for stream in streams.Elements:
    name = stream.Name
    # 进一步操作...

# 读取模块输出
block_node = aspen.Tree.FindNode(r"\Data\Blocks\RPLUG\Output\TEMP")
temperature = block_node.Value
```

### 修改变量数据

```python
# 修改流股输入
flow_node = aspen.Tree.FindNode(r"\Data\Streams\FEED\Input\TOTFLOW\MIXED")
flow_node.Value = 100.0  # 设置为 100 kmol/h

# 修改模块参数
temp_node = aspen.Tree.FindNode(r"\Data\Blocks\HEATER\Input\TEMP")
temp_node.Value = 350.0  # 设置加热温度为 350°C

# 修改后必须重新运行模拟才能生效
aspen.Run2()
```

## 常见任务

### 任务 1: 物性配置

**添加组分（重要：不能用 Add！）**

Aspen 的组分列表是**表格结构**，不是简单列表，必须使用"先插入行，再填数据"的逻辑：

```python
# 获取组分表格节点
comp_table = aspen.Tree.FindNode(r"\Data\Components\Specifications\Input\TYPE")
elements = comp_table.Elements

# 添加一个组分（甲醇）
elements.InsertRow(0, 0)  # 在第 0 行位置插入新行
elements.SetLabel(0, 0, False, "CH3OH")  # 设置组分标识符

# 批量添加多个组分
components = ["WATER", "ETHANOL", "CH3OH"]
for comp in components:
    elements.InsertRow(0, 0)
    elements.SetLabel(0, 0, False, comp)

# 注意：组分标识符可以用：
# - 化学式：WATER, CH3OH, C2H6O
# - 名称：METHANOL, ETHANOL（部分支持）
# - CAS 号：7732-18-5（精确但不易记忆）
```

**设置热力学方法**

```python
# 抑制对话框（强烈建议在修改设置前执行）
aspen.SuppressDialogs = 1

# 设置物性方法（如 UNIQUAC, RK-SOAVE, NRTL-RK）
method_node = aspen.Tree.FindNode(r"\Data\Properties\Specifications\Input\GBASEOPSET")
method_node.Value = "UNIQUAC"

# 运行以激活二元交互参数（BIPs）
aspen.Run2()
```

### 任务 2: 流股操作

**创建和删除流股**

```python
# 创建新流股
streams = aspen.Tree.Elements("Data").Elements("Streams")
# 格式：流股名称!类型
streams.Elements.Add("S_NEW!MATERIAL")  # 物料流
streams.Elements.Add("Q_NEW!HEAT")      # 热流
streams.Elements.Add("W_NEW!WORK")      # 功流

# 删除流股
streams.Elements.Remove("S_OLD")
```

**连接流股到模块**

```python
# 获取模块端口
block_ports = aspen.Tree.Elements("Data").Elements("Blocks").Elements("HEATER").Elements("Ports")

# 连接流股到端口
block_ports.Elements("IN").Elements.Add("S_FEED")   # 连接输入流
block_ports.Elements("OUT").Elements.Add("S_PRODUCT")  # 连接输出流

# 断开流股
block_ports.Elements("IN").Elements.Remove("S_OLD")
```

**常见流股数据路径**

```python
# 输入参数（设置）
aspen.Tree.FindNode(r"\Data\Streams\S1\Input\TOTFLOW\MIXED").Value      # 总流量
aspen.Tree.FindNode(r"\Data\Streams\S1\Input\TEMP\MIXED").Value         # 温度
aspen.Tree.FindNode(r"\Data\Streams\S1\Input\PRES\MIXED").Value         # 压力
aspen.Tree.FindNode(r"\Data\Streams\S1\Input\FRAC\MIXED\WATER").Value   # 组分摩尔分数

# 输出结果（读取）
aspen.Tree.FindNode(r"\Data\Streams\S1\Output\MASSFLMX\MIXED").Value    # 质量流量
aspen.Tree.FindNode(r"\Data\Streams\S1\Output\MOLEFLOW\MIXED\WATER").Value  # 组分摩尔流量
```

### 任务 3: 模块操作

**创建和删除模块**

```python
blocks = aspen.Tree.Elements("Data").Elements("Blocks")

# 常见模块类型：
# RPlug - 平推流反应器
# RCSTR - 全混流反应器
# Flash2 - 闪蒸罐
# Heater - 加热器/冷却器
# Radfrac - 精馏塔
# DSTWU - 简捷精馏
# Heater, Mixer, Splitter 等

blocks.Elements.Add("R1!RPlug")      # 创建平推流反应器
blocks.Elements.Remove("OLD_BLOCK")  # 删除模块
```

**修改模块参数**

```python
# 反应器参数
aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_TEMP").Value = 300.0    # 反应温度
aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_PRES").Value = 101.325  # 反应压力
aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\LENGTH").Value = 5.0        # 反应器长度
aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\DIAM").Value = 0.5          # 反应器直径

# 精馏塔参数
aspen.Tree.FindNode(r"\Data\Blocks\T1\Input\NSTAGES").Value = 30        # 理论板数
aspen.Tree.FindNode(r"\Data\Blocks\T1\Input\FEED_STAGE").Value = 15     # 进料板位置
aspen.Tree.FindNode(r"\Data\Blocks\T1\Input\REFLUX_RATIO").Value = 2.5  # 回流比
```

### 任务 4: 单位处理

**为什么单位很重要？**

Aspen 支持多套单位制（SI、英制、公制等），同一个物理量在不同单位下的数值差异巨大。Python 读写时使用的是**当前单位集**下的数值。

**推荐做法：切换单位集**

```python
# 设置为公制单位（MET = Metric）
aspen.Tree.Elements('Data').Elements("Setup").Elements("Global").Elements("Input").Elements("INSET").Value = "MET"

# 运行以应用单位集更改
aspen.Run2()

# 此后所有读写都使用公制单位：
# - 温度：°C
# - 压力：bar (注意：不是 kPa 或 MPa)
# - 流量：kmol/h, kg/h, m3/h
# - 焓：kJ/kmol, kJ/kg
```

**检查变量单位**

```python
# 方法：使用 AttributeValue 获取元数据
node = aspen.Tree.FindNode(r"\Data\Streams\S1\Input\TEMP\MIXED")
unit_info = node.AttributeValue(2)  # HAP_UNITROW = 2，获取物理量类型
print(f"物理量类型代码: {unit_info}")
# 完整的单位对照表需要参考 Aspen 变量浏览器或类型库
```

**单位换算示例**

```python
# Aspen 内部用 bar，但实验数据是 kPa
pressure_kpa = 150.0
pressure_bar = pressure_kpa / 100.0  # 转换为 bar
node.Value = pressure_bar
```

### 任务 5: 数据提取与导出

**导出为不同格式**

```python
# 保存为 .apw（包含输入和输出）
aspen.Save()
aspen.SaveAs(r"D:\new_path\file.apw", True)  # True = 覆盖已存在文件

# 导出为 .bkp（备份文件，仅包含输入）
aspen.Export(1, r"D:\backup\file.bkp")

# 导出为 .rep（文本格式报告）
aspen.Export(2, r"D:\reports\file.rep")

# 导出为 .txt（纯文本）
aspen.Export(5, r"D:\data\file.txt")

# 导出流程图
aspen.Export(11, r"D:\diagrams\flowsheet.dxf")
```

**批量数据提取模式**

```python
# 扫描所有流股并提取关键数据
results = {}
streams_node = aspen.Tree.FindNode(r"\Data\Streams")

for stream in streams_node.Elements:
    name = stream.Name
    # 提取总流量
    flow = aspen.Tree.FindNode(fr"\Data\Streams\{name}\Output\MOLEFLOW\MIXED").Value
    # 提取温度
    temp = aspen.Tree.FindNode(fr"\Data\Streams\{name}\Output\TEMP\MIXED").Value
    results[name] = {"flow": flow, "temp": temp}

print(results)
```

## 高级应用

### 高级 1: 参数优化模式

**基本循环优化结构**

```python
import time

# 目标：找到最佳反应温度使产物收率最大
best_temp = None
best_yield = 0
target_product = "DMS"

for temp in range(200, 401, 10):  # 200-400°C，步长 10°C
    # 1. 修改参数
    temp_node = aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_TEMP")
    temp_node.Value = float(temp)

    # 2. 运行模拟
    aspen.Run2()
    time.sleep(0.5)  # 等待计算完成

    # 3. 提取结果
    product_flow = aspen.Tree.FindNode(r"\Data\Streams\PRODUCT\Output\MOLEFLOW\MIXED\DMS").Value

    # 4. 记录最优
    if product_flow > best_yield:
        best_yield = product_flow
        best_temp = temp

    print(f"温度: {temp}°C, 产物流量: {product_flow:.6f}")

print(f"\n最优温度: {best_temp}°C, 最大收率: {best_yield:.6f}")
```

### 高级 2: 遗传算法优化框架

```python
import random

def evaluate_design(params):
    """评估一组设计参数的目标函数值"""
    temp, length, diam, pres = params

    # 设置参数
    aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_TEMP").Value = temp
    aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\LENGTH").Value = length
    aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\DIAM").Value = diam
    aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\PRES").Value = pres

    # 运行并提取结果
    aspen.Run2()
    product_yield = aspen.Tree.FindNode(r"\Data\Streams\OUT\Output\MOLEFLOW\MIXED\PRODUCT").Value

    return product_yield  # 返回目标函数值

def simple_genetic_algorithm(objective_func, param_bounds, pop_size=20, generations=20):
    """
    简化的遗传算法框架
    param_bounds: [(min, max), (min, max), ...] 每个参数的取值范围
    """
    # 初始化种群
    population = []
    for _ in range(pop_size):
        individual = [random.uniform(b[0], b[1]) for b in param_bounds]
        population.append(individual)

    # 进化循环
    for gen in range(generations):
        # 评估适应度
        fitness = [objective_func(ind) for ind in population]

        # 选择（轮盘赌）
        total_fit = sum(fitness) if sum(fitness) > 0 else 1
        probs = [f/total_fit for f in fitness]
        parents = [random.choices(population, weights=probs)[0] for _ in range(pop_size)]

        # 交叉（单点交叉）
        offspring = []
        for i in range(0, pop_size, 2):
            p1, p2 = parents[i], parents[min(i+1, pop_size-1)]
            if random.random() < 0.8:  # 交叉概率 80%
                cross_point = random.randint(1, len(p1)-1)
                child1 = p1[:cross_point] + p2[cross_point:]
                child2 = p2[:cross_point] + p1[cross_point:]
                offspring.extend([child1, child2])
            else:
                offspring.extend([p1, p2])

        # 变异
        for i in range(len(offspring)):
            if random.random() < 0.1:  # 变异概率 10%
                param_idx = random.randint(0, len(offspring[i])-1)
                min_val, max_val = param_bounds[param_idx]
                offspring[i][param_idx] = random.uniform(min_val, max_val)

        population = offspring[:pop_size]
        best_fitness = max(fitness)
        print(f"Generation {gen+1}: Best fitness = {best_fitness:.6f}")

    # 返回最优个体
    final_fitness = [objective_func(ind) for ind in population]
    best_idx = final_fitness.index(max(final_fitness))
    return population[best_idx], max(final_fitness)

# 使用示例：
best_params, best_value = simple_genetic_algorithm(
    evaluate_design,
    param_bounds=[(200, 400), (1, 3), (0.5, 2), (100, 300)],  # 温度、长度、直径、压力范围
    pop_size=20,
    generations=20
)
print(f"最优参数: {best_params}, 最优值: {best_value:.6f}")
```

### 高级 3: AttributeValue 元数据系统

**什么是 AttributeValue？**

除了 `Value` 属性获取的数值外，Aspen 变量还有丰富的"元数据"：单位、物理量类型、上下限、默认值等。这些元数据通过 `AttributeValue(attribute_id)` 访问。

**常用属性 ID**

```python
# 核心属性（通过解析 Aspen 类型库获得）
HAP_VALUE = 0          # 数值（等同于 .Value）
HAP_UNITROW = 2        # 物理量类型（如 Temperature、Pressure）
HAP_OPTIONLIST = 5     # 选项列表（如算法类型选项）
HAP_ENTERABLE = 7      # 是否可编辑
HAP_UPPERLIMIT = 8     # 上限
HAP_LOWERLIMIT = 9     # 下限
HAP_PROMPT = 19        # 提示文本
HAP_INOUT = 14         # 输入/输出状态

# 获取元数据示例
node = aspen.Tree.FindNode(r"\Data\Blocks\B1\Input\ALGORITHM")

# 获取选项列表
options = node.AttributeValue(5).Elements
for opt in options:
    print(f"可选算法: {opt}")

# 获取提示文本
prompt = node.AttributeValue(19)
print(f"提示信息: {prompt}")
```

**修改底层属性**

```python
# SetAttributeValue(attr_number, force, new_value)
# attr_number: 属性 ID
# force: True=强制覆盖，False=正常修改
# new_value: 新值

node = aspen.Tree.FindNode(r"\Data\Blocks\B1\Input\B:F_BASIS")
node.SetAttributeValue(0, False, "MASS")  # 修改计算基准为质量基准
```

## 最佳实践

### 调试技巧：使用 dir() 探索对象

由于 Aspen 的 COM 接口是动态绑定，IDE 无法自动补全。使用 Python 内省功能探索可用方法：

```python
# 查看对象的所有方法和属性
methods = dir(aspen.Tree)
print([m for m in methods if not m.startswith('_')])  # 过滤掉魔法方法

# 查看方法的详细帮助
help(aspen.Tree.FindNode)
help(node.Elements)
```

### 错误处理模式

```python
def safe_run_aspen(aspen_obj, max_retries=3):
    """带重试的 Aspen 运行函数"""
    for attempt in range(max_retries):
        try:
            aspen_obj.Run2()
            return True
        except Exception as e:
            print(f"运行失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print("已达最大重试次数，放弃")
                return False
            time.sleep(2)
    return False

def safe_get_value(node_path, default=None):
    """安全获取节点值，节点不存在时返回默认值"""
    try:
        node = aspen.Tree.FindNode(node_path)
        return node.Value
    except Exception as e:
        print(f"无法读取 {node_path}: {e}")
        return default
```

### 迭代器技巧

Aspen 的 Elements 是可迭代对象，但直接迭代可能导致问题（迭代过程中不能修改集合）：

```python
# 错误：直接迭代时修改
for stream in streams.Elements:
    if stream.Name == "OLD":
        streams.Elements.Remove(stream.Name)  # 可能导致迭代器失效

# 正确：先转换为列表
elements_list = list(streams.Elements)
for stream in elements_list:
    if stream.Name == "OLD":
        streams.Elements.Remove(stream.Name)

# 或者用 while 循环
i = 0
while i < streams.Elements.Count:
    stream = streams.Elements.Item(i)
    if stream.Name == "OLD":
        streams.Elements.Remove(stream.Name)
    else:
        i += 1
```

### 性能优化

```python
# 批量操作时减少重复的 FindNode 调用
# 低效：
for i in range(100):
    temp_node = aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_TEMP")
    temp_node.Value = i

# 高效：
temp_node = aspen.Tree.FindNode(r"\Data\Blocks\R1\Input\REAC_TEMP")
for i in range(100):
    temp_node.Value = i
    aspen.Run2()
```

## 故障排查

### 常见问题

**1. 找不到节点错误**
```
解决方案：
- 检查路径语法（使用 r"" 原始字符串避免转义问题）
- 在 Aspen 变量浏览器中确认节点存在
- 尝试用 Elements 逐层访问，找出哪一层出错
```

**2. 模拟不收敛**
```
解决方案：
- 检查输入参数是否合理（如负数流量）
- 增加迭代次数或调整收敛容差
- 使用 aspen.Reinit() 重置初值
- 分步运行：先运行部分模块，再整体运行
```

**3. 后台残留进程**
```
解决方案：
- 使用 aspen.Quit() 而不是 Close()
- 脚本异常时确保执行清理（使用 try-finally）
- 手动结束进程：taskkill /F /IM AspenPlus.exe
```

**4. 单位不匹配**
```
解决方案：
- 始终在脚本开头设置单位集
- 记录数据的单位并在注释中标明
- 关键参数进行单位换算验证
```

**5. 类型库过期方法**
```
已废弃方法（不要使用）：
- aspen.Run() → 改用 Run2()
- aspen.Close() → 改用 Quit()
- 使用 .Add() 添加组分 → 改用 InsertRow + SetLabel

如何识别：
- 官方文档基于 VB，Python 层面可能不同
- 使用 dir() 和 help() 查看实际可用方法
```

## 第三方库

### CodeLibrary (AspenPlus-Python-Interface)

如果你使用 [CodeLibrary](https://github.com/YouMayCallMeJesus/AspenPlus-Python-Interface) 库，了解底层 COM 接口仍然重要：

```python
from CodeLibrary import Simulation

# CodeLibrary 封装了 COM 接口
sim = Simulation(
    AspenFileName="file.bkp",
    WorkingDirectoryPath=r"D:\path",
    VISIBILITY=False
)

# 底层仍然是 COM 操作
sim.AspenSimulation.Tree.FindNode(...).Value = ...
sim.EngineRun()

# 封装的优势：简化初始化，但高级操作仍需直接访问 COM 接口
```

**何时使用底层 COM？**
- CodeLibrary 未封装的功能
- 需要更精细的控制
- 调试 COM 层面的问题
- 性能关键路径

## 参考资源

- **QQ 交流群**: 56721026 - Python 与 Aspen 联动
- **CEPD 化工社区**: https://bbs.imbhj.com/
- **CodeLibrary**: https://github.com/YouMayCallMeJesus/AspenPlus-Python-Interface
- **详细文档**: https://wenxiaoshuo.github.io/AspenWithPython/
