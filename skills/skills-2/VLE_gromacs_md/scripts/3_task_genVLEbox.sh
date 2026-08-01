#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/log.sh"

# 继承父脚本的 VERBOSE 设置
VERBOSE=${VERBOSE:-false}
LOG_FILE=${LOG_FILE:-"workflow.log"}

# 严格校验 todolist.json
if [ -f "todolist.json" ] && [ -f "$SCRIPT_DIR/validate_todolist.py" ]; then
    python3 "$SCRIPT_DIR/validate_todolist.py" todolist.json --mode all || exit 1
fi

log_info "开始处理任务3：准备GROMACS盒子（气液两相）"

# 检查jq是否安装
if ! command -v jq &> /dev/null; then
    echo "✗ 错误: 需要安装jq工具来解析JSON文件" >&2
    echo "请运行: sudo apt-get install jq (Ubuntu/Debian)" >&2
    echo "或: sudo yum install jq (CentOS/RHEL)" >&2
    exit 1
fi

# 盒子大小：必须通过 BOX_SIZE 环境变量指定
if [ -z "$BOX_SIZE" ]; then
    log_error "必须设置盒子大小: export BOX_SIZE=<长度(Å)>"
    log_error "示例: BOX_SIZE=80 bash 3_task_genVLEbox.sh"
    exit 1
fi

# 创建或清空box.inp文件
> box.inp

# 从JSON文件中提取task3的分子信息
total_molecules=$(jq '.task3.molecules | map(.count) | add' todolist.json)
liquid_molecules=$(jq '[.task3.molecules[] | select(.phase == "l") | .count] | add // 0' todolist.json)
gas_molecules=$(jq '[.task3.molecules[] | select(.phase == "g") | .count] | add // 0' todolist.json)

log_info "总分子数: $total_molecules"
log_info "液相分子数: $liquid_molecules"
log_info "气相分子数: $gas_molecules"

# 设置盒子区域
if [ "$gas_molecules" -eq 0 ] && [ "$liquid_molecules" -gt 0 ]; then
    # 均相：所有分子放在同一个立方体内
    liquid_bottom=0.0
    liquid_top=$BOX_SIZE
    gas_bottom=$BOX_SIZE
    gas_top=$BOX_SIZE
    log_info "均相盒子: ${BOX_SIZE} × ${BOX_SIZE} × ${BOX_SIZE} Å"
else
    # 气液两相：液相占下半部分，气相占上半部分
    half_box=$(echo "scale=2; $BOX_SIZE / 2" | bc)
    liquid_bottom=0.0
    liquid_top=$half_box
    gas_bottom=$half_box
    gas_top=$BOX_SIZE
    log_info "VLE盒子: ${BOX_SIZE} × ${BOX_SIZE} × ${BOX_SIZE} Å"
    log_info "液相区域: z = ${liquid_bottom} - ${liquid_top} Å"
    log_info "气相区域: z = ${gas_bottom} - ${gas_top} Å"
fi

# 写入box.inp文件头
cat >> box.inp << EOF
#
# Box configuration generated from todolist.json task3 (气液两相)
#

tolerance 2.0
add_box_sides 1.2
filetype pdb
output box.pdb

EOF

# 处理液相分子
log_info "处理液相分子:"
jq -r '.task3.molecules[] | select(.phase == "l") | "\(.name) \(.count)"' todolist.json | while read -r molecule count; do
    log_info "  添加液相分子: $molecule 数量: $count"
    cat >> box.inp << EOF
# Add $molecule molecules (液相)
structure ${molecule}.pdb
  number $count
  inside box 0. 0. $liquid_bottom $BOX_SIZE $BOX_SIZE $liquid_top
end structure

EOF
done

# 处理气相分子
log_info "处理气相分子:"
jq -r '.task3.molecules[] | select(.phase == "g") | "\(.name) \(.count)"' todolist.json | while read -r molecule count; do
    log_info "  添加气相分子: $molecule 数量: $count"
    cat >> box.inp << EOF
# Add $molecule molecules (气相)
structure ${molecule}.pdb
  number $count
  inside box 0. 0. $gas_bottom $BOX_SIZE $BOX_SIZE $gas_top
end structure

EOF
done

log_info "box.inp 文件已生成"
[ "$VERBOSE" = true ] && cat box.inp
log_success "任务3完成"
