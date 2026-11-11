# Compound、粒子与 Port

## 心智模型

`Compound` 是有序层级树：内部节点是组件，叶节点是粒子。`Particle` 只是 `Compound` 的语义别名，不是另一种数据类型。

- `children` 表示包含关系；`labels` 是名称到对象的引用，二者不等价。
- `compound.particles()` 递归产生叶粒子；`compound[0]` 也按叶粒子索引，不是第一个 child。
- `compound["name"]` 读取 label；重复添加时使用 `label="monomer[$]"`，再通过 `compound["monomer"][i]` 访问。
- `root`、`parent`、`successors()` 用于遍历；`print_hierarchy()` 用于检查组件结构。
- `n_bonds` 用于含子节点的 Compound；单粒子使用 `n_direct_bonds`。

添加同一个实例不会复制它。需要独立分子时使用 `mb.clone(prototype)`，它会复制层级、坐标、键和 Port。

## 导入与逐粒子构建

SMILES 默认由 RDKit 生成显式氢、三维坐标和键，并做初始 UFF 几何优化：

```python
import mbuild as mb

molecule = mb.load("CCO", smiles=True, seed=42)
molecule.name = "ETO"

assert molecule.n_particles == 9
assert molecule.n_bonds == 8
```

文件导入：

```python
from pathlib import Path
import mbuild as mb

structure_path = Path(__file__).resolve().parent / "molecule.mol2"
molecule = mb.load(str(structure_path))
```

- 可复用组件的资源路径相对组件文件解析，不相对进程当前目录猜测。
- PDB 默认需要 MDTraj；可改用 `mb.load(path, backend="parmed")`。ParmEd 可能按距离和标准残基模板推断键，导入后必须检查。
- XYZ 不携带键；`mb.load("molecule.xyz")` 得到的 `n_bonds` 通常为零。键必须由可靠来源提供或显式构建，不能把近距离当作已验证的化学键。
- 更新已有拓扑的坐标时使用 `compound.update_coordinates(path)`；不要重新导入后丢失组件和 Port。

手动构建粗粒化或简单粒子系统：

```python
import mbuild as mb

a = mb.Particle(name="A", pos=[0.0, 0.0, 0.0], mass=12.0)
b = mb.Particle(name="B", pos=[0.15, 0.0, 0.0], mass=14.0)
dimer = mb.Compound([a, b], name="Dimer")
dimer.add_bond((a, b), bond_order=1.0)

assert dimer.n_particles == 2
assert dimer.n_bonds == 1
```

需要元素推断质量时传 `element="C"` 等符号；显式 `mass` 会覆盖元素质量。含子节点的 Compound 的质量和电荷由叶粒子汇总。

## 标签与层级

```python
system = mb.Compound(name="System")
system.add(mb.clone(molecule), label="solvent[$]")
system.add(mb.clone(molecule), label="solvent[$]")

assert len(system["solvent"]) == 2
assert system["solvent"][0] is not system["solvent"][1]
```

将深层对象暴露到上层接口时，只添加引用，不改变包含关系：

```python
parent.add(child["down"], label="down", containment=False)
```

这称为 hoist。它让外部代码使用 `parent["down"]`，同时保留原组件的内部层级。

## 用 Port 形成可复用连接

Port 的 `anchor` 是实际成键粒子，`orientation` 指离锚点的方向，`separation` 是锚点到 Port 中心的距离。两个组件各提供目标键长的一半；`mb.force_overlap()` 对齐两个 Port，默认在锚点之间成键，并移除已使用的 Port。

下面从甲烷 SMILES 去掉一个氢，构造带一个连接位点的甲基，再形成乙烷。该例不依赖 MDTraj：

```python
import mbuild as mb


def make_methyl():
    compound = mb.load("C", smiles=True, seed=42)
    carbon = compound[0]
    leaving_h = compound[1]
    orientation = leaving_h.pos - carbon.pos
    compound.remove(leaving_h)
    compound.add(
        mb.Port(
            anchor=carbon,
            orientation=orientation,
            separation=0.075,
        ),
        label="up",
    )
    return compound


ethane = mb.Compound(name="Ethane")
ethane.add(make_methyl(), label="methyl_1")
ethane.add(make_methyl(), label="methyl_2")

mb.force_overlap(
    move_this=ethane["methyl_1"],
    from_positions=ethane["methyl_1"]["up"],
    to_positions=ethane["methyl_2"]["up"],
)

assert ethane.n_particles == 8
assert ethane.n_bonds == 7
assert len(ethane.available_ports()) == 0
```

位点选择规则：

- 先用 `list(enumerate(compound.particles()))` 和键关系确认索引；索引依赖输入文件顺序。
- `replace` 氢或其他离去原子时，在删除前保存连接方向。
- 多 Port 组件采用一致标签，如 `up`、`down`、`left`、`right`、`front`、`back`。
- 需要纯几何对齐且不成键时传 `add_bond=False`。
- `available_ports()` 只列出当前 Compound 直接引用的未使用 Port；`all_ports()` 遍历后继节点，包括已使用 Port。

## 封装自定义组件

将稳定结构、位点选择和参数验证放进 `Compound` 子类，使调用者只接触物理参数：

```python
from pathlib import Path
import mbuild as mb


class SingleCarbonSite(mb.Compound):
    def __init__(self, structure_file, separation=0.075):
        super().__init__()
        mb.load(
            str(structure_file),
            compound=self,
            backend="parmed",
            infer_hierarchy=False,
        )
        carbons = list(self.particles_by_name("C"))
        if len(carbons) != 1:
            raise ValueError("Expected exactly one carbon attachment site")
        self.add(
            mb.Port(
                anchor=carbons[0],
                orientation=[0, 1, 0],
                separation=separation,
            ),
            label="up",
        )


structure_file = Path(__file__).resolve().parent / "site.pdb"
site = SingleCarbonSite(structure_file)
```

这个类只适用于恰好一个碳位点的输入。真实组件应按化学名称、元素和键邻居选择锚点，并验证预期粒子数、键数及 Port 方向。

## 坐标变换

所有变换原地修改对象：

```python
import numpy as np

molecule.translate([0.1, 0.0, 0.0])
molecule.translate_to([1.0, 1.0, 1.0])
molecule.rotate(np.pi / 2, around=[0, 0, 1])
molecule.spin(np.pi, around=[0, 1, 0])
```

- `translate()` 相对移动；`translate_to()` 将 Compound 中心移到目标点。
- `rotate()` 绕经过原点的轴旋转；`spin()` 绕自身中心或指定 anchor 旋转。
- 变换会同时移动真实粒子和 Port；使用 `xyz` 只处理真实粒子，`xyz_with_ports` 包含 ghost 粒子。
- 需要保留原型时先 `mb.clone()`，避免后续体系共享被修改的坐标。

完成标准：每种组件的粒子、键、层级、锚点、Port 方向和独立性均已检查；至少一次实际连接形成预期的新键。
