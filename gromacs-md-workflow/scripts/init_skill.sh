#!/bin/bash
# 将 skill 的 .claude/ 配置部署到项目根 .claude/
# 用法: bash scripts/init_skill.sh [--dry-run] [--force]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SOURCE="$SKILL_DIR/.claude"
# skill 在 .claude/skills/VLE_gromacs_md/，需要上溯 3 级到项目根
TARGET="$(cd "$SKILL_DIR/../../.." && pwd)/.claude"

DRY_RUN=false
FORCE=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --force) FORCE=true ;;
    *) echo "未知参数: $arg"; exit 1 ;;
  esac
done

if [ ! -d "$SOURCE" ]; then
  echo "✗ 源目录不存在: $SOURCE"
  exit 1
fi

echo "Skill 目录: $SKILL_DIR"
echo "部署目标:   $TARGET"
echo ""

# 1. 确保目标目录存在
if [ "$DRY_RUN" = false ]; then
  mkdir -p "$TARGET/agents"
fi

# 2. 部署 agents/
for agent_file in "$SOURCE/agents/"*.md; do
  [ -f "$agent_file" ] || continue
  fname=$(basename "$agent_file")
  dest="$TARGET/agents/$fname"
  if [ "$DRY_RUN" = true ]; then
    echo "[dry-run] 复制 agents/$fname -> $dest"
  elif [ -f "$dest" ] && [ "$FORCE" = false ]; then
    read -p "agents/$fname 已存在，覆盖? [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] && cp "$agent_file" "$dest" && echo "  ✓ agents/$fname"
  else
    cp "$agent_file" "$dest" && echo "  ✓ agents/$fname"
  fi
done

# 3. 部署 CLAUDE.md -> CLAUDE_VLE.md（不覆盖项目已有 CLAUDE.md）
src_claude="$SOURCE/CLAUDE.md"
dest_claude="$TARGET/CLAUDE_VLE.md"
if [ -f "$src_claude" ]; then
  if [ "$DRY_RUN" = true ]; then
    echo "[dry-run] 复制 CLAUDE.md -> $dest_claude"
  else
    cp "$src_claude" "$dest_claude" && echo "  ✓ CLAUDE_VLE.md"
  fi
fi

# 4. 合并 settings.json
src_settings="$SOURCE/settings.json"
dest_settings="$TARGET/settings.json"
if [ -f "$src_settings" ]; then
  if [ "$DRY_RUN" = true ]; then
    echo "[dry-run] 合并 settings.json hooks -> $dest_settings"
  elif [ ! -f "$dest_settings" ]; then
    cp "$src_settings" "$dest_settings" && echo "  ✓ settings.json（新建）"
  else
    # 用 python3 合并：将 skill 的 hooks 追加到项目已有 settings.json
    python3 - "$src_settings" "$dest_settings" <<'PYEOF'
import json, sys

src_path, dst_path = sys.argv[1], sys.argv[2]
with open(src_path) as f:
    src = json.load(f)
with open(dst_path) as f:
    dst = json.load(f)

# 合并 hooks（按 matcher 分组追加）
for matcher_type in ["PreToolUse", "PostToolUse"]:
    src_hooks = src.get("hooks", {}).get(matcher_type, [])
    dst_hooks = dst.setdefault("hooks", {}).setdefault(matcher_type, [])
    for src_group in src_hooks:
        m = src_group["matcher"]
        existing = next((g for g in dst_hooks if g["matcher"] == m), None)
        if existing:
            # 同一 matcher 的 hooks 数组合并（去重按 command）
            existing_cmds = {h["command"] for h in existing["hooks"]}
            for h in src_group["hooks"]:
                if h["command"] not in existing_cmds:
                    existing["hooks"].append(h)
        else:
            dst_hooks.append(src_group)

# 合并 permissions.allow（去重）
src_allow = src.get("permissions", {}).get("allow", [])
dst_allow = dst.setdefault("permissions", {}).setdefault("allow", [])
for p in src_allow:
    if p not in dst_allow:
        dst_allow.append(p)

with open(dst_path, "w") as f:
    json.dump(dst, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("  ✓ settings.json（已合并）")
PYEOF
  fi
fi

echo ""
echo "✓ 部署完成。skill 配置已部署到 $TARGET"
