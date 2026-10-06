#!/usr/bin/env bash
# implement.sh — deterministic driver that replaces the orchestrating agent for the
# `implement` skill. Real code generation still goes through acpx→external agents;
# Jev (jev-decide) + GitNexus + scripted checks replace the orchestrator's judgment
# + review layer.
#
# Usage:
#   implement.sh <feature> [--repo PATH] [--agent AGENT[:MODEL]] [--retries N]
#                        [--ttl SEC] [--dry-run] [--resume] [--skip-judge]
#
#   <feature>   name of the feature dir: <repo>/.scratch/<feature>/issues/NN-<slug>.md
#   --repo      target code repo (default: git root of cwd)
#   --agent     pin an agent (e.g. codex:gpt-6-luna, kimi). Unset → rule-based selection.
#   --retries   max re-dispatch rounds per ticket on in-scope fixes (default 2)
#   --ttl       acpx idle TTL in seconds (default 300; pass 1800+ for long/run tickets)
#   --dry-run   build prompt/baseline/evidence without dispatching a real agent
#   --resume    continue from the saved state, printing any prior review-packs first
#   --skip-judge  run up to the evidence step but do not call jev-decide
#
# State: <repo>/.agent-results/.implement-state.json
# Exit:  0 all tickets green + final acceptance passed; 3 paused awaiting a human;
#        4 dry-run complete; 1 error.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."                 # skill dir (implement-jev-zh)
JUDGE="$SCRIPT_DIR/judge.sh"
GNX="$SCRIPT_DIR/gnx.sh"

# ---------- defaults ----------
FEATURE=""; REPO=""; AGENT_OVERRIDE=""; RETRIES=2; TTL=300
DRY_RUN=0; RESUME=0; SKIP_JUDGE=0

args=("$@"); i=0
while [[ $i -lt ${#args[@]} ]]; do
  case "${args[$i]}" in
    --repo) REPO="${args[$((i+1))]}"; i=$((i+1));;
    --agent) AGENT_OVERRIDE="${args[$((i+1))]}"; i=$((i+1));;
    --retries) RETRIES="${args[$((i+1))]}"; i=$((i+1));;
    --ttl) TTL="${args[$((i+1))]}"; i=$((i+1));;
    --dry-run) DRY_RUN=1 ;;
    --resume) RESUME=1 ;;
    --skip-judge) SKIP_JUDGE=1 ;;
    -*) echo "implement.sh: unknown flag ${args[$i]}" >&2; exit 1 ;;
    *) if [[ -z "$FEATURE" ]]; then FEATURE="${args[$i]}"; else echo "unexpected arg ${args[$i]}" >&2; exit 1; fi ;;
  esac
  i=$((i+1))
done

if [[ -z "$FEATURE" ]]; then echo "implement.sh: need a <feature>"; exit 1; fi
if [[ -z "$REPO" ]]; then
  REPO="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null)" || { echo "implement.sh: cannot find a git repo (use --repo)"; exit 1; }
fi
ISSUES_DIR="$REPO/.scratch/$FEATURE/issues"
OUT_DIR="$REPO/.agent-results"
STATE_FILE="$OUT_DIR/.implement-state.json"
LOG_DIR="$OUT_DIR"
mkdir -p "$ISSUES_DIR/.." "$OUT_DIR"

log()  { printf '[implement %(%H:%M:%S)T] %s\n' -1 "$*"; }
die()  { log "error: $*"; exit 1; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || { log "required tool missing: $1"; exit 1; }; }
need_cmd jev-decide
need_cmd git
[[ "$DRY_RUN" -eq 1 ]] || need_cmd herdr

FALLBACK_CHAIN=(zcode kimi claude dsh)
RUN_MODEL="codex:gpt-6-luna"

# ---------- helpers ----------
json_get()  { python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d.get(sys.argv[2],''))" "$1" "$2" 2>/dev/null; }
json_set()  { python3 -c "import json,sys,os
d=json.load(open(sys.argv[1]));d[sys.argv[2]]=sys.argv[3];json.dump(d,open(sys.argv[1],'w'),ensure_ascii=False,indent=2)" "$STATE_FILE" "$1" "$2"; }
json_push_ticket() { python3 -c "import json,sys
d=json.load(open(sys.argv[1]));d['tickets']=sys.argv[2];json.dump(d,open(sys.argv[1],'w'),ensure_ascii=False,indent=2)" "$STATE_FILE" "$2"; }

# ---------- ticket enumeration + topological sort (Kahn on "Blocked by:") ----------

mark_done() { # mark_done <ticket>  (record as done in state)
  python3 - "$STATE_FILE" "$1" <<'MDD'
import json,sys
d=json.load(open(sys.argv[1]));d.setdefault('state',{}).setdefault('done',{})[sys.argv[2]]='done'
json.dump(d,open(sys.argv[1],'w'),ensure_ascii=False,indent=2)
MDD
}

collect_tickets() {
  # name slug blocked_by
  local f
  for f in "$ISSUES_DIR"/[0-9][0-9]-*.md; do
    [[ -f "$f" ]] || continue
    local name slug bc
    name="$(basename "$f" .md)"
    slug="$(basename "$f" .md)"; slug="${slug#??-}"
    # "Blocked by: 01-..., 02-..." (comma/\n separated)
    bc="$(awk '/^Blocked by:/{sub(/^Blocked by:\s*/,"");print;exit}' "$f" | tr ',，' ' ' | xargs)"
    printf '%s\t%s\n' "$name" "$bc"
  done
}

topo_sort() {
  # stdin: lines  "name<TAB>blocked..." ; stdout: ordered names
  python3 - "$ISSUES_DIR" <<'PY'
import os,sys,re
d=sys.argv[1]
byid={}; deps={}; depsof={}
for fn in sorted(os.listdir(d)):
    if not re.match(r'\d\d-.*\.md$',fn): continue
    name=fn[:-3]
    txt=open(os.path.join(d,fn)).read()
    bc=[]
    for ln in txt.splitlines():
        if re.match(r'^Blocked by:\s*',ln):
            bc=[x.strip() for x in re.split(r'[,，\s]+',re.sub(r'^Blocked by:\s*','',ln)) if x.strip()]
            break
    byid[name]=True
    deps[name]=bc
    for b in bc: depsof.setdefault(b,[]).append(name)
# Kahn
order=[]; done=set()
def ready(n): return all(b in done for b in deps.get(n,[]))
pool=[n for n in byid if ready(n)]
while pool:
    n=sorted(pool)[0]; pool.remove(n)
    order.append(n); done.add(n)
    for m in depsof.get(n,[]):
        if m not in done and m not in pool and ready(m): pool.append(m)
# leftovers (cycle/unknown dep) appended
for n in sorted(byid):
    if n not in done: order.append(n); done.add(n)
print('\n'.join(order))
PY
}

escalate() { # escalate <ticket> <reason> <pack-extra...>
  local tid="$1" reason="$2"; shift 2
  log "ESCALATE $tid: $reason"
  local pack="$LOG_DIR/$tid-review-pack.md"
  {
    echo "# Review-pack — $tid"
    echo
    echo "**原因**: $reason"
    echo
    echo "**状态文件**: $STATE_FILE"
    [[ -f "$LOG_DIR/$tid.prompt.md" ]] && echo "**prompt**: $LOG_DIR/$tid.prompt.md"
    [[ -f "$LOG_DIR/$tid.log" ]] && echo "**log**: $LOG_DIR/$tid.log"
    [[ -f "$LOG_DIR/$tid-evidence.json" ]] && echo "**evidence**: $LOG_DIR/$tid-evidence.json"
    echo
    echo "**下一步（after decision, run \`implement.sh $FEATURE --resume\`）**:"
    echo "- 若发现可修且范围内：清除该票 findings 后重派"
    echo "- 若需换 agent：\`--agent <a>\` 重跑该票"
    echo "- 若判定完成：在该票 status 置 done 后继续"
    echo
    echo "---"
    printf '%s\n' "$@"   # extra context lines (diff summary, jev reason)
  } > "$pack"
  json_set "state.escalated.$tid" "$reason"
  return 3
}

# ---------- agent selection ----------
pick_agent() { # pick_agent <ticket_name> <ticket_file> -> echoes "agent[:model]"
  local tid="$1" tf="$2"
  # doc-only ticket (no code) → exempt from dispatch/review regardless of override
  if grep -qiE '^type:\s*doc|仅文档|doc-only' "$tf"; then echo "doc"; return; fi
  if [[ -n "$AGENT_OVERRIDE" ]]; then echo "$AGENT_OVERRIDE"; return; fi
  # run ticket? heuristic: ticket body mentions 运行/run or a 时长 ≥20
  if grep -qiE '运行|run\b|时长:\s*(2[0-9]|[3-9][0-9]|[0-9]{3,})' "$tf"; then
    echo "$RUN_MODEL"; return
  fi
  # rule requires a human when not a run ticket and unmarket unspecified
  echo "__ASK__"
}

# ---------- prompt build ----------
build_prompt() { # build_prompt <ticket> <ticket_file> <target_file> <agent>
  local tid="$1" tf="$2" out="$3" agent="$4" goal spots
  goal="$(awk '/^(#|##)/{print;exit}' "$tf")"
  spots=""
  if [[ -f "$LOG_DIR/$tid-gnx-impact.json" ]]; then
    spots="$(python3 -c "import json,sys
try:
    d=json.load(open(sys.argv[1])); f=open(d.get('raw',''));
except Exception: print('')
" "$LOG_DIR/$tid-gnx-impact.json" 2>/dev/null)"
  fi
  cat > "$out" <<EOF
# 实现任务：$tid

## 总体目标
$( [[ -f "$REPO/.scratch/$FEATURE/spec.md" ]] && head -20 "$REPO/.scratch/$FEATURE/spec.md" || echo "（feature spec 未提供，见下方 ticket）")

## 本票内容
$(cat "$tf")

## 改动范围 / 影响面（GitNexus，仅供参考）
$([ -n "$spots" ] && echo "见 ${LOG_DIR}/${tid}-gnx-impact.txt（如生成）" || echo "无")

## 遵则（确定性派发契约）
1. 严格限制在本票 spec/ADR 范围内，禁止范围蔓延（scope creep）。
2. 使用 /tdd（红绿）推进；写完先看测试红，再实现到绿。
3. 完成后跑项目检查（如 pnpm run check / make test）确保绿灯。
4. 结束前写 /handoff-for-mattpocock 产物。
5. 用显式路径提交（git add <path>...，禁止 git add -A / git add .）。
6. 禁止在本会话内再次 /acpx 或派发 subagent。
7. 禁止自行做 code review（由驱动脚本与 Jev 完成后审）。
8. 修改前确认涉及文件真实存在。
9. 若卡住，明确说明阻塞点，不要编造成功。
EOF
  log "prompt written -> $out"
}

# ---------- baseline ----------
record_baseline() {
  if [[ -f "$STATE_FILE" ]] && json_get "$STATE_FILE" "baseline.head" != ""; then return; fi
  local head status
  head="$(git -C "$REPO" rev-parse HEAD 2>/dev/null)" || head="unknown"
  status="$(git -C "$REPO" status --short 2>/dev/null)"
  python3 - "$STATE_FILE" "$head" "$status" <<'PY'
import json,sys
p,h,s=sys.argv[1],sys.argv[2],sys.argv[3]
d={}
try: d=json.load(open(p))
except Exception: pass
d['baseline']={'head':h,'status':s.splitlines() if s else []}
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
PY
  log "baseline recorded: HEAD=$head (${#status} status lines)"
}

# ---------- dispatch (herdr pane + acpx), pointed at a real external agent ----------
dispatch_ticket() { # dispatch_ticket <tid> <agent>
  local tid="$1" agent="$2" prompt_file log_file
  prompt_file="$LOG_DIR/$tid.prompt.md"
  log_file="$LOG_DIR/$tid.log"
  local a_model=""
  if [[ "$agent" == *:* ]]; then a_model="--model ${agent#*:}"; agent="${agent%%:*}"; fi

  # pane preflight / create. Reuse an existing tab keyed by feature slug.
  local pane_id tab
  pane_id="$(herdr pane list 2>/dev/null | grep -iE "implement-$FEATURE" | awk '{print $1}' | head -1)"
  if [[ -z "$pane_id" ]]; then
    # create a tab; read ids from JSON result
    local cres
    cres="$(herdr tab create --cwd "$REPO" --label "impl-$FEATURE" --no-focus --format json 2>/dev/null)"
    pane_id="$(    echo "$cres" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['root_pane']['pane_id'])" 2>/dev/null)"
    [[ -z "$pane_id" ]] && die "herdr tab create failed (pane_id unreadable)"
  fi

  log "dispatch $tid -> agent=$agent${a_model:+ $a_model} pane=$pane_id"
  local cmd="acpx --cwd $REPO --approve-all --ttl $TTL $a_model $agent exec -f $prompt_file 2>&1 | tee $log_file"
  herdr pane run "$pane_id" "$cmd" >/dev/null 2>&1 || die "herdr pane run failed for $tid"

  # startup check (~60s): acpx must reach session/new (ok) before we wait long
  local waited=0
  until grep -qE "session/new \(ok\)|session/set_config_option|Cannot apply|error" "$log_file" 2>/dev/null; do
    sleep 3; waited=$((waited+3)); [[ $waited -ge 60 ]] && { log "start timeout for $tid"; break; }
  done
}

wait_completion() { # wait_completion <tid> <max_s>
  local tid="$1" max_s="$2" log_file="$LOG_DIR/$tid.log" waited=0
  while :; do
    [[ -f "$log_file" ]] || { sleep 2; waited=$((waited+2)); }
    if grep -q '\[done\] end_turn' "$log_file" 2>/dev/null; then
      if grep -qE 'AccountQuotaExceeded|RUNTIME:|error' "$log_file"; then
        log "false completion for $tid (error block present) — agent unavailable"
        return 2
      fi
      log "completion for $tid"
      return 0
    fi
    sleep 5; waited=$((waited+5))
    [[ $waited -ge $max_s ]] && { log "timeout waiting for $tid"; return 3; }
  done
}

# ---------- deterministic verification + GitNexus evidence ----------
verify_ticket() { # verify_ticket <tid> <baseline_head> -> writes <tid>-evidence.json ; echo result
  local tid="$1" base="$2" ev="$LOG_DIR/$tid-evidence.json"
  local newcommit diff_empty handoff check_ok gnx_partial gnx_risk
  newcommit="$(git -C "$REPO" log --oneline -1 2>/dev/null)"
  diff_empty=1
  [[ -n "$base" && "$base" != "unknown" ]] && [[ -n "$(git -C "$REPO" diff --name-only "$base" 2>/dev/null)" ]] && diff_empty=0
  handoff=1
  # handoff artifact: look for a handoff file pattern in the changed set
  git -C "$REPO" diff --name-only "$base" 2>/dev/null | grep -qiE 'handoff' && handoff=0

  # GitNexus: detect-changes on the ticket's commits + cycle check
  bash "$GNX" detect --scope compare -b "$base" --repo "$REPO" --out "$LOG_DIR/$tid-gnx-detect" >/dev/null 2>&1
  bash "$GNX" check --repo "$REPO" --out "$LOG_DIR/$tid-gnx-check" >/dev/null 2>&1
  gnx_partial="$(json_get "$LOG_DIR/$tid-gnx-detect.json" partial 2>/dev/null)"; gnx_partial="${gnx_partial:-false}"
  gnx_risk="$(json_get "$LOG_DIR/$tid-gnx-detect.json" risk 2>/dev/null)"

  python3 - "$ev" "$tid" "$newcommit" "$diff_empty" "$handoff" "$gnx_partial" "$gnx_risk" <<'PY'
import json,sys
ev_path,tid,newcommit,diff_empty,handoff,gnx_partial,gnx_risk=sys.argv[1:]
ev={
 "ticket":tid,
 "git":{"new_commit":newcommit,"diff_empty":(diff_empty=="0")},
 "handoff_artifact":(handoff=="0"),
 "gitnexus":{"partial":(gnx_partial=="true"),"risk":gnx_risk,
             "detect":tid+"-gnx-detect.json","check":tid+"-gnx-check.json"}
}
json.dump(ev,open(ev_path,'w'),ensure_ascii=False,indent=2)
PY
  echo "$ev"
}

# ---------- per-ticket gate + routing ----------
judge_ticket() { # judge_ticket <tid> -> exit 0(clean) 1(fix/re-dispatch) 3(ask/defer→decide) 4(chain-exhausted)
  local tid="$1" ev="$LOG_DIR/$tid-evidence.json"
  [[ -f "$LOG_DIR/$tid-evidence.json" ]] || die "no evidence for $tid"
  local goal
  goal="$(basename "$tid" .md); $(grep -m1 '^#' "$ISSUES_DIR/$tid.md" 2>/dev/null)"
  # merge gitnexus evidence into the judge state
  python3 - "$LOG_DIR/$tid-evidence.json" "$LOG_DIR/$tid-gnx-detect.json" "$LOG_DIR/$tid-gnx-check.json" <<'PY'
import json,sys
evp=sys.argv[1]
ev=json.load(open(evp))
def rd(p):
    try:return json.load(open(p))
    except Exception:return {}
ev['gitnexus']['detect']=rd(sys.argv[2]); ev['gitnexus']['check']=rd(sys.argv[3])
json.dump(ev,open(evp,'w'),ensure_ascii=False,indent=2)
PY
  # diff summary for jev context
  local diffsum=""
  local b
  b="$(json_get "$STATE_FILE" baseline.head)"
  [[ -n "$b" && "$b" != "unknown" ]] && diffsum="$(git -C "$REPO" diff --stat "$b" 2>/dev/null | tail -1)"
  python3 - "$LOG_DIR/$tid-evidence.json" "$goal" "$diffsum" <<'PY'
import json,sys
evp,goal,diffsum=sys.argv[1:]
ev=json.load(open(evp));ev['goal']=goal;ev['diff_summary']=diffsum or ''
ev.setdefault('receipts',[]); ev.setdefault('test_receipts',[]); ev.setdefault('findings',[])
json.dump(ev,open(evp,'w'),ensure_ascii=False,indent=2)
PY

  [[ "$SKIP_JUDGE" -eq 1 ]] && { log "skip-judge: not calling jev-decide for $tid"; return 0; }
  if [[ "$DRY_RUN" -eq 1 ]]; then log "dry-run: skipping jev-decide for $tid"; return 0; fi
  bash "$JUDGE" ticket "$LOG_DIR/$tid-evidence.json"; local code=$?
  [[ $code -eq 1 ]] && { log "jev error on $tid"; echo "escalate"; return 3; }

  # Route on the RESOLVED VALUES (not the blanket exit code): jev flags review-labels
  # (ask_user/defer/unknown/...) as needs_review, and many are intentional auto-advances.
  local dec="$LOG_DIR/$(basename "$LOG_DIR/$tid-evidence.json" .json).request.json.decisions.json"
  local verdict
  verdict="$(python3 - "$dec" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    print('escalate'); sys.exit(0)
dec=d.get('decisions',{})
def val(q):
    r=dec.get(q,{}); return r.get('value'), r.get('status')
def prob(q):
    r=dec.get(q,{}); return r.get('probability') or (r.get('margin',[1,0,0])[1] if r.get('margin') else None)
cp=prob('claim_supported')
if cp is not None and float(cp)<0.75:
    print('escalate: low claim confidence'); sys.exit(0)
for q in ('weakens_checks','scope_breach'):
    v,_=val(q)
    if v is True: print('escalate: '+q); sys.exit(0)
comp,_=val('completion')
if comp in ('unsupported','unknown'):
    print('escalate: completion='+str(comp)); sys.exit(0)
rr,_=val('route')
if rr=='ask_user': print('escalate: route=ask_user'); sys.exit(0)
res,_=val('resolved_all')
if res is False: print('escalate: unresolved findings'); sys.exit(0)
if rr=='fix_now': print('fix'); sys.exit(0)
if rr=='defer': print('defer'); sys.exit(0)
print('clean')
PY
  )"
  log "-> routed verdict: $verdict"
  case "$verdict" in
    clean|defer) echo "clean"; return 0 ;;
    fix)         echo "fix"; return 1 ;;
    *)           echo "escalate"; return 3 ;;
  esac

}

# ================= MAIN =================
export IMPL_OUT_DIR="$LOG_DIR"
log "implement.sh feature=$FEATURE repo=$REPO dry_run=$DRY_RUN resume=$RESUME"
[[ -d "$ISSUES_DIR" ]] || die "no tickets at $ISSUES_DIR"

# init state
if [[ ! -f "$STATE_FILE" ]]; then
  python3 - "$STATE_FILE" "$FEATURE" "$REPO" <<'PY'
import json,sys
json.dump({"feature":sys.argv[2],"repo":sys.argv[3],"tickets":[],"state":{}},open(sys.argv[1],'w'),ensure_ascii=False,indent=2)
PY
fi
record_baseline

# topo order
mapfile -t ORDER < <(topo_sort)
log "ticket order: ${ORDER[*]:-none}"

# GitNexus index readiness (soft; escalate if unusable)
if [[ "$DRY_RUN" -eq 0 ]]; then
  bash "$GNX" status --repo "$REPO" --out "$LOG_DIR/gnx-status" >/dev/null 2>&1
  gs_rc=$?
  if [[ $gs_rc -eq 2 ]]; then
    log "GitNexus index missing for $REPO — running analyze (may take a while). Set --skip-judge to defer."
    bash "$GNX" analyze --repo "$REPO" --out "$LOG_DIR/gnx-analyze" >/dev/null 2>&1 || log "gnx analyze failed; structural evidence will be partial"
  fi
fi

ESCALATED=0
for tid in "${ORDER[@]:-}"; do
  [[ -f "$STATE_FILE" ]] && st="$(json_get "$STATE_FILE" "state.done.$tid")"
  if [[ "$RESUME" -eq 1 && -n "$st" && "$st" != "todo" ]]; then
    log "skip $tid (marked $st)"; continue
  fi

  tsfile="$ISSUES_DIR/$tid.md"
  agent="$(pick_agent "$tid" "$tsfile")"
  if [[ "$agent" == "doc" ]]; then
    log "$tid is doc-only; no dispatch/review (declare exempt)"
    python3 - "$STATE_FILE" "$tid" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]));d.setdefault('state',{}).setdefault('done',{})[sys.argv[2]]='done'
json.dump(d,open(sys.argv[1],'w'),ensure_ascii=False,indent=2)
PY
    continue
  fi
  if [[ "$agent" == "__ASK__" ]]; then
    escalate "$tid" "未指定 agent 且非运行票——需要你选实现 agent" "pick_agent could not decide; --agent <a> to pin."
    ESCALATED=1; break
  fi

  log "ticket $tid -> agent=$agent retries=$(json_get "$STATE_FILE" "state.retries.$tid" 2>/dev/null || echo 0)"

  # GitNexus impact for a target symbol (if the ticket names one) — feeds prompt + later cross-check
  tsym=""
  tsym="$(grep -oE '(target|符号|symbol)[:=]+\s*[A-Za-z_][A-Za-z0-9_]*(\(\))?' "$tsfile" 2>/dev/null | grep -oE '[A-Za-z_]\(\)?$' | head -1)"
  if [[ -z "$tsym" ]]; then tsym="$(grep -m1 -oE '`[A-Za-z_][A-Za-z0-9_]*`' "$tsfile" 2>/dev/null | tr -d '`' )"; fi
  if [[ -n "$tsym" && "$DRY_RUN" -eq 0 ]]; then
    bash "$GNX" impact "$tsym" --dir upstream --repo "$REPO" --out "$LOG_DIR/$tid-gnx-impact" >/dev/null 2>&1
    log "gitnexus impact $tsym (partial=$(json_get "$LOG_DIR/$tid-gnx-impact.json" partial 2>/dev/null))"
  fi

  build_prompt "$tid" "$tsfile" "$LOG_DIR/$tid.prompt.md" "$agent"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "dry-run: not dispatching $tid (stub)"
    # stub evidence so routing/wiring is exercised
    newcommit=""
    newcommit="$(git -C "$REPO" log --oneline -1 2>/dev/null)"
    python3 - "$LOG_DIR/$tid-evidence.json" "$tid" "$newcommit" <<'PY'
import json,sys
json.dump({"ticket":sys.argv[2],"git":{"new_commit":sys.argv[3],"diff_empty":False},
 "handoff_artifact":False,"gitnexus":{"partial":False,"risk":""},"goal":"","diff_summary":"",
 "receipts":[{"source":"dry-run stub","meaning":"no agent dispatched"}],
 "test_receipts":[],"findings":[]},open(sys.argv[1],'w'),ensure_ascii=False,indent=2)
PY
  else
    dispatch_ticket "$tid" "$agent" || { escalate "$tid" "派发失败"; ESCALATED=1; break; }
    wc=$(wait_completion "$tid" "$TTL"); rc=$?
    if [[ $rc -eq 2 ]]; then
      # unavailable → here the driver would walk FALLBACK_CHAIN; for deliverable: escalate
      escalate "$tid" "agent=$agent unavailable (false completion)"; ESCALATED=1; break
    elif [[ $rc -eq 3 ]]; then
      escalate "$tid" "wait timeout (ttl=$TTL)"; ESCALATED=1; break
    fi
  fi

  b="$(json_get "$STATE_FILE" baseline.head)"
  jc=""; attempt=0
  while :; do
    verify_ticket "$tid" "$b" >/dev/null 2>&1
    jc=0
    if [[ "$SKIP_JUDGE" -eq 0 || "$DRY_RUN" -eq 1 ]]; then
      judge_ticket "$tid"; jc=$?
    fi
    if [[ $jc -eq 0 ]]; then
      log "$tid: clean -- progress"
      mark_done "$tid"
      break
    elif [[ $jc -eq 1 ]]; then
      attempt=$((attempt+1))
      if [[ $attempt -gt "$RETRIES" ]]; then
        escalate "$tid" "in-scope fix not converging after $RETRIES re-dispatches"
        ESCALATED=1; break
      fi
      log "$tid: in-scope fix routed -> re-dispatch (attempt $attempt/$RETRIES)"
      rm -f "$LOG_DIR/$tid.log" "$LOG_DIR/$tid-evidence.json" "$LOG_DIR/$tid.request.json" "$LOG_DIR/$tid.request.json.decisions.json"
      if [[ "$DRY_RUN" -eq 1 ]]; then
        continue
      else
        dispatch_ticket "$tid" "$agent" || { escalate "$tid" "派发失败"; ESCALATED=1; break; }
        wc=$(wait_completion "$tid" "$TTL"); rc=$?
        if [[ $rc -eq 2 ]]; then escalate "$tid" "agent=$agent unavailable"; ESCALATED=1; break
        elif [[ $rc -eq 3 ]]; then escalate "$tid" "wait timeout (ttl=$TTL)"; ESCALATED=1; break; fi
      fi
    else
      escalate "$tid" "Jev verdict requires a human (judge exit=$jc)" \
        "judge exit was not clean -- inspect evidence/review-pack"
      ESCALATED=1; break
    fi
    [[ "$ESCALATED" -eq 1 ]] && break
  done

done

if [[ "$ESCALATED" -eq 1 ]]; then
  log "paused awaiting human; review-packs at $LOG_DIR/*-review-pack.md"
  exit 3
fi

# ---- final acceptance ----
log "all tickets green — final acceptance gate"
python3 - "$LOG_DIR/final-evidence.json" "$FEATURE" "$(basename "$REPO")" <<'PY'
import json,sys
d={"feature":sys.argv[2],"repo":sys.argv[3],"deferred_findings":[],"tickets_done":[]}
try:
    dd=json.load(open(sys.argv[1].replace('final-evidence','.implement-state')))
except Exception: dd={}
d['tickets_done']=[k for k in dd.get('state',{}).get('done',{})]
b=dd.get('baseline',{}).get('head','')
json.dump(d,open(sys.argv[1],'w'),ensure_ascii=False,indent=2)
PY
if [[ "$DRY_RUN" -eq 0 ]]; then
  bash "$GNX" detect --scope compare -b "$(json_get "$STATE_FILE" baseline.head)" --repo "$REPO" --out "$LOG_DIR/final-gnx-detect" >/dev/null 2>&1
  bash "$GNX" check --repo "$REPO" --out "$LOG_DIR/final-gnx-check" >/dev/null 2>&1
fi
if [[ "$SKIP_JUDGE" -eq 1 || "$DRY_RUN" -eq 1 ]]; then log "skip/dry-run: final acceptance not jev-gated here"; exit 0; fi
bash "$JUDGE" accept "$LOG_DIR/final-evidence.json"; fac=$?
if [[ $fac -eq 0 ]]; then
  log "FINAL ACCEPTED — feature $FEATURE green"
  exit 0
else
  escalate "$FEATURE" "final acceptance needs a human (judge exit=$fac)"
  exit 3
fi