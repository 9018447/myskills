#!/bin/bash
set -euo pipefail
# 环境变量与路径设置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/log.sh"

# 严格校验 todolist.json
if [ -f "todolist.json" ] && [ -f "$SCRIPT_DIR/validate_todolist.py" ]; then
    python3 "$SCRIPT_DIR/validate_todolist.py" todolist.json --mode all || exit 1
fi

filter_unique_lines() {
    python3 - <<'PY'
import sys

seen = set()
for raw in sys.stdin:
    line = raw.strip()
    if not line or line in seen:
        continue
    seen.add(line)
    print(line)
PY
}

# 继承父脚本的 VERBOSE 设置
VERBOSE=${VERBOSE:-false}
LOG_FILE=${LOG_FILE:-"workflow.log"}

if [ -n "${PREPARE_MOLECULES:-}" ]; then
    molecules=$(printf '%s\n' "$PREPARE_MOLECULES" | filter_unique_lines)
    log_info "从 PREPARE_MOLECULES 读取目标分子列表 (${PREPARE_MOLECULE_CONTEXT:-runtime})"
elif [ -f "box.inp" ]; then
    molecules=$(awk '/^structure/ { name=$2; sub(/\.[Pp][Dd][Bb]$/,"",name); print name }' box.inp | filter_unique_lines)
    log_info "从 box.inp 读取目标分子列表"
elif [ -f "todolist.json" ] && [ "${PREPARE_MOLECULE_SOURCE:-}" = "task4" ] && jq -e '.task4.molecules | length > 0' todolist.json > /dev/null 2>&1; then
    molecules=$(jq -r '.task4.molecules[].name' todolist.json | filter_unique_lines)
    log_info "根据 PREPARE_MOLECULE_SOURCE=task4 从 todolist.json 的 task4 读取目标分子列表"
elif [ -f "todolist.json" ] && jq -e '.task3.molecules | length > 0' todolist.json > /dev/null 2>&1; then
    molecules=$(jq -r '.task3.molecules[].name' todolist.json | filter_unique_lines)
    log_info "未找到 box.inp，改为从 todolist.json 的 task3 读取目标分子列表"
else
    molecules=$(printf '%s\n' *.fchk 2>/dev/null | sed 's/\.fchk$//' | filter_unique_lines)
    log_info "未找到 box.inp，回退为处理当前目录中的全部 .fchk 文件"
fi


# 单分子准备阶段脚本
# 根据runmd.md中描述的步骤1实现

log_info "开始单分子准备阶段..."
log_info "脚本目录: $SCRIPT_DIR"

# 从 todolist.json 中的 task1 区块读取指定分子的 charge 值
# 如果找不到或为空则返回 0
get_charge_for_molecule() {
    mol="$1"
    todofile="todolist.json"

    # 检查jq是否安装
    if ! command -v jq &> /dev/null; then
        log_error "需要安装jq工具来解析JSON文件"
        echo "0"
        return
    fi

    if [ ! -f "$todofile" ]; then
        echo "0"
        return
    fi

    # 使用jq从task1中提取指定分子的电荷值（不区分大小写）
    ch=$(jq -r --arg mol "$mol" '
        .task1.molecules[] |
        select(.name == $mol or (.name | ascii_downcase) == ($mol | ascii_downcase)) |
        .charge // 0
    ' "$todofile" | head -n 1)

    if [ -z "$ch" ]; then
        echo "0"
    else
        echo "$ch"
    fi
}

# 前置检查：确保每个 *.fchk 都有对应的 *.xyz
log_info "检查 fchk 和 xyz 文件配对..."
missing_xyz=0
for fchk_file in *.fchk; do
    if [ -f "$fchk_file" ]; then
        xyz_file="${fchk_file%.fchk}.xyz"
        if [ ! -f "$xyz_file" ]; then
            log_info "缺失 $xyz_file 文件，将从 $fchk_file 生成"
            missing_xyz=1
        fi
    fi
done

# 如果有缺失的xyz文件，则运行fch2xyz.sh
if [ $missing_xyz -eq 1 ]; then
    log_info "运行 fch2xyz.sh 生成缺失的 xyz 文件..."
    bash "$SCRIPT_DIR/fch2xyz.sh"
fi

# 再次检查所有xyz文件是否已生成
log_info "再次检查所有必需文件..."
for fchk_file in *.fchk; do
    if [ -f "$fchk_file" ]; then
        xyz_file="${fchk_file%.fchk}.xyz"
        if [ ! -f "$xyz_file" ]; then
            log_error "$xyz_file 未能成功生成"
            exit 1
        fi
    fi
done

log_info "所有 fchk 文件都有对应的 xyz 文件"

# 对每个分子执行单分子准备步骤
for fchk_file in *.fchk; do
    if [ -f "$fchk_file" ]; then
        filename="${fchk_file%.fchk}"

        if [ -n "$molecules" ] && ! printf '%s\n' "$molecules" | grep -Fxq "$filename"; then
            log_info "跳过分子: $filename（不在当前目标列表中）"
            continue
        fi

        log_info "处理分子: $filename"
        
        # 1. RESP 电荷生成
        chg_file="${filename}.chg"
        if [ -f "$chg_file" ] && [ -s "$chg_file" ]; then
            log_info "  跳过: $chg_file 已存在且非空"
        else
            log_info "  步骤 1: 生成 RESP 电荷..."
            bash "$SCRIPT_DIR/resp.sh" "$fchk_file"
        fi

        # 2. 结构转换 & 拓扑生成
        log_info "  步骤 2a: XYZ 转换为 MOL2..."
        xyz_file="${filename}.xyz"
        
        if [ ! -f "$xyz_file" ]; then
            log_error "  找不到 XYZ 文件: $xyz_file"
            exit 1
        fi
        
        if ! obabel "$xyz_file" -O "${filename}.mol2" -omol2 >> "$LOG_FILE" 2>&1; then
            log_error "  obabel 转换失败"
            exit 1
        fi
        
        # 检查 mol2 文件是否包含 ATOM 行
        if [ ! -f "${filename}.mol2" ] || ! grep -q "ATOM" "${filename}.mol2"; then
            log_error "  ${filename}.mol2 未生成或不包含 ATOM 行"
            exit 1
        fi
        log_info "  成功生成 ${filename}.mol2"
        
        # 2b. MOL2 → GROMACS
        log_info "  步骤 2b: 生成 GROMACS 拓扑文件..."
        bash "$SCRIPT_DIR/gentop.sh" "${filename}.mol2"
        
        # 检查产出文件
        gro_file="${filename}.gro"
        top_file="${filename}.top"
        itp_file="${filename}.itp"
        
        if [ ! -f "$gro_file" ]; then
            log_error "  $gro_file 未生成"
            exit 1
        fi
        
        if [ ! -f "$top_file" ]; then
            log_error "  $top_file 未生成"
            exit 1
        fi
        
        if [ ! -f "$itp_file" ]; then
            log_error "  $itp_file 未生成"
            exit 1
        fi
        
        # 检查 gro 文件中的原子数是否正确
        atom_count=$(sed -n '2p' "$gro_file")
        if [ -z "$atom_count" ] || [ "$atom_count" -le 0 ]; then
            log_error "  $gro_file 中的原子数无效"
            exit 1
        fi
        
        log_info "  成功生成 $gro_file, $top_file, $itp_file"
    fi
done

log_success "所有分子准备完成"
if [ "$VERBOSE" = true ]; then
    echo "产出文件列表:"
    for xyz_file in *.xyz; do
        if [ -f "$xyz_file" ]; then
            filename="${xyz_file%.xyz}"
            echo "  - ${filename}.chg"
            echo "  - ${filename}.mol2"
            echo "  - ${filename}.gro"
            echo "  - ${filename}.top"
            echo "  - ${filename}.itp"
        fi
    done
fi
