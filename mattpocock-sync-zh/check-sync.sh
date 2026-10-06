#!/usr/bin/env bash
set -euo pipefail

# check-sync.sh — 检测/拉取/接受 mattpocock/skills 上游变化，维护 -zh 翻译的同步基线。
# 基线是"每个上游技能目录内文件的内容哈希(blob sha)"，代表本仓库已吸收到上游哪个版本。
# 中文译文不与上游英文逐字节比对；本脚本只追踪上游移动。
#
# 依赖: gh + jq（git 分发靠 git）。零新增依赖。

SCRIPT_REAL="$(readlink -f "${BASH_SOURCE[0]}")"
REPO_ROOT="$(cd "$(dirname "$SCRIPT_REAL")/.." && pwd)"
MIRROR="$REPO_ROOT/mattpocock-skills-zh"
BASELINE="$MIRROR/.sync-baseline.json"
STAGING="$MIRROR/.sync-staging"
UPSTREAM="mattpocock/skills"
REF="main"

usage() { cat <<'EOF'
用法:
  check-sync.sh [--check]     读基线→拉上游树→对比→打印"上游前移"的技能列表。
                              无基线时先建立基线(首次)并存覆盖表。
  check-sync.sh --pull <skill> 把该技能上游当前+基线两份内容抓进 .sync-staging/<skill>/ 作 .old/.new，供对照重译。
  check-sync.sh --accept <skill> 翻译完成后，把该技能基线哈希更新为当前上游状态(标记已吸收)。
  check-sync.sh --reset      删除基线重建(首次运行/异常修复用)。
EOF
}

need() { command -v "$1" >/dev/null 2>&1 || { echo "缺少依赖: $1" >&2; exit 1; }; }

# 输出 "path<TAB>sha" —— 上游 skills/ 下所有有效技能内容文件
fetch_tree() {
  local tmp; tmp="$(mktemp)"
  gh api "repos/$UPSTREAM/git/trees/$REF?recursive=1" > "$tmp" 2>/dev/null \
    || { echo "无法拉取上游 tree（网络 / gh 鉴权？）" >&2; rm -f "$tmp"; exit 1; }
  jq -r '.tree[]
         | select(.type=="blob")
         | select(.path|startswith("skills/"))
         | select(.path|test("^skills/(deprecated|in-progress)/")|not)
         | select(.path|test("\\.(png|svg|gif|jpg|jpeg|webp)$")|not)
         | select(.path|match("^skills/[^/]+/[^/]+/"))
         | [.path,.sha] | @tsv' "$tmp"
  rm -f "$tmp"
}

skill_of()        { printf '%s' "$1" | cut -d/ -f1-3; }   # skills/<cat>/<skill>
basename_of_skill(){ printf '%s' "$1" | awk -F/ '{print $3}'; }

zh_exists() { [ -n "${1:-}" ] && [ -f "$REPO_ROOT/$1-zh/SKILL.md" ]; }

# 读 "path<TAB>sha" 行流到关联数组 (全局 $1 为数组名)
load_map() {
  local -n _map="$1"; _map=()
  while IFS=$'\t' read -r p s; do [ -n "$p" ] && _map["$p"]="$s"; done
}

write_baseline() {
  local ts; ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  {
    printf '{\n  "upstream": "%s",\n  "ref": "%s",\n  "updated_at": "%s",\n  "tree": {\n' "$UPSTREAM" "$REF" "$ts"
    local first=1 key
    for key in "${!BASE[@]}"; do
      [ "$first" = 1 ] || printf ',\n'; first=0
      printf '    %s: %s' "$(jq -n --arg v "$key" '$v')" "$(jq -n --arg v "${BASE[$key]}" '$v')"
    done
    printf '\n  }\n}\n'
  } > "$BASELINE"
}

need gh; need jq

cmd="${1:---check}"

if [ "$cmd" = "--reset" ]; then
  rm -f "$BASELINE"; echo "已删除基线 $BASELINE"; exit 0
fi

NOW_TREE="$(mktemp)"; trap 'rm -f "$NOW_TREE"' EXIT
fetch_tree > "$NOW_TREE"

declare -A CUR
load_map CUR < "$NOW_TREE"

# 基线（可能还没有）
declare -A BASE
has_base=0
if [ -f "$BASELINE" ]; then
  load_map BASE < <(jq -r '.tree | to_entries[] | "\(.key)\t\(.value)"' "$BASELINE")
  has_base=1
fi

# ......... --check / 默认 .........
if [ "$cmd" != "--pull" ] && [ "$cmd" != "--accept" ]; then
  if [ "$has_base" = 0 ]; then
    # 首次运行：整体建立基线，打印覆盖表
    for key in "${!CUR[@]}"; do BASE["$key"]="${CUR[$key]}"; done
    write_baseline
    echo "首次运行：已在当前上游 $REF 建立基线（现有中文翻译视为已吸收到当前版本）。"
    echo "上游 → 中文 覆盖表："
    printf '  %-20s %s\n' "上游技能" "状态"
    for d in "${!CUR[@]}"; do printf '%s\n' "$(skill_of "$d")"; done | sort -u | while read -r d; do
      z="$(basename_of_skill "$d")"
      if zh_exists "$z"; then printf '  %-20s 已翻译\n' "$z"; else printf '  %-20s 未翻译(缺 zh)\n' "$z"; fi
    done
    exit 0
  fi

  declare -A CHANGED_KEYS CHANGED_DIRS
  dir_cnt=0
  for key in "${!CUR[@]}"; do
    if [ -z "${BASE[$key]+x}" ]; then      CHANGED_KEYS["$key"]="新增"; CHANGED_DIRS["$(skill_of "$key")"]=1; dir_cnt=$((dir_cnt+1))
    elif [ "${CUR[$key]}" != "${BASE[$key]}" ]; then CHANGED_KEYS["$key"]="变更"; CHANGED_DIRS["$(skill_of "$key")"]=1; dir_cnt=$((dir_cnt+1)); fi
  done
  for key in "${!BASE[@]}"; do
    if [ -z "${CUR[$key]+x}" ]; then       CHANGED_KEYS["$key"]="移除"; CHANGED_DIRS["$(skill_of "$key")"]=1; dir_cnt=$((dir_cnt+1)); fi
  done

  if [ "$dir_cnt" -eq 0 ]; then
    echo "✅ 相对上次同步，上游 skills/ 无变化。"
    exit 0
  fi

  echo "上游 skills/ 相对上次同步有 ${#CHANGED_DIRS[@]} 个技能前移："
  printf '  %-22s %-14s %s\n' "上游技能" "zh" "变化文件"
  for d in $(printf '%s\n' "${!CHANGED_DIRS[@]}" | sort); do
    z="$(basename_of_skill "$d")"
    if zh_exists "$z"; then zseen="已有 $z-zh"; else zseen="未翻译"; fi
    filelist=""
    for key in "${!CHANGED_KEYS[@]}"; do
      if [ "$(skill_of "$key")" = "$d" ]; then
        short="${key#"$d"/}"
        [ -n "$filelist" ] && filelist+=", "
        filelist+="$short[${CHANGED_KEYS[$key]}]"
      fi
    done
    printf '  %-22s %-14s %s\n' "$z" "$zseen" "$filelist"
  done
  exit 0
fi

# ......... --pull .........
if [ "$cmd" = "--pull" ]; then
  skill="${2:-}"; [ -n "$skill" ] || { usage; exit 1; }
  [ -f "$BASELINE" ] || { echo "尚无基线；先跑 check-sync.sh --check 建立基线。" >&2; exit 1; }

  target=""
  for p in "${!CUR[@]}"; do
    if [ "$(basename_of_skill "$(skill_of "$p")")" = "$skill" ]; then target="$(skill_of "$p")"; break; fi
  done
  [ -n "$target" ] || { echo "上游没有该技能(skill 名不匹配)：$skill" >&2; exit 1; }

  out="$STAGING/$skill"; mkdir -p "$out"
  new_cnt=0; old_cnt=0
  for p in "${!CUR[@]}"; do
    [ "$(skill_of "$p")" = "$target" ] || continue
    rel="${p#"$target"/}"; dest="$out/$rel.new"; mkdir -p "$(dirname "$dest")"
    gh api "repos/$UPSTREAM/contents/$p?ref=$REF" -q '.content' 2>/dev/null \
      | { base64 -d 2>/dev/null || true; } > "$dest" || true
    new_cnt=$((new_cnt+1))
  done
  for key in "${!BASE[@]}"; do
    [ "$(skill_of "$key")" = "$target" ] || continue
    rel="${key#"$target"/}"; dest="$out/$rel.old"; mkdir -p "$(dirname "$dest")"
    gh api "repos/$UPSTREAM/git/blobs/${BASE[$key]}" -q '.content' 2>/dev/null \
      | { base64 -d 2>/dev/null || true; } > "$dest" || true
    old_cnt=$((old_cnt+1))
  done

  echo "已拉取 $skill 到 $out/：当前→*.new（$new_cnt 个文件），上版→*.old（$old_cnt 个文件）。"
  echo "重译：diff $out/SKILL.md.old $out/SKILL.md.new ；译完跑 check-sync.sh --accept $skill"
  exit 0
fi

# ......... --accept .........
if [ "$cmd" = "--accept" ]; then
  skill="${2:-}"; [ -n "$skill" ] || { usage; exit 1; }
  [ -f "$BASELINE" ] || { echo "尚无基线；先跑 check-sync.sh --check 建立基线。" >&2; exit 1; }

  changed=0
  # 更新/移除本技能既有条目
  for key in "${!BASE[@]}"; do
    if [ "$(basename_of_skill "$(skill_of "$key")")" = "$skill" ]; then
      if [ -n "${CUR[$key]+x}" ] && [ "${BASE[$key]}" != "${CUR[$key]}" ]; then
        BASE["$key"]="${CUR[$key]}"; changed=$((changed+1))
      elif [ -z "${CUR[$key]+x}" ]; then
        unset 'BASE[$key]'; changed=$((changed+1))
      fi
    fi
  done
  # 吸收本技能下、上游新增的文件
  for p in "${!CUR[@]}"; do
    if [ "$(basename_of_skill "$(skill_of "$p")")" = "$skill" ] && [ -z "${BASE[$p]+x}" ]; then
      BASE["$p"]="${CUR[$p]}"; changed=$((changed+1))
    fi
  done
  write_baseline
  echo "已把 $skill 标记为吸收到当前上游（$changed 处哈希更新）。再跑 --check 不再报它。"
  exit 0
fi

usage