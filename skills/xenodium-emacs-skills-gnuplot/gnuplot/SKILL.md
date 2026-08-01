---
name: gnuplot
description: >
  Gnuplot 科研绘图与数据可视化 skill。用于生成 gnuplot 脚本（.gp/.plt 文件）来绘制 2D/3D 图表、
  函数曲线、数据拟合、热力图、等高线图、矢量图、直方图、误差条图等。当用户需要：绘制科学图表、
  数据可视化、生成 gnuplot 代码、将数据文件绘制成图表、创建出版质量的科研图片、绘制数学函数、
  进行曲线拟合、制作多子图布局、设置坐标轴/刻度/图例/颜色样式时，都应使用此 skill。
  即使用户没有明确提到 gnuplot，只要涉及科学绘图、数据图表、函数可视化等需求，也应触发此 skill。
---

# Gnuplot 科研绘图 Skill

Gnuplot 是一个强大且轻量的命令行绘图工具，自 1986 年以来持续开发，广泛用于科研数据可视化。
它的优势在于：代码量少、输出质量高（支持 PDF/EPS/PNG 等出版格式）、跨平台、支持函数和数据绘图。

## 核心工作流

### 1. 理解用户需求

明确以下信息（缺失时主动询问）：
- **数据来源**：函数表达式、数据文件（CSV/TXT/DAT）、还是内联数据？
- **图表类型**：折线图、散点图、柱状图、3D 表面、热力图、等高线图、矢量图等？
- **输出格式**：PNG（屏幕查看）、PDF/EPS（出版投稿）、SVG（网页）？
- **尺寸要求**：默认 800x600 单屏图；出版图通常 8cm 或 16cm 宽；双栏图 18cm 宽。
- **特殊需求**：多子图、双 Y 轴、误差条、拟合、对数坐标、时间轴等。

### 2. 生成脚本的基本结构

每个 gnuplot 脚本应遵循这个模板顺序：

```gnuplot
# 1. 输出终端设置
set terminal pdfcairo size 16cm,12cm font 'Times New Roman,12'
set output "output.pdf"

# 2. 全局样式设置
set border lw 0.5
set style line 1 lc rgb '#e41a1c' lw 2 pt 7 ps 1.2
set style line 2 lc rgb '#377eb8' lw 2 pt 5 ps 1.2
set style line 3 lc rgb '#4daf4a' lw 2 pt 9 ps 1.2

# 3. 坐标轴与刻度
set xlabel "X Label" font ",14"
set ylabel "Y Label" font ",14"
set xrange [xmin:xmax]
set yrange [ymin:ymax]
set key top right box

# 4. 绘图命令（脚本末尾）
plot 'data.txt' using 1:2 with linespoints ls 1 title "Data"
```

### 3. 运行方式

```bash
# 方式 1：直接执行脚本
gnuplot script.gp

# 方式 2：交互式加载
gnuplot
gnuplot> load "script.gp"

# 方式 3：命令行内联（快速测试）
gnuplot -e "set terminal pngcairo; set output 'test.png'; plot sin(x)"
```

## 详细指南

根据用户需求，阅读对应的参考文件：

| 需求 | 参考文件 |
|------|---------|
| 2D 图表（折线、散点、柱状、误差条、填充、极坐标、参数方程） | `references/2d-plots.md` |
| 3D 图表（表面、等高线、热力图、矢量图、参数曲面） | `references/3d-plots.md` |
| 颜色、线条样式、点型、透明度、填充 | `references/styles.md` |
| 坐标轴、刻度、标签、图例、字体 | `references/axes-ticks.md` |
| 多子图布局、内嵌图、手动定位 | `references/layout.md` |
| 快速参考卡（常用命令速查） | `references/quickref.md` |

## 关键概念速查

### 终端（Terminal）选择

| 终端 | 用途 | 特点 |
|------|------|------|
| `pngcairo` | 屏幕查看、网页 | 支持透明、抗锯齿、dash 样式 |
| `pdfcairo` | 出版投稿 | 矢量格式，可无损缩放 |
| `epscairo` | LaTeX 投稿 | EPS 矢量格式 |
| `svg` | 网页交互 | 矢量，浏览器可编辑 |
| `qt` / `wxt` | 交互式预览 | 弹出窗口实时查看 |

### 缩写对照表

Gnuplot 大量使用缩写，常见对照：

| 全称 | 缩写 | 含义 |
|------|------|------|
| `with lines` | `w l` | 线条 |
| `with points` | `w p` | 散点 |
| `with linespoints` | `w lp` | 线条+散点 |
| `with boxes` | `w boxes` | 柱状 |
| `with impulses` | `w imp` | 脉冲/棒状 |
| `with errorbars` | `w err` | 误差条 |
| `with filledcurves` | `w filled` | 填充曲线 |
| `linetype` | `lt` | 线型 |
| `linewidth` | `lw` | 线宽 |
| `linecolor` | `lc` | 线色 |
| `pointtype` | `pt` | 点型 |
| `pointsize` | `ps` | 点大小 |
| `dashtype` | `dt` | 虚线样式 |
| `notitle` | `not` | 不显示图例 |

### 定义函数与拟合

```gnuplot
# 定义函数
f(x) = a*x + b
g(x) = a*exp(-((x-b)/c)**2)

# 拟合（fit 函数 数据文件 via 参数）
fit f(x) 'data.txt' using 1:2 via a, b
# 带误差权重的拟合
fit g(x) 'data.txt' using 1:2:3 yerror via a, b, c
```

### 数据文件格式

gnuplot 支持多种数据格式，最常见的是空格/制表符分隔的纯文本：

```
# 注释行以 # 开头
# 列之间用空格或制表符分隔
1.0  2.0  0.6
3.1  3.9  0.5
4.9  5.0  1.5
7.2  8.1  0.9
8.9  10.3 0.7
```

使用 `using` 语法选择列：`plot 'data.txt' using 1:2`（第 1 列为 x，第 2 列为 y）。
- `$1`, `$2` 等引用列值
- `$0` 是行号（从 0 开始）
- 可进行运算：`using 1:($2*100)` 将第 2 列乘以 100

### 统计功能

```gnuplot
stats 'data.txt' using 1:2 name "A"
# 之后可用 A_min_x, A_max_x, A_mean_x, A_stddev_x 等变量
```

### 多图模式

```gnuplot
set multiplot layout 2,2 spacing 0.1,0.15 margins 0.1,0.95,0.1,0.95
# ... 绘制 4 个子图 ...
unset multiplot
```

## 输出最佳实践

1. **出版质量**：使用 `pdfcairo` 或 `epscairo`，字体选 Times New Roman 或 Arial，字号 10-12pt。
2. **PPT/报告**：使用 `pngcairo`，分辨率至少 1000x800，字号 14-18pt。
3. **LaTeX**：使用 `epslatex` 或 `cairolatex` 终端，可直接嵌入 LaTeX 数学公式。
4. **中文支持**：设置 `set encoding utf8`，使用支持中文的字体（如 Sarasa Term SC、Noto Sans CJK）。
5. **脚本化**：将绘图命令保存为 `.gp` 文件，便于版本控制和复用。
