# 来源行动手册

why skill 会为每个可用的证据类别各启动一名调查员，每名调查员只读下面对应其来源的一份行动手册。这些行动手册是常见 MCP 的具体示例。同一类别换用其他 MCP 时，请在它们的基础上适配。

| 类别 | 行动手册 | 所记录的示例 MCP |
|---|---|---|
| 版本控制历史 | [`code-archaeology.md`](./sources/code-archaeology.md) | git、`gh` |
| Issue / 工单跟踪器 | [`linear.md`](./sources/linear.md) | Linear（可适配 Jira、GitHub Issues、Plane、Shortcut） |
| 长文档 | [`notion.md`](./sources/notion.md) | Notion（可适配 Confluence、Google Docs、Coda） |
| 实时团队聊天 | [`slack.md`](./sources/slack.md) | Slack（可适配 Discord、Microsoft Teams、Mattermost） |
| 基础设施可观测性 | [`datadog.md`](./sources/datadog.md) | Datadog（可适配 New Relic、Honeycomb、Grafana、Splunk） |
| 错误 / 异常跟踪 | [`sentry.md`](./sources/sentry.md) | Sentry（可适配 Rollbar、Bugsnag、Airbrake） |
| 产品分析数仓 | [`databricks.md`](./sources/databricks.md) | Databricks SQL（可适配 Snowflake、BigQuery、ClickHouse、dbt） |

横向通用：

- [`incident-postmortem.md`](./sources/incident-postmortem.md)。当目标代码看起来具有防御性（空值检查、重试、超时、限流、功能开关、出口防护、OOM 处理器）时，附加上它。
