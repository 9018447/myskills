#!/usr/bin/env bash
# judge.sh — build a jev-decide request from a template (or template merge) + a state
# JSON, then call jev-decide. Deterministic gate primitive for implement.sh.
#
# Usage:
#   judge.sh <mode> <state-file.json> [--dry-run]
#     mode = ticket            merge completion + review + fix-routing into ONE request (per-ticket gate)
#          | accept            use final-acceptance template (whole-feature gate)
#   <state-file.json>          fields the chosen template(s) expect (see templates for the schema)
#   --dry-run                  build + offline-validate the request shape, no API call
#
# Exit codes mirror jev-decide: 0 = go, 2 = needs review, 1 = error.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPL_DIR="$SCRIPT_DIR/judge-templates"
DRY_RUN=0
MODE="${1:-}"
STATE_FILE="${2:-}"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
  esac
done

if [[ -z "$MODE" || -z "$STATE_FILE" ]]; then
  echo "usage: judge.sh <ticket|accept> <state-file.json> [--dry-run]" >&2
  exit 1
fi
if [[ ! -f "$STATE_FILE" ]]; then
  echo "judge.sh: state file not found: $STATE_FILE" >&2
  exit 1
fi

# Resolve which templates feed the request.
case "$MODE" in
  ticket) TEMPLATES=("$TMPL_DIR/completion.json" "$TMPL_DIR/review.json" "$TMPL_DIR/fix-routing.json") ;;
  accept) TEMPLATES=("$TMPL_DIR/final-acceptance.json") ;;
  *)
    echo "judge.sh: unknown mode '$MODE' (expected ticket|accept)" >&2
    exit 1
    ;;
esac

# Merge templates + state into a single request via python (JSON shaping is saner than jq).
REQ_DIR="${IMPL_OUT_DIR:-.agent-results}"
REQ_FILE="$REQ_DIR/$(basename "$STATE_FILE" .json).request.json"

python3 - "$STATE_FILE" "${TEMPLATES[@]}" > "$REQ_FILE" <<'PY'
import json, sys, re, time

state_file = sys.argv[1]
templates = sys.argv[2:]
with open(state_file) as f:
    state = json.load(f)

# Deep-merge template states; later templates must not clobber real goals/tickets.
merged = {"model": "typesafe/jev-1.13", "state": {}, "questions": {}}
first = True
for t in templates:
    with open(t) as f:
        tmpl = json.load(f)
    s = dict(tmpl["state"]); q = dict(tmpl["questions"])
    for k, v in state.items():
        if v is not None and v != "" and v != [] and v != {}:
            s[k] = v
    merged["state"].update(s)     # keep real state; template defaults overwrite blanks
    merged["questions"].update(q) # collect every question across the merged set
    if first:
        merged["model"] = tmpl.get("model", merged["model"])
        first = False

json.dump(merged, sys.stdout, ensure_ascii=False, indent=2)
PY

if [[ ! -s "$REQ_FILE" ]]; then
  echo "judge.sh: failed to build request" >&2
  exit 1
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "judge.sh: request built at $REQ_FILE (offline validation)" >&2
  out="$(jev-decide decide "$REQ_FILE" --dry-run 2>&1)"
  code=$?
else
  out="$(jev-decide decide "$REQ_FILE" 2>&1)"
  code=$?
fi

# persist the decisions JSON so implement.sh can route on per-value signals
if [[ -n "$out" ]]; then
  printf '%s\n' "$out" > "$REQ_FILE.decisions.json"
  printf '%s\n' "$out" | tail -5 >&2
fi
echo "judge.sh: jev-decide exit=$code (0=go 2=needs_review 1=error); decisions -> $REQ_FILE.decisions.json" >&2
exit "$code"