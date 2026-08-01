---
name: mdanalysis-skill
description: |
  Comprehensive MDAnalysis toolkit for molecular dynamics simulation analysis.
  Use when working with MD simulation data for:
  (1) Loading and analyzing trajectories from Gromacs, Amber, NAMD, CHARMM, LAMMPS and other formats,
  (2) Computing RMSD, RMSF, hydrogen bonds, radial distribution functions, and other analyses,
  (3) Atom selection and structural analysis,
  (4) Creating custom analysis workflows for biomolecular simulations.
---

# MDAnalysis Skill

Comprehensive toolkit for analyzing molecular dynamics simulations using MDAnalysis - a Python library for analysis of many-body systems at the molecular scale.

## Quick Start

```python
import MDAnalysis as mda

# Load trajectory
u = mda.Universe('topology.pdb', 'trajectory.xtc')

# Select atoms
ca = u.select_atoms('name CA')

# Analyze
for ts in u.trajectory:
    print(ca.center_of_mass())
```

## Core Workflows

### Load Simulation Data

```python
import MDAnalysis as mda

# From topology + trajectory files
u = mda.Universe('topol.tpr', 'traj.trr')  # Gromacs
u = mda.Universe('protein.psf', 'trajectory.dcd')  # NAMD/CHARMM
u = mda.Universe('topology.pdb', 'trajectory.xtc')  # Generic
```

### Atom Selection

Use CHARMM-style selection syntax:

```python
# By atom name
ca = u.select_atoms('name CA')

# By residue
arg = u.select_atoms('resname ARG')

# Combined
backbone = u.select_atoms('protein and backbone')
```

### Run Analysis

```python
from MDAnalysis.analysis import align, rms, hbonds

# RMSD alignment
aligner = align.AlignTraj(u, u, select='backbone', in_memory=True)
aligner.run()

# Hydrogen bonds
hba = hbonds.HydrogenBondAnalysis(u, d_a_cutoff=3.5)
hba.run()
```

## Reference Files

For detailed information, load these reference files as needed:

- **`references/api.md`** - Complete API reference for Universe, AtomGroup, analysis modules, and selection syntax
- **`references/examples.md`** - Ready-to-use code examples for common analysis tasks (RMSD, distances, H-bonds, PCA, custom analysis)
- **`references/installation.md`** - Installation instructions, dependencies, development setup, and troubleshooting
- **`references/atomgroup-usage.md`** - Detailed AtomGroup usage examples (selection, properties, geometric calculations, data export) - Load when working with complex atom selections or AtomGroup operations
- **`references/trajectory-analysis.md`** - Custom trajectory analysis guide (AnalysisFromFunction, analysis_class decorator, AnalysisBase inheritance) - Load when creating custom analysis workflows
- **`references/topology-system.md`** - Topology system reference (attributes, bonds/angles/dihedrals, adding/modifying topology) - Load when working with topology information or creating/modifying molecular structure
- **`references/io-and-performance.md`** - IO理念与性能优化详解（延迟加载原理、轨迹切片语法、Universe pickle序列化、时间步配置）- Load when working with large trajectories, needing pickle serialization, or understanding MDAnalysis memory model
- **`references/distances-library.md`** - 距离计算库函数详解（capped_distance、calc_angles、calc_dihedrals、配位数计算）- Load when computing distances/angles/dihedrals efficiently or implementing neighbor-based analyses
- **`references/nonorthogonal-box.md`** - 非正交盒子处理详解（晶胞参数转换、三斜盒子距离计算、常见陷阱）- Load when working with non-orthogonal simulation boxes or triclinic cells
- **`references/enhanced-sampling.md`** - 增强采样分析集成（COLVAR文件处理、偏置权重、加权直方图、多温度分析）- Load when analyzing metadynamics, umbrella sampling, or other enhanced sampling simulations

## Bundled Scripts

本 skill 包含三个即用型分析脚本，适用于常见 MD 分析任务。**优先使用脚本**进行快速分析或建立可复用工作流；**使用参考文档**学习 API 或开发自定义 Python 代码。

| 脚本 | 用途 | 何时使用 | 详细文档 |
|------|------|----------|----------|
| `hb_distribution_analysis/` | 通用氢键分析（XY 平面分布 + 生命周期 ACF） | 需要可配置的供体/受体分析、YAML 驱动、无代码修改 | `scripts/hb_distribution_analysis/README.md` |
| `Plot_RDF/residue_rdf_all_pairs.py` | 残基级 RDF 计算所有残基对 | 快速 CLI 工作流、残基集不固定、自动检测体系 | `scripts/Plot_RDF/README.md` |
| `plot_orientation/water_orientation_z_analysis.py` | Z 分辨水分子取向分析 | 界面/板状系统、取向随 Z 坐标变化 | `scripts/plot_orientation/README.md` |

### 快速命令示例

```bash
# 氢键分析（YAML 配置驱动）
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 50

# RDF 计算（自动检测所有残基对）
python scripts/Plot_RDF/residue_rdf_all_pairs.py --structure topol.tpr --trajectory traj.xtc

# 水分子取向分析
python scripts/plot_orientation/water_orientation_z_analysis.py --structure topol.tpr --trajectory traj.trr
```

> **脚本 vs 参考文档**：脚本提供确定性的可运行工作流；参考文档提供 API 说明、理论背景和自定义开发指南。

## Supported Formats

### Simulation Packages
Gromacs, Amber, NAMD, CHARMM, DL_Poly, HooMD, LAMMPS, and others

### Trajectory Formats
DCD, XTC, TRR, NCDF, H5MD, LAMMPS DUMP, GSD, MMTF, XYZ

### Topology Formats
PDB, PQR, PDBQT, PSF, TOP, GRO, MOL2, TPR, ITP, CRD

## Best Practices

1. **Check system first** - Verify atom selection and topology before analysis
2. **Use explicit selections** - Be precise in selection strings
3. **Handle memory carefully** - Process large trajectories in chunks (`u.trajectory[::10]`)
4. **Prefer built-in functions** - Use optimized `MDAnalysis.analysis` modules
5. **Test on small data** - Verify code on subset before full run
6. **Cite properly** - Include MDAnalysis citations in publications
7. **Use lib.distances for raw computation** - `MDAnalysis.lib.distances` functions work without Universe objects and are C-optimized; prefer them over ASE for PBC distance calculations

## Citation

When using MDAnalysis in published work, cite:

- R. J. Gowers et al., Proceedings of the 15th Python in Science Conference, 2016. doi:10.25080/Majora-629e541a-00e
- N. Michaud-Agrawal et al., J. Comput. Chem. 32 (2011), 2319--2327. doi:10.1002/jcc.21787

## Resources

- **Documentation**: https://docs.mdanalysis.org
- **User Guide**: https://userguide.mdanalysis.org
- **GitHub**: https://github.com/MDAnalysis/mdanalysis
- **License**: GNU GPL v2
