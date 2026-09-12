# AGENTS.md — myskills 仓库约定

这个仓库是个人技能库的中心仓库。中心远程是 Codeup（`aliyun`），`git push aliyun` 会同时推送到 GitHub 和 Gitee 镜像。

## 目录布局

- 顶层目录 = 一个技能（含 `SKILL.md`）
- 例外：`manager/`（管理工具）、`machines/`（各机器状态）、集合目录（`data-processing/`、`molecular-*/`、`tools/`、`machine-learning-potentials/`、`atomistic-workflows/`、`agent-workflow/`、`matlab-skills-catalog/`、`mattpocock-skills-zh/`，它们内部含子技能）
- `agents.json` —— agent 注册表：id、名称、skills 目录路径（支持 `~`；也支持项目级 agent，填项目内的绝对路径）。新增支持的 agent 就加一条
- `skills-manifest.json` —— 分发清单：每个 agent 装哪些技能。**这是分发的唯一来源**。另有两个可选字段：`sources`（技能来源 GitHub 仓库，install 时自动记录）、`presets`（预设集：名字 → 技能列表，TUI 里按 p 管理，应用到 agent 时并集追加）
- `machines/<hostname>.json` —— 各机器同步状态（sha、时间、断链数）

## 行为约定

1. **改了技能就当场 `git add` + `commit` + `git push aliyun`**，不要堆积未提交的改动。
2. **不要手工**在各 agent 的 skills 目录（`~/.claude/skills` 等）里创建实体目录或符号链接。分发只通过 `skills-manifest.json` + `link` 完成。
3. 不要把密钥、机器特定路径写进技能。`.secret.key` 已被 gitignore，保持如此。
4. 集合目录里的子技能参与分发时，清单里写集合内的相对路径形式目前不支持——需要分发的技能应放在顶层。

## 工具用法（manager/）

首次使用在 `manager/` 下跑一次 `npm link`，之后全局可用：

```bash
myskills                 # 进管理 TUI：浏览/搜索技能、勾选分发、分组浏览（g：按agent/来源/项目路径/预设集）、预设集（p）、机器状态、agent 注册表、GitHub 安装；标题与面板常驻标出作用域（用户级/项目级），项目目录下自动进项目模式，o 切项目/全局（项目没有 .myskills.json 时按 o 就地新建并创建目标目录）
myskills link            # 按清单重建各 agent 目录的符号链接（清理孤儿/断链）
myskills init [--skills a,b] # 在项目 git 根生成 .myskills.json：项目级目标默认全开并创建对应目录（不覆盖已有文件）
myskills status          # 写入 machines/<hostname>.json
myskills sync            # pull --ff-only → link → status → 提交并推送清单（skills-manifest.json、agents.json）与状态
myskills install <github-url> [--name n]   # 从 GitHub 安装技能入仓并推送（走 gh，支持 /tree/ref/subdir 集合仓子目录）
myskills migrate         # 存量收敛 dry-run；加 --apply 执行
```

`myskills` 可从任意目录运行：默认按命令安装位置定位中心仓库，也可用 `MYSKILLS_ROOT` 指定仓库根。`link` 在当前目录或其子目录向上找到 `.myskills.json` 时进入项目模式，把项目清单中的技能链接到项目内 agent 目录；`link --global` 强制按中心仓库的全局清单操作。项目级分发的目标 agent 与 `agents.json` 注册表相同，路径去掉 `~/` 前缀（如 `~/.claude/skills` → 项目内 `.claude/skills`），默认全部开启；`.myskills.json` 写了显式 `targets`（含空数组）则以它为准。目标目录不需要预先存在：`init`、TUI 按 `o` 建立项目级分发或重新开启某个目标、以及 `link` 都会自动创建（如 `.claude/skills`）。项目级分发可先在项目根运行 `myskills init --skills skill-a,skill-b`，再在项目内任意子目录运行 `myskills link`；也可以在项目目录下直接进 TUI——标题与面板常驻标出当前编辑的是用户级（`skills-manifest.json`）还是项目级（`.myskills.json`），项目里还没有清单时按 `o` 会新建（落在 git 根）并切进项目模式，勾选技能与切换目标 agent 都会写入 `.myskills.json`，`l` 走项目 link。

没跑过 `npm link` 的环境用 `node manager/src/cli.ts <子命令>` 等价替代；TUI 对应 `node manager/src/tui.ts`。

测试：`cd manager && npm test`（node:test，fixture 文件系统 + 本地裸仓库 + PATH 注入桩 gh）。

## 新机器 bootstrap

```bash
git clone git@codeup.aliyun.com:69b3a6855523c716219ff9a9/myskills.git ~/my-skills
cd ~/my-skills/manager && npm link && cd ..
myskills migrate --apply   # 若本机有存量技能目录；否则跳过
myskills sync              # 拉最新、按清单建链接、上报状态
```

安装新技能只在登录了 `gh` 的机器上执行；分发靠 git，其他机器 `sync` 即得。

<!-- handoff:start -->
## Active handoff

- 交接文档：`/tmp/agent-handoffs/smh--my-skills/handoff.md`
- 恢复被中断的工作时，先读这份交接文档再继续。
<!-- handoff:end -->
