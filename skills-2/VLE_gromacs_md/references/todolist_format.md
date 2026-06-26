# todolist.json 格式规范

`todolist.json` 是工作流的核心配置文件。脚本在运行前会自动对其进行严格校验，不符合规范的 JSON 会直接中止。

## 结构要求

```json
{
  "task1": {
    "description": "string (可选)",
    "molecules": [
      {
        "name": "AAA",
        "smiles": "string (可选)",
        "charge": 0
      }
    ]
  },
  "task2": {
    "description": "string (可选)",
    "conformations": []
  },
  "task3": {
    "description": "string (可选)",
    "molecules": [
      {
        "name": "AAA",
        "count": 200,
        "phase": "l"
      }
    ]
  },
  "task4": {
    "description": "string (可选)",
    "molecules": [
      {
        "name": "BBB",
        "count": 2000,
        "phase": "g",
        "fchk": "string (可选)",
        "source_file": "string (可选)",
        "aliases": ["alias1", "alias2"]
      }
    ]
  }
}
```

## 校验规则

1. **必须是合法 JSON**，不能含尾随逗号。
2. **顶层键只允许** `task1`、`task2`、`task3`、`task4`，不能多。
3. **task3 必须存在**，其 `molecules` 数组中的每个对象**只能包含** `name`、`count`、`phase`，不能少也不能多。
4. **task4（VLE 用）** 中的每个对象**只能包含** `name`、`count`、`phase`，以及可选的 `fchk`、`source_file`、`aliases`，不能多。
5. `name` 必须是非空字符串，只能以字母开头且仅含字母数字，**不能为 `MOL` 或 `UNL`**。
6. `count` 必须是正整数。
7. `phase` 只能是 `"l"`（液相）或 `"g"`（气相）。
8. **通过校验后，脚本会自动将 JSON 格式化为标准 2 空格缩进并写回文件**。

## 各 task 语义

### task1

用于单分子准备阶段读取电荷信息，影响 `resp.sh` / `gentop.sh` 后续生成的拓扑。

### task3

用于主盒子生成。支持 `phase` 字段：

- `l`：放在液相区域
- `g`：放在气相区域

即使全部是液相，仍建议显式写出 `phase: "l"`，保持文档一致性。

### task4

只在 VLE 阶段使用，用来表达共存相阶段的体系组成。要区分两种语义：

1. **基础液相主体/继承项**（如 `task3 box`）：表示最终 VLE 体系继承自前一阶段已平衡好的液相盒子；是组成说明，不是新的单分子输入，不要求存在对应 `*.fchk`。
2. **新增分子**（如额外插入的 `Water`、`CO2`）：只有这些才需要在 `VLE_MD/` 中继续准备 `gro/itp/top`。

若新增分子的真实源文件名与 `name` 不一致，优先在 `task4` 中显式写 `fchk` / `source_file` / `aliases`，例如 `{"name":"H2O","fchk":"water.fchk"}`。
