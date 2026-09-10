#!/bin/bash

set -euo pipefail

# 从gro文件提取边界尺寸并扩展盒子
# 用法: ./expand_box.sh [GMXRC路径] [输入gro文件] [输出gro文件]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vle_workflow_guard.sh"

GMXRC="${1:-/media/smh/d/gromacs/bin/GMXRC}"
INPUT_GRO="${2:-npt.gro}"
OUTPUT_GRO="${3:-npt_expanded.gro}"

if [[ ! -f "$INPUT_GRO" ]]; then
    echo "错误: 输入文件 $INPUT_GRO 不存在"
    exit 1
fi

BOX_LINE=$(tail -n 1 "$INPUT_GRO")

BOX_X=$(echo "$BOX_LINE" | awk '{print $1}')
BOX_Y=$(echo "$BOX_LINE" | awk '{print $2}')
BOX_Z=$(echo "$BOX_LINE" | awk '{print $3}')

BOX_Z=$(echo "$BOX_Z * 2" | bc)

echo "从 $INPUT_GRO 提取的边界尺寸:"
echo "  X: $BOX_X"
echo "  Y: $BOX_Y"
echo "  Z: $BOX_Z"

load_gromacs_env "$GMXRC" "$DEFAULT_GROMACS_ENV_SCRIPT"

echo "执行 gmx editconf..."
gmx editconf -f "$INPUT_GRO" -o "$OUTPUT_GRO" -box "$BOX_X" "$BOX_Y" "$BOX_Z"

if [[ $? -eq 0 ]]; then
    echo "成功: 输出文件已保存为 $OUTPUT_GRO"
else
    echo "错误: gmx editconf 执行失败"
    exit 1
fi
