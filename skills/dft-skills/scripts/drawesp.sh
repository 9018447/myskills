#!/bin/bash

# ------------------------------------------------------------
# 脚本功能：
# 1. 将当前目录下所有 *.fchk 文件使用 Multiwfn 转换为
#    ESP 和 DENSITY 的 .cube 文件（分别命名为 ESP*.cube、DENSITY*.cube）。
# 2. 使用 xyzrender 将生成的 DENSITY 与对应的 ESP 文件渲染为 SVG。
# ------------------------------------------------------------

# ---------- 第一步：fchk → cube ----------
for inf in *.fchk; do
    # 若没有匹配到文件，跳过循环
    [[ -e "$inf" ]] || continue

    echo "Converting ${inf} to cube files..."

    Multiwfn "${inf}" << EOF > /dev/null
5
1
1
2
0
5
12
1
2
0
q
EOF

    # 重命名生成的文件
    mv totesp.cub "ESP${inf//.fchk}.cube"
    mv density.cub "DENSITY${inf//.fchk}.cube"
done

# ---------- 第二步：cube → svg ----------
for densfile in DENSITY*.cube; do
    # 若没有匹配到文件，跳过循环
    [[ -e "$densfile" ]] || continue

    # 取得基础名称（去掉 DENSITY 前缀和 .cube 后缀）
    base="${densfile#DENSITY}"
    base="${base%.cube}"

    # 对应的 ESP 文件名
    espfile="ESP${base}.cube"

    # 检查对应的 ESP 文件是否存在
    if [[ ! -f "$espfile" ]]; then
        echo "Warning: 对应的 ESP 文件 ${espfile} 未找到，跳过 ${densfile}"
        continue
    fi

    # 输出 SVG 文件名
    outfile="${base}_esp.svg"

    echo "Rendering ${densfile} 与 ${espfile} 为 ${outfile} ..."
    xyzrender "${densfile}" --esp "${espfile}" --iso 0.005 --opacity 0.75 -o "${outfile}"
done

echo "All conversions and renderings completed successfully!"
