# AGENTS.md — myskills 仓库约定

这个仓库是个人技能库的中心仓库。中心远程是 Codeup（`aliyun`），`git push aliyun` 会同时推送到 GitHub 和 Gitee 镜像。

## 目录布局

- 顶层目录 = 一个技能（含 `SKILL.md`）
- 例外：`manager/`（管理工具）、`machines/`（各机器状态）、集合目录（`data-processing/`、`molecular-*/`、`tools/`、`machine-learning-potentials/`、`atomistic-workflows/`、`agent-workflow/`、`matlab-skills-catalog/`、`mattpocock-skills-zh/`，它们内部含子技能）
- `agents.json` —— agent 注册表：id、名称、skills 目录路径（支持 `~`）。新增支持的 agent 就加一条
- `skills-manifest.json` —— 分发清单：每个 agent 装哪些技能。**这是分发的唯一来源**
- `machines/<hostname>.json` —— 各机器同步状态（sha、时间、断链数）

## 行为约定

1. **改了技能就当场 `git add` + `commit` + `git push aliyun`**，不要堆积未提交的改动。
2. **不要手工**在各 agent 的 skills 目录（`~/.claude/skills` 等）里创建实体目录或符号链接。分发只通过 `skills-manifest.json` + `link` 完成。
3. 不要把密钥、机器特定路径写进技能。`.secret.key` 已被 gitignore，保持如此。
4. 集合目录里的子技能参与分发时，清单里写集合内的相对路径形式目前不支持——需要分发的技能应放在顶层。

## 工具用法（manager/）

```bash
node manager/src/cli.ts link       # 按清单重建各 agent 目录的符号链接（清理孤儿/断链）
node manager/src/cli.ts status     # 写入 machines/<hostname>.json
node manager/src/cli.ts sync       # pull --ff-only → link → status → 提交并推送状态
node manager/src/cli.ts install <github-url> [--name n]   # 从 GitHub 安装技能入仓并推送（走 gh，支持 /tree/ref/subdir 集合仓子目录）
node manager/src/cli.ts migrate    # 存量收敛 dry-run；加 --apply 执行
node manager/src/tui.ts            # 管理 TUI：浏览/搜索技能、勾选分发、link/sync、机器状态、agent 注册表、GitHub 安装
```

测试：`cd manager && npm test`（node:test，fixture 文件系统 + 本地裸仓库 + PATH 注入桩 gh）。

## 新机器 bootstrap

```bash
git clone git@codeup.aliyun.com:69b3a6855523c716219ff9a9/myskills.git ~/my-skills
cd ~/my-skills
node manager/src/cli.ts migrate --apply   # 若本机有存量技能目录；否则跳过
node manager/src/cli.ts sync              # 拉最新、按清单建链接、上报状态
```

安装新技能只在登录了 `gh` 的机器上执行；分发靠 git，其他机器 `sync` 即得。
