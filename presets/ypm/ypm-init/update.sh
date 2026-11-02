#!/bin/sh
# YPM skills 批量重连（2026-10-28 首相令）。按 ~/cabinet.yaml 把 archives/<role>/skills、
# library/playbooks、library/principles 以相对软链接注册进各 Agent 用户级技能目录。
# 只动 skills 链接：不碰 AGENTS.md/指令文件（2026-10-28 首相令），不动真实文件与其他来源配置。
# 公务员角色组变换时，更新 archive_for_role 的映射。
# 同名旧链接确认是软链接即改链本包（2026-10-24 裁定）；真实文件冲突保留现状并报告；
# 指向本包 archives/library 的死链直接清除；重复执行结果不变。
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
ROSTER=${ROSTER:-"$HOME/cabinet.yaml"}

[ -f "$ROSTER" ] || { echo "名册不存在: $ROSTER" >&2; exit 1; }
[ -d "$SCRIPT_DIR/library/playbooks" ] && [ -d "$SCRIPT_DIR/archives" ] || {
	echo "包目录不完整（本脚本应放在 ypm-init/ 内）: $SCRIPT_DIR" >&2
	exit 1
}

created=0
relinked=0
removed=0
conflicts=""

archive_for_role() {
	case "$1" in
	permanent_secretaries) echo "permanent-secretary" ;;
	private_secretary) echo "private-secretary" ;;
	permanent_under_secretaries) echo "permanent-under-secretary" ;;
	*)
		r=$(printf '%s' "$1" | sed 's/_secretaries$/_secretary/; s/_/-/g')
		[ -d "$SCRIPT_DIR/archives/$r/skills" ] && echo "$r" || return 1
		;;
	esac
}

link_one() { # $1 目标技能目录 $2 源技能目录
	name=$(basename "$2")
	dst="$1/$name"
	want=$(realpath --relative-to="$1" "$2")
	if [ -L "$dst" ]; then
		[ "$(readlink "$dst")" = "$want" ] && return 0
		ln -sfn "$want" "$dst" || return 1
		relinked=$((relinked + 1))
		echo "  改链 $name"
	elif [ -e "$dst" ]; then
		conflicts="$conflicts$dst（真实文件，未动）
"
	else
		ln -s "$want" "$dst" || return 1
		created=$((created + 1))
		echo "  新链 $name"
	fi
}

MAP=$(awk '
	BEGIN { FS = ":" }
	/^[A-Za-z_]+:[[:space:]]*$/ { sec = $1; role = ""; next }
	sec == "civil_servants" && /^  [A-Za-z_]+:[[:space:]]*$/ {
		role = $1; sub(/^[[:space:]]+/, "", role); next
	}
	/^[[:space:]]+skills_dir:/ {
		v = $2; sub(/^[[:space:]]+/, "", v)
		if (sec == "minister") print "minister\t" v
		else if (role != "") print role "\t" v
	}
' "$ROSTER")

[ -n "$MAP" ] || { echo "名册未解析到任何 skills_dir" >&2; exit 1; }

while IFS="	" read -r role dir; do
	[ -n "$role" ] || continue
	echo "== $role -> $dir"
	if [ ! -d "$dir" ]; then
		echo "  !! 技能目录不存在，跳过"
		continue
	fi
	arch=$(archive_for_role "$role") || arch=""
	if [ -z "$arch" ] && [ "$role" != "minister" ]; then
		echo "  !! 未知角色组，请更新本脚本的角色映射"
		continue
	fi
	for l in $(find "$dir" -maxdepth 1 -xtype l 2>/dev/null); do
		t=$(readlink "$l" || true)
		case "$t" in
		*ypm-init/archives/* | *ypm-init/library/*)
			rm "$l" && {
				echo "  清死链 $(basename "$l")"
				removed=$((removed + 1))
			}
			;;
		esac
	done
	if [ -n "$arch" ]; then
		for src in "$SCRIPT_DIR/archives/$arch/skills"/*; do
			[ -f "$src/SKILL.md" ] && link_one "$dir" "$src"
		done
	fi
	for src in "$SCRIPT_DIR/library/playbooks"/* "$SCRIPT_DIR/library/principles"/*; do
		[ -f "$src/SKILL.md" ] && link_one "$dir" "$src"
	done
done <<EOF
$MAP
EOF

echo
echo "== 复检"
while IFS="	" read -r role dir; do
	[ -n "$role" ] || continue
	[ -d "$dir" ] || continue
	own=0
	bad=0
	for e in "$dir"/*; do
		[ -L "$e" ] || continue
		rf=$(readlink -f "$e" 2>/dev/null) || rf=""
		case "$rf" in
		"$SCRIPT_DIR"/*)
			own=$((own + 1))
			[ -f "$e/SKILL.md" ] || {
				bad=$((bad + 1))
				echo "  !! SKILL.md 不可读: $e"
			}
			;;
		esac
	done
	dead=$(find "$dir" -maxdepth 1 -xtype l 2>/dev/null | wc -l)
	echo "   $role: 本包链接 $own，不可读 $bad，死链 $dead"
done <<EOF
$MAP
EOF

echo
echo "== 汇总: 新链 $created，改链 $relinked，清死链 $removed"
if [ -n "$conflicts" ]; then
	echo "== 冲突（保留现状，待裁）:"
	printf '%s' "$conflicts"
fi
exit 0
