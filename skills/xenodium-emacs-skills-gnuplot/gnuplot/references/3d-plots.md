# 3D 绘图参考

## 目录
1. [基本 3D 表面](#基本-3d-表面)
2. [表面上色 (pm3d)](#表面上色-pm3d)
3. [等高线图](#等高线图)
4. [热力图](#热力图)
5. [热力图+等高线](#热力图等高线)
6. [热力图+表面](#热力图表面)
7. [矢量图](#矢量图)
8. [参数方程 3D](#参数方程-3d)
9. [坐标映射](#坐标映射)
10. [视角与渲染](#视角与渲染)

---

## 基本 3D 表面

```gnuplot
# 设置采样密度
set isosamples 40
unset key

# 隐藏被遮挡的线条
set hidden3d

# 设置范围和视角
set xrange [-4:4]
set yrange [-4:4]
set ztics 1
set view 29,53  # 仰角, 方位角

# splot 是 3D 绘图命令
splot besj0(x**2 + y**2)

# 从数据文件绘制 3D 表面
# 数据格式：x y z，空行分隔不同的 y 值（网格格式）
splot 'grid_data.txt' using 1:2:3 with lines
```

## 表面上色 (pm3d)

```gnuplot
# 纯色表面（隐藏线 + 颜色填充）
set iso 100
set samp 100
unset key
unset surface
set pm3d
set view 29,53

splot besj0(x**2 + y**2)

# 带线条的彩色表面
set iso 30
set samp 30
set style line 1 lt 4 lw 0.5
set pm3d at s hidden3d 1
set view 29,53
splot besj0(x**2 + y**2)

# 自定义调色板
set palette defined (0 'blue', 0.5 'white', 1 'red')

# 使用 depthorder 渲染参数曲面（按距离排序颜色）
set pm3d depthorder
splot cos(u)*cos(v), sin(u)*cos(v), sin(u) with pm3d
```

## 等高线图

```gnuplot
# 纯等高线图（俯视投影）
set cntrparam levels 10    # 等高线数量
set contour base            # 在底面绘制
unset surface
set view map                # 俯视角度
set xrange [-4:4]
set yrange [-4:4]
set iso 100
set samp 100
set key rmargin

splot sin(x) + cos(2*y)

# 等高线叠加在表面上
set cntrparam levels 10
set contour both            # 表面和底面都画
set hidden3d
set view 60,30
set style line 1 lc rgb '#cccccc'
splot sin(x) + cos(2*y) with lines ls 1
```

## 热力图

```gnuplot
# 基本热力图（俯视 pm3d）
set xrange [-4:4]
set yrange [-4:4]
set iso 100
set samp 100
unset key
unset surface
set view map
set pm3d at b              # at b = 在底部渲染

splot sin(y**2 + x**2) - cos(x**2)

# 自定义调色板（两色渐变）
set palette defined (0 'black', 1 'gold')
replot

# 多色渐变
set palette defined (0 'black', 1 'aquamarine', 1.5 'red', 2 'gold')
replot
```

## 热力图+等高线

```gnuplot
set xrange [0:pi]
set yrange [0:pi]
set iso 200
set samp 200
set cntrparam levels 10
unset key
unset surface
set view map
set contour base
set pm3d at b

# 4 列数据：x y z_for_contour z_for_color
splot '++' using 1:2:($1**2-$2**2):(sin($1**2+$2**2)) with lines lw 2
```

## 热力图+表面

```gnuplot
set iso 40
set samp 40
unset key
set xrange [-pi:pi]
set yrange [-pi:pi]
f(x,y) = sin(x)*cos(y)

# hidden front 使 surface 最后绘制，不被热图覆盖
set hidden front
set xyplane at -1          # xy 平面下移到 z=-1

splot f(x,y) with pm3d at b, f(x,y) with lines
```

## 矢量图

```gnuplot
# 2D 矢量场（需要 4 列：x y dx dy）
set xrange [0:pi]
set yrange [0:pi]
set iso 60
set samp 60
unset key
a = 0.2
plot '++' using 1:2:(-a*sin($1)*cos($2)):(a*cos($1)*sin($2)) \
     with vectors size 0.06,15 filled

# 3D 矢量场（需要 6 列：x y z dx dy dz）
set xrange [-pi:pi]
set yrange [-pi:pi]
set zrange [-pi:pi]
unset key
set iso 50
set samp 20
set view 37,300
a = 0.9
splot '++' using 1:2:(2*a*cos($2)*sin($1)): \
      (-a*sin($1)*cos($2)):(a*cos($1)*sin($2)):(a*cos($1)) \
      with vectors size 0.06,15 filled
```

## 参数方程 3D

```gnuplot
# 3D 参数曲线
set parametric
set samp 100
set urange [-pi:pi]
splot cos(u), sin(3*u), cos(5*u) lw 2

# 参数曲面（需要两个参数 u, v）
set parametric
set iso 50
set urange [-pi:pi]
set vrange [-pi:pi]
set hidden3d
set view 50,60

# 球面
splot cos(u)*cos(v), sin(u)*cos(v), sin(u)

# 莫比乌斯带
set urange [-pi:pi]
set vrange [-0.3:0.3]
splot (1 + v/2 * cos(u/2)) * cos(u), \
      (1 + v/2 * cos(u/2)) * sin(u), \
      v/2 * sin(u/2)
```

## 坐标映射

```gnuplot
# 圆柱坐标系
set mapping cylindrical
set hidden
unset border
unset tics
set xrange [-pi:pi]
set yrange [-pi:pi]
set zrange [0:pi]
set iso 60
unset key
set view 90,0
splot '++' using 1:2:(sin($2)) with lines

# 球坐标系
set mapping spherical
```

## 视角与渲染

```gnuplot
# 设置视角：仰角, 方位角
set view 60,30

# 交互式旋转（在交互模式下）
# 用鼠标拖动旋转

# 网格密度
set isosamples 40    # 第一个参数方向的采样
set samples 40       # 第二个参数方向的采样

# 隐藏线消除
set hidden3d         # 基本隐藏
set hidden3d front   # 表面在前面渲染

# 设置 xy 平面位置
set xyplane at -1    # 将 xy 平面移到 z=-1
```
