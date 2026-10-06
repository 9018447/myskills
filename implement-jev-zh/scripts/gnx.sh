#!/usr/bin/env bash
# gnx.sh — GitNexus structural-evidence leg for implement.sh. LLM-free.
# Captures raw output to a txt, extracts a best-effort structured JSON summary
# (risk level, partial/truncated/unavailable markers).
#
# Usage:
#   gnx.sh status [--repo R]              → fresh index present?
#   gnx.sh analyze [--repo R]             → build/refresh index (0 = done)
#   gnx.sh impact "<symbol>" [--dir upstream|downstream] [--repo R]  → blast radius
#   gnx.sh detect [--scope all|compare] [-b BASE] [--repo R]   → diff→flows + risk
#   gnx.sh check [--repo R]               → import-cycle check
#   ... --out PREFIX                      → write raw to PREFIX.txt, JSON to PREFIX.json
#
# Exit 0 = evidence gathered & parsed; 2 = evidence incomplete/partial/unavailable.
set -uo pipefail

GNX_BIN="${GNX_BIN:-$(command -v gitnexus || true)}"
OUT_PREFIX=""; REPO=""; CMD=""; EXTRA=()

args=("$@"); i=0
while [[ $i -lt ${#args[@]} ]]; do
  case "${args[$i]}" in
    --repo) REPO="${args[$((i+1))]}"; i=$((i+1));;
    --out) OUT_PREFIX="${args[$((i+1))]}"; i=$((i+1));;
    *) if [[ -z "$CMD" ]]; then CMD="${args[$i]}"; else EXTRA+=("${args[$i]}"); fi ;;
  esac
  i=$((i+1))
done

write_raw_txt() { : > "$1"; }

if [[ -z "$GNX_BIN" ]]; then
  ( [[ -n "$OUT_PREFIX" ]] && cat > "$OUT_PREFIX.json" ) <<'EOF'
{"error":"gitnexus binary not found","partial":true}
EOF
  exit 2
fi
repo_arg=(); [[ -n "$REPO" ]] && repo_arg=(--repo "$REPO")
if [[ -n "$OUT_PREFIX" ]]; then
  mkdir -p "$(dirname "$OUT_PREFIX")"; RAW="$OUT_PREFIX.txt"; JSON="$OUT_PREFIX.json"
else
  RAW="${TMPDIR:-/tmp}/gnx-$$.txt"; JSON="${TMPDIR:-/tmp}/gnx-$$.json"
fi
: > "$RAW"

# extracts
risk_of()    { grep -oE '风险等级：\s*[A-Za-z]+' "$1" | head -1 | sed 's/风险等级：\s*//' | tr -d ' '; }
count_of()   { grep -oE '变更：\s*[0-9]+ 个文件，[0-9]+ 个符号' "$1" | head -1; }
marker_of()  { grep -iqE 'partial|truncated|尚未索引|索引过期|Failed|Traceback|cannot|无法|失败|Error' "$1" && echo 1 || echo 0; }

esc() { python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "$1" 2>/dev/null; }

flush() { # flush <cmd> <partial> <risk> <count>
  local cmd="$1" partial="$2" risk="$3" count="$4"
  rm -f "$JSON"
  cat > "$JSON" <<EOF
{
  "cmd": $(esc "$cmd"),
  "raw": $(esc "$RAW"),
  "partial": $partial,
  "risk": $(esc "$risk"),
  "count": $(esc "$count")
}
EOF
}

case "$CMD" in
  status|analyze)
    "$GNX_BIN" "$CMD" "${repo_arg[@]}" > "$RAW" 2>&1
    if grep -qE '尚未索引|未索引|No registered repo|not yet indexed' "$RAW"; then
      flush "$CMD" "true" "missing" ""; exit 2
    fi
    flush "$CMD" "false" "present" ""; exit 0
    ;;
  impact)
    SYM="${EXTRA[0]:-}"; dir="upstream"
    if [[ -z "$SYM" ]]; then flush "impact" "true" "" ""; exit 1; fi
    for e in "${EXTRA[@]:-}"; do
      case "$e" in upstream|downstream|-d) dir="$e" ;; esac
    done
    [[ "$dir" == "-d" ]] && dir="upstream"
    "$GNX_BIN" impact "$SYM" -d "$dir" "${repo_arg[@]}" > "$RAW" 2>&1
    ;;
  detect)
    scope="all"; base=""
    for e in "${EXTRA[@]:-}"; do
      case "$e" in
        --scope) ;;
        all|staged|unstaged|compare) scope="$e" ;;
        -b) ;;
        *) base="$e" ;;
      esac
    done
    base_arg=(); [[ -n "$base" && "$scope" == "compare" ]] && base_arg=(-b "$base")
    "$GNX_BIN" detect-changes --scope "$scope" "${base_arg[@]}" "${repo_arg[@]}" > "$RAW" 2>&1
    ;;
  check)
    "$GNX_BIN" check --cycles "${repo_arg[@]}" > "$RAW" 2>&1
    ;;
  *)
    flush "$CMD" "true" "" ""; exit 1 ;;
esac

risk="$(risk_of "$RAW")"; count="$(count_of "$RAW")"; marker="$(marker_of "$RAW")"
flush "$CMD" "$marker" "$risk" "$count"
exit "$([[ "$marker" == "1" ]] && echo 2 || echo 0)"