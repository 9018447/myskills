---
name: explore-repo
description: 对仓库做可信验收的只读探索：陌生仓库定位实现、梳理调用链与架构、变更前影响面调研、交接上手。Codex 产出带证据索引的报告，可信脚本核验每条引用真实存在、写入不越界。适用于要交付可复现报告的调研任务；无报告产物的随问随答不适用。
---

# explore-repo：证据可核验的仓库探索工作流

在**目标仓库根目录**操作。任务契约固定为 `.agent/luna/task.json`，产物固定在 `.agent/luna/explore/<task_id>/`。工作流 YAML 与可信驱动位于本技能目录（`workflow.yml`、`scripts/driver.py`）。

## 1. 写任务契约

按下列 schema 写 `.agent/luna/task.json`（相对路径按仓库根解析）：

```json
{
  "task_id": "explore-auth-001",
  "objective": "梳理认证子系统的入口与调用链",
  "focus_paths": ["src/auth/"],
  "exclude_paths": ["node_modules/", "dist/"],
  "allowed_write_paths": [],
  "constraints": ["只读探索", "不得访问网络"],
  "max_attempts": 2,
  "timeout_seconds": 1800
}
```

`task_id` 仅限字母数字与 `._-`；`allowed_write_paths` 可留空，产物目录会自动加入白名单。完成标准：第 2 步 preflight 通过。

## 2. 运行

```bash
specify workflow run /home/smh/myskills/explore-repo/workflow.yml --json
```

完成标准：stdout 拿到单个 JSON 对象，`status` 为 `completed`。步骤失败时对象带 `error` 字段。

## 3. 失败恢复

```bash
specify workflow status <run_id> --json
specify workflow resume <run_id> --json
```

仅 `paused`/`failed` 可恢复；恢复前先读 `.specify/workflows/runs/<run_id>/log.jsonl` 定位失败步骤并检查副作用。

## 4. 判读结果

读 `.agent/luna/explore/<task_id>/verify.json` 的 `verdict`：

- `pass` —— 报告存在、三个必需章节齐全、每条引用路径真实存在、写入全部落在白名单内
- `repairable` —— 存在可修复失败（如引用路径不存在），工作流已自动重试一次；`failures` 数组列出明细
- `fatal` —— 写入越界或结构性失败，升级人工处理

`report.md` 是交付物，`evidence.json` 是引用索引，`explore.log` 是 Codex 原始输出（关联 `run_id` 留档）。

## 5. 汇报字段

`task_id`、`run_id`、`verdict`、报告绝对路径、尝试次数、实际模型（`gpt-6-luna`）。

## 参考资料

- 裁决语义：`verify` 恒以 0 退出，`verify.json` 是唯一裁决来源；`assert-passed` 步骤强制终态为 `pass`，绕过即失败。
- 修复上限：`max_attempts`（默认 2）次探索后仍 `repairable` 按失败终止。
- 引擎状态在当前工作目录 `.specify/workflows/runs/<run_id>/`，与业务产物分开放。
