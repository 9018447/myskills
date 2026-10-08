# 蒸馏建模与设计

## 1. 二元蒸馏（McCabe-Thiele）

BioSTEAM 将 McCabe-Thiele 法扩展到 3+ 种组分：比轻关键组分更易挥发的组分进入馏出物，比重关键组分更重的组分进入塔底产物。

```python
bst.settings.set_thermo(['Water', 'Ethanol', 'Glycerol', 'Yeast'], db='BioSTEAM')

feed = bst.Stream(
    Water=1.08e+03, Ethanol=586, Glycerol=10, Yeast=50,
    units='kg/hr',
)
feed.vle(V=0, P=101325)  # 在泡点进料

McCabeThiele = bst.BinaryDistillation(
    ins=feed,
    outs=('distillate', 'bottoms_product'),
    LHK=('Ethanol', 'Water'),   # 轻、重关键组分
    y_top=0.79,                 # 馏出物中轻关键组分组成
    x_bot=0.001,                # 塔底产物中轻关键组分组成
    k=1.25,                     # 实际回流比/最小回流比
    is_divided=True,            # 精馏段与提馏段是否分隔
)
McCabeThiele.simulate()
McCabeThiele.plot_stages()     # 绘制塔板图
```

## 2. 多组分简捷蒸馏（FUG）

```python
FUG = bst.ShortcutColumn(
    ins=[feed],
    outs=['distillate', 'bottoms_product'],
    LHK=['Cyclohexane', 'n-Heptane'],
    P=feed.P,
    Lr=0.98,   # 轻关键组分回收率
    Hr=0.98,   # 重关键组分回收率
    k=1.25,    # 回流比/最小回流比
)
FUG.simulate()
FUG.show('cmol100')
```

## 3. 严格蒸馏（MESH 法）

将简捷模型转换为严格模型：

```python
# 从简捷模型转换
MESH = McCabeThiele.to_rigorous_column()

# 或直接创建 MESH
MESH = bst.MESHDistillation(
    ins=[feed], outs=['distillate', 'bottoms_product'],
    N_stages=42, feed_stages=[18],
    LHK=('Cyclohexane', 'n-Heptane'),
    stage_specifications={0: ('Reflux', 1.629), -1: ('Flow', 0.13563)},
    P=[366463.0 + i*690.0 for i in range(42)]  # 每级压降
)
MESH.simulate()
```

## 4. 蒸馏求解器对比

| 方法 | 适用场景 |
|---|---|
| **Bubble-Point** | 常规蒸馏效果好，但可能失败于吸收/汽提 |
| **Sum-Rates** | 吸附/汽提效果好，常规蒸馏效果较差 |
| **Inside-Out** | 最鲁棒的方法之一，适用于常规蒸馏和吸收/汽提 |
| **Simultaneous-Correction** | 信任域优化，初始猜测接近解时收敛良好 |

BioSTEAM 默认先尝试 inside-out 方法，若失败则尝试其他算法。
