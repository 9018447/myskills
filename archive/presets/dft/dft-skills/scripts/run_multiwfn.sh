#!/bin/bash
# Multiwfn 批处理脚本
# 用法: ./run_multiwfn.sh <输入文件> <模式> [参数]

export OMP_NUM_THREADS=12
export MKL_NUM_THREADS=12

INPUT="$1"
MODE="$2"

if [ -z "$INPUT" ] || [ -z "$MODE" ]; then
    echo "Usage: $0 <input_file> {esp|aim|nci|igmh <frag_range>|xyz2gjf|tranxyz|all}"
    exit 1
fi

run_esp() {
    echo "=== Running ESP analysis ==="
    cat ESP.txt | Multiwfn "$INPUT"
}

run_aim() {
    echo "=== Running AIM analysis ==="
    cat AIM.txt | Multiwfn "$INPUT"
    # 自动移动到 VMD 目录（按需修改路径）
    # mv -f *.pdb "/media/smh/d/vmd-2.0.0a7"
}

run_nci() {
    echo "=== Running NCI analysis ==="
    cat NCI.txt | Multiwfn "$INPUT"
    # 退出码 59 是正常的（由 'q' 命令导致）
    if [ $? -eq 59 ]; then
        echo "NCI finished with exit code 59 (expected)."
    fi
}

run_igmh() {
    local frag_range="$1"
    if [ -z "$frag_range" ]; then
        echo "Error: IGMH mode requires fragment atom range, e.g.: $0 <file> igmh 1-6"
        exit 1
    fi
    echo "=== Running IGMH analysis (fragment: $frag_range) ==="
    printf '20\n11\n2\n%s\nc\n2\n3\n0\n0\nq\n' "$frag_range" | Multiwfn "$INPUT"
}

run_xyz2gjf() {
    if [ ! -f "template.gjf" ]; then
        echo "Error: template.gjf not found in current directory."
        exit 1
    fi
    echo "=== Converting to gjf ==="
    cat xyz2gjf.txt | Multiwfn "$INPUT"
}

run_tranxyz() {
    echo "=== Converting to xyz ==="
    cat tranxyz.txt | Multiwfn "$INPUT"
}

case "$MODE" in
    esp)
        run_esp
        ;;
    aim)
        run_aim
        ;;
    nci)
        run_nci
        ;;
    igmh)
        run_igmh "$3"
        ;;
    xyz2gjf)
        run_xyz2gjf
        ;;
    tranxyz)
        run_tranxyz
        ;;
    all)
        run_esp
        run_aim
        run_nci
        run_xyz2gjf
        run_tranxyz
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 <input_file> {esp|aim|nci|igmh <frag_range>|xyz2gjf|tranxyz|all}"
        exit 1
        ;;
esac
