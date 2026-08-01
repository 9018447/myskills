# Vega 语法完整合并规范

## 目录
1. [数据合并 (data)](#1-数据合并)
2. [比例尺合并 (scales)](#2-比例尺合并)
3. [Marks 选择与合并](#3-marks)
4. [坐标轴 (axes)](#4-坐标轴)
5. [图例 (legends)](#5-图例)
6. [Transforms 数据变换](#6-transforms)

---

## 1. 数据合并

每个数据集必须拥有 **唯一的 name**。合并时将两份 JSON 的 `data` 数组拼接，并重命名冲突的数据源：

```json
"data": [
  {
    "name": "source_a",
    "values": [...]
  },
  {
    "name": "data_a",
    "source": "source_a",
    "transform": [{"type": "filter", "expr": "isValid(datum['x'])"}]
  },
  {
    "name": "source_b",
    "values": [...]
  },
  {
    "name": "data_b",
    "source": "source_b",
    "transform": [{"type": "formula", "expr": "toNumber(datum['x'])", "as": "x"}]
  }
]
```

**常用 Transform 类型（供用户通过自然语言触发）：**

| Transform | 用途 |
|---|---|
| `filter` | 过滤数据，只保留满足条件的行 |
| `formula` | 为数据新建计算列 |
| `aggregate` | 对数据分组汇总（sum, mean, count等）|
| `regression` | 拟合回归曲线（linear, log, poly等）|
| `kde` | 核密度估计 |
| `loess` | LOESS 平滑曲线 |
| `fold` | 将宽格式数据转换为长格式 |
| `bin` | 将连续数据分桶 |
| `stack` | 用于堆叠面积图/柱状图 |
| `window` | 滚动窗口聚合 |

---

## 2. 比例尺合并

**关键原则**：多个数据集共享同一 X 轴或 Y 轴时，必须合并 scale 的 `domain.fields`，否则某些数据会渲染到画布之外，或无法显示。

```json
"scales": [
  {
    "name": "x",
    "type": "linear",
    "domain": {
      "fields": [
        {"data": "data_a", "field": "pressure_bar"},
        {"data": "data_b", "field": "pressure_bar"}
      ]
    },
    "range": [0, {"signal": "width"}],
    "nice": true,
    "zero": false
  },
  {
    "name": "y",
    "type": "linear",
    "domain": {
      "fields": [
        {"data": "data_a", "field": "value"},
        {"data": "data_b", "field": "value"}
      ]
    },
    "range": [{"signal": "height"}, 0],
    "nice": true,
    "zero": true
  }
]
```

**Scale 类型说明：**

| 类型 | 适用场景 |
|---|---|
| `linear` | 连续数据（默认）|
| `log` | 跨越多个数量级的数据（对数轴）|
| `sqrt` / `pow` | 非线性关系 |
| `time` / `utc` | 时间序列 |
| `ordinal` | 离散分类数据 |
| `band` | 柱状图的分类轴 |

**颜色 Scale（适用于离散分类）：**
```json
{
  "name": "color",
  "type": "ordinal",
  "domain": ["Dataset A", "Dataset B"],
  "range": {"scheme": "category10"}
}
```

---

## 3. Marks 选择与合并

根据用户的需求，选择对应的 mark 类型，并将它们全部放入 `marks` 数组：

### 折线图 (line)
```json
{
  "name": "line_mark_a",
  "type": "group",
  "from": {
    "facet": {
      "name": "faceted_path_a",
      "data": "data_a",
      "groupby": ["temperature_K"]
    }
  },
  "encode": {
    "update": {
      "width": {"field": {"group": "width"}},
      "height": {"field": {"group": "height"}}
    }
  },
  "marks": [
    {
      "type": "line",
      "style": ["line"],
      "sort": {"field": "x"},
      "from": {"data": "faceted_path_a"},
      "encode": {
        "update": {
          "x": {"scale": "x", "field": "pressure_bar"},
          "y": {"scale": "y", "field": "value"},
          "stroke": {"scale": "color", "field": "temperature_K"},
          "strokeWidth": {"value": 2},
          "defined": {
            "signal": "isValid(datum['pressure_bar']) && isFinite(+datum['pressure_bar'])"
          }
        }
      }
    }
  ]
}
```

### 散点图/点图 (point)
```json
{
  "name": "point_mark_b",
  "type": "symbol",
  "from": {"data": "data_b"},
  "encode": {
    "update": {
      "x": {"scale": "x", "field": "pressure_bar"},
      "y": {"scale": "y", "field": "value"},
      "fill": {"scale": "color", "field": "temperature_K"},
      "shape": {"value": "circle"},
      "size": {"value": 50},
      "opacity": {"value": 0.8},
      "tooltip": {
        "signal": "{'pressure_bar': datum['pressure_bar'], 'value': datum['value']}"
      }
    },
    "hover": {
      "size": {"value": 100},
      "opacity": {"value": 1}
    }
  }
}
```

### 面积图 (area) - 进阶选项
```json
{
  "type": "area",
  "from": {"data": "data_a"},
  "encode": {
    "update": {
      "x": {"scale": "x", "field": "x_field"},
      "y": {"scale": "y", "field": "y_field"},
      "y2": {"scale": "y", "value": 0},
      "fill": {"value": "steelblue"},
      "fillOpacity": {"value": 0.5}
    }
  }
}
```

### 柱状图 (bar/rect)
```json
{
  "type": "rect",
  "from": {"data": "data_a"},
  "encode": {
    "update": {
      "x": {"scale": "x", "field": "category"},
      "width": {"scale": "x", "band": 1},
      "y": {"scale": "y", "field": "value"},
      "y2": {"scale": "y", "value": 0},
      "fill": {"value": "steelblue"}
    }
  }
}
```

### 文本标签 (text)
```json
{
  "type": "text",
  "from": {"data": "data_a"},
  "encode": {
    "update": {
      "x": {"scale": "x", "field": "x_field"},
      "y": {"scale": "y", "field": "y_field"},
      "text": {"field": "label"},
      "align": {"value": "center"},
      "baseline": {"value": "bottom"},
      "fontSize": {"value": 11},
      "fill": {"value": "#333"}
    }
  }
}
```

---

## 4. 坐标轴

合并后只需定义**一套** x 轴和一套 y 轴（除非用户要求双轴）：

```json
"axes": [
  {
    "scale": "x",
    "orient": "bottom",
    "grid": true,
    "gridColor": "#eee",
    "title": "压力 (bar)",
    "labelAngle": 0,
    "tickCount": {"signal": "ceil(width/40)"},
    "zindex": 0
  },
  {
    "scale": "y",
    "orient": "left",
    "grid": true,
    "gridColor": "#eee",
    "title": "数值",
    "labelOverlap": true,
    "zindex": 0
  }
]
```

**轴的自定义选项（用户通过自然语言请求时使用）：**

- `"labelAngle": -45` — 倾斜标签
- `"format": ".2f"` — 数字格式（如 `".2e"` 科学计数法）
- `"title"` — 轴标题文本
- `"grid": false` — 隐藏网格线
- `"tickCount": 5` — 指定刻度数量
- `"labelFontSize": 12` — 标签字号

---

## 5. 图例

图例的 `stroke` 用于折线图，`fill` 用于点图/面积图。如果一个数据集是 line、另一个是 point，它们颜色映射的 channel 不同，需要给不同数据集定义不同的颜色 scale 或同时指定 `fill` 和 `stroke`：

```json
"legends": [
  {
    "stroke": "color_a",
    "title": "Dataset A (线)",
    "orient": "right",
    "gradientLength": {"signal": "clamp(height, 64, 200)"}
  },
  {
    "fill": "color_b",
    "title": "Dataset B (点)",
    "orient": "right"
  }
]
```

若两个数据集使用**同一颜色 scale**（如都按 temperature_K 着色），则只需定义一个图例，并给该 scale 一个 `"title"` 即可。

---

## 6. Transforms 数据变换

### 回归曲线 (regression)
```json
{
  "name": "regression_line",
  "source": "data_a",
  "transform": [
    {
      "type": "regression",
      "x": "pressure_bar",
      "y": "value",
      "method": "linear",
      "as": ["x", "y"]
    }
  ]
}
```
Method 可选: `"linear"`, `"log"`, `"exp"`, `"pow"`, `"quad"`, `"poly"`

### LOESS 平滑曲线
```json
{
  "name": "loess_data",
  "source": "data_a",
  "transform": [
    {"type": "loess", "x": "pressure_bar", "y": "value", "bandwidth": 0.3}
  ]
}
```

### 错误条 (Error Bars) - 使用 aggregate
```json
{
  "name": "summary",
  "source": "data_a",
  "transform": [
    {
      "type": "aggregate",
      "groupby": ["pressure_bar"],
      "ops": ["mean", "stdev"],
      "fields": ["value", "value"],
      "as": ["mean_val", "stdev_val"]
    }
  ]
}
```
