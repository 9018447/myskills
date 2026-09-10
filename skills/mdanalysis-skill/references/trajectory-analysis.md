# MDAnalysis自定义轨迹分析深度指南

## 目录
1. [概述](#概述)
2. [三种自定义分析方法](#三种自定义分析方法)
3. [半径回转分析实例](#半径回转分析实例)
4. [AnalysisFromFunction方法](#analysisfromfunction方法)
5. [analysis_class装饰器方法](#analysis_class装饰器方法)
6. [自定义类方法](#自定义类方法)
7. [AnalysisBase基类详解](#analysisbase基类详解)
8. [最佳实践与设计模式](#最佳实践与设计模式)
9. [性能优化技巧](#性能优化技巧)
10. [贡献代码到MDAnalysis](#贡献代码到mdanalysis)

## 概述

MDAnalysis提供了三种不同的方式来创建自定义轨迹分析方法，从最简单到最灵活：

1. **直接从函数运行分析** - 使用`AnalysisFromFunction`
2. **将函数转换为类** - 使用`analysis_class`装饰器
3. **编写自己的类** - 继承`AnalysisBase`基类

本指南将详细介绍这三种方法的使用场景、实现方式和最佳实践。

## 三种自定义分析方法

### 方法对比

| 方法                 | 复杂度 | 灵活性 | 适用场景               |
| -------------------- | ------ | ------ | ---------------------- |
| AnalysisFromFunction | 低     | 中等   | 快速原型开发、简单分析 |
| analysis_class       | 中等   | 中等   | 可重用的分析函数       |
| 自定义AnalysisBase类 | 高     | 高     | 复杂算法、高级功能     |

## 半径回转分析实例

### 半径回转理论基础

半径回转(Radius of Gyration)是衡量结构紧凑程度的重要参数，计算公式如下：

对于整体半径回转：
```
Rg² = Σ(m_i * |r_i - r_cm|²) / M
```

其中：
- m_i 是原子i的质量
- r_i 是原子i的位置
- r_cm 是所选原子组的质心
- M 是总质量

对于各轴方向的半径回转：
```
Rg_x² = Σ(m_i * (y_i - y_cm)² + (z_i - z_cm)²) / M
```

### 实现半径回转计算函数

```python
import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis.base import AnalysisFromFunction, analysis_class
from MDAnalysis.analysis.base import AnalysisBase
import pandas as pd
import matplotlib.pyplot as plt

def radius_of_gyration(ag, masses=None, total_mass=None):
    """
    计算原子组的半径回转
    
    Parameters:
    -----------
    ag : AtomGroup
        要分析的原子组
    masses : array-like, optional
        原子质量数组，避免重复计算
    total_mass : float, optional
        总质量，避免重复计算
    
    Returns:
    --------
    dict : 包含各种半径回转值的字典
    """
    if masses is None:
        masses = ag.masses
    if total_mass is None:
        total_mass = masses.sum()
    
    # 计算质心
    com = ag.center_of_mass()
    
    # 计算相对于质心的位置
    rg_squared = ((ag.positions - com)**2 * masses[:, np.newaxis]).sum(axis=0) / total_mass
    rg_total = np.sqrt(rg_squared.sum())
    
    # 各轴方向的半径回转
    rg_x = np.sqrt(rg_squared[1] + rg_squared[2])  # y² + z²
    rg_y = np.sqrt(rg_squared[0] + rg_squared[2])  # x² + z²
    rg_z = np.sqrt(rg_squared[0] + rg_squared[1])  # x² + y²
    
    return {
        'radius_of_gyration': rg_total,
        'radius_of_gyration_x': rg_x,
        'radius_of_gyration_y': rg_y,
        'radius_of_gyration_z': rg_z
    }
```

## AnalysisFromFunction方法

### 基本用法

`AnalysisFromFunction`是最简单的自定义分析方法，适合快速原型开发：

```python
def create_analysis_from_function_example():
    """
    使用AnalysisFromFunction创建分析示例
    """
    # 加载示例数据
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    
    # 选择蛋白质骨架
    protein = u.select_atoms('protein and name CA')
    
    # 创建分析对象
    rog = AnalysisFromFunction(
        radius_of_gyration,  # 分析函数
        u.trajectory,        # 轨迹
        protein              # 函数的第一个参数
    )
    
    # 运行分析
    rog.run()
    
    # 获取结果
    results = rog.results.timeseries
    print(f"分析完成，共{len(results)}帧")
    print(f"平均半径回转: {np.mean(results):.3f} Å")
    
    return rog

# 运行示例
# rog_func = create_analysis_from_function_example()
```

### 带参数的AnalysisFromFunction

```python
def create_analysis_with_parameters():
    """
    带额外参数的AnalysisFromFunction示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 预计算质量
    masses = protein.masses
    total_mass = masses.sum()
    
    # 创建分析对象，传递额外参数
    rog = AnalysisFromFunction(
        radius_of_gyration,
        u.trajectory,
        protein,
        masses=masses,      # 额外参数
        total_mass=total_mass  # 额外参数
    )
    
    # 运行分析
    rog.run(start=10, stop=80, step=8)  # 指定帧范围
    
    return rog

# 示例：分析特定帧范围
# rog_param = create_analysis_with_parameters()
```

### AnalysisFromFunction的优势与限制

**优势：**
- 实现简单，代码量少
- 适合快速原型开发
- 自动处理轨迹迭代

**限制：**
- 功能相对有限
- 不支持复杂的状态管理
- 结果格式固定

## analysis_class装饰器方法

### 基本用法

`analysis_class`装饰器将普通函数转换为可重用的分析类：

```python
@analysis_class
def radius_of_gyration_analysis(ag, masses=None, total_mass=None):
    """
    使用analysis_class装饰器的半径回转分析
    """
    if masses is None:
        masses = ag.masses
    if total_mass is None:
        total_mass = masses.sum()
    
    com = ag.center_of_mass()
    rg_squared = ((ag.positions - com)**2 * masses[:, np.newaxis]).sum(axis=0) / total_mass
    rg_total = np.sqrt(rg_squared.sum())
    
    rg_x = np.sqrt(rg_squared[1] + rg_squared[2])
    rg_y = np.sqrt(rg_squared[0] + rg_squared[2])
    rg_z = np.sqrt(rg_squared[0] + rg_squared[1])
    
    return {
        'radius_of_gyration': rg_total,
        'radius_of_gyration_x': rg_x,
        'radius_of_gyration_y': rg_y,
        'radius_of_gyration_z': rg_z
    }

def use_analysis_class():
    """
    使用analysis_class创建的类
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 创建分析实例
    rog_analysis = radius_of_gyration_analysis(protein)
    
    # 运行分析
    rog_analysis.run()
    
    # 获取结果
    results = rog_analysis.results
    print(f"分析完成，结果形状: {results.shape}")
    
    return rog_analysis

# 使用示例
# rog_class = use_analysis_class()
```

### 多轨迹重用

```python
def reuse_analysis_class():
    """
    在多个轨迹上重用analysis_class
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    from MDAnalysis.tests.datafiles import GRO, XTC
    
    # 创建分析类
    rog_analysis = radius_of_gyration_analysis
    
    # 第一个轨迹
    u1 = mda.Universe(PSF, DCD)
    protein1 = u1.select_atoms('protein and name CA')
    
    analysis1 = rog_analysis(protein1)
    analysis1.run()
    
    # 第二个轨迹
    u2 = mda.Universe(PSF, DCD)  # 实际使用不同轨迹
    protein2 = u2.select_atoms('protein and name CA')
    
    analysis2 = rog_analysis(protein2)
    analysis2.run()
    
    return analysis1, analysis2
```

### analysis_class的优势与限制

**优势：**
- 可重用性强
- 保持函数的简洁性
- 支持面向对象接口

**限制：**
- 仍然受限于函数式编程模型
- 复杂状态管理仍有限制

## 自定义类方法

### 继承AnalysisBase创建自定义分析类

```python
class RadiusOfGyrationCustom(AnalysisBase):
    """
    自定义半径回转分析类，继承AnalysisBase
    """
    
    def __init__(self, atomgroup, verbose=False):
        """
        初始化分析类
        
        Parameters:
        -----------
        atomgroup : AtomGroup
            要分析的原子组
        verbose : bool
            是否显示进度条
        """
        super().__init__(atomgroup.universe.trajectory, verbose=verbose)
        self.atomgroup = atomgroup
        
    def _prepare(self):
        """
        准备阶段，在循环开始前调用
        """
        # 预计算常量
        self.masses = self.atomgroup.masses
        self.total_mass = self.masses.sum()
        
        # 初始化结果存储
        self.results = []
        self.times = []
        
    def _single_frame(self):
        """
        单帧分析，在每个帧上调用
        """
        # 当前帧的分析
        com = self.atomgroup.center_of_mass()
        positions = self.atomgroup.positions
        
        # 计算半径回转
        rg_squared = ((positions - com)**2 * self.masses[:, np.newaxis]).sum(axis=0) / self.total_mass
        rg_total = np.sqrt(rg_squared.sum())
        
        rg_x = np.sqrt(rg_squared[1] + rg_squared[2])
        rg_y = np.sqrt(rg_squared[0] + rg_squared[2])
        rg_z = np.sqrt(rg_squared[0] + rg_squared[1])
        
        # 存储结果
        self.results.append([
            self._ts.frame,           # 帧号
            self._ts.time,            # 时间
            rg_total,                 # 总半径回转
            rg_x,                     # x方向
            rg_y,                     # y方向
            rg_z                      # z方向
        ])
        
        self.times.append(self._ts.time)
        
    def _conclude(self):
        """
        结束阶段，在循环结束后调用
        """
        # 转换为numpy数组
        self.results = np.array(self.results)
        
        # 创建DataFrame
        self.df = pd.DataFrame(
            self.results,
            columns=[
                'Frame', 'Time (ps)', 'Radius of Gyration',
                'Radius of Gyration (x-axis)', 'Radius of Gyration (y-axis)',
                'Radius of Gyration (z-axis)'
            ]
        )
        
        # 计算平均值
        self.average = self.df.iloc[:, 2:].mean()
        
        # 计算标准差
        self.std = self.df.iloc[:, 2:].std()

def use_custom_class_analysis():
    """
    使用自定义类进行分析
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 创建分析实例
    rog_custom = RadiusOfGyrationCustom(protein, verbose=True)
    
    # 运行分析
    rog_custom.run()
    
    # 显示结果
    print("平均半径回转:")
    print(rog_custom.average)
    
    print("\n结果统计:")
    print(rog_custom.df.describe())
    
    return rog_custom

# 使用示例
# rog_custom = use_custom_class_analysis()
```

### 高级自定义类示例

```python
class AdvancedRadiusOfGyration(AnalysisBase):
    """
    高级半径回转分析类，支持更多功能
    """
    
    def __init__(self, atomgroup, selection='all', verbose=False, 
                 calculate_components=True, output_format='both'):
        """
        初始化高级分析类
        
        Parameters:
        -----------
        atomgroup : AtomGroup
            要分析的原子组
        selection : str
            选择字符串
        verbose : bool
            是否显示进度
        calculate_components : bool
            是否计算各分量
        output_format : str
            输出格式 ('array', 'df', 'both')
        """
        super().__init__(atomgroup.universe.trajectory, verbose=verbose)
        self.atomgroup = atomgroup
        self.calculate_components = calculate_components
        self.output_format = output_format
        
        # 根据选择更新原子组
        if selection != 'all':
            self.atomgroup = self.atomgroup.select_atoms(selection)
    
    def _prepare(self):
        """准备阶段"""
        self.masses = self.atomgroup.masses
        self.total_mass = self.masses.sum()
        
        # 初始化存储
        self.all_results = []
        self.frame_indices = []
        self.times = []
        
        # 如果需要，初始化额外的分析
        if hasattr(self.atomgroup, 'residues'):
            self.residue_info = True
        else:
            self.residue_info = False
    
    def _single_frame(self):
        """单帧分析"""
        # 基本半径回转计算
        com = self.atomgroup.center_of_mass()
        positions = self.atomgroup.positions
        
        # 整体半径回转
        rg_squared = ((positions - com)**2 * self.masses[:, np.newaxis]).sum(axis=0) / self.total_mass
        rg_total = np.sqrt(rg_squared.sum())
        
        result_row = {
            'frame': self._ts.frame,
            'time': self._ts.time,
            'rg_total': rg_total
        }
        
        # 计算各轴分量（如果需要）
        if self.calculate_components:
            rg_x = np.sqrt(rg_squared[1] + rg_squared[2])
            rg_y = np.sqrt(rg_squared[0] + rg_squared[2])
            rg_z = np.sqrt(rg_squared[0] + rg_squared[1])
            
            result_row.update({
                'rg_x': rg_x,
                'rg_y': rg_y,
                'rg_z': rg_z
            })
        
        # 可选：计算残基级别的半径回转
        if self.residue_info:
            residue_rg = self._calculate_residue_level_rg(positions, com)
            result_row['residue_rg'] = residue_rg
        
        self.all_results.append(result_row)
        self.frame_indices.append(self._ts.frame)
        self.times.append(self._ts.time)
    
    def _calculate_residue_level_rg(self, positions, com):
        """计算残基级别的半径回转"""
        residue_rg_values = []
        
        for residue in self.atomgroup.residues:
            res_atoms = residue.atoms & self.atomgroup
            if len(res_atoms) > 0:
                res_positions = res_atoms.positions
                res_masses = res_atoms.masses
                res_com = np.average(res_positions, weights=res_masses, axis=0)
                
                res_rg = np.sqrt(
                    ((res_positions - res_com)**2 * res_masses[:, np.newaxis]).sum() / res_masses.sum()
                )
                residue_rg_values.append(res_rg)
        
        return np.mean(residue_rg_values) if residue_rg_values else 0.0
    
    def _conclude(self):
        """结束阶段"""
        # 创建最终结果
        if self.output_format in ['array', 'both']:
            self.results_array = np.array([
                [r['frame'], r['time'], r['rg_total']] + 
                ([r['rg_x'], r['rg_y'], r['rg_z']] if self.calculate_components else []) +
                ([r.get('residue_rg', 0)] if self.residue_info else [])
                for r in self.all_results
            ])
        
        if self.output_format in ['df', 'both']:
            columns = ['Frame', 'Time (ps)', 'Radius of Gyration']
            if self.calculate_components:
                columns.extend(['RG_X', 'RG_Y', 'RG_Z'])
            if self.residue_info:
                columns.append('Mean_Residue_RG')
            
            self.df = pd.DataFrame(self.all_results)
            self.df = self.df[columns]
        
        # 计算统计信息
        self.stats = {
            'mean': np.mean([r['rg_total'] for r in self.all_results]),
            'std': np.std([r['rg_total'] for r in self.all_results]),
            'min': np.min([r['rg_total'] for r in self.all_results]),
            'max': np.max([r['rg_total'] for r in self.all_results])
        }

def demonstrate_advanced_class():
    """
    演示高级自定义类的使用
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein')
    
    # 创建高级分析实例
    advanced_rog = AdvancedRadiusOfGyration(
        protein, 
        selection='protein and name CA',  # 只分析Cα原子
        verbose=True,
        calculate_components=True,
        output_format='both'
    )
    
    # 运行分析
    advanced_rog.run()
    
    # 显示结果
    print("统计信息:")
    for key, value in advanced_rog.stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n结果形状: {advanced_rog.df.shape}")
    print(advanced_rog.df.head())
    
    return advanced_rog

# 使用示例
# advanced_result = demonstrate_advanced_class()
```

## AnalysisBase基类详解

### AnalysisBase属性和方法

`AnalysisBase`类提供了许多有用的属性和方法：

```python
class AnalysisBaseFeatures(AnalysisBase):
    """
    演示AnalysisBase的所有特性和属性
    """
    
    def __init__(self, atomgroup, verbose=False):
        super().__init__(atomgroup.universe.trajectory, verbose=verbose)
        self.atomgroup = atomgroup
    
    def _prepare(self):
        """
        演示_prepare方法和可用属性
        """
        print("=== _prepare阶段 ===")
        print(f"轨迹长度: {len(self._trajectory)}")
        print(f"初始帧: {self._trajectory[0].frame}")
        print(f"初始时间: {self._trajectory[0].time}")
        
        # 初始化结果存储
        self.results = []
    
    def _single_frame(self):
        """
        演示_single_frame方法和可用属性
        """
        print(f"=== 处理帧 {self._frame_index} ===")
        print(f"  当前帧绝对索引: {self._ts.frame}")
        print(f"  当前时间: {self._ts.time}")
        print(f"  相对帧索引: {self._frame_index}")
        print(f"  当前步长: {self._ts.dt}")
        
        # 实际分析
        result = self.atomgroup.radius_of_gyration()
        self.results.append({
            'frame': self._ts.frame,
            'time': self._ts.time,
            'rg': result,
            'relative_index': self._frame_index
        })
    
    def _conclude(self):
        """
        演示_conclude方法
        """
        print("=== _conclude阶段 ===")
        print(f"总共处理了 {len(self.results)} 帧")
        print(f"起始帧: {self.start}")
        print(f"结束帧: {self.stop}")
        print(f"步长: {self.step}")
        print(f"分析帧数: {self.n_frames}")
        print(f"是否详细输出: {self._verbose}")
        
        self.final_results = pd.DataFrame(self.results)

def demonstrate_analysisbase_features():
    """
    演示AnalysisBase的所有功能
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    analyzer = AnalysisBaseFeatures(protein, verbose=True)
    analyzer.run(start=0, stop=10, step=2)
    
    return analyzer
```

### AnalysisBase的关键属性

| 属性                | 描述             | 用途                     |
| ------------------- | ---------------- | ------------------------ |
| `self.start`        | 开始分析的帧索引 | 在run()中定义            |
| `self.stop`         | 停止分析的帧索引 | 在run()中定义            |
| `self.step`         | 帧间跳跃数       | 在run()中定义            |
| `self.n_frames`     | 分析的总帧数     | 用于初始化结果数组       |
| `self._verbose`     | 详细输出标志     | 控制进度条显示           |
| `self._trajectory`  | 实际轨迹对象     | 访问轨迹数据             |
| `self._ts`          | 当前时间步对象   | 访问当前帧数据           |
| `self._frame_index` | 相对帧索引       | 当前帧在分析范围内的索引 |

### 运行方法详解

```python
def explain_run_method():
    """
    详细解释run方法的工作流程
    """
    print("""
    AnalysisBase.run()方法执行顺序：
    
    1. 设置分析参数 (start, stop, step)
    2. 调用 _prepare() - 初始化阶段
    3. 循环遍历轨迹帧：
       - 设置当前时间步 (self._ts)
       - 调用 _single_frame() - 单帧分析
       - 更新相对帧索引 (self._frame_index)
    4. 调用 _conclude() - 结束和汇总阶段
    
    这种设计模式确保了：
    - 统一的接口
    - 自动的轨迹管理
    - 可选的进度显示
    - 标准化的结果存储
    """)
```

## 最佳实践与设计模式

### 设计模式1：工厂模式

```python
class RadiusOfGyrationFactory:
    """
    半径回转分析工厂类
    """
    
    @staticmethod
    def create_analysis(method='function', **kwargs):
        """
        根据方法类型创建分析实例
        
        Parameters:
        -----------
        method : str
            分析方法 ('function', 'class', 'custom')
        **kwargs : dict
            传递给分析类的参数
        """
        atomgroup = kwargs.pop('atomgroup')
        
        if method == 'function':
            return AnalysisFromFunction(radius_of_gyration, atomgroup.universe.trajectory, atomgroup)
        elif method == 'class':
            rog_class = analysis_class(radius_of_gyration)
            return rog_class(atomgroup)
        elif method == 'custom':
            return RadiusOfGyrationCustom(atomgroup, **kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @classmethod
    def benchmark_methods(cls, atomgroup, methods=['function', 'class', 'custom']):
        """
        比较不同方法的性能
        """
        import time
        
        results = {}
        
        for method in methods:
            start_time = time.time()
            
            if method == 'custom':
                analyzer = cls.create_analysis(method, atomgroup=atomgroup, verbose=False)
            else:
                analyzer = cls.create_analysis(method, atomgroup=atomgroup)
            
            analyzer.run()
            end_time = time.time()
            
            results[method] = {
                'time': end_time - start_time,
                'results_shape': getattr(analyzer, 'results', getattr(analyzer, 'df', None)).shape if hasattr(analyzer, 'results') or hasattr(analyzer, 'df') else None
            }
        
        return results

def factory_example():
    """
    工厂模式使用示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 创建不同类型的分析器
    func_analyzer = RadiusOfGyrationFactory.create_analysis('function', atomgroup=protein)
    class_analyzer = RadiusOfGyrationFactory.create_analysis('class', atomgroup=protein)
    custom_analyzer = RadiusOfGyrationFactory.create_analysis('custom', atomgroup=protein, verbose=False)
    
    # 运行分析
    func_analyzer.run()
    class_analyzer.run()
    custom_analyzer.run()
    
    # 性能比较
    benchmark_results = RadiusOfGyrationFactory.benchmark_methods(protein)
    
    print("性能比较结果:")
    for method, stats in benchmark_results.items():
        print(f"  {method}: {stats['time']:.3f}s, shape: {stats['results_shape']}")
    
    return benchmark_results
```

### 设计模式2：装饰器增强

```python
def timing_decorator(func):
    """
    计时装饰器
    """
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.3f}s")
        return result
    return wrapper

def validation_decorator(func):
    """
    输入验证装饰器
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(atomgroup, *args, **kwargs):
        # 验证输入
        if len(atomgroup) == 0:
            raise ValueError("AtomGroup不能为空")
        
        if not hasattr(atomgroup, 'positions'):
            raise ValueError("AtomGroup必须有位置信息")
        
        return func(atomgroup, *args, **kwargs)
    return wrapper

@timing_decorator
@validation_decorator
def enhanced_radius_of_gyration(ag, masses=None, total_mass=None):
    """
    带装饰器增强的半径回转计算
    """
    if masses is None:
        masses = ag.masses
    if total_mass is None:
        total_mass = masses.sum()
    
    com = ag.center_of_mass()
    rg_squared = ((ag.positions - com)**2 * masses[:, np.newaxis]).sum(axis=0) / total_mass
    rg_total = np.sqrt(rg_squared.sum())
    
    return rg_total

def decorator_example():
    """
    装饰器使用示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 使用增强的函数
    result = enhanced_radius_of_gyration(protein)
    print(f"增强版半径回转: {result:.3f} Å")
    
    return result
```

### 设计模式3：配置驱动分析

```python
class ConfigurableAnalysis:
    """
    配置驱动的分析类
    """
    
    def __init__(self, config):
        """
        Parameters:
        -----------
        config : dict
            分析配置字典
        """
        self.config = config
        self.validate_config()
    
    def validate_config(self):
        """验证配置"""
        required_keys = ['atomgroup', 'analysis_type']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"缺少必需的配置项: {key}")
    
    def create_analysis(self):
        """根据配置创建分析实例"""
        analysis_type = self.config['analysis_type']
        atomgroup = self.config['atomgroup']
        
        if analysis_type == 'radius_of_gyration':
            method = self.config.get('method', 'function')
            
            if method == 'function':
                return AnalysisFromFunction(
                    radius_of_gyration,
                    atomgroup.universe.trajectory,
                    atomgroup,
                    **{k: v for k, v in self.config.items() 
                       if k not in ['atomgroup', 'analysis_type', 'method']}
                )
            elif method == 'class':
                rog_class = analysis_class(radius_of_gyration)
                return rog_class(atomgroup)
            elif method == 'custom':
                return RadiusOfGyrationCustom(
                    atomgroup,
                    verbose=self.config.get('verbose', False)
                )
        
        else:
            raise ValueError(f"未知的分析类型: {analysis_type}")
    
    def run_analysis(self):
        """运行分析"""
        analyzer = self.create_analysis()
        analyzer.run(**{k: v for k, v in self.config.items() 
                       if k in ['start', 'stop', 'step']})
        return analyzer

def configurable_analysis_example():
    """
    配置驱动分析示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 定义配置
    config = {
        'atomgroup': protein,
        'analysis_type': 'radius_of_gyration',
        'method': 'custom',
        'verbose': False,
        'start': 0,
        'stop': 20,
        'step': 2
    }
    
    # 创建并运行分析
    configurable = ConfigurableAnalysis(config)
    result = configurable.run_analysis()
    
    print(f"配置驱动分析完成，结果形状: {result.df.shape}")
    return result
```

## 性能优化技巧

### 技巧1：内存优化

```python
class MemoryOptimizedAnalysis(AnalysisBase):
    """
    内存优化的分析类
    """
    
    def __init__(self, atomgroup, chunk_size=1000, verbose=False):
        super().__init__(atomgroup.universe.trajectory, verbose=verbose)
        self.atomgroup = atomgroup
        self.chunk_size = chunk_size
    
    def _prepare(self):
        """预分配内存"""
        n_frames = len(self._trajectory)
        
        # 预分配结果数组
        self.results = np.empty((n_frames, 6))  # 假设6列结果
        self.valid_frames = np.zeros(n_frames, dtype=bool)
        
        # 预计算常量
        self.masses = self.atomgroup.masses
        self.total_mass = self.masses.sum()
    
    def _single_frame(self):
        """优化的单帧处理"""
        # 使用numpy操作而不是循环
        positions = self.atomgroup.positions
        masses = self.masses
        
        # 向量化计算
        com = np.average(positions, weights=masses, axis=0)
        centered_pos = positions - com
        
        # 一次性计算所有分量
        rg_squared_components = (centered_pos**2 * masses[:, np.newaxis]).sum(axis=0) / self.total_mass
        
        # 存储结果
        idx = self._frame_index
        self.results[idx, 0] = self._ts.frame
        self.results[idx, 1] = self._ts.time
        self.results[idx, 2] = np.sqrt(rg_squared_components.sum())  # 总半径回转
        self.results[idx, 3] = np.sqrt(rg_squared_components[1] + rg_squared_components[2])  # x
        self.results[idx, 4] = np.sqrt(rg_squared_components[0] + rg_squared_components[2])  # y
        self.results[idx, 5] = np.sqrt(rg_squared_components[0] + rg_squared_components[1])  # z
        
        self.valid_frames[idx] = True
    
    def _conclude(self):
        """整理结果"""
        # 只保留有效的帧
        valid_mask = self.valid_frames[:self.n_frames]
        self.results = self.results[:self.n_frames][valid_mask]

def memory_optimization_example():
    """
    内存优化示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 创建内存优化的分析器
    mem_opt = MemoryOptimizedAnalysis(protein, verbose=True)
    mem_opt.run()
    
    print(f"内存优化分析完成，结果形状: {mem_opt.results.shape}")
    return mem_opt
```

### 技巧2：并行处理

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

def parallel_analysis_chunks(atomgroup, n_processes=None):
    """
    并行处理分析的分块方法
    """
    if n_processes is None:
        n_processes = mp.cpu_count()
    
    # 获取轨迹信息
    total_frames = len(atomgroup.universe.trajectory)
    chunk_size = max(1, total_frames // n_processes)
    
    def process_chunk(args):
        """处理单个块"""
        start, stop, chunk_id = args
        u = atomgroup.universe
        
        results = []
        for i in range(start, min(stop, total_frames)):
            u.trajectory[i]  # 加载特定帧
            result = radius_of_gyration(atomgroup)
            results.append({
                'frame': i,
                'time': u.trajectory.time,
                'result': result
            })
        
        return chunk_id, results
    
    # 准备分块参数
    chunks = []
    for i, start in enumerate(range(0, total_frames, chunk_size)):
        stop = min(start + chunk_size, total_frames)
        chunks.append((start, stop, i))
    
    # 并行处理
    all_results = [None] * len(chunks)
    
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk): chunk_id 
                          for chunk, chunk_id in [(chunk, chunk[2]) for chunk in chunks]}
        
        for future in as_completed(future_to_chunk):
            chunk_id, results = future.result()
            all_results[chunk_id] = results
    
    # 合并结果
    final_results = []
    for chunk_results in all_results:
        if chunk_results:
            final_results.extend(chunk_results)
    
    return pd.DataFrame(final_results)

def parallel_processing_example():
    """
    并行处理示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 运行并行分析
    parallel_results = parallel_analysis_chunks(protein, n_processes=2)
    
    print(f"并行分析完成，处理了 {len(parallel_results)} 帧")
    print(f"平均半径回转: {parallel_results['result'].mean():.3f}")
    
    return parallel_results
```

### 技巧3：缓存优化

```python
from functools import lru_cache
import hashlib

class CachedAnalysis(AnalysisBase):
    """
    带缓存的分析类
    """
    
    def __init__(self, atomgroup, cache_enabled=True, verbose=False):
        super().__init__(atomgroup.universe.trajectory, verbose=verbose)
        self.atomgroup = atomgroup
        self.cache_enabled = cache_enabled
        self._cache = {}
    
    def _get_cache_key(self, positions, masses):
        """生成缓存键"""
        if not self.cache_enabled:
            return None
        
        # 创建基于位置和质量的哈希键
        pos_hash = hashlib.md5(positions.tobytes()).hexdigest()
        mass_hash = hashlib.md5(masses.tobytes()).hexdigest()
        return f"{pos_hash}_{mass_hash}"
    
    def _cached_radius_of_gyration(self, positions, masses, total_mass):
        """带缓存的半径回转计算"""
        cache_key = self._get_cache_key(positions, masses)
        
        if cache_key and cache_key in self._cache:
            return self._cache[cache_key]
        
        # 执行计算
        com = np.average(positions, weights=masses, axis=0)
        centered_pos = positions - com
        rg_squared = (centered_pos**2 * masses[:, np.newaxis]).sum(axis=0) / total_mass
        rg_total = np.sqrt(rg_squared.sum())
        
        result = {
            'total': rg_total,
            'x': np.sqrt(rg_squared[1] + rg_squared[2]),
            'y': np.sqrt(rg_squared[0] + rg_squared[2]),
            'z': np.sqrt(rg_squared[0] + rg_squared[1])
        }
        
        if cache_key:
            self._cache[cache_key] = result
        
        return result
    
    def _single_frame(self):
        """单帧分析"""
        positions = self.atomgroup.positions
        masses = self.masses
        
        result = self._cached_radius_of_gyration(positions, masses, self.total_mass)
        
        self.results.append({
            'frame': self._ts.frame,
            'time': self._ts.time,
            'rg_total': result['total'],
            'rg_x': result['x'],
            'rg_y': result['y'],
            'rg_z': result['z']
        })
    
    def _prepare(self):
        self.results = []
        self.masses = self.atomgroup.masses
        self.total_mass = self.masses.sum()
    
    def _conclude(self):
        self.df = pd.DataFrame(self.results)

def caching_example():
    """
    缓存优化示例
    """
    from MDAnalysis.tests.datafiles import PSF, DCD
    u = mda.Universe(PSF, DCD)
    protein = u.select_atoms('protein and name CA')
    
    # 创建带缓存的分析器
    cached_analysis = CachedAnalysis(protein, cache_enabled=True, verbose=True)
    cached_analysis.run()
    
    print(f"缓存分析完成，缓存大小: {len(cached_analysis._cache)}")
    print(f"结果形状: {cached_analysis.df.shape}")
    
    return cached_analysis
```

## 贡献代码到MDAnalysis

### 代码贡献流程

```python
def contribution_guidelines():
    """
    MDAnalysis代码贡献指南
    """
    guidelines = """
    ## 贡献自定义分析到MDAnalysis
    
    ### 1. 代码质量要求
    - 遵循PEP 8编码规范
    - 提供完整的文档字符串
    - 包含单元测试
    - 支持AnalysisBase基类
    
    ### 2. 文档要求
    - 清晰的API文档
    - 使用示例
    - 参数说明
    - 返回值描述
    
    ### 3. 测试要求
    - 边界条件测试
    - 性能基准测试
    - 与其他分析的一致性验证
    
    ### 4. 提交流程
    1. Fork MDAnalysis仓库
    2. 创建功能分支
    3. 实现功能并测试
    4. 提交Pull Request
    5. 代码审查和修改
    6. 合并到主分支
    """
    
    print(guidelines)

def example_contributable_class():
    """
    符合贡献标准的示例类
    """
    class RadiusOfGyrationContribution(AnalysisBase):
        """
        计算原子组的半径回转
        
        半径回转是衡量分子结构紧凑程度的参数，定义为：
        
        Rg² = Σ(m_i * |r_i - r_cm|²) / M
        
        其中 m_i 是原子i的质量，r_i 是位置，r_cm 是质心，M 是总质量。
        
        Parameters
        ----------
        atomgroup : AtomGroup
            要分析的原子组
        verbose : bool, optional
            是否显示进度条
            
        Attributes
        ----------
        results : numpy.ndarray
            分析结果数组，形状为(n_frames, n_properties)
        df : pandas.DataFrame
            结果的DataFrame格式
        average : dict
            各属性的平均值
            
        Examples
        --------
        >>> import MDAnalysis as mda
        >>> from MDAnalysisTests.datafiles import PSF, DCD
        >>> u = mda.Universe(PSF, DCD)
        >>> protein = u.select_atoms('protein and name CA')
        >>> rog = RadiusOfGyrationContribution(protein)
        >>> rog.run()
        >>> print(rog.results.shape)
        (98, 6)
        """
        
        def __init__(self, atomgroup, verbose=False):
            super().__init__(atomgroup.universe.trajectory, verbose=verbose)
            self.atomgroup = atomgroup
        
        def _prepare(self):
            """准备分析所需的数据结构"""
            self.masses = self.atomgroup.masses
            self.total_mass = self.masses.sum()
            self._results = []
        
        def _single_frame(self):
            """处理单个时间步"""
            positions = self.atomgroup.positions
            com = self.atomgroup.center_of_mass()
            
            # 计算半径回转
            dr = positions - com
            rg_squared = np.average(np.sum(dr**2, axis=1), weights=self.masses)
            rg_total = np.sqrt(rg_squared)
            
            # 各轴分量
            rg_components = np.sqrt(
                np.average(dr**2, weights=self.masses, axis=0)
            )
            
            self._results.append([
                self._ts.frame,
                self._ts.time,
                rg_total,
                rg_components[0],  # x
                rg_components[1],  # y
                rg_components[2]   # z
            ])
        
        def _conclude(self):
            """整理最终结果"""
            self.results = np.array(self._results)
            self.df = pd.DataFrame(
                self.results,
                columns=['Frame', 'Time', 'Rg_Total', 'Rg_X', 'Rg_Y', 'Rg_Z']
            )
            
            # 计算统计信息
            self.average = {
                'total': np.mean(self.results[:, 2]),
                'x': np.mean(self.results[:, 3]),
                'y': np.mean(self.results[:, 4]),
                'z': np.mean(self.results[:, 5])
            }
    
    return RadiusOfGyrationContribution
```

### 单元测试示例

```python
def create_unit_tests():
    """
    为自定义分析类创建单元测试
    """
    test_code = '''
import numpy as np
import pytest
import MDAnalysis as mda
from MDAnalysisTests.datafiles import PSF, DCD
from your_module import RadiusOfGyrationContribution

class TestRadiusOfGyrationContribution:
    """测试半径回转分析类"""
    
    @pytest.fixture
    def universe(self):
        """测试用的宇宙对象"""
        return mda.Universe(PSF, DCD)
    
    @pytest.fixture
    def protein(self, universe):
        """测试用的蛋白质原子组"""
        return universe.select_atoms('protein and name CA')
    
    def test_initialization(self, protein):
        """测试初始化"""
        analyzer = RadiusOfGyrationContribution(protein)
        assert analyzer.atomgroup == protein
        assert hasattr(analyzer, '_results')
    
    def test_run_analysis(self, protein):
        """测试分析运行"""
        analyzer = RadiusOfGyrationContribution(protein)
        analyzer.run(start=0, stop=5)
        
        assert analyzer.results.shape[0] == 5
        assert analyzer.results.shape[1] == 6
        assert isinstance(analyzer.df, pd.DataFrame)
    
    def test_results_validity(self, protein):
        """测试结果有效性"""
        analyzer = RadiusOfGyrationContribution(protein)
        analyzer.run(start=0, stop=1)
        
        results = analyzer.results[0]
        assert results[2] >= 0  # 总半径回转应为正
        assert all(r >= 0 for r in results[3:])  # 各分量应为正
    
    def test_empty_atomgroup_raises_error(self):
        """测试空原子组抛出错误"""
        with pytest.raises(ValueError):
            # 创建空的原子组
            empty_ag = mda.AtomGroup([], mda.Universe(PSF, DCD))
            RadiusOfGyrationContribution(empty_ag)
    
    def test_consistency_with_builtin(self, protein):
        """测试与内置方法的一致性"""
        # 比较自定义实现与内置实现的结果
        analyzer = RadiusOfGyrationContribution(protein)
        analyzer.run(start=0, stop=1)
        
        # 使用MDAnalysis内置方法验证
        expected = protein.radius_of_gyration()
        actual = analyzer.results[0, 2]  # 总半径回转
        
        np.testing.assert_allclose(actual, expected, rtol=1e-5)
'''
    
    print("单元测试模板:")
    print(test_code)
```

## 总结

本指南详细介绍了MDAnalysis中创建自定义轨迹分析的三种主要方法：

1. **AnalysisFromFunction**: 最简单的方法，适合快速原型开发
2. **analysis_class装饰器**: 将函数转换为可重用的类
3. **AnalysisBase继承**: 最灵活的方法，支持复杂分析逻辑

每种方法都有其适用场景，选择合适的方法取决于分析的复杂度和重用需求。通过遵循最佳实践和设计模式，可以创建高效、可维护的自定义分析代码。

记住，如果你开发了有用的分析方法，考虑将其贡献给MDAnalysis社区，这样可以帮助更多的研究人员！