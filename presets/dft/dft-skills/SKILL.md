---
name: dft-skills
description: |
  Gaussian 16 小分子 DFT 计算全流程技能，覆盖前处理、输入文件生成、后处理分析和可视化渲染。
  当用户提到以下任何内容时触发此技能（即使没有明确说"DFT"或"Gaussian"）：
  - 分子结构优化、频率计算、DFT 计算、量子化学计算
  - obabel 格式转换、smiles 转 xyz/sdf
  - xtb 预优化、半经验优化
  - genmer/molclus 构象搜索、团簇构象、团簇优化
  - Gaussian 输入文件（.gjf）生成
  - ESP、IGMH、AIM、NCI、NBO 分析
  - Multiwfn 波函数分析
  - formchk 格式转换
  - cube 文件生成与渲染（xyzrender）
  - VMD 可视化脚本
  - 分子结合能、BSSE/Counterpoise 校正
  - 弥散函数、色散校正(D3BJ)
---

# DFT Skills — Gaussian 16 小分子计算全流程

本技能引导用户完成从分子结构准备到最终可视化的完整 DFT 计算流程。
以交互方式逐步确认每个步骤，而非一次性执行全部操作。

## 工具路径

本技能依赖以下工具链，其中部分为不开源的本地程序，通过绝对路径调用：

| 工具 | 调用方式 | 说明 |
|------|----------|------|
| obabel | `which obabel` | 系统PATH，格式转换 |
| xtb | `which xtb` | 系统PATH，半经验预优化 |
| formchk | `which formchk` | 系统PATH，Gaussian chk 转换 |
| Multiwfn | `which Multiwfn` | 系统PATH，波函数分析 |
| xyzrender | `which xyzrender` | 系统PATH，cube 渲染 |

### 环境检查

```bash
which obabel xtb formchk Multiwfn xyzrender 2>/dev/null
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS:-未设置}"
```

记录哪些工具可用，后续步骤仅推荐可行的路径。如果关键工具缺失，告知用户并建议安装。

## 交互流程

### 第一步：确认用户目标

向用户展示可用的工作模块，询问本次需要做什么：

1. **前处理** — 格式转换 + 结构预优化
2. **团簇构象搜索** — genmer/molclus 自动化构象搜索
3. **Gaussian 输入文件** — 生成 .gjf 计算输入
4. **后处理** — chk 转换 + Multiwfn 分析（ESP/IGMH/AIM/NCI）
5. **可视化** — xyzrender 渲染或 VMD 脚本生成
6. **完整流程** — 从头到尾全部执行

用户可能只需要其中一部分，不要假设需要完整流程。

### 第二步：根据目标引导

根据用户选择，进入对应子流程。每个子流程在开始前确认输入文件路径和关键参数。

---

## 默认工作流（用户未指定时）

如果用户只是说"帮我处理这个分子"或"优化一下这个结构"，不指定具体步骤，按以下默认流程执行：

### 单分子工作流

```
1. obabel 格式转换 → 获取分子 XYZ
2. 为分子创建独立工作目录（防止 xtb 输出覆盖）
3. xtb GFN2 预优化 + 频率计算
4. 提取 xtb 优化结构，生成 B3LYP/6-311G(d,p) Opt Freq .gjf
```

**关键：每个分子使用独立工作目录**
```bash
# 正确做法：为每个分子创建独立目录
mkdir -p "molecule_name/xtb_optimization"
cd "molecule_name/xtb_optimization"
xtb "../../input.xyz" --gfn 2 --ohess --chrg 0

# 错误做法：在同一目录对多个分子运行 xtb
# → xtb_output 文件会被覆盖！
cd /same/directory
xtb molecule1.xyz --gfn 2 --ohess  # → 覆盖
xtb molecule2.xyz --gfn 2 --ohess  # → 覆盖
```

**xtb 输出文件名说明**：xtb 会在当前目录生成 `xtb_output.xxx` 系列文件（结构、频率等），同一目录下只能存放一个分子的结果。

### 团簇构象搜索工作流

对于团簇体系，使用 genmer/molclus 进行构象搜索：

```
1. 准备各单体的 xyz 文件
2. 使用 cluster_search_step1.sh 自动化构象搜索
3. 脚本自动生成最优构象的 .gjf 文件
```

**脚本调用示例**：
```bash
./cluster_search_step1.sh 2 "water.xyz:3" "methane.xyz:2" 0 cluster_opt
```

---

## 模块一：前处理

### 1.1 格式转换（obabel）

确认输入文件格式和目标格式，然后执行转换。

```bash
obabel -i<输入格式> <输入文件> -o<输出格式> -O<输出文件> -3d
```

常见转换：
| 输入 | 输出 | 命令示例 |
|------|------|----------|
| SMILES | XYZ | `obabel -:'CC(=O)O' -oxyz -Ooutput.xyz -3d` |
| SDF | XYZ | `obabel -isdf input.sdf -oxyz -Ooutput.xyz -3d` |
| XYZ | SDF | `obabel -ixyz input.xyz -osdf -Ooutput.sdf` |

### 1.2 预优化（xtb）

**每个分子使用独立工作目录** — xtb 在当前目录生成 `xtb_output.xxx` 文件，多个分子在同一目录会导致覆盖。

操作流程：
1. 为分子创建独立目录（如 `molecule_name/xtb_optimization/`）
2. 进入该目录执行 xtb，或使用绝对路径指定输入文件

```bash
# 目录结构示例
project/
├── molecule_A/
│   └── xtb_optimization/     # xtb 输出在这里
│       ├── xtb_output.xyz    # 优化后的结构
│       └── xtb_output.hess   # 频率数据
└── molecule_B/
    └── xtb_optimization/     # 独立目录，不与 A 混淆
```

执行命令：
```bash
cd "molecule_name/xtb_optimization"
xtb "../../input.xyz" --gfn 2 --ohess [--chrg <电荷>]
```

- `--gfn 2`：GFN2-xTB 方法（推荐）
- `--ohess`：优化 + Hessian（频率）
- `--chrg`：分子电荷（默认 0）
- 产出：优化后的结构文件 `xtb_output.xyz` 和频率数据 `xtb_output.hess`

## 模块二：Gaussian 输入文件生成

读取 `references/gaussian-templates.md` 获取完整模板。

### 团簇构象搜索（genmer/molclus）

对于团簇体系，需要先生成低能构象。使用 `references/cluster_search_step1.sh` 脚本自动化构象搜索全流程。

**脚本功能**：
1. 转换 .fchk 文件为 .xyz 格式（Multiwfn）
2. 配置并运行 genmer 生成初始团簇构象
3. 配置并运行 molclus 进行构象优化和筛选
4. 运行 isostat 进行异构体统计分析
5. 使用 Multiwfn 生成最终 Gaussian 输入文件（.gjf）

**用法**：
```bash
./cluster_search_step1.sh <分子种类数> "<分子1_xyz:数量>" "<分子2_xyz:数量>" ... <总电荷> <输出文件名>
```

**参数说明**：
- 分子种类数：正整数（1-10），表示有多少种不同的分子
- 分子xyz:数量：格式为 "文件名:数量"，例如 "water.xyz:3"
- 总电荷：整数，例如 0, 1, -1, 2, -2
- 输出文件名：Gaussian 输入文件名（不含扩展名）

**示例**：
```bash
# 两种分子：3个水分子和2个甲烷分子，总电荷0，输出文件名为 cluster_opt
./cluster_search_step1.sh 2 "water.xyz:3" "methane.xyz:2" 0 cluster_opt

# 单种分子：5个苯分子，总电荷-1，输出文件名为 benzene_cluster
./cluster_search_step1.sh 1 "benzene.xyz:5" -1 benzene_cluster
```

**产出文件**：
- `results/cluster.xyz` — 最优团簇构象
- `results/isomers.xyz` — 异构体集合
- `<输出文件名>.gjf` — Gaussian 输入文件（复制回原目录）

**依赖工具**：
- genmer — 团簇初始构象生成
- molclus — 构象优化和筛选
- isostat — 异构体统计分析
- Multiwfn — 格式转换和 .gjf 生成

**注意**：
- 脚本为完全非交互模式，适合批处理和自动化流程
- genmer 运行时自动输入回车继续
- 中间文件自动清理，仅保留最终结果

### 单分子/简单体系 .gjf 生成

对于非团簇体系或已知构象的分子，直接生成 .gjf 文件。

#### 交互参数收集

生成 .gjf 前确认：
1. **计算类型**：中性分子优化/阴离子优化/团簇结合能/NBO
2. **分子电荷和自旋多重度**（默认 0 1）
3. **分子几何**来源：从 XYZ 文件提取或用户直接提供
4. **文件名**：用于 %chk 和输出命名
5. **计算资源**：内存（默认 20GB）、核心数（默认 16）

#### 模板选择逻辑

- 中性分子 → `B3LYP/6-311G(d,p) Opt Freq EmpiricalDispersion=GD3BJ`
- 阴离子 → `B3LYP/6-311+G(d,p) Opt Freq EmpiricalDispersion=GD3BJ`（加弥散函数）
- 团簇结合能 → 加 `counterpoise=2`，每个原子后加片段编号
- NBO → 从已有 chk 读取几何，使用 `geom=check Guess=Read pop=nboread`

#### 几何坐标提取

从 XYZ 文件提取坐标写入 .gjf：

```bash
# 读取 xyz 文件的坐标部分（跳过前两行），转为 Gaussian 格式
# 需要将元素符号 + xyz 坐标写入 .gjf 的 [GEOMETRY] 位置
```

---

## 模块三：后处理

### 3.1 chk 转换

```bash
formchk <filename>.chk
```

产出 `<filename>.fchk`。

### 3.2 Multiwfn 分析

**Multiwfn 需要预先准备固定的参数文件**，每个分析类型对应一个 txt 文件，执行时通过重定向输入。

```
Multiwfn <fchk文件> < <分析类型>.txt
```

分析前准备：

1. **fchk 文件路径**（必须是包含频率分析的 fchk）
2. **分析类型**：ESP / IGMH / AIM / NCI
3. **线程设置**：`export OMP_NUM_THREADS=12` 和 `export MKL_NUM_THREADS=12`
4. **写入参数文件**（每次分析前先写入文件）

#### ESP 分析

**已有封装好的脚本 `scripts/drawesp.sh`**

*.fchk -> *ESP.svg

直接使用bash运行

---
脚本原理：
Multiwfn 产出 `totesp.cub` 和 `density.cub`（.cub 后缀）。
**xyzrender 需要 .cube 后缀**，渲染前需重命名：

```bash
Multiwfn molecule.fchk < ESP.txt
mv totesp.cub ESP.cube
mv density.cub DENSITY.cube
xyzrender DENSITY.cube --esp ESP.cube --iso 0.005 --opacity 0.75 -o esp.svg
```
---

#### IGMH 分析

准备 `IGMH.txt`，**片段原子序号是关键参数**，必须与用户确认：
```bash
Multiwfn molecule.fchk < IGMH.txt
```
产出 `sl2r.cub`、`dg.cub`、`dg_inter.cub`、`dg_intra.cub`。

#### AIM 分析

准备 `AIM.txt`，然后执行：
```bash
Multiwfn molecule.fchk < AIM.txt
```
产出 `CPs.pdb`、`paths.pdb`、`mol.pdb`。
可自动移动到 VMD 目录：
```bash
mv -f *.pdb "/media/smh/d/vmd-2.0.0a7"
```

#### NCI 分析
已经有封装好的bash脚本

`scripts/drawnci.sh`

直接运行

---

准备 `NCI.txt`，然后执行：
```bash
Multiwfn molecule.fchk < NCI.txt
```
产出 `func1.cub`（sign(lambda2)*rho）和 `func2.cub`（RDG）。

**参数文件见 `references/multiwfn-analysis.md`**

---

### 3.3 格式转换

| 转换方向 | Multiwfn 输入文件 | 说明 |
|----------|-------------------|------|
| xyz/fchk → gjf | `xyz2gjf.txt` | 需要当前目录有 template.gjf |
| gjf/fchk → xyz | `tranxyz.txt` | — |

使用 template.gjf 模板时，`[GEOMETRY]` 行会被替换为当前坐标。
`scripts/` 目录下的 `run_multiwfn.sh` 脚本封装了上述分析流程，用户只需指定 fchk 文件和分析类型即可批量处理。
目录如下：
  - ESP.txt
  - AIM.txt
  - NCI.txt
  - xyz2gjf.txt（10 后两个空行）
  - tranxyz.txt（2 后一个空行）
  - run_multiwfn.sh（批处理脚本）
```bash
  run_multiwfn.sh 通过 cat <file> | Multiwfn 以管道方式传入输入，并统一设置了
  OMP_NUM_THREADS=12 和 MKL_NUM_THREADS=12。

  用法示例：

  ./run_multiwfn.sh input.fchk esp
  ./run_multiwfn.sh input.fchk aim
  ./run_multiwfn.sh input.fchk nci
  ./run_multiwfn.sh input.fchk igmh 1-6   # IGMH 需指定片段原子范围
  ./run_multiwfn.sh input.fchk xyz2gjf    # 需当前目录有 template.gjf
  ./run_multiwfn.sh input.fchk tranxyz
  ./run_multiwfn.sh input.fchk all        # 顺序运行所有

  NCI 的退出码 59 在脚本中做了兼容处理；AIM 后的 mv
```
---

## 模块四：可视化

### 4.1 xyzrender 渲染

读取 `references/visualization.md` 获取渲染命令。

渲染前确认：
1. cube 文件路径
2. 渲染类型：ESP / NCI
3. 等值面参数和透明度

**ESP 渲染**：

Multiwfn 产出 `totesp.cub` 和 `density.cub`，需重命名为 `.cube` 后缀：

```bash
mv totesp.cub ESP.cube
mv density.cub DENSITY.cube
xyzrender DENSITY.cube --esp ESP.cube --iso 0.005 --opacity 0.75 -o esp.svg
```

**NCI 渲染**：

Multiwfn 产出 `func1.cub`（sign(lambda2)*rho）和 `func2.cub`（RDG），需重命名：

```bash
mv func1.cub signrho.cube
mv func2.cub rdg.cube
xyzrender signrho.cube --nci-surf rdg.cube -o nci.svg
```

批量处理脚本见 `scripts/drawesp.sh` 和 `scripts/drawnci.sh`。

### 4.2 VMD 脚本生成

读取 `references/visualization.md` 中的 VMD 模板，根据分析类型生成对应的 .vmd 脚本：

| 分析类型 | VMD 脚本 | 需要的文件 |
|----------|----------|------------|
| AIM | `AIM.vmd` | CPs.pdb, paths.pdb, mol.pdb |
| IGMH | `IGM_inter.vmd` | sl2r.cub, dg_inter.cub |
| ESP 等值面 | `ESPiso.vmd` | density.cub, ESP.cub |

生成后告知用户在 VMD 中加载对应脚本。

---

## 完整流程（模块五）

当用户选择完整流程时，根据体系类型选择不同路径：

### 单分子完整流程

```
obabel 转换 → xtb 预优化
→ 生成 Gaussian .gjf → [用户自行提交计算]
→ formchk → Multiwfn 分析 → xyzrender/VMD 可视化
```

### 团簇完整流程

```
准备单体 xyz 文件 → cluster_search_step1.sh 构象搜索
→ 脚本自动生成最优构象 .gjf → [用户自行提交计算]
→ formchk → Multiwfn 分析 → xyzrender/VMD 可视化
```

注意 Gaussian 计算本身不在本技能范围内——只生成输入文件，不执行计算。

---

## 注意事项

- Gaussian 16 计算不在此技能执行范围内，只负责生成 .gjf 输入文件
- Multiwfn 分析必须基于包含频率分析的 fchk 文件
- IGMH 分析的片段原子序号由用户提供，技能不自动推断
- 团簇结合能的 counterpoise 计算需要为每个原子标注片段编号
- 所有批处理脚本在使用前确认工作目录路径
