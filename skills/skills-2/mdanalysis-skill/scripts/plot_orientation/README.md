# Z-Resolved Water Orientation Analysis

`water_orientation_z_analysis.py` 分析水分子样分子相对于模拟 Z 轴的取向分布，适用于界面或板状系统，其中取向随 Z 坐标变化。

---

## 目录

- [快速开始](#快速开始)
- [命令行参数](#命令行参数)
- [取向定义](#取向定义)
- [输出文件说明](#输出文件说明)
- [使用场景](#使用场景)
- [算法说明](#算法说明)
- [依赖](#依赖)

---

## 快速开始

```bash
# 基本用法（使用默认水分子选择）
python scripts/plot_orientation/water_orientation_z_analysis.py \
  --structure topol.tpr \
  --trajectory traj.trr

# 自定义分子定义
python scripts/plot_orientation/water_orientation_z_analysis.py \
  --structure topol.tpr \
  --trajectory traj.trr \
  --water-resname SOL \
  --oxygen-selection "name OW" \
  --hydrogen-selection "name HW1 HW2" \
  --output-prefix sol_orientation \
  --z-bins 120 \
  --theta-bins 120 \
  --start 100 \
  --stop 2000 \
  --step 5

# 仅输出数据，跳过绘图
python scripts/plot_orientation/water_orientation_z_analysis.py \
  --structure topol.tpr \
  --trajectory traj.trr \
  --no-plots
```

---

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--structure` | 拓扑文件路径（`.tpr`、`.gro`、`.pdb` 等） | **必填** |
| `--trajectory` | 轨迹文件路径（`.xtc`、`.trr`、`.dcd` 等） | **必填** |
| `--water-resname` | 目标分子的残基名 | `SOL` |
| `--oxygen-selection` | 氧原子的 MDAnalysis 选择字符串 | `name OW` |
| `--hydrogen-selection` | 氢原子的 MDAnalysis 选择字符串 | `name HW1 HW2` |
| `--output-prefix` | 输出文件前缀 | `water_orientation_z` |
| `--z-bins` | Z 方向分箱数 | `100` |
| `--theta-bins` | θ 角度分箱数 | `90` |
| `--start` | 起始帧索引 | `0` |
| `--stop` | 结束帧索引（不包含） | `None`（全轨迹） |
| `--step` | 帧步长 | `1` |
| `--no-plots` | 跳过绘图，仅输出数据 | `False` |

---

## 取向定义

取向向量定义为：**从氧原子指向两个氢原子中点**的向量。

对于每个残基，脚本：
1. 选择恰好 **1 个氧原子** 和 **2 个氢原子**
2. 计算氢原子中点：`midpoint = (H1 + H2) / 2`
3. 计算取向向量：`orientation = midpoint - oxygen`
4. 计算取向向量与 Z 轴的夹角：`θ = arccos(orientation · z_axis / |orientation|)`

**坐标系约定：**
- `cos(θ) = 1`：取向向量与 +Z 轴平行（指向上方）
- `cos(θ) = -1`：取向向量与 -Z 轴平行（指向下方）
- `cos(θ) = 0`：取向向量与 XY 平面平行

---

## 输出文件说明

对于输出前缀 `water_orientation_z`，脚本生成以下文件：

| 文件 | 内容 |
|------|------|
| `water_orientation_z_profile.dat` | Z 分辨的 cos(θ)、θ 和数密度剖面 |
| `water_orientation_z_hist2d.dat` | Z-θ 二维分布的扁平化表格 |
| `water_orientation_z_raw.npz` | NumPy 压缩存档，包含所有计算数组 |
| `water_orientation_z_heatmap.png` | Z-θ 热图 |
| `water_orientation_z_profile.png` | Z 分辨剖面图 |

### `*_profile.dat` 结构

```
# z_center(nm)  mean_cos_theta  mean_theta(deg)  number_density(nm^-3)
0.000          0.012           89.3             0.033
0.050          0.034           88.0             0.032
...
```

### `*_raw.npz` 包含的数组

```
z_centers      # Z 坐标中心 (nm)
theta_centers  # θ 角度中心 (度)
hist2d         # Z-θ 二维直方图
cos_theta_mean # 每个 Z bin 的平均 cos(θ)
theta_mean     # 每个 Z bin 的平均 θ (度)
number_density # 每个 Z bin 的数密度 (nm⁻³)
```

---

## 使用场景

### 适用场景

1. **界面系统**：液-液界面、液-气界面、固-液界面
2. **受限系统**：孔隙、狭缝、层状结构
3. **表面吸附**：分子在表面附近的取向重组
4. **膜系统**：跨膜水分子取向分布

### 与其他脚本的区别

| 特性 | `plot_orientation` | `hb_distribution_analysis` |
|------|-------------------|----------------------------|
| 分析维度 | Z-θ 二维分布 | XY 平面密度分布 |
| 输出 | 热图 + 剖面数据 | 密度图 + 生命周期 ACF |
| 配置方式 | 命令行参数 | YAML 配置文件 |
| 适用系统 | 各向异性系统（界面/板状） | 各向同性系统（体相） |

---

## 算法说明

### 残基筛选逻辑

1. **氧原子选择**：在指定 `resname` 内执行 `oxygen_selection`
2. **氢原子选择**：在同一残基内执行 `hydrogen_selection`
3. **有效残基判定**：恰好 1 个氧原子 且 恰好 2 个氢原子
4. **无效残基跳过**：不满足上述条件的残基被静默跳过

### 分箱统计

对于每个有效残基：
1. 根据 Z 坐标确定 Z bin 索引
2. 根据夹角 θ 确定 θ bin 索引
3. 在二维直方图中累加计数

**归一化**：
- `hist2d`：原始计数（未归一化）
- `number_density`：按 Z bin 体积归一化

---

## 依赖

| 包 | 用途 |
|---|---|
| `MDAnalysis` | 轨迹读取，原子选择 |
| `numpy` | 数值计算，数组操作 |
| `matplotlib` | 绘图（热图、剖面图） |
| `pandas` | CSV 数据导出 |

安装：
```bash
uv pip install MDAnalysis matplotlib pandas
# 或
pip install MDAnalysis matplotlib pandas
```

---

## 示例输出解释

### 典型界面系统特征

在液-气界面附近：
- Z < 界面位置：`cos(θ) ≈ 0`（分子平行于界面）
- Z ≈ 界面位置：`cos(θ)` 逐渐趋向 -1（氧指向气相）
- Z > 界面位置：体相行为（`cos(θ) ≈ 0`，无净取向）

### 板状受限系统

在两个疏水表面之间：
- 靠近表面：`cos(θ) ≈ 1` 或 `-1`（氧指向或背向表面）
- 中心区域：`cos(θ) ≈ 0`（随机取向）
