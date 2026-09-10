#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/log.sh"
source "$SCRIPT_DIR/lib/topology.sh"

VERBOSE=${VERBOSE:-false}
LOG_FILE=${LOG_FILE:-"workflow.log"}

log_info "开始构建系统盒子和拓扑文件..."
log_info "脚本目录: $SCRIPT_DIR"

# 2.1 盒子结构生成
log_info "步骤 2.1: 生成盒子结构"

if [ ! -f "box.inp" ]; then
    log_error "box.inp 文件不存在"
    exit 1
fi

gro_files=( *.gro )
if [ -e "${gro_files[0]}" ]; then
    if command -v obabel >/dev/null 2>&1; then
        log_info "检测到 .gro 文件，使用 obabel 转换为 .pdb..."
        for gro in "${gro_files[@]}"; do
            if [ -f "$gro" ]; then
                pdb="${gro%.gro}.pdb"
                log_info "转换 $gro -> $pdb"
                if ! obabel -igro "$gro" -opdb -O "$pdb" >> "$LOG_FILE" 2>&1; then
                    log_info "警告: 使用 obabel 转换 $gro 失败"
                fi
            fi
        done
    else
        log_info "警告: obabel 未找到，跳过 .gro -> .pdb 转换"
    fi
else
    log_info "未检测到 .gro 文件，跳过转换步骤"
fi

python "$SCRIPT_DIR/modify_resname.py" >> "$LOG_FILE" 2>&1
log_info "修改Resname完成"

log_info "运行 Packmol 生成 box.pdb..."
if [ "$VERBOSE" = true ]; then
    packmol < box.inp
else
    packmol < box.inp >> "$LOG_FILE" 2>&1
fi

if [ ! -f "box.pdb" ]; then
    log_error "Packmol 运行失败，未生成 box.pdb"
    exit 1
fi

line_count=$(wc -l < box.pdb)
if [ "$line_count" -lt 3 ]; then
    log_error "box.pdb 文件行数少于3行"
    exit 1
fi

log_success "盒子结构生成完成"

# 2.2 统一拓扑文件 topol.top
log_info "步骤 2.2: 构建统一拓扑文件 topol.top"

itp_files=(*.itp)
if [ ! -f "${itp_files[0]}" ]; then
    log_error "当前目录中未找到 .itp 文件"
    exit 1
fi

first_top=$(ls *.top | head -n 1)
if [ -z "$first_top" ]; then
    log_error "当前目录中未找到 .top 文件"
    exit 1
fi

cp "$first_top" topol.top
head -n 5 topol.top > temp_topol.top && mv temp_topol.top topol.top
log_info "使用 $first_top 作为模板创建 topol.top"

merge_topology topol.top "$(basename "$(pwd)")" "${itp_files[@]}"

echo "拓扑文件构建完成"

# 2.3 最终检查
log_info "步骤 2.3: 最终检查"

missing_includes=0
for itp in "${itp_files[@]}"; do
    if [ -f "$itp" ]; then
        if ! grep -q "#include \"$itp\"" topol.top; then
            log_info "警告: $itp 可能未被正确包含在 topol.top 中"
            missing_includes=1
        fi
    fi
done

if [ $missing_includes -eq 0 ]; then
    log_info "所有 itp 文件均已包含"
fi

for target_file in topol.top box.pdb; do
    if grep -Eq '(^|[^A-Za-z0-9])(MOL|UNL)([^A-Za-z0-9]|$)' "$target_file"; then
        log_error "检测到未替换的通用残基名: $target_file"
        exit 1
    fi
done

log_success "系统盒子和拓扑文件构建完成"
