# hb_distribution_analysis — 通用氢键分析包

适用于任意分子动力学体系的氢键分析工具，输出两类核心结果：
- **XY 平面氢键数密度图**（空间分布热图）
- **氢键生命周期自相关函数**（ACF 衰减曲线）

通过修改一个 YAML 配置文件即可适配不同体系，**无需修改 Python 代码**。

---

## 目录

- [快速开始](#快速开始)
- [命令行参数](#命令行参数)
- [配置文件 system.yaml](#配置文件-systemyaml)
- [适配新体系示例](#适配新体系示例)
- [Python API](#python-api)
- [输出文件说明](#输出文件说明)
- [算法说明](#算法说明)
- [包结构](#包结构)
- [依赖](#依赖)

---

## 快速开始

```bash
# 在 skill 根目录运行
cd /path/to/your/simulation

# 分析末尾 50 帧（推荐最少 50 帧以得到有意义的生命周期）
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 50

# 快速测试（10 帧，跳过图片和数据导出）
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 10 --no-plots --no-data

# 用自定义体系配置
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -c my_system.yaml -n 100
```

---

## 命令行参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `-t, --topology` | 拓扑文件（`.tpr`、`.gro`、`.pdb` 等） | **必填** |
| `-r, --trajectory` | 轨迹文件（`.xtc`、`.trr`、`.dcd` 等） | **必填** |
| `-c, --config` | 体系配置 YAML 文件路径 | 内置 ChCl:EG 配置 |
| `-d, --distance` | D-A 截断距离（Å），覆盖 YAML 值 | YAML 中设定（3.5） |
| `-a, --angle` | D-H-A 最小角度（°），覆盖 YAML 值 | YAML 中设定（120） |
| `-n, --last-frames` | 只分析末尾 N 帧 | 全轨迹 |
| `-o, --output` | 输出目录，覆盖 YAML 值 | YAML 中的 `output_dir` |
| `--no-plots` | 跳过绘图 | False |
| `--no-data` | 跳过数据导出 | False |
| `-v, --verbose` | 输出详细配置信息 | False |

**参数优先级**：命令行 `-d/-a/-o` > YAML 配置 > 内置默认值

---

## 配置文件 system.yaml

`system.yaml` 是适配不同体系的**唯一需要修改的文件**。

```yaml
system_name: "ChCl:EG Eutectic Solvent (1:2 molar ratio)"

groups:
  - name: "Choline"            # 显示名称（出现在图例和交互类型标签中）
    resname: "Cho"             # MDAnalysis resname；多个写列表: ["Cho", "Cho2"]
    can_donate: true           # 是否有 O-H/N-H 供体
    donor_heavy_sel: "name O*" # 供体重原子选择（在本组 resname 内）
    can_accept: true           # 是否可作为受体
    acceptor_sel: "name O*"    # 受体原子选择

  - name: "Chloride"
    resname: "Chl"
    can_donate: false
    can_accept: true
    acceptor_sel: "name CL*"

  - name: "EthyleneGlycol"
    resname: "Eth"
    can_donate: true
    donor_heavy_sel: "name O*"
    can_accept: true
    acceptor_sel: "name O*"

hydrogens_sel: "name H*"   # 全局 H 原子选择（通常无需修改）
distance_cutoff: 3.5       # D-A 最大距离（Å）
angle_cutoff: 120          # D-H-A 最小角度（°）
output_dir: "hb_analysis_output"
n_bins: 100                # 2D 密度图格点数
dpi: 300                   # 图片分辨率
```

> [!NOTE]
> `resname` 支持单个字符串或列表；`donor_heavy_sel` / `acceptor_sel` 是 MDAnalysis 选择语法（仅在本组 resname 内生效）。

**Interaction Types 自动生成规则**：
所有 `can_donate=true` 的组 × 所有 `can_accept=true` 的组 = 交叉枚举。
例如上述配置自动产生：
- Choline-Choline, Choline-Chloride, Choline-EthyleneGlycol
- EthyleneGlycol-Choline, EthyleneGlycol-Chloride, EthyleneGlycol-EthyleneGlycol

---

## 适配新体系示例

### 示例 1：咪唑类离子液体 [BMIM][PF₆]

```yaml
system_name: "BMIM-PF6 Ionic Liquid"

groups:
  - name: "BMIM"
    resname: "BMIM"
    can_donate: true
    donor_heavy_sel: "name N*"   # 咪唑环 C2-H，此处以 N 为重原子近似
    can_accept: false

  - name: "PF6"
    resname: "PF6"
    can_donate: false
    can_accept: true
    acceptor_sel: "name F*"

hydrogens_sel: "name H*"
distance_cutoff: 3.5
angle_cutoff: 120
```

### 示例 2：含蛋白质的水溶液

```yaml
system_name: "Protein in Water"

groups:
  - name: "Water"
    resname: "SOL"
    can_donate: true
    donor_heavy_sel: "name OW"
    can_accept: true
    acceptor_sel: "name OW"

  - name: "Protein"
    resname: ["LYS", "SER", "THR", "TYR", "ASN", "GLN"]  # 多个残基
    can_donate: true
    donor_heavy_sel: "name N* O*"
    can_accept: true
    acceptor_sel: "name N* O*"

hydrogens_sel: "name H*"
distance_cutoff: 3.5
angle_cutoff: 120
```

### 示例 3：深共晶溶剂（ChCl + 尿素）

```yaml
system_name: "ChCl:Urea DES"

groups:
  - name: "Choline"
    resname: "Cho"
    can_donate: true
    donor_heavy_sel: "name O*"
    can_accept: true
    acceptor_sel: "name O*"

  - name: "Chloride"
    resname: "Chl"
    can_donate: false
    can_accept: true
    acceptor_sel: "name CL*"

  - name: "Urea"
    resname: "URE"
    can_donate: true
    donor_heavy_sel: "name N*"   # N-H 供体
    can_accept: true
    acceptor_sel: "name O*"      # C=O 受体
```

---

## Python API

### 最简使用

```python
from scripts.hb_distribution_analysis import HBAnalyzer, run_analysis

analyzer = HBAnalyzer("md.tpr", "md.xtc")
run_analysis(analyzer, last_frames=100)
```

### 从外部 YAML 加载配置

```python
from scripts.hb_distribution_analysis import HBAnalyzer, load_config, run_analysis

config = load_config("my_system.yaml")
analyzer = HBAnalyzer("md.tpr", "md.xtc", config=config)
run_analysis(analyzer, last_frames=200, output_dir="results/")
```

### 分步调用（精细控制）

```python
from scripts.hb_distribution_analysis import HBAnalyzer, load_config
from scripts.hb_distribution_analysis.calculators import calculate_hydrogen_bonds, calculate_lifetime_by_type
from scripts.hb_distribution_analysis.analyzers import create_2d_density_map
from scripts.hb_distribution_analysis.visualization import plot_2d_density_maps, plot_lifetime_autocorr
from scripts.hb_distribution_analysis.exporters import save_density_maps, save_lifetime_data

config = load_config("system.yaml")
analyzer = HBAnalyzer("md.tpr", "md.xtc", config=config)

# 1. 计算氢键（只分析末尾 100 帧）
hba = calculate_hydrogen_bonds(analyzer, last_frames=100)

# 2. 生命周期 ACF
calculate_lifetime_by_type(hba, analyzer)

# 3. 2D 密度图
create_2d_density_map(analyzer, n_bins=200)

# 4. 单独绘图
plot_2d_density_maps(analyzer, output_dir="figs/")
plot_lifetime_autocorr(analyzer, output_dir="figs/")

# 5. 单独导出
save_density_maps(analyzer, output_dir="data/")
save_lifetime_data(analyzer, output_dir="data/")

# 6. 复用密度图数据（NumPy 格式）
import numpy as np
d = np.load("data/hb_density_maps.npz")
print(d.files)   # 查看所有 key
density = d["Choline_Chloride_density"]  # 取某一类型
```

---

## 输出文件说明

```
hb_analysis_output/
├── hb_2d_density_maps.png    # XY 平面氢键数密度热图（各分子对）
├── hb_lifetime_autocorr.png  # 生命周期自相关函数 C(τ) 衰减曲线
├── hb_density_maps.npz       # 密度矩阵数据（NumPy 压缩格式）
└── hb_lifetime_data.csv      # ACF 数据表（tau_ps 列 + 各交互类型列）
```

#### `hb_density_maps.npz` 的结构

每种交互类型存储三个数组（以 `_` 替换 `-`）：
```
Choline_Chloride_density   → shape (n_bins, n_bins)，单位 Å⁻²
Choline_Chloride_x_edges   → X 轴边界坐标（Å），length n_bins+1
Choline_Chloride_y_edges   → Y 轴边界坐标（Å），length n_bins+1
```

#### `hb_lifetime_data.csv` 的结构

| tau_ps | Choline-Choline | Choline-Chloride | ... |
|---|---|---|---|
| 0.0 | 1.000000 | 1.000000 | ... |
| 10.0 | 0.823451 | 0.912301 | ... |

---

## 算法说明

### 氢键检测

使用 MDAnalysis `HydrogenBondAnalysis`，采用 D-H···A 几何判据：
- **距离**：D-A 间距 ≤ `distance_cutoff`（默认 3.5 Å）
- **角度**：D-H-A 角度 ≥ `angle_cutoff`（默认 120°）

选择字符串由 `system.yaml` 自动生成，无需手动编写。

### 生命周期自相关函数

采用**连续时间自相关函数（Continuous ACF）**：

$$C(\tau) = \frac{\sum_p \sum_t h_p(t) \cdot h_p(t+\tau)}{\sum_p \sum_t h_p(t) \cdot h_p(t)}$$

其中 $h_p(t)$ 为分子对 $p$ 在帧 $t$ 是否形成氢键（0 或 1）。

**性能优化**：
1. 预读取所有原子属性为 numpy 数组（消除 MDAnalysis 热循环 API 调用）
2. 使用 `scipy.signal.fftconvolve` 计算 ACF（O(n log n)，替代 O(n²) 双循环）

> [!IMPORTANT]
> 生命周期分析建议帧数 ≥ 50（即 `-n 50`），帧数太少 ACF 无法完整衰减到 1/e。

---

## 包结构

```
scripts/hb_distribution_analysis/
├── system.yaml       ← 体系配置文件（用户主要修改此文件）
├── __init__.py       # 公开 API，run_analysis 便捷入口
├── __main__.py       # 允许 python -m scripts.hb_distribution_analysis 调用
├── config.py         # SystemConfig dataclass，load_config()
├── core.py           # HBAnalyzer 分析器类
├── calculators.py    # 氢键检测 + 生命周期 ACF 计算
├── analyzers.py      # 2D 密度图构建
├── visualization.py  # 绘图函数
├── exporters.py      # NPZ + CSV 数据导出
└── main.py           # 命令行入口（argparse）
```

---

## 依赖

| 包 | 用途 |
|---|---|
| `MDAnalysis` | 轨迹读取，氢键检测 |
| `numpy` | 数值计算 |
| `scipy` | FFT 自相关（`fftconvolve`） |
| `matplotlib` | 绘图 |
| `pandas` | CSV 导出 |
| `pyyaml` | YAML 配置文件解析 |

安装：
```bash
uv pip install MDAnalysis scipy matplotlib pandas pyyaml
# 或
pip install MDAnalysis scipy matplotlib pandas pyyaml
```
