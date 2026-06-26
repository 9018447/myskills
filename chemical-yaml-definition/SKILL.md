---
name: chemical-yaml-definition
description: >
  Define new chemicals (ionic liquids, custom solvents) for thermosteam via YAML
  files with pure-component properties, constant property models, and COSMO-SAC sigma
  profiles. Use `tmo.load_chemicals_from_yaml('path.yml')` to load. Trigger whenever
  user mentions defining custom chemicals, ionic liquids, YAML chemical format,
  adding new species to thermosteam, or COSMO-SAC sigma profiles for user-defined
  compounds. Also triggers when user needs to create Chemical objects for compounds
  not in PubChem/ChEDL databases.
---

# Chemical YAML Definition

Define custom chemicals (ionic liquids, novel solvents, etc.) that are absent from PubChem/ChEDL databases via a single YAML file. The loader `tmo.load_chemicals_from_yaml(path)` returns a `Chemicals` object ready for `.compile()` and `settings.set_thermo()`.

## Quickstart

```python
import thermosteam as tmo

chems = tmo.load_chemicals_from_yaml('my_chemicals.yml')
chems.compile(skip_checks=True)
tmo.settings.set_thermo(chems)

# Now use in streams:
s = tmo.Stream('feed', MyIL=100, T=300, P=101325)
```

## YAML Schema Reference

Top-level key MUST be `chemicals`. Each entry is a chemical ID (used as `Chemicals.ID`).

```yaml
chemicals:
  MyChemical:
    search_db: false          # false → Chemical.blank(); true/省略 → Chemical(ID)
    phase: l                  # 锁定到单相 (可选: 'l', 'g', 's')
    phase_ref: l              # 298K 参考相 (可选)

    names:
      CAS: "143314-16-3"
      common_name: "my_chem"  # 用于 COSMO-SAC 查找（小写）
      formula: "C6H11BF4N2"   # 自动计算 MW（覆盖 data 中的 MW）
      iupac_name: "..."
      smiles: "..."
      InChI: "..."
      pubchemid: "..."
      aliases:
        - "alias1"
        - "alias2"

    data:                     # 标量纯组分属性（标准单位）
      MW: 197.97              # g/mol
      Tm: 288.0               # K
      Tb: 573.15              # K
      Tc: 850.0               # K
      Pc: 2.2e6               # Pa
      Vc: 6.8e-4              # m³/mol
      omega: 0.65             # 无因次
      Hf: -3.5e5              # J/mol
      dipole: 4.5             # Debye

    properties:               # 温变物性模型（v1 仅支持常数）
      V:                      # PhaseHandle → 需要阶段子键
        l:
          constant: 1.8e-4    # m³/mol
      Cn:
        l:
          constant: 350.0     # J/mol/K
      mu:
        l:
          constant: 0.001     # Pa·s
      kappa:
        l:
          constant: 0.15      # W/m/K
      Psat:                   # 非 PhaseHandle → 直接写模型
        constant: 1.0e-6      # Pa
      Hvap:
        constant: 50000.0     # J/mol

    cosmo:                    # COSMO-SAC sigma profile（可选）
      A: 250.0                # COSMO 面积 [Å²]
      V: 320.0                # COSMO 体积 [Å³]
      Pnhb: [0.0, 0.01, ...]  # 51 个浮点数，非氢键
      POH:  [0.0, ...]        # 51 个浮点数，OH 氢键
      POT:  [0.0, ...]        # 51 个浮点数，OT 氢键
```

## Canonical Units

所有 YAML 中的数值使用以下标准单位（`chemical_units_of_measure`）：

| 字段 | 单位 | 字段 | 单位 |
|---|---|---|---|
| MW | g/mol | Tm, Tb, Tt, Tc | K |
| Pc, Pt, Psat | Pa | V, Vc | m³/mol |
| Cn | J/mol/K | mu | Pa·s |
| sigma | N/m | kappa | W/m/K |
| Hvap, Hf, LHV, HHV, Hfus | J/mol | S0 | J/K/mol |
| dipole | Debye | epsilon | 无因次 |

## 关键细节与陷阱

### 1. PyYAML 6.x 科学计数法 BUG

PyYAML 6.x 将 `2.0e6`、`2e6` 解析为**字符串**而非浮点数。加载器内部有 `_coerce_data()` 自动转换，但用户需注意：
- 在 YAML 中写非科学计数法的值（如 `2000000.0`）更安全
- 或用 PyYAML 显式类型：`!!float 2.0e6`

### 2. 单相锁定化学品 vs PhaseHandle

`phase: l` 锁定后，`lock_phase()` 将 `chem.V`（原本是 `PhaseHandle`）替换为具体实现类（如 `VolumeLiquid`）。这意味着：
- **调用时不加阶段参数**：`IL.V(298.15, 101325)`，**不是** `IL.V('l', 298.15, 101325)`
- `VolumeLiquid` 是 TP 依赖属性（T 和 P 都需要）
- `HeatCapacityLiquid`（Cn）是 T 依赖属性（只需 T）：`IL.Cn(298.15)`

YAML 语法不变，仍可写 `{l: {constant: ...}}`。加载器通过 `_is_phase_wrapped_spec()` 自动识别。

### 3. COSMO-SAC 查找键

`estimate_sigma_profiles()` 通过 `(chem.common_name or chem.ID).lower()` 查询。所以：
- YAML 中设置 `common_name` 且小写，或
- 确保 ID 与 `add_cosmo_profile` 传入的键匹配

### 4. formula 自动计算 MW

`formula` setter 会调用 `compute_molecular_weight()` 并**覆盖** `data:` 中的 MW。如果设置了 formula，data 中的 MW 会被忽略。

### 5. COSMO 数据格式

- 3 个向量各需 **51 个浮点数**（`NUM_SIGMA_POINTS = 51`）
- 数据写入 `cosmosac_database.json`（`thermosteam/equilibrium/` 下）
- 每次加载有 `cosmo:` 段落的化学品会写入/追加到该文件

### 6. search_db: false → 必需的最小数据

对于离子液体（锁相为 l），`blank()` 需要至少：
- `MW`（或 `formula`）
- `Tc`、`Pc`（用于 EOS 初始化）
- `V` 和 `Cn` 的常数模型（否则无方法可用）
- `Psat` 设极小值（IL 蒸气压可忽略）

### 7. 温变模型 v1 限制

当前仅支持常数模型（`constant` 键）。温度相关的 Antoine/DIPPR 系数暂不支持（无法在 YAML 中序列化 lambda）。用户可先通过 YAML 加载常数模型，再在 Python 中手动附加 callable 模型。

## 实现参考

- **加载器**: `thermosteam/thermosteam/chemical_yaml_loader.py`
- **Chemical 类**: `thermosteam/thermosteam/_chemical.py`（`blank()` at line 648, `lock_phase()` at line 2158）
- **COSMO-SAC**: `thermosteam/thermosteam/equilibrium/fast_sigma.py`（`add_cosmo_profile()` at line 116）
- **PhaseHandle**: `thermosteam/thermosteam/base/phase_handle.py`
- **示例 YAML**: `examples/custom_chemicals.yml`
- **测试**: `tests/test_chemical_yaml.py`