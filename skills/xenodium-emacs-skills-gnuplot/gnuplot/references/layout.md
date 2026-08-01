# 多子图布局参考

## 目录
1. [自动布局 (multiplot layout)](#自动布局-multiplot-layout)
2. [手动定位子图](#手动定位子图)
3. [内嵌子图](#内嵌子图)
4. [子图中的标签与箭头](#子图中的标签与箭头)
5. [子图间距与边距](#子图间距与边距)

---

## 自动布局 (multiplot layout)

```gnuplot
# 最常用：2x2 网格布局
set multiplot layout 2,2

# key 放在顶部边距
set key tmargin left box lt -1
plot besj0(x)
plot besj1(x)
plot besy0(x)
plot besy1(x)

unset multiplot
```

```gnuplot
# 带标题和间距的布局
set multiplot layout 2,2 title "My Plots" font ",22" \
    spacing 0.1,0.15 margins 0.1,0.95,0.1,0.95
# margins 的四个值：left, right, bottom, top

# 每个子图需要 reset 或重新设置参数
set title "Plot 1"
plot sin(x)

set title "Plot 2"
plot cos(x)

# ...继续绘制其他子图...
unset multiplot
```

## 手动定位子图

```gnuplot
# 使用 origin 和 size 精确控制位置
set multiplot
unset key
unset tics

# 第一个子图：占上半部分
set size 1, 0.5
set origin 0, 0.5
plot [0:10] sin(x)

# 第二个子图：左下 1/4
set origin 0, 0
set size 0.5, 0.5
plot [0:10] cos(x)

# 第三个子图：右下 1/4
set origin 0.5, 0
set size 0.5, 0.5
plot [0:10] tan(x)

unset multiplot
```

## 内嵌子图

```gnuplot
# 在一个图中嵌入放大细节
set multiplot

# 主图
set samples 1000
set grid
set xtics 0.4
set ytics 10
plot [0:2*pi] exp(x)*sin(1/x)

# 内嵌放大图（使用 origin + size 定位）
reset
set origin 0.2, 0.4
set size 0.4, 0.4
clear                     # 清除子图区域内的内容
set sample 1000
set nokey
set xtics 0.1
set ytics 0.5
set bmargin 1
set tmargin 1
set lmargin 3
set rmargin 1
plot [0:0.2] exp(x)*sin(1/x)

unset multiplot
```

## 子图中的标签与箭头

```gnuplot
# 在多子图中添加跨子图的箭头连接
set xrange [-pi:pi]
set ytics 0.5
unset key
set multiplot layout 2,2 title "Derivatives of Sin(x)" font ",22"

# 定义箭头样式
set style arrow 1 head filled size screen 0.03,15,135 lt 2 lw 2
# screen 坐标系中的箭头（跨子图连接）
set arrow 1 from screen 0.41,0.74 to screen 0.65,0.74 arrowstyle 1
set arrow 2 from screen 0.87,0.64 to screen 0.87,0.3 arrowstyle 1
set arrow 3 from screen 0.7,0.15 to screen 0.4,0.15 arrowstyle 1
set arrow 4 from screen 0.35,0.35 to screen 0.35,0.7 arrowstyle 1

set title "sin(x)"
plot sin(x)

set title "sin'(x) = cos(x)"
plot cos(x)

set title "sin'''(x) = -cos(x)"
plot -cos(x)

set title "sin''(x) = -sin(x)"
plot -sin(x)

unset multiplot
```

## 子图间距与边距

```gnuplot
# 使用变量控制边距（方便统一调整）
left = 0.1
right = 0.95
bottom = 0.1
top = 0.95
hspace = 0.1     # 水平间距
wspace = 0.15    # 垂直间距

set multiplot layout 2,2 \
    spacing hspace,wspace \
    margins left,right,bottom,top

# 子图内边距（影响坐标轴与子图边界的关系）
set lmargin 5    # 左边距（字符宽度）
set rmargin 2    # 右边距
set tmargin 2    # 上边距
set bmargin 3    # 下边距
```

## 子图标签技巧

```gnuplot
# 给每个子图加编号标签 (1) (2) (3) (4)
set label "(1)" at graph 0.02,0.03 font ',20' textcolor rgb 'red'

# graph 坐标系 (0-1) 适合定位在子图角落
# at graph 0.02, 0.03 = 左下角
# at graph 0.98, 0.97 = 右上角

# 使用 reset 清除前一个子图的设置
reset
# reset 会清除所有设置，包括变量
# 如果需要保留变量，使用 unset 逐个清除
```
