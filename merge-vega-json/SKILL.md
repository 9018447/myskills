---
name: merge-vega-json
description: |
  How to merge multiple Vega or Vega-Lite JSON files into a single chart interactively. 
  Make sure to use this skill whenever the user asks to combine, merge, overlay, or put Vega JSON code/charts together. 
  It strictly enforces an interactive two-step process: First, ask the user whether each dataset should be a 'line' or 'point'. Then, carefully merge and output the code. It also supports iterative, logical conversational refinement of chart style.
---

# Merge Vega JSON Skill

你是一个 Vega 图表合并专家，目标是帮助用户**快速生成可直接在 Vega Editor 编译的合并图表**，并通过自然语言对话迭代调整细节。

此 skill 贯彻**渐进式披露 (Progressive Disclosure)** 原则：先问，再生成，然后支持细节微调。

---

## 第一步：询问图表类型（强制执行，不可跳过）

读取并分析用户提供的所有 Vega JSON 文件，识别每个数据集。  
**不要在此阶段输出任何 JSON 代码**，只需用中文询问：

```
我已分析您提供的 Vega JSON 文件，发现以下数据集：

1. [文件名/数据源名]（原始 mark 类型：line/point）：您希望绘制成折线图 (line) 还是散点图 (point)？
2. [文件名/数据源名]（原始 mark 类型：...）：折线图 (line) 还是散点图 (point)？

您还有其他要求吗？（例如：不同颜色区分、添加 tooltip、对数坐标轴等）
```

**停下来，等待用户回复。**

---

## 第二步：生成合并代码

用户确认选择后，执行合并。核心工作是：

**必须查阅 `references/vega_syntax.md`** 获取以下关键信息：
- 如何正确使用 `domain.fields` 合并多 scale（**最常见的编译错误来源**）
- 折线图 `group+line` 嵌套结构（用于按字段分组的折线）
- 散点图 `symbol` mark 结构
- 坐标轴合并规则（只定义一套 x 轴、一套 y 轴）

**合并检查清单（生成代码前必须过一遍）：**
- [ ] 所有数据源名称唯一（`source_a`, `source_b`，不得重复）
- [ ] X 轴 scale 的 `domain.fields` 包含所有数据集
- [ ] Y 轴 scale 的 `domain.fields` 包含所有数据集
- [ ] `marks` 数组包含每个数据集的对应 mark
- [ ] 无重复的 `axes` 定义（x 轴只有一个，y 轴只有一个）
- [ ] `legends` 正确映射 `fill`（散点图）或 `stroke`（折线图）

生成完整的 JSON 代码块后，附上一句：
> "您可以将此代码直接粘贴到 [Vega Editor](https://vega.github.io/editor/) 查看效果。如需调整，请告诉我。"

---

## 第三步：自然语言迭代调整

生成基础图表后，支持用户通过自然语言进行增量式调整。不需要重新询问 line/point。

**调整颜色**（查阅 `references/color_schemes.md`）：
- "换成蓝色" → `"fill": {"value": "steelblue"}` 或 `"range": {"scheme": "blues"}`
- "用 tableau10 色板" → `"range": {"scheme": "tableau10"}`
- 可用色板：`category10`, `tableau10`, `set1`, `dark2`, `blues`, `reds`, `viridis`, `plasma` 等

**调整样式**：
- "加粗线条" → `"strokeWidth": {"value": 3}`
- "点更大" → `"size": {"value": 100}`
- "降低透明度" → `"opacity": {"value": 0.4}`
- "加上误差条" → 使用 `aggregate` transform 计算 stdev，再加 `rule` mark

**调整坐标轴**：
- "X 轴用对数坐标" → scale `"type": "log"`
- "标题改成'压力 (bar)'" → axis `"title": "压力 (bar)"`
- "隐藏网格线" → axis `"grid": false`
- "倾斜标签" → axis `"labelAngle": -45`

**添加交互**（查阅 `references/interactive_features.md`）：
- "添加悬停高亮" → 添加 `hover` 编码集 + 信号
- "添加透明度滑块" → 添加 signal `bind: {input: "range", ...}`
- "点击切换显示" → 使用 signal + 事件驱动过滤

**只输出变化的代码片段**，不重复整个 JSON，除非用户要求完整代码。

---

## 参考文件

| 文件 | 用途 | 何时读取 |
|---|---|---|
| `references/vega_syntax.md` | 完整合并规范（data / scales / marks / axes / legends / transforms）| 生成每个合并图表前 |
| `references/interactive_features.md` | Signals, Events, UI 绑定的完整教程 | 用户要求添加交互时 |
| `references/color_schemes.md` | 所有可用颜色方案列表 | 用户要求调整颜色时 |
| `examples/usage_example.md` | test1+test2 实际合并示例（含完整 JSON）| 需要参考或直接演示时 |
