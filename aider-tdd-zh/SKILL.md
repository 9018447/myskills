---
name: aider-tdd-zh
description: 用 aider headless 做 SPEC 驱动的单文件编码：先写 SPEC-AIDER.md 并与用户确认，再一次性派发实现目标文件，最后对照 SPEC 验收标准验证。只适用于单个文件的编码工作。
tags: [user]
---

# aider SPEC 驱动（单文件，headless 派发）

把 aider 当成一个无状态的写文件工头：它只负责按 prompt 改代码。aider 的 one-shot 调用之间没有对话记忆，靠 git 提交和 SPEC-AIDER.md 在磁盘上续接——这正好满足"每次新派发都是新鲜上下文"。

本技能走 SPEC 驱动，不是 TDD：没有先写测试的红绿循环，而是先把"要做成什么样"写成可验收的 SPEC，用户确认后一次性派发实现，最后逐条对照验收标准验证。

**适用范围**：只做单个文件的编码工作——新建一个文件，或者修改/重写一个已有文件。任务一旦需要同时动多个生产文件（跨文件重构、共享常量/schema/协议迁移、新接口要改调用方），本技能不适用，直接告诉用户换方式，不要硬套。

## 事实（已确认）

- aider 已装在 `~/.local/bin/aider`，默认配置 `~/.aider.conf.yml` 已指向 glm-5.3-flash 网关、开 prompt cache、开 thinking。本技能不再重复指定 `--model`。
- `aider -f <prompt.md> --yes-always` 是无状态一次调用：读 prompt 文件 → 改文件 → 跑 `--auto-test`（若指定）→ git 自动 commit → 退出。
- `--read <file>` 把文件标为只读，进 prompt cache，aider 不会改它。
- SPEC-AIDER.md 用 `--read` 加载，不放进可编辑文件列表。

## 硬约束（违反即任务错误）

- **SPEC 先确认，后派发**。SPEC-AIDER.md 写好后把"行为"和"验收标准"两节念给用户，用户点头之前不派任何 aider 调用。
- **目标文件唯一**。整个流程只允许 aider 改动这一个生产文件（新建或修改）。每次派发后用 `git show --stat HEAD` 检查：出现任何其他生产文件就是越界，回滚重派。
- **测试文件不计入交付物**。仓库已有测试就复用；需要新测试时最多建一个测试文件，它只是验证手段，不是交付物。
- **实现状态看 aider 日志末尾的测试输出，不自己重跑**。日志里必须有 `collected N items` 和全绿 PASSED；日志里没跑测试、输出被截断，才自己重跑 `<TEST_CMD>`。
- **期望值来自 SPEC，不从实现反推**。SPEC 里的验收值用字面量或手算示例写死，派发后不许反过来照着代码改 SPEC。

## 默认（可被具体事实推翻）

- SPEC-AIDER.md 放仓库根目录；prompt 草稿放 `.aider-prompts/<任务名>.md`；日志放 `.agent-results/<任务名>-impl.log` 等，先 `mkdir -p`。
- 实现派发加 `--auto-lint`（如果仓库有 linter）。
- 所有派发都在仓库根目录：`cd <repo> && aider ...`。

## 未知（先调查，不要猜）

- **目标文件的准确路径**？文件已存在还是新建？新建的话放哪个目录、跟随什么命名惯例？文件已存在就读一遍现状再写 SPEC。
- **测试入口是什么**？看 `package.json` 的 `scripts.test`、`pyproject.toml` / `pytest.ini`、`Makefile` 的 `test` 目标、`Cargo.toml` 的 `[dev-dependencies]`。仓库没有测试设施就不传 `--test-cmd`，验收改为对照 SPEC 逐条人工检查（一次性脚本/REPL/CLI 调用）。
- **linter 入口**？找 `ruff` / `black --check` / `eslint` / `cargo clippy`。没有就不传 `--lint-cmd`。

## 流程（按执行顺序）

### 1. 确认这是单文件任务，锁定目标文件

拿到需求先回答：这个任务的代码改动是否全部落在同一个文件里？是，记下路径；不是，停。文件已存在就读一遍现状（接口、依赖、代码风格），写进 SPEC。

### 2. 写 SPEC-AIDER.md

在仓库根写 `SPEC-AIDER.md`，结构：

```markdown
# <功能名>

## 目标文件
- 路径：<唯一的生产文件路径>
- 现状：新建 / 已有；已有文件的关键接口和依赖

## 行为
1. <用户可观察的行为，一条一句话>
2. ...

## 接口
- 公共接口：<模块.函数 或 类.方法>，签名与返回
- 不变的部分：已有文件中不许改签名/行为的部分

## 反模式禁令
- 期望值来自字面量或手算示例，不用与实现相同的方式重算
- 不顺手实现 SPEC 没列的行为
- 不重构目标文件之外的代码

## 验收标准
- [ ] 行为 1：<可检查的判据>
- [ ] 行为 2：<可检查的判据>
```

把"行为"和"验收标准"两节念给用户确认。SPEC-AIDER.md 可以不进 git，但留在磁盘上供每次 `--read`。

### 3. 探测 test-cmd 和 lint-cmd

跑（举例，按仓库实际替换）：

```bash
cat package.json | grep -A2 '"scripts"'
ls pytest.ini pyproject.toml Makefile Cargo.toml 2>/dev/null
```

把结果记下来，作为 `<TEST_CMD>` 和 `<LINT_CMD>`。**这步是 Unknown，必须做**；仓库没有测试设施就跳过 test-cmd（见"未知"节）。

### 4. 实现派发（一次）

写 `.aider-prompts/<任务名>-impl.md`：

```markdown
你在仓库根目录，按 SPEC-AIDER.md 工作。

只做一件事：把 <目标文件路径>（必要时新建）实现到满足 SPEC-AIDER.md 的全部行为和验收标准。

硬约束：
- 只改 <目标文件路径> 这一个生产文件。
- 已有文件：保持 SPEC 里"不变的部分"，不重构无关代码。
- 不顺手实现 SPEC 没要求的行为，不抽 SPEC 没要求的抽象层。
- 完成后 git commit，提交信息以 "feat(<任务名>): " 开头。
```

派发：

```bash
cd <repo> && aider \
  --yes-always \
  --read SPEC-AIDER.md \
  --test-cmd "<TEST_CMD>" \
  --auto-test \
  --lint-cmd "<LINT_CMD>" \
  -f .aider-prompts/<任务名>-impl.md \
  <目标文件路径> \
  > .agent-results/<任务名>-impl.log 2>&1
```

（没有测试设施就去掉 `--test-cmd` 和 `--auto-test` 两行。）

### 5. 验证：先看日志和 diff，再对照 SPEC

不自己重跑测试，按顺序查三件事：

1. `git show --stat HEAD`：只应有目标文件（和最多一个新测试文件）。出现其他生产文件就是越界，回滚该 commit 重派。
2. 日志末尾测试输出：`collected N items` 且全 PASSED，没有 failed、error、skipped（skipped/xfail 是 aider 在躲失败，不算过）。日志里缺测试输出或被截断，才自己敲 `<TEST_CMD>` 重跑。
3. 逐条勾 SPEC 验收标准。测试没覆盖到的条目，用一次性检查补验（脚本、REPL、CLI 调用都行）。

### 6. 迭代（有差距才走）

对照 SPEC 找出差距，写补丁 prompt `.aider-prompts/<任务名>-fix.md`：只描述差在哪、怎样才算对，附失败输出原文。派发方式同第 4 步，日志名换成 `<任务名>-fix.log`。

**连续两次补丁派发后仍有验收条目不过：停下来**，把日志尾部、diff 和不过的条目贴给用户，不要让 aider 继续猜。

### 7. 收尾

向用户汇报：目标文件路径、commit 列表、每条验收标准怎么过的（贴对应证据）。

## 停止条件

- **两次补丁派发后验收仍不过**：停下贴日志和 diff，不要让 aider 无限循环——它会开始改 SPEC 覆盖不到的地方来"看起来通过"。
- **aider 改了目标文件之外的文件**：回滚该 commit，重派。
- **实现中发现 SPEC 与代码现状冲突**（接口对不上、行为已存在）：停下来问用户，先改 SPEC 再继续，不要让 aider 自行取舍。
- **测试命令探测不到**：问用户，不要猜一个 `pytest` / `npm test` 塞进去；确认没有就按"无测试设施"路径走，交付前明确告诉用户"本任务没有自动化验证，验收是人工检查的"。

## 完成条件

- SPEC-AIDER.md 每条验收标准都有对应的通过证据（测试输出或一次性检查结果）。
- 每个 commit 的 `git show --stat` 只含目标文件（和最多一个测试文件）。
- `.agent-results/` 里每次派发的日志都在，方便事后回看。

## 验证方法

第一次用这个技能时，挑一个真实单文件任务跑一遍，观察：

- 实现派发的 commit 是不是只动了目标文件（`git show --stat HEAD`）；
- 日志末尾是不是真的印了 collected N items 和全绿 PASSED（有测试设施时）；
- SPEC 验收标准是不是逐条有证据，而不是"看起来能用"。

如果观察对不上，回来改这个 SKILL.md——不是加更多文字，而是找到对应那条硬约束，把它改成可执行的具体动作。
