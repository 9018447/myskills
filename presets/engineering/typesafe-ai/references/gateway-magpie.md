# magpie 网关能力矩阵（实测）

本文件是**测量结果**，不是 TypeSafe 官方文档。它记录通过本机 `magpie` 网关
（`http://127.0.0.1:3425/v1/systemone`）调用决策模型时，哪些请求形状真的能用。
官方 API（`https://api.typesafe.ai/v1/systemone`）的能力以 `references/` 下的文档镜像
为准。

- 实测日期：2026-11-02
- 复现方式见文末[怎么重跑](#怎么重跑)

## 别名与真实模型

| 请求里的 `model`                             | 结果                                                                                                                 |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `decision-models`                            | 200。响应 `model` 字段回报 **`Kev-4b`** —— 默认路径不是 Jev                                                          |
| `Kev-4b`                                     | 200（同一模型的显式名）                                                                                              |
| `bailian-decision/decision-model-preview`    | 200。响应 `model` 回报 `decision-model-preview`，另带 `request_id` 与 `latency_ms`                                   |
| `jev-latest`、`siliconflow/Kev-4B`、`kev-4b` | 404，报错 `magpie knows no Jev model "…"; name the provider before it, like bailian-decision/decision-model-preview` |

**结论**：`model` 字段只接受 magpie 自己的别名或 `provider/model` 形式；文档里的
`jev-*` 名字在 magpie 上不可用。每次请求都把响应的 `model` 字段记下来，阈值是按模型
版本校准的。

## 问题类型

| `type`   | magpie | 官方 API                                                            |
| -------- | ------ | ------------------------------------------------------------------- |
| `noul`   | ✅      | ✅                                                                   |
| `choice` | ✅      | ✅                                                                   |
| `score`  | ✅      | ✅                                                                   |
| `box`    | ❌ 400  | ✅（需 `TypeSafe-Danger-Zone-Images: true`，官方标注 dreamer-ready） |

`box` 在 magpie 上的失败是确定的，不是拼写问题。上游 `bailian-decision` 透传的报错：

```
<400> InternalError.Algo.InvalidParameter: invalid SystemOne request:
Input tag 'box' found using 'type' does not match any of the expected tags:
'noul', 'choice', 'score': questions.b
```

带上 `TypeSafe-Danger-Zone-Images: true` 也是 400。

## 图片：被接受但被忽略（静默失效）

**这是本矩阵里最需要警惕的一条。** 在 magpie 上，带 `assets` 的请求返回 200，但模型
并不读图：答案完全由文本决定，且不会给出任何警告。

证据（一张 320×240 的图，内容是**红圆 + 蓝方**）：

| state 里放什么                                          | `有红色圆形？` | `有绿色三角形？` | `有蓝色方形？` | `input_tokens` |
| ------------------------------------------------------- | -------------- | ---------------- | -------------- | -------------- |
| 只有图片引用 `a1b2c3d4-scene`                           | 0.210          | 0.175            | 0.249          | 64             |
| 图片引用 + 正确 caption                                 | 0.890          | 0.176            | —              | 89             |
| 图片引用 + **误导** caption（"只有绿色三角形和黄色线"） | 0.007          | **0.982**        | 0.009          | 82             |
| 完全不传 assets（纯文字占位）                           | 0.366          | 0.189            | 0.334          | —              |

只给图片时三个判断都在噪声区（图上真实存在的红圆 0.210、根本不存在的绿三角 0.175，
没有区分度）；caption 一改，答案立刻跟着 caption 走。`input_tokens` 64–89 也说明图片
字节没有进入上下文。中文与英文提问表现一致，两个 `model` 别名一致。

**做法**：magpie 路径上不要用图片做判断。若状态里确实有图片信息，先由其他工具把它转成
文本再进 `state`，并在真值表里注明该判断的来源是转写文本、不是像素。真需要 Box 或图像
判断时，走官方 API 并在请求上带 `TypeSafe-Danger-Zone-Images: true`（见
`references/images.md`、`references/box.md`）。

顺带一句关于配套 Noul 的实测：在不含产品的消息上，裸 Choice 会硬选出 `kettle_20`=0.45
（confidence 只有 0.174）；配套 Noul 给 0.049，`none_of_the_above` 选项给 0.614 —— 两种写法
都能挡住空值，裸 Choice 挡不住。官方"自 Jev 1.14 起配套 Noul 通常更好"的说法在这条路径上
无法验证（跑的是 Kev-4b），两种写法都得用否定用例各自测。

## 请求形状（magpie 实测可接受 / 拒绝）

| 写法                                                 | 结果                                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------------------- |
| `instructions` + `criteria`                          | ✅ 三种类型都接受                                                          |
| `criteria` 为 `{选项名: 描述}` 映射（Choice）        | ✅                                                                         |
| `criteria` 为有序字符串数组（Score）                 | ✅                                                                         |
| `criteria` 为 `{"true": …, "false": …}` 对象（Noul） | ✅                                                                         |
| Noul 省略 `criteria`                                 | ✅（`instructions` 足够时推荐先试）                                        |
| `criteria` 为两元素数组（Noul）                      | ❌ 400                                                                     |
| `criteria` 为 `{等级: 描述}` 对象（Score）           | ❌ 400                                                                     |
| `question` / `options` / `levels` / `true_criterion` | ❌ 400（Choice、Score）；Noul 用 `question` 单字段侥幸可用，属别名，别依赖 |

`state` 侧实测：字符串、嵌套对象、对象数组都可以；用反引号路径引用（`` `message` ``、
`` `catalog` ``）能被正确解析。`state` 传数组形式的 text/image part 也会返回 200，但
如上所述图片不起作用。

## 批处理与延迟

同一 `state`、6 个问题（每组跑 3 次取中位数）：

| 方式                   | 中位耗时 | 3 次观测           | 与批量比                |
| ---------------------- | -------- | ------------------ | ----------------------- |
| 1 次请求带 6 个问题    | 0.20 s   | 0.13 / 0.20 / 0.23 | 基准                    |
| 拆成 2 次请求（3 + 3） | 0.26 s   | 0.26 / 0.26 / 0.26 | 主档位不变，末位漂移    |
| 拆成 6 次单问请求      | 0.84 s   | 0.77 / 0.84 / 0.86 | 同上                    |

说精确点：Choice 的选中项在两种拆分下都逐字一致；Noul 概率与 Score 位置会变到小数第四位
（2 次拆分的最大差 0.0044，6 次拆分最大 0.0009），落在 0.7 / 0.3 阈值同一侧，真值表的
判定不变 —— 但不要把这种一致性当保证，也不要在测试里断言精确概率。一起问更快，答案稳定，
`state` 只计一次 token，与 `references/cookbook-parallel-questions.md` 的结论方向一致。
首轮冷跑的 0.38 s 比 3 次中位数高，说明这个量级上噪声不小；把本表当"拆不拆都行"的依据，
不要当延迟基准。

## 语言

一整套探针都用中文状态与中文问题跑过，Kev-4b 上的分离很干净（是 0.95–0.98，否
0.05–0.18），干扰项测试也说明它是按文本判的。**这只是 Kev-4b 的观测。**
`references/models.md` 对 Jev 的说明是英文最佳、CJK 属"handled but not equally well"，
需在自有内容上自测。换模型别名时重新跑探针，不要沿用旧阈值。

## 怎么重跑

```bash
python3 scripts/probe.py --endpoint http://127.0.0.1:3425/v1/systemone \
  --state state.json --questions questions.json --receipts .probe-receipts
```

`scripts/probe.py` 会在发请求前拦住 magpie 不支持的 `box` 与图片 `assets`，把静默失效
变成显式错误；负载与响应逐条落盘，任何结论都能复现。
