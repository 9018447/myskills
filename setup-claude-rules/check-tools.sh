#!/usr/bin/env bash
# 检查搜索路由规则与编码分工规则依赖的工具是否在 PATH 中。
# 始终 exit 0：缺工具不阻断安装，只报告，由用户决定先装还是照常写规则。

for t in rg zg ast-grep gitnexus acpx; do
  if command -v "$t" >/dev/null 2>&1; then
    echo "ok      $t -> $(command -v "$t")"
  else
    echo "MISSING $t"
  fi
done

# aider-rs 是 Claude Code 插件（MCP 工具），不是 PATH 命令。装在全局插件目录时 claude plugin list 能看到；
# 但若仅在 aider-rs 源码仓库根目录里开发载入，则 session 里虽有工具、本机全局却查不到。
if claude plugin list 2>/dev/null | grep -q 'aider-rs'; then
  echo "ok      aider-rs -> (Claude plugin, via claude plugin list)"
else
  echo "MISSING aider-rs  全局未安装；编码分工规则依赖它，需先装插件（见 aider-rs 仓库 plugin/install.sh）。"
  echo "        note        若本会话运行在该插件源码仓库内（开发模式），工具可用但 claude plugin list 也查不到，属正常。"
fi

# LSP 不是命令行工具，由宿主 agent 内置提供，这里只能提示
echo "note    LSP 由宿主 agent（如 Claude Code）内置提供，脚本无法检查"
