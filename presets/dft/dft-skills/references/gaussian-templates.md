# Gaussian 16 输入文件模板

## 中性分子 — 结构与频率优化

```gjf
%chk=[FILENAME].chk
%mem=20GB
%nprocshared=16
#p B3LYP/6-311G(d,p) Opt Freq EmpiricalDispersion=GD3BJ

[FILENAME] optimization and frequency

0 1
[GEOMETRY]

```

## 阴离子 — 加弥散函数

```gjf
%chk=[FILENAME].chk
%mem=20GB
%nprocshared=16
#p B3LYP/6-311+G(d,p) Opt Freq EmpiricalDispersion=GD3BJ

[FILENAME] anion optimization with diffuse functions

0 1
[GEOMETRY]

```

## 团簇结合能 — BSSE 校正

```gjf
%chk=[FILENAME].chk
%mem=20GB
%nprocshared=16
#p B3LYP/6-311+G(d,p) EmpiricalDispersion=GD3BJ counterpoise=2

Counterpoise calculation for binding energy

0 1
[ATOM_SYMBOL] [X] [Y] [Z] [FRAGMENT_ID]
...
```

片段编号规则：
- 每个原子后跟片段编号（1 或 2，对应 counterpoise=2）
- 如果整体/片段的电荷和自旋多重度不同，需要写全：`整体电荷 整体自旋 片段1电荷 片段1自旋 片段2电荷 片段2自旋`

## NBO 分析

```gjf
%oldchk=[OPTIMIZED].chk
%chk=[FILENAME]_NBO.chk
%mem=20GB
%nprocshared=16
#p M062X/6-311+G(d,p) empiricaldispersion=gd3 scrf(SMD,solvent=water) geom=check Guess=Read pop=nboread

NBO calculation using optimized geometry

0 1

$NBO plot file=./NBO $END

```

注意：
- `%oldchk` 指向结构和频率优化后产出的 chk 文件
- `geom=check` 从旧 chk 读取几何
- `Guess=Read` 从旧 chk 读取初始猜测
- 末尾空行不可省略

## 从 XYZ 提取坐标

XYZ 文件格式：
```
[原子数]
[注释行]
[元素符号] [X] [Y] [Z]
...
```

Gaussian .gjf 的几何部分只需元素符号和 XYZ 坐标（无原子数和注释行）。
