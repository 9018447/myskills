# 文档镜像索引

`references/` 是 [docs.typesafe.ai](https://docs.typesafe.ai) 的本地镜像，用来免去每次
联网取文档。抓取于 **2026-11-02**，保留 Mintlify 提供的原始 Markdown（内文链接仍指向
线上地址）。

- 需要**本机网关的实际能力**时，先读 [gateway-magpie.md](gateway-magpie.md) —— 它是测量
  结果，比官方文档更贴近默认路径。
- 需要**语法、限额、模型行为**时，下表是最接近的页面。镜像可能落后于线上；结论要落到
  实时探针测试上，或在改动前刷新本目录。

| 本地文件                         | 来源页面                                                    |
| -------------------------------- | ----------------------------------------------------------- |
| `primitives.md`                  | /primitives.md —— 问题类型总览、一次多问、答案形状          |
| `choice.md`                      | /primitives/choice.md                                       |
| `score.md`                       | /primitives/score.md —— 含复合打分拆分示例                  |
| `noul.md`                        | /primitives/noul.md —— 含 `criteria` 的 `{true,false}` 形状 |
| `box.md`                         | /primitives/box.md —— 官方 API 专用，magpie 不支持          |
| `advanced.md`                    | /primitives/advanced.md —— 结构化指令与判据                 |
| `images.md`                      | /images.md —— `assets`、引用串、danger-zone header          |
| `state.md`                       | /concepts/state.md —— 状态结构与路径引用                    |
| `confidence.md`                  | /confidence.md —— confidence 与 probability 的区别          |
| `models.md`                      | /models.md —— 模型、别名、上下文限额、语言支持              |
| `jaggedness.md`                  | /model-jaggedness/jev-1.13.md —— 已知短板与规避             |
| `how-to-build.md`                | /concepts/how-to-build-with-system-one.md —— 架构           |
| `api-system-one.md`              | /api/system-one.md —— 完整请求与响应字段                    |
| `api-errors.md`                  | /api/errors.md —— 请求限额与 HTTP 状态码                    |
| `pattern-fan-out.md`             | /patterns/fan-out.md —— 投机式扇出                          |
| `pattern-composite-scoring.md`   | /patterns/composite-scoring.md                              |
| `pattern-intent-routing.md`      | /patterns/intent-routing.md                                 |
| `pattern-confidence-routing.md`  | /patterns/confidence-routing.md                             |
| `cookbook-parallel-questions.md` | /cookbooks/parallel_questions.md                            |
| `cookbook-function-calling.md`   | /cookbooks/function_calling.md                              |
| `cookbook-value-extraction.md`   | /cookbooks/pre_parsed_value_extraction_cookbook.md          |
| `cookbook-date-extraction.md`    | /cookbooks/date_extraction_cookbook.md                      |
| `cookbook-autoformat.md`         | /cookbooks/autoformat.md                                    |
| `cookbook-semantic-find.md`      | /cookbooks/semantic_find.md                                 |
| `cookbook-rerank.md`             | /cookbooks/rerank_typesafe.md                               |
| `cookbook-rag-passages.md`       | /cookbooks/classifying_rag_passages.md                      |
| `cookbook-citation-check.md`     | /cookbooks/citation_check.md                                |
| `cookbook-sde-cascade.md`        | /cookbooks/sde_cascade.md                                   |
| `cookbook-feature-discovery.md`  | /cookbooks/autoresearch_feature_discovery.md                |

## 刷新镜像

```bash
cd "$(dirname "$0")"   # 技能目录
R=references
fetch() { curl -sL -m 60 "https://docs.typesafe.ai/$2" -o "$R/$1"; }
fetch primitives.md                primitives.md
fetch choice.md                   primitives/choice.md
fetch score.md                    primitives/score.md
fetch noul.md                     primitives/noul.md
fetch box.md                      primitives/box.md
fetch advanced.md                 primitives/advanced.md
fetch images.md                   images.md
fetch state.md                    concepts/state.md
fetch confidence.md               confidence.md
fetch models.md                   models.md
fetch jaggedness.md               model-jaggedness/jev-1.13.md
fetch how-to-build.md             concepts/how-to-build-with-system-one.md
fetch api-system-one.md           api/system-one.md
fetch api-errors.md               api/errors.md
fetch pattern-fan-out.md          patterns/fan-out.md
fetch pattern-composite-scoring.md patterns/composite-scoring.md
fetch pattern-intent-routing.md   patterns/intent-routing.md
fetch pattern-confidence-routing.md patterns/confidence-routing.md
fetch cookbook-parallel-questions.md cookbooks/parallel_questions.md
fetch cookbook-function-calling.md cookbooks/function_calling.md
fetch cookbook-value-extraction.md cookbooks/pre_parsed_value_extraction_cookbook.md
fetch cookbook-date-extraction.md cookbooks/date_extraction_cookbook.md
fetch cookbook-autoformat.md      cookbooks/autoformat.md
fetch cookbook-semantic-find.md   cookbooks/semantic_find.md
fetch cookbook-rerank.md          cookbooks/rerank_typesafe.md
fetch cookbook-rag-passages.md    cookbooks/classifying_rag_passages.md
fetch cookbook-citation-check.md  cookbooks/citation_check.md
fetch cookbook-sde-cascade.md     cookbooks/sde_cascade.md
fetch cookbook-feature-discovery.md cookbooks/autoresearch_feature_discovery.md
```

新页面从 [文档索引](https://docs.typesafe.ai/llms.txt) 里找：页面路径加 `.md` 后缀即为
Markdown 版。刷新后把本文件的抓取日期一并改掉。
