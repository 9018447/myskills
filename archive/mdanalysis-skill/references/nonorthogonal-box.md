# MDAnalysis非正交盒子处理详解

## 目录

1. [盒子参数基础](#1-盒子参数基础)
2. [晶胞参数到盒子矩阵转换](#2-晶胞参数到盒子矩阵转换)
3. [非正交盒子中的距离计算](#3-非正交盒子中的距离计算)
4. [常见问题与注意事项](#4-常见问题与注意事项)

---

## 1. 盒子参数基础

MDAnalysis使用6个参数描述模拟盒子：

```python
u = mda.Universe('topol.tpr', 'traj.xtc')

# 盒子参数: [lx, ly, lz, alpha, beta, gamma]
print(u.dimensions)
# [50.0, 50.0, 47.8, 90.0, 90.0, 90.0]
```

| 参数 | 含义 | 单位 |
|------|------|------|
| `lx, ly, lz` | 盒子边长 | Å |
| `alpha` | b与c边的夹角 | 度 |
| `beta` | a与c边的夹角 | 度 |
| `gamma` | a与b边的夹角 | 度 |

**正交盒子**：`alpha = beta = gamma = 90.0`

**非正交（三斜）盒子**：任意角度，常见于LAMMPS三斜晶胞、表面模型等。

---

## 2. 晶胞参数到盒子矩阵转换

MDAnalysis内部将6参数`[a, b, c, alpha, beta, gamma]`转换为3×3盒子矩阵。理解这个转换对非正交体系至关重要。

### 转换函数

```python
from MDAnalysis.lib.mdamath import triclinic_vectors

# 晶胞参数 -> 3×3盒子矩阵
dim = np.array([50.0, 50.0, 50.0, 90.0, 90.0, 60.0])
box_matrix = triclinic_vectors(dim)
# array([[50.0,  0.0,  0.0],
#        [25.0, 43.3,  0.0],
#        [ 0.0,  0.0, 50.0]])
```

### 转换公式

盒子矩阵的构建遵循以下约定：

```
box[0] = [lx, 0, 0]
box[1] = [ly*cos(gamma), ly*sin(gamma), 0]
box[2] = [lz*cos(beta), lz*(cos(alpha) - cos(beta)*cos(gamma))/sin(gamma), ...]
```

其中第一行沿x轴，第二行在xy平面内，第三行为z方向分量。

### 反向转换

```python
from MDAnalysis.lib.mdamath import triclinic_box

# 3×3盒子矩阵 -> 晶胞参数
dim = triclinic_box(box_matrix)
# array([50.0, 50.0, 50.0, 90.0, 90.0, 60.0])
```

---

## 3. 非正交盒子中的距离计算

在非正交盒子中计算距离时，必须传入`box`参数以应用最小镜像约定（Minimum Image Convention, MIC）：

```python
from MDAnalysis.lib.distances import distance_array, capped_distance

# 使用晶胞参数（6参数格式）
box = np.array([50.0, 14.3, 47.8, 90.0, 90.0, 69.2])

# 距离矩阵（自动考虑PBC）
dmat = distance_array(coords1, coords2, box=box)

# 截断距离搜索
pairs, dists = capped_distance(coords1, coords2, max_cutoff=3.5, box=box)
```

### 也可以传入盒子矩阵

```python
# 从Universe获取盒子矩阵
box_matrix = mda.lib.mdamath.triclinic_vectors(u.dimensions)

# 部分函数也接受3×3矩阵
dmat = distance_array(coords1, coords2, box=u.dimensions)  # 推荐：直接传6参数
```

### 在AnalysisBase中使用

```python
class MyAnalysis(AnalysisBase):
    def _single_frame(self):
        # 每帧自动更新dimensions
        box = self.atomgroup.dimensions  # [a, b, c, alpha, beta, gamma]
        pairs, _ = capped_distance(
            coords_A, coords_B, max_cutoff=3.5, box=box
        )
```

---

## 4. 常见问题与注意事项

### dimensions为None或全零

```python
u = mda.Universe('coords.xyz')
print(u.dimensions)  # None 或 [0, 0, 0, 0, 0, 0]

# XYZ等格式不含盒子信息，必须手动设置
u.dimensions = np.array([50.0, 50.0, 50.0, 90.0, 90.0, 90.0])
```

### 验证晶胞参数转换

在使用非正交盒子前，建议验证6参数到3×3矩阵的转换是否正确：

```python
from MDAnalysis.lib.mdamath import triclinic_vectors, triclinic_box

dim = np.array([a, b, c, alpha, beta, gamma])
box_mat = triclinic_vectors(dim)
dim_check = triclinic_box(box_mat)

# 验证往返转换一致
np.testing.assert_allclose(dim, dim_check, atol=1e-6)
```

### LAMMPS三斜盒子

LAMMPS的triclinc盒子使用tilt factor（xy, xz, yz），需注意转换：

```python
# LAMMPS DUMP文件中的盒子信息格式
# tilt factors: xy, xz, yz
# 需要转换为 [a, b, c, alpha, beta, gamma] 格式
# MDAnalysis的LAMMPSReader会自动处理此转换
```

### 单位一致性

MDAnalysis默认使用Å作为长度单位。如果轨迹文件使用其他单位（如nm），需要确认：

```python
# Gromacs轨迹通常使用nm，MDAnalysis会自动转换为Å
# LAMMPS轨迹单位取决于input文件中的units设置
# 建议检查：print(u.dimensions) 确认数值量级是否合理
```

综上，在处理非正交盒子时，关键是确保晶胞参数正确传入距离计算函数，并在必要时验证6参数与3×3矩阵之间的转换一致性。
