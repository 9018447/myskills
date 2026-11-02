---
name: typesafe-ai
license: MIT
description: >
  TypeSafe System One 模型（也叫 Decision Models，如 Jev）的集成工艺。这类模型对文本和
  应用状态回答类型化问题，并给出校准概率；图片与 Box 只在 TypeSafe 官方 API 可用，默认网关
  不支持。在构建、审查或调试调用 TypeSafe 的代码时使用；
  编写其问题或状态时使用；用类型化问题替换 LLM 的 prompt-then-parse 步骤、关键词匹配或脆弱
  启发式时使用；或在头脑风暴应用中哪里适合放"可编程常识"时使用。
---

# 用 TypeSafe 构建

TypeSafe 的 **Jev** 是第一个公开的 **System One 模型**，它对你的应用所提供的状态回答类型化
问题。状态就是你的代码随请求发送的文本和应用数据（官方 API 还能带图片）。Jev 官方 API 有四
类问题：Choice（从选项中选一个）、Noul（某陈述为真的概率）、Score（在你描述的等级上打分）、
Box（在图片中定位某个目标）。每个答案都以带校准概率的类型化数据返回，供你的代码使用。

能力按路径分层，先确认你走的是哪条：**默认的 magpie 网关只支持 Choice / Noul / Score**。
`type: box` 被 400 挡回；图片更阴——带 `assets` 的请求返回 200，但模型根本不读图，答案完全
由文本决定，还不给任何警告。需要图片或 Box 就走官方 `https://api.typesafe.ai/v1/systemone`
并带 `TypeSafe-Danger-Zone-Images: true`。实测矩阵见
[references/gateway-magpie.md](references/gateway-magpie.md)。

本 skill 的其余部分是指导：一些倾向于产出可靠集成的模式。没有一条是绝对的。模型会变，应用
各不相同，边界情况永远存在。当某种情形需要别的做法时，测试替代方案，然后运用你的判断。

## 判断交给 Jev，决策留在代码

最好的集成形态通常是：Jev 负责判断，代码决定如何处理这些判断。把每个决策想象成一张
**真值表**。Jev 提供输入，比如"这位客户听起来沮丧吗？"或"这条消息是关于哪个产品的？"。
代码持有把这些输入映射到动作的逻辑。

如果一个问题让 Jev 直接做决策，比如"这张工单该升级吗？"或"agent 下一步该做什么？"，通常
说明问题问错了层。正确做法是把决策拆成它所依赖的判断，决策本身写在代码里——代码里的逻辑
可见、可测。把真值表写出来的过程本身也常常暴露出业务逻辑的缺口。一组判断没有定义对应的
结果，这是系统的设计问题，最好在代码里解决。

## 文档：先读本地镜像

请求语法、问题类型、限额与模型行为已经镜像在 [references/index.md](references/index.md)
（抓自 docs.typesafe.ai，2026-11-02）。**先读本地文件，不要为这些内容联网**。只有要确认最新
行为、或镜像里没有那一页时才访问线上，然后按 index 里的脚本刷新。

### 请求入口与骨架

所有请求默认走 `magpie` 本机网关而不是 `typesafe.ai`：
`http://127.0.0.1:3425/v1/systemone`，`model` 填 `decision-models`。它是类 Jev 的决策模型，
构建与用法照官方文档；但网关只认它自己的别名和 `provider/model` 形式，文档里的 `jev-latest`
之类名字在这里返回 404。响应里的 `model` 字段才是真正作答的模型，把它记下来——阈值是按模型
版本校准的。本机网关不需要鉴权；官方 API 用 `Authorization: Bearer $TYPESAFE_API_KEY`。

请求骨架照抄可用。字段名写错会被 400 挡回，实测 `question` / `options` / `levels` /
`true_criterion` 都不接受，正确形状只有 `instructions` 加 `criteria`：

```json
{
  "model": "decision-models",
  "state": {"message": "客户写道：机器冒烟了，我要退钱。",
            "catalog": {"blender_x9": "Blender X9 搅拌机"}},
  "questions": {
    "refund_requested": {
      "type": "noul",
      "instructions": "`message` 是否在请求退款？",
      "criteria": {"true": "明确要求退钱", "false": "只是询问退款政策或没有涉及退款"}
    },
    "product": {
      "type": "choice",
      "instructions": "`message` 涉及 `catalog` 中的哪一款？",
      "criteria": {"blender_x9": "目录条目 blender_x9", "none": "没有提到任何一款"}
    },
    "frustration": {
      "type": "score",
      "instructions": "`message` 的作者显得有多不满？",
      "criteria": ["平静中性，只是在陈述情况",
                  "有明显不便，但措辞礼貌",
                  "非常愤怒，使用威胁或强烈措辞"]
    }
  }
}
```

`criteria` 的形状随类型而变：Choice 是 `{选项名: 描述}` 映射，Score 是有序字符串数组，Noul
是 `{"true": …, "false": …}` 对象（可以省略）。答案在 `answers.<问题ID>` 下，各类型的字段：
Noul 给 `noul`，Choice 给 `choice` / `probabilities` / `confidence`，Score 给 `score` /
`legend` / `probabilities` / `confidence`。完整字段表、请求限额与错误码见
[api-system-one.md](references/api-system-one.md) 和 [api-errors.md](references/api-errors.md)。
探针脚本 `scripts/probe.py` 已经把发送、解读、留档和网关护栏做好了。

- 问题类型：[primitives](references/primitives.md) 及各类型自己的页面
  （[choice](references/choice.md)、[score](references/score.md)、[noul](references/noul.md)、
  [box](references/box.md)）、[结构化指令与判据](references/advanced.md)、
  [图片](references/images.md)（仅官方 API）。
- 模型、上下文限额、语言支持与速率限额：[models](references/models.md)。已知的模型
  短板及其规避方法在[锯齿页](references/jaggedness.md)。
- 架构：[如何与 TypeSafe 构建](references/how-to-build.md)、patterns（`references/pattern-*.md`）
  和 cookbooks（`references/cookbook-*.md`）。与你的用例最接近的 cookbook 是新工作流的好起点。
- 本机网关到底能用什么：[gateway-magpie.md](references/gateway-magpie.md)。它是测量结果，
  比官方文档更贴近默认路径。

镜像落后于线上、或你要的页面不在镜像里时，从[文档索引](https://docs.typesafe.ai/llms.txt)
开始：页面路径后追加 `.md` 即为该页的 Markdown 版，相对链接以 `https://docs.typesafe.ai`
为基准解析。取不到线上文档时就用已安装 SDK 的类型或本地镜像，并告知用户你这样做了。与其
猜测依赖版本的细节，不如省略它们。

## 工作流

1. **从决策逻辑出发。** 先想清楚应用要展示、选择、修改或移交什么。勾画出做决策的真值表或
   规则，列出它们需要的输入。需要理解语言或图片的输入适合做成问题（图片先确认路径支持，见
   [请求入口与骨架](#请求入口与骨架)）。算术、日期、精确查找
   和政策通常属于代码。目标是让每个问题都喂给真值表，且每种答案组合都有对应结果，包括
   Noul 落在阈值之间的情况。如果仅靠代码就足以可靠地决策，告诉用户。
2. **所有问题措辞集中一处。** 问题、选项、判据、阈值是集成中最常被审计和修改的部分。把它们
   集中在一个模块里便于维护。[设计状态](#设计状态)与[撰写问题](#撰写问题)描述了行之有效的
   做法。
3. **对实时 API 做探针测试。** 按[用实时 API 测试](#用实时-api-测试)所述发送测试请求。用
   代表性用例、困难用例和否定用例。持续迭代直到应用行为符合预期。`scripts/probe.py` 已经做
   好了发送、解读与留档，并在发送前拦住当前路径不支持的题型与图片。
4. **集成。** 几个习惯在这里有帮助。暴露或记录确切的请求负载，连同响应里的 `model` 字段——
   阈值是按模型版本校准的，别名换了就得重探。API 调用失败时，把失败作为
   错误上报，而不是当作一个答案；例如，不要把失败的调用当成"否"。API key 留在服务端。

如果用户的请求是开放式的，从[Cookbooks](#cookbooks)里给出最契合其目标的几个方向，并推荐
一个。如果请求很具体，直接构建。

## 设计状态

检验任何问题的一个有用标准是**人类测试**：一个聪明人只看这份状态和这个问题，能否凭直觉
快速作答？当问题通不过测试时，修复通常应在状态里，而不是在措辞里。

- **给人会看的东西。** 即每条消息的发送者、完整会话而非截断的最后一行、人名而非裸 ID 或
  @-mention 标记、问题所涉及的那个条目而非整个目录。你的代码已经知道的事实也要写进状态，
  比如"`replies` 里的所有消息都发于退款之后"，而不是让模型重新推导。
- **供给模型可能缺失的事实**，比如内部产品名或代号指代什么。
- **确保状态里每个字段都相关。** 无关细节会扰乱上下文、降低准确率。为某个问题加的字段可能
  带偏另一个问题的答案，模型还可能把空列表读出某种信号。
- **截断要谨慎。** 只在必要时截断长字符串，并检查截掉的部分不包含问题需要的上下文。
- **用具名字段组织结构。** 带描述性 key 的 JSON 对象比序列化的 JSON 字符串效果好。它们还让
  问题能按路径引用各部分。像 `candidates.refund_policy` 这样的稳定命名比数组下标更容易引用。
- **考虑剔除任何人都无法判断的内容**，比如无法辨认的裁剪图或连专家都有争议的区别。模型在
  这些问题上的答案往往是噪声，而代码会把噪声当信号。
- **默认路径上状态只能是文本。** magpie 网关不读图：`assets` 照收、返回 200，答案却全由
  文本决定。图里的信息先用其他工具转写成文字（谁、什么、位置、屏幕上的原话）再进 `state`，
  并在真值表里注明这一判断的来源是转写文本、不是像素。见
  [gateway-magpie.md](references/gateway-magpie.md)。

## 撰写问题

把复杂判断或决策拆成部件，答案在代码里用加权和、布尔逻辑、阈值或其他启发式组合成最终
决策。例如，不要问"这是欺诈吗？"或"这是垃圾信息吗？"，而是问一组构成欺诈或垃圾信息可能性
的原子问题。每个问题最好的形态是：**一个聪明人一眼就能做出的单一判断**。

- **问具体、可观察的事。** 瞄准人能指认的东西："这里有字符串拼接构造的 SQL 查询吗？"优于
  "这里有 SQL 注入风险吗？"。
- **一个问题一个判断；警惕 "or"。** 由 "or" 或 "and" 连接的两个条件通常拆成两个问题更好。
  同理，一组规则通常一条规则一个问题更好。
- **把意图锚定到目标。** 当判断关于某人想要什么时，点明其目标有帮助："用户想复制这些文件
  中的哪一个？"优于"哪个名字是主输入？"。
- **直接点名主体。** "`photo` 里咖啡杯在哪里？"比把 `target` 定义在别处的 "`photo` 里
  `target` 在哪里？"读起来好。只有某个问题需要的上下文（包括图片），通常放在该问题的指令
  （问题文本）或判据（选项描述、等级描述、或是与非的含义）里最合适。多个问题共享的上下文
  可以在状态里放一次，每个问题用反引号引用其精确路径。当你要对多个条目问同一个问题时，
  把每个条目放进各自的问题通常比让模型在共享列表里查 ID 效果更好。
- **每个问题独立作答。** 一个请求里的问题互相看不见，也看不见彼此的答案。任何问题所依赖的
  上下文都属于状态或该问题本身。
- **平实写作。** 问题不是 LLM prompt。开场白、"请考虑 X、Y、Z"清单、输出格式指令都是噪声。
  选项的描述放在判据里，不放在问题里。把问题表述成"是"意味着肯定答案。注意双重否定，以及
  "下一步"这类预设。
- **点名造成混淆的情形。** 如果答案总在两种结果之间混淆，就在判据里用具体情形说明两者的
  界限。例如，对"这是退款请求吗？"注明：关于退款政策的*提问*不是请求。"其他类型消息除外"
  这种模糊排除帮助更小，还可能把注意力引向错误答案。

### 判据

- **空值情形单独问。** Box 总会返回一个位置，Choice 总会选一个选项——即使什么都不匹配。
  在同一次请求里配一个 Noul 问"是否有匹配"（"`photo` 里有咖啡杯吗？"、"`message` 提到了
  我们产品中的任何一个吗？"），代码就能识别什么都不匹配的情况。自 Jev 1.14 起，这种配套
  Noul 通常好于"以上都不是"选项。两种写法都要用否定用例实测：在不含产品的消息上，裸 Choice
  会硬选出 `kettle_20`=0.45（confidence 只有 0.174），而配套 Noul 给 0.049、`none` 选项给
  0.614——两者都能挡住，裸 Choice 挡住不了。
- **选项名会发送给模型；问题 ID 不会。** 描述内容的名字（`refund_request`、
  `shipping_delay`）对模型有帮助。位置性名字（`A`、`left`、`option_1`）给不了模型任何有效
  信息，还可能造成偏置。
- **选项保持互斥且具体。** 选项之间共享的措辞，或与输入共享的措辞，会把概率拉向这些选项。
  覆盖多重含义的选项常值得拆分，因为其概率无法告诉代码到底命中了哪层含义。方向和幅度通常
  拆成两个独立问题更好，免得一个的答案混进另一个。
- **Score 的每个等级描述成一种情境。** 每个等级单独读起来就成立："客户提到了轻微的不便"
  优于"比上一级更生气"。
- **Noul 的 `false` 判据描述成具体情境**，比如"包裹按时送达"，而不是"不迟到"。
- **多个陈述可能同时成立时，一个陈述一个 Noul。** Choice 只选一个选项，一条既是退款请求
  又是投诉的消息会被迫在两者间瓜分概率。独立的 Noul 允许每个各自为真。

## 组合请求

**共享状态的问题打包在一起。** 一个 handy 的启发式：如果两次调用会带着相同状态发送不同
问题，它们大概率可以合成一次调用。问题便宜且并行执行，状态只读取、只付费一次。见
[parallel questions](references/cookbook-parallel-questions.md)；实测在同一 state 上把 6 个
问题拆成 2 次或 6 次请求，Choice 与 Score 的主值完全一致、概率漂移 ≤0.005，而单次批量往返
0.38s 对逐条 0.82s。

**投机式提问**，即在还不知道是否需要答案之前先把问题问了。只在某些情况下才有用的问题，
可以和识别该情况的问题放进同一次请求。一起问"`order` 是退货请求吗？"和"`order.items` 里
哪一件被退回？"，代码只在第一个答案为"是"时读取第二个答案。第二个问题不需要 "if" 从句，
因为条件由代码处理。见[speculative fan-out](references/pattern-fan-out.md)。

第二次请求通常在以下情况才值得：

- 代码需要一个答案才能构造下一份状态、取证或选择下一批选项；
- 某个状态字段对一个问题的答案有可测量的干扰；
- 不同问题集需要分开缓存或版本化。

## 解读答案

### 置信度很少该当闸门

幼稚的实现常用答案的 `confidence` 作为代码是否行动的关卡。Confidence 衡量的是答案概率分布
的集中程度，这与答案正确的可能性不是一回事。想清楚你的用例里概率应该长什么样；基于它们做
另一种计算可能更合适。

### 概率与阈值

- **概率是答案正确的可能性。** Jev 不是概率论计算器。向它要判断，概率或赔率上的数学运算
  在代码里做。Noul 接近 0.5 通常说明状态没能解决问题。
- **最高概率答案是好的默认值**：Choice 的首选选项，或 Score 的位置。
- **0.7 和 0.3 是不错的 Noul 起始阈值**：高于 0.7 读作"是"，低于 0.3 读作"否"，中间波段
  意味着问题未被解决——可以在真值表里给它自己一行。应用有要求时再调整，并警惕把阈值过拟合
  到少量测试用例上。
- **换个模型别名就重跑探针。** `decision-models` 只是网关别名，真实模型看响应的 `model`
  字段。官方文档对 Jev 的说明是英文最佳、CJK "handled but not equally well"
  （[models](references/models.md)），非英文工作负载要在自有内容上自测；
  [gateway-magpie.md](references/gateway-magpie.md) 里存了一份中文实测记录。
- **看 Score 的分布。** Score 的位置可能被拉向中间并掩盖双峰答案，所以代码读取哪个值之前，
  先看各等级的概率。

## 用实时 API 测试

向实时 API 发送测试请求是检验问题与实际数据契合度的好方法。先向用户征求许可。确定实验
预算（TypeSafe 非常便宜，少量花费能走很远），披露将发送什么数据（指出任何个人或隐私数据）。
默认路径是本机 magpie 网关：不产生外部调用费用、也不需要 key，但数据照样离开了进程，征求
许可与披露不能省。换成官方 API 时，说明会使用用户的 `TYPESAFE_API_KEY`。

- 从几个代表性用例开始，加上困难用例，以及答案为"否"或"无匹配"的用例。
- 比较措辞时，把每个变体作为同一请求中的不同问题发送，共享同一状态。
- 逐条阅读答案，不只看聚合指标。
- 为每个用例保留确切的请求负载，任何结果都可复现。
- 每次改动后，用调参时没用过的用例检验。

确保发送测试请求的 agent 有访问 API 端点的网络权限；magpie 是在本机跑的，先用
`ss -ltn | grep 3425` 确认网关在 listening，不在就告诉用户而不是静默降级。

### 答案看起来不对时

按此顺序检查：

1. 实际发送的负载；
2. 状态，对照人类测试；
3. 选项与候选：正确答案在其中吗？
4. 问题的粒度：每个问题能再拆成更小的判断吗？
5. 措辞。

如果问题清晰、状态完整，答案仍是你确信错误的，查阅所用模型的锯齿页。它列出了已知短板及
规避方法。如果行为未被收录，TypeSafe 团队欢迎通过该页面链接的渠道提交示例。同时，与用户
一起想出一个避开该短板的替代方案。

### 黄旗信号

通常，好的改动是让定义更清晰或改进状态。每个改动都要用非调参用例检验。为产出特定数值而
雕琢的措辞是 **prompt gymnastics**（措辞体操），它在新输入和下一个模型版本上往往会崩。一些
黄旗：

- 判据里点名了具体测试条目，或每个失败用例就多一个从句；
- 用注意事项来解释模型的怪癖；
- 阈值拟合到特定用例；
- 测试断言精确概率；
- 代码悄悄覆盖答案。

结构性的修复通常是更好的状态、独立的问题，或代码。

## Cookbooks

以下每个起点都围绕一个目标组合问题。清单之外的想法同样欢迎。

- **路由并填参数。** 一次请求识别用户在问什么、各参数的值是什么，代码随后调用对应处理函数。
  见[function calling](references/cookbook-function-calling.md)和
  [intent routing](references/pattern-intent-routing.md)。
- **选择而非生成。** 代码找出候选值或文本片段，模型挑出意图所指，代码复制或规范化它。见
  [value extraction](references/cookbook-value-extraction.md)、
  [date extraction](references/cookbook-date-extraction.md)和
  [structure recovery](references/cookbook-autoformat.md)。
- **取证并判断。** 检索候选并逐一问相关度。见
  [line-by-line search](references/cookbook-semantic-find.md)、
  [re-ranking](references/cookbook-rerank.md)和
  [classifying RAG passages](references/cookbook-rag-passages.md)。
- **把答案变成数据。** 每个维度打分一次，之后让代码或用户改权重与视图。如果你有标注结果，
  答案可以成为模型的特征。见
  [composite scoring](references/pattern-composite-scoring.md)和
  [feature discovery](references/cookbook-feature-discovery.md)。
- **验证并升级。** 对照证据核查声明或字段，把不通过的用例转给人工或推理模型。见
  [citation checks](references/cookbook-citation-check.md)和
  [extraction cascades](references/cookbook-sde-cascade.md)。

TypeSafe 团队持续在实时文档中加入经过充分检验的 cookbook 模式。镜像里的 cookbook 不够用时，
查一查[线上 cookbooks 索引](https://docs.typesafe.ai/go/cookbooks.md)有没有契合你正在解决的
问题的那一个，顺手把它补进 `references/`。
