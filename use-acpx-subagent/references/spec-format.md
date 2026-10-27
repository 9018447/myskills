# 构建规格

source-root 是按固定 commit 导出的源文件目录，payload 是审阅后的指令与技能目录。读取 assets/examples/ecc/spec.json 获得完整实际规格。

| 字段 | 说明 |
| --- | --- |
| name、description、purpose | 名称、触发描述、职责 |
| source.url、source.revision | 仓库 URL、完整 40 位 commit SHA |
| source.files | path、git_blob 数组；必须包含 LICENSE |
| workspace_mode | review 或 edit |
| result_kind | generic 或 ecc-review |
| dependencies | path、reason 数组；指向 payload/skills/*/SKILL.md |
| stages | 固定顺序的 id、prompt 数组；prompt 在 payload/prompts/ |

不得加入 agent、model、provider、adapter。执行器只在 dispatch 时传入。

payload 必须含 AGENTS.md、contracts/result.schema.json、全部阶段 prompts 及关键 skills。只允许 AGENTS.md、prompts/、skills/、contracts/。禁止绝对路径、.. 和符号链接。Git blob 算法为 SHA1("blob " + bytes_length + NUL + file_bytes)，每次构建都校验。

模板变量为 TASK、WORKTREE、RUN_DIR、AGENTS_FILE、SKILL_PATHS、DIFF_FILE、BASE、HEAD、CHECKS_FILE、RESULT_SCHEMA，写成 {{NAME}}。SKILL_PATHS 展开为绝对路径与用途。运行变量在 prepare 时渲染。

JSON Schema 使用明确子集：type、properties、required、additionalProperties、items、enum、minItems、minLength、minimum、maximum；description、title、$schema 只作说明。类型支持 object、array、string、integer、number、boolean、null。不用 $ref、oneOf、pattern 等未实现关键词。

generic 契约至少要求 summary 字符串和 status（complete/blocked）。最终结果只接受直接 JSON，不从 Markdown 猜测抽取。ECC 契约另验置信度、位置和证据，计算计数和 verdict。blocked 保留为 INCOMPLETE，不能成为 APPROVE。

内置多步图在首个 ACP 节点后执行 checks，末节点按真实检查复核。阶段 id 不得为 run_checks 或 finalize。第三个及后续阶段沿用固定顺序；不支持声明循环、分支或自动重试。

checks 由调用方提供，例如 [{"name":"unit","argv":["python3","-m","unittest"],"timeout":120}]。命令以 argv 数组执行，不用 shell，不让模型编造。未指定 checks 时记录 No checks requested，不宣称构建或测试通过。
