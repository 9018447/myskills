# 导出、力场、验证与故障排查

## 保存结构与层级

```python
system.save("system.pdb", overwrite=True, box=system.box)
system.save("system.mol2", overwrite=True)
system.save("system.gro", overwrite=True, residues=["ETO", "HOH"])
system.save("component.json", overwrite=True, include_ports=True)
```

- 默认不输出 Port；只有调试或保存可复用组件时才考虑 `include_ports=True`。
- `overwrite` 默认 False。自动化脚本选择新输出路径，只有用户允许替换时才设 True。
- 周期体系显式传 `box=system.box`。省略时，部分写出路径使用加缓冲的 bounding box，可能丢失目标模拟盒。
- `residences` 不是参数；残基参数名为 `residues`，取 Compound 的 `name`。
- mBuild JSON 用于保留层级、键和可用 Port，适合组件往返；PDB/GRO/MOL2 等主要用于模拟器交换，不保证保留完整组件层级。

主要格式包括 PDB、MOL2、GRO、TOP、GSD、LAMMPS data、XYZ、JSON、MCF、PSF；SDF 需要 Open Babel。具体支持由当前 mBuild、GMSO 和 ParmEd 后端共同决定，先用小规模往返验证目标格式。

## 结构输出不等于力场输出

当前 `Compound.save()` 负责结构与格式转换，不会自动替体系选择或应用力场。没有原子定型时，PDB/MOL2/GRO 主要包含坐标和键；不要把原子名称当作已经验证的力场类型。

使用 Foyer 时，将 mBuild 转为 ParmEd，再显式应用力场：

```python
import foyer

forcefield = foyer.Forcefield(name="oplsaa")
structure = system.to_parmed(residues=["ETO", "HOH"])
typed = forcefield.apply(structure)
typed.save("system.top", overwrite=True)
typed.save("system.gro", overwrite=True)
```

此例生成 GROMACS 的 TOP/GRO 文件对，需要 Foyer 及其兼容运行时；其他目标引擎可能还要求 GMSO、MoSDeF-GOMC 等扩展。力场 XML、SMARTS 匹配、残基名称、原子名称、电荷和缺失参数都要检查。出现未匹配原子或参数时停止交付参数化结果，不用零参数或名称替换掩盖。

OPLS-AA 的 Ryckaert-Bellemans 扭转项在 ParmEd 中通常位于 `typed.rb_torsions`，此时 `typed.dihedrals` 可以为空。验证时检查 `typed.dihedrals or typed.rb_torsions`，并结合所用泛函形式审查 improper 警告，不要求所有扭转项都存放在同一个列表。

`energy_minimize()` 是另一项独立能力：

- 默认 UFF 等通用力场路径需要 Open Babel。
- 使用 Foyer XML/OPLS-AA 和 OpenMM 的路径需要相应可选依赖。
- 适合几十到几百粒子的小组分，不把它当作整个大体系的通用预平衡替代品。
- RDKit SMILES 导入已做初始 UFF 几何优化，但这不等于目标模拟力场参数化。

## 可视化

Jupyter 中：

```python
component.visualize(show_ports=True)
system.visualize(show_ports=False)
```

默认可视化后端为 py3dmol，也支持 nglview；先检查对应包是否安装。无界面环境用结构保存、层级打印、数值检查和外部查看器，不把可视化调用作为 headless 脚本的必要步骤。

## 数值与拓扑检查

```python
from collections import Counter
import numpy as np

assert np.isfinite(system.xyz).all()
assert system.n_particles == expected_particles
assert system.n_bonds == expected_bonds
assert system.box is not None

child_counts = Counter(child.name for child in system.children)
print(child_counts)
system.print_hierarchy()
```

按体系契约推导 `expected_particles` 和 `expected_bonds`：

- N 个未跨分子成键的副本：粒子数和键数均为单组分的 N 倍。
- 每用 `force_overlap()` 连接一对带锚点的 Port：新增一条键，两个 Port 被占用并移除。
- Polymer：重复次数乘 sequence 长度得到单体数，再计入端基或封端氢。
- Lattice：晶胞数乘每晶胞基点数，再考虑自定义跨晶胞键。

检查重叠：

```python
overlaps = system.check_for_overlap(
    excluded_bond_depth=1,
    minimum_distance=0.10,
)
assert not overlaps
```

此功能需要 `freud`。`excluded_bond_depth=1` 排除直接键合原子；若阈值仍小于 1–2、1–3 等局部化学距离，按需调整排除深度并解释。无 freud 时至少做有限坐标、解析拓扑、PACKMOL 收敛和外部引擎检查，不声称已完成全面碰撞验证。

文件往返：

```python
reloaded = mb.load("system.pdb", backend="parmed")
assert reloaded.n_particles == system.n_particles
assert reloaded.n_bonds == system.n_bonds
assert reloaded.box.lengths == system.box.lengths
```

ParmEd 可能推断键，因此还要抽查元素、残基和关键连接；往返相同也可能只是重复同一推断。最终科学验证应包括目标模拟器对输入文件的解析和短时能量/稳定性检查。

## 常见错误与处理

### `DelayImportError` 或 `No module named 'mdtraj'`

PDB 默认后端是 MDTraj。安装它，或对已有文件显式使用 `backend="parmed"` 并验证键。内置 recipe 若内部固定使用默认 PDB 路径，仅修改外层调用无效，需要补依赖或改用自定义组件。

### GMSO 写出 XYZ 时 `No module named 'foyer'`

本次验证所用 GMSO 0.18.0 的 formats 导入链会加载 Foyer，即使只写坐标。补齐兼容的 Foyer 运行时后再执行 PACKMOL；不要把此错误误诊为 PACKMOL 缺失。

本仓库 `environment-dev.yml` 使用 MoSDeF 的 Foyer 和 forcefield-utilities 开发源码，以及 OpenMM。一次性验证可用临时 overlay：

```bash
uv run \
  --with 'foyer @ git+https://github.com/mosdef-hub/foyer.git@main' \
  --with 'forcefield-utilities @ git+https://github.com/mosdef-hub/forcefield-utilities.git@main' \
  --with openmm --with mdtraj --with lark --with requests \
  python script.py
```

该命令跟随 main，适合验证而非长期复现。正式环境应记录并固定解析后的 commit 和包版本；也可以直接使用项目声明的 conda 开发环境。不要只安装 PyPI Foyer 0.7.6 后继续叠加兼容包：它依赖旧 OpenMM 的 `simtk` 命名空间，当前 Python 3.12 无法解析相应的旧 OpenMM 轮子。

### `No module named 'pkg_resources'`

旧 PyPI Foyer 0.7.6 还需要 setuptools 提供的 `pkg_resources`，而新版 setuptools 已移除它。维护明确使用旧 OpenMM 的历史环境时可固定 `setuptools<81`；当前 Python 3.12 新环境采用上面的开发栈，而不是仅降级 setuptools 后继续处理 `simtk` 错误。

### `packmol` 为 None 或 PACKMOL 不收敛

先确认可执行文件位于 `uv run` 环境的 PATH。收敛失败时检查盒子是否过小、密度是否过高、分子自身几何、overlap/edge、sidemax 和固定朝向；保留 `packmol_file` 检查实际输入。不要通过删除分子或忽略未放置原子来制造成功。

### `Exactly 2 of n_compounds, box, and density must be specified`

为 `fill_box` 恰好提供其中两个。多组分使用 box + density 时还要提供 `compound_ratio`。`fill_sphere` 则只在 n_compounds 和 density 中提供一个。

### `edge must be 0 if use_pbc is set to True`

周期填充使用 `use_pbc=True, edge=0`。需要边界缓冲时使用非周期填充，并明确输出体系不是按 PBC 放置。

### 粒子数或键数不符

依次检查：输入文件是否含键、叶粒子索引是否选错、是否重复添加同一实例而未 clone、Port 是否被封端、sequence 的 n 是否误解、JSON 是否漏掉 Port。打印层级和每组分计数，定位到首次偏离的构建步骤。

### `Port` 方向或分离距离异常

在删除离去原子前计算方向；Port 的 separation 是锚点到 Port 中心距离，两个 Port 各承担目标键长的一半。已使用 Port 上调用 `update_separation()` 或 `update_orientation()` 不会改变已成键结构，应在连接前设置。

### 保存后盒长变大或不对

保存时显式传 `box=system.box`。未提供盒子时，部分后端会使用加 0.5 nm 总缓冲的 bounding box，这不是目标周期盒。

## 交付前证据

- 完整脚本的实际命令与退出码。
- mBuild 版本、关键可选依赖、PACKMOL 路径和两个随机 seed。
- 组分计数、粒子数、键数、可用 Port、盒子与周期性。
- 输出文件重新读取结果；适用时的 overlap 检查。
- 力场来源和原子定型结果，或明确说明只交付结构。
- 尚未验证的化学假设、目标模拟器兼容性和生产尺度适用性。
