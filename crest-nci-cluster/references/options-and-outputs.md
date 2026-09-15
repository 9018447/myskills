# CREST NCI 模式选项与输出详解

基于 CREST 3.0.2 实测（`crest --help general/conf/other` 与实际 `--nci` 运行）。
旧版 CREST（2.x）只有命令行接口，没有 TOML；标志名基本通用。

## 方法背景

NCI 模式 = iMTD-GC 工作流的特化版本：MTD（metadynamics）数量减少、偏置参数
调整，并在 MTD 期间叠加自动拟合的椭球费米型壁势（`wall_fermi`，日志中显示
`logfermi wall potential`）。壁势抵消 MTD 最大化 RMSD 导致的解离倾向；后续
多级几何优化中壁势自动移除，因此优化结构不会被人为压缩。

椭球半轴由输入结构的原子空间分布自动确定，dry run 会打印三个半轴（Å）：

```
> constraint: wall_fermi atoms: 18/all
  radii(AA)=     5.43084     4.70326     4.89080
```

## 完整常用 CLI 选项

### NCI 与采样工作流（`crest --help conf`）

| 标志 | 含义 / 默认 |
|---|---|
| `-nci` / `--nci` | 椭球壁 + NCI 专用 MTD 设置 |
| `-wscal <real>` | 椭球轴缩放因子，默认 1.0 |
| `-v3` | iMTD-GC 工作流（默认） |
| `-v4` | iMTD-sMTD 工作流 |
| `-quick` / `-squick` / `-mquick` | 缩减档：粗系综 / 进一步缩减 / 最大缩减（下限） |
| `-mdlen`, `-len <real>` | 所有 MTD 长度（ps）；`x<real>` 表示默认长度倍率 |
| `-mdtemp <T...>` | MTD 温度（默认 300 K） |
| `-tstep <int>` | MD 时间步 fs，默认 5 |
| `-shake <0/1/2>` | 约束：0 关 / 1 仅 H / 2 全键，默认 2 |
| `-mddump <int>` | 轨迹写出间隔 fs，默认 100 |
| `-vbdump <real>` | Vbias 写出间隔 ps，默认 1.0 |
| `-tnmd <real>` | 附加常规 MD 温度，默认 400 K |
| `-nocross` | 跳过 GC（genetic crossing）步骤 |
| `-hflip` | MTD 后旋转 OH 基团的增强例程（默认关） |
| `-origin` | 记录每个构象的生成步骤（默认开） |
| `-keepdir` | 保留构象生成阶段的子目录 |

### 通用/技术（`crest --help general`）

| 标志 | 含义 |
|---|---|
| `--input <file>` | 指定 TOML 输入（>= 3.0） |
| `-T <int>` | 线程数；否则读 `OMP_NUM_THREADS` |
| `-gfn2`（默认）/ `-gfn1` / `-gfn0` | GFN2/1/0-xTB |
| `-gff` / `-gfnff` | GFN-FF 力场（需 xtb >= 6.3，自动键约束） |
| `-gfn2//gfnff` | GFN-FF 采样、GFN2 复合终优化 |
| `-opt <lev>` | 所有优化的级别：vloose/loose/normal/tight/vtight |
| `-chrg <int>` | 总电荷 |
| `-uhf <int>` | Nα−Nβ |
| `-g <solvent>` | GBSA 隐式溶剂 |
| `-alpb <solvent>` | ALPB 隐式溶剂（通常更推荐） |
| `-cinp <file>` | 附加 xtb 格式约束文件 |
| `-xnam <bin>` | 指定 xtb 可执行文件名 |
| `--dry` | dry run，只打印设置 |
| `-niceprint` | 优化进度条 |

### 系综筛选默认值（dry run 输出）

| 阈值 | 标志 | 默认 |
|---|---|---|
| 能量窗口 kcal/mol | `-ewin` | 6.0 |
| RMSD 阈值 Å | `-rthr` | 0.125 |
| 能量阈值 kcal/mol | `-ethr` | 0.05 |
| 转动常数阈值 | `-bthr` | 0.01 |
| Boltzmann 温度 K | `-temp` | 298.15 |

## TOML 写法要点（>= 3.0）

- 顶层：`input`、`runtype = "nci-mtd"`、`threads`。
- 方法在 `[calculation]` + `[[calculation.level]]` 表中，`method = "gfn2"`。
- 先以 `crest input.toml --dry` 验证：识别成功时打印 `* runtype = "nci-mtd"`、
  `wall_fermi` 约束与 `MTD-GC modified mode : "-nci"`。
- 模板：`assets/input_nci.toml`。
- 命令行选项与 TOML 键的完整对应见官方 Keyword Documentation：
  https://crest-lab.github.io/crest-docs/ （不要凭记忆编造 TOML 键名，
  不确定时用 dry run 验证）。

## 输出文件

| 文件 | 说明 |
|---|---|
| `crest_best.xyz` | 最低能量构型；可作为更高精度单点/重跑的输入 |
| `crest_conformers.xyz` | CREGEN 去重后的独特构象系综，按能量排序，标题行仅能量（Eh）；构象布居为成员 rotamer 的简并平均 |
| `crest_rotamers.xyz` | 细分旋转异构体后的系综（条目数 ≥ conformers）；标题行 = 能量（Eh）+ Boltzmann 分数 + `!`，分数总和为 1 |
| `crest_dynamics.trj` | 采样轨迹（多帧 XYZ） |
| `crest_0.mdrestart` | MTD 重启文件 |
| `crest_input_copy.xyz` | 输入备份 |
| `gfn2_xtb.log` 等 | 各级 xtb 单点/优化日志（异常时排查用） |

日志结尾 `Final Ensemble Information` 示例（(H₂O)₆，squick，24 线程，25 s）：

```
total number unique points considered further :  182
E lowest                              :  -30.49651
ensemble average energy (kcal)        :   0.309
ensemble entropy (J/mol K, cal/mol K):  35.459    8.475
ensemble free energy (kcal/mol)      :  -2.527
population of lowest in %            :  42.418
number of unique conformers ...       :  97
```

## 与其他工作流的组合

- **多起点**：不同初始拼装分别建目录跑 NCI，再
  `crest -compare ens1.xyz ens2.xyz`（`--help compare`，默认各取前 10）比较合并。
- **粗筛 + 精跑**：`-gfn2//gfnff` 或 `-gff -squick` 粗搜 → 取 `crest_best.xyz`
  作为输入做默认档 GFN2 NCI。
- **隐式溶剂一致性**：采样与最终能量评估必须使用相同溶剂设置，否则相对能量不可比。
- 从单分子/碎片**生成**初始团簇结构属 QCG（`crest -qcg`，见 `--help qcg`），
  其输出可作为 NCI 的输入。

## 引用

- CREST：P. Pracht, F. Bohle, S. Grimme, *PCCP* **2020**, 22, 7169–7192. DOI 10.1039/C9CP06869D
- GFN2-xTB：C. Bannwarth, S. Ehlert, S. Grimme, *JCTC* **2019**, 15, 1652–1671；
  另见 S. Grimme, *JCTC* **2019**, 15, 2847–2862。
- CREST 3：P. Pracht et al., *J. Chem. Phys.* **2024**, 160, 114110.
- 官方示例：https://crest-lab.github.io/crest-docs/page/examples/example_3.html
