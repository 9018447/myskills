---
name: aider-tdd-zh
description: 用 aider headless 跑红绿循环。先判断任务类型：新行为走垂直切片（一个测试一次 RED/GREEN）；共享常量/schema/协议迁移走原子切换（RED 一次翻全部测试、GREEN 一次翻全部实现）。GREEN 状态看 aider 日志末尾测试输出，日志不全才自己重跑。
tags: [user]
---

# aider TDD（红→绿，headless 派发）

把 aider 当成一个无状态的写文件工头：它只负责按 prompt 改代码。aider 的 one-shot 调用之间没有对话记忆，靠 git 提交和 SPEC-AIDER.md 在磁盘上续接——这正好满足"每次新派发都是新鲜上下文"。

**先分类，再切片。** 拿到需求后第一件事是判断这个任务属于下面哪一类，选错模式会导致 GREEN 永远过不了（见"任务分类"）。

## 事实（已确认）

- aider 已装在 `~/.local/bin/aider`，默认配置 `~/.aider.conf.yml` 已指向 glm-5.3-flash 网关、开 prompt cache、开 thinking。本技能不再重复指定 `--model`。
- `aider -f <prompt.md> --yes-always` 是无状态一次调用：读 prompt 文件 → 改文件 → 跑 `--auto-test`（若指定）→ git 自动 commit → 退出。
- `--read <file>` 把文件标为只读，进 prompt cache，aider 不会改它。
- SPEC-AIDER.md 用 `--read` 加载，不放进可编辑文件列表。

## 任务分类（先做，这一步决定后面走哪条流程）

用这个判别问题，在派任何 RED 之前回答：

> **如果按 SPEC 列出的顺序逐个实现，实现第 1 条时，第 2..N 条对应的现有测试会不会一起变红？**

- **不会** → 垂直切片模式（greenfield 新行为）。走下面的"流程"。
- **会** → 原子迁移模式（共享常量 / schema / 协议迁移）。走下面的"迁移流程"。

会同时变红的典型信号：一个常量（如 `GRID_SIZE=35`）、一个文件格式（CSV 列数）、一个协议字符串（`protocol=drying/2`）、一个 builder 返回形状，被多个测试和多处生产代码同时引用。改它一处，全塌。这种情况下"一个切片一个测试"是错的——你必须把所有旧测试一次性翻成新形状，再把生产代码一次性翻成新形状，中间没有中间态。

**不要在迁移任务上硬套垂直切片。** 如果已经按切片派了一次 RED，发现 GREEN 永远过不了（旧测试全红），立刻停下来切到迁移模式，把已有的半个切片丢弃或合并进迁移 RED。

## 硬约束（违反即任务错误）

两条模式共用：

- **红和绿必须分两次派发**。RED 派发（`--no-auto-test`）改测试，不跑测试；GREEN 派发（`--auto-test`）改实现，跑到全绿。不能让 aider 一次写完测试又写完实现——那它会直接写对，你看不到红。
- **RED 阶段 aider 不许写生产代码**。prompt 里明确禁止改生产文件；如果 `git show --stat HEAD` 显示动了生产代码，撤销那批 commit，重派。
- **GREEN 阶段 aider 不许改测试断言**。如果 GREEN 日志显示测试文件被改了，停下来看 diff——aider 可能在改测试来"通过"。
- **GREEN 状态看 aider 日志末尾的测试输出，不自己重跑**。日志里必须有 `collected N items` 和全绿 PASSED；日志里没跑测试、输出被截断、或同一个 commit 把测试文件也改了，才自己重跑 `<TEST_CMD>`。
- **测试接缝先与用户确认**。写任何测试之前，写出"测哪个公共接口、测哪几个行为"，用户点头后再派 RED。

垂直切片模式额外加一条：

- **每个切片只有一个测试**。一个 RED 派发只产出一个新测试函数/用例；对应一个 GREEN 派发只产出让它过的最小实现。

原子迁移模式明确豁免上一条：

- **一次 RED 翻完所有受影响测试**，一次 GREEN 翻完所有受影响生产代码。这不是水平切片——测试不是"想象中的行为"，而是把现有测试改成符合新契约的形状；RED 之后全红、GREEN 之后全绿是预期的最终态，中间没有可发布状态。

## 默认（可被具体事实推翻）

- SPEC-AIDER.md 放仓库根目录；prompt 草稿放 `.aider-prompts/<切片名>.md`；日志放 `.agent-results/<切片名>-red.log` 等，先 `mkdir -p`。
- 切片顺序按 SPEC-AIDER 里的行为列表从上到下，一个示踪子弹接一个示踪子弹。
- GREEN 派发加 `--auto-lint`（如果仓库有 linter）。
- 所有派发都在仓库根目录用 `--cwd` 等价方式：`cd <repo> && aider ...`。

## 未知（先调查，不要猜）

- **测试入口是什么**？看 `package.json` 的 `scripts.test`、`pyproject.toml` / `pytest.ini`、`Makefile` 的 `test` 目标、`Cargo.toml` 的 `[dev-dependencies]`。找不到就问用户。
- **linter 入口**？同上，找 `ruff` / `black --check` / `eslint` / `cargo clippy`。没有就不传 `--lint-cmd`。
- **源码和测试文件路径**？如果仓库已有测试目录约定（`tests/`、`__tests__/`、`*.spec.ts`），跟随它；没有就让 aider 在 SPEC-AIDER 里提议位置，你确认。

## 流程（按执行顺序）

### 0. 任务分类

在写任何 prompt 之前，用上面"任务分类"那个判别问题过一遍当前需求。回答是"会同时变红"就跳到"迁移流程"，否则继续下面的垂直切片流程。

### 1. 确认接缝并写 SPEC-AIDER.md

如果用户没给 spec，在仓库根写 `SPEC-AIDER.md`，结构：

```markdown
# <功能名>

## 行为
1. <用户可观察的行为，一条一句话>
2. ...

## 测试接缝
- 公共接口：<模块.函数 或 类.方法>
- 不测试：<私有函数、内部状态、mock 掉的协作者>

## 反模式禁令
- 不 mock 内部协作者
- 期望值来自字面量或手算示例，不用与被测代码相同的方式重算
- 不水平切片（不一次写完所有测试）

## 验收标准
- [ ] 行为 1 有通过测试
- [ ] 行为 2 有通过测试
```

把接缝那一节念给用户确认。SPEC-AIDER.md 本身不进 git 跟踪它也行，但留在磁盘上供每次 `--read`。

### 2. 探测 test-cmd 和 lint-cmd

跑（举例，按仓库实际替换）：

```bash
cat package.json | grep -A2 '"scripts"'
ls pytest.ini pyproject.toml Makefile Cargo.toml 2>/dev/null
```

把结果记下来，作为下一步的 `<TEST_CMD>` 和 `<LINT_CMD>`。**这步是 Unknown，必须做。**

### 3. 选第一个切片

从 SPEC-AIDER 行为列表挑第 1 条，确定：
- 测试文件名（如 `tests/checkout_test.py`）
- 生产文件路径（如 `checkout.py`，GREEN 阶段才用）
- 切片名（如 `checkout-valid-cart`）

### 4. RED 派发

写 `.aider-prompts/<切片名>-red.md`：

```markdown
你在仓库根目录，按 SPEC-AIDER.md 工作。

本切片：行为"<SPEC-AIDER 第 1 条行为原文>"。

只做一件事：在 <测试文件路径> 里写一个失败测试，测这个行为。

硬约束：
- 不要修改任何生产代码文件。
- 只新增一个测试函数，名字描述该行为（中文或英文按仓库惯例）。
- 期望值来自独立字面量或手算示例，不要调用被测代码本身来生成期望值。
- 如果测试文件不存在就创建；如果存在就追加，不要删已有测试。
- 写完后用 git commit，提交信息以 "test(<切片名>): " 开头。

不要运行测试。不要写实现。完成后退出。
```

派发：

```bash
cd <repo> && aider \
  --yes-always \
  --read SPEC-AIDER.md \
  --no-auto-test \
  --no-auto-lint \
  -f .aider-prompts/<切片名>-red.md \
  <测试文件路径> \
  > .agent-results/<切片名>-red.log 2>&1
```

### 5. 看 RED 派发的 diff 和日志，确认红的形式正确

不重跑测试。检查两件事：

1. `git show --stat HEAD` 看这个 commit 是不是只动了测试文件，没碰生产代码。如果动了生产文件，aider 越界了，回滚那个 commit 重派。
2. `cat <测试文件路径>` 看测试本身：期望值是不是字面量、有没有从实现反推、有没有顺手把 SPEC-AIDER 其他行为也测了。测试写错（fixture 缺失、import 路径错）就让 aider 修测试本身，不算 GREEN。

看完直接进第 6 步，不敲 `<TEST_CMD>`。

### 6. GREEN 派发

写 `.aider-prompts/<切片名>-green.md`：

```markdown
你在仓库根目录，按 SPEC-AIDER.md 工作。上一个切片已经写好测试：<测试文件路径> 里那个测"<行为>"的用例，现在它是红的。

只做一件事：在 <生产文件路径>（必要时新建）里写最小实现让这个测试过。

硬约束：
- 只改让这个测试过所必需的代码。不要顺手实现 SPEC-AIDER 里其他行为。
- 不要重构。不要抽新抽象层。不要加 SPEC-AIDER 没要求的配置。
- 不要修改测试断言。
- 完成后 git commit，信息以 "feat(<切片名>): " 开头。
```

派发（带 `--auto-test`，aider 会自己迭代到测试绿）：

```bash
cd <repo> && aider \
  --yes-always \
  --read SPEC-AIDER.md \
  --test-cmd "<TEST_CMD>" \
  --auto-test \
  --lint-cmd "<LINT_CMD>" \
  -f .aider-prompts/<切片名>-green.md \
  <生产文件路径> <测试文件路径> \
  > .agent-results/<切片名>-green.log 2>&1
```

### 7. 读 GREEN 日志，确认绿

不自己重跑。打开 `.agent-results/<切片名>-green.log`，翻到末尾看 pytest 输出：

- `collected N items` 的 N 是不是等于当前测试总数（旧的 + 新的）。
- 所有条目都是 PASSED，没有 failed、error、skipped。
- 如果日志里根本没有 pytest 输出，或者输出被截断，或者同一个 commit 把测试文件也改了——这时候才自己敲 `<TEST_CMD>` 重跑。

通过后进第 8 步循环。

### 8. 循环

回到第 3 步，选下一个行为，重复 RED → 红 → GREEN → 绿。SPEC-AIDER 行为列表每条对应一次循环。

### 9. 重构（可选，最后做一次）

所有切片绿了之后，派一次重构：

```markdown
所有测试已绿。现在只做重构：改善命名、抽重复、拆长函数。

硬约束：
- 行为不变。
- 测试不许改（除非在改测试的可读性，不改断言）。
- 每一步保证 <TEST_CMD> 仍绿。
```

派发同 GREEN 的 flag，但 prompt 换成上面这段。

## 迁移流程（共享常量 / schema / 协议切换）

适用：改一个被多处共享的常量、返回形状、文件格式、协议字符串，会让其他测试一起红的任务。

### M1. 列出受影响范围

先做两件事，把范围写进 SPEC-AIDER.md 的迁移节：

```bash
# 哪些测试引用了这个常量/字段/协议字符串？
grep -rn "DRYING_GRID_SIZE\|35点\|35成员\|protocol=" tests/
# 哪些生产代码引用了它？
grep -rn "DRYING_GRID_SIZE" src/
```

把结果列在 SPEC-AIDER.md 里：

```markdown
## 迁移节
- 旧常量：DRYING_GRID_SIZE = 35
- 新常量：DRYING_GRID_SIZE = 1
- 受影响测试：tests/test_drying_oracle.py（约 10 处断言）、tests/test_drying_cli.py（约 5 处）
- 受影响生产代码：drying_oracle.py、drying_hanna_oracle.py、cli.py
- 目标形状：返回单点 (T=298.15, x_w=0.001)；CSV 单列；protocol=drying/2
```

把这份清单念给用户确认。**范围没确认之前不派 RED。**

### M2. RED 一次翻完所有测试

`.aider-prompts/migrate-red.md`：

```markdown
你在仓库根目录，按 SPEC-AIDER.md 的"迁移节"工作。

本任务是协议迁移：把现有测试从旧形状（35 点网格）翻到新形状（单点）。

只做一件事：把 <测试文件 1>、<测试文件 2> 里所有断言旧形状的测试改成断言新形状。
- 网格大小断言从 35 改成 1
- 对单个点的期望值：T=298.15、x_w=0.001
- CSV 断言从多列改成单列
- protocol 字段从旧值改成 "drying/2"

硬约束：
- 不要修改任何生产代码文件。
- 不要新增或删除测试函数，只改断言和 fixture 的形状。
- 不要"先让一部分测试过"——本任务预期所有这些测试在 RED 之后全部失败，因为实现还没改。
- 期望值用新形状的字面量，不要从实现反推。
- 完成后 git commit，信息以 "test(migrate): " 开头。

不要运行测试。不要写实现。完成后退出。
```

派发：

```bash
cd <repo> && aider \
  --yes-always \
  --read SPEC-AIDER.md \
  --no-auto-test \
  --no-auto-lint \
  -f .aider-prompts/migrate-red.md \
  <测试文件 1> <测试文件 2> \
  > .agent-results/migrate-red.log 2>&1
```

### M3. 读 RED diff 确认没碰生产代码

`git show --stat HEAD`：应该只列出测试文件。如果动了生产文件，回滚重派。

### M4. GREEN 一次翻完所有生产代码

`.aider-prompts/migrate-green.md`：

```markdown
你在仓库根目录，按 SPEC-AIDER.md 的"迁移节"工作。上一步已经把所有测试翻成新形状，现在全部失败，因为生产代码还是旧的。

只做一件事：把 <生产文件 1>、<生产文件 2>、<生产文件 3> 改成匹配新形状。
- 常量 DRYING_GRID_SIZE 改成 1
- builder 返回单点而不是网格
- fitness 聚合从均值改成返回单值
- CSV schema 改成单列
- protocol 字段改成 "drying/2"

硬约束：
- 不要修改测试断言。
- 不要重构、不要抽新抽象层，只做形状迁移所必需的改动。
- 如果某个旧函数在迁移后没人调用了，可以删掉，但不要顺手整理其他无关代码。
- 完成后 git commit，信息以 "feat(migrate): " 开头。
```

派发：

```bash
cd <repo> && aider \
  --yes-always \
  --read SPEC-AIDER.md \
  --test-cmd "<TEST_CMD>" \
  --auto-test \
  --lint-cmd "<LINT_CMD>" \
  -f .aider-prompts/migrate-green.md \
  <生产文件 1> <生产文件 2> <生产文件 3> \
  <测试文件 1> <测试文件 2> \
  > .agent-results/migrate-green.log 2>&1
```

### M5. 读 GREEN 日志确认全绿

同垂直切片第 7 步，但要看 `collected N items` 的 N 是迁移前的测试总数——一个都不能少。如果有 skipped/xfail，是 aider 在躲失败，不是真绿。

## 停止条件

- **连续两次 GREEN 派发后测试仍红**：停下来，把日志尾部和测试输出贴给用户。不要让 aider 无限循环——它会开始改测试断言来"通过"。
- **aider 在 RED 阶段改了生产代码**：回滚，重派。
- **任务分类误判**：按垂直切片派了 1-2 次后发现旧测试跟着一起红（切不动），立刻停下来切到迁移模式，不要硬凑切片。
- **SPEC-AIDER 行为列表与代码现状冲突**（比如行为已经实现了）：停下来问用户，不要硬派。
- **测试命令探测不到**：问用户，不要猜一个 `pytest` / `npm test` 塞进去。

## 完成条件

- SPEC-AIDER.md 里每条验收标准都有一个对应测试，且 `<TEST_CMD>` 全绿。
- 垂直切片：`git log --oneline` 能看到 `test(<切片名>):` 和 `feat(<切片名>):` 成对出现。
- 迁移模式：`git log --oneline` 能看到一次 `test(migrate):` 和一次 `feat(migrate):`，且 `grep -rn <旧常量/旧协议> tests/ src/` 为空。
- `.agent-results/` 里每个切片或迁移的红/绿日志都在，方便事后回看哪一步出了什么幺蛾子。

## 验证方法

第一次用这个技能时，挑一个真实切片跑一遍，观察：
- RED 派发的 commit 是不是只动了测试文件（`git show --stat HEAD`）；
- GREEN 日志末尾是不是真的印了 collected N items 和全绿 PASSED；
- aider 写的测试期望值是不是字面量，不是从实现反推。

如果三个观察里有一个对不上，回来改这个 SKILL.md——不是加更多文字，而是找到对应那条硬约束，把它改成可执行的具体动作。
