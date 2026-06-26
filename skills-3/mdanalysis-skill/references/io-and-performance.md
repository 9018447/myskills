# MDAnalysis IO理念与性能优化详解

## 目录

1. [IO核心理念：延迟加载](#1-io核心理念延迟加载)
2. [轨迹切片与迭代详解](#2-轨迹切片与迭代详解)
3. [Universe序列化（pickle）](#3-universe序列化pickle)
4. [时间步配置](#4-时间步配置)
5. [性能优化最佳实践](#5-性能优化最佳实践)

---

## 1. IO核心理念：延迟加载

MDAnalysis的IO设计理念是**延迟加载（lazy loading）**：初始化Universe时不会将整条轨迹读入内存，而是仅索引每帧的起始位置。

```python
import MDAnalysis as mda

# 初始化并不会读取坐标数据
u = mda.Universe('topol.tpr', 'traj.xtc')

# 仅索引帧起始位置，不加载坐标
print(u.trajectory)  # <XYZReader traj.xtc with 1000 frames of 5000 atoms>
```

### 内部机制：offset索引

MDAnalysis会遍历文件流，将每帧开头在文件中的字节位置保存在`u.trajectory._offsets`中：

```
文件流:
|<帧0数据>|<帧1数据>|<帧2数据>|...|<帧N数据>|
   ^          ^          ^              ^
offsets[0] offsets[1] offsets[2]    offsets[N]
```

```python
# 查看offset索引（仅在print(u.trajectory)后可用）
print(u.trajectory._offsets)  # array([0, 32400, 64800, ...])
```

这意味着：
- 内存占用仅为N个整数（帧位置），而非N帧完整坐标
- 可以随机访问任意一帧，无需从头读取
- 与ASE每次实例化N个`Atoms`对象的方式相比，内存效率显著更高

### 何时触发真正的数据读取

```python
ag = u.atoms        # 不读取坐标，仅创建引用
xyz = ag.positions  # 此时才读取当前帧的坐标数据

# 迭代时逐帧读取，每帧仅一帧数据在内存中
for ts in u.trajectory:
    print(ag.center_of_mass())  # 每次只有当前帧在内存中
```

---

## 2. 轨迹切片与迭代详解

`u.trajectory`本质上是一个Python迭代器，支持丰富的切片和索引操作。

### 切片语法

```python
# 从第10帧到第10000帧，每20步取一帧
for ts in u.trajectory[10:10000:20]:
    print(ts.frame)  # 10, 30, 50, 70, ...

# 从第0帧开始，每100帧取一帧（抽样分析）
for ts in u.trajectory[::100]:
    process_frame(ts)

# 最后500帧
for ts in u.trajectory[-500:]:
    process_frame(ts)
```

### 直接索引

```python
# 跳转到第70帧（不遍历前面的帧）
u.trajectory[70]
print(u.trajectory.ts)  # <Timestep 70 with unit cell dimensions [50.0, ...]>

# 读取坐标
xyz_70 = u.atoms.positions
```

### 手动导航

```python
# 前进一帧
u.trajectory.next()

# 回到第一帧
u.trajectory.rewind()

# 最后一帧
u.trajectory[-1]
```

### 在自定义分析中使用

在`AnalysisBase`的子类中，轨迹迭代由`run()`方法自动管理：

```python
class MyAnalysis(AnalysisBase):
    def _single_frame(self):
        # self._ts 即当前帧的Timestep
        # self._frame_index 即当前帧在迭代范围内的索引
        positions = self.atomgroup.positions
        # ...

# run()方法支持start/stop/step参数
analysis = MyAnalysis(u.atoms)
analysis.run(start=100, stop=5000, step=10)  # 分析第100-5000帧，每10帧取一次
```

---

## 3. Universe序列化（pickle）

对于大型轨迹文件（数GB级别），遍历文件建立offset索引可能需要数分钟。使用`pickle`可以保存已索引的Universe，避免重复遍历。

### 保存Universe

```python
import pickle
import os
from MDAnalysis import Universe

# 使用绝对路径（重要：确保pickle文件可在任意目录下使用）
xyzfile = os.path.abspath('/path/to/traj.xyz')
outuni = './traj.uni'

u = Universe(xyzfile)
print(u.trajectory)  # 触发offset索引，大文件可能需要几分钟

# 保存已索引的Universe
with open(outuni, 'wb') as f:
    pickle.dump(u, f)
```

### 加载已保存的Universe

```python
import pickle

with open('./traj.uni', 'rb') as f:
    v = pickle.load(f)

print(v.trajectory)  # 直接可用，无需重新遍历文件
# <XYZReader /path/to/traj.xyz with 100 frames of 3240 atoms>
```

### 注意事项

- **必须使用绝对路径**初始化Universe，否则pickle文件在其他目录下可能无法找到轨迹文件
- pickle保存的是offset索引和文件引用，不是坐标数据本身
- 轨迹文件路径不能改变，否则需要重新创建pickle
- 典型性能收益：6GB的XYZ文件遍历约需3分钟，pickle加载仅需数秒

---

## 4. 时间步配置

部分轨迹格式不包含时间步信息，MDAnalysis会发出警告。需要手动设置`dt`：

```python
u = mda.Universe('coords.xyz')

# 设置时间步为0.5 fs = 0.0005 ps
u.trajectory.ts.dt = 0.0005  # 单位：ps

# 现在可以正确获取时间
for ts in u.trajectory:
    print(f"Frame {ts.frame}, time = {ts.time:.4f} ps")
```

如果不设置`dt`，MDAnalysis会使用默认值并可能发出警告。

---

## 5. 性能优化最佳实践

| 技巧 | 说明 | 适用场景 |
|------|------|----------|
| 轨迹切片 | `u.trajectory[::N]`抽样 | 大轨迹快速预览 |
| pickle序列化 | 保存offset避免重新索引 | 重复分析同一轨迹 |
| 预分配数组 | `_prepare()`中分配结果数组 | 自定义分析 |
| 向量化操作 | 使用NumPy而非Python循环 | 距离/角度计算 |
| lib.distances | C优化的底层距离函数 | 所有距离计算 |
| 缓存AtomGroup | 避免循环中重复select_atoms | 多帧迭代分析 |

### 与ASE的性能对比

MDAnalysis的`lib.distances`底层为C实现，在周期性体系距离计算上比ASE快约15倍：

```python
# MDAnalysis: ~1 ms
from MDAnalysis.lib.distances import distance_array
dmatrix = distance_array(xyz1, xyz2, box=cellpar)

# ASE: ~17 ms（同样的计算）
from ase.geometry import get_distances
vec, dmatrix = get_distances(xyz1, p2=xyz2, cell=cell, pbc=True)
```

综上，MDAnalysis的IO设计使其非常适合处理大型轨迹文件的逐帧统计分析，合理利用pickle和切片功能可以显著提高工作效率。
