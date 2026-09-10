# MDAnalysis Scripts Collection

本目录包含三个即用型分子动力学分析脚本，适用于常见的轨迹分析任务。每个脚本都提供 CLI 接口和详细文档，可作为独立工具使用或作为自定义分析的起点。

---

## 快速对比

| 脚本 | 分析维度 | 配置方式 | 输出 | 适用体系 |
|------|----------|----------|------|----------|
| [hb_distribution_analysis](./hb_distribution_analysis/) | 2D 密度 + 时间 ACF | YAML 文件 | PNG/PDF + NPZ/CSV | 任意分子体系 |
| [Plot_RDF](./Plot_RDF/) | 径向分布 (RDF) | 命令行参数 | CSV | 残基级结构分析 |
| [plot_orientation](./plot_orientation/) | Z-θ 取向分布 | 命令行参数 | PNG + NPZ/CSV | 界面/板状系统 |

---

## 脚本详情

### 1. 通用氢键分析 (`hb_distribution_analysis/`)

**功能：** 适用于任意分子体系的氢键分析，输出 XY 平面数密度图和生命周期自相关函数。

**特点：**
- ✅ YAML 配置驱动，无需修改代码
- ✅ 自动处理供体/受体选择
- ✅ 支持 50+ 帧的生命周期分析
- ✅ 出版级可视化（色盲友好配色）

**快速开始：**
```bash
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 50
```

**详细文档：** [hb_distribution_analysis/README.md](./hb_distribution_analysis/README.md)

---

### 2. 残基级 RDF 分析 (`Plot_RDF/`)

**功能：** 计算所有残基类型对的径向分布函数。

**特点：**
- ✅ 自动检测体系中的所有残基类型
- ✅ C 优化的距离计算
- ✅ 单个 CSV 文件包含所有残基对数据

**快速开始：**
```bash
python scripts/Plot_RDF/residue_rdf_all_pairs.py \
  --structure topol.tpr \
  --trajectory traj.xtc \
  --output rdf.csv
```

**详细文档：** [Plot_RDF/README.md](./Plot_RDF/README.md)

---

### 3. Z 分辨取向分析 (`plot_orientation/`)

**功能：** 分析水分子样分子沿 Z 轴的取向分布。

**特点：**
- ✅ 适用于界面或受限系统
- ✅ 可自定义分子定义（残基名、原子选择）
- ✅ 输出热图和剖面数据

**快速开始：**
```bash
python scripts/plot_orientation/water_orientation_z_analysis.py \
  --structure topol.tpr \
  --trajectory traj.trr
```

**详细文档：** [plot_orientation/README.md](./plot_orientation/README.md)

---

## 通用依赖

所有脚本共享以下核心依赖：

```bash
uv pip install MDAnalysis numpy matplotlib pandas pyyaml
# 或
pip install MDAnalysis numpy matplotlib pandas pyyaml
```

| 依赖 | 用途 |
|------|------|
| `MDAnalysis` | 轨迹读取，原子选择，分析功能 |
| `numpy` | 数值计算，数组操作 |
| `matplotlib` | 绘图和可视化 |
| `pandas` | CSV 数据导出 |
| `scipy` | FFT 自相关计算（氢键分析） |
| `pyyaml` | YAML 配置解析（氢键分析） |

---

## 选择合适的脚本

### 根据分析目标选择

| 目标 | 推荐脚本 |
|------|----------|
| 研究分子间氢键网络 | `hb_distribution_analysis/` |
| 分析残基级空间分布 | `Plot_RDF/` |
| 研究界面分子取向 | `plot_orientation/` |

### 根据体系特征选择

| 体系特征 | 推荐脚本 |
|----------|----------|
| 各向同性体相系统 | `hb_distribution_analysis/`, `Plot_RDF/` |
| 各向异性界面系统 | `plot_orientation/`, `hb_distribution_analysis/` |
| 受限/多孔系统 | `plot_orientation/`, `Plot_RDF/` |

---

## 常见工作流

### 工作流 1：共晶溶剂结构分析

```bash
# 1. 氢键网络分析
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 100 -c my_system.yaml

# 2. 残基间径向分布
python scripts/Plot_RDF/residue_rdf_all_pairs.py --structure md.tpr --trajectory md.xtc --output rdf.csv
```

### 工作流 2：电解质溶液界面研究

```bash
# 1. 界面取向分析
python scripts/plot_orientation/water_orientation_z_analysis.py \
  --structure md.tpr --trajectory md.trr --start 5000

# 2. 离子配对 RDF
python scripts/Plot_RDF/residue_rdf_all_pairs.py \
  --structure md.tpr --trajectory md.xtc \
  --resnames NA CL --output ions_rdf.csv
```

---

## 输出数据格式

### 图像文件
- **PNG**：快速预览和演示
- **PDF**：出版质量（`hb_distribution_analysis` 支持）

### 数据文件
- **CSV**：文本表格，可用 Excel/Python/R 处理
- **NPZ**：NumPy 压缩存档，包含多维数组

所有数据文件都包含清晰的列名或数组键，便于后续分析。

---

## 故障排除

### 问题：拓扑文件不兼容

**解决方案：** MDAnalysis 支持多种格式，确保使用兼容的拓扑/轨迹组合：
- GROMACS: `.tpr` + `.xtc/.trr`
- AMBER: `.prmtop` + `.nc`
- CHARMM: `.psf` + `.dcd`
- 通用: `.pdb` + `.xtc`

### 问题：内存不足

**解决方案：**
1. 使用帧切片：`--start`, `--stop`, `--step`
2. 减少分箱数：`--nbins` 或 `--n-bins`
3. 使用 `--last-frames` 仅分析轨迹末尾

### 问题：氢键分析帧数不足

**解决方案：** 生命周期分析需要 ≥50 帧才能获得有意义的 ACF 衰减：
```bash
python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 100
```

---

## 贡献与反馈

如需添加新脚本或改进现有脚本，请遵循以下原则：
1. 保持 CLI 接口一致性
2. 提供详细的 README 文档
3. 包含使用示例和输出说明
4. 使用现有的依赖包（避免引入新依赖）

---

## 相关资源

- **MDAnalysis 官方文档**: https://docs.mdanalysis.org
- **MDAnalysis 用户指南**: https://userguide.mdanalysis.org
- **本 Skill 主文档**: ../SKILL.md
- **参考文档目录**: ../references/
