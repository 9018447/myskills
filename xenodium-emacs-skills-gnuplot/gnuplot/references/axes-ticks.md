# 坐标轴、刻度与标签参考

## 目录
1. [坐标轴范围](#坐标轴范围)
2. [坐标轴标签](#坐标轴标签)
3. [图例 (Key/Legend)](#图例-keylegend)
4. [主刻度与副刻度](#主刻度与副刻度)
5. [自定义刻度标签](#自定义刻度标签)
6. [时间轴](#时间轴)
7. [对数坐标](#对数坐标)
8. [刻度格式化](#刻度格式化)
9. [网格](#网格)
10. [边框](#边框)

---

## 坐标轴范围

```gnuplot
# 设置范围
set xrange [0:100]
set yrange [-0.5:1.0]
set zrange [0:10]

# 在 plot 命令中指定范围（优先级更高）
plot [0:10][-1:1] sin(x)

# 自动范围（默认）
set autoscale x
set autoscale y

# 部分自动
set xrange [0:*]  # x 最小值为 0，最大值自动
```

## 坐标轴标签

```gnuplot
# 基本标签
set xlabel "X Axis Label"
set ylabel "Y Axis Label"
set zlabel "Z Axis Label"
set title "Plot Title"

# 字体设置
set xlabel "Label" font ",18"
set ylabel "Label" font "Arial,14"
set title "Title" font "Times New Roman,20"

# 多行标题（手动换行）
set title "Line 1\nLine 2"

# 标签旋转
set xlabel "rotated" rotate by 45
set ylabel "vertical" rotate by 90  # 竖排

# 偏移（避免与刻度重叠）
set xlabel "offset" offset 0,-1

# Unicode/中文标签
set encoding utf8
set title "中文标题" font "Sarasa Term SC,18"

# 使用数学符号
set xlabel "Pressure {/Symbol a} (Pa)"
set ylabel "X^2_3 with subscripts"
# {/Symbol ...} 使用 Symbol 字体
# {/=14 Big text} 改变局部字号
```

## 图例 (Key/Legend)

```gnuplot
# 位置设置
set key top left          # 左上
set key top right         # 右上
set key bottom left       # 左下
set key bottom right      # 右下
set key center            # 居中
set key outside           # 图外

# 精确定位（使用坐标系）
set key at graph 0.4, 0.95   # graph 坐标系（0-1）
set key at first 5, 100      # 数据坐标系

# 外观设置
set key box lt -1 lw 2       # 加边框
set key Left                  # 文本左对齐
set key reverse               # 图例符号在文本左边
set key spacing 1.5           # 行间距
set key font ",14"            # 字体
set key width 3               # 文本宽度（字符数）
set key samplen 4             # 示例线长度

# 隐藏图例
unset key
# 或在 plot 时指定
plot sin(x) notitle

# 图例在图外（适合图例多的情况）
set key outside right top
```

## 主刻度与副刻度

```gnuplot
# 副刻度（每个主刻度之间的细分数量）
set mxtics 4    # x 轴每个主刻度 4 个副刻度
set mytics 2    # y 轴每个主刻度 2 个副刻度

# 第二坐标轴的刻度
set ytics nomirror    # 不镜像到右边
set y2tics 0.4        # y2 轴主刻度间距
set my2tics 4         # y2 轴副刻度

# 刻度长度调整
set tics scale 3      # 主刻度长度为默认 3 倍
set tics scale 3,1.5  # 主刻度 3 倍，副刻度 1.5 倍

# 刻度方向
set tics out           # 刻度朝外
set tics in            # 刻度朝内（默认）

# 移除所有刻度
unset tics
# 或
set notics

# 移除单个轴的刻度
unset xtics
unset ytics
```

## 自定义刻度标签

```gnuplot
# 手动指定刻度标签
set xtics ("{/Symbol p}" pi, "{/Symbol p}/2" pi/2, \
    "2{/Symbol p}" 2*pi, "3{/Symbol p}/2" 3*pi/2, "0" 0)

# 添加额外标签（不覆盖已有的）
set xtics add ("{/Symbol p}/4" pi/4)

# 等间隔自定义标签
set xtics ("A" 0, "B" 1, "C" 2, "D" 3, "E" 4)

# 极坐标刻度
set rtics 0,2,10    # 起始, 间隔, 终点
set ttics 30         # 角度刻度每 30 度
```

## 时间轴

```gnuplot
# 告诉 gnuplot x 轴是时间数据
set xdata time
set timefmt "%d/%m/%Y %H:%M"  # 输入格式
set format x "%d/%m/%y"        # 输出格式

# 旋转标签避免重叠
set xtics rotate by -30
set rmargin 7

# 地域设置（中文月份等）
set locale "zh_CN.utf8"
set timefmt "%d/%m/%Y %H:%M"
set format x "%Y年%b"

# 常用时间格式
# %Y = 四位年    %y = 两位年
# %m = 两位月    %b = 月份缩写
# %d = 两位日    %H = 24小时
# %M = 分钟      %S = 秒
```

## 对数坐标

```gnuplot
# 设置对数轴
set log x          # x 轴对数
set log y          # y 轴对数
set log xy         # 双对数

# 指定对数底数（默认 10）
set logscale x 2   # 以 2 为底

# 取消对数
unset logscale x
```

## 刻度格式化

```gnuplot
# 格式化刻度文本
set format y "P = %.2f Watts"
set format x "%.3f%%"      # 百分号需要双写

# 隐藏刻度标签（保留刻度线）
set format y ""
set format x ""

# 科学计数法
set format y "%.1e"
set format y "%g"    # 自动选择格式

# 数字分隔符
set decimalsign locale "zh_CN.utf8"
set decimalsign ","   # 手动指定
```

## 网格

```gnuplot
# 启用网格
set grid

# 网格线样式
set grid lw 0.5 lt 0 lc rgb '#cccccc'   # 浅灰色
set grid back    # 网格在数据后面

# 只在主刻度或副刻度画网格
set grid xtics ytics mxtics mytics

# 极坐标网格
set grid polar
```

## 边框

```gnuplot
# 边框设置（1=下, 2=左, 4=上, 8=右，可组合）
set border 15     # 四边都画（默认）
set border 3      # 只画下和左
unset border      # 无边框

# 边框线宽
set border lw 0.5

# 边框样式
set border back   # 边框在数据后面
set border front  # 边框在数据前面
```
