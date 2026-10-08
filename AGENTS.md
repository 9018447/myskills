# AGENTS.md — myskills 仓库约定

这个仓库是个人技能库的中心仓库。中心远程是 GitHub（`origin`），`git push origin` 会同时推送到 Gitee 镜像。GitHub SSH 走 443 端口（`~/.ssh/config` 里已把 `github.com` 指到 `ssh.github.com:443`），因为 22 端口不通。

## 目录布局

- 顶层目录 = 一个技能（含 `SKILL.md`）；技能判别统一为「目录含 `SKILL.md` 才是技能」，无 `SKILL.md` 的顶层目录不再是技能
- `presets/<预设名>/<技能名>/` —— 预设集：预设成员技能的真身。预设文件夹内递归下探识别成员（穿过不含 `SKILL.md` 的中间目录，命中含 `SKILL.md` 的目录即成员）；平铺残留的非技能文件（CHANGELOG、docs 等）留在文件夹内不识别。原集合目录（agent-workflow、atomistic-workflows、data-processing、machine-learning-potentials、matlab-skills-catalog、molecular-*、tools、gitnexus 等）都已归位为预设文件夹
- 例外：`manager/`（管理工具）、`machines/`（各机器状态）、`testdir/`。顶层出现既无 `SKILL.md` 又非豁免的非空目录时，CLI/TUI 启动会交互询问是否移入 `presets/`：同意则移入，拒绝记入仓库根 `.preset-prompt.json` 持久化名单不再问；非交互环境跳过询问不动。名单可手改
- 启动 reconcile：每次 CLI/TUI 启动自动执行——为 `presets/` 成员补顶层相对符号链接、清理指向已删成员的断链；顶层真身与预设成员重名、同一技能归属两个预设会直接报错（不自动搬家）
- `agents.json` —— agent 注册表：id、名称、skills 目录路径（支持 `~`；也支持项目级 agent，填项目内的绝对路径）。新增支持的 agent 就加一条
- `skills-manifest.json` —— 分发清单：每个 agent 装哪些技能。**这是分发的唯一来源**。另有两个可选字段：`sources`（技能来源 GitHub 仓库，install 时自动记录）、`presetApplied`（预设集 → 已应用的 agent 列表）。预设成员不再写在 JSON 里——一律以 `presets/` 文件夹实况为准（readdir 现读）；应用仍是互斥接管：预设成员从 agent 个人清单移出、改由预设管，一个技能只属于一处；每个预设是独立分发单元，成员改动随 link/sync 传播到已应用的 agent，取消应用后下次 link 移除其链接，个人清单不回填
- `machines/<hostname>.json` —— 各机器同步状态（sha、时间、断链数）

## 行为约定

1. **改了技能就当场 `git add` + `commit` + `git push origin`**，不要堆积未提交的改动。
2. **不要手工**在各 agent 的 skills 目录（`~/.claude/skills` 等）里创建实体目录或符号链接。分发只通过 `skills-manifest.json` + `link` 完成。
3. 不要把密钥、机器特定路径写进技能。`.secret.key` 已被 gitignore，保持如此。
4. 集合/预设子技能的真身放在 `presets/<预设名>/` 下，经预设应用（TUI 按 p，或把 agent 加进 `presetApplied`）参与分发；不再需要把技能挪到顶层。预设文件夹内可以直接增删子技能目录，成员改动随 link/sync 传播到已应用的 agent。

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

预设集操作在 TUI 里按 `p`：新建预设、把技能移入预设（真身 mv 进 `presets/<预设名>/`，同名技能已在其他预设或顶层重名会拒绝）、删除预设（成员真身移回顶层）。存量数据迁移到 presets/ 布局用 `node manager/src/migrate-preset-folders.ts`（幂等，重复执行报告无操作）。

`myskills` 可从任意目录运行：默认按命令安装位置定位中心仓库，也可用 `MYSKILLS_ROOT` 指定仓库根。`link` 在当前目录或其子目录向上找到 `.myskills.json` 时进入项目模式，把项目清单中的技能链接到项目内 agent 目录；`link --global` 强制按中心仓库的全局清单操作。项目级分发的目标 agent 与 `agents.json` 注册表相同，路径去掉 `~/` 前缀（如 `~/.claude/skills` → 项目内 `.claude/skills`），默认全部开启；`.myskills.json` 写了显式 `targets`（含空数组）则以它为准。目标目录不需要预先存在：`init`、TUI 按 `o` 建立项目级分发或重新开启某个目标、以及 `link` 都会自动创建（如 `.claude/skills`）。项目级分发可先在项目根运行 `myskills init --skills skill-a,skill-b`，再在项目内任意子目录运行 `myskills link`；也可以在项目目录下直接进 TUI——标题与面板常驻标出当前编辑的是用户级（`skills-manifest.json`）还是项目级（`.myskills.json`），项目里还没有清单时按 `o` 会新建（落在 git 根）并切进项目模式，勾选技能与切换目标 agent 都会写入 `.myskills.json`，`l` 走项目 link。

没跑过 `npm link` 的环境用 `node manager/src/cli.ts <子命令>` 等价替代；TUI 对应 `node manager/src/tui.ts`。

测试：`cd manager && npm test`（node:test，fixture 文件系统 + 本地裸仓库 + PATH 注入桩 gh）；类型检查 `npm run check`（tsc --noEmit，tsconfig strict）。git 提交时 pre-commit 自动跑两者（hook 在 `scripts/git-hooks/`，已提交；新机器 clone 后需执行一次 `git config core.hooksPath scripts/git-hooks`）。

## 新机器 bootstrap

```bash
git clone git@github.com:9018447/myskills.git ~/my-skills
cd ~/my-skills/manager && npm link && cd ..
myskills migrate --apply   # 若本机有存量技能目录；否则跳过
myskills sync              # 拉最新、按清单建链接、上报状态
```

安装新技能只在登录了 `gh` 的机器上执行；分发靠 git，其他机器 `sync` 即得。新布局（presets/ 预设文件夹 + 顶层符号链接）对 bootstrap 流程透明：clone 下来的仓库自带 presets/ 与 reconcile，`sync` 的 link 步骤会为已应用预设的成员建链接，无需额外步骤。

<!-- handoff:start -->
## Active handoff

- 交接文档：`/tmp/agent-handoffs/smh--my-skills/handoff.md`
- 恢复被中断的工作时，先读这份交接文档再继续。
<!-- handoff:end -->

## Tool Routing

Use specialized code search tools instead of shell `grep`/`find` or built-in `Grep`/`Glob`.

- File discovery: `rg --files`
- Content search, first stop: `jg` (jevgrep — natural-language question → relevant-file list + declaration locations; auth `jg auth`, health `jg doctor`)
- Second tier: `zg` (fallback local index; `zg --rg` for exact/exhaustive text; missing/stale index → rebuild with `zg index`) · `ast-grep` (structure) · `GitNexus` (call chains, dependencies, impact) · LSP (symbols)
- Last resort: `rg` / `grep` — only for declared exceptions (shell composition, filesystem metadata, scripting) or when the tools above cannot cover the task; state the reason on the spot.

Retrieval order: `jg → zg / ast-grep / GitNexus → rg`. After locating code, `Read` the exact source before concluding or editing. Full policy: `.claude/rules/code-search.md`.

## Division of Labor

Claude Code (the main agent) writes documents, orchestrates tasks, and holds the global picture. Coding: trivial and single-file changes are done by the main agent directly; cross-file implementation always enters through `/poteto-mode` — the dispatch chain and the single-agent vs concurrent choice live inside that skill, and the main agent never codes across files itself. Details: `.claude/rules/coding-principle.md`.

## Verification

For code review, done-work confirmation, and fact-checking, use the jev judgment service (the `jev` skill) instead of reading everything yourself: assemble evidence into `state`, batch independent questions into one request, and judge low-confidence or escalated conclusions yourself. jev's conclusions are decision aids, not authorization boundaries; exact rules and arithmetic go to code. Details: `.claude/rules/verification.md`.

## Work Principles

Universal work principles: subtract before you add, test behavior not implementation, accept only with evidence (prove-it-works), fix root causes not symptoms, after two failures of the same fix re-examine the shared premise, encode lessons in structure not memory. Details: `.claude/rules/work-principles.md`.

Missing skills: the skills referenced in these sections come from https://github.com/9018447/myskills — if one is not installed on this machine, fetch it from there.
