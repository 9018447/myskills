# Multiwfn 分析输入文件

所有分析前设置线程：
```bash
export OMP_NUM_THREADS=12
export MKL_NUM_THREADS=12
```

## ESP 分析

输入文件 `ESP.txt`：
```
5
1
1
22
0
5
12
1
2
0
q
```

产出：`totesp.cub` 和 `density.cub`

## IGMH 分析

输入文件 `IGMH.txt`：
```
20
11
2
[片段原子序号范围，如 1-6]
c
2
3
0
0
q
```

**片段原子序号是关键参数**，必须与用户确认。

产出：`sl2r.cub` `dg.cub` `dg_inter.cub` `dg_intra.cub`

## AIM 分析

输入文件 `AIM.txt`：
```
2
2
3
4
5
8
-4
6
0
-5
6
0
7
-1
-10
100
2
1
mol.pdb
0
q
```

产出：`CPs.pdb` `paths.pdb` `mol.pdb`

自动移动到 VMD 目录：
```bash
mv -f *.pdb "/media/smh/d/vmd-2.0.0a7"
```

## NCI 分析

输入文件 `NCI.txt`：
```
20
1
3
3
q
```

产出：`func1.cub`（sign(lambda2)*rho）和 `func2.cub`（RDG）

注意：退出码 59 是正常的（由 'q' 命令导致），文件仍然会正确写入。

## 格式转换

### xyz/fchk → gjf

输入文件 `xyz2gjf.txt`：
```
100
2
10

0
q
```

注意：第 4 行（`10` 之后）必须有**两个空行**。
需要当前目录存在 `template.gjf` 模板文件，`[GEOMETRY]` 或 `[GEOMETRY]` 行会被替换为当前坐标。

### gjf/fchk → xyz

输入文件 `tranxyz.txt`：
```
100
2
2

0
q
```
