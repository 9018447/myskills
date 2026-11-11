# 聚合物、表面与内置 recipe

## 选择内置组件还是自定义组件

优先复用当前包中已有且化学模型匹配的组件：

```python
from mbuild.lib.recipes import Alkane, Monolayer, Polymer, TiledCompound
from mbuild.lib.moieties import CH2, CH3, Silane
from mbuild.lib.molecules import Ethane, Methane, WaterTIP3P
from mbuild.lib.surfaces import Betacristobalite
```

使用前检查对应源码和输入资源。部分内置组件从 PDB 读取，当前环境没有 MDTraj 时会在实例化阶段失败；这属于依赖问题，不是组件拓扑问题。第三方 recipe 可通过 `mb.recipes` 插件入口发现，用 `dir(mb.recipes)` 查看当前实际可用项。

## Polymer：从单体到链

已有两个正确 Port 的单体可直接传给 `Polymer(monomers=[...])`。从完整分子开始时，用 `add_monomer()` 指定位点：

- `indices` 按 `compound.particles()` 的叶粒子顺序索引，支持负索引。
- `replace=True`：indices 指向被移除的占位原子，通常是氢；Port 添加到其原键合邻居。
- `replace=False`：indices 指向实际锚点，不删除粒子；通常还需明确 `orientation`。
- `separation` 是最终单体间键长，不是每个 Port 的长度。
- `build(n, sequence)` 中 n 是整个 sequence 的重复次数，不是单体总数。

```python
import mbuild as mb
from mbuild.lib.recipes import Polymer

monomer = mb.load("CC", smiles=True, seed=42)
chain = Polymer()
chain.add_monomer(
    compound=monomer,
    indices=[2, -2],
    separation=0.15,
    replace=True,
)
chain.build(n=3, sequence="A", add_hydrogens=True)

assert chain.n_particles == 20
assert chain.n_bonds == 19
assert len(chain.available_ports()) == 0
```

此例生成 3 个 `-CH2-CH2-` 单元并在两端补氢，即己烷。`indices=[2, -2]` 依赖当前 RDKit 粒子顺序；换输入或后端后重新确认位点。

共聚物按单体添加顺序映射字符：

```python
chain = Polymer()
chain.add_monomer(monomer_a, indices=[2, -2], separation=0.15)
chain.add_monomer(monomer_b, indices=[3, -1], separation=0.15)
chain.build(n=4, sequence="ABBA", add_hydrogens=False)
```

这里生成 `4 * len("ABBA")` 个单体。未提供端基时：

- `add_hydrogens=True` 用氢封端。
- `add_hydrogens=False` 暴露 `head_port`、`tail_port`，并在链层级保留可用 Port。

自定义端基使用 `add_end_groups()`，其 `index`、`replace`、`separation` 与单体规则相同。`label="head"` 或 `"tail"` 选择位置；相同端基可用 `duplicate=True`，不同端基分别调用并传 `duplicate=False`。

## Alkane：常见链的捷径

```python
from mbuild.lib.recipes import Alkane

hexane = Alkane(n=6, cap_front=True, cap_end=True)
open_chain = Alkane(n=6, cap_front=False, cap_end=False)
```

`n` 是碳原子数，不是 `Polymer.build(n=...)` 的序列重复次数。未封端的一端会暴露 `up` 或 `down` Port。需要其他官能团连接时保留对应端点，不再额外补氢。

## Pattern：把组件放到点集或宿主位点

`Pattern` 是三维点集。常用构造器包括 `Grid2DPattern`、`Grid3DPattern`、`Random2DPattern`、`Random3DPattern`、`DiskPattern`、`SpherePattern` 和 `Triangle2DPattern`。

只平移副本：

```python
copies = mb.Grid2DPattern(n=2, m=3).apply(mb.clone(molecule))
system = mb.Compound(copies)
```

连接到有 Port 的宿主：

```python
pattern = mb.Grid2DPattern(n=2, m=2)
guests, backfills = pattern.apply_to_compound(
    host=host,
    guest=guest,
    guest_port_name="down",
    backfill=backfill,
    backfill_port_name="up",
)
system = mb.Compound([host, guests, backfills])
```

- 默认 guest 端口为 `down`，backfill 端口为 `up`；按实际组件覆盖。
- pattern 点数不能超过宿主可用 Port 数。
- 默认 `scale=True` 会把归一化点集缩放到宿主 bounding box，并平移到宿主 mins；已有绝对坐标时传 `scale=False`。
- 每个点选择最近的宿主 Port；未占用 Port 可由 backfill 封端。
- 返回值是已连接组件列表，仍需加入最终根 Compound。

## Monolayer 与 TiledCompound

`Monolayer` 组合表面平铺、pattern、链和 backfill：

```python
import mbuild as mb
from mbuild.lib.atoms import H
from mbuild.lib.recipes import Alkane, Monolayer
from mbuild.lib.surfaces import Betacristobalite

chain = Alkane(n=10, cap_end=False)
surface = Betacristobalite()
monolayer = Monolayer(
    surface=surface,
    chains=chain,
    backfill=H(),
    pattern=mb.Grid2DPattern(n=4, m=4),
    tile_x=2,
    tile_y=1,
)
```

多种链同时提供 `chains=[chain_a, chain_b]` 和等长 `fractions=[fraction_a, fraction_b]`。最后一种链占据剩余 pattern 点；检查实际数量，因为中间链使用 `round(fraction * n_points)`。随机 pattern 和多链分配使用 NumPy 随机数，复现时在这些构造步骤前设置 `np.random.seed(42)`。

直接复制周期组件：

```python
from mbuild.lib.recipes import TiledCompound

tiled = TiledCompound(tile=surface, n_tiles=(2, 2, 1))
```

`TiledCompound` 要求每个复制方向的原始 tile 具有相应 periodicity，并设置正确 box；它还会缝合跨周期边界的键。对只有坐标、没有准确盒子和周期信息的任意分子，不应把它当作通用复制器。

完成标准：单体总数和序列、端基、可用 Port、每类链数量、表面剩余位点及周期键均与构建契约一致。
