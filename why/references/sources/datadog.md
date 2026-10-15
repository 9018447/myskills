# Datadog 遥测

## 该来源包含什么

Datadog 存有运行时记录——生产环境里实际发生了什么，而不是计划或讨论中的内容。

- **指标。**团队埋点的计数器、gauge、直方图。一个指标的*存在*本身就是证据：有人认为这个数字值得盯着。
- **监控器与告警。**团队认定值得把人吵醒的条件。一条在 `rate_limit_hit > 10/min` 时触发的监控器，是“团队担心过这个阈值”的直接证据。
- **仪表盘。**精心挑选的视图。这些图表告诉你团队认为子系统的哪些方面重要。
- **APM trace 与 span。**请求级别的运行时数据。对“这里为什么慢”“这里为什么有个超时”一类问题有用。
- **日志。**大容量的事件记录。其中常常包含促成防御性代码的错误情形。
- **事故。**带有时间线的正式事故记录，并关联事后复盘。
- **Notebook。**探索性调查。常常包含假设与分析。

Datadog 回答“这段代码写成前后，生产环境的真实情况是什么？”——而这往往能解释代码为什么长成这样。

## 如何搜索

使用 Datadog MCP。先宽后窄。

1. **找出所属服务。**

   ```
   search_datadog_services (filter by name or team)
   search_datadog_service_dependencies (see upstream/downstream)
   ```

2. **先看仪表盘和监控器。它们告诉你团队在乎什么。**

   ```
   search_datadog_dashboards (query: feature name, service name, symbol)
   search_datadog_monitors   (same queries)
   ```

   当某个仪表盘或监控器覆盖了目标时，记下它的查询与盯守的阈值。阈值常常就是“这里为什么钳制在 N？”的答案。

3. **围绕目标的指标。**

   ```
   search_datadog_metrics (by name pattern, e.g., the feature or symbol)
   get_datadog_metric_context (metadata: description, units, tags)
   get_datadog_metric (timeseries; "was there a spike around the PR date?")
   ```

   把某条指标的轨迹与目标的加入/变更日期关联起来，是很有力的支撑证据：“`payment_timeout` 指标在 2023-11-03 飙升，而重试逻辑在 2023-11-06 合并。”

4. **日志。收窄范围，不要倾倒。**

   ```
   search_datadog_logs (raw log patterns near the target, set use_log_patterns=true)
   analyze_datadog_logs (SQL-style aggregations, only when you need counts)
   ```

   用符号、错误字符串或功能名搜索。**强烈建议使用限定时间的查询**（例如改动前后 30 天）。日志量巨大。不加约束的搜索浪费时间，还可能超时。

5. **APM span 与 trace。**

   ```
   aggregate_spans    (stats: "how often does this endpoint fail?")
   search_datadog_spans (inspect individual spans)
   get_datadog_trace  (a specific trace ID)
   ```

   对超时、重试、慢路径和跨服务行为有用。

6. **事故。**

   ```
   search_datadog_incidents (by title, team, date range)
   get_datadog_incident     (full detail for a specific incident)
   ```

   如果目标看起来是防御性的，就搜索它加入前后时段的事故。某起事故的时间线里如果包含“为 X 添加防御性检查”，那就是近乎直接的证据。

## 什么样的证据算好证据

- 监控器的查询和阈值与代码执行的约束相吻合（代码钳制到 100，监控器在请求超过 100/min 时告警）
- 由目标作者创建的仪表盘，其部件与代码所度量或防范的内容一一对应
- 某条指标显示代码合并前一刻生产环境飙升、合并后转为平稳
- 引用了目标代码、相同符号或相同错误字符串的事故记录
- 日志显示出防御性代码所要阻止的特定错误模式，时间戳落在改动之前的窗口内

## 常见陷阱

- **相关不是因果。**PR 前飙升、PR 后回稳只是提示，不是定论。同一窗口内可能还落了其他改动。检查相邻的 PR。
- **对找到的那张图表过度拟合。**Datadog 可视化是人*做*出来的，反映的是制作者的视角。一张名为“retry success rate”的图表，证明的是团队在意重试成功率，而不是某行代码因它而存在。
- **消失的遥测。**指标可能被改名、删除，或保留期很短。如果找不到相关窗口的数据，那是缺口，不是空结果。
- **规模带来的噪声。**用常见字符串搜日志会返回成千上万条匹配。要下狠心按服务、标签和时间收窄。用 `analyze_datadog_logs` 做聚合，而不是倾倒原始日志。
- **有埋点不等于有因果。**一个指标的存在说明有人在意到愿意测量它，不代表代码是*因为*它才加的。与 commit/PR 日期交叉核对。

## 需要返回什么

对每个相关条目：
- 类型（仪表盘 / 监控器 / 指标 / 日志模式 / trace / 事故 / notebook）
- 标题或名称
- 链接或标识（仪表盘 ID、监控器 ID、指标名、事故 ID）
- 负责人/作者与创建/修改日期
- 与问题相关的具体条件、查询或引文（尽量逐字）
- 相关性：它对目标代码暗示了什么，以及这层关联有多强
