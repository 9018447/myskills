#!/bin/bash
# Index all CUBE/3DL files in the LUT library
# Usage: bash scripts/index_luts.sh [directory]

LUT_DIR="${1:-$(dirname "$0")/../assets/luts}"

echo "=== LUT Library Index ==="
echo "Directory: $LUT_DIR"
echo ""

if [ ! -d "$LUT_DIR" ]; then
    echo "ERROR: Directory not found: $LUT_DIR"
    exit 1
fi

count=0
for category in "$LUT_DIR"/*/; do
    if [ -d "$category" ]; then
        cat_name=$(basename "$category")
        echo "## $cat_name"
        for cube in "$category"*.cube "$category"*.3dl "$category"*.CUBE "$category"*.3DL 2>/dev/null; do
            if [ -f "$cube" ]; then
                name=$(basename "$cube")
                # Read LUT size from header
                size=$(grep -i "LUT_3D_SIZE" "$cube" 2>/dev/null | head -1 | awk '{print $2}')
                if [ -z "$size" ]; then
                    size="unknown"
                fi
                entries=$((size * size * size))
                echo "  - $name (${size}x${size}x${size} = $entries entries)"
                count=$((count + 1))
            fi
        done
        echo ""
    fi
done

# Also check root level
for cube in "$LUT_DIR"*.cube "$LUT_DIR"*.3dl 2>/dev/null; do
    if [ -f "$cube" ]; then
        name=$(basename "$cube")
        size=$(grep -i "LUT_3D_SIZE" "$cube" 2>/dev/null | head -1 | awk '{print $2}')
        [ -z "$size" ] && size="unknown"
        echo "  - $name (${size}x${size}x${size})"
        count=$((count + 1))
    fi
done

echo "=== Total: $count LUT files ==="
