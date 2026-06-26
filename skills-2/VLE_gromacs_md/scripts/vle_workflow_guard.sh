#!/bin/bash

DEFAULT_GROMACS_ENV_SCRIPT="${DEFAULT_GROMACS_ENV_SCRIPT:-/media/smh/d/gromacs/bin/GMXRC}"
MAX_LOCAL_CPUS="${MAX_LOCAL_CPUS:-12}"

guard_log_info() {
    local msg="$*"
    if declare -F log_info > /dev/null 2>&1; then
        log_info "$msg"
    else
        echo "$msg"
    fi
}

guard_log_error() {
    local msg="$*"
    if declare -F log_error > /dev/null 2>&1; then
        log_error "$msg"
    else
        echo "$msg" >&2
    fi
}

resolve_runtime_dir() {
    local fallback_dir="${1:-$(pwd)}"
    local resolved_dir=""

    if [ -n "${WORK_DIR:-}" ]; then
        resolved_dir="$WORK_DIR"
    else
        resolved_dir="$fallback_dir"
    fi

    if [ ! -d "$resolved_dir" ]; then
        guard_log_error "运行目录不存在: $resolved_dir"
        return 1
    fi

    printf '%s\n' "$resolved_dir"
}

enter_runtime_dir() {
    local fallback_dir="${1:-$(pwd)}"
    local resolved_dir
    resolved_dir=$(resolve_runtime_dir "$fallback_dir") || return 1
    cd "$resolved_dir" || {
        guard_log_error "无法切换到运行目录: $resolved_dir"
        return 1
    }
    export WORK_DIR="$resolved_dir"
    guard_log_info "运行目录: $resolved_dir"
}

cap_cpu_threads() {
    local requested="${1:-1}"
    local capped

    if ! [[ "$requested" =~ ^[0-9]+$ ]] || [ "$requested" -lt 1 ]; then
        requested=1
    fi

    capped="$requested"
    if [ "$capped" -gt "$MAX_LOCAL_CPUS" ]; then
        guard_log_info "线程数 $requested 超过本地默认上限，自动下调为 $MAX_LOCAL_CPUS"
        capped="$MAX_LOCAL_CPUS"
    fi

    printf '%s\n' "$capped"
}

load_gromacs_env() {
    local candidate
    local source_target
    local had_nounset=0

    if command -v gmx > /dev/null 2>&1 && [ -n "${GMXBIN:-}" ]; then
        guard_log_info "GROMACS 环境已就绪"
        return 0
    fi

    for candidate in "$@"; do
        if [ -n "$candidate" ] && [ -f "$candidate" ]; then
            source_target="$candidate"
            if [ "$(basename "$candidate")" = "GMXRC" ] && [ -f "${candidate}.bash" ]; then
                source_target="${candidate}.bash"
            fi
            guard_log_info "加载 GROMACS 环境: $source_target"
            if [[ $- == *u* ]]; then
                had_nounset=1
                set +u
            fi
            source "$source_target"
            if [ "$had_nounset" -eq 1 ]; then
                set -u
            fi
            export GMXRC="$source_target"
            break
        fi
    done

    if ! command -v gmx > /dev/null 2>&1; then
        guard_log_error "gmx 命令不可用，请确认环境脚本是否存在且可用"
        return 1
    fi

    guard_log_info "GROMACS 环境加载成功"
}

copy_topology_dependencies() {
    local source_dir="$1"
    local target_dir="$2"
    local pattern
    local file

    mkdir -p "$target_dir"
    shopt -s nullglob
    for pattern in '*.itp' '*.top' '原子类型.txt'; do
        for file in "$source_dir"/$pattern; do
            if [ -f "$file" ]; then
                cp "$file" "$target_dir/"
            fi
        done
    done
    shopt -u nullglob
}
