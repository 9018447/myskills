#!/usr/bin/env bash
# status.sh — 总览 <repo>/.scratch 下每个 feature 的实现状态，并用一次 Jev 判断给出
# 各 feature 的阶段意见与"下一步优先推进哪个"的建议。只读（唯一写入是缓存的请求文件）。
#
# Usage:
#   status.sh [--repo PATH] [--dry-run] [--detail]
#     --repo    目标代码仓库（默认：当前目录所在 git 根）
#     --dry-run 只出确定性统计与请求，不调用 Jev（零 token）
#     --detail  额外打印每条证据明细
# Exit: 0 正常；1 环境/参数错误或 Jev 调用失败
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

REPO=""; DRY_RUN=0; DETAIL=0
args=("$@"); i=0
while [[ $i -lt ${#args[@]} ]]; do
  case "${args[$i]}" in
    --repo) REPO="${args[$((i+1))]}"; i=$((i+1));;
    --dry-run) DRY_RUN=1 ;;
    --detail) DETAIL=1 ;;
    -h|--help) cat <<'H'
status.sh — 总览每个 feature 的实现状态（含 Jev 阶段意见与下一步建议）
用法: status.sh [--repo PATH] [--dry-run] [--detail]
H
      exit 0 ;;
    *) echo "status.sh: unknown flag ${args[$i]}" >&2; exit 1 ;;
  esac
  i=$((i+1))
done

if [[ -z "$REPO" ]]; then
  REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "status.sh: 须在 git 仓库内或传 --repo"; exit 1; }
fi
command -v jev-decide >/dev/null 2>&1 || { echo "status.sh: jev-decide 缺失（uv tool jev-skill 安装到 ~/.local/bin）"; exit 1; }

SCRATCH="$REPO/.scratch"
OUT="$REPO/.agent-results"
mkdir -p "$OUT" 2>/dev/null || true
SUM="$OUT/_status-summary.json"

# 1) gather: 确定性统计（打印表格到终端；JSON 写 $SUM 供后续步骤读）
python3 - "$SCRATCH" "$OUT" "$DETAIL" "$SUM" <<'PY'
import json, sys, glob, os, re
scratch, out, detail, sum_path = sys.argv[1], sys.argv[2], (sys.argv[3]=="1"), sys.argv[4]
summary={"repo":os.path.realpath(os.path.join(scratch,"..")), "shared_state_feature":None,
         "shared_done":[], "features":{}}
sf=os.path.join(out,".implement-state.json")
if os.path.exists(sf):
    try:
        d=json.load(open(sf))
        summary["shared_state_feature"]=d.get("feature")
        summary["shared_done"]=list(d.get("state",{}).get("done",{}).keys())
    except Exception:
        pass
cur=summary["shared_state_feature"]
feats=sorted(os.path.basename(fd.rstrip("/")) for fd in glob.glob(scratch+"/*/"))
if not feats:
    print("status.sh: 该仓库 .scratch 下没有任何 feature"); sys.exit(0)
rows=[]
for f in feats:
    issues=os.path.join(scratch,f,"issues")
    tickets=sorted(os.path.basename(x)[:-3] for x in glob.glob(issues+"/[0-9][0-9]-*.md"))
    doc=ran=review=0
    for t in tickets:
        try:
            body=open(os.path.join(issues,t+".md"),encoding="utf-8").read()
        except Exception:
            body=""
        if re.search(r"type:\s*doc|doc-only|仅文档", body): doc+=1
        if any(os.path.exists(os.path.join(out,t+s)) for s in (".log","-evidence.json","-review-pack.md")):
            ran+=1
        if os.path.exists(os.path.join(out,t+"-review-pack.md")): review+=1
    owns=(cur==f)
    done=sum(1 for t in tickets if t in summary["shared_done"]) if owns else 0
    spec=os.path.exists(os.path.join(scratch,f,"spec.md"))
    summary["features"][f]={"tickets":len(tickets),"doc":doc,"ran":ran,"review_packs":review,
                            "done":done,"spec":spec,"state_owns":owns}
    rows.append((f,len(tickets),done,ran,review,doc,"有" if spec else "无","接管" if owns else "-"))
with open(sum_path,"w",encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)
w=max([len(r[0]) for r in rows]+[7])
hdr=f"{'feature':<{w}} 票 已完成 跑过 卡住 文档 spec 状态文件"
print(hdr); print("-"*len(hdr))
for r in rows:
    print(f"{r[0]:<{w}} {r[1]:>2} {r[2]:>4} {r[3]:>4} {r[4]:>4} {r[5]:>4} {r[6]:>3} {r[7]:>6}")
if detail:
    print("\n[detail] shared_state_feature=",cur," done=",summary["shared_done"])
PY
code=$?
[[ $code -ne 0 ]] && { echo "status.sh: 统计失败" >&2; exit 1; }

# 2) build one jev request from the summary
REQ="$OUT/_status.request.json"
python3 - "$SUM" > "$REQ" <<'PY'
import json, sys
s=json.load(open(sys.argv[1]))
feats=dict(s["features"])
OPTS=[
 ("从未开始/未运行","没有任何可运行记录或运行产物"),
 ("推进中","有部分票已运作或有产物，但未完成"),
 ("中途暂停","存在 review_pack，需要人介入"),
 ("接近完成","大部分票已标记完成，差整体验收"),
 ("已完成待验收","票已全部完成，等待整体验收门"),
 ("维护中/停滞","长期未动/缺 spec 或定位不清"),
]
qs={}
for f, fs in feats.items():
    # 把该 feature 自己的证据写进提示，锚定 Jev 按数据判，而不是只给档位列表
    anchor=(f"tickets={fs['tickets']}, done={fs['done']}, ran={fs['ran']}, "
            f"review_packs={fs['review_packs']}, doc={fs['doc']}, "
            f"spec={'有' if fs['spec'] else '无'}, 状态文件={'接管' if fs['state_owns'] else '未接管'}")
    qs[f]={
      "type":"choice",
      "instructions":f"该 feature 的实现证据: {anchor}。请据此选择它当前最贴切的阶段。没有运行产物或没有票时不要判成已完成。",
      "criteria":{lab:desc for lab,desc in OPTS},
    }
focus_crit={}
for f, fs in feats.items():
    focus_crit[f]=(f"tickets={fs['tickets']},done={fs['done']},ran={fs['ran']},"
                   f"review_packs={fs['review_packs']},spec={'有' if fs['spec'] else '无'}")
qs["focus"]={
  "type":"choice",
  "instructions":"综合各 feature 的实现阶段与证据，下一步最应该优先推进(或验收/收尾)哪一个，并说明原因。",
  "criteria":focus_crit,
}
req={"model":"typesafe/jev-1.13","state":s,"questions":qs}
json.dump(req, sys.stdout, ensure_ascii=False, indent=2)
PY
echo "status.sh: request -> $REQ" >&2

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "status.sh: --dry-run，未调用 Jev（零 token）" >&2
  exit 0
fi

# 3) call jev-decide
out="$(jev-decide decide "$REQ" 2>&1)"
code=$?
if [[ -n "$out" ]]; then printf '%s\n' "$out" > "$REQ.decisions.json"; fi
if [[ $code -eq 1 || -z "$out" ]]; then
  echo "status.sh: jev-decide 失败 (exit=$code)" >&2; printf '%s\n' "$out" | tail -20 >&2; exit 1
fi

# 4) render verdicts (choice values; flag low-confidence / needs-review per feature)
python3 - "$SUM" "$REQ.decisions.json" <<'PY'
import json, sys
s=json.load(open(sys.argv[1])); dec=json.load(open(sys.argv[2])).get("decisions",{})
feats=dict(s["features"])
print("\n=== 全部 feature 状态（Jev 判断）===")
low=[]
for f, fs in feats.items():
    q=dec.get(f,{})
    lab=q.get("value")
    prob=q.get("probability") or (q.get("margin",[0,1,0])[1] if q.get("margin") else None)
    note=(" (p=%.2f)"%prob) if isinstance(prob,(int,float)) else ""
    reason=(" · "+q["reason"]) if q.get("reason") else ""
    print(f"  {f:<30} -> {lab}{note}{reason}")
    if q.get("status")=="needs_review": low.append(f)
fq=dec.get("focus",{})
print("\n=== 下一步建议（Jev）===")
print(f"  优先关注: {fq.get('value')}")
if fq.get("reason"): print(f"  原因: {fq['reason']}")
if low: print("\n  需人工再看的 feature:", ", ".join(low))
PY
exit 0