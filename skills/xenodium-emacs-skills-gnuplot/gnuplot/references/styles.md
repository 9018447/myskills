# 颜色与样式参考

## 目录
1. [曲线颜色](#曲线颜色)
2. [自定义线条样式](#自定义线条样式)
3. [点型与 linespoints](#点型与-linespoints)
4. [透明度](#透明度)
5. [填充样式](#填充样式)
6. [虚线样式](#虚线样式)
7. [绘制对象](#绘制对象)
8. [调色板](#调色板)

---

## 曲线颜色

```gnuplot
# 使用颜色名称
plot [0:1] x**0.5 lc rgb 'orange', x lc rgb 'steelblue', \
     x**2 lc rgb 'bisque', x**3 lc rgb '#2e8b57'

# 使用十六进制颜色（需要单引号）
plot sin(x) lc rgb '#FF5733'

# 使用颜色序号（lt = linetype）
plot sin(x) lt 1, cos(x) lt 2, tan(x) lt 3

# 查看所有可用颜色
# 在 gnuplot 交互模式下输入：show colors
```

常用颜色名：`red`, `blue`, `green`, `orange`, `purple`, `cyan`, `magenta`, `yellow`, `black`, `white`, `gray`, `dark-gray`, `light-gray`, `coral`, `salmon`, `gold`, `aquamarine`, `seagreen`, `steelblue`, `navy`, `violet`, `pink`, `brown`

## 自定义线条样式

```gnuplot
# 定义样式（ls = line style）
set style line 1 dashtype 2 lw 4 lc rgb '#990042'
set style line 2 dashtype 3 lw 3 lc rgb '#31f120'
set style line 3 dashtype 4 lw 3 lc rgb '#0044a5'
set style line 4 dashtype 5 lw 4 lc rgb '#888888'

# 使用样式
plot [0:1] x**0.5 ls 1, x ls 2, x**2 ls 3, x**3 ls 4

# 自动循环使用用户样式
set style increment userstyles
# 恢复默认
set style increment default

# 全局线宽设置（影响所有元素）
set term pngcairo lw 4
# 重新设置边框和刻度线宽
set border lw 0.25
```

## 点型与 linespoints

```gnuplot
# 带点的线
plot sin(x)/x with linespoints pointsize 2 pointtype 6 lw 2

# 定制 linespoints 样式
set style function linespoints
# pi = pointinterval：每隔多少个采样点放置一个 marker
set style line 1 lw 4 lc rgb '#990042' ps 2 pt 6 pi 5
set style line 2 lw 3 lc rgb '#31f120' ps 2 pt 12 pi 3
set style line 3 lw 3 lc rgb '#0044a5' ps 2 pt 9 pi 5
set style line 4 lw 4 lc rgb '#888888' ps 2 pt 7 pi 4

plot [0:1] x**0.5 ls 1, x ls 2, x**2 ls 3, x**3 ls 4
```

常用点型 (pointtype / pt)：
| pt | 形状 | pt | 形状 |
|----|------|----|------|
| 1  | +    | 7  | 实心圆 |
| 2  | ×    | 8  | 空心三角 |
| 3  | *    | 9  | 实心三角 |
| 4  | 空心方框 | 10 | 倒三角 |
| 5  | 实心方框 | 11 | 菱形 |
| 6  | 空心圆 | 12 | 十字 |

## 透明度

```gnuplot
# 透明填充（0=全透明, 1=不透明）
set style fill transparent solid 0.3
plot [0:pi] sin(x)**2 with filledcurves above y1=0 lc rgb '#00ffff', \
     0.75*cos(2*x)**2 with filledcurves above y1=0 lc rgb '#aa00aa'

# 透明图案填充
set style fill transparent pattern 3

# 透明线条（在颜色后加透明度，0-255）
plot sin(x) lc rgb '#FF000080'  # 50% 透明的红色
```

## 填充样式

```gnuplot
# 实心填充
set style fill solid 0.5 border lt -1

# 图案填充
set style fill pattern 1  # pattern 编号 1-13

# 空心（不填充）
set style fill empty

# 柱状图专用
set style fill solid 1.0 border lt -1
set boxwidth 0.8
```

## 虚线样式

```gnuplot
# 使用 dashtype（仅 pngcairo/pdfcairo 等支持）
set style line 1 dt 1 lw 2  # 短划线
set style line 2 dt 2 lw 2  # 点线
set style line 3 dt 3 lw 2  # 点划线
set style line 4 dt 4 lw 2  # 长划线
set style line 5 dt 5 lw 2  # 短划点划线

# 自定义虚线模式（dash:gap 比例）
set style line 1 dt (5,3) lw 2      # 5 单位划线, 3 单位间隔
set style line 2 dt (10,3,2,3) lw 2 # 自定义模式

# 也可以在 plot 时直接指定
plot sin(x) dashtype '--' lw 2
```

## 绘制对象

```gnuplot
# 画圆
set object 1 circle at graph 0.5,0.5 size graph 0.25 \
    fillcolor rgb 'blue' fillstyle solid arc [0:30] front

# 画矩形
set object 1 rect from screen 0.1,0.1 to screen 0.3,0.3 \
    fillcolor rgb 'lightblue' fillstyle solid

# 画箭头
set arrow 1 from first 8, 1.5 to pi*7/4, 1 lt -1 lw 2 front size 0.3,15
# arrow style 定义
set style arrow 1 head filled size screen 0.03,15,135 lt 2 lw 2

# 画标签
set label "annotation" at graph 0.5,0.5 center font ",16"
```

## 调色板

```gnuplot
# 预定义调色板
set palette defined (0 'blue', 0.5 'white', 1 'red')

# 多色渐变
set palette defined (0 'black', 0.33 'blue', 0.66 'yellow', 1 'red')

# 使用内置颜色模型
set palette model RGB defined (0 '#0000ff', 1 '#ff0000')

# HSV 模型
set palette model HSV defined (0 0 1 1, 1 1 1 1)

# 查看调色板效果
# test palette  # 会显示当前调色板的色条

# 颜色条设置
set colorbox
set cblabel "Color Label"
set cbrange [min:max]
```
