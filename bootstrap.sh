#!/usr/bin/env bash
# myskills 快速初始化：新机器克隆仓库后跑这一个脚本即可
# 用法：git clone git@codeup.aliyun.com:69b3a6855523c716219ff9a9/myskills.git ~/myskills && ~/myskills/bootstrap.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 检查环境"
command -v git >/dev/null || { echo "缺 git"; exit 1; }
command -v node >/dev/null || { echo "缺 node"; exit 1; }
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] || { echo "需要 node >= 22（当前 $(node -v)）"; exit 1; }
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 -T git@codeup.aliyun.com 2>&1 | grep -q 'successfully'; then
  echo "警告: codeup SSH 不通，sync 推送会失败；先去 Codeup 后台加公钥"
fi

echo "==> 安装 CLI（manager npm link）"
(cd manager && npm install && npm link)

echo "==> 收敛存量技能（dry-run 预览，有则应用）"
if ! myskills migrate >/tmp/myskills-migrate-dryrun 2>&1 || [ -s /tmp/myskills-migrate-dryrun ]; then
  cat /tmp/myskills-migrate-dryrun
  myskills migrate --apply
fi

echo "==> 同步并重建全局软链"
myskills sync

echo "==> 完成。验证：myskills 进 TUI；ls -l ~/.claude/skills 应指向 $PWD"
