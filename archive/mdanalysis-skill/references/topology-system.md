# MDAnalysis拓扑系统详解

## 目录

1. [拓扑系统概述](#1-拓扑系统概述)
2. [拓扑属性（Topology Attributes）](#2-拓扑属性topology-attributes)
   - 2.1 [标准属性（Canonical Attributes）](#21-标准属性canonical-attributes)
   - 2.2 [格式特定属性](#22-格式特定属性)
   - 2.3 [连接性信息](#23-连接性信息)
   - 2.4 [添加拓扑属性](#24-添加拓扑属性)
   - 2.5 [修改拓扑属性](#25-修改拓扑属性)
   - 2.6 [默认值和属性级别](#26-默认值和属性级别)
3. [拓扑对象（Topology Objects）](#3-拓扑对象topology-objects)
   - 3.1 [四种拓扑对象类型](#31-四种拓扑对象类型)
   - 3.2 [拓扑对象的属性](#32-拓扑对象的属性)
   - 3.3 [添加拓扑对象到Universe](#33-添加拓扑对象到universe)
   - 3.4 [从AtomGroup创建拓扑对象](#34-从atomgroup创建拓扑对象)
   - 3.5 [删除拓扑对象](#35-删除拓扑对象)
4. [拓扑特定方法](#4-拓扑特定方法)
   - 4.1 [需要坐标的通用方法](#41-需要坐标的通用方法)
   - 4.2 [需要电荷属性的方法](#42-需要电荷属性的方法)
   - 4.3 [需要质量属性的方法](#43-需要质量属性的方法)
5. [实际应用示例](#5-实际应用示例)
   - 5.1 [创建和操作拓扑系统](#51-创建和操作拓扑系统)
   - 5.2 [拓扑分析](#52-拓扑分析)
   - 5.3 [拓扑修改](#53-拓扑修改)
6. [最佳实践](#6-最佳实践)
   - 6.1 [拓扑验证](#61-拓扑验证)
   - 6.2 [性能考虑](#62-性能考虑)

---

## 1. 拓扑系统概述

MDAnalysis将宇宙（Universe）的静态数据分组到其拓扑中，这通常从拓扑文件加载。拓扑信息分为三个类别：

- [原子容器（残基和片段）](groups_of_atoms.html#residues-and-segments)
- [原子属性（如名称、质量、温度因子）](#topology-attributes)
- [拓扑对象：键、角、二面角、不当二面角](#topology-objects)

用户几乎不会直接与Topology交互。修改原子容器或拓扑属性通常通过Universe进行。查看容器或拓扑属性的方法，或计算拓扑对象值的方法，通过AtomGroup访问。

## 2. 拓扑属性（Topology Attributes）

MDAnalysis支持每个Atom和AtomGroup的一系列拓扑属性。如果某个属性在Atom上定义，则在AtomGroup上也会定义，反之亦然——但是，它们使用该属性的单数和复数版本专门访问。

### 2.1 标准属性（Canonical Attributes）

这些属性是从每个Universe派生的，包括使用empty()创建的Universe。它们编码每个对象的MDAnalysis顺序。

#### 原子级别的标准属性：
| 属性（Atom） | 属性组（AtomGroup） | 描述                              |
| ------------ | ------------------- | --------------------------------- |
| index        | indices             | MDAnalysis规范原子索引（从0开始） |
| resindex     | resindices          | MDAnalysis规范残基索引（从0开始） |
| segindex     | segindices          | MDAnalysis片段索引（从0开始）     |

#### 通用格式属性：
| 属性（Atom） | 属性组（AtomGroup） | 描述                                       |
| ------------ | ------------------- | ------------------------------------------ |
| id           | ids                 | 原子序列号（从1开始，PSF/DMS/TPR格式除外） |
| mass         | masses              | 原子质量（推测，默认值：0.0）              |
| resid        | resids              | 残基编号（从1开始，TPR格式除外）           |
| resnum       | resnums             | resid的别名                                |
| segid        | segids              | 片段名称（默认：'SYSTEM'）                 |
| type         | types               | 原子名称、元素或力场原子类型               |

### 2.2 格式特定属性

以下表格列出了从支持格式读取的属性，这些属性也可以添加到不支持它们的文件创建的Universe中：

| 属性      | 属性组    | 描述           | 支持的格式                                                                                                                         |
| --------- | --------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| altLoc    | altLocs   | 替代位置       | MMTF, PDB, ENT, PDBQT, XPDB                                                                                                        |
| bonds     | bonds     | 键信息         | DATA, DMS, GSD, MMTF, MOL2, PSF, TOP/PRMTOP/PARM7, TPR, TXYZ/ARC, XML                                                              |
| angles    | angles    | 角信息         | DATA, GSD, PSF, TOP/PRMTOP/PARM7, TPR, XML                                                                                         |
| dihedrals | dihedrals | 二面角信息     | DATA, GSD, PSF, TOP/PRMTOP/PARM7, TPR, XML                                                                                         |
| impropers | impropers | 不当二面角信息 | DATA, GSD, PSF, TOP/PRMTOP/PARM7, TPR, XML                                                                                         |
| charge    | charges   | 部分原子电荷   | DATA, DMS, GSD, MMTF, MOL2, PDBQT, PQR, PSF, TOP/PRMTOP/PARM7, TPR, XML                                                            |
| element   | elements  | 原子元素       | IN/FHIAIMS, MOL2, PDB, TPR, TXYZ/ARC, XYZ                                                                                          |
| name      | names     | 原子名称       | CONFIG, CRD, DMS, GMS, GRO, GSD, HISTORY, IN/FHIAIMS, MMTF, MOL2, PDB, PDBQT, PQR, PSF, TOP/PRMTOP/PARM7, TPR, TXYZ/ARC, XPDB, XYZ |
| resname   | resnames  | 残基名称       | CRD, DMS, GRO, GSD, MMTF, MOL2, PDB, PDBQT, PQR, PSF, TOP/PRMTOP/PARM7, TPR, XPDB                                                  |

### 2.3 连接性信息

MDAnalysis还可以读取连接性信息（如果文件提供）。这些成为可用的拓扑对象，具有额外的功能。

| 属性      | 属性组    | 支持的格式                                                            |
| --------- | --------- | --------------------------------------------------------------------- |
| angles    | angles    | DATA, GSD, PSF, TOP/PRMTOP/PARM7, TPR, XML                            |
| bonds     | bonds     | DATA, DMS, GSD, MMTF, MOL2, PSF, TOP/PRMTOP/PARM7, TPR, TXYZ/ARC, XML |
| dihedrals | dihedrals | DATA, GSD, PSF, TOP/PRMTOP/PARM7, TPR, XML                            |
| impropers | impropers | DATA, GSD, PSF, TOP/PRMTOP/PARM7, TPR, XML                            |

### 2.4 添加拓扑属性

每个上述属性都可以使用add_TopologyAttr()添加到Universe中（如果文件中不可用）。

```python
# 添加拓扑属性的语法
universe.add_TopologyAttr(topologyattr, values=None)

# 示例：添加温度因子
temp_factors = [20.0] * len(universe.atoms)
universe.add_TopologyAttr('tempfactors', temp_factors)

# 示例：添加电荷
charges = [0.0] * len(universe.atoms)
universe.add_TopologyAttr('charges', charges)
```

### 2.5 修改拓扑属性

现有的拓扑属性可以通过分配新值直接修改（注意：此方法不能用于连接性属性，即键、角、二面角和不当二面角）。

```python
# 修改原子名称
protein.atoms.names = ['CA'] * len(protein.atoms)

# 修改残基名称
protein.residues.resnames = ['ALA'] * len(protein.residues)

# 修改电荷
protein.atoms.charges = [0.1, -0.1, 0.0] * (len(protein.atoms)//3)
```

### 2.6 默认值和属性级别

拓扑信息在MDAnalysis中始终与级别相关联：原子、残基或片段之一。例如，indices是原子信息，resindices是残基信息，segindices是片段信息。

| 属性     | 默认值                    | 级别 | 类型          |
| -------- | ------------------------- | ---- | ------------- |
| charges  | 0.0                       | 原子 | float         |
| masses   | 0.0                       | 原子 | numpy.float64 |
| names    | ''                        | 原子 | object        |
| resnames | ''                        | 残基 | object        |
| resids   | 从1到n_residues的连续序列 | 残基 | int           |
| segids   | ''                        | 片段 | object        |

## 3. 拓扑对象（Topology Objects）

MDAnalysis通过连接性定义四种类型的TopologyObject：

### 3.1 四种拓扑对象类型

- **Bond（键）**：连接两个原子
- **Angle（角）**：连接三个原子形成角度
- **Dihedral（二面角）**：连接四个原子形成二面角
- **ImproperDihedral（不当二面角）**：特殊的四原子角度关系

每个拓扑对象的值可以用value()方法计算。

### 3.2 拓扑对象的属性

每个TopologyObject包含以下属性：

- **atoms**：对象中的有序原子
- **indices**：对象中的有序原子索引
- **type**：键/角/二面角/不当二面角的类型，或原子类型的元组
- **is_guessed**：记录对象是从文件读取还是被推测的

### 3.3 添加拓扑对象到Universe

从版本0.21.0开始，有特定方法用于向Universe添加TopologyObject：

```python
# 添加键
universe.add_bonds([(atom1.index, atom2.index)])

# 添加角
universe.add_angles([(atom1.index, atom2.index, atom3.index)])

# 添加二面角
universe.add_dihedrals([(atom1.index, atom2.index, atom3.index, atom4.index)])

# 添加不当二面角
universe.add_impropers([(atom1.index, atom2.index, atom3.index, atom4.index)])
```

### 3.4 从AtomGroup创建拓扑对象

AtomGroup可以通过相应属性表示为键、角、二面角或不当角：

```python
# 从AtomGroup创建拓扑对象
bond = atom_group.bond      # 需要2个原子
angle = atom_group.angle    # 需要3个原子
dihedral = atom_group.dihedral  # 需要4个原子
improper = atom_group.improper  # 需要4个原子

# 计算值
bond_value = bond.value()   # 键长
angle_value = angle.value() # 角度
dihedral_value = dihedral.value()  # 二面角值
```

### 3.5 删除拓扑对象

从版本0.21.0开始，有特定方法用于从Universe删除TopologyObject：

```python
# 删除键
universe.delete_bonds([(atom1.index, atom2.index)])

# 删除角
universe.delete_angles([(atom1.index, atom2.index, atom3.index)])

# 删除二面角
universe.delete_dihedrals([(atom1.index, atom2.index, atom3.index, atom4.index)])

# 删除不当二面角
universe.delete_impropers([(atom1.index, atom2.index, atom3.index, atom4.index)])
```

## 4. 拓扑特定方法

### 4.1 需要坐标的通用方法

以下方法都需要坐标（positions）属性：

```python
# 边界框
bbox = atom_group.bbox()

# 边界球
bsphere_center, bsphere_radius = atom_group.bsphere()

# 几何中心
center = atom_group.center_of_geometry()

# 质心
center_of_mass = atom_group.center_of_mass()

# 平移、旋转、变换
atom_group.translate([10, 0, 0])  # 平移
atom_group.rotate(rotation_matrix)  # 旋转
atom_group.wrap()  # 周期性包装
atom_group.unwrap()  # 解包周期性
```

### 4.2 需要电荷属性的方法

当Universe中定义了charges属性时，以下方法可用：

```python
# 电荷相关计算
center_of_charge = atom_group.center_of_charge()  # 电荷中心
dipole_moment = atom_group.dipole_moment()  # 偶极矩
total_charge = atom_group.total_charge()  # 总电荷
```

### 4.3 需要质量属性的方法

当Universe中定义了masses属性时，以下方法可用：

```python
# 质量相关计算
center_of_mass = atom_group.center_of_mass()  # 质心
total_mass = atom_group.total_mass()  # 总质量
radius_of_gyration = atom_group.radius_of_gyration()  # 回转半径
moment_of_inertia = atom_group.moment_of_inertia()  # 惯性矩
principal_axes = atom_group.principal_axes()  # 主轴
```

## 5. 实际应用示例

### 5.1 创建和操作拓扑系统

```python
import MDAnalysis as mda
import numpy as np

# 创建简单的系统
u = mda.Universe.empty(
    n_atoms=4,
    atom_resindex=[0, 0, 1, 1],
    residue_segindex=[0],
    trajectory=True
)

# 添加基本属性
u.add_TopologyAttr('names', ['C', 'O', 'N', 'C'])
u.add_TopologyAttr('resnames', ['ALA', 'GLY'])
u.add_TopologyAttr('resids', [1, 2])

# 添加键信息
u.add_bonds([(0, 1), (2, 3)])  # 原子0-1和2-3之间形成键

# 添加角信息
u.add_angles([(0, 1, 2)])  # 原子0-1-2形成角

print(f"系统中的键: {len(u.bonds)}")
print(f"系统中的角: {len(u.angles)}")
```

### 5.2 拓扑分析

```python
# 选择特定的原子组
protein = u.select_atoms('protein')

# 计算拓扑相关的性质
if hasattr(protein, 'masses'):
    com = protein.center_of_mass()
    rg = protein.radius_of_gyration()
    print(f"质心: {com}")
    print(f"回转半径: {rg}")

# 如果有电荷信息
if hasattr(protein, 'charges'):
    total_chg = protein.total_charge()
    dipole = protein.dipole_moment()
    print(f"总电荷: {total_chg}")
    print(f"偶极矩: {dipole}")
```

### 5.3 拓扑修改

```python
# 修改现有拓扑属性
def modify_residue_names(universe, old_name, new_name):
    """修改残基名称"""
    resnames = universe.residues.resnames.copy()
    resnames[resnames == old_name] = new_name
    universe.add_TopologyAttr('resnames', resnames)

# 添加自定义属性
def add_custom_attribute(atom_group, attr_name, values):
    """为原子组添加自定义属性"""
    if len(values) != len(atom_group):
        raise ValueError("值的数量必须与原子数量匹配")
    
    # 将属性添加到宇宙
    atom_group.universe.add_TopologyAttr(attr_name, values)
```

## 6. 最佳实践

### 6.1 拓扑验证
```python
def validate_topology(universe):
    """验证拓扑的完整性"""
    print(f"原子数量: {len(universe.atoms)}")
    print(f"残基数量: {len(universe.residues)}")
    print(f"片段数量: {len(universe.segments)}")
    print(f"键数量: {len(universe.bonds) if hasattr(universe, 'bonds') else 0}")
    print(f"角数量: {len(universe.angles) if hasattr(universe, 'angles') else 0}")
```

### 6.2 性能考虑
- 使用适当的属性级别（原子vs残基vs片段）
- 避免不必要的拓扑修改
- 利用向量化操作而非循环

这个详细的指南涵盖了MDAnalysis拓扑系统的各个方面，从基本概念到实际应用，为分子动力学分析提供了完整的拓扑操作框架。