---
name: gromacs-md-workflow
description: "Automates GROMACS molecular dynamics workflows from Gaussian fchk files — homogeneous liquid builds, RESP charge generation, Sobtop/Packmol topology, and vapor-liquid equilibrium (VLE) slab construction. All simulation stages run via pueue task queue by default. Use this skill whenever the user mentions GROMACS, molecular dynamics, fchk, RESP, Sobtop, Packmol, homogeneous solution, mixed box, VLE, slab, coexistence, NPT, NVT, energy minimization, pueue, or wants to convert quantum chemistry output into runnable MD input files. Also trigger when the user has .fchk files and wants to set up a simulation, or asks about building a liquid box, inserting gas molecules, or running equilibration pipelines."
version: 1.3.0
compatibility: "Requires Bash, Python 3, GROMACS, Multiwfn, Sobtop, Open Babel, Packmol, jq, and bc. Local execution only."
author: "VLE GROMACS MD Team"
user-invocable: true
allowed-tools: "Read, Write, Edit, Bash, Glob, Grep"
metadata:
  version: "1.3.0"
tags: ["gromacs", "molecular-dynamics", "vle", "fchk", "resp", "sobtop", "packmol"]
source: https://github.com/anthropics/claude-code
---

# GROMACS 分子动力学工作流

## 快速上手

最简单的用法 — 从 fchk 文件到可运行的 MD：

```bash
# 0. 首次使用：部署 skill 配置到项目根目录
bash scripts/init_skill.sh

# 1. 把 fchk 文件和 todolist.json 放在同一目录
# 2. 设置盒子大小（必须！）
export BOX_SIZE=80  # 盒子边长，单位：Å
# 3. 一键启动（自动初始化 + EM + NVT + 后台 NPT/MD）
pueue add -- bash scripts/run_workflow.sh
```

一个最小的 `todolist.json` 示例（均相液体，200 个乙醇分子）：

```json
{
  "task1": {
    "molecules": [
      { "name": "EOH", "smiles": "CCO", "charge": 0 }
    ]
  },
  "task2": { "conformations": [] },
  "task3": {
    "molecules": [
      { "name": "EOH", "count": 200, "phase": "l" }
    ]
  }
}
```

然后把 `EOH.fchk` 放到同目录，设置 `BOX_SIZE` 环境变量后运行 `bash scripts/run_workflow.sh` 即可。

**重要**：`BOX_SIZE` 必须在运行工作流前设置，否则 `3_task_genVLEbox.sh` 阶段会报错中止。

> 完整的 todolist.json 格式规范见 `references/todolist_format.md`。

---

## 路线选择

进入工作目录后，先看现有工件来判断走哪条路线，不要机械执行用户口头指令：

| 当前目录工件 | 应走路线 | 原因 |
| --- | --- | --- |
| 只有 `*.fchk` / `todolist.json`，没有 `topol.top` | `--mode homogeneous`（默认） | 还没完成均相构建 |
| 已有 `topol.top` 且存在 `md.gro` / `md*.gro` / `npt.gro` | `--mode post-homogeneous-vle` | 均相结果已可作为 VLE 基底 |
| 已有 `VLE_MD/npt_expanded.gro` | 直接续跑 VLE 构建 | 5_beta 已完成 |
| 已有 `VLE_MD/system_with_gas.gro` 和 `VLE_topol.top` | 直接续跑 VLE MD | 建模已完成 |

## 主入口

```bash
bash scripts/run_workflow.sh
```

所有模拟阶段（EM → NVT → NPT → MD）**必须**通过 **pueue** 后台执行。工作流只在前台做目录初始化和体系构建，然后将完整管线提交到 pueue 队列。

**执行规则**：除前台调试（`--no-pueue`）和文件准备/体系构建外，所有 GROMACS 模拟命令一律使用 `pueue add -- bash ...` 提交，禁止直接在前台运行模拟。例如：

```bash
# ✅ 正确：通过 pueue 提交模拟
pueue add -- bash scripts/5_build_system.sh
pueue add -- bash -c "cd workdir && gmx mdrun -deffnm md"

# ❌ 错误：直接前台运行模拟（仅限调试场景）
bash scripts/5_build_system.sh
gmx mdrun -deffnm md
```

常用变体：

```bash
# 只初始化目录，不跑模拟
bash scripts/run_workflow.sh --init-only

# 查看当前进度
bash scripts/run_workflow.sh --status

# 预演模式（查看将要执行的命令）
bash scripts/run_workflow.sh --dry-run

# 已有 em.gro 或 nvt.gro，只继续后台管线
bash scripts/run_workflow.sh --resume-md

# 关闭 GPU
bash scripts/run_workflow.sh --cpu-only

# 自定义线程
bash scripts/run_workflow.sh --threads 6

# 前台执行（调试用，不经过 pueue）
bash scripts/run_workflow.sh --no-pueue
```

### pueue 监控

```bash
pueue          # 查看队列中所有任务
pueue log <task_id> # 查看某个任务的输出
pueue status        # 查看 daemon 状态
pueue pause <id>    # 暂停某个任务
pueue resume <id>   # 恢复某个任务
pueue remove <id>   # 从队列中移除任务
```

## 1. 均相 / 混合体系

默认阶段顺序：

`em -> nvt -> npt_precompress -> npt_release -> npt -> md`

关键默认值：
- `nvt` 默认开启
- 三阶段 NPT 的压力参数已调优，减少初始盒子偏松导致的局部真空
- **盒子大小必须通过 `BOX_SIZE` 环境变量指定**（单位：Å），例如：`export BOX_SIZE=80`
- 生产阶段 `md.mdp` 默认 5 ns
- 本地 MD 使用 `ntmpi=1`、`ntomp=12`，开启 GPU 加速
- 后台阶段建议显式加 `-pin on`，避免 GROMACS 性能警告

## 2. VLE / 气液共存

只有在均相体系已完成（有 `md.gro` / `npt.gro`）时才进入 VLE 路线。

VLE 阶段顺序：`em -> vle_npt -> vle_nvt`

```bash
# 完整气液两相流程（自动检测已有均相产物）
bash scripts/run_workflow.sh --mode gas-liquid

# 已有 topol.top + md.gro/npt.gro，只继续 VLE
bash scripts/run_workflow.sh --mode post-homogeneous-vle
```

模式语义要点：
- `gas-liquid` 检测到 `topol.top` + `md.gro` / `npt.gro` 时自动跳过均相重建
- `post-homogeneous-vle` 只要有 `topol.top` 和可复用基底结构即可继续
- `VLE_MD/` 中已有 `npt_expanded.gro` 时跳过 `5_beta_VLE.sh`；已有 `system_with_gas.gro` + `VLE_topol.top` 时直接复用

## 关键约束

- **模拟必须走 pueue**：所有 `gmx mdrun`、`gmx grompp` 等模拟阶段命令，必须通过 `pueue add -- bash ...` 提交。前台直接运行仅用于调试（`--no-pueue`）或纯文件操作（目录初始化、体系构建、拓扑生成等非计算步骤）。
- **盒子大小必须通过 `BOX_SIZE` 环境变量指定**：运行 `3_task_genVLEbox.sh` 前必须设置 `export BOX_SIZE=<边长(Å)>`，否则脚本会报错中止。
- **盒子尺寸验证需在 task3 前显式运行**：编辑 todolist.json task3 后，hook 会提醒确定 BOX_SIZE。运行 `3_task_genVLEbox.sh` 前必须通过 box-size-validator 或手动设置 `export BOX_SIZE=<Å>`。
- `task3` 用于主盒子；只做均相液体时全部设为 `phase: "l"` 即可。
- `task4` 只服务于 VLE 阶段；其中"基础液相盒子占位项"是语义说明，不等于新的单分子输入。
- `task4` 的运行态新增分子会由 `5_beta_VLE.sh` 自动过滤掉 `box` / `existing` / `base` 这类占位项，并把解析到的源文件复制为标准化的 `${name}.fchk` 名称。
- 若磁盘文件名与 `task4.name` 不同，可显式写 `fchk`、`source_file` 或 `aliases`，例如 `{"name":"H2O","fchk":"water.fchk"}`。
- 所有残基名必须最终收敛为 3 个字符，且不能保留 `MOL`、`UNL` 等通用默认残基名。
- 使用 pueue 前需确保 daemon 已启动（`pueue daemon`），否则任务会提交失败。

## 常见失败模式

| 现象 | 处理方式 |
| --- | --- |
| `3_task_genVLEbox.sh` 报错"必须设置盒子大小" | 运行前设置环境变量：`export BOX_SIZE=80`（单位：Å） |
| `gas-liquid` 又重跑均相 EM/NVT/NPT | 确认 `topol.top` 与 `md.gro` / `npt.gro` 是否同目录存在 |
| `H2O.fchk` 缺失但有 `water.fchk` | 通过 `fchk` / `source_file` / `aliases` 声明来源；脚本也做大小写无关匹配 |
| `4_prepare_molecules.sh` 误读 `task3` | `5_beta_VLE.sh` 通过环境变量显式传名单，不再依赖 `task3` 回退 |
| `gmx insert-molecules` 只插入部分气体 | `5_build_system.sh` 会自动计算更大的 Z 长度并重试；仍失败则中止 |
| 看到 `MOL` / `UNL` | 不要改 `gentop.sh`；保留 `modify_resname.py` 作为唯一残基名修正规则 |
| 前台直接运行 `gmx mdrun` | 应改用 `pueue add -- bash -c "cd <dir> && gmx mdrun ..."` 提交；前台运行仅限调试 |

## 你什么时候需要读更多

| 你遇到的情况 | 读这个 |
| --- | --- |
| GMXRC、Sobtop、Multiwfn、Open Babel 环境问题 | `references/dependencies.md` |
| 不确定如何设置 `BOX_SIZE` 盒子大小 | `references/advanced.md`（`3_task_genVLEbox.sh` 章节） |
| 想看 `task3` / `task4` 的详细边界、VLE 中间目录和恢复逻辑 | `references/advanced.md` |
| 需要完整的 todolist.json 格式规范和校验规则 | `references/todolist_format.md` |
| 想了解 pueue 集成细节、任务管理、故障排除 | `references/advanced.md`（pueue 章节） |
| 想了解后台 runner 的重构背景 | `references/REFACTOR_SUMMARY.md` |

只在真正需要细节时再展开这些参考文件，不要把整个手册一次性搬进回答。
