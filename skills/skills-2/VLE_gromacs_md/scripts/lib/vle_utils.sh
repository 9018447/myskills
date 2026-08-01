#!/bin/bash

resolve_existing_vle_base_structure() {
    local preferred="${VLE_BASE_STRUCTURE:-}"
    local candidate=""
    local work_dir="${WORK_DIR:-$(pwd)}"

    if [ -n "$preferred" ] && [ -f "$work_dir/$preferred" ]; then
        printf '%s\n' "$preferred"
        return 0
    fi

    if [ -f "$work_dir/md.gro" ]; then
        printf '%s\n' "md.gro"
        return 0
    fi

    for candidate in "$work_dir"/md*.gro; do
        if [ -f "$candidate" ]; then
            basename "$candidate"
            return 0
        fi
    done

    if [ -f "$work_dir/npt.gro" ]; then
        printf '%s\n' "npt.gro"
        return 0
    fi

    return 1
}

resolve_fchk_file() {
    local mol_name="$1"
    local explicit_hint="${2:-}"
    local alias_csv="${3:-}"
    local candidate=""
    local probe_name=""
    local probe_lower=""
    local raw_candidates=("$mol_name")

    if [ -n "$explicit_hint" ]; then
        raw_candidates=("$explicit_hint" "${raw_candidates[@]}")
    fi

    if [ -n "$alias_csv" ]; then
        IFS=',' read -r -a alias_array <<< "$alias_csv"
        raw_candidates+=("${alias_array[@]}")
    fi

    for probe_name in "${raw_candidates[@]}"; do
        [ -n "$probe_name" ] || continue
        candidate=$(normalize_fchk_candidate "$probe_name") || continue
        if [ -f "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
        probe_lower=$(printf '%s' "${candidate%.fchk}" | tr '[:upper:]' '[:lower:]')
        shopt -s nullglob nocaseglob
        for candidate in *.fchk; do
            if [ "$(printf '%s' "${candidate%.fchk}" | tr '[:upper:]' '[:lower:]')" = "$probe_lower" ]; then
                shopt -u nullglob nocaseglob
                printf '%s\n' "$candidate"
                return 0
            fi
        done
        shopt -u nullglob nocaseglob
    done

    return 1
}

normalize_fchk_candidate() {
    local raw_name="$1"
    if [ -z "$raw_name" ]; then
        return 1
    fi
    case "$raw_name" in
        *.fchk) printf '%s\n' "$raw_name" ;;
        *) printf '%s.fchk\n' "$raw_name" ;;
    esac
}

is_runtime_placeholder() {
    local lowered
    lowered=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
    case "$lowered" in
        *box*|*existing*|*base*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}
