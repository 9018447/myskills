# 综合实例：从零构建甘蔗乙醇流程

## 1. 定义物性包

```python
import biosteam as bst
from biosteam import settings, units, Stream
from biosteam.units import Mixer, Splitter, Flash, Pump, HXutility

Water = bst.Chemical('Water')
Ethanol = bst.Chemical('Ethanol')
Glucose = bst.Chemical('Glucose', phase='s')
Yeast = bst.Chemical('DryYeast', phase='s', search_db=False, MW=1.)
CO2 = bst.Chemical('CO2', phase='g')

chemicals = bst.Chemicals([Water, Ethanol, Glucose, Yeast, CO2])
settings.set_thermo(chemicals)
settings.CEPCI = 603.1
```

## 2. 创建流程

```python
# 进料
feed = Stream(Water=1000, Glucose=200, T=298.15, P=101325)

# 发酵罐（用闪蒸罐模拟）
fermenter = Flash(ins=feed, outs=('offgas', 'broth'), V=0.1, P=101325, T=308)

# 蒸馏
distillation = bst.BinaryDistillation(
    ins=fermenter-1,  # fermenter 液相出口
    outs=('ethanol_product', 'stillage'),
    LHK=('Ethanol', 'Water'),
    y_top=0.80,
    x_bot=0.001,
    k=1.25,
    is_divided=True,
)

# 创建并模拟系统
sys = bst.main_flowsheet.create_system()
sys.simulate()

# 查看结果
sys.show()
sys.results()
```

## 3. 添加工艺规格

```python
# 调整进料确保乙醇产率稳定
@fermenter.add_specification(run=True)
def adjust_feed():
    glucose_needed = distillation.outs[0].imol['Ethanol'] * 1.8  # 化学计量比
    feed.imol['Glucose'] = glucose_needed
    feed.imol['Water'] = glucose_needed * 10  # 稀释

sys2 = bst.main_flowsheet.create_system()
sys2.simulate()
```
