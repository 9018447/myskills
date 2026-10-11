---
name: mattpocock-sync-zh
description: 主动维护 mattpocock/skills 上游更新与本地 -zh 汉化翻译的同步。定期检索上游 github 库更新，展示技能变化并给简单总结，由用户决定吸收哪些 skill。
tags: [user]
---

# Matt Pocock skills 上游同步（-zh 汉化维护）

本技能负责维护 `mattpocock/skills`（GitHub 上游）与本地汉化的 `-zh` 技能之间的同步。中文译文不翻译成英文逐字节比对，而是用**基线**记录"每个上游技能目录内文件的内容哈希（blob sha）"，代表本地已吸收到上游哪个版本。运行后自动输出"上游哪些技能前移了"，由你决定吸收哪几个。

## 两种"同步"不要混淆

- 本技能 = **追踪上游英文内容移动**，用于决定「要不要重译某个 -zh 技能」。入口是 `check-sync.sh`，基线在 `mattpocock-skills-zh/.sync-baseline.json`。
- 镜像目录 `mattpocock-skills-zh/`（翻译过的 README/docs/CHANGELOG 的那棵复制树）本身的更新，靠中心仓库自身的 `git pull` 跟随上游镜像仓库，与本技能无关。本技能只管 `skills/{engineering,productivity,misc}` 下每个技能的 `SKILL.md` / 参考文件。

## 触发

人工调用：`/mattpocock-sync-zh`。

## 标准流程（每步对应 check-sync.sh 的一个子命令）

### 1) 检索 —— `check-sync.sh --check`（默认命令，也可直接跑 `check-sync.sh`）

读基线 → 拉上游 `main` 的文件树 → 逐文件对比，把变化聚合到技能级，打印表格：

```
上游技能           zh             变化文件
implement          已有 implement-zh SKILL.md[变更]
chief-of-staff     未翻译(缺 zh)   SKILL.md[新增]
```

- **无基线**（首次运行 / `--reset` 之后）：把当前上游 `main` 整体设为基线，并打印「上游技能 → 中文 覆盖表」，标出哪些技能本地还没有 `-zh` 翻译。
- 变化类型：`[新增]`（上游新文件/新技能）、`[变更]`（内容改了）、`[移除]`（上游删了）。`skills/deprecated/` 与 `skills/in-progress/`（实验技能，如 chief-of-staff）不进追踪。

### 2) 给用户摘要

根据 `--check` 输出的变化文件清单，**用中文自然段落**给一个简单总结：上游这个技能大概改了什么、是否影响现有译文措辞、建议要不要重译。需要具体内容时，用 `--pull <skill>` 把新旧两份英文正文抓下来，读 diff 后再总结。不要擅自翻译或合并，最终由用户挑。

### 3) 备料 —— `check-sync.sh --pull <skill>`

把该技能的上游**当前**英文稿抓到 `.sync-staging/<skill>/<文件>.new`，把**上次吸收版本**抓到 `...`.old`，供对照。

重译时看 `diff .sync-staging/<skill>/SKILL.md.old .sync-staging/<skill>/SKILL.md.new`，把改动并入对应的 `skills/<skill>-zh/SKILL.md`（顶层平铺目录，改完照仓库约定当场 `git add`+`commit`+`push`）。`.sync-staging/` 已被 gitignore，不提交。

### 4) 吸收 —— `check-sync.sh --accept <skill>`

确认某技能已吸收（译文已同步）。脚本把该技能目录下所有文件的哈希更新为当前上游状态。之后再跑 `--check` 就不报它了。每个技能独立吸收，`--accept` 只影响你名字里的那一个。

### 维护基线

- `check-sync.sh --reset`：删掉基线。下次 `--check` 会以当前上游为全新起点重建（用于基线坏了 / 想整体重新对齐时，慎用）。

## 一次性确认

- `--check` 打印的覆盖表能看清「上游有哪些技能、哪些本地还没翻译」。
- 伪造一个旧的元素后 `--check` 会把它报为前移；`--pull <skill>` 后 `.old`/`.new` 都有内容可 diff；`--accept <skill>` 之后 `--check` 不再报它。

## 依赖与环境

- 依赖 `gh`（已登录）与 `jq`，零新增脚本依赖。
- 仓库远程：`origin` 指向 GitHub（push 同时含 gitee）。改完技能/脚本按 `AGENTS.md` **当场提交并推送**。