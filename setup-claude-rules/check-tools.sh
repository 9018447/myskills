#!/usr/bin/env bash
# 检查搜索路由规则与编码分工规则依赖的工具是否在 PATH 中。
# 始终 exit 0：缺工具不阻断安装，只报告，由用户决定先装还是照常写规则。

for t in rg zg ast-grep gitnexus aider acpx; do
  if command -v "$t" >/dev/null 2>&1; then
    echo "ok      $t -> $(command -v "$t")"
  else
    echo "MISSING $t"
  fi
done

# LSP 不是命令行工具，由宿主 agent 内置提供，这里只能提示
echo "note    LSP 由宿主 agent（如 Claude Code）内置提供，脚本无法检查"
