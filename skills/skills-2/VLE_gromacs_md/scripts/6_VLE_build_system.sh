#!/bin/bash
# VLE 系统构建脚本
# 功能：将气体分子插入到扩展的 NPT 系统中，构建气液两相平衡系统

set -euo pipefail

# 环境变量与路径设置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vle_workflow_guard.sh"
WORK_DIR="${WORK_DIR:-$(pwd)}"
WORK_DIR="$(resolve_runtime_dir "$WORK_DIR")"

# 继承 VERBOSE 设置
VERBOSE=${VERBOSE:-false}
LOG_FILE=${LOG_FILE:-"$WORK_DIR/6_VLE_build.log"}

# 加载共享库
source "$SCRIPT_DIR/lib/log.sh"
source "$SCRIPT_DIR/lib/topology.sh"

log_info "=== VLE 系统构建开始 ==="
log_info "工作目录: $WORK_DIR"

# 检查工作目录
if [ ! -d "$WORK_DIR" ]; then
    log_error "工作目录不存在: $WORK_DIR"
    exit 1
fi

enter_runtime_dir "$WORK_DIR"

# 步骤 1：前置检查
log_info "步骤 1: 前置检查"

# 检查必需文件
required_files=("npt_expanded.gro" "topol.top")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "缺少必需文件: $file"
        exit 1
    fi
    log_info "  ✓ 找到 $file"
done

# 检查 jq 工具
if ! command -v jq &> /dev/null; then
    log_error "需要安装 jq 工具"
    exit 1
fi

# 检查 todolist.json
TODOLIST="$WORK_DIR/todolist.json"
if [ ! -f "$TODOLIST" ]; then
    log_error "找不到 todolist.json: $TODOLIST"
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

log_success "前置检查完成"

# 步骤 2：解析 task4 气体分子配置
log_info "步骤 2: 解析 task4 气体分子配置"

gas_molecules=()
while IFS= read -r line; do
    name=$(echo "$line" | cut -d' ' -f1)
    count=$(echo "$line" | cut -d' ' -f2)
    gas_molecules+=("$name:$count")
    log_info "  气体分子: $name, 数量: $count"
done < <(jq -r '.task4.molecules[] | select(.phase == "g") | "\(.name) \(.count)"' "$TODOLIST")

if [ ${#gas_molecules[@]} -eq 0 ]; then
    log_error "task4 中没有定义气体分子 (phase='g')"
    exit 1
fi

log_success "找到 ${#gas_molecules[@]} 种气体分子"

# 步骤 3：检查气体分子文件
log_info "步骤 3: 检查气体分子文件"

for mol_pair in "${gas_molecules[@]}"; do
    mol_name="${mol_pair%%:*}"
    for ext in gro itp; do
        file="${mol_name}.${ext}"
        if [ ! -f "$file" ]; then
            log_error "缺少文件: $file"
            exit 1
        fi
        log_info "  ✓ 找到 $file"
    done
done

log_success "所有气体分子文件检查完成"

# 步骤 4：修改气体分子 resname
log_info "步骤 4: 修改气体分子 resname"

MODIFY_SCRIPT="$SCRIPT_DIR/modify_resname.py"
if [ ! -f "$MODIFY_SCRIPT" ]; then
    log_error "找不到 modify_resname.py: $MODIFY_SCRIPT"
    exit 1
fi

for mol_pair in "${gas_molecules[@]}"; do
    mol_name="${mol_pair%%:*}"
    for ext in gro itp top; do
        target_file="${mol_name}.${ext}"
        if [ ! -f "$target_file" ]; then
            continue
        fi

        log_info "  修改 ${target_file} 的 resname"
        python3 "$MODIFY_SCRIPT" "$target_file" "$mol_name" >> "$LOG_FILE" 2>&1

        if [ $? -ne 0 ]; then
            log_error "resname 修改失败: ${target_file}"
            exit 1
        fi
        log_info "  ✓ ${target_file} resname 修改完成"
    done
done

log_success "resname 修改完成"

# 步骤 5：加载 GROMACS 环境
log_info "步骤 5: 加载 GROMACS 环境"

load_gromacs_env "${GMXRC:-}" "$DEFAULT_GROMACS_ENV_SCRIPT"
log_info "已加载 GROMACS 环境"

get_gro_atom_count() {
    local gro_file="$1"
    sed -n '2p' "$gro_file" | awk '{print $1}'
}

expand_box_z_for_retry() {
    local input_file="$1"
    local output_file="$2"
    local target_box_z="$3"
    local box_x=""
    local box_y=""
    local box_z=""

    read -r box_x box_y box_z < <(tail -n 1 "$input_file" | awk '{print $1, $2, $3}')

    log_info "  扩展盒子 Z 方向: ${box_z} -> ${target_box_z}"
    gmx editconf -f "$input_file" -o "$output_file" -box "$box_x" "$box_y" "$target_box_z" >> "$LOG_FILE" 2>&1
}

calculate_retry_box_z() {
    local current_box_z="$1"
    local requested_count="$2"
    local inserted_count="$3"

    python3 - <<PY
from decimal import Decimal, ROUND_HALF_UP

current = Decimal("$current_box_z")
requested = Decimal("$requested_count")
inserted = Decimal("$inserted_count")

if inserted <= 0:
    target = current * Decimal("2.00")
else:
    target = max(
        current * Decimal("1.80"),
        current * (requested / inserted) * Decimal("1.20"),
        current + Decimal("6.00"),
    )

print(target.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP))
PY
}

count_inserted_molecules() {
    local input_file="$1"
    local output_file="$2"
    local molecule_atom_count="$3"
    local input_atoms=""
    local output_atoms=""
    local added_atoms=""

    input_atoms=$(get_gro_atom_count "$input_file")
    output_atoms=$(get_gro_atom_count "$output_file")
    added_atoms=$((output_atoms - input_atoms))

    if [ "$added_atoms" -lt 0 ]; then
        log_error "分子插入后原子数异常减少: ${input_file} -> ${output_file}"
        exit 1
    fi

    if [ $((added_atoms % molecule_atom_count)) -ne 0 ]; then
        log_error "插入后的原子增量 ${added_atoms} 不能整除单分子原子数 ${molecule_atom_count}"
        exit 1
    fi

    printf '%s\n' $((added_atoms / molecule_atom_count))
}

log_info "步骤 6: 插入气体分子到系统"

# 记录插入前的原子数
input_atoms=$(sed -n '2p' npt_expanded.gro | awk '{print $1}')
log_info "插入前原子数: $input_atoms"

current_input="npt_expanded.gro"
step_index=1
inserted_gas_molecules=()
for mol_pair in "${gas_molecules[@]}"; do
    mol_name="${mol_pair%%:*}"
    mol_count="${mol_pair##*:}"
    molecule_atom_count=$(get_gro_atom_count "${mol_name}.gro")
    attempt_input="$current_input"
    retry_input=""
    current_box_z=""
    retry_box_z=""
    actual_inserted=0

    if [ "$step_index" -eq "${#gas_molecules[@]}" ]; then
        next_output="system_with_gas.gro"
    else
        next_output=".insert_step_${step_index}.gro"
    fi

    log_info "  插入 ${mol_name}，目标数量 ${mol_count}，输入 ${attempt_input}，输出 ${next_output}"
    gmx insert-molecules -f "$attempt_input" -ci "${mol_name}.gro" -nmol "$mol_count" -o "$next_output" >> "$LOG_FILE" 2>&1

    if [ ! -f "$next_output" ]; then
        log_error "分子插入失败，未生成 $next_output"
        exit 1
    fi

    actual_inserted=$(count_inserted_molecules "$attempt_input" "$next_output" "$molecule_atom_count")
    if [ "$actual_inserted" -eq "$mol_count" ]; then
        log_info "  ✓ ${mol_name} 已完整插入 ${actual_inserted} 个分子"
    else
        read -r _ _ current_box_z < <(tail -n 1 "$attempt_input" | awk '{print $1, $2, $3}')
        retry_box_z=$(calculate_retry_box_z "$current_box_z" "$mol_count" "$actual_inserted")
        log_info "  ${mol_name} 首次仅插入 ${actual_inserted}/${mol_count} 个分子，改为直接放大盒子后重试一次"
        rm -f "$next_output"

        retry_input=".insert_retry_${step_index}.gro"
        expand_box_z_for_retry "$attempt_input" "$retry_input" "$retry_box_z"
        log_info "  使用放大后的盒子再次插入 ${mol_name}，目标数量 ${mol_count}"
        gmx insert-molecules -f "$retry_input" -ci "${mol_name}.gro" -nmol "$mol_count" -o "$next_output" >> "$LOG_FILE" 2>&1

        if [ ! -f "$next_output" ]; then
            log_error "放大盒子后分子插入失败，未生成 $next_output"
            exit 1
        fi

        actual_inserted=$(count_inserted_molecules "$retry_input" "$next_output" "$molecule_atom_count")
        if [ "$actual_inserted" -ne "$mol_count" ]; then
            log_error "${mol_name} 在直接放大盒子到 Z=${retry_box_z} 后仍仅插入 ${actual_inserted}/${mol_count} 个分子，停止以避免生成错误拓扑"
            exit 1
        fi

        log_info "  ✓ ${mol_name} 在放大盒子后已完整插入 ${actual_inserted} 个分子"
    fi

    inserted_gas_molecules+=("$mol_name:$actual_inserted")
    if [ "$current_input" != "npt_expanded.gro" ] && [ -f "$current_input" ] && [ "$current_input" != "$attempt_input" ]; then
        rm -f "$current_input"
    fi
    if [ -n "$retry_input" ] && [ -f "$retry_input" ]; then
        rm -f "$retry_input"
    fi
    current_input="$next_output"
    step_index=$((step_index + 1))
done

# 验证生成文件
if [ ! -f "system_with_gas.gro" ]; then
    log_error "未生成 system_with_gas.gro"
    exit 1
fi

# 验证原子数增加
output_atoms=$(sed -n '2p' system_with_gas.gro | awk '{print $1}')
log_info "插入后原子数: $output_atoms"

if [ "$output_atoms" -le "$input_atoms" ]; then
    log_error "分子插入失败：原子数未增加"
    exit 1
fi

added_atoms=$((output_atoms - input_atoms))
log_success "成功插入 $added_atoms 个原子"

log_info "步骤 7: 在原始 topol.top 基础上合并 task4 分子参数"

base_topology="topol.top"
if [ ! -f "$base_topology" ]; then
    log_error "缺少基础拓扑文件: $base_topology"
    exit 1
fi

for mol_pair in "${inserted_gas_molecules[@]}"; do
    mol_name="${mol_pair%%:*}"
    if [ ! -f "${mol_name}.itp" ]; then
        log_error "缺少 task4 分子拓扑: ${mol_name}.itp"
        exit 1
    fi
done

gas_molecules_str="${gas_molecules[*]}"
inserted_gas_molecules_str="${inserted_gas_molecules[*]}"

merge_vle_topology "$base_topology" "$gas_molecules_str" "$inserted_gas_molecules_str" "VLE_topol.top"

log_info "已写回合并后的 atomtypes 备份: 原子类型.txt"
log_success "VLE_topol.top 生成完成"

log_info "步骤 9: 最终验证"

for target_file in system_with_gas.gro VLE_topol.top; do
    if grep -Eq '(^|[^A-Za-z0-9])(MOL|UNL)([^A-Za-z0-9]|$)' "$target_file"; then
        log_error "检测到未替换的通用残基名，文件检查失败: $target_file"
        exit 1
    fi
    log_info "  ✓ $target_file 中未检测到 MOL/UNL"
done

missing_includes=0
for mol_pair in "${inserted_gas_molecules[@]}"; do
    mol_name="${mol_pair%%:*}"
    if ! grep -q "#include \"${mol_name}.itp\"" "VLE_topol.top"; then
        log_info "警告: ${mol_name}.itp 可能未被正确包含"
        missing_includes=1
    fi
done

if [ $missing_includes -eq 0 ]; then
    log_info "所有 itp 文件均已包含"
fi

molecule_types=$(awk '/\[ molecules \]/,0' "VLE_topol.top" | grep -v '^\[' | grep -v '^;' | grep -v '^$' | wc -l)
log_info "VLE 系统包含 $molecule_types 种分子类型"

log_success "=== VLE 系统构建完成 ==="
log_info "输出文件:"
log_info "  - system_with_gas.gro"
log_info "  - VLE_topol.top"
log_info "  - 原子类型.txt"
