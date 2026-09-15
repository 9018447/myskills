---
name: crest-nci-cluster
description: >-
  Run and analyze CREST NCI-mode cluster searches (crest struc.xyz --nci,
  or TOML runtype="nci-mtd") for non-covalently bound molecular clusters and
  aggregates: water/solvent clusters, ion solvation shells, hydrogen-bonded
  and van-der-Waals complexes, molecular aggregates. Covers ellipsoid-wall
  metadynamics setup, dry-run validation, execution with GFN-xTB/GFN-FF,
  ensemble output parsing (crest_best.xyz / crest_conformers.xyz), and
  Boltzmann-population analysis. Trigger when the user asks to search/sample
  cluster structures, low-lying isomers of a molecular aggregate, (H2O)n
  clusters, NCI conformers with CREST, 团簇搜索, 团簇构型采样, 水团簇,
  非共价复合物, 聚集体构象搜索, or mentions crest --nci / nci-mtd.
---

# CREST NCI 团簇搜索

用 CREST 的 NCI（non-covalent interactions）模式搜索非共价结合团簇的低能构型系综。
核心机制：在常规 iMTD-GC 构象搜索的 MTD 阶段加一个**椭球费米壁势（ellipsoid wall
potential, `wall_fermi`）**，阻止偏置势把碎片推散；几何优化阶段壁势自动移除，避免
人为压缩。

## 1. 先判断是否该用 NCI 模式

| 用户目标 | 正确入口 |
|---|---|
| 已知碎片组成的**聚集体**，搜索碎片相对排布与低能异构体 | **NCI 模式（本 skill）** |
| 只有分子式/碎片列表，需要从头随机组装团簇 | QCG 模式（`crest -qcg`，不在本 skill） |
| 单个柔性分子的构象/旋转异构体 | 常规构象搜索（`crest struc.xyz`，不加 `--nci`） |
| 反应、过渡态、键的形成/断裂 | 不适用，CREST 只做非反应性采样 |

NCI 的输入必须**已经是一个拼装好的聚集体**：碎片处于相互作用距离内（典型氢键
1.7–2.5 Å），不能是相距很远的孤立分子——椭球尺寸由输入构型自动测定，输入过散会
得到过大的椭球壁。

## 2. 前置检查

```bash
crest --version      # 需要 crest；TOML 输入需要 >= 3.0（本地实测 3.0.2）
xtb --version        # CREST 调用 xtb 做能量/梯度/优化，必须在 PATH 中
```

缺失时提示用户安装（conda: `conda install -c conda-forge crest xtb`）。
线程数取 `-T`，否则读 `OMP_NUM_THREADS`。

## 3. 标准工作流

1. **准备输入结构** `struc.xyz`（Å 单位的 XYZ）。可用 `assets/h2o6.xyz` 作格式范例。
   - 碎片本身先粗优化（`xtb frag.xyz --opt`），再手动/用组装脚本拼成聚集体；
   - 避免原子重叠，碎片间距放在典型非共价作用距离；
   - 检查总电荷（`-chrg`）与自旋（`-uhf` = Nα−Nβ），闭壳中性体系省略。
2. **dry run 核对设置**（任何正式运行前必做）：
   ```bash
   crest struc.xyz --nci --dry -T 24
   ```
   确认输出含 `MTD-GC modified mode : "-nci"` 与 `wall_fermi atoms: N/all` 及半轴
   长度（Å）。半轴与团簇尺寸明显不符，说明输入拼装过散或过紧，回到第 1 步。
3. **正式运行**。测试/小团簇用缩减档提速；生产计算用默认档（不要加 quick 类标志）。
   日志重定向保存，运行可能从数分钟到数小时：
   ```bash
   crest struc.xyz --nci -T 24 > nci_run.log 2>&1
   ```
4. **确认正常结束**：日志末尾出现 `CREST terminated normally.`，并检查
   `Wall Time Summary`。
5. **分析系综**（见第 6 节），必要时按第 7 节调参重跑。

## 4. 两种调用方式

### 4.1 命令行（所有 CREST 2.x/3.x）

```bash
crest struc.xyz --nci [options]
```

### 4.2 TOML 输入（CREST >= 3.0，推荐，设置可复现）

模板见 `assets/input_nci.toml`：

```toml
input   = "struc.xyz"
runtype = "nci-mtd"
threads = 24

[calculation]
[[calculation.level]]
method = "gfn2"
```

运行：`crest input.toml [--dry]`。注意 TOML 下多数命令行标志不再使用，参数写进
TOML；`--dry` 仍可附加。

## 5. 常用选项（CLI）

NCI 专属：

| 选项 | 作用 |
|---|---|
| `--nci` / `-nci` | 开启 NCI 团簇模式（椭球壁 + 专用 MTD 偏置，减少 MTD 数） |
| `--wscal <real>` | 椭球三轴整体缩放因子，默认 1.0；`<1` 收紧（团簇易散时），`>1` 放宽（壁干扰重排时） |

成本/精度档（与 `--nci` 组合）：

| 选项 | 作用 |
|---|---|
| `-quick` / `-squick` / `-mquick` | 逐级缩减的快速档；只用于测试与粗筛。实测 (H₂O)₆ `--nci -squick`，24 线程约 25 s |
| `-gfn2`（默认）/`-gfn1`/`-gfn0`/`-gff` | GFN2-xTB / GFN1 / GFN0 / GFN-FF 力场（大团簇提速，GFN-FF 自动加键约束） |
| `-gfn2//gfnff` | GFN-FF 采样 + GFN2 终优化的复合方法 |
| `-T <n>` | CPU 线程数 |

体系与环境：

| 选项 | 作用 |
|---|---|
| `-chrg <int>` | 总电荷（如 `(H2O)n·Cl⁻` 用 `-chrg -1`） |
| `-uhf <int>` | Nα−Nβ 未配对电子数 |
| `-alpb <solv>` / `-g <solv>` | ALPB / GBSA 隐式溶剂；水合团簇可考虑 `-alpb water`，但会显著改变相对能量，决定后全流程一致使用 |
| `-ewin <real>` | 保留系综的能量窗口（kcal/mol，默认 6.0） |
| `-mdlen/-len <ps>` | MTD 长度；`<1` 的倍率写法如 `x1.5` 表示默认长度 ×1.5 |
| `-mdtemp <T>` | MTD 温度（默认 300 K；难采样可提高） |
| `-keepdir` | 保留各生成步骤子目录（调试用） |
| `--dry` | 只打印将采用的设置后退出，不做计算 |

完整选项表与输出文件详解见 `references/options-and-outputs.md`。

## 6. 输出与结果分析

成功运行后的关键产物（CWD 中）：

| 文件 | 内容 |
|---|---|
| `crest_best.xyz` | 全局最低能构型（单一 XYZ） |
| `crest_conformers.xyz` | 去重后的独特**构象**系综（多结构 XYZ，能量在标题行，单位 Eh） |
| `crest_rotamers.xyz` | 进一步细分旋转异构后的完整系综（通常 ≥ 构象数） |
| `crest_dynamics.trj` | MTD/MD 轨迹 |
| `crest_0.mdrestart` | MTD 重启信息 |
| `crest_input_copy.xyz` | 输入结构备份 |
| 日志（stdout） | `Final Ensemble Information`：独特构型数、最低能量、系综平均能、熵、自由能、最低构象布居 |

用随附脚本生成排名表（相对能量 kcal/mol + 指定温度下 Boltzmann 布居）：

```bash
python3 scripts/summarize_ensemble.py crest_conformers.xyz --temp 298.15 --top 20
# rotamer 级：标题行自带 CREST 官方布居，脚本会并排显示 crest/% 与重算值
python3 scripts/summarize_ensemble.py crest_rotamers.xyz --top 20
# 其他用法：--ewin 6.0 按能量窗口过滤，--json 输出机器可读结果
```

布居口径注意：`crest_rotamers.xyz` 标题行第二字段是 CREST 写出的逐条 rotamer
Boltzmann 分数（脚本实测与重算值一致、总和 100%）；`crest_conformers.xyz` 只有
能量，其构象布居是成员 rotamer 的**简并平均/求和**（日志 `population of lowest`
即此口径），脚本对该文件给的是等简并近似，正式报告以 CREST 日志/rotamer 文件为准。

能量在 XYZ 标题行；无能量字段的结构会被跳过并提示。构型查看用任意分子可视化程序
（VMD、ChemCraft、ASE、`obabel` 转换等）。

## 7. 调参与故障排查

- **系综里出现碎片解离/飞散结构**：椭球壁太松。逐步试 `--wscal 0.9`、`0.8`；
  或降低 MTD 温度 `--mdtemp 260`。同时检查输入是否本身过散。
- **构型多样性不足、所有结果挤在输入附近**：壁可能太紧或采样不足。试
  `--wscal 1.1`、`-mdlen x1.5`、提高 MTD 温度，或用默认档重跑（勿用 quick 档下结论）。
- **大团簇太慢**：先用 `-gfn2//gfnff` 或 `-gff -squick` 粗筛，取 `crest_best.xyz`
  再用默认 GFN2 精跑。
- **dry-run 半轴异常**：椭球由输入构型的原子分布自动拟合。重新拼装输入，使碎片
  在作用距离内且整体近似紧凑。
- **找不到足够低能构型**：NCI 比单分子构象搜索更难（每个碎片自身也有构象）。
  从多个不同初始拼装各跑一次，再用 `crest -compare ens1.xyz ens2.xyz` 合并比较；
  必要时增大 `-ewin`。
- **带电/开壳层**：务必显式 `-chrg`/`-uhf`，并在 dry run 中核对。
- **几何优化阶段看不到壁势是正常的**：壁势只存在于 MTD，优化时自动移除。

## 8. 引用

向用户报告结果时附上：
- P. Pracht, F. Bohle, S. Grimme, *PCCP* **2020**, 22, 7169–7192（CREST）
- S. Grimme, *JCTC* **2019**, 15, 2847–2862（GFN2-xTB）
- P. Pracht et al., *J. Chem. Phys.* **2024**, 160, 114110（CREST 3）

方法细节：文档示例为 (H₂O)₆，默认设置下从单一输入可自动生成数十个团簇
（文档报告 69 个），其中包含 WATER27 基准集中的已知低能结构；本 skill 实测
`squick` 档得 97 个独特构象 / 182 个 rotamer。
