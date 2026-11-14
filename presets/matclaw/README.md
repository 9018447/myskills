# matclaw 预设集

MatClaw 容器计算技能库，**46 个组 / 188 个子技能 / 508 个文件**（含 scripts、references、assets）。
覆盖电子结构、力学、热学、声子、缺陷、光学、磁学、拓扑、催化、电池、相图、输运、表面界面、
蒙特卡洛、分子动力学、机器学习势、生物分子模拟、量子化学、化学信息学等。

## 布局

每个**组**是一个预设成员（组目录含 `SKILL.md` 作索引与方法决策树），子技能嵌套在组目录内，
各自带 `SKILL.md` 与附属脚本/参考文档。这与上游 `container/skills/<组>/<子技能>/` 层级一致。

子技能**不单独分发**：myskills 的成员识别在含 `SKILL.md` 的目录处即止，因此组成员是 46 个组，
不是 188 个子技能。177 个子技能没有 YAML frontmatter，此处按上游原样保留——它们是组内
参考文档，不作为独立技能加载，无需补头部。

## 成员

| 组 | 子技能数 | 文件数 |
|---|---|---|
| `2d-materials` | 4 | 5 |
| `advanced-electronic` | 5 | 6 |
| `agent-browser` | 0 | 1 |
| `alloy-disorder` | 2 | 3 |
| `band-advanced` | 3 | 4 |
| `battery-electrode` | 2 | 3 |
| `biomolecular-md` | 1 | 2 |
| `bonding-analysis` | 10 | 11 |
| `catalysis-electrochem` | 6 | 7 |
| `catalyst-screening` | 3 | 4 |
| `code-interfaces` | 5 | 6 |
| `deepchem` | 0 | 6 |
| `defects-reactions` | 13 | 14 |
| `dft-corrections` | 3 | 4 |
| `electron-phonon` | 4 | 5 |
| `electronic-structure` | 8 | 9 |
| `fermi-surface` | 3 | 4 |
| `ferroelectric` | 5 | 6 |
| `general-tools` | 16 | 280 |
| `high-throughput` | 8 | 9 |
| `interface` | 2 | 3 |
| `kpath-utilities` | 5 | 6 |
| `magnetic-properties` | 3 | 4 |
| `materials-compute` | 0 | 1 |
| `materials-databases` | 2 | 3 |
| `mechanical-properties` | 5 | 6 |
| `mlip-guide` | 4 | 5 |
| `molecular-qchem` | 1 | 2 |
| `optical-properties` | 6 | 7 |
| `phase-diagram` | 2 | 3 |
| `phase-transition` | 6 | 7 |
| `piezoelectric` | 1 | 2 |
| `potential-analysis` | 3 | 4 |
| `rdkit-kdense` | 0 | 7 |
| `semiconductor-kit` | 4 | 5 |
| `spectroscopy` | 2 | 3 |
| `spin-texture` | 2 | 3 |
| `structure-models` | 8 | 9 |
| `structure-tools` | 8 | 9 |
| `surface-energy` | 2 | 3 |
| `thermal-properties` | 13 | 14 |
| `thermoconductivity` | 1 | 2 |
| `topological` | 2 | 3 |
| `transport-properties` | 2 | 3 |
| `wannier-functions` | 1 | 2 |
| `wavefunction-analysis` | 2 | 3 |

## 来源

上游目录 `container/skills/` 不在 MatClaw 公开 git 仓库中（各分支与标签均无），只烘焙进容器镜像，
因此从镜像层提取：

- 镜像：`ghcr.io/dingyanglyu/matclaw-agent:latest`（amd64）
- manifest：`sha256:465052af6a782a93fbea5421069f3c20ec1d5d768047c842c64db480f996cbcd`
- 层：`COPY skills/ /home/node/.claude/skills/`，`sha256:9e657287dd5ee0ff67c94f32fc774db58569698a8018f3bb66a162b62a00a663`（2.48 MB）
- 提取日期：2026-11-14
- 上游仓库：https://github.com/DingyangLyu/MatClaw （Apache-2.0）
- 其中 `general-tools`、`rdkit`、`deepchem` 等源自 K-Dense AI 的
  [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)，
  各自 frontmatter 保留原许可证（MIT / BSD-3-Clause）

508 个文件中 466 个与上游逐字一致，42 个 `SKILL.md` 只改了 frontmatter，正文与全部
scripts / references / assets 字节未动。两处改动见下。

## 与现有技能的关系

- **`rdkit` 组改名为 `rdkit-kdense`**：myskills 顶层已有 `rdkit`（1177 行，version 2023.09.4），
  上游这份是 K-Dense 版（778 行），内容不同、并非重复。改名避免成员重名报错，两份都保留。
  组 `SKILL.md` 的 `name:` 字段同步改为 `rdkit-kdense`，其余字节未动。
- **41 个组级 `description:` 加了双引号**：上游写成
  `description: 2D Materials Toolkit (4 sub-skills: band-edges, ...)`，
  裸标量含 `: ` 不是合法 YAML，严格加载器会报错。加引号后描述文本逐字不变。
  myskills 自身用逐行正则解析 frontmatter（`manager/src/core.ts:98`），本来不受影响；
  修它是为了别的 agent 用标准 YAML 读时不失败。16 个子技能的 frontmatter 原本就合法，未动。
- **`general-tools` 的 16 个子技能中有 9 个与 myskills 现有技能同名**：
  `pdf`、`scientific-visualization` 内容完全相同；`docx`、`matplotlib`、`plotly`、`pptx`、
  `seaborn`、`sympy`、`xlsx` 是不同版本。本预设按组分发，这些子技能是组内嵌套文档、
  不单独成为技能，因此不构成重名冲突，全部原样保留，未覆盖任何现有技能。
- **`monte-carlo` 不在本预设内**：它已单独存为 `presets/monte-carlo/`，且采用扁平布局
  （5 个子技能各为成员）。两者布局不同是有意为之，勿合并以免成员重名。

## 运行依赖

技能正文假定 MatClaw 容器环境：Quantum ESPRESSO 7.5、LAMMPS、RASPA3、MACE、pymatgen、ASE、
phonopy、BoltzTraP2、spglib、mp-api。本机未装齐这些引擎，直接照搬命令会失败。

特别注意 **RASPA3 ≠ RASPA2**：`monte-carlo` 等技能要求 `raspa3` 二进制与 JSON 输入
`simulation.json`，而本机 `/RASPA/simulations` 是 RASPA 2.0.41（`simulate`，文本输入），
两代不兼容。
