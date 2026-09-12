---
name: myskills-bootstrap
description: 在新机器上初始化 myskills 技能分发体系：克隆中心仓库、注册全局命令、收敛存量技能、建立符号链接。当用户说"初始化技能库""bootstrap skills""新机器装技能"时使用。
---

# myskills 新机器初始化

中心仓库在 Codeup（国内直连），GitHub/Gitee 是镜像。分发的唯一来源是仓库根的 `skills-manifest.json`，各 agent 的 skills 目录里只允许出现指向仓库的符号链接。

## 前提检查

依次确认，缺什么先装什么：

1. `git --version` 可用
2. `node --version` ≥ 22（需要能直接跑 .ts）
3. SSH key 已加到 Codeup：`ssh -T git@codeup.aliyun.com` 能通（不通则提示用户去 Codeup 后台加公钥）

## 初始化步骤

```bash
# 1. 克隆中心仓库
git clone git@codeup.aliyun.com:69b3a6855523c716219ff9a9/myskills.git ~/my-skills
cd ~/my-skills

# 2. 注册全局命令（以后直接敲 myskills）
cd manager && npm install && npm link && cd ..

# 3. 仅当本机已有存量技能目录时执行（全新机器跳过）：
#    ~/.agents/skills ~/.claude/skills ~/.cursor/skills ~/.kimi-code/skills
#    ~/.codex/skills ~/.pi/agent/skills ~/.omp/agent/skills
myskills migrate          # 先 dry-run 看计划
myskills migrate --apply  # 确认后执行：独有技能拷入仓库，其余换成符号链接

# 4. 同步：拉最新、按清单建全局链接、上报本机状态到 machines/
myskills sync
```

## 验证

- `myskills` 不带参数能进 TUI
- 各 agent 的 skills 目录里是指向 `~/my-skills/` 的符号链接，且无断链：
  `ls -l ~/.claude/skills` 等，箭头应指向 myskills 仓库
- `machines/<本机hostname>.json` 已生成并随 sync 推送

## 日常命令

- `myskills` —— TUI：浏览/搜索技能、勾选分发、机器状态、agent 注册表
- `myskills sync` —— 拉取远程改动并重建链接（有更新就跑）
- `myskills install <github-url>` —— 从 GitHub 装新技能（需 `gh` 已登录），其他机器 sync 即得
- `myskills link` —— 只按清单重建符号链接
- `myskills init [--skills a,b]` —— 在项目 git 根生成 `.myskills.json` 作为项目级分发清单，项目级目标目录（如 `.claude/skills`）不存在时自动创建
- 项目级分发：在项目根运行 `myskills init`（可用 `--skills` 指定技能），再在项目内任意子目录运行 `myskills link`；如需操作中心仓库全局清单，使用 `myskills link --global`
- 也可以直接进 TUI：界面常驻标出当前是用户级还是项目级，`o` 在两者间切换；项目还没有 `.myskills.json` 时按 `o` 就地新建（落 git 根）并创建目标目录
- 所有命令都可从任意目录运行；必要时用 `MYSKILLS_ROOT=/path/to/my-skills` 指定中心仓库

## 注意

- 不要手工在各 agent 的 skills 目录里建目录或链接，一律改 `skills-manifest.json` 后 `myskills link`（或在 TUI 里勾选后按 l）
- 项目级分发只通过项目根 `.myskills.json` 的 `skills`/`targets` 配置，并用项目内 `myskills link` 建链；目标目录由 init/link/TUI 自动创建，不要手工建
- 首次 clone 较慢（历史里有约 435MB 的快照提交），属正常
- 改了技能内容就当场 `git add && git commit && git push aliyun`，不要堆积
