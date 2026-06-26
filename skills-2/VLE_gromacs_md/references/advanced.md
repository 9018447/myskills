# 高级用法与维护说明

本文档面向维护者或需要手动拆分流程的用户，重点说明双工作流的执行边界、VLE 体系的额外注意事项，以及常用分析命令。

## 1. 两条工作流的关系

### 1.1 主流程：均相/混合体系

主入口是：

```bash
bash scripts/run_workflow.sh
```

它负责：

1. 复制模板文件与脚本。
2. 根据 `task3` 生成 `box.inp`。
3. 根据 `*.fchk` 生成 `xyz/chg/mol2/gro/top/itp`。
4. 构建 `box.pdb` 与 `topol.top`。
5. 前台完成 EM + 默认 NVT，后台启动三阶段 NPT 与 MD。

### 1.2 VLE 流程：在主流程结果之上继续构建

VLE 相关脚本：

- `scripts/5_beta_VLE.sh`
- `scripts/6_VLE_build_system.sh`
- `scripts/expand_box.sh`

建议顺序：

```bash
# 先完成主流程，至少拿到 npt.gro 和 topol.top
bash scripts/run_workflow.sh

# 准备 VLE 共存相工作目录
bash scripts/5_beta_VLE.sh

# 在 VLE_MD 中插入气体分子并生成新拓扑
cd VLE_MD
bash ../scripts/6_VLE_build_system.sh
```

如果工作目录里已经存在 `md_extend.gro`、`npt_expanded.gro`、`system_with_gas.gro` 等中间文件，优先解释为“当前案例已经处在 VLE 后处理链路的中段或后段”，应该接续现有阶段检查，而不是重新讲一遍从 `task1/task3` 开始的全流程。当前 `run_workflow.sh` 也会按这一原则自动分支：

- 已有 `topol.top` + `md.gro` / `md*.gro` / `npt.gro` 时，`--mode local-gas-liquid` 会自动跳过均相重建，直接续跑 VLE。
- 已有 `VLE_MD/npt_expanded.gro` 时，会跳过 `5_beta_VLE.sh`，只重做 `6_VLE_build_system.sh`。
- 已有 `VLE_MD/system_with_gas.gro` + `VLE_topol.top` 时，会直接复用已构建好的 VLE 输入。

## 2. `todolist.json` 约定

### `task1`

用于单分子准备阶段读取电荷信息，影响 `resp.sh` / `gentop.sh` 后续生成的拓扑。

### `task3`

用于主盒子生成。当前脚本支持读取 `phase`：

- `l`：放在液相区域
- `g`：放在气相区域

即使全部是液相，仍建议显式写出 `phase: "l"`，这样主流程和 VLE 文档保持一致。

### `task4`

只在 VLE 阶段使用，用来表达共存相阶段的体系组成。这里要区分两种语义：

1. **基础液相主体/继承项**：例如 `task3 box`，表示最终 VLE 体系继承自前一阶段已经平衡好的液相盒子；它是组成说明，不是新的单分子输入，因此不要求存在 `task3 box.fchk`。
2. **新增分子**：例如额外插入的 `Water`、`CO2`。只有这些新增分子才需要在 `VLE_MD/` 中继续准备 `gro/itp/top`，并在插分子与拓扑合并时真正参与处理。

当前脚本实现里，`6_VLE_build_system.sh` 最终只对 `phase == "g"` 的新增分子执行 `gmx insert-molecules`。因此在用 skill 解读案例时，不应把 `task4` 中的每个名称都等价为“必须有对应 fchk 的单分子”。

但要注意，当前 `5_beta_VLE.sh` 虽然会自动过滤 `task3 box` 这类占位项并标准化复制 `*.fchk`，仍然建议把运行态意图写清楚。因此：

- `task3 box` 这类条目在**语义上**表示基础液相主体，脚本会自动识别并跳过其单分子准备。
- 若新增分子的真实源文件名与 `name` 不一致，优先在 `task4` 中显式写 `fchk` / `source_file` / `aliases`，例如 `{"name":"H2O","fchk":"water.fchk"}`。
- `5_beta_VLE.sh` 会把解析到的源文件统一复制成 `${name}.fchk`，随后显式把运行态分子列表传给 `4_prepare_molecules.sh`，不再误读 `task3`。

## 3. 目录结构

```text
working_directory/
├── todolist.json
├── md_mdp/
│   ├── minim.mdp
│   ├── nvt.mdp
│   ├── npt_precompress.mdp
│   ├── npt_release.mdp
│   ├── npt.mdp
│   ├── md.mdp
│   ├── vle_npt.mdp          # VLE专用：半各向同性控压Z轴，5ns
│   └── vle_nvt.mdp          # VLE专用：NVT产出，10ns
├── scripts/
├── *.fchk
├── box.inp
├── box.pdb
├── topol.top
├── workflow.log
├── gromacs_md.log
├── output_files/
│   ├── em.*
│   ├── nvt.*
│   ├── npt.*
│   └── md.*
└── VLE_MD/
    ├── npt_expanded.gro
    ├── todolist.json
    ├── topol.top
    ├── *.fchk / *.gro / *.itp / *.top
    ├── system_with_gas.gro
    ├── VLE_topol.top
    ├── vle_npt.*             # VLE NPT阶段输出（5ns）
    └── vle_nvt.*             # VLE NVT阶段输出（10ns）
```

## 4. 关键脚本职责

### `3_task_genVLEbox.sh`

- 从 `task3` 生成 `box.inp`
- 按 `phase` 把液相和气相分配到不同的 `z` 区域
- 兼容”全部液相”的旧用法
- **盒子大小必须通过 `BOX_SIZE` 环境变量指定**（单位：Å），未设置时脚本会报错中止

**重要**：运行前必须设置 `BOX_SIZE` 环境变量：

```bash
export BOX_SIZE=80  # 盒子边长（Å）
bash scripts/3_task_genVLEbox.sh
```

对于 VLE 气液两相体系：
- 液相占据 z = 0 到 BOX_SIZE/2
- 气相占据 z = BOX_SIZE/2 到 BOX_SIZE

对于均相液体体系：
- 所有分子占据整个盒子（z = 0 到 BOX_SIZE）

### `4_prepare_molecules.sh`

- 在当前目录查找 `*.fchk`
- 如果存在 `box.inp`，优先只处理其中用到的分子
- 如果设置了 `PREPARE_MOLECULES` / `PREPARE_MOLECULE_SOURCE`，则优先按显式传入的运行态名单处理（VLE 子流程现在使用这一机制）
- 如果没有 `box.inp`，回退为处理当前目录全部 `*.fchk`

这个回退逻辑对于 `VLE_MD/` 特别重要，因为 VLE 子流程不再依赖 `box.inp`。

### `5_build_system.sh`

这是兼容入口，实际委托给 `5_alapha_build_system.sh`。保留这个名字是为了不破坏老文档和旧脚本调用。

### `5_beta_VLE.sh`

- 解析可用的基础结构，优先 `md.gro` / `md*.gro`，否则回退到 `npt.gro`
- 默认在 Z 轴将基础结构扩展为两倍
- 创建 `VLE_MD/`
- 复制扩盒结果、`topol.top`、`todolist.json` 与 `task4` 中新增分子所需 `*.fchk`
- 支持 `task4` 的 `fchk` / `source_file` / `aliases` 字段，并把来源文件标准化复制为 `${name}.fchk`
- 在 `VLE_MD/` 中显式指定运行态分子列表后调用 `4_prepare_molecules.sh`

注意：如果案例里的 `task4` 含有 `task3 box` 这样的占位项，skill 应把它解释为基础液相主体，而不是要求这类名称一定存在对应 `*.fchk`。

### `6_VLE_build_system.sh`

- 从 `VLE_MD/todolist.json` 读取 `task4`
- 逐种执行 `gmx insert-molecules`
- 生成 `system_with_gas.gro`
- 合并 `atomtypes`
- 生成 `VLE_topol.top`
- 若某种气体插入不足，会按当前盒子尺寸直接计算更大的 Z 长度，用 `gmx editconf` 放大一次后重试；若仍失败则中止，避免生成与实际结构不匹配的拓扑

## 5. VLE / 共存相体系的物理与数值注意事项

### 5.1 不要假设只有单界面

在周期性边界条件下，沿 `z` 方向拉开盒子通常会形成两个界面。这是 slab / coexistence 模拟的常见情形，不是脚本错误。

### 5.2 压强耦合设置

VLE模拟已自动使用专用的 `vle_npt.mdp` 和 `vle_nvt.mdp`：

- `vle_npt.mdp`：半各向同性控压，XY方向固定（compressibility = 0.0），Z方向压缩至1bar（compressibility = 4.5e-5），运行5ns
- `vle_nvt.mdp`：NVT系综，运行10ns用于产出

如需自定义VLE模拟参数，可修改上述两个mdp文件。

### 5.3 盒子尺寸要满足最小镜像要求

无论是主流程还是 VLE 流程，盒子尺寸都应大于非键相互作用截断距离的两倍，否则会引入错误的自相互作用。

### 5.4 VLE 收敛比体相更慢

表面张力、密度剖面和相界面位置通常比体相温压更慢收敛，不要只看短时间内的温度、压力稳定就判断 VLE 已收敛。

## 6. 常用拆分执行方式

```bash
# 只做目录初始化
bash scripts/run_workflow.sh --setup-only

# 只做单分子准备
bash scripts/4_prepare_molecules.sh

# 只做主体系构建
bash scripts/5_build_system.sh

# 已有 em.gro 或 nvt.gro 时，只继续后台三阶段 NPT+MD
bash scripts/run_workflow.sh --md-only
```

## 7. 日志与排错

```bash
# 查看主流程日志
cat workflow.log

# 查看后台日志
tail -f gromacs_md.log

# 查看后台状态
bash scripts/check_progress.sh
```

VLE 阶段常见检查点：

- `npt.gro` 是否来自稳定的液相/混合液平衡
- `task4` 中哪些条目是新增分子，哪些只是基础液相盒子的占位描述
- 只有新增分子的 `name` 才需要与 `*.fchk` 文件名一致
- 如果真实源文件名与 `task4.name` 不同，优先写 `fchk` / `source_file` / `aliases`，不要再手工创建符号链接作为首选方案
- `VLE_MD/` 内是否已生成对应的 `*.gro` 与 `*.itp`
- `system_with_gas.gro` 的原子数是否显著高于 `npt_expanded.gro`

## 8. 常用分析命令

### 温度 / 压力

```bash
gmx energy -f output_files/md.edr -o temperature.xvg
gmx energy -f output_files/md.edr -o pressure.xvg
```

### 密度剖面（界面体系常用）

```bash
gmx density -f output_files/md.xtc -s output_files/md.tpr -d Z -center -o density_z.xvg
```

### RMSD

```bash
gmx rms -s output_files/md.tpr -f output_files/md.xtc -o rmsd.xvg
```

### 电势或界面相关分析

如需做更严格的界面分析，可继续结合 `gmx potential`、`gmx energy` 中与表面张力或压力张量相关的条目分析。

## 9. pueue 任务管理集成

### 9.1 架构概述

所有模拟阶段默认通过 pueue 任务队列后台执行。工作流的执行模型：

```
前台（run_workflow.sh）          后台（pueue 队列）
├── 目录初始化                   ├── local_stage_runner.sh
├── 体系构建（Packmol 等）       │   ├── EM
├── todolist 校验                │   ├── NVT（可选）
└── 提交 pueue 任务              │   ├── NPT（三阶段）
                                 └── MD
```

`local_stage_runner.sh` 是后台管线的核心执行器，负责按顺序运行各阶段并处理 checkpoint resume。

### 9.2 提交流程

`run_workflow.sh` 中的 `run_full_pipeline_via_pueue()` 函数：

1. 将运行环境写入 `.gromacs_local.env`（结构文件、拓扑、MDP 目录、GPU 标志等）
2. 在目标目录中执行 `pueue add -- bash local_stage_runner.sh`
3. 返回任务 ID，用户可通过 `pueue list` 跟踪

VLE 流程使用 `run_vle_pipeline_via_pueue()`，逻辑类似但起始结构为 `system_with_gas.gro`。

### 9.3 常用监控命令

```bash
# 查看队列状态
pueue list

# 查看某个任务的实时输出
pueue log <task_id>

# 查看任务详细信息
pueue status

# 暂停/恢复任务
pueue pause <task_id>
pueue resume <task_id>

# 移除任务
pueue remove <task_id>

# 清空已完成的任务
pueue clean
```

### 9.4 前台执行模式

使用 `--no-pueue` 可以让所有阶段在前台执行，适用于调试：

```bash
bash scripts/run_workflow.sh --no-pueue
```

前台模式下，EM 和 NVT 会阻塞终端，NPT+MD 仍通过 pueue 后台运行。

### 9.5 故障排除

| 问题 | 原因 | 解决方案 |
| --- | --- | --- |
| `pueue add` 失败 | daemon 未启动 | 运行 `pueue daemon` |
| 任务状态为 `Failed` | 模拟错误 | 运行 `pueue log <id>` 查看详细输出 |
| 任务卡住不动 | 等待资源或死锁 | `pueue kill <id>` 终止后检查日志 |
| `Missing env file` | 环境文件未生成 | 确认 `run_workflow.sh` 的 setup 阶段正常完成 |
| GPU 相关错误 | GPU 不可用或驱动问题 | 使用 `--cpu-only` 禁用 GPU |

### 9.6 checkpoint 与恢复

`local_stage_runner.sh` 支持 checkpoint resume：

- 每个阶段默认每 15 分钟写入一次 checkpoint（可通过 `--checkpoint-minutes` 调整）
- 如果任务中断，重新运行 `run_workflow.sh` 会自动从最后的 checkpoint 恢复
- 已完成的阶段会被跳过（通过检查 `.gro` / `.edr` / `.xtc` 文件是否存在）

## 10. 外部参考

- GROMACS Manual: https://manual.gromacs.org/
- GROMACS interface-related analysis: https://manual.gromacs.org/current/reference-manual/analysis/interface-related.html
- GROMACS tutorial (biphase/coexistence): https://tutorials.gromacs.org/tutorial-biphase-new.html
- GROMACS forum discussion on slab/interface setup: https://gromacs.bioexcel.eu/
- Packmol: https://www.ime.unicamp.br/~martinez/packmol/
- Open Babel: https://openbabel.org/
- Multiwfn: http://sobereva.com/multiwfn/
