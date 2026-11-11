---
name: mbuild
description: "使用 mBuild 构建、连接和组装分子体系，并导出可验证的结构文件。适用于 SMILES/结构文件导入、Compound/Port 组件、聚合物与表面、PACKMOL 填充或溶剂化、晶格/CIF、力场与格式导出。"
---

# mBuild

交付可运行、可复现、经过拓扑检查的 Python 脚本。以当前源码和运行时行为为准；旧教程只用于理解概念。

## 执行流程

### 1. 明确体系契约

从用户输入和现有文件中确定：

- 组分：SMILES 或结构文件、分子名称、原子/粗粒化模型、连接位点。
- 组装：各组分数量或比例、目标密度、区域、链序列、表面覆盖方式。
- 边界：盒子长度与角度、是否周期、非正交盒的表示。
- 交付：输出格式、残基名称、是否包含力场参数、目标模拟器。

缺少科学参数时，先构建明确标注为 smoke test 的小体系；把用户确认作为生产体系的完成条件，不把任意默认值当作物理结论。

### 2. 检查当前环境

在仓库根目录使用 `uv run`，并确认实际导入的是预期版本：

```bash
uv run python - <<'PY'
import importlib.util
import shutil
import mbuild as mb

print("mBuild:", mb.__version__)
print("PACKMOL:", shutil.which("packmol"))
for name in ("rdkit", "parmed", "gmso", "foyer", "mdtraj", "openbabel", "openmm"):
    print(f"{name}:", bool(importlib.util.find_spec(name)))
PY
```

SMILES 首选 RDKit；PACKMOL 填充需要可执行的 `packmol`。当前 mBuild 的 XYZ 写出经过 GMSO，若导入链要求 Foyer，即使不做力场指派也必须补齐它。PDB 默认读取后端是 MDTraj；未安装时显式使用 `backend="parmed"` 并检查推断的键。

缺少依赖时说明缺失项及用途，获得同意后使用项目的依赖管理方式安装。只做一次性验证时，可用临时 overlay，避免改动依赖清单。例如为 PDB 默认后端补充 MDTraj：

```bash
uv run --with mdtraj python script.py
```

当前 PyPI 的 Foyer 0.7.6 依赖旧 OpenMM 的 `simtk` 命名空间，与当前 Python 3.12 可用轮子不兼容。若 GMSO 导入链需要 Foyer，按本仓库 `environment-dev.yml` 选择 Foyer/OpenMM 开发栈；具体临时命令和旧版 `pkg_resources` 问题见 [references/io-validation.md](references/io-validation.md)。

### 3. 按任务分支加载参考

- 创建粒子、读取分子、定义层级、使用 Port 或坐标变换：阅读 [references/components.md](references/components.md)。
- 构建聚合物、烷烃、表面单层或周期平铺：阅读 [references/recipes.md](references/recipes.md)。
- 填充盒子、混合物、溶剂化、球形/局部区域、晶格或 CIF：阅读 [references/systems.md](references/systems.md)。
- 保存格式、残基、力场、可视化、验证或故障排查：阅读 [references/io-validation.md](references/io-validation.md)。

只加载当前分支所需文件。函数参数不确定时查询当前对象，而非凭记忆补齐：

```bash
uv run python -c 'import mbuild as mb; help(mb.fill_box)'
```

### 4. 建立 tracer，再扩大体系

先让一个组分、一次连接或一个晶胞通过，再增加数量和复制次数。每次扩展后检查粒子数、键数、端口、盒子和坐标；不要直到最终保存才运行脚本。

统一单位：

- 长度、坐标、键长、overlap、edge：nm。
- `Compound.rotate()`、`spin()`、二面角变换：弧度。
- `Box` 和 `Lattice` 的角度：度。
- `fill_box` 等函数的 density：kg/m³；粒子质量：amu。

为 RDKit 构象和 PACKMOL 分别设置 seed。保留组分层级与有意义的 `name`，不要提前摊平成纯坐标数组。

### 5. 验证并交付

完成条件：

- 在用户要求的运行目录执行完整脚本，退出码为 0。
- 每类组分的粒子数、键数、数量或比例符合解析计算值。
- 所有应形成的键都存在；可用端口数量符合封端设计。
- 坐标为有限值，盒子与周期性符合契约；输出文件重新读取后拓扑仍正确。
- 力场输出已明确原子定型和参数来源；结构文件不被表述为已完成力场指派。
- 报告脚本、输出文件、seed、验证结果及未验证的科学假设。

## 完整 smoke test

以下示例用 RDKit 创建乙醇、用 PACKMOL 放入周期盒、保存 PDB 并重新读取。先完成环境检查；`foyer` 是当前 GMSO 写出链的运行时依赖，并非在这里应用力场。

```python
from pathlib import Path

import mbuild as mb

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

ethanol = mb.load("CCO", smiles=True, seed=42)
ethanol.name = "ETO"
n_ethanol = 10

system = mb.fill_box(
    compound=ethanol,
    n_compounds=n_ethanol,
    box=mb.Box(lengths=[3.0, 3.0, 3.0]),
    use_pbc=True,
    edge=0,
    seed=42,
)

assert system.n_particles == n_ethanol * ethanol.n_particles
assert system.n_bonds == n_ethanol * ethanol.n_bonds
assert system.periodicity == (True, True, True)
assert system.box.lengths == (3.0, 3.0, 3.0)

output_file = output_dir / "ethanol.pdb"
system.save(str(output_file), overwrite=True, box=system.box)

reloaded = mb.load(str(output_file), backend="parmed")
assert reloaded.n_particles == system.n_particles
assert reloaded.n_bonds == system.n_bonds

print(f"Saved {n_ethanol} ethanol molecules to {output_file}")
print(f"particles={system.n_particles}, bonds={system.n_bonds}")
```

```bash
uv run python build_ethanol.py
```

此例验证几何、拓扑、周期边界和文件往返；它没有应用模拟力场，也不证明目标密度或盒子尺寸适合生产模拟。
