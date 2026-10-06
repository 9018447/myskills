#!/usr/bin/env bash
# 为指定仓库确定性地安装 agent 规则集。脚本驱动，幂等，缺工具不阻断。
# 用法: install.sh [目标仓库根目录，缺省当前目录]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(pwd)}"
ROOT="$(cd "$ROOT" && pwd)"
RULES_DIR="$ROOT/.claude/rules"

# 1. 工具检查（check-tools.sh 恒 exit 0，缺工具只报告不阻断）
TOOLS="$(bash "$SCRIPT_DIR/check-tools.sh" 2>&1 || true)"

# 2. 写两个细则文件（覆盖已存在者）
mkdir -p "$RULES_DIR"
cp "$SCRIPT_DIR/ADD_RULES.md"  "$RULES_DIR/code-search.md"
cp "$SCRIPT_DIR/CODING_RULES.md" "$RULES_DIR/coding-principle.md"

# 3. 选概要落点：CLAUDE.md 存在用它；否则 AGENTS.md；都不存在创建 AGENTS.md
summary_action="updated summary"
if [[ -f "$ROOT/CLAUDE.md" ]]; then
  SUMMARY="$ROOT/CLAUDE.md"
elif [[ -f "$ROOT/AGENTS.md" ]]; then
  SUMMARY="$ROOT/AGENTS.md"
else
  SUMMARY="$ROOT/AGENTS.md"
  summary_action="created summary file"
fi

# 4. 幂等追加：从文件里第一个 '## Tool Routing' 起截断旧块，再追加模板原文。
#    只动尾部块，保留其上方的用户章节。
tmp="$(mktemp)"
# 尾部已有旧块时截断；文件不存在（首次创建 AGENTS.md）时直接空输出
if [[ -f "$SUMMARY" ]]; then
  awk '!/^## Tool Routing/ { print } /^## Tool Routing/ { exit }' "$SUMMARY" > "$tmp"
fi
mv "$tmp" "$SUMMARY"
cat "$SCRIPT_DIR/APPEND_CLAUDE.md" >> "$SUMMARY"

# 5. 结果摘要
echo "$TOOLS"
echo "rules -> $RULES_DIR/code-search.md, $RULES_DIR/coding-principle.md"
echo "summary: $SUMMARY ($summary_action)"
echo "done:   code-search.md 与 coding-principle.md 已写入，概要块已落位；三处写入完成。"