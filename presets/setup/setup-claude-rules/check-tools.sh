#!/usr/bin/env bash
# 检查搜索路由规则与编码分工规则依赖的工具是否在 PATH 中。
# 始终 exit 0：缺工具不阻断安装，只报告，由用户决定先装还是照常写规则。

for t in jg rg zg ast-grep gitnexus acpx; do
  if command -v "$t" >/dev/null 2>&1; then
    echo "ok      $t -> $(command -v "$t")"
  else
    echo "MISSING $t"
  fi
done

# jg 需要 OpenRouter 凭据，有命令没凭据照样不可用
if command -v jg >/dev/null 2>&1; then
  jg doctor >/dev/null 2>&1 && echo "ok      jg auth (Jev reachable)" || echo "WARN    jg auth 未配置/不可达，跑一次 jg auth"
fi

# LSP 不是命令行工具，由宿主 agent 内置提供，这里只能提示
echo "note    LSP 由宿主 agent（如 Claude Code）内置提供，脚本无法检查"
