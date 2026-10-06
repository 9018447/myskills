#!/usr/bin/env bash
# status.sh — 总览 <repo>/.scratch 下每个 feature 的实现状态，用 zg 检索代码里的真实实现痕迹，
# 并把确定性证据 + zg 检索结果交给一次 Jev 判断，给出各 feature 阶段意见与下一步建议。
# 只读（唯一写入是 .agent-results/ 下的缓存请求/证据文件）。
#
# Usage:
#   status.sh [--repo PATH] [--dry-run] [--detail] [--zg]
#     --repo      目标代码仓库（默认：当前目录所在 git 根）
#     --dry-run   只出确定性统计 + zg 检索 + 请求，不调用 Jev（零 token）
#     --zg        用 zg 语义索引检索：缺索引则先用本地嵌入模型 potion-code-16m-v2 自动建一次
#                 （首次需联网下载模型 + 磁盘；否则本次按需构建失败即报错退出）。
#                 默认走词表层 --rg（无需索引，随处可用）。语义在建/已建索引下对泛词更抗噪声。
#     --detail    额外打印证据明细
# Exit: 0 正常；1 环境/参数错误或 Jev 调用失败
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

REPO=""; DRY_RUN=0; DETAIL=0; SEMANTIC=0
args=("$@"); i=0
while [[ $i -lt ${#args[@]} ]]; do
  case "${args[$i]}" in
    --repo) REPO="${args[$((i+1))]}"; i=$((i+1));;
    --dry-run) DRY_RUN=1 ;;
    --detail) DETAIL=1 ;;
    --zg) SEMANTIC=1 ;;
    -h|--help) sed -n '1,17p' "${BASH_SOURCE[0]}" | grep '^#' | sed 's/^# *//'; exit 0 ;;
    *) echo "status.sh: unknown flag ${args[$i]}" >&2; exit 1 ;;
  esac
  i=$((i+1))
done

if [[ -z "$REPO" ]]; then
  REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "status.sh: 须在 git 仓库内或传 --repo"; exit 1; }
fi
command -v jev-decide >/dev/null 2>&1 || { echo "status.sh: jev-decide 缺失（uv tool jev-skill 安装到 ~/.local/bin）"; exit 1; }
if command -v zg >/dev/null 2>&1; then ZG="$(command -v zg)"; else ZG=""; fi

# 语义模式(--zg)：缺索引则用本地嵌入模型自动构建一次（首次需联网下载模型 + 磁盘）。
# 注意 zg 语义索引按运行目录(cwd)解析，故探测与构建都 cd 进 repo 根执行。
if [[ "$SEMANTIC" -eq 1 ]]; then
  if [[ -z "$ZG" ]]; then
    echo "status.sh: WARN --zg 需要 zg（zvec-grep），本机未找到；该 feature 的代码检索将标为 NA" >&2
  elif ! ( cd "$REPO" && "$ZG" status 2>&1 | grep -qi 'ready' ); then
    echo "status.sh: --zg 检测到无语义索引，正在用本地嵌入模型 potion-code-16m-v2 构建（首次需联网下载+磁盘）..." >&2
    ( cd "$REPO" && "$ZG" index "$REPO" --embedding local/potion-code-16m-v2 ) >&2 \
      || { echo "status.sh: 索引构建失败（需联网下载 16M 模型 + 磁盘；可改跑默认词表层 --rg）" >&2; exit 1; }
  fi
fi

SCRATCH="$REPO/.scratch"
OUT="$REPO/.agent-results"
mkdir -p "$OUT" 2>/dev/null || true
SUM="$OUT/_status-summary.json"

# 1) gather: 确定性统计 + zg 检索实现痕迹（表格打到终端；JSON 写 $SUM）
python3 - "$SCRATCH" "$OUT" "$DETAIL" "$SUM" "$ZG" "$REPO" "$SEMANTIC" <<'PY'
import json, sys, glob, os, re, subprocess, shutil
scratch, out, detail, sum_path, zg_bin, repo, semantic = (
    sys.argv[1], sys.argv[2], (sys.argv[3]=="1"), sys.argv[4],
    sys.argv[5] or "", sys.argv[6], (sys.argv[7]=="1"))

summary={"repo":os.path.realpath(os.path.join(scratch,"..")), "shared_state_feature":None,
         "shared_done":[], "repo_history":{}, "features":{}}

# 仓库级历史产物（旧流程痕迹，非新驱动命名）
LEGACY_EXT=(".log", "-prompt.md", "-evidence.json", "-review-pack.md", ".evidence.json")
legacy_total=0
if os.path.isdir(out):
    for fn in os.listdir(out):
        if fn.startswith("_status") or fn.startswith("_syn") or fn==".implement-state.json": continue
        low=fn.lower()
        if low.endswith(LEGACY_EXT) or "jev-review" in low or low.endswith(".log"):
            legacy_total+=1
summary["repo_history"]["legacy_artifacts"]=legacy_total

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

STOP=set("the this that with from have will for and are was were into onto over you to of in on at be is been being not by as or an it its specified implement implementation module process system file data gpt step make using use used via per the".split())

def zg_search(q):
    """return (n_files, [paths]) by running zg; None if zg unavailable"""
    if not zg_bin:
        return None, []
    excls=["-g","!.scratch/**","-g","!.agent-results/**","-g","!**/.git/**","-g","!**/.zvec-grep/**",
           "-g","!**/.lavish/**","-g","!**/_status*"]
    cwd=None
    if int(semantic)==0:
        # 词表层：managed ripgrep，search 走路径参数
        cmd=[zg_bin,"query","--rg","-e",q,"-m","20"]+excls+[repo]
    else:
        # 语义：索引按运行目录解析（尾随路径不生效、-e/-m 仅 rg 可用），需 cd 进 repo 根
        cwd=repo
        cmd=[zg_bin,"query"]+[q]+excls
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120,cwd=cwd)
    except Exception:
        return None,[]
    out_txt=r.stdout
    if r.returncode not in (0,1):   # 1 = 无匹配/缺索引；其它=错误
        return None,[]
    files=[]; seen=set()
    if int(semantic)==1:
        # 语义行形如:  #1 matchedBy=fts+vector path/to/file.jl:1-45
        prog=re.compile(r'^\s*#\d+\s+matchedBy=\S+\s+([^:\s](?:[^:]*))(?::\d+(?:-\d+)?)?\s*$')
        for ln in out_txt.splitlines():
            m=prog.match(ln)
            if m:
                p=m.group(1).strip()
                if p and p not in seen:
                    seen.add(p); files.append(p)
    else:
        for ln in out_txt.splitlines():
            if not ln.strip(): continue
            if re.match(r'^\s*\d+[:.]', ln): continue   # 内容行 N:xx
            if "Error" in ln or ln.startswith("zvec"): continue
            p=ln.strip().lstrip("·").strip()
            if p and p not in seen:
                seen.add(p); files.append(p)
    return len(files), files[:6]

def tokens_for(f, tickets):
    # 从 spec+票 提取高区分度领域词作检索 query
    texts=[]
    sp=os.path.join(scratch,f,"spec.md")
    if os.path.exists(sp):
        try: texts.append(open(sp,encoding="utf-8").read())
        except Exception: pass
    for t in tickets:
        try: texts.append(open(os.path.join(scratch,f,"issues",t+".md"),encoding="utf-8").read())
        except Exception: pass
    cnt={}
    catslug=re.split(r'[^a-z0-9]+',f.lower())
    for x in catslug: cnt[x]=cnt.get(x,0)+1
    for txt in texts:
        for w in re.findall(r'[a-zA-Z][a-zA-Z0-9]{3,}', txt.lower()):
            if w in STOP: continue
            cnt[w]=cnt.get(w,0)+1
    # 去掉太泛的
    top=[w for w,_ in sorted(cnt.items(),key=lambda kv:-kv[1]) if len(w)>=4]
    return [w for w in top if w not in ("agr","adr","mmith","psim")][:4]

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
    toks=tokens_for(f, tickets)
    # 词表层用 | 正则分列；语义用空格短语（嵌入按整句语义而非单个字）
    if toks:
        q=("|".join(re.escape(w) for w in toks) if int(semantic)==0 else " ".join(toks))
    else:
        q=""
    zgn, zgp = (zg_search(q) if q else (None,[]))
    summary["features"][f]={"tickets":len(tickets),"doc":doc,"ran":ran,"review_packs":review,
                            "done":done,"spec":spec,"state_owns":owns,
                            "zg_files":zgn,"zg_paths":zgp,"zg_query":q}
    rows.append((f,len(tickets),done,ran,review,doc,
                 (str(zgn) if zgn is not None else "NA"),"有" if spec else "无","接管" if owns else "-"))
with open(sum_path,"w",encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)

print(f"仓库历史产物(.agent-results).: {legacy_total}（旧流程痕迹，非新驱动命名）")
w=max([len(r[0]) for r in rows]+[7])
hdr=f"{'feature':<{w}} 票 已完成 跑过 卡住 文档 代码命中 spec 状态文件"
print(hdr); print("-"*len(hdr))
for r in rows:
    print(f"{r[0]:<{w}} {r[1]:>2} {r[2]:>4} {r[3]:>4} {r[4]:>4} {r[5]:>4} {r[6]:>8} {r[7]:>3} {r[8]:>6}")
for f in feats:
    fs=summary["features"][f]
    print(f"  · {f}: zg query=“{fs['zg_query']}” 命中 {fs['zg_files']} 文件 " +
          ("(".join(fs["zg_paths"][:3])+")" if fs["zg_paths"] else ""))
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
 ("从未开始/未运行","代码检索也无任何命中，也无运行记录"),
 ("推进中","有部分代码命中或有运行产物，但未见完成标记"),
 ("中途暂停","存在 review_pack，需人介入"),
 ("接近完成","票多 done 或代码命中广，差整体验收"),
 ("已完成待验收","票全 done 且代码命中充分，等整体验收门"),
 ("维护中/停滞","有历史痕迹但缺 spec/定位不清"),
]
qs={}
for f, fs in feats.items():
    zg = fs.get("zg_files")
    zg_s = ("代码命中 %s 个文件" % zg) if zg is not None else "代码检索不可用"
    if fs.get("zg_paths"):
        zg_s += " ("+", ".join(fs["zg_paths"][:3])+")"
    anchor=(f"tickets={fs['tickets']}, done={fs['done']}, ran={fs['ran']}, "
            f"review_packs={fs['review_packs']}, {zg_s}, "
            f"spec={'有' if fs['spec'] else '无'}")
    qs[f]={
      "type":"choice",
      "instructions":f"该 feature 的实现证据: {anchor}。关键是: 代码检索(zg)命中了它的实现文件,说明它大体已实现(可能只是未转移到新驱动状态)；切勿因新驱动下 ran/done=0 就判成'从未开始/未实现'。请据此选择最贴切阶段。",
      "criteria":{lab:desc for lab,desc in OPTS},
    }
focus_crit={}
for f, fs in feats.items():
    focus_crit[f]=(f"tickets={fs['tickets']},done={fs['done']},首拍代码命中={fs.get('zg_files')},"
                   f"review_packs={fs['review_packs']},spec={'有' if fs['spec'] else '无'}")
qs["focus"]={
  "type":"choice",
  "instructions":f"该仓库 .agent-results 有 {s['repo_history'].get('legacy_artifacts',0)} 个旧流程产物(可能含未转入新状态的历史实现)。综合各 feature 的代码命中与证据，下一步最应优先推进/验收/收尾哪一个，并说明原因。",
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
o="$(jev-decide decide "$REQ" 2>&1)"
code=$?
if [[ -n "$o" ]]; then printf '%s\n' "$o" > "$REQ.decisions.json"; fi
if [[ $code -eq 1 || -z "$o" ]]; then
  echo "status.sh: jev-decide 失败 (exit=$code)" >&2; printf '%s\n' "$o" | tail -20 >&2; exit 1
fi

# 4) render verdicts (choice values; flag low-confidence / needs-review per feature)
python3 - "$SUM" "$REQ.decisions.json" <<'PY'
import json, sys
s=json.load(open(sys.argv[1])); dec=json.load(open(sys.argv[2])).get("decisions",{})
feats=dict(s["features"])
print("\n=== 全部 feature 状态（Jev 判断，已含 zg 代码检索证据）===")
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