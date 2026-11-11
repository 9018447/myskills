# 盒子、PACKMOL 与晶格

## Box 与周期边界

```python
import mbuild as mb

orthorhombic = mb.Box(lengths=[4.0, 4.0, 5.0])
triclinic = mb.Box(lengths=[4.0, 4.0, 5.0], angles=[90, 90, 120])
```

长度单位 nm，角度单位度。`Box.vectors` 使用行向量。`Compound.periodicity` 是三个布尔值，不用来设置盒长；盒长通过 `Compound.box = mb.Box(...)` 设置。

PACKMOL 填充函数中：

- `overlap` 控制不同分子的原子间最小距离，单位 nm。
- `edge` 是边界缓冲区；`use_pbc=True` 时必须显式传 `edge=0`。
- `seed` 固定 PACKMOL 随机序列；它不会固定此前的 RDKit 构象 seed。
- `fix_orientation` 可为单个布尔值或与组分等长的列表。
- 大盒子超出初始近似范围时调整 `sidemax`。
- `packmol_file="packmol.inp"` 可保留输入以诊断失败；输出路径由用户指定，不写入源码目录。

## fill_box：均匀液体和混合物

`n_compounds`、`box`、`density` 必须恰好提供两个：

- 数量 + 盒子：直接控制组成和体积。
- 数量 + 密度：计算盒长；多组分时数量列表与 compound 列表等长。
- 盒子 + 密度：计算数量；多组分必须提供 `compound_ratio`。

```python
import mbuild as mb

water = mb.load("O", smiles=True, seed=42)
water.name = "HOH"

system = mb.fill_box(
    compound=water,
    n_compounds=100,
    box=mb.Box([3.0, 3.0, 3.0]),
    use_pbc=True,
    edge=0,
    overlap=0.2,
    seed=42,
)

assert system.n_particles == 100 * water.n_particles
assert system.n_bonds == 100 * water.n_bonds
assert system.periodicity == (True, True, True)
```

按密度构建双组分体系：

```python
system = mb.fill_box(
    compound=[hexane, ethanol],
    box=mb.Box([5.0, 5.0, 5.0]),
    density=680,
    compound_ratio=[0.5, 0.5],
    use_pbc=True,
    edge=0,
    seed=42,
)
```

密度计算需要每个粒子的可靠质量；缺失元素或显式 mass 会导致数量错误。`compound_ratio` 描述数量比，不是质量分数。计算后按各子 Compound 的名称统计实际数量，不假设浮点舍入后的比例完全等于输入。

## solvate：固定一个溶质

```python
solvated = mb.solvate(
    solute=solute,
    solvent=water,
    n_solvent=500,
    box=mb.Box([4.0, 4.0, 4.0]),
    center_solute=True,
    use_pbc=True,
    edge=0,
    overlap=0.2,
    seed=42,
)
```

`solute` 是一个 Compound，不是每种溶质的数量列表。默认将其质心移到盒子中心；已有绝对位置时设 `center_solute=False`。检查溶质是否完整位于目标盒内，以及溶质与溶剂之间是否存在不合理接触。

## fill_region 与 fill_sphere

局部直角区域：

```python
region = mb.Box(lengths=[2.0, 3.0, 3.0])
filled = mb.fill_region(
    compound=water,
    n_compounds=50,
    region=region,
    bounds=[[3.0, 2.0, 2.0, 5.0, 5.0, 5.0]],
    seed=42,
)
```

bounds 顺序为 `[min_x, min_y, min_z, max_x, max_y, max_z]`。多组分时 compound、n_compounds、region、bounds 按位置对应。当前实现会检查每个 bound 的类型，因此使用实际的六元素列表；需要覆盖整个 region 时给出该区域的完整 bounds。

球形区域：

```python
droplet = mb.fill_sphere(
    compound=water,
    sphere=[3.0, 3.0, 3.0, 1.5],
    n_compounds=50,
    seed=42,
)
```

sphere 顺序为球心 x/y/z 和半径，单位 nm。`fill_sphere` 在 `n_compounds` 与 `density` 中恰好提供一个；多组分按密度确定数量时同样需要 `compound_ratio`。

## Lattice：从晶胞构建晶体

`lattice_points` 的 key 是组分 ID，value 是该组分的分数坐标列表；`compound_dict` 用相同 key 映射到实际 Compound。`angles` 与 `lattice_vectors` 二选一，未提供时使用正交晶胞。

```python
import mbuild as mb

lattice = mb.Lattice(
    lattice_spacing=[0.4123, 0.4123, 0.4123],
    lattice_points={
        "Cl": [[0.0, 0.0, 0.0]],
        "Cs": [[0.5, 0.5, 0.5]],
    },
)
crystal = lattice.populate(
    compound_dict={
        "Cl": mb.Compound(name="Cl", element="Cl"),
        "Cs": mb.Compound(name="Cs", element="Cs"),
    },
    x=2,
    y=2,
    z=2,
)

assert crystal.n_particles == 16
assert crystal.box.lengths == (0.8246, 0.8246, 0.8246)
```

每个晶胞有两个粒子，2×2×2 个晶胞共 16 个粒子。分数坐标不是 nm；`lattice_spacing` 才是 nm。

从 CIF 读取：

```python
from mbuild.lattice import load_cif

lattice = load_cif("structure.cif", wrap_coords=True)
crystal = lattice.populate(x=3, y=3, z=3)
```

CIF 分支需要 `garnett`。若 CIF 已定义分子组分，先检查 `lattice.lattice_points`，再提供匹配的 `compound_dict`；否则默认点 ID 创建原子/粒子。检查元素、晶胞角度、分数坐标和复制后的粒子数。

## 组装后的验证

```python
import numpy as np

assert np.isfinite(system.xyz).all()
assert system.box is not None
print(system.print_hierarchy())
```

至少核对：

- `system.n_particles`、`system.n_bonds` 与各组分解析值。
- 每种直接子 Compound 的名称和数量。
- `system.box.lengths`、`angles`、`periodicity`。
- 非周期体系的坐标范围，或周期体系的跨边界分子与键。
- 文件往返后的数量、键和盒子，详见 [io-validation.md](io-validation.md)。

完成标准：完整执行 PACKMOL 或晶格填充，实际组成、盒子、周期性和文件往返均通过断言；PACKMOL 收敛警告已处理，而非仅确认生成了文件。
