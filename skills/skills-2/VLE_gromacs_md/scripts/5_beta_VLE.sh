#!/bin/bash
# VLE MD 准备脚本
# 功能：扩展盒子、检查 task4 分子的 fchk 文件，创建 VLE_MD 目录，移动文件并生成分子文件

set -euo pipefail

# 环境变量与路径设置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/log.sh"
source "$SCRIPT_DIR/lib/vle_utils.sh"
source "$SCRIPT_DIR/vle_workflow_guard.sh"
WORK_DIR="${WORK_DIR:-$(pwd)}"
WORK_DIR="$(resolve_runtime_dir "$WORK_DIR")"
EXPAND_BOX_SCRIPT="$SCRIPT_DIR/expand_box.sh"

# 继承 VERBOSE 设置
VERBOSE=${VERBOSE:-false}
LOG_FILE="${LOG_FILE:-$WORK_DIR/5_beta_VLE.log}"

enter_runtime_dir "$WORK_DIR"

# 检查 jq 是否安装
if ! command -v jq &> /dev/null; then
    log_error "需要安装 jq 工具来解析 JSON 文件"
    exit 1
fi

# 检查 todolist.json 是否存在
TODOLIST="$WORK_DIR/todolist.json"
if [ ! -f "$TODOLIST" ]; then
    log_error "找不到 todolist.json 文件"
    exit 1
fi

# 严格校验 todolist.json
if [ -f "$SCRIPT_DIR/validate_todolist.py" ]; then
    python3 "$SCRIPT_DIR/validate_todolist.py" "$TODOLIST" --mode all || exit 1
fi

# 检查 task4 是否存在
if ! jq -e '.task4' "$TODOLIST" &> /dev/null; then
    log_error "todolist.json 中不存在 task4"
    exit 1
fi

# 提取 task4 中的分子列表
log_info "从 task4 提取分子列表..."
runtime_molecules=()
all_molecules=()
declare -A RUNTIME_FCHK_HINTS
declare -A RUNTIME_FCHK_ALIASES

while IFS=$'\t' read -r mol_name fchk_hint aliases; do
    [ -n "$mol_name" ] || continue
    all_molecules+=("$mol_name")
    if is_runtime_placeholder "$mol_name"; then
        log_info "  识别为占位项，跳过运行态分子准备: $mol_name"
        continue
    fi
    runtime_molecules+=("$mol_name")
    RUNTIME_FCHK_HINTS["$mol_name"]="$fchk_hint"
    RUNTIME_FCHK_ALIASES["$mol_name"]="$aliases"
done < <(jq -r '.task4.molecules[] | [(.name // ""), (.fchk // .source_file // ""), ((.aliases // []) | map(tostring) | join(","))] | @tsv' "$TODOLIST")

if [ ${#all_molecules[@]} -eq 0 ]; then
    log_error "task4 中没有定义分子"
    exit 1
fi

if [ ${#runtime_molecules[@]} -eq 0 ]; then
    log_error "task4 中没有需要运行态处理的新增分子"
    exit 1
fi

log_info "task4 原始条目 ${#all_molecules[@]} 个: ${all_molecules[*]}"
log_info "运行态新增分子 ${#runtime_molecules[@]} 个: ${runtime_molecules[*]}"

log_info "检查运行态分子的 fchk 文件..."
missing_files=()
declare -A RESOLVED_FCHK_FILES
for mol in "${runtime_molecules[@]}"; do
    if resolved_file=$(resolve_fchk_file "$mol" "${RUNTIME_FCHK_HINTS[$mol]}" "${RUNTIME_FCHK_ALIASES[$mol]}"); then
        RESOLVED_FCHK_FILES["$mol"]="$resolved_file"
        log_info "  ✓ $mol 使用 ${resolved_file}"
    else
        missing_files+=("${mol}.fchk")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    log_error "以下运行态分子的 fchk 文件缺失:"
    for file in "${missing_files[@]}"; do
        log_error "  - $file"
    done
    exit 1
fi

log_success "所有运行态分子的 fchk 文件检查通过"

BASE_STRUCTURE=$(resolve_existing_vle_base_structure "$WORK_DIR")
log_info "VLE 基础结构: $BASE_STRUCTURE"

log_info "扩展 $BASE_STRUCTURE 盒子（Z方向两倍）..."
if [ ! -f "$EXPAND_BOX_SCRIPT" ]; then
    log_error "找不到 expand_box.sh 脚本"
    exit 1
fi

GMXRC_PATH="${GMXRC:-$DEFAULT_GROMACS_ENV_SCRIPT}"
bash "$EXPAND_BOX_SCRIPT" "$GMXRC_PATH" "$WORK_DIR/$BASE_STRUCTURE" "$WORK_DIR/npt_expanded.gro"

if [ $? -eq 0 ]; then
    log_success "$BASE_STRUCTURE 盒子扩展完成: npt_expanded.gro"
else
    log_error "盒子扩展失败"
    exit 1
fi

# 创建 VLE_MD 目录
VLE_DIR="$WORK_DIR/VLE_MD"
if [ -d "$VLE_DIR" ]; then
    if [ -f "$VLE_DIR/system_with_gas.gro" ] && [ -f "$VLE_DIR/VLE_topol.top" ]; then
        log_success "VLE_MD 中已存在完整构建结果，跳过重新准备"
        exit 0
    fi
    log_info "VLE_MD 目录已存在，清理待重建的中间文件..."
    find "$VLE_DIR" -maxdepth 1 -type f \( -name '*.fchk' -o -name '*.xyz' -o -name '*.chg' -o -name '*.mol2' -o -name '*.gro' -o -name '*.top' -o -name '*.itp' -o -name '*.log' -o -name 'npt_expanded.gro' -o -name 'todolist.json' -o -name 'todolist.md' -o -name '原子类型.txt' \) -delete
else
    log_info "创建 VLE_MD 目录..."
fi

mkdir -p "$VLE_DIR"
log_success "VLE_MD 目录已创建: $VLE_DIR"

if [ ! -f "$WORK_DIR/npt_expanded.gro" ]; then
    log_error "找不到 npt_expanded.gro 文件"
    exit 1
fi

if [ ! -f "$WORK_DIR/topol.top" ]; then
    log_error "找不到 topol.top 文件"
    exit 1
fi

log_info "复制 npt_expanded.gro、topol.top 与待办文件到 VLE_MD..."
cp "$WORK_DIR/npt_expanded.gro" "$VLE_DIR/"
cp "$WORK_DIR/topol.top" "$VLE_DIR/"
cp "$WORK_DIR/todolist.json" "$VLE_DIR/"
if [ -f "$WORK_DIR/todolist.md" ]; then
    cp "$WORK_DIR/todolist.md" "$VLE_DIR/"
fi
copy_topology_dependencies "$WORK_DIR" "$VLE_DIR"

log_info "复制运行态分子的 fchk 文件到 VLE_MD..."
for mol in "${runtime_molecules[@]}"; do
    fchk_file="${RESOLVED_FCHK_FILES[$mol]}"
    log_info "  复制 $fchk_file -> ${mol}.fchk"
    cp "$fchk_file" "$VLE_DIR/${mol}.fchk"
done

log_success "文件移动完成"

# 进入 VLE_MD 目录
WORK_DIR="$VLE_DIR"
enter_runtime_dir "$VLE_DIR"
log_info "工作目录: $(pwd)"

# 运行 4_prepare_molecules.sh
PREPARE_SCRIPT="$SCRIPT_DIR/4_prepare_molecules.sh"
if [ ! -f "$PREPARE_SCRIPT" ]; then
    log_error "找不到脚本: $PREPARE_SCRIPT"
    exit 1
fi

log_info "运行 4_prepare_molecules.sh..."
PREPARE_MOLECULE_SOURCE="task4" PREPARE_MOLECULE_CONTEXT="vle-runtime" PREPARE_MOLECULES="$(printf '%s\n' "${runtime_molecules[@]}")" bash "$PREPARE_SCRIPT"

if [ $? -eq 0 ]; then
    log_success "4_prepare_molecules.sh 执行完成"
else
    log_error "4_prepare_molecules.sh 执行失败"
    exit 1
fi

# 检查 task4 产出文件
log_info "检查 task4 产出文件..."
missing_outputs=()

for mol in "${runtime_molecules[@]}"; do
    # 检查必需的产出文件
    for ext in chg mol2 gro top itp; do
        output_file="${mol}.${ext}"
        if [ ! -f "$output_file" ]; then
            missing_outputs+=("$output_file")
        else
            # 检查文件是否为空
            if [ ! -s "$output_file" ]; then
                missing_outputs+=("$output_file (空文件)")
            else
                log_info "  ✓ $output_file"
            fi
        fi
    done
done

if [ ${#missing_outputs[@]} -gt 0 ]; then
    log_error "以下产出文件缺失或为空:"
    for file in "${missing_outputs[@]}"; do
        log_error "  - $file"
    done
    exit 1
fi

log_success "所有 task4 产出文件检查通过"
log_success "VLE MD 准备完成！"
log_info "输出目录: $VLE_DIR"
