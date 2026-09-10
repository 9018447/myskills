# Vega 交互功能参考

本文档告诉你如何利用 Vega 的 **Signals**、**Event Streams**、以及 **Input Bindings** 实现真正的交互式图表。

## 目录
1. [Signals（信号）](#1-signals)
2. [事件驱动的交互（Event Streams）](#2-event-streams)
3. [Input Bindings（UI 控件绑定）](#3-input-bindings)
4. [悬停高亮 (Hover Highlight)](#4-悬停高亮)
5. [数据选择过滤 (Click to Highlight/Filter)](#5-数据选择过滤)
6. [缩放与平移 (Zoom & Pan)](#6-缩放与平移)

---

## 1. Signals

Signals 是 Vega 的响应式变量，驱动图表的动态行为。

```json
"signals": [
  {
    "name": "opacity",
    "value": 0.7
  },
  {
    "name": "pointSize",
    "value": 50
  }
]
```

结合 `bind` 绑定到 UI 控件（见下方 Input Bindings）。

---

## 2. Event Streams

Event Streams 捕获用户交互，并更新信号值：

| 选择器字符串 | 含义 |
|---|---|
| `"mousemove"` | 任何 mousemove 事件 |
| `"rect:click"` | 点击 rect mark |
| `"@markName:mouseover"` | 鼠标悬停到名为 markName 的 mark |
| `"[mousedown, mouseup] > mousemove"` | 拖动（drag）|
| `"timer{1000}"` | 每 1 秒触发一次 |
| `"click[event.shiftKey]"` | Shift+点击 |

---

## 3. Input Bindings

在 `signals` 中通过 `bind` 自动生成 UI 控件，实现用户可调节参数：

### 滑块 (Slider)
```json
{
  "name": "opacity",
  "value": 0.7,
  "bind": {"input": "range", "min": 0, "max": 1, "step": 0.05, "name": "透明度"}
}
```

### 下拉选择 (Select)
```json
{
  "name": "colorScheme",
  "value": "category10",
  "bind": {
    "input": "select",
    "options": ["category10", "tableau10", "set1", "dark2", "paired"],
    "name": "颜色方案"
  }
}
```

### 复选框 (Checkbox)
```json
{
  "name": "showGrid",
  "value": true,
  "bind": {"input": "checkbox", "name": "显示网格"}
}
```

### 单选按钮 (Radio)
```json
{
  "name": "scaleType",
  "value": "linear",
  "bind": {
    "input": "radio",
    "options": ["linear", "log"],
    "name": "坐标轴类型"
  }
}
```

### 实际使用中的效果（在 mark encode 中引用 signal）
```json
"encode": {
  "update": {
    "opacity": {"signal": "opacity"},
    "size": {"signal": "pointSize"}
  }
}
```

---

## 4. 悬停高亮

**实现思路**: 定义一个 `hoveredDataset` 信号，在 `mouseover` 时更新，其他 mark 通过 `opacity` 降低对比度。

```json
"signals": [
  {"name": "hoveredId", "value": null,
   "on": [
     {"events": "*:mouseover", "update": "datum && datum.temperature_K"},
     {"events": "*:mouseout",  "update": "null"}
   ]
  }
]
```

在 mark 的 `encode.update` 中使用：
```json
"opacity": [
  {"test": "hoveredId && datum.temperature_K !== hoveredId", "value": 0.2},
  {"value": 0.9}
]
```

---

## 5. 数据选择过滤

**点击图例（或某个点）切换数据显示**：

```json
"signals": [
  {
    "name": "selectedDatasets",
    "value": [],
    "on": [
      {
        "events": {"source": "view", "type": "click", "markname": "legend_entries"},
        "update": "indata('selected', 'value', datum.value) ? splice(selectedDatasets, indexof(selectedDatasets, datum.value), 1) : push(selectedDatasets, datum.value)"
      }
    ]
  }
]
```

---

## 6. 缩放与平移

**利用 `domainRaw` 实现 zoom/pan**：

```json
"signals": [
  {
    "name": "xdom",
    "update": "slice(xdomainExtent)",
    "on": [
      {
        "events": {"type": "wheel", "consume": true},
        "update": "[xdom[0] + (xdom[1] - xdom[0]) * event.deltaY * 0.001, xdom[1] - (xdom[1] - xdom[0]) * event.deltaY * 0.001]"
      }
    ]
  }
],
"scales": [
  {
    "name": "x",
    "type": "linear",
    "domainRaw": {"signal": "xdom"},
    "range": [0, {"signal": "width"}]
  }
]
```
