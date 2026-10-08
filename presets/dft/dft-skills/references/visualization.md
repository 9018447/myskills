# 可视化工具

## xyzrender

基于 Python 的可视化渲染引擎，必须基于 .cube 后缀的文件进行绘制。

**注意**：Multiwfn 产出的文件是 `.cub` 后缀，xyzrender 需要 `.cube` 后缀，渲染前需重命名。

### ESP 渲染

需要文件：`DENSITY.cube` + `ESP.cube`（由 `density.cub` 和 `totesp.cub` 重命名得到）

```bash
mv density.cub DENSITY.cube
mv totesp.cub ESP.cube
xyzrender DENSITY.cube --esp ESP.cube --iso 0.005 --opacity 0.75 -o esp.svg
```

### NCI 渲染

需要文件：`func1.cube` + `func2.cube`（由 `func1.cub` 和 `func2.cub` 重命名得到）
`func1.cub` 是 sign(lambda2)*rho，`func2.cub` 是 RDG

```bash
mv func1.cub signrho.cube
mv func2.cub rdg.cube
xyzrender signrho.cube --nci-surf rdg.cube -o nci.svg
```

## VMD 脚本

### AIM 可视化 (AIM.vmd)

```tcl
color Display Background white
axes location Off
display depthcue off
display rendermode GLSL

set CPsize 0.07
set pathsize 0.02

mol new CPs.pdb
# (3,-3) critical points
mol modselect 0 0 name C
mol modstyle 0 0 VDW $CPsize 22.0
mol modcolor 0 0 ColorID 11
# (3,-1)
mol addrep 0
mol modselect 1 0 name N
mol modstyle 1 0 VDW $CPsize 22.0
mol modcolor 1 0 ColorID 3
# (3,+1)
mol addrep 0
mol modselect 2 0 name O
mol modstyle 2 0 VDW $CPsize 22.0
mol modcolor 2 0 ColorID 4
# (3,+3)
mol addrep 0
mol modselect 3 0 name F
mol modstyle 3 0 VDW $CPsize 22.0
mol modcolor 3 0 ColorID 7
# Topology paths
mol new paths.pdb
mol modstyle 0 1 VDW $pathsize 22.0
mol modcolor 0 1 ColorID 32
# Molecular structure
mol new mol.pdb
mol modstyle 0 2 CPK 0.7 0.3 22.0 22.0
mol off 2
```

### IGMH 可视化 (IGM_inter.vmd)

```tcl
mol new sl2r.cub
mol addfile dg_inter.cub
mol delrep 0 top
mol representation CPK 1.0 0.3 18.0 16.0
mol addrep top
mol representation Isosurface 0.01000 1 0 0 1 1
mol color Volume 0
mol addrep top
mol scaleminmax top 1 -0.05 0.05
color scale method BGR
color Display Background white
axes location Off
display depthcue off
display rendermode GLSL
light 3 on
material change specular Opaque 0.300000
```

### ESP 等值面可视化 (ESPiso.vmd)

```tcl
color scale method BWR
color Display Background white
axes location Off
display depthcue off
display rendermode GLSL
light 2 on
light 3 on
material change transmode EdgyGlass 1.0
material change specular EdgyGlass 0.15
material change shininess EdgyGlass 0.95
material change opacity EdgyGlass 0.7
material change outlinewidth EdgyGlass 0.9
material change outline EdgyGlass 0.5

set nsystem 1
set colorlow -0.03
set colorhigh 0.03

for {set i 1} {$i<=$nsystem} {incr i} {
    set id [expr $i-1]
    mol new density$i.cub
    mol addfile ESP$i.cub
    mol modstyle 0 $id CPK 1.000000 0.300000 22.000000 22.000000
    mol addrep $id
    mol modstyle 1 $id Isosurface 0.001000 0 0 0 1 1
    mol modmaterial 1 $id EdgyGlass
    mol modcolor 1 $id Volume 1
    mol scaleminmax $id 1 $colorlow $colorhigh
}
```
