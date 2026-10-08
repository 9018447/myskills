# Stream 与 Unit 参考

## 1. Stream 流对象

Stream 定义物料流量及热力学状态。

### 创建 Stream

```python
# 方法一：指定组分流量（默认 kmol/hr）
feed = bst.Stream(Water=50, Methanol=20)

# 方法二：指定单位
feed = bst.Stream(Water=1.08e+03, Ethanol=586, units='kg/hr')

# 方法三：设置总流量和单位
corn_feed = Stream(
    Starch=62, Fiber=19, Water=15, Oil=4,
    total_flow=100000,
    units='bu/day',  # 蒲式耳/天
)

# 方法四：空流（后续通过 imol/imass 填充）
s = bst.Stream()
s.imol['Water'] = 100
s.imass['Ethanol'] = 500  # kg/hr
```

### 显示与查看

```python
feed.show()                  # 默认显示
feed.show(flow='kg/hr')      # 按质量流量显示
feed.show(T='degC')          # 温度用摄氏度
feed.show(P='atm')           # 压力用大气压
feed.show(composition=True)  # 显示组成百分比
feed.show('cwt')             # 组合：composition + 质量流量 + 温度°C
feed.show(df=True)           # 以 DataFrame 表格显示
```

### 流属性

```python
feed.F_mass              # 总质量流量 [kg/hr]
feed.F_vol               # 总体积流量 [m³/hr]
feed.imol['Water']       # 水的摩尔流量 [kmol/hr]
feed.imass['Ethanol']    # 乙醇的质量流量 [kg/hr]
feed.T                   # 温度 [K]
feed.P                   # 压力 [Pa]
feed.H                   # 焓 [kJ/hr]
feed.cost                # 成本 [USD/hr]
feed.price = 0.15        # 设置价格 [USD/kg]

# 相平衡计算
feed.vle(V=0, P=101325)  # 在泡点（V=0）计算气液平衡
s.dew_point_at_P()       # 露点
s.bubble_point_at_P()    # 泡点
```

## 2. Unit 单元操作

### 创建单元

```python
unit = Unit(ID='unit', ins=ins, outs=outs)

# 为单元提供进口流和出口流
ins = Stream('feed')
outs = [Stream('product')]
unit = Unit(ID='my_unit', ins=ins, outs=outs)
unit.show(data=False)
```

### 变量名自动推断 ID

```python
feed = Stream()      # 自动推断 ID 为 'feed'
product = Stream()   # 自动推断 ID 为 'product'
unit = Unit(ins=feed, outs=product)
```

### 参数默认值规则

| 参数 | 行为 |
|---|---|
| `ins=None, outs=None` | 初始化为缺失流 (missing stream) |
| `ins=(), outs=()` | 初始化为空流 (empty stream) |
| `ins='', outs=['']` | 空字符串默认使用未使用的 ID |

### 区域命名约定

默认 ID 遵循 `{字母}{区域+数字}` 格式：

| 字母 | 单元操作 |
|------|----------|
| C | Centrifuge（离心机） |
| D | Distillation column（蒸馏塔） |
| E | Evaporator（蒸发器） |
| F | Flash tank（闪蒸罐） |
| H | Heat exchange（换热） |
| M | Mixer（混合器） |
| P | Pump（泵，包括输送带） |
| R | Reactor（反应器） |
| S | Splitter（分流器，包括固/液分离器） |
| T | Tank or bin（储罐或储料仓） |
| U | Other units（其他单元） |
| J | Junction（非物理单元，用于调整流） |
| PS | Process specification（非物理单元） |

```python
Mixer().show(data=False)           # M1, M2, ...
Mixer(100).show(data=False)        # M101（从101开始编号）
Splitter(split=0.5).show()         # S1, S2, ...
```

### 常用内置单元操作

```python
# 混合器
M1 = Mixer(ins=(recycle, feed), outs='mixed_stream')

# 分流器
S1 = Splitter(ins=feed, outs=('stream1', 'stream2'), split=0.5)

# 闪蒸罐
F1 = Flash(ins=feed, outs=('vapor', 'liquid'), V=0.1, P=101325)

# 泵
P1 = Pump(ins=feed, P=5*101325)

# 换热器
H1 = HXutility(ins=feed, T=350)  # 加热/冷却到指定温度

# 储罐
T1 = StorageTank(ins=corn_feed)

# 精馏塔
D1 = BinaryDistillation(ins=feed, outs=('distillate', 'bottoms'),
                        LHK=('Ethanol', 'Water'), y_top=0.79,
                        x_bot=0.001, k=1.25, is_divided=True)

# 简捷蒸馏（FUG法）
FUG = ShortcutColumn(ins=[feed], outs=['distillate', 'bottoms'],
                     LHK=['Cyclohexane', 'n-Heptane'],
                     P=feed.P, Lr=0.98, Hr=0.98, k=1.25)

# 严格蒸馏（MESH法）
MESH = MESHDistillation(ins=[feed], outs=['distillate', 'bottoms'],
                        N_stages=42, feed_stages=[18],
                        LHK=('Ethanol', 'Water'),
                        stage_specifications={0: ('Reflux', 1.0), -1: ('Flow', 0.78624)})

# 换热器（过程/过程）
HX = HXprocess(ins=(inlet, flash_gas), outs=('throttle_in', 'out'), dT=9.55)

# 等焓阀
valve = IsenthalpicValve(ins=throttle_in, outs='valve_out', P=1e5, vle=True)
```

### 单元操作通用属性

```python
unit.simulate()            # 模拟单元
unit.show(data=False)      # 显示不含数据
unit.results()             # 返回结果 DataFrame
unit.results(basis='SI')   # 以 SI 单位制返回
unit.diagram()             # 显示单元示意图

# 访问进出口流
unit.ins[0]   # 第一个进口流
unit.outs[0]  # 第一个出口流
unit.feed     # 第一个进口流（别名）
unit.vapor    # 第一个气相出口（仅部分单元）
unit.liquid   # 第一个液相出口（仅部分单元）

# 成本与能耗
unit.net_duty    # 总热负荷 [kJ/hr]
unit.net_power   # 电耗 [kW]
```

## 3. 管线标记法

`-pipe-` 记法简化单元间连接：`M1-0` 等价于 `M1.outs[0]`。

```python
# 传统写法
M1 = Mixer(ins=(recycle, feed))
F1 = Flash(ins=M1.outs[0], outs=('vapor_product', 'liquid'), V=0.1, P=101325)

# 管线标记法
M1 = Mixer(ins=(recycle, feed))
F1 = Flash(ins=M1-0, outs=('vapor_product', 'liquid'), V=0.1, P=101325)

# S1 的进口是 F1 的第二个出口（液相）
S1 = Splitter(ins=F1-1, outs=(recycle, 'liquid_product'), split=0.5)
```

### 示例：构建含循环的流程

```python
import biosteam as bst
from biosteam.units import Mixer, Splitter

bst.settings.set_thermo(['Water'])

feed1 = bst.Stream()
M1 = Mixer(outs='s1')
S1 = Splitter(outs=('s2', 'product1'), split=0.5)
feed2 = bst.Stream()
M2 = Mixer(outs='s3')
S2 = Splitter(outs=('recycle', 'product2'), split=0.5)

# 用管线标记法连接（形成循环回路 S2 -> M1）
S2-0 - M1-1   # 将 S2 的第一个出口连接到 M1 的第二个进口
```

## 4. 流程图管理

```python
# 查看流程图
bst.main_flowsheet.diagram()

# 清除当前流程图
bst.main_flowsheet.clear()

# 设置新的流程图
bst.main_flowsheet.set_flowsheet('my_flowsheet')

# 创建系统
sys = bst.main_flowsheet.create_system()

# 通过流程图对象管理
from biosteam import main_flowsheet as F
F.register(unit)  # 注册单元到当前流程图
```

注意：切换流程图后，原流程图中的对象不可访问。导入外部生物精炼厂时会自动定义其专属流程图。
