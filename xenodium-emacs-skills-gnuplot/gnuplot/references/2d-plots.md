# 2D 绘图参考

## 目录
1. [基本函数绘图](#基本函数绘图)
2. [数据文件绘图](#数据文件绘图)
3. [散点图](#散点图)
4. [柱状图与直方图](#柱状图与直方图)
5. [误差条图](#误差条图)
6. [填充曲线](#填充曲线)
7. [脉冲图/棒状图](#脉冲图棒状图)
8. [双 Y 轴图](#双-y-轴图)
9. [极坐标绘图](#极坐标绘图)
10. [参数方程曲线](#参数方程曲线)
11. [曲线拟合](#曲线拟合)
12. [圆圈图](#圆圈图)

---

## 基本函数绘图

```gnuplot
# 直接绘制内置函数
plot sin(x), cos(x)

# 指定范围
plot [0:10] sin(x)/x

# 自定义函数
f(x) = a*x**2 + b*x + c
a = 1; b = -2; c = 3
plot [-5:5] f(x)

# 多条曲线，每条指定样式
plot [-pi:pi] sin(x) w l lw 2 lc rgb 'red' title "sin", \
             cos(x) w l lw 2 lc rgb 'blue' title "cos"
```

## 数据文件绘图

```gnuplot
# 基本用法：第 1 列为 x，第 2 列为 y
plot 'data.txt' using 1:2 with lines

# 指定分隔符（如 CSV）
set datafile separator ","
plot 'data.csv' using 1:2 with points

# 跳过注释行（默认 # 开头的行被忽略）
plot 'data.txt' using 1:2

# 选择特定列，进行运算
plot 'data.txt' using 1:($2/$3) with lines  # 第 2 列除以第 3 列

# 多个数据文件
plot 'file1.txt' using 1:2 w l title "Set A", \
     'file2.txt' using 1:2 w l title "Set B"

# 使用 '+' 虚拟文件（自动生成 x 采样值）
plot [0:10] '+' using 1:(sin($1)):(cos($1)) with circles
```

## 散点图

```gnuplot
# 基本散点图
plot 'data.txt' using 1:2 with points pt 7 ps 1.5

# 常用点型 (pt)
# pt 1: +    pt 2: x    pt 3: *    pt 4: 空心方框
# pt 5: 实心方框  pt 6: 空心圆  pt 7: 实心圆  pt 8: 三角
# pt 9: 倒三角  pt 10: 菱形  pt 11: 五角星  pt 12: 十字

# 按第 3 列值着色的散点图
plot 'data.txt' using 1:2:3 with points pt 7 ps 2 palette

# 三维散点（2D 投影，用颜色表示 z）
set view map
splot 'data.txt' using 1:2:3 with points pt 7 ps 2 palette
```

## 柱状图与直方图

```gnuplot
# 基本柱状图
set style fill solid 0.8 border lt -1
set boxwidth 0.8
plot 'data.txt' using 1:2 with boxes

# 并排直方图（多组数据）
set style data histograms
set style fill solid 1.0 border lt -1
set boxwidth 0.9
plot 'data.txt' using 2, '' using 3

# 堆叠直方图
set style data histograms
set style histogram rowstacked
set style fill solid 1.0 border lt -1
plot 'data.txt' using 2, '' using 3

# 自定义 x 轴标签
set xtics ("Group A" 0, "Group B" 1, "Group C" 2, "Group D" 3)

# 带数据标签的柱状图
set style fill solid 0.8
plot 'data.txt' using 1:2 with boxes, \
     '' using 0:($2+0.3):2 with labels notitle
```

## 误差条图

```gnuplot
# Y 误差条（数据格式: x y ydelta 或 x y ylow yhigh）
plot 'data.txt' using 1:2:3 with yerrorbars pt 7 ps 1.2 lw 2

# XY 误差条（数据格式: x y xdelta ydelta）
plot 'data.txt' using 1:2:3:4 with xyerrorbars pt 7 ps 1.2

# 箱形误差条（填充背景）
set style fill pattern 2 border lt -1
plot 'data.txt' using 1:2:3 with boxerrorbars

# 误差条宽度控制
set bars 3  # 误差条横线宽度
```

## 填充曲线

```gnuplot
# 填充到 y=0
set style fill solid 0.5
plot [0:20] besy0(x) with filledcurves above y1=0 lc rgb 'seagreen'

# 两条曲线之间的填充
set style fill transparent solid 0.3
plot [0:pi] sin(x)**2 with filledcurves above y1=0 lc rgb '#00ffff', \
     0.75*cos(2*x)**2 with filledcurves above y1=0 lc rgb '#aa00aa'

# 使用虚拟文件填充两线之间
set style fill pattern 5
plot [0:1] '+' using 1:(-$1):(-$1**2) with filledcurves, \
     -x lw 3 notitle, -x**2 lw 3 notitle

# 填充到指定 y 值
plot 'data.txt' using 1:2 with filledcurves y=2 lc rgb 'seagreen'
```

## 脉冲图/棒状图

```gnuplot
# 基本脉冲图
set samples 30
plot [0:2*pi] sin(x) with impulses lw 2

# 带点的脉冲图
plot [0:2*pi] sin(x) with impulses lw 2, \
     sin(x) with points pt 7 ps 1.5 notitle
```

## 双 Y 轴图

```gnuplot
# 设置第二 Y 轴
set y2tics -100, 20
set ytics nomirror  # 不镜像到右边
set y2label "Second Axis"

# 分配曲线到不同轴
plot sin(1/x) axis x1y1 with lines title "Left Y", \
     100*cos(x) axis x1y2 with lines title "Right Y"
```

## 极坐标绘图

```gnuplot
# 启用极坐标
set polar
set size ratio 1
set xtics axis nomirror
set ytics axis nomirror
set zeroaxis
unset border
set samples 500

# 心形线
plot [0:2*pi] 4*(1-sin(t))

# 螺旋线
plot [0:6*pi] t/10
```

## 参数方程曲线

```gnuplot
# 启用参数模式
set parametric
set samples 1000

# Lissajous 曲线
plot [0:2*pi] sin(7*t), cos(11*t)

# 圆
plot [0:2*pi] cos(t), sin(t)

# 3D 参数曲线
set parametric
set urange [-pi:pi]
splot cos(u), sin(3*u), cos(5*u) lw 2
```

## 曲线拟合

```gnuplot
# 线性拟合
f(x) = a*x + b
fit f(x) 'data.txt' using 1:2 via a, b
plot 'data.txt' using 1:2, f(x)

# 二次拟合
g(x) = a*x**2 + b*x + c
fit g(x) 'data.txt' using 1:2 via a, b, c

# 带误差权重的拟合（第 3 列为 y 误差）
fit g(x) 'data.txt' using 1:2:3 yerror via a, b, c

# 高斯拟合
gauss(x) = a*exp(-((x-mu)/sigma)**2/2)
fit gauss(x) 'spectrum.txt' using 1:2 via a, mu, sigma

# 在图例中显示拟合参数
key_str = sprintf("y = %.3fx + %.3f", a, b)
plot 'data.txt' title "Data", f(x) title key_str
```

## 圆圈图

```gnuplot
# 圆圈图需要 3 列：x y radius
plot '+' using 1:(sin($1)):(cos($1)+1) with circles

# 气泡图（用颜色表示第 4 维）
plot 'data.txt' using 1:2:3:4 with circles palette
```
