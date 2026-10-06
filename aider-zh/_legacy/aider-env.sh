#!/usr/bin/env bash
# 从 Claude Code 的 ~/.claude/settings.json env 块一次性提取网关配置，
# 导出成 litellm/aider 认的环境变量后 exec aider。
# 用法: aider-env.sh [aider 参数...]   （与直接调 aider 相同，模型自动带上）
set -euo pipefail

SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
[[ -f "$SETTINGS" ]] || { echo "settings not found: $SETTINGS" >&2; exit 1; }

BASE_URL="$(jq -r '.env.ANTHROPIC_BASE_URL // empty' "$SETTINGS")"
TOKEN="$(jq -r '.env.ANTHROPIC_AUTH_TOKEN // .env.ANTHROPIC_API_KEY // empty' "$SETTINGS")"
MODEL="$(jq -r '.env.ANTHROPIC_MODEL // empty' "$SETTINGS")"

export ANTHROPIC_API_BASE="$BASE_URL" ANTHROPIC_BASE_URL="$BASE_URL"
export ANTHROPIC_API_KEY="$TOKEN" ANTHROPIC_AUTH_TOKEN="$TOKEN"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# litellm 不认识自建网关的模型名（如 glm-5.3-flash[1m]），窗口/输出上限会算成 0，
# aider 会误报 token 超限；用元数据文件补上真实上限。
if [[ -f "$SCRIPT_DIR/aider-model-metadata.json" && ! " $* " == *" --model-metadata-file "* ]]; then
  set -- --model-metadata-file "$SCRIPT_DIR/aider-model-metadata.json" "$@"
fi

# 用户显式传了 --model 就尊重用户，否则用 settings 里的模型名
if [[ -n "$MODEL" && ! " $* " == *" --model "* ]]; then
  set -- --model "anthropic/$MODEL" "$@"
fi

exec aider "$@"
