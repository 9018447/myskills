# MDAnalysis AtomGroup Python用法详解

## 目录

1. [基础导入和设置](#1-基础导入和设置)
2. [创建AtomGroup的不同方法](#2-创建atomgroup的不同方法)
   - 2.1 [使用选择语言](#21-使用选择语言)
   - 2.2 [通过索引和切片](#22-通过索引和切片)
   - 2.3 [布尔索引](#23-布尔索引)
   - 2.4 [从现有AtomGroup构建](#24-从现有atomgroup构建)
3. [AtomGroup属性和方法](#3-atomgroup属性和方法)
   - 3.1 [基本属性](#31-基本属性)
   - 3.2 [位置和坐标](#32-位置和坐标)
   - 3.3 [几何计算](#33-几何计算)
4. [高级操作示例](#4-高级操作示例)
   - 4.1 [按残基分组](#41-按残基分组)
   - 4.2 [按属性分组](#42-按属性分组)
   - 4.3 [迭代和遍历](#43-迭代和遍历)
5. [动态选择示例](#5-动态选择示例)
6. [实用函数示例](#6-实用函数示例)
   - 6.1 [计算RMSD](#61-计算rmsd)
   - 6.2 [计算径向分布函数](#62-计算径向分布函数)
7. [条件选择和过滤](#7-条件选择和过滤)
8. [数据导出和可视化准备](#8-数据导出和可视化准备)
9. [性能优化技巧](#9-性能优化技巧)
10. [错误处理和调试](#10-错误处理和调试)

---

## 1. 基础导入和设置

```python
import MDAnalysis as mda
from MDAnalysis.tests.datafiles import PSF, DCD
import numpy as np

# 创建示例系统
u = mda.Universe(PSF, DCD)  # 加载PSF和DCD文件
```

## 2. 创建AtomGroup的不同方法

### 2.1 使用选择语言
```python
# 选择所有蛋白质原子
protein = u.select_atoms('protein')

# 选择特定残基
residue_10 = u.select_atoms('resid 10')

# 选择特定原子类型
backbone = u.select_atoms('backbone')

# 复杂选择
water_and_ions = u.select_atoms('resname SOL or resname NA or resname CL')
```

### 2.2 通过索引和切片
```python
# 获取前10个原子
first_10_atoms = u.atoms[:10]

# 获取每隔一个原子
every_other_atom = u.atoms[::2]

# 获取特定范围
range_atoms = u.atoms[100:200:5]
```

### 2.3 布尔索引
```python
# 基于条件的布尔索引
masses = u.atoms.masses
heavy_atoms = u.atoms[masses > 12.0]  # 选择质量大于12的原子

# 基于位置的布尔索引
positions = u.atoms.positions
z_positive = u.atoms[positions[:, 2] > 0]  # z坐标为正的原子
```

### 2.4 从现有AtomGroup构建
```python
# 通过加法组合
combined = protein + water_and_ions

# 通过减法排除
no_hydrogen = u.atoms - u.select_atoms('hydrogen')

# 使用集合操作
intersection = protein.intersection(u.select_atoms('backbone'))
union_group = protein.union(water_and_ions)
difference = protein.difference(u.select_atoms('hydrogen'))
```

## 3. AtomGroup属性和方法

### 3.1 基本属性
```python
print(f"原子数量: {len(protein)}")
print(f"原子ID: {protein.ids}")
print(f"残基ID: {protein.resids}")
print(f"残基名称: {protein.resnames}")
print(f"原子名称: {protein.names}")
print(f"原子类型: {protein.types}")
print(f"质量: {protein.masses}")
print(f"电荷: {protein.charges}")
```

### 3.2 位置和坐标
```python
# 获取当前帧的位置
positions = protein.positions
print(f"位置形状: {positions.shape}")

# 获取质心
center_of_mass = protein.center_of_mass()
print(f"质心: {center_of_mass}")

# 获取几何中心
centroid = protein.centroid()
print(f"几何中心: {centroid}")

# 获取边界框
bbox = protein.bbox()
print(f"边界框: {bbox}")
```

### 3.3 几何计算
```python
# 计算回转半径
rg = protein.radius_of_gyration()
print(f"回转半径: {rg}")

# 计算最小距离
distance = protein[0].distance_to(protein[1])
print(f"原子间距离: {distance}")

# 计算角度
angle = protein[0].angle(protein[1], protein[2])
print(f"角度: {angle}")
```

## 4. 高级操作示例

### 4.1 按残基分组
```python
# 按残基分割
residue_groups = protein.split('residue')

# 按分子分割
molecule_groups = u.atoms.split('molecule')

# 按段分割
segment_groups = u.atoms.split('segment')
```

### 4.2 按属性分组
```python
# 按残基名称分组
by_resname = protein.groupby('resname')

# 按链分组
by_segment = u.atoms.groupby('segid')

# 按多个属性分组
by_resname_and_chain = protein.groupby(['resname', 'segid'])
```

### 4.3 迭代和遍历
```python
# 遍历所有原子
for atom in protein[:10]:  # 前10个原子
    print(f"原子: {atom.name}, 残基: {atom.resname}{atom.resid}")

# 遍历所有残基
for residue in protein.residues:
    print(f"残基: {residue.resname}{residue.resid}, 原子数: {len(residue.atoms)}")

# 遍历所有片段
for segment in u.segments:
    print(f"段: {segment.segid}, 分子数: {len(segment.molecules)}")
```

## 5. 动态选择示例

```python
# 创建动态选择（随时间变化）
mobile_protein = u.select_atoms('protein and around 5.0 resid 100', updating=True)

# 在轨迹循环中使用
for ts in u.trajectory:
    # 选择当前帧中距离参考点5Å内的水分子
    nearby_water = u.select_atoms('resname SOL and around 5.0 protein')
    print(f"时间步 {ts.frame}: {len(nearby_water)} 个附近水分子")
```

## 6. 实用函数示例

### 6.1 计算RMSD
```python
from MDAnalysis.analysis import rms

# 计算蛋白质骨架的RMSD
R = rms.RMSD(protein.select_atoms('backbone'), 
             ref_frame=0, 
             verbose=True)
R.run()

print("RMSD结果:")
print(R.rmsd.shape)
```

### 6.2 计算径向分布函数
```python
from MDAnalysis.analysis import rdf

# 计算氧原子间的径向分布函数
oxygen = u.select_atoms('name OH*')
rdf_result = rdf.InterRDF(oxygen, oxygen).run()
```

## 7. 条件选择和过滤

```python
def select_by_distance(ref_group, target_group, cutoff=5.0):
    """选择距离参考组小于指定截断距离的目标原子"""
    distances = []
    for atom in target_group:
        min_dist = float('inf')
        for ref_atom in ref_group:
            dist = atom.distance_to(ref_atom)
            if dist < min_dist:
                min_dist = dist
        distances.append(min_dist)
    
    # 返回距离小于截断值的原子
    mask = np.array(distances) < cutoff
    return target_group[mask]

# 使用示例
protein_heavy = protein.select_atoms('not hydrogen')
water_oxygens = u.select_atoms('resname SOL and name OW')
nearby_water = select_by_distance(protein_heavy, water_oxygens, cutoff=3.5)
```

## 8. 数据导出和可视化准备

```python
# 导出坐标用于可视化
def export_coordinates(atomgroup, filename):
    """导出原子坐标到文本文件"""
    coords = atomgroup.positions
    np.savetxt(filename, coords, 
               header=f'Coordinates for {len(atomgroup)} atoms',
               fmt='%.3f')

# 导出用于分析的数据
def prepare_analysis_data(atomgroup):
    """准备分析所需的数据结构"""
    data = {
        'positions': atomgroup.positions,
        'names': atomgroup.names,
        'resnames': atomgroup.resnames,
        'resids': atomgroup.resids,
        'masses': atomgroup.masses,
        'charges': atomgroup.charges
    }
    return data

# 使用示例
analysis_data = prepare_analysis_data(protein)
export_coordinates(protein, 'protein_coords.txt')
```

## 9. 性能优化技巧

```python
# 避免重复选择 - 缓存AtomGroup
cached_selection = u.select_atoms('protein and name CA')  # 缓存选择

# 批量操作而不是逐个原子操作
def batch_process(atomgroup):
    """批量处理原子组"""
    positions = atomgroup.positions
    # 向量化操作
    center = positions.mean(axis=0)
    centered_positions = positions - center
    return centered_positions

# 使用NumPy进行高效计算
def fast_distance_calculation(group1, group2):
    """快速计算两组原子间的最小距离"""
    pos1 = group1.positions
    pos2 = group2.positions
    
    # 使用广播计算所有距离
    diff = pos1[:, np.newaxis, :] - pos2[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=2))
    
    return np.min(distances)
```

## 10. 错误处理和调试

```python
def safe_select_atoms(universe, selection_string):
    """安全的选择函数，包含错误处理"""
    try:
        atomgroup = universe.select_atoms(selection_string)
        if len(atomgroup) == 0:
            print(f"警告: 选择 '{selection_string}' 返回了空的AtomGroup")
        return atomgroup
    except Exception as e:
        print(f"选择失败: {e}")
        return None

# 检查AtomGroup的有效性
def validate_atomgroup(atomgroup):
    """验证AtomGroup是否有效"""
    if atomgroup is None:
        return False
    if len(atomgroup) == 0:
        print("AtomGroup为空")
        return False
    return True

# 使用示例
selected = safe_select_atoms(u, 'protein')
if validate_atomgroup(selected):
    print(f"成功选择了 {len(selected)} 个原子")
else:
    print("选择无效或为空")
```

这些示例展示了MDAnalysis中AtomGroup的各种实用Python用法，从基础操作到高级分析技术，可以帮助您更有效地进行分子动力学分析。