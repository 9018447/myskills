# VLE GROMACS MD TodoList

> 该文件用于记录当前工作目标、所选路线、当前阶段、下一步动作与关键检查结果。
> `todolist.json` 负责机器可读的分子/配比配置；`todolist.md` 负责人类与模型共享的流程状态。

## todolist.json 严格格式

机器可读配置由 `todolist.json` 提供，任何脚本运行前都会先经过 `validate_todolist.py` 校验。**校验失败会直接中止 workflow**。

### 允许字段

- **顶层键**：仅允许 `task1`、`task2`、`task3`、`task4`，禁止任何额外键。
- **task3.molecules[]**：每项必须且只能包含 `name`（字符串）、`count`（正整数）、`phase`（`"l"` 或 `"g"`）。
- **task4.molecules[]**：每项必须包含 `name`、`count`、`phase`，可选 `fchk`、`source_file`、`aliases`（字符串数组）。不允许其它字段。
- **task1.molecules[]**：每项必须包含 `name`，可选 `smiles`、`charge`（数值）。
- `name` 规则：非空、字母开头、仅含字母数字、**不能为 `MOL` 或 `UNL`**。

### 格式化规则

通过校验后，脚本会自动用标准 2 空格缩进重写文件，确保不会因缺少换行或缩进混乱导致下游解析异常。

## 使用规则

1. 开始前必须先与用户确认本次目标，并写入“任务目标确认”。
2. 只能在以下两条路线中二选一，并在“当前路线”中明确标记：
   - `workflow_a_homogeneous`：普通均相溶液/混合体系，严格遵循 `em -> nvt -> npt_precompress -> npt_release -> npt -> md`。
   - `workflow_b_vle`：气液分相/VLE。必须先确认已经完成普通均相体系，并指定结构基础文件（优先 `md.gro`，其次 `md*.gro`，再次 `npt.gro`）。随后再执行扩盒、插分子、改残基名、合并拓扑、`em -> npt -> nvt`。
3. 每完成一个阶段，立即更新“阶段状态追踪”和“下一步”。
4. 一旦进入 VLE 路线，必须在“VLE 前置确认”中记录：
   - 用户指定的结构基础文件
   - 该结构对应的基础拓扑文件
   - 是否已完成盒子扩展
   - 是否已完成插入气体
5. 结构和拓扑建立完成后，必须在“残基名检查”中记录检查结果，确认 `.gro` 与 `topol.top`/`VLE_topol.top` 中不存在 `MOL`、`UNL` 等通用残基名。

---

## 任务目标确认

- 用户目标：
- 用户是否明确要求气液分相 / VLE：
- 当前解释后的执行目标：
- 当前工作目录：
- **盒子大小确认**：`BOX_SIZE` 环境变量已设置（单位：Å），值为：

## 当前路线

- 选定路线：`workflow_a_homogeneous` / `workflow_b_vle`
- 选择理由：

## 阶段状态追踪

| 阶段 | 适用路线 | 状态 | 产物/依据 | 备注 |
|------|----------|------|-----------|------|
| 分子准备与拓扑生成 | A / B | pending | `*.gro`, `*.itp`, `topol.top` | |
| EM | A / B | pending | `em.gro` | |
| NVT | A | pending | `nvt.gro` | |
| NPT 第一阶段（强预压缩） | A | pending | `npt_precompress.gro` | |
| NPT 第二阶段（降压到常压） | A | pending | `npt_release.gro` | |
| NPT 第三阶段（正式 NPT / CR） | A / B | pending | `npt.gro` 或 `vle_npt.gro` | |
| MD | A | pending | `md.gro`, `md.xtc` | |
| 结构基础确认 | B | pending | `md.gro` / `md*.gro` / `npt.gro` | |
| 扩展盒子 | B | pending | `npt_expanded.gro` | |
| 插入气体分子 | B | pending | `system_with_gas.gro` | |
| 合并拓扑 | B | pending | `VLE_topol.top` | |
| VLE EM | B | pending | `em.gro` | |
| VLE NPT | B | pending | `vle_npt.gro` | |
| VLE NVT | B | pending | `vle_nvt.gro` | |

## VLE 前置确认

- 是否需要本阶段：
- 用户指定结构基础文件（优先 `md.gro` / `md*.gro`，否则 `npt.gro`）：
- 对应基础拓扑文件：
- 该基础结构是否来自已完成的普通均相体系：
- task4 中待插入分子：

## 残基名检查

- 检查时间：
- 检查对象：
  - `.gro` 文件：
  - 拓扑文件：
- 是否发现 `MOL` / `UNL` / 其他通用默认残基名：
- 所有残基名是否严格为3个字符：
- 是否存在重复残基名冲突：
  - 如存在，冲突解决方式：
- 最终结论：

## 下一步

- 当前应执行：
- 执行所需输入：
- 完成标准：
