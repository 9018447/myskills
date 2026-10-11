# Residue-Level RDF Analysis (All Pairs)

`residue_rdf_all_pairs.py` 计算轨迹中所有残基类型对的残基中心径向分布函数（RDF），并导出到单个 CSV 文件。适用于需要快速分析整个 MD 体系残基级结构的场景。

---

## 目录

- [快速开始](#快速开始)
- [命令行参数](#命令行参数)
- [输出文件说明](#输出文件说明)
- [算法说明](#算法说明)
- [使用场景](#使用场景)
- [依赖](#依赖)

---

## 快速开始

```bash
# 基本用法（自动检测所有残基类型）
python scripts/Plot_RDF/residue_rdf_all_pairs.py \
  --structure topol.tpr \
  --trajectory traj.xtc \
  --output rdf_all_pairs.csv

# 指定残基类型和帧范围
python scripts/Plot_RDF/residue_rdf_all_pairs.py \
  --structure topol.tpr \
  --trajectory traj.xtc \
  --output rdf_selected_pairs.csv \
  --resnames SOL NA CL \
  --nbins 300 \
  --rmax-nm 1.5 \
  --start 0 \
  --stop 1000 \
  --step 10
```

---

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--structure` | 拓扑文件路径（`.tpr`、`.gro`、`.pdb` 等） | **必填** |
| `--trajectory` | 轨迹文件路径（`.xtc`、`.trr`、`.dcd` 等） | **必填** |
| `--output` | 输出 CSV 文件路径 | **必填** |
| `--resnames` | 要分析的残基名列表（空格分隔） | `None`（自动检测所有残基） |
| `--nbins` | RDF 分箱数 | `200` |
| `--rmax-nm` | 最大距离（nm） | `None`（最短盒边的一半） |
| `--start` | 起始帧索引 | `0` |
| `--stop` | 结束帧索引（不包含） | `None`（全轨迹） |
| `--step` | 帧步长 | `1` |

---

## 输出文件说明

### CSV 文件结构

输出的 CSV 文件包含以下列：

| 列名 | 说明 |
|------|------|
| `r_nm` | RDF 径向距离中心（nm） |
| `rdf_<RES1>_<RES2>` | 残基对 `<RES1>`-`<RES2>` 的 RDF 值 |

### 示例输出

```csv
r_nm,rdf_SOL_SOL,rdf_SOL_NA,rdf_SOL_CL,rdf_NA_NA,rdf_NA_CL,rdf_CL_CL
0.0075,0.000,0.000,0.000,0.000,0.000,0.000
0.0225,0.984,1.342,1.521,0.832,0.765,0.698
0.0375,2.134,2.891,3.012,1.234,1.543,1.321
...
```

### RDF 归一化说明

- **同种残基对**（如 `SOL-SOL`）：使用理想气体归一化
- **异种残基对**（如 `SOL-NA`）：按体相平均密度归一化
- **极限行为**：当 r → ∞ 时，所有 RDF 趋向于 1.0

---

## 算法说明

### 残基中心计算

使用 MDAnalysis 的 `center_of_geometry(compound="residues")` 方法：

```python
residue_center = residue.atoms.center_of_geometry()
```

每个残基的中心是其所有原子的几何中心（质量未加权）。

### 距离计算

使用 `MDAnalysis.lib.distances` 的 **C 优化**距离计算函数：

- **异种残基**：`capped_distance(res1_centers, res2_centers, max_cutoff)`
- **同种残基**：`self_capped_distance(centers, max_cutoff)`（避免重复计算）

### RDF 计算公式

对于残基对类型 A-B：

$$g_{AB}(r) = \frac{V}{4\pi r^2 \Delta r \cdot N_A \cdot N_B} \cdot \langle n_{AB}(r) \rangle$$

其中：
- $V$：系统体积
- $\Delta r$：分箱宽度
- $N_A, N_B$：残基 A 和 B 的数量
- $n_{AB}(r)$：距离在 $[r, r+\Delta r]$ 范围内的 A-B 对数量

---

## 使用场景

### 适用场景

1. **混合溶剂分析**：研究不同溶剂组分之间的空间关联
2. **离子配对**：分析阳离子-阴离子径向分布
3. **溶质-溶剂相互作用**：研究溶质周围的溶剂结构
4. **快速体系概览**：无需预设残基类型，自动检测所有残基对

### 与氢键分析的区别

| 特性 | `Plot_RDF` | `hb_distribution_analysis` |
|------|-----------|----------------------------|
| 分析对象 | 残基中心距离 | 氢键几何判据 |
| 输出 | RDF 曲线 | 2D 密度图 + 生命周期 |
| 空间维度 | 径向（各向同性） | XY 平面（各向异性） |
| 定量信息 | 配位数、接触距离 | 氢键数目、持续时间 |

---

## 依赖

| 包 | 用途 |
|---|---|
| `MDAnalysis` | 轨迹读取，残基选择，距离计算 |
| `numpy` | 数值计算，直方图统计 |
| `pandas` | CSV 数据导出 |

安装：
```bash
uv pip install MDAnalysis pandas
# 或
pip install MDAnalysis pandas
```

---

## 常见问题

### Q: 如何确定 `--rmax-nm`？

A: 对于立方盒子，使用盒边长的一半；对于非正交盒子，脚本会自动使用第一帧最短盒边的一半作为默认值。

### Q: 为什么某些残基对的 RDF 在短距离处为零？

A: 可能原因：
1. **位阻效应**：残基体积较大，中心无法过于接近
2. **拓扑约束**：共价键限制了残基间最小距离
3. **截断距离不足**：`--rmax-nm` 设置过小，未覆盖第一配位峰

### Q: 如何提高 RDF 分辨率？

A: 增大 `--nbins` 值，但注意：
- 分箱过细会增加统计噪声
- 建议同时增加分析帧数（`--start`、`--stop`、`--step`）
- 常用值：`--nbins 200` 到 `--nbins 500`

---

## 示例：电解质溶液分析

分析 NaCl 水溶液中各组分间的径向分布：

```bash
python scripts/Plot_RDF/residue_rdf_all_pairs.py \
  --structure nacl_water.tpr \
  --trajectory nacl_water.xtc \
  --output nacl_rdf.csv \
  --resnames SOL NA CL \
  --nbins 300 \
  --rmax-nm 1.0 \
  --stop 5000
```

**预期结果：**
- `rdf_SOL_SOL`：~0.3 nm 处的水-氢键峰
- `rdf_NA_CL`：~0.25 nm 处的接触离子对峰
- `rdf_NA_SOL`：~0.24 nm 处的 Na-O 配位峰
