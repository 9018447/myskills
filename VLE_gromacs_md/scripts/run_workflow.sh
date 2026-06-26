#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
WORK_DIR="$(pwd)"
GUARD_SCRIPT="$SCRIPT_DIR/vle_workflow_guard.sh"

source "$GUARD_SCRIPT"
source "$SCRIPT_DIR/lib/log.sh"
source "$SCRIPT_DIR/lib/status.sh"
source "$SCRIPT_DIR/lib/vle_utils.sh"

MODE="local-homogeneous"
NTMPI=1
NTOMP=12
USE_GPU=true
USE_PUEUE=true
SETUP_ONLY=false
MD_ONLY=false
RUN_NVT=true
VERBOSE=${GROMACS_VERBOSE:-false}
DRY_RUN=false
CHECKPOINT_MINUTES=15
MAXWARN=5
SHOW_STATUS=false

LOG_FILE="workflow.log"
> "$LOG_FILE"

usage() {
    cat <<'EOF'
GROMACS VLE/MD Workflow

Usage: bash scripts/run_workflow.sh [options]

Workflow Types:
  --mode homogeneous        Build homogeneous liquid system (default)
  --mode gas-liquid         Build vapor-liquid equilibrium system
  --mode post-homogeneous-vle   Continue VLE from existing homogeneous

Execution Control:
  --init-only, --setup-only     Initialize only, no simulation
  --resume-md, --md-only        Resume MD from existing results
  --enable-nvt, --run-nvt       Enable NVT equilibration
  --dry-run                     Preview commands
  --status                      Show current progress and exit

Parallel Computing:
  --threads N              Quick set: OpenMP=N, MPI=1 (default: 12)
  --mpi-threads N          MPI processes (default: 1)
  --omp-threads N          OpenMP threads per MPI (default: 12)

Hardware & Output:
  --no-gpu, --cpu-only     Disable GPU
  --no-pueue               Run stages in foreground (default: use pueue)
  --verbose                Verbose output

Advanced:
  --checkpoint-minutes N   Checkpoint interval (default: 15)
  --maxwarn N              grompp max warnings (default: 5)

Legacy (backward compatible): --ntmpi N, --ntomp N
EOF
}

detect_and_source_gmxrc() {
    local gmxrc_path=""
    if [ -f "$DEFAULT_GROMACS_ENV_SCRIPT" ]; then
        gmxrc_path="$DEFAULT_GROMACS_ENV_SCRIPT"
    elif [ -n "${GMXRC:-}" ] && [ -f "$GMXRC" ]; then
        gmxrc_path="$GMXRC"
    elif [ -f "$HOME/.bashrc" ]; then
        gmxrc_path=$(python3 - <<'PY'
from pathlib import Path
import re
text = Path.home().joinpath('.bashrc').read_text(errors='ignore')
match = re.search(r'source\s+([^\s]+/GMXRC)', text)
print(match.group(1) if match else '')
PY
)
    fi

    if [ -z "$gmxrc_path" ] || [ ! -f "$gmxrc_path" ]; then
        gmxrc_path="/media/smh/d/gromacs/bin/GMXRC"
    fi

    if [ ! -f "$gmxrc_path" ]; then
        log_error "未找到 GMXRC 文件: $gmxrc_path"
        return 1
    fi

    load_gromacs_env "$gmxrc_path"
    log_success "GROMACS 环境加载成功"
}

check_need_setup() {
    if [ ! -d "$WORK_DIR/md_mdp" ] || [ ! -d "$WORK_DIR/scripts" ] || [ ! -f "$WORK_DIR/todolist.json" ] || [ ! -f "$WORK_DIR/todolist.md" ]; then
        return 0
    fi
    return 1
}

run_setup() {
    log_section "========================================"
    log_section "初始化工作环境"
    log_section "========================================"

    if [ ! -f "$WORK_DIR/todolist.json" ] && [ -f "$SKILL_ROOT/assets/todolist.json" ]; then
        cp "$SKILL_ROOT/assets/todolist.json" "$WORK_DIR/todolist.json"
        log_success "创建 todolist.json"
    fi

    if [ ! -f "$WORK_DIR/todolist.md" ] && [ -f "$SKILL_ROOT/todolist.md" ]; then
        cp "$SKILL_ROOT/todolist.md" "$WORK_DIR/todolist.md"
        log_success "创建 todolist.md"
    fi

    mkdir -p "$WORK_DIR/md_mdp"
    if [ -d "$SKILL_ROOT/assets/md_mdp" ]; then
        cp "$SKILL_ROOT/assets/md_mdp"/*.mdp "$WORK_DIR/md_mdp/"
        log_success "同步 MDP 文件到 md_mdp/"
    fi

    mkdir -p "$WORK_DIR/scripts"
    local script_files=(
        run_workflow.sh
        local_stage_runner.sh
        check_progress.sh
        validate_todolist.py
        3_task_genVLEbox.sh
        4_prepare_molecules.sh
        5_build_system.sh
        5_beta_VLE.sh
        6_VLE_build_system.sh
        expand_box.sh
        vle_workflow_guard.sh
        resp.sh
        gentop.sh
        fch2xyz.sh
        modify_resname.py
    )

    local script_name
    for script_name in "${script_files[@]}"; do
        if [ -f "$SCRIPT_DIR/$script_name" ]; then
            local src="$SCRIPT_DIR/$script_name"
            local dst="$WORK_DIR/scripts/$script_name"
            if [ "$src" != "$dst" ]; then
                cp "$src" "$dst"
                chmod +x "$dst" 2>/dev/null || true
            fi
        fi
    done

    mkdir -p "$WORK_DIR/scripts/lib"
    if [ -d "$SCRIPT_DIR/lib" ]; then
        local src_dir="$SCRIPT_DIR/lib"
        local dst_dir="$WORK_DIR/scripts/lib"
        if [ "$src_dir" != "$dst_dir" ]; then
            cp "$src_dir"/*.sh "$dst_dir/"
        fi
    fi

    log_success "同步工作流脚本到 scripts/"
}

find_mdp_dir() {
    local base_dir="$1"
    if [ -d "$base_dir/md_mdp" ]; then
        printf '%s\n' "$base_dir/md_mdp"
        return 0
    fi
    if [ -d "$base_dir/../md_mdp" ]; then
        printf '%s\n' "$base_dir/../md_mdp"
        return 0
    fi
    return 1
}

ensure_vle_restart_ready() {
    local base_structure=""
    ensure_file "$WORK_DIR/topol.top" "topol.top"
    if ! base_structure=$(resolve_existing_vle_base_structure); then
        log_error "未找到可用于 VLE 的基础结构，请提供 md.gro、md*.gro 或 npt.gro"
        exit 1
    fi
    log_info "检测到可复用的 VLE 基础结构: $base_structure"
}

gpu_flags_local() {
    if [ "$USE_GPU" = true ]; then
        printf '%s\n' '-pme gpu'
    else
        printf '%s\n' ''
    fi
}

prepare_homogeneous_system() {
    export VERBOSE LOG_FILE
    log_section "[prepare] 均相体系构建"
    run_cmd bash "$WORK_DIR/scripts/4_prepare_molecules.sh"
    run_cmd bash "$WORK_DIR/scripts/3_task_genVLEbox.sh"
    run_cmd bash "$WORK_DIR/scripts/5_build_system.sh"
    ensure_file "$WORK_DIR/box.pdb" "box.pdb"
    ensure_file "$WORK_DIR/topol.top" "topol.top"
    log_success "均相体系准备完成"
}

run_gmx_stage() {
    local sim_dir="$1"
    local mdp="$2"
    local input="$3"
    local topo="$4"
    local stage_name="$5"
    local extra_args="${6:-}"
    (
        cd "$sim_dir"
        run_cmd gmx grompp -f "$mdp" -c "$input" -p "$topo" -o "${stage_name}.tpr" -maxwarn "$MAXWARN" $extra_args
        if [ "$stage_name" = "em" ]; then
            run_cmd gmx mdrun -v -deffnm "$stage_name" -pin on -ntmpi 1
        else
            run_cmd gmx mdrun -deffnm "$stage_name" -pin on -ntmpi "$NTMPI" -ntomp "$NTOMP" $(gpu_flags_local)
        fi
    )
    log_success "${stage_name} 完成: $sim_dir"
}

run_em_stage() {
    local sim_dir="$1"
    local structure_file="$2"
    local topology_file="$3"
    local mdp_dir="$4"
    run_gmx_stage "$sim_dir" "$mdp_dir/minim.mdp" "$structure_file" "$topology_file" "em"
}

run_nvt_stage() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    run_gmx_stage "$sim_dir" "$mdp_dir/nvt.mdp" "em.gro" "$topology_file" "nvt"
}

run_npt_precompress_stage() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    local input_file="em.gro"
    local checkpoint_args=()

    if [ -f "$sim_dir/nvt.gro" ]; then
        input_file="nvt.gro"
        if [ -f "$sim_dir/nvt.cpt" ]; then
            checkpoint_args=(-t nvt.cpt)
        fi
    fi

    run_gmx_stage "$sim_dir" "$mdp_dir/npt_precompress.mdp" "$input_file" "$topology_file" "npt_precompress" "${checkpoint_args[*]}"
}

run_npt_release_stage() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    run_gmx_stage "$sim_dir" "$mdp_dir/npt_release.mdp" "npt_precompress.gro" "$topology_file" "npt_release" "-t npt_precompress.cpt"
}

run_npt_stage() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    run_gmx_stage "$sim_dir" "$mdp_dir/npt.mdp" "npt_release.gro" "$topology_file" "npt" "-t npt_release.cpt"
}

run_homogeneous_npt_pipeline() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"

    run_npt_precompress_stage "$sim_dir" "$topology_file" "$mdp_dir" "$gpu_flag"
    run_npt_release_stage "$sim_dir" "$topology_file" "$mdp_dir" "$gpu_flag"
    run_npt_stage "$sim_dir" "$topology_file" "$mdp_dir" "$gpu_flag"
}

write_local_background_env() {
    local sim_dir="$1"
    local structure_file="$2"
    local topology_file="$3"
    local mdp_dir="$4"
    local gpu_flag="$5"
    local start_stage="em"
    local start_checkpoint=""

    if [ "$structure_file" = "em.gro" ]; then
        start_checkpoint="em.cpt"
    elif [ "$structure_file" = "nvt.gro" ]; then
        start_checkpoint="nvt.cpt"
    fi

    mkdir -p "$sim_dir/scripts"
    cat > "$sim_dir/scripts/.gromacs_local.env" <<EOF
RUN_DIR="$sim_dir"
PIPELINE_NAME="local-background"
STRUCTURE_FILE="$structure_file"
TOPOLOGY_FILE="$topology_file"
MDP_DIR="$mdp_dir"
START_STAGE="$start_stage"
START_CHECKPOINT="$start_checkpoint"
RUN_NVT="$RUN_NVT"
RESUME_STAGES=true
EM_ONLY=false
NTMPI="$NTMPI"
NTOMP="$NTOMP"
USE_GPU="$USE_GPU"
GPU_FLAGS="$gpu_flag"
GMX_SOURCE="${GMXRC:-}"
EOF
}

run_md_background() {
    local sim_dir="$1"
    local structure_file="$2"
    local topology_file="$3"
    local mdp_dir="$4"
    local gpu_flag="$5"
    local runner_path="$WORK_DIR/scripts/local_stage_runner.sh"
    write_local_background_env "$sim_dir" "$structure_file" "$topology_file" "$mdp_dir" "$gpu_flag"
    (
        cd "$sim_dir"
        pueue add -- bash "$runner_path"
    )
    log_success "后台管线已提交到 pueue 队列: $sim_dir"
}

run_full_pipeline_via_pueue() {
    local sim_dir="$1"
    local structure_file="$2"
    local topology_file="$3"
    local mdp_dir="$4"
    local gpu_flag="$5"
    local pipeline_name="${6:-local-md}"
    local runner_path="$WORK_DIR/scripts/local_stage_runner.sh"
    write_local_background_env "$sim_dir" "$structure_file" "$topology_file" "$mdp_dir" "$gpu_flag"
    (
        cd "$sim_dir"
        pueue add -- bash "$runner_path"
    )
    log_success "完整管线 ($pipeline_name) 已提交到 pueue 队列: $sim_dir"
    log_info "使用 'pueue list' 查看进度，'pueue log' 查看输出"
}

run_vle_pipeline_via_pueue() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    local runner_path="$WORK_DIR/scripts/local_stage_runner.sh"
    write_local_background_env "$sim_dir" "system_with_gas.gro" "$topology_file" "$mdp_dir" "$gpu_flag"
    (
        cd "$sim_dir"
        pueue add -- bash "$runner_path"
    )
    log_success "VLE 管线已提交到 pueue 队列: $sim_dir"
    log_info "使用 'pueue list' 查看进度，'pueue log' 查看输出"
}

run_vle_prepare_build() {
    log_section "[VLE] 运行 5_beta 和 6"
    if [ -f "$WORK_DIR/VLE_MD/system_with_gas.gro" ] && [ -f "$WORK_DIR/VLE_MD/VLE_topol.top" ]; then
        log_info "检测到现有 VLE 构建产物，跳过 5_beta/6 重新构建"
    elif [ -f "$WORK_DIR/VLE_MD/npt_expanded.gro" ] && [ -f "$WORK_DIR/VLE_MD/topol.top" ] && [ -f "$WORK_DIR/VLE_MD/todolist.json" ]; then
        log_info "检测到现有 VLE 准备产物，跳过 5_beta，仅重新执行 6_VLE_build_system.sh"
        (
            cd "$WORK_DIR/VLE_MD"
            run_cmd bash "$WORK_DIR/scripts/6_VLE_build_system.sh"
        )
    else
        run_cmd bash "$WORK_DIR/scripts/5_beta_VLE.sh"
        ensure_file "$WORK_DIR/VLE_MD/npt_expanded.gro" "VLE_MD/npt_expanded.gro"
        (
            cd "$WORK_DIR/VLE_MD"
            run_cmd bash "$WORK_DIR/scripts/6_VLE_build_system.sh"
        )
    fi
    ensure_file "$WORK_DIR/VLE_MD/system_with_gas.gro" "VLE_MD/system_with_gas.gro"
    ensure_file "$WORK_DIR/VLE_MD/VLE_topol.top" "VLE_MD/VLE_topol.top"
    log_success "VLE 体系构建完成"
}

ensure_local_setup_if_needed() {
    if check_need_setup; then
        run_setup
    fi
}

validate_todolist() {
    local mode="${1:-all}"
    local validator="$WORK_DIR/scripts/validate_todolist.py"
    if [ ! -f "$validator" ]; then
        log_error "找不到校验脚本: validate_todolist.py"
        exit 1
    fi
    if ! python3 "$validator" "$WORK_DIR/todolist.json" --mode "$mode"; then
        log_error "todolist.json 校验失败，workflow 中止"
        exit 1
    fi
}

run_local_homogeneous() {
    ensure_local_setup_if_needed
    detect_and_source_gmxrc
    local mdp_dir
    mdp_dir=$(find_mdp_dir "$WORK_DIR") || {
        log_error "未找到 md_mdp 目录"
        exit 1
    }
    local gpu_flag
    gpu_flag=$(gpu_flags_local)

    if [ "$MD_ONLY" = false ]; then
        prepare_homogeneous_system
        if [ "$USE_PUEUE" = true ]; then
            run_full_pipeline_via_pueue "$WORK_DIR" box.pdb topol.top "$mdp_dir" "$gpu_flag" "均相 EM→NVT→NPT→MD"
        else
            run_em_stage "$WORK_DIR" box.pdb topol.top "$mdp_dir"
            if [ "$RUN_NVT" = true ]; then
                run_nvt_stage "$WORK_DIR" topol.top "$mdp_dir" "$gpu_flag"
            fi
            local start_structure="em.gro"
            if [ "$RUN_NVT" = true ]; then
                start_structure="nvt.gro"
            fi
            run_md_background "$WORK_DIR" "$start_structure" topol.top "$mdp_dir" "$gpu_flag"
        fi
    else
        ensure_file "$WORK_DIR/topol.top" "topol.top"
        local start_structure=""
        if [ -f "$WORK_DIR/nvt.gro" ]; then
            start_structure="nvt.gro"
        elif [ -f "$WORK_DIR/em.gro" ]; then
            start_structure="em.gro"
        else
            log_error "--md-only 需要已有 em.gro 或 nvt.gro"
            exit 1
        fi
        if [ "$USE_PUEUE" = true ]; then
            run_full_pipeline_via_pueue "$WORK_DIR" "$start_structure" topol.top "$mdp_dir" "$gpu_flag" "均相续跑 NPT→MD"
        else
            run_md_background "$WORK_DIR" "$start_structure" topol.top "$mdp_dir" "$gpu_flag"
        fi
    fi
}

prepare_homogeneous_until_npt() {
    ensure_local_setup_if_needed
    detect_and_source_gmxrc
    local mdp_dir
    mdp_dir=$(find_mdp_dir "$WORK_DIR") || {
        log_error "未找到 md_mdp 目录"
        exit 1
    }
    local gpu_flag
    gpu_flag=$(gpu_flags_local)

    if [ "$MD_ONLY" = false ]; then
        prepare_homogeneous_system
        run_em_stage "$WORK_DIR" box.pdb topol.top "$mdp_dir"
        if [ "$RUN_NVT" = true ]; then
            run_nvt_stage "$WORK_DIR" topol.top "$mdp_dir" "$gpu_flag"
        fi
        run_homogeneous_npt_pipeline "$WORK_DIR" topol.top "$mdp_dir" "$gpu_flag"
    else
        ensure_file "$WORK_DIR/npt.gro" "npt.gro"
        ensure_file "$WORK_DIR/topol.top" "topol.top"
    fi
}

run_vle_npt_stage() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    (
        cd "$sim_dir"
        run_cmd gmx grompp -f "$mdp_dir/vle_npt.mdp" -c em.gro -p "$topology_file" -o vle_npt.tpr -maxwarn 5
        run_cmd gmx mdrun -deffnm vle_npt -pin on -ntmpi "$NTMPI" -ntomp "$NTOMP" $gpu_flag
    )
    log_success "VLE NPT (5ns semiisotropic) 完成: $sim_dir"
}

run_vle_nvt_stage() {
    local sim_dir="$1"
    local topology_file="$2"
    local mdp_dir="$3"
    local gpu_flag="$4"
    (
        cd "$sim_dir"
        run_cmd gmx grompp -f "$mdp_dir/vle_nvt.mdp" -c vle_npt.gro -t vle_npt.cpt -p "$topology_file" -o vle_nvt.tpr -maxwarn 5
        run_cmd gmx mdrun -deffnm vle_nvt -pin on -ntmpi "$NTMPI" -ntomp "$NTOMP" $gpu_flag
    )
    log_success "VLE NVT (10ns production) 完成: $sim_dir"
}

run_vle_md_from_existing_npt() {
    detect_and_source_gmxrc
    run_vle_prepare_build
    local vle_dir="$WORK_DIR/VLE_MD"
    local mdp_dir
    mdp_dir=$(find_mdp_dir "$vle_dir") || {
        log_error "VLE_MD 附近未找到 md_mdp 目录"
        exit 1
    }
    local gpu_flag
    gpu_flag=$(gpu_flags_local)

    if [ "$USE_PUEUE" = true ]; then
        run_vle_pipeline_via_pueue "$vle_dir" VLE_topol.top "$mdp_dir" "$gpu_flag"
    else
        run_em_stage "$vle_dir" system_with_gas.gro VLE_topol.top "$mdp_dir"
        run_vle_npt_stage "$vle_dir" VLE_topol.top "$mdp_dir" "$gpu_flag"
        run_vle_nvt_stage "$vle_dir" VLE_topol.top "$mdp_dir" "$gpu_flag"
        log_success "VLE MD 模拟完成 (EM -> NPT 5ns -> NVT 10ns)"
    fi
}

run_local_gas_liquid() {
    if [ -f "$WORK_DIR/topol.top" ] && resolve_existing_vle_base_structure > /dev/null; then
        log_info "检测到已有均相阶段产物，local-gas-liquid 自动切换为续跑 VLE 路径"
        ensure_local_setup_if_needed
    else
        prepare_homogeneous_until_npt
    fi
    run_vle_md_from_existing_npt
}

run_post_homogeneous_vle() {
    ensure_local_setup_if_needed
    ensure_vle_restart_ready
    run_vle_md_from_existing_npt
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --init-only|--setup-only)
            SETUP_ONLY=true
            shift
            ;;
        --resume-md|--md-only)
            MD_ONLY=true
            shift
            ;;
        --enable-nvt|--run-nvt)
            RUN_NVT=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --status)
            SHOW_STATUS=true
            shift
            ;;
        --threads)
            NTOMP="$2"
            NTMPI=1
            shift 2
            ;;
        --mpi-threads)
            NTMPI="$2"
            shift 2
            ;;
        --omp-threads)
            NTOMP="$2"
            shift 2
            ;;
        --ntmpi)
            NTMPI="$2"
            shift 2
            ;;
        --ntomp)
            NTOMP="$2"
            shift 2
            ;;
        --no-gpu|--cpu-only)
            USE_GPU=false
            shift
            ;;
        --no-pueue)
            USE_PUEUE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --checkpoint-minutes)
            CHECKPOINT_MINUTES="$2"
            shift 2
            ;;
        --maxwarn)
            MAXWARN="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            echo "使用 --help 查看可用选项"
            exit 1
            ;;
    esac
done

# 模式名映射：用户友好的名称 → 内部名称
case "$MODE" in
    homogeneous) MODE="local-homogeneous" ;;
    gas-liquid) MODE="local-gas-liquid" ;;
esac

NTOMP=$(cap_cpu_threads "$NTOMP")

if [ "$SHOW_STATUS" = true ]; then
    show_workflow_status
    exit 0
fi

if [ "$SETUP_ONLY" = true ]; then
    run_setup
    exit 0
fi

validate_todolist all

if [ "$DRY_RUN" = true ]; then
    echo "========================================"
    echo "预演模式 - 将要执行的操作"
    echo "========================================"
    echo ""
    echo "工作流模式: $MODE"
    echo "MPI 线程数: $NTMPI"
    echo "OpenMP 线程数: $NTOMP"
    echo "GPU 加速: $([ "$USE_GPU" = true ] && echo "启用" || echo "禁用")"
    echo "NVT 阶段: $([ "$RUN_NVT" = true ] && echo "启用" || echo "跳过")"
    echo "任务管理: $([ "$USE_PUEUE" = true ] && echo "pueue (后台)" || echo "前台")"
    echo ""
    echo "将要执行的阶段:"
    case "$MODE" in
        local-homogeneous)
            if [ "$MD_ONLY" = false ]; then
                echo "  1. 初始化工作环境 (前台)"
                echo "  2. 均相体系构建 (前台)"
                if [ "$USE_PUEUE" = true ]; then
                    echo "  3. 完整管线 EM → NVT → NPT → MD (pueue 后台)"
                else
                    echo "  3. 能量最小化 (EM) (前台)"
                    if [ "$RUN_NVT" = true ]; then
                        echo "  4. NVT 平衡 (前台)"
                        echo "  5. NPT + MD (pueue 后台)"
                    else
                        echo "  4. NPT + MD (pueue 后台)"
                    fi
                fi
            else
                if [ "$USE_PUEUE" = true ]; then
                    echo "  1. 续跑完整管线 (pueue 后台)"
                else
                    echo "  1. 续跑 NPT + MD (pueue 后台)"
                fi
            fi
            ;;
        local-gas-liquid)
            echo "  1. 检查已有均相产物 (前台)"
            echo "  2. VLE 体系构建 (5_beta + 6) (前台)"
            if [ "$USE_PUEUE" = true ]; then
                echo "  3. VLE 完整管线 EM → NPT → NVT (pueue 后台)"
            else
                echo "  3. VLE EM (前台)"
                echo "  4. VLE NPT 5ns (前台)"
                echo "  5. VLE NVT 10ns (前台)"
            fi
            ;;
        post-homogeneous-vle)
            echo "  1. 检查 VLE 重启条件 (前台)"
            echo "  2. VLE 体系构建 (前台)"
            if [ "$USE_PUEUE" = true ]; then
                echo "  3. VLE 完整管线 EM → NPT → NVT (pueue 后台)"
            else
                echo "  3. VLE EM (前台)"
                echo "  4. VLE NPT 5ns (前台)"
                echo "  5. VLE NVT 10ns (前台)"
            fi
            ;;
    esac
    echo ""
    echo "========================================"
    exit 0
fi

case "$MODE" in
    local-homogeneous)
        run_local_homogeneous
        ;;
    local-gas-liquid)
        run_local_gas_liquid
        ;;
    post-homogeneous-vle)
        run_post_homogeneous_vle
        ;;
    *)
        log_error "不支持的模式: $MODE"
        usage
        exit 1
        ;;
esac
