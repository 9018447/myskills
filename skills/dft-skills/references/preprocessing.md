# 前处理工具参考

## obabel — 格式转换

```bash
obabel [-i<输入格式>] <输入文件> [-o<输出格式>] -O<输出文件> [-3d]
```

- `-3d`：生成三维结构（推荐始终添加）
- 支持：sdf, xyz, smiles, mol2, pdb 等格式
- SMILES 直接输入：`obabel -:'CC(=O)O' -oxyz -Ooutput.xyz -3d`

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

**从 xtb 输出提取优化结构**：
- 优化后几何：`xtb_output.xyz`
- 如果需要重新定位分子到原点：obabel 转换
