# MDAnalysis距离计算库函数详解

## 目录

1. [距离计算库概述](#1-距离计算库概述)
2. [distance_array与self_distance_array](#2-distance_array与self_distance_array)
3. [capped_distance高效邻居搜索](#3-capped_distance高效邻居搜索)
4. [calc_angles与calc_dihedrals](#4-calc_angles与calc_dihedrals)
5. [配位数计算实例](#5-配位数计算实例)
6. [独立使用（无需Universe）](#6-独立使用无需universe)

---

## 1. 距离计算库概述

`MDAnalysis.lib.distances`是MDAnalysis的底层距离计算模块，由C语言编写并封装为Python接口。该模块的核心优势：

- **高性能**：C底层实现，在周期性边界条件下的距离计算比ASE快约15倍
- **独立使用**：不依赖Universe/AtomGroup，可直接传入NumPy坐标数组
- **PBC支持**：通过`box`参数自动处理最小镜像约定（minimum image convention）

### 核心函数一览

| 函数 | 功能 | 输入形状 | 输出形状 |
|------|------|----------|----------|
| `distance_array` | 两组原子间距离矩阵 | (N,3), (M,3) | (N,M) |
| `self_distance_array` | 同组原子间距离矩阵（压缩） | (N,3) | (N*(N-1)/2,) |
| `capped_distance` | 截断距离内的原子对 | (N,3), (M,3) | (pairs, dists) |
| `self_capped_distance` | 截断距离内同组原子对 | (N,3) | (pairs, dists) |
| `calc_angles` | 三原子角度 | 3×(N,3) | (N,) |
| `calc_dihedrals` | 四原子二面角 | 4×(N,3) | (N,) |

---

## 2. distance_array与self_distance_array

### distance_array

计算两组原子之间的完整距离矩阵，考虑周期性边界条件：

```python
import numpy as np
from MDAnalysis.lib.distances import distance_array

# ref: 中心原子坐标 (N, 3)
# conf: 配位原子坐标 (M, 3)
# box: [a, b, c, alpha, beta, gamma]
dmat = distance_array(ref, conf, box=box)
# dmat.shape = (N, M)，dmat[i, j] = ref[i]与conf[j]的距离

# 不考虑PBC（孤立体系或已经处理过周期性）
dmat = distance_array(ref, conf)  # box=None
```

### self_distance_array

计算同组原子之间的距离，返回压缩形式（仅上三角部分）：

```python
from MDAnalysis.lib.distances import self_distance_array

# coords: (N, 3)
dists = self_distance_array(coords, box=box)
# dists.shape = (N*(N-1)/2,)
# 可用MDAnalysis.lib.distances.convert_array_to_matrix还原为(N,N)矩阵
```

---

## 3. capped_distance高效邻居搜索

`capped_distance`是最高效的截断距离搜索函数，适用于配位数计算、近邻列表等场景。

### 基本用法

```python
from MDAnalysis.lib.distances import capped_distance

# 查找cutoff范围内的所有原子对
pairs, distances = capped_distance(
    reference=coords_A,       # (N, 3) 参考原子坐标
    configuration=coords_B,   # (M, 3) 目标原子坐标
    max_cutoff=3.5,           # 最大截断距离（Å）
    min_cutoff=None,          # 最小截断距离（可选，用于排除过近的对）
    box=box,                  # [a, b, c, alpha, beta, gamma]，可选
)

# pairs: (K, 2) 数组，每行为 (ref_index, conf_index)
# distances: (K,) 数组，对应距离值
```

### 搜索方法选择

`method`参数控制搜索算法：

```python
# 暴力搜索（默认，适合小体系）
capped_distance(ref, conf, max_cutoff=5.0, method='bruteforce')

# KD-Tree（适合中等体系，中低密度）
capped_distance(ref, conf, max_cutoff=5.0, method='pkdtree')

# 网格搜索（适合大体系，高密度）
capped_distance(ref, conf, max_cutoff=5.0, method='nsgrid')
```

| 方法 | 适用场景 | 时间复杂度 |
|------|----------|------------|
| `bruteforce` | 原子数<1000 | O(N×M) |
| `pkdtree` | 中等密度体系 | O(N log M) |
| `nsgrid` | 大体系高密度 | O(N+M) |

### self_capped_distance

同组原子之间的截断搜索：

```python
from MDAnalysis.lib.distances import self_capped_distance

pairs, distances = self_capped_distance(
    coords, max_cutoff=3.5, box=box
)
# pairs中每行的两个索引都指向coords
```

---

## 4. calc_angles与calc_dihedrals

直接从坐标数组计算角度和二面角，无需创建AtomGroup：

### calc_angles

```python
from MDAnalysis.lib.distances import calc_angles

# 计算A-B-C角度（弧度）
# positions: 每个形状为 (N, 3)
angles = calc_angles(
    positions_A,  # 第一个原子位置
    positions_B,  # 中心原子位置（角的顶点）
    positions_C,  # 第三个原子位置
    box=box       # 可选，考虑PBC
)
# angles.shape = (N,)，单位为弧度

# 转换为角度
angles_deg = np.degrees(angles)
```

### calc_dihedrals

```python
from MDAnalysis.lib.distances import calc_dihedrals

# 计算A-B-C-D二面角（弧度）
dihedrals = calc_dihedrals(
    positions_A,
    positions_B,
    positions_C,
    positions_D,
    box=box       # 可选
)
# dihedrals.shape = (N,)，范围 [-π, π]
```

---

## 5. 配位数计算实例

利用`capped_distance`和`np.bincount`组合，实现高效的配位数计算：

### 基本配位数函数

```python
import numpy as np
from MDAnalysis.lib.distances import capped_distance

def count_cn(center_atoms, coord_atoms, cutoff_hi, cutoff_lo=None, box=None):
    """计算配位数

    Args:
        center_atoms: (N, 3) 中心原子坐标
        coord_atoms: (M, 3) 配位原子坐标
        cutoff_hi: 最大截断距离（Å）
        cutoff_lo: 最小截断距离（Å），可选
        box: [a, b, c, alpha, beta, gamma]，考虑PBC

    Returns:
        (N,) 数组，每个中心原子的配位数
    """
    pairs, _ = capped_distance(
        reference=center_atoms,
        configuration=coord_atoms,
        max_cutoff=cutoff_hi,
        min_cutoff=cutoff_lo,
        box=box
    )
    cn = np.bincount(pairs[:, 0], minlength=center_atoms.shape[0])
    return cn
```

### 在轨迹分析中使用

```python
# 在AnalysisBase._single_frame中使用
class CoordinationAnalysis(AnalysisBase):
    def _single_frame(self):
        center = self.atomgroup.select_atoms("type 1").positions
        coord = self.atomgroup.select_atoms("type 2").positions
        cn = count_cn(center, coord, cutoff_hi=3.0, box=self.atomgroup.dimensions)
        self.results.cn_history.append(cn.copy())
```

### 性能对比

对于100对100原子的距离矩阵计算（含PBC）：

```python
# MDAnalysis (C优化): ~1 ms
from MDAnalysis.lib.distances import distance_array
dmat = distance_array(xyz1, xyz2, box=cellpar)

# ASE (纯Python): ~17 ms
from ase.geometry import get_distances
vec, dmat = get_distances(xyz1, p2=xyz2, cell=cell, pbc=True)
```

在需要对上万帧重复计算时，MDAnalysis的性能优势非常显著。

---

## 6. 独立使用（无需Universe）

`lib.distances`中的所有函数可以完全独立于Universe和AtomGroup使用，只需要NumPy坐标数组：

```python
import numpy as np
from MDAnalysis.lib.distances import distance_array, capped_distance, calc_angles

# 从任意来源获取坐标（例如自定义文件读取）
coords = np.loadtxt('positions.txt')  # (N, 3)
box = np.array([50.0, 50.0, 50.0, 90.0, 90.0, 90.0])

# 直接计算距离
dmat = distance_array(coords[:10], coords[10:], box=box)

# 直接搜索邻居
pairs, dists = capped_distance(coords[:10], coords[10:], max_cutoff=5.0, box=box)

# 直接计算角度
angles = calc_angles(coords[0:1], coords[1:2], coords[2:3], box=box)
```

这种设计使得`lib.distances`可以嵌入任何Python分析脚本中，无需初始化MDAnalysis的Universe体系。
