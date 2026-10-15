# Databricks 分析与系统表

## 该来源包含什么

Databricks 是产品分析、数据管道与数仓遥测层，与 Datadog 互补。Datadog 是*基础设施/运行时*视角，Databricks 是*产品/数据*视角（用户做了什么、跑过哪些实验、功能使用量如何演变、某个阈值常量从何而来）。

- **产品分析事件。**`your_warehouse.events.analytics_track_event`（原始表）以及 `<your_analytics_db>.<schema>.<table>` 中带类型、去重后的事件级 dbt 模型。用户行为：功能调用、点击、接受/拒绝、提交、客户端上报的错误。
- **用量与计费事件。**`your_warehouse.events.usage_event` / `<your_analytics_db>.<schema>.stg_usage_events`、`your_warehouse.events.raw_model_event` / `<your_analytics_db>.<schema>.stg_raw_model_events`。用于成本或用量驱动的决策。
- **实验 / 功能开关数据。**曝光表与结果表。**Schema 因公司而异。**在假定表名之前，先用 `SHOW TABLES` 探查。
- **系统表。**`system.query.history`、`system.compute.warehouses`、`system.billing.*`、`system.access.audit`。回答“这条查询代价高吗？”“这个查询大家跑得多频繁？”“数仓负载何时飙升？”
- **dbt 血缘。**`<your_analytics_db>.<schema>` 中的模型能揭示哪些管道依赖某个表/字段。上游变更常常是下游消费代码变更的动因。
- **Databricks notebook。**工程师在改代码之前写的探索性分析。**无法通过 SQL MCP 查询。**如果你怀疑缘由写在某个 notebook 里，把它列为缺口。

## 如何搜索

使用 Databricks SQL MCP。主工具：`execute_sql_read_only`。如果它返回了 `statement_id`，用 `poll_sql_result` 轮询，而不要重跑。

**查询前先摸清方向。**Schema 因公司而异。先探查，再信任某个表名：

```sql
SHOW TABLES IN <your_analytics_db>.<schema> LIKE '*<keyword>*';
DESCRIBE TABLE <your_analytics_db>.<schema>.stg_<event>;
```

**每条查询都要限定时间。**这些表非常庞大，无约束的扫描会超时。用框住上线日期的时间窗口过滤 `_timestamp`（事件表）或 `start_time`（`system.query.history`），通常是前后各约 30 天，只有在充分理由时才放宽。

**优先用带类型的 dbt 模型，而不是原始表。**`<your_analytics_db>.<schema>.<table>` 已去重、带类型并采用 liquid clustering；`your_warehouse.events.analytics_track_event` 有重复行和未定型的 `properties_json`。模型命名模式：`stg_<source>_<event_name_with_underscores>`，其中 `<source>` 是 `app`、`backend`、`website` 或 `cli`。单凭模式确定不了确切模型名时，用 `SHOW TABLES` 确认。只有在还没有对应 dbt 模型、或你需要 dbt 刷新滞后窗口内的事件时，才退回原始表。

**带类型的 dbt 模型的列约定**（了解这些可以省一次 `DESCRIBE` 往返）：

- `_timestamp`、`_id`、`_auth_id`、`_request_id`、`event_name`。每个模型都有，是标准列
- `properties_<name>`。带类型、下划线命名的事件属性（`properties_entrypoint`、`properties_size_bytes` 等）
- `context_team_id`、`context_client_version`、`context_country`、`context_client_os`。预先提取好的客户端上下文

### 往往卓有成效的调查模式

挑选与目标匹配的“表 + 列”组合：

1. **事件使用轨迹。**在 PR 合并前后 ±30 天窗口内，统计相关 `stg_*` 模型的每日计数。合并后一两天内从零跃升到稳定量级的阶跃，是“该 PR 上线了这个功能”的有力旁证；衰减到零则暗示弃用或删除。
2. **护栏 / 防御性检查的来源。**取 PR *之前* 14 天内相关 `properties_<name>` 列的分布（中位数 / p99 / max）。如果 p99 恰好与目标的阈值常量吻合，说明这个数字是从数据里选出来的。
3. **实验 / 功能开关查询。**用 `SHOW TABLES ... LIKE '*experiment*'` 找到曝光表，然后按 variant 拉取 PR 日期前后相关 flag key 的曝光计数。
4. **迁移、回填或性能重写的查询历史证据。**用 `statement_text ILIKE '%<table_or_symbol>%'` 过滤 `system.query.history`，配合紧凑的 `start_time` 窗口，就能找出很可能促成这次改动的高开销查询（按 `total_duration_ms` 排序，或聚合 `SUM(read_bytes)`、`COUNT(*)`）。
5. **dbt 血缘。**如果目标读自或写入某个 `<your_analytics_db>.<schema>` 模型，该模型自身的 git 历史（在本仓库内）往往载有缘由。把这条线索交还给 git 调查员，不要自己去追。

## 什么样的证据算好证据

除上述模式形态之外：

- 某个错误分类事件的计数在防御性代码 PR 合并后的几天内跌到接近零。提示该 PR 解决了那一类错误
- 曝光表中的一行写明了目标的功能开关 key，并在 PR 上线日期前后带有“已上线”/“已结束”的决策记录

## 常见陷阱

- **有埋点不等于有因果。**某个事件的存在说明有人在意到愿意记录它，不代表目标代码是*因为*它才存在的。在声称因果之前，先配上 git 调查员给出的 PR/commit 引用。
- **悄无声息的埋点变更。**事件量的阶跃可能意味着开始记录一个新事件，而不是用户行为变了。在把上升曲线读成功能上线信号之前，先检查同一窗口内有没有埋点方面的 PR。
- **Schema 漂移。**事件属性会演化。今天带类型 dbt 模型上的某个列，在目标代码编写时可能还不存在。较老的数据可能只在原始 `properties_json` 里携带该属性。
- **dbt 刷新滞后。**`<your_analytics_db>.<schema>.*` 按计划重建（通常是每小时/每天）。最近几小时的事件，退回 `your_warehouse.events.*` 并按 `_id` 去重。
- **因公司而异的表。**实验、功能开关、计费和用量表各不相同。从一个你从未确认其存在的表里报告结果，是典型的失败模式。先用 `SHOW TABLES` / `DESCRIBE TABLE` 探查。
- **保留期断崖。**如果相关窗口早于表的保留期或 dbt 模型的创建日期，那是一个*缺口*，不是空结果。要明确指出，免得综合者把“没有结果”读成“没有活动”。
- **Notebook 无法查询。**SQL MCP 看不到 Databricks notebook。如果你怀疑缘由写在某个 notebook 里，就返回一个缺口。

## 需要返回什么

对每一条相关发现：
- 类型（产品事件 / 实验曝光 / 用量或计费事件 / 系统表行 / dbt 模型）
- 全限定表名，以及你执行的确切查询
- 查询的时间窗口
- 紧凑的数值摘要（计数、分位数、首次/末次出现时间戳）。**不要倾倒原始行。**
- 与目标上线日期的时间相关性（例如“首行 2024-08-15，PR #49074 于 2024-08-14 合并”）
- 相关性 + 强度：直接 / 旁证 / 弱
