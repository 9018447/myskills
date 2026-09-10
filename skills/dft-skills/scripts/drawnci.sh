#!/bin/bash
# NCI surface batch generation using Multiwfn + xyzrender
# 用法: bash drawnci.sh [WORK_DIR]
#
# Workflow:
#   1. Multiwfn computes grid data (sign(lambda2)*rho + RDG)
#   2. Outputs func1.cub / func2.cub
#   3. xyzrender renders NCI surface

WORK_DIR="${1:-.}"
OUTPUT_DIR="$WORK_DIR/nci_surfaces"

export OMP_NUM_THREADS=12
export MKL_NUM_THREADS=12

mkdir -p "$OUTPUT_DIR"

MW_INPUT=$(mktemp)
cat > "$MW_INPUT" <<'EOF'
20
1
3
3
0
0
q
EOF

fchk_files=("$WORK_DIR"/*.fchk)
total=${#fchk_files[@]}
echo "Found $total .fchk files"

processed=0
skipped=0

for fchk in "${fchk_files[@]}"; do
    basename=$(basename "$fchk" .fchk)
    echo "--- [$basename] ---"

    rm -f "$WORK_DIR"/func1.cub "$WORK_DIR"/func2.cub "$WORK_DIR"/func1.cube "$WORK_DIR"/func2.cube

    Multiwfn "$fchk" < "$MW_INPUT" > /dev/null 2>&1

    if [ ! -f "$WORK_DIR"/func1.cub ] || [ ! -f "$WORK_DIR"/func2.cub ]; then
        echo "  ERROR: cube files not generated — SKIP"
        skipped=$((skipped + 1))
        continue
    fi

    mv "$WORK_DIR"/func1.cub "$OUTPUT_DIR/${basename}_signrho.cube"
    mv "$WORK_DIR"/func2.cub "$OUTPUT_DIR/${basename}_rdg.cube"

    echo "  Rendering NCI surface..."
    xyzrender "$OUTPUT_DIR/${basename}_signrho.cube" \
        --nci-surf "$OUTPUT_DIR/${basename}_rdg.cube" \
        -o "$OUTPUT_DIR/${basename}_nci.svg" 2>&1

    if [ -f "$OUTPUT_DIR/${basename}_nci.svg" ]; then
        size=$(du -h "$OUTPUT_DIR/${basename}_nci.svg" | cut -f1)
        echo "  OK: ${basename}_nci.svg ($size)"
        processed=$((processed + 1))
    else
        echo "  WARNING: SVG not generated"
        skipped=$((skipped + 1))
    fi
done

rm -f "$MW_INPUT"

echo "=========================================="
echo "DONE!  Processed: $processed  |  Skipped: $skipped"
echo "Output: $OUTPUT_DIR"
