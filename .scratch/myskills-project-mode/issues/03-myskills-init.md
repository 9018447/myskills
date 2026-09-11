# 03 — `myskills init` 项目脚手架

**构建内容：** 在项目目录运行 `myskills init`（可带 `--skills a,b`）生成官方格式的 `.myskills.json`：探测到的 agent 项目级目录写入 `targets`，无探测结果则省略 `targets` 交给自动探测接管；`skills` 缺省为空数组。文件已存在时报错不覆盖。

**被以下阻塞：** 02 — 项目模式 `link`（init 产出的文件格式由 02 定义并消费）。

## 验收标准

- [ ] core.ts：`initProject` 生成 `.myskills.json`，格式与 02 的解析器完全兼容
- [ ] 探测到 agent 目录时写入显式 `targets`；未探测到时省略该键
- [ ] `--skills a,b` 逗号分隔写入并去重排序；已存在文件时报错退出码 1
- [ ] 生成后立即 `myskills link` 可用（端到端）
- [ ] `npm test` 全绿（新增 init 测试）
- [ ] 提交并推送 aliyun

## 被以下阻塞

- 02 — 项目模式 `link`
