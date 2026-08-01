# MDAnalysis增强采样分析集成

## 目录

1. [增强采样与COLVAR文件](#1-增强采样与colvar文件)
2. [偏置权重提取与应用](#2-偏置权重提取与应用)
3. [加权直方图分析](#3-加权直方图分析)
4. [多温度分析组织](#4-多温度分析组织)

---

## 1. 增强采样与COLVAR文件

增强采样方法（如元动力学metadynamics、伞形采样umbrella sampling）通过施加偏置势加速构型空间采样。PLUMED等工具会在轨迹之外生成COLVAR文件，记录集体变量和偏置势信息。

### COLVAR文件格式

典型COLVAR文件为空格分隔的文本文件：

```
#! FIELDS time distcn bias
#! SET min_distcn 0.5
  0.0000  2.345  0.000
  0.0005  2.567  1.234
  0.0010  2.123  0.567
  ...
```

### 加载COLVAR数据

```python
import numpy as np
import pandas as pd

# 方法1: numpy
colvar = np.loadtxt('COLVAR', comments='#')  # 跳过注释行
# 列顺序与FIELDS行对应

# 方法2: pandas（更灵活）
colvar = pd.read_csv('COLVAR', sep=r'\s+', comment='#',
                     names=['time', 'distcn', 'bias'])
bias = colvar['bias'].values
```

### 与MDAnalysis轨迹帧对齐

```python
import MDAnalysis as mda

u = mda.Universe('traj.lammpstrj', topology_format='LAMMPSDUMP')
u.trajectory.ts.dt = 0.0005  # 设置时间步

# 确保帧数一致
bias = np.loadtxt('COLVAR', comments='#')[:, -1]  # 最后一列为bias
assert u.trajectory.n_frames == len(bias), "帧数不匹配"
```

---

## 2. 偏置权重提取与应用

增强采样的核心是利用偏置势对构型进行重新加权，恢复无偏分布。

### 权重计算公式

```python
import numpy as np

# 从COLVAR提取bias
bias = np.loadtxt('COLVAR', comments='#')[:, -1]

# 计算玻尔兹曼权重
# beta = 1 / (kB * T)，kB = 8.314e-3 kJ/(mol·K)
T = 300  # 温度 (K)
kB = 8.314e-3  # kJ/(mol·K)
beta = 1.0 / (kB * T)

# 权重 = exp(beta * bias)
weights = np.exp(beta * bias)

# 归一化权重（用于概率密度估计）
weights_normalized = weights / weights.sum()
```

### 在AnalysisBase中集成

```python
class EnhancedSamplingAnalysis(AnalysisBase):
    def __init__(self, atomgroup, colvar_file, temperature=300, **kwargs):
        super().__init__(atomgroup.universe.trajectory, **kwargs)
        self.atomgroup = atomgroup
        self.cell = atomgroup.universe.dimensions

        # 加载COLVAR
        self.bias = np.loadtxt(colvar_file, comments='#')[:, -1]
        assert atomgroup.universe.trajectory.n_frames == len(self.bias)

        # 计算beta
        self.beta = 1.0 / (8.314e-3 * temperature)

    def _prepare(self):
        self.results.angles = []
        self.results.frame_indices = []

    def _single_frame(self):
        # 当前帧的分析逻辑
        frame = self._ts.frame
        # ... 计算结构特征 ...
        self.results.frame_indices.append(frame)

    def _conclude(self):
        # 获取对应帧的bias权重
        self.results.weights = np.exp(self.beta * self.bias[self.results.frame_indices])
```

---

## 3. 加权直方图分析

### 使用matplotlib绘制加权直方图

```python
import matplotlib.pyplot as plt
import numpy as np

# 分析结果和对应权重
angles_deg = np.degrees(angles)  # 角度数据（度）
weights = np.exp(beta * bias)    # 偏置权重

# 绘制加权直方图
plt.hist(angles_deg, weights=weights, bins=100, density=True)
plt.xlabel('Angle (°)')
plt.ylabel('Weighted Probability Density')
plt.savefig('weighted_distribution.png', dpi=300)
```

### 使用numpy进行程序化加权分析

```python
# 加权直方图
hist, bin_edges = np.histogram(
    angles_deg,
    bins=100,
    weights=weights,
    density=True
)

# 加权统计量
weighted_mean = np.average(angles_deg, weights=weights)
weighted_std = np.sqrt(np.average((angles_deg - weighted_mean)**2, weights=weights))

# 加权核密度估计（更严谨的方法）
from scipy.stats import gaussian_kde
kde = gaussian_kde(angles_deg, weights=weights / weights.sum())
x_grid = np.linspace(angles_deg.min(), angles_deg.max(), 500)
density = kde(x_grid)
```

### 帧范围匹配注意事项

当使用`run(start, stop, step)`参数时，需要确保权重数组与实际分析的帧对应：

```python
analysis = EnhancedSamplingAnalysis(u.atoms, 'COLVAR', temperature=300)
analysis.run(start=200000, stop=-1, step=100)

# 在_conclude中，self.results.frame_indices记录了实际分析的帧号
# 对应的权重通过 self.bias[frame_indices] 获取
```

---

## 4. 多温度分析组织

当对同一体系在不同温度下进行采样时，使用面向对象的方法可以有效管理多组数据。

### 多温度分析模板

```python
class MultiTempAnalysis:
    """管理多个温度下的增强采样分析"""

    def __init__(self, system_name, temperatures):
        self.system_name = system_name
        self.temperatures = temperatures
        self.analyses = {}  # temperature -> analysis instance

    def add_temperature(self, temperature, traj_file, colvar_file):
        u = mda.Universe(traj_file, topology_format='LAMMPSDUMP')
        u.trajectory.ts.dt = 0.0005
        analysis = EnhancedSamplingAnalysis(u.atoms, colvar_file, temperature=temperature)
        self.analyses[temperature] = {
            'universe': u,
            'analysis': analysis,
        }

    def run_all(self, **run_kwargs):
        for temp, data in self.analyses.items():
            print(f"Running T={temp} K...")
            data['analysis'].run(**run_kwargs)

    def compare_distributions(self, property_name='angles'):
        """比较不同温度下的加权分布"""
        fig, ax = plt.subplots()
        for temp, data in sorted(self.analyses.items()):
            angles = np.degrees(data['analysis'].results.angles)
            weights = data['analysis'].results.weights
            ax.hist(angles, weights=weights, bins=100,
                    density=True, alpha=0.5, label=f'{temp} K')
        ax.legend()
        ax.set_xlabel('Angle (°)')
        ax.set_ylabel('Weighted Probability Density')
        plt.savefig(f'{self.system_name}_temp_comparison.png', dpi=300)
```

### 使用示例

```python
# 统一文件命名约定: {system}_{temp}.lammpstrj, {system}_{temp}.colvar
mta = MultiTempAnalysis('catalyst_A', temperatures=[300, 400, 500])
mta.add_temperature(300, 'catalyst_A_300.lammpstrj', 'catalyst_A_300.colvar')
mta.add_temperature(400, 'catalyst_A_400.lammpstrj', 'catalyst_A_400.colvar')
mta.add_temperature(500, 'catalyst_A_500.lammpstrj', 'catalyst_A_500.colvar')

mta.run_all(start=10000, step=50)
mta.compare_distributions()
```

通过将不同温度的数据封装为类的属性，可以避免过程式编程中变量繁多、难以追踪的问题，同时便于后续扩展新的分析维度。
