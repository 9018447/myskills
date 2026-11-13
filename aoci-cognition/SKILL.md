---
name: aoci-cognition
description: 只用 AOCI 建立对本仓库的整体框架认知，逐项给出掌握程度百分比，并回答能否接手开发。
disable-model-invocation: true
---

# AOCI 认知盘点

只读盘点：不写索引、不 maintain、不改任何文件。框架认知只来自 AOCI 索引。

## 步骤

### 1. 建立完整认知

- `aoci_rules` —— 取当前会话合同（决定顺序与停点）。
- `aoci_overview` —— 取完整 Whole-Index，这是“整体框架认知”的唯一来源。
- 需要具体事实时用 `aoci_get_entries` / `aoci_search` 定位。

被截断的 chunk 不算完整认知：合同规定模型不能声称拥有未完整接收的索引，分页/续传拿全。

**完成判据**：拿到覆盖全部受管理对象的完整 Overview，且没有截断的 chunk。

### 2. 量化掌握程度

每个百分比都要指回一条命令输出：

```bash
"$AOCI" --repo <root> status
"$AOCI" --repo <root> verify
"$AOCI" --repo <root> index score
```

- 覆盖：已索引受管理对象数 ÷ 受管理对象总数（`status` / `verify` 的 missing 数）。
- 质量：`index score` 九维（format / coverage / freshness / quota / dict / token / agent_ready / escale / tagparse）。
- 治理：`verify` 退出码（0 = 治理完整）与 missing / stale / orphan / unbaselined 计数。

按子系统逐项给百分比，每项标一句依据（哪条命令的哪个数）。给不出依据的数字就不给——写“未知 + 缺什么证据”比写一个凭感觉的百分比有用。

**完成判据**：每项百分比都能指回一个可复核的输出。

### 3. 能不能接手

判据（全部满足 → 可以接手）：

- 索引完整：无 missing / skipped 条目，coverage 与 freshness 达标。
- 治理干净：`verify` 退出码 0。
- 本次任务涉及的对象都有 Entry 覆盖。
- 明确划出 AOCI 之外的未知：数据库运行态、部署与运维配置、第三方服务、线上行为、外部依赖的实际版本。

回答结构：

1. 掌握程度表：子系统 / 百分比 / 依据
2. 未知清单：AOCI 覆盖不到的部分
3. 一句结论：能接手或不能接手 + 还差什么（具体到哪个对象、哪个维度）

**完成判据**：结论与上面判据一致，缺口是具体的。

## 注意

- 本技能只读：任何 `aoci_update_entry` / `aoci_maintain` / `scan --force` 都不属于这里。
- AOCI 给的是仓库内认知；判断运行时行为要另取证据，别把索引当运行态。

## 共享速查

二进制定位、命令清单、退出码、MCP 工具清单：读 `aoci-init` 技能目录下的 `AOCI-QUICKREF.md`（omp: `skill://aoci-init/AOCI-QUICKREF.md`；其他宿主按本技能目录相对解析 `../aoci-init/AOCI-QUICKREF.md`）。
