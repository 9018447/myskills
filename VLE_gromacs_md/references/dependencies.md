# 依赖配置与环境检查

本文档说明本 skill 所依赖的软件、推荐环境变量，以及最常见的安装/排错方法。

## 1. 必需依赖

- GROMACS
- Multiwfn
- Sobtop
- Open Babel
- Packmol
- jq
- bc
- python3

## 2. 关键环境变量

### `GMXRC`

建议显式导出：

```bash
export GMXRC="/path/to/gromacs/bin/GMXRC"
```

主脚本会按以下顺序寻找 GROMACS 环境：

1. `$GMXRC`
2. `~/.bashrc` 中的 `source .../GMXRC`
3. 默认路径 `/media/smh/d/gromacs/bin/GMXRC`

如果你的 GROMACS 不在默认位置，最好始终手动设置 `GMXRC`，避免后台脚本找错环境。

若工作流或子脚本启用了 `set -u` / `set -euo pipefail`，还要额外检查你的 `GMXRC` 是否是一个会读取未定义变量的包装脚本。真实案例中 `/media/smh/d/gromacs/bin/GMXRC` 在 nounset 环境下会因为访问未定义的 `shell` / `GMXLDLIB` 而中断，此时应优先加载 `GMXRC.bash`，或在 `source` 前后临时关闭再恢复 nounset。

### `SOBTOP_DIR`

```bash
export SOBTOP_DIR="/path/to/sobtop"
```

`gentop.sh` 会使用这个目录定位 Sobtop。若未设置，则会回退到 `/media/smh/d/sobtop`。

## 3. 安装建议

### GROMACS

```bash
# Ubuntu / Debian
sudo apt-get install gromacs
```

如果需要特定版本或 GPU 支持，更推荐从源码自行编译。

### Multiwfn

从官方站点下载后加入 `PATH`：

```bash
tar -xzf Multiwfn_*.tar.gz
export PATH="$PATH:/path/to/Multiwfn"
```

### Sobtop

Sobtop 不一定有系统包管理器版本，通常需要手动安装。确保 `sobtop` 可执行文件、其数据目录和参数文件都位于 `SOBTOP_DIR` 所指向的目录树内。

### Open Babel

```bash
sudo apt-get install openbabel
```

### Packmol

```bash
sudo apt-get install packmol
```

### 系统工具

```bash
sudo apt-get install jq bc python3
```

## 4. 快速验证命令

```bash
# GROMACS
source "$GMXRC"
gmx --version

# Multiwfn
Multiwfn < /dev/null

# Sobtop
ls "$SOBTOP_DIR"

# Open Babel
obabel -V

# Packmol
packmol < /dev/null

# 其他工具
jq --version
bc --version
python3 --version
```

## 5. 与脚本直接相关的依赖注意事项

### `resp.sh` 依赖 Multiwfn 交互行为

`resp.sh` 通过预设交互序列调用 Multiwfn。如果你使用的 Multiwfn 版本菜单编号不同，RESP 电荷生成可能失败。此时应优先检查：

- Multiwfn 版本是否与原脚本开发环境一致
- 输入 `.fchk` 是否完整可读
- 输出 `.chg` 是否生成且非空

### `gentop.sh` 依赖 Sobtop 目录结构

`gentop.sh` 会在临时目录中链接 Sobtop 资源后再运行，因此不能只复制单个 `sobtop` 可执行文件，而应保证整套资源完整可用。

### `expand_box.sh` 与 `6_VLE_build_system.sh` 依赖 GROMACS 命令

VLE 流程额外依赖：

- `gmx editconf`
- `gmx insert-molecules`

如果你的 GROMACS 安装是精简版或命令不可用，VLE 流程会在这两步失败。

## 6. 常见问题

### 找不到 Sobtop

报错示例：`Sobtop 目录不存在`

处理方式：

```bash
export SOBTOP_DIR="/actual/path/to/sobtop"
bash scripts/run_workflow.sh --setup-only
```

### 找不到 Multiwfn

报错示例：`Multiwfn: command not found`

处理方式：

```bash
export PATH="$PATH:/path/to/Multiwfn"
```

### Open Babel 转换失败

报错示例：`obabel: command not found` 或 `mol2` 文件为空。

处理方式：

1. 确认 `obabel -V` 能正常输出版本号。
2. 检查 `.xyz` 文件是否由 `fch2xyz.sh` 正确生成。

### Packmol 装箱失败

报错示例：`box.pdb not created`

处理方式：

1. 检查 `box.inp` 是否存在。
2. 检查是否已设置 `BOX_SIZE` 环境变量（`3_task_genVLEbox.sh` 需要此变量）。
3. 检查 `box.inp` 中引用的 `*.pdb` 是否已生成。
4. 检查分子数量、盒子尺寸是否过于激进。

### VLE 阶段插入失败

如果 `6_VLE_build_system.sh` 中 `gmx insert-molecules` 失败，通常优先检查：

1. `npt_expanded.gro` 的盒子是否足够大。
2. `task4` 中的数量是否过大。
3. 气体分子的 `gro` 是否正确生成且残基名可被识别。

当前脚本会先把基础结构在 Z 轴默认扩展为两倍；如果插入仍不足，会按当前盒子尺寸直接计算一个更大的 Z 长度，用 `gmx editconf` 放大一次后重试。若这次仍未插满，说明该配方在现有液相密度下仍然过于拥挤，应重新评估 `task4` 数量或初始基底盒子尺寸。

## 7. 并行设置建议

### CPU-only

```bash
bash scripts/run_workflow.sh --no-gpu --ntmpi 1 --ntomp 12
```

### GPU + MPI

```bash
bash scripts/run_workflow.sh --ntmpi 1 --ntomp 12
```

默认本地设置为 `--ntmpi 1 --ntomp 12`，并开启 GPU 加速。总线程数约为：`ntmpi × ntomp`。

如果后台阶段日志出现

```text
NOTE: The number of threads is not equal to the number of (logical) cpus ... Consider using -pin on
```

优先检查后台 `mdrun` 是否显式带了 `-pin on`。这不会阻止模拟，但会带来不必要的性能损失。
