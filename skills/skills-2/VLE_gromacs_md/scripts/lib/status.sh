#!/bin/bash

STATUS_DONE="✓"
STATUS_RUNNING="▶"
STATUS_PREPARING="◐"
STATUS_NOT_STARTED="✗"

check_stage_status() {
    local stage="$1"
    local dir="${2:-.}"
    if [ -f "$dir/$stage.gro" ] || [ -f "$dir/$stage.edr" ] || [ -f "$dir/$stage.xtc" ]; then
        echo "$STATUS_DONE"
    elif [ -f "$dir/$stage.tpr" ]; then
        if pgrep -f "mdrun.*$stage" > /dev/null 2>&1; then
            echo "$STATUS_RUNNING"
        else
            echo "$STATUS_PREPARING"
        fi
    else
        echo "$STATUS_NOT_STARTED"
    fi
}

check_file_exists() {
    local file="$1"
    local dir="${2:-.}"
    if [ -f "$dir/$file" ]; then
        echo "$STATUS_DONE"
    else
        echo "$STATUS_NOT_STARTED"
    fi
}

show_workflow_status() {
    local work_dir="${WORK_DIR:-$(pwd)}"
    local log_file="${LOG_FILE:-workflow.log}"

    echo "========================================"
    echo "GROMACS 工作流状态"
    echo "========================================"
    echo ""

    if [ -f "$work_dir/VLE_topol.top" ] || [ -d "$work_dir/VLE_MD" ]; then
        echo "工作流类型: VLE 气液共存"
    elif [ -f "$work_dir/topol.top" ]; then
        echo "工作流类型: 均相体系"
    else
        echo "工作流类型: 未初始化"
    fi
    echo ""

    echo "配置文件:"
    echo "  $(check_file_exists todolist.json "$work_dir") todolist.json"
    echo "  $(check_file_exists todolist.md "$work_dir") todolist.md"
    echo ""

    echo "结构文件:"
    echo "  $(check_file_exists box.pdb "$work_dir") box.pdb"
    echo "  $(check_file_exists topol.top "$work_dir") topol.top"
    echo "  $(check_file_exists em.gro "$work_dir") em.gro"
    echo "  $(check_file_exists nvt.gro "$work_dir") nvt.gro"
    echo "  $(check_file_exists npt.gro "$work_dir") npt.gro"
    echo "  $(check_file_exists md.gro "$work_dir") md.gro"
    echo ""

    echo "模拟阶段:"
    echo "  $(check_stage_status em "$work_dir") 能量最小化 (EM)"
    echo "  $(check_stage_status nvt "$work_dir") NVT 平衡"
    echo "  $(check_stage_status npt_precompress "$work_dir") NPT 第一阶段 (强预压缩)"
    echo "  $(check_stage_status npt_release "$work_dir") NPT 第二阶段 (降压)"
    echo "  $(check_stage_status npt "$work_dir") NPT 第三阶段 (正式)"
    echo "  $(check_stage_status md "$work_dir") 生产 MD"
    echo ""

    if [ -d "$work_dir/VLE_MD" ]; then
        echo "VLE 阶段 (VLE_MD/):"
        echo "  $(check_file_exists npt_expanded.gro "$work_dir/VLE_MD") npt_expanded.gro"
        echo "  $(check_file_exists system_with_gas.gro "$work_dir/VLE_MD") system_with_gas.gro"
        echo "  $(check_file_exists VLE_topol.top "$work_dir/VLE_MD") VLE_topol.top"
        echo "  $(check_stage_status em "$work_dir/VLE_MD") VLE EM"
        echo "  $(check_stage_status vle_npt "$work_dir/VLE_MD") VLE NPT (5ns)"
        echo "  $(check_stage_status vle_nvt "$work_dir/VLE_MD") VLE NVT (10ns)"
        echo ""
    fi

    echo "后台任务 (pueue):"
    if command -v pueue &> /dev/null; then
        if pueue status >/dev/null 2>&1; then
            echo "  daemon 状态: 运行中"
            echo ""
            pueue list 2>/dev/null || echo "  队列为空"
        else
            echo "  daemon 状态: 未启动 (运行 'pueue daemon' 启动)"
        fi
    else
        echo "  pueue 未安装 (运行 'cargo install pueue' 安装)"
    fi
    echo ""

    if [ -f "$work_dir/$log_file" ]; then
        echo "最新日志 (最后5行):"
        tail -5 "$work_dir/$log_file"
    fi
}
