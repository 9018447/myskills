#!/bin/bash
# Shared logging library for GROMACS VLE/MD workflow scripts

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

VERBOSE=${VERBOSE:-false}
LOG_FILE=${LOG_FILE:-"workflow.log"}

if [ ! -f "$LOG_FILE" ]; then
    : > "$LOG_FILE"
fi

log_info() {
    echo "$*" >> "$LOG_FILE"
    if [ "$VERBOSE" = true ]; then
        echo "$*"
    fi
}

log_success() {
    local msg="✓ $*"
    echo -e "${GREEN}${msg}${NC}"
    echo "$msg" >> "$LOG_FILE"
}

log_error() {
    local msg="✗ $*"
    echo -e "${RED}${msg}${NC}" >&2
    echo "$msg" >> "$LOG_FILE"
}

log_section() {
    local msg="$*"
    echo -e "${BLUE}${msg}${NC}"
    echo "$msg" >> "$LOG_FILE"
}

run_cmd() {
    if [ "${DRY_RUN:-false}" = true ]; then
        echo "[预演] $*"
        return 0
    fi
    if [ "$VERBOSE" = true ]; then
        "$@"
    else
        "$@" >> "$LOG_FILE" 2>&1
    fi
}

ensure_file() {
    local file_path="$1"
    local label="$2"
    if [ ! -e "$file_path" ]; then
        log_error "$label 不存在: $file_path"
        exit 1
    fi
}
