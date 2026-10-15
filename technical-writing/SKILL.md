---
name: technical-writing
description: "分层的技术写作标准：Diátaxis 结构、Google 开发者文档风格的句子、STE 指令规则、Global English 句法。用于 /technical-writing，或撰写与评审文档、RFC、readme、PR 描述、提交信息之时。"
---

# 技术写作

目标是写出疲惫的工程师第一遍就能读懂的文字。四个层次带你到达，每个层次对应一个问题：这是哪类文档、句子如何面对读者、每句话承载多少信息、是否有句子能读出两种意思。四个层次全部应用。

三条规则凌驾于层次之上：

- **删掉每个不起作用的词。** 没有这个词句子照样成立，这个词就删。"In order to" 就是 "to"。"It is important to note that" 什么都不是。
- **用短的日常词。** "Use"，不要 "utilize"。"Help"，不要 "facilitate"。"Do"，不要 "perform"。长词必须用精确性来换取它的长度。
- **当一条规则让句子变差时，换个方式修改句子，或干脆不动它。** 规则服务于读者。一句每条规则都遵守、却读起来像机器写的句子，就是失败的句子。

代码库就是词表。写真实的符号、文件、标志或命令名，不要写同义词或对它的描述。

不要发明行话。用开发者会脱口而出的词："move"、"delete"、"a budget that only decreases"，而不是 "evacuate"、"ratchet" 或 "endgame"。命名模式可以用，只要文档第一次提到它时说明其含义。发现新的违规词及其替代词时，在你回复中以补充 `unslop` 的 abstract-metaphor 规则的形式提出，并附上 diff。不要直接修改那个 skill。

## 变换节奏

层次决定文档说什么、每句话承载多少。一篇文档可以全部达标、读起来却仍像机器写的：每句都短促，通篇没有观点，没有任何具体的东西。

- 有意混合句子长短。短句用来敲定一个要点。不慌不忙的长句带着事实及其条件或后果。
- 每句一个想法不等于每句一种长度。拆开承载两个想法的句子。留下只承载一个想法的长句。
- 在模式允许的地方亮出观点。Explanation 要权衡取舍，那就说出你怎么看，而不是罗列优缺点。Reference 保持干燥。
- 具体胜于空洞。不要写 "schema changes can cause issues"，要写 "a column rename fails the build"。

## 先选模式（Diátaxis）

一篇文档，一种模式。两个问题定模式：内容是指导行动（做）还是促进理解（想），它服务于学习还是工作？

- 行动 + 学习：**tutorial**。
- 行动 + 工作：**how-to**。
- 理解 + 工作：**reference**。
- 理解 + 学习：**explanation**。

这套罗盘既可用于整篇文档，也可用于单个句子。

**Tutorial：在做中学。** 你是老师。学习者的成功是你的责任，不是他们的。开头就说学习者将构建出什么，而不是他们将"学到"什么。每一步都产出一个可见的结果，越早越好、越频繁越好。告诉他们应该看到什么：预期输出、prompt 的变化、那行日志。解释压缩到一个从句加一个链接。教学式的停顿会打断课程。保持具体。以"我们"的口吻、用命令来写："First, do x. Now, do y."

**How-to：通往目标的步骤。** 解决一个人遇到的问题，而不是机器能执行的某个操作。假定读者有能力。跳过教学。只有行动：不岔开话题、不补背景、不为完整而完整。这些内容用链接代替。允许分叉和判断："If you want x, do y." 按任务给指南命名："How to calibrate the radar array"，而不是 "Radar array calibration"。

**Reference：供查阅的事实。** 描述。只描述。没有指令、没有劝说、没有观点。要干燥、完整、笃定。陈述事实、选项、限制和错误，不加任何含糊其辞。结构与所描述之物一一对应，让代码和文档可以对照导航。材料放在读者预期的地方。尽可能从代码生成，这样它才不会失真。

**Explanation：理解与缘由。** 一个有边界的主题，脱离产品也能读。每个标题都应经得起在前面加一个隐含的 "About..."。锚定一个真实的 why 问题。给出背景：设计决策、历史、约束、备选方案。观点只允许出现在这里，别处都不行。

不要混用模式：tutorial 里不放 reference 式的表格，reference 里不放 tutorial 式的手把手，how-to 里不争论。要拆开再用链接连起来。

## 面向读者写句子（Google 开发者文档风格）

- 以 "you" 称呼读者，用现在时。"Will" 只用于确实发生在将来的事。
- 说清谁做什么："the compiler checks"，而不是 "is checked"。只有施动者未知或无关紧要时才用被动。
- 把指令写成命令："Click Submit." 平实地陈述事实。绝不用 "should be done"。
- 条件放在指令前面："To delete the document, click Delete." 读者会跳过不适用的部分。
- 常见情况在前。例外在后。
- 听起来像一位懂行的朋友。不要流行语、不要比喻修辞、指令里不要 "please"，操作步骤里绝不用 "simply"、"easy" 或 "quickly"。如果真简单，读者就不会来了。
- 不要预先宣布（"we will soon support..."），也不要让连续的句子以同一个短语开头。
- 链接文字要说明链接去向：页面标题或简短描述。绝不用 "click here"。宁可页面上多一句背景说明，也好过把读者链去别处。
- 标题要承载论点，而不只是话题（"Pick the mode first"，而不是 "Modes"）。用 sentence case。任务标题是光杆动词短语（"Create an instance"）。概念标题是名词短语。每页一个 h1，不跳级。
- 有先后顺序用编号列表，其余用无序列表。用完整的句子引入列表。各项保持平行结构。
- 代码用代码字体。UI 元素加粗。使用串行逗号。去掉 "etc."，并在开头就说明列表并不完整。

## 让句子一次只承载一条信息（STE 规则）

- 每句一条指令。其他句子每句一个想法。
- 超过约 20 个词的指令、超过约 25 个词的其他句子，都要拆分。
- 警告或条件放在它所保护的那一步之前："If hot oil touches your skin, injuries can occur."
- 保留 "the" 和 "a"："Remove backup file" 能读出两种意思，"Remove the backup file" 只有一种。
- 每个词只给一个含义、一个职责，然后守住它。如果 "check" 表示检查，就不要再用它表示约束。
- 每个动作选一个词并贯彻到底："start"，不要这里 "start"、那里 "initiate"。
- 操作步骤写成直接命令，绝不写成叙述，也绝不用被动语态："Install the component"，而不是 "the component must be installed"。
- 能不用 "-ing" 词就不用。它们承担的语法角色太多，容易滋生误读。

## 不让任何句子存在两种读法（Global English）

- "only"、"not" 这类词要紧挨着它们修饰的词："only fails on growth" 和 "fails only on growth" 说的是两回事。
- 拆开长名词串："the proto import budget check script" 应变成 "the script that checks the proto-import budget"。
- 让每个 "it"、"they"、"this" 都只指向一个明确的东西。拿不准就重复名词。绝不用 "this" 或 "which" 指代整个从句。
- 不要省略动词："Phase 1 moves the converters and Phase 2 the runtime" 让 Phase 2 没了动词。给它补上。
- 保留体现结构的小词。"Ensure that the switch is off" 保留 "that"，因为它让句子只有一种解析方式。绝不用字数换清晰度。
- 当重复冠词能防止误读时，就在并列中重复它：两者是不同东西时写 "the client and the host"，而不是 "the client and host"。
- 当句子可能有两种组合方式时，说明 "and" 或 "or" 连接的是哪些部分。"Both...and"、"either...or" 和 "if...then" 是免费的消歧手段。
- 用句号，不用分号。把破折号换成一个新句子。
- 括号里的内容要么是完整的语法单位，要么独立成句。绝不要用 "(s)" 构成复数。
- 不用斜杠：写 "a, b, or both"，而不是 "a/b" 或 "and/or"。
- 每样东西在任何地方都用同一个名字。一个文档把同一个东西一会儿叫 "the gate"、一会儿叫 "the ratchet"、一会儿叫 "the budget check"，就是在教读者三样东西。多次编辑之间改动一句没有变化的句子的措辞，代价同理。没变的东西不要折腾。
- 避开习语、口语、拉丁语缩写和比喻。非母语读者、翻译者和 agent 解析平实句式的能力都最好。

## 语气与仓库细则

- 本 skill 触及的每篇文档都应用 **unslop** skill。AI 垃圾文风（AI slop）的模式目录归那个 skill 管：AI 词汇、填充词、对冲式措辞、格式化痕迹。
- PR 描述和提交信息也是写作。除 Diátaxis 之外的每个层次都适用于它们。PR 正文是一份审查者一分钟能读完的简报。不要粘贴 swarm 日志、SHA 列表或指标表格。用链接。
- 产品 UI 文案不是文档。那类内容遵循你产品的文案指南。
- 代码片段用 tab 缩进。写真实的路径和真实的符号。让每个计数或目录树声明在落地它的那个 commit 上都成立，并附上能重新生成它的命令。

## 实战示例

改写前：

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

改写后：

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
