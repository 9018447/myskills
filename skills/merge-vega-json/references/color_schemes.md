# Vega 颜色方案参考

## 分类色板（适用于离散分类数据，如不同温度或数据集）

在合并多个数据集时，建议使用分类色板区分不同数据集：

| 方案名 | 颜色数 | 描述 |
|---|---|---|
| `category10` | 10 | 经典10色，d3 默认 |
| `tableau10` | 10 | Tableau 配色，视觉均衡 |
| `tableau20` | 20 | 20种不同颜色 |
| `set1` | 9 | 鲜明对比色 |
| `set2` | 8 | 柔和色调 |
| `dark2` | 8 | 深色系，适合白底背景 |
| `paired` | 12 | 成对配色（深浅对） |
| `pastel1` | 9 | 淡色，适合背景填充 |

### 使用示例（ordinal scale）：
```json
{
  "name": "color",
  "type": "ordinal",
  "domain": {"data": "data_a", "field": "temperature_K"},
  "range": {"scheme": "tableau10"}
}
```

---

## 连续色板（适用于连续数值映射）

| 方案名 | 类型 | 描述 |
|---|---|---|
| `viridis` | 多色渐变 | 感知均匀，色盲友好 |
| `plasma` | 多色渐变 | 高对比度 |
| `inferno` | 多色渐变 | 暗色系 |
| `magma` | 多色渐变 | 紫-橙 |
| `blues` | 单色渐变 | 蓝色深浅 |
| `reds` | 单色渐变 | 红色深浅 |
| `greens` | 单色渐变 | 绿色深浅 |
| `oranges` | 单色渐变 | 橙色深浅 |
| `purples` | 单色渐变 | 紫色深浅 |
| `greys` | 单色渐变 | 灰色深浅 |
| `tealblues` | 双色渐变 | 蓝绿-蓝 |

### 使用示例（linear scale）：
```json
{
  "name": "color",
  "type": "linear",
  "domain": {"data": "data_a", "field": "temperature_K"},
  "range": {"scheme": "viridis"},
  "zero": false
}
```

---

## 发散色板（适用于有正/负或中心点的数据）

| 方案名 | 描述 |
|---|---|
| `redblue` | 红-白-蓝 |
| `redyellowblue` | 红-黄-蓝 |
| `spectral` | 彩虹色 |
| `piyg` | 粉-白-绿 |
| `rdylgn` | 红-黄-绿 |

---

## 手动指定颜色数组

```json
"range": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"]
```

或者使用 HCL 插值：
```json
{
  "name": "color",
  "type": "linear",
  "range": {"scheme": "blues"},
  "interpolate": "hcl"
}
```
