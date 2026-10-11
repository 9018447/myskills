#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vle_workflow_guard.sh"
RUN_DIR="${RUN_DIR:-}"
ENV_FILE="${LOCAL_ENV_FILE:-$SCRIPT_DIR/.gromacs_local.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Missing env file: $ENV_FILE" >&2
    exit 1
fi

source "$ENV_FILE"

PIPELINE_NAME="${PIPELINE_NAME:-local-md}"
STRUCTURE_FILE="${STRUCTURE_FILE:-box.pdb}"
TOPOLOGY_FILE="${TOPOLOGY_FILE:-topol.top}"
MDP_DIR="${MDP_DIR:-md_mdp}"
START_STAGE="${START_STAGE:-em}"
START_CHECKPOINT="${START_CHECKPOINT:-}"
RUN_NVT="${RUN_NVT:-true}"
RESUME_STAGES="${RESUME_STAGES:-false}"
EM_ONLY="${EM_ONLY:-false}"
NTMPI="${NTMPI:-1}"
NTOMP="${NTOMP:-12}"
USE_GPU="${USE_GPU:-true}"
GPU_FLAGS="${GPU_FLAGS:-}"
GMX_SOURCE="${GMX_SOURCE:-$DEFAULT_GROMACS_ENV_SCRIPT}"
CHECKPOINT_MINUTES="${CHECKPOINT_MINUTES:-15}"
MAXWARN="${MAXWARN:-5}"

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

resolved_gpu_flags() {
    if [ "$USE_GPU" = true ]; then
        if [ -n "$GPU_FLAGS" ]; then
            printf '%s\n' "$GPU_FLAGS"
        else
            printf '%s\n' '-pme gpu'
        fi
    else
        printf '%s\n' ''
    fi
}

stage_done() {
    local stage="$1"
    [ -f "$stage.gro" ] || [ -f "$stage.edr" ] || [ -f "$stage.xtc" ]
}

run_mdrun() {
    local stage="$1"
    local cpi_args=()
    local gpu_args
    gpu_args=$(resolved_gpu_flags)
    if [ "$RESUME_STAGES" = true ] && [ -f "$stage.cpt" ]; then
        cpi_args=(-cpi "$stage.cpt")
    fi

    if [ "$stage" = "em" ]; then
        unset OMP_NUM_THREADS
        gmx mdrun -v -deffnm "$stage" -pin on -ntmpi 1 -cpt "$CHECKPOINT_MINUTES" -cpo "$stage.cpt" "${cpi_args[@]}"
    else
        export OMP_NUM_THREADS="$NTOMP"
        if [ "$USE_GPU" = true ]; then
            gmx mdrun -v -deffnm "$stage" -pin on -ntmpi "$NTMPI" -ntomp "$NTOMP" -cpt "$CHECKPOINT_MINUTES" -cpo "$stage.cpt" "${cpi_args[@]}" $gpu_args
        else
            gmx mdrun -v -deffnm "$stage" -pin on -ntmpi "$NTMPI" -ntomp "$NTOMP" -cpt "$CHECKPOINT_MINUTES" -cpo "$stage.cpt" "${cpi_args[@]}"
        fi
    fi
}

run_stage() {
    local stage="$1"
    local mdp_name="$2"
    local structure_input="$3"
    local checkpoint_input="$4"

    if [ "$RESUME_STAGES" = true ] && stage_done "$stage"; then
        log "$stage already completed, skipping"
        return 0
    fi

    if [ "$RESUME_STAGES" = true ] && [ -f "$stage.tpr" ] && [ -f "$stage.cpt" ] && [ ! -f "$stage.gro" ]; then
        log "Resuming $stage from checkpoint"
        run_mdrun "$stage"
        return 0
    fi

    local grompp_cmd=(gmx grompp -f "$MDP_DIR/$mdp_name" -c "$structure_input" -p "$TOPOLOGY_FILE" -o "$stage.tpr" -maxwarn "$MAXWARN")
    if [ -n "$checkpoint_input" ] && [ -f "$checkpoint_input" ]; then
        grompp_cmd+=( -t "$checkpoint_input" )
    fi

    log "Preparing $stage"
    "${grompp_cmd[@]}"
    log "Running $stage"
    run_mdrun "$stage"
}

RUN_DIR="$(resolve_runtime_dir "${RUN_DIR:-$SCRIPT_DIR}")"
cd "$RUN_DIR"
NTOMP="$(cap_cpu_threads "$NTOMP")"
load_gromacs_env "$GMX_SOURCE" "${GMXRC:-}"

if [ ! -f "$STRUCTURE_FILE" ]; then
    echo "Missing structure file: $STRUCTURE_FILE" >&2
    exit 1
fi

if [ ! -f "$TOPOLOGY_FILE" ]; then
    echo "Missing topology file: $TOPOLOGY_FILE" >&2
    exit 1
fi

if [ ! -d "$MDP_DIR" ]; then
    echo "Missing MDP directory: $MDP_DIR" >&2
    exit 1
fi

log "Pipeline: $PIPELINE_NAME"

if [ "$START_STAGE" = "em" ]; then
    run_stage em minim.mdp "$STRUCTURE_FILE" ""
    equil_input="em.gro"
    equil_checkpoint=""
else
    log "Continuing pipeline from $START_STAGE using $STRUCTURE_FILE"
    equil_input="$STRUCTURE_FILE"
    equil_checkpoint="$START_CHECKPOINT"
fi

if [ "$EM_ONLY" = true ]; then
    log "EM-only mode enabled, stopping after minimization"
    exit 0
fi

if [ -f "VLE_topol.top" ]; then
    log "Detected VLE simulation, using VLE-specific MDP files"
    run_stage vle_npt vle_npt.mdp "em.gro" ""
    run_stage vle_nvt vle_nvt.mdp "vle_npt.gro" "vle_npt.cpt"
else
    if [ "$START_STAGE" = "em" ] && [ "$RUN_NVT" = true ]; then
        run_stage nvt nvt.mdp "$equil_input" "$equil_checkpoint"
        equil_input="nvt.gro"
        equil_checkpoint="nvt.cpt"
    fi

    run_stage npt_precompress npt_precompress.mdp "$equil_input" "$equil_checkpoint"
    run_stage npt_release npt_release.mdp "npt_precompress.gro" "npt_precompress.cpt"
    run_stage npt npt.mdp "npt_release.gro" "npt_release.cpt"
    run_stage md md.mdp "npt.gro" "npt.cpt"
fi

log "Pipeline completed"
