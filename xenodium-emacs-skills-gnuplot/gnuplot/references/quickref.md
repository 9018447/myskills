# Gnuplot 快速参考卡

## 输出终端

| 终端 | 命令 | 用途 |
|------|------|------|
| PNG 图片 | `set terminal pngcairo size 800,600 font 'Arial,12'` | 屏幕/网页 |
| PDF | `set terminal pdfcairo size 16cm,12cm font 'Times,12'` | 出版 |
| EPS | `set terminal epscairo size 8cm,6cm` | LaTeX 投稿 |
| SVG | `set terminal svg size 800,600` | 网页可编辑 |
| 交互窗口 | `set terminal qt` | 实时预览 |

## 2D 绘图类型

```gnuplot
plot ... with lines          # 折线图
plot ... with points         # 散点图
plot ... with linespoints    # 线+点
plot ... with boxes          # 柱状图
plot ... with impulses       # 脉冲图
plot ... with steps          # 阶梯图
plot ... with histeps        # 直方图阶梯
plot ... with errorbars      # 误差条
plot ... with filledcurves   # 填充曲线
plot ... with circles        # 圆圈图
plot ... with vectors        # 矢量图
plot ... with labels         # 标签
plot ... with image          # 图像
```

## 3D 绘图类型

```gnuplot
splot ... with lines         # 网格线
splot ... with pm3d          # 彩色表面
splot ... with points        # 3D 散点
splot ... with vectors       # 3D 矢量
splot ... with impulses      # 3D 脉冲
splot ... with labels        # 3D 标签
```

## 线型简写

| 全称 | 缩写 | 全称 | 缩写 |
|------|------|------|------|
| `with` | `w` | `linetype` | `lt` |
| `linewidth` | `lw` | `linecolor` | `lc` |
| `pointtype` | `pt` | `pointsize` | `ps` |
| `dashtype` | `dt` | `notitle` | `not` |
| `pointinterval` | `pi` | `linespoints` | `lp` |

## 坐标轴设置

```gnuplot
set xrange [min:max]
set yrange [min:max]
set xlabel "text"
set ylabel "text"
set y2label "text"           # 右侧 Y 轴
set ytics nomirror           # Y 轴刻度不镜像
set y2tics start, step       # 右侧 Y 轴刻度
set log x                    # 对数 X 轴
set log y                    # 对数 Y 轴
set xdata time               # 时间轴
set timefmt "%Y-%m-%d"       # 时间输入格式
set format x "%m/%d"         # 时间输出格式
```

## 刻度控制

```gnuplot
set mxtics 4                 # X 轴副刻度数
set mytics 4                 # Y 轴副刻度数
set tics scale 3             # 刻度长度
set tics out                 # 刻度朝外
set xtics ("label" value, ...)  # 自定义标签
set xtics add ("label" value)   # 追加标签
```

## 图例设置

```gnuplot
set key top right            # 位置
set key outside              # 图外
set key box                  # 加边框
set key reverse              # 符号在左
set key font ",14"           # 字体
set key spacing 1.5          # 行距
unset key                    # 隐藏
```

## 样式与颜色

```gnuplot
set style line N lc rgb 'color' lw W dt D pt P ps S
set style fill solid 0.5     # 实心填充
set style fill pattern N     # 图案填充
set style data histograms    # 柱状图模式
set style histogram rowstacked  # 堆叠柱状图
set boxwidth 0.8             # 柱宽
set pointsize 2              # 全局点大小
set palette defined (0 'blue', 1 'red')  # 调色板
```

## 多图布局

```gnuplot
set multiplot layout rows,cols spacing dx,dy
# ...
unset multiplot
```

## 数据文件操作

```gnuplot
# 基本读取
plot 'file.txt' using 1:2

# CSV 文件
set datafile separator ","
plot 'file.csv' using 1:2

# 列运算
plot 'file.txt' using 1:($2*100)

# 跳过行
plot 'file.txt' every ::5       # 跳过前 5 行
plot 'file.txt' every 2         # 每隔一行

# 统计
stats 'file.txt' using 1 name "A"
# A_min, A_max, A_mean, A_stddev, A_min_x, A_max_x ...
```

## 拟合

```gnuplot
f(x) = a*x + b
fit f(x) 'data.txt' using 1:2 via a, b
# 带误差
fit f(x) 'data.txt' using 1:2:3 yerror via a, b
```

## 常用内置函数

| 函数 | 说明 | 函数 | 说明 |
|------|------|------|------|
| `sin(x)` | 正弦 | `cos(x)` | 余弦 |
| `tan(x)` | 正切 | `exp(x)` | 指数 |
| `log(x)` | 自然对数 | `log10(x)` | 常用对数 |
| `sqrt(x)` | 平方根 | `abs(x)` | 绝对值 |
| `atan2(y,x)` | 反正切 | `erf(x)` | 误差函数 |
| `erfc(x)` | 补误差函数 | `besj0(x)` | 贝塞尔 J0 |
| `besj1(x)` | 贝塞尔 J1 | `besy0(x)` | 贝塞尔 Y0 |
| `rand(x)` | 随机数 | `ceil(x)` | 向上取整 |
| `floor(x)` | 向下取整 | `int(x)` | 截断取整 |

## 变量与宏

```gnuplot
# 变量
a = 10
b = "hello"

# 宏（字符串变量用 @ 引用）
sx = "set xrange "
@sx [0:10]     # 等价于 set xrange [0:10]

# sprintf 格式化字符串
key_str = sprintf("y = %.3fx + %.3f", a, b)
```

## 注释与箭头

```gnuplot
set label "text" at x,y
set arrow from x1,y1 to x2,y2
set object circle at x,y size r
set object rect from x1,y1 to x2,y2
```

## 网格

```gnuplot
set grid                  # 基本网格
set grid xtics ytics mxtics mytics  # 指定网格
set grid lw 0.5 lt 0 lc rgb '#ccc'  # 网格样式
set grid back             # 网格在后面
```
