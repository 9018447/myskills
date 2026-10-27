# 生成约定

输出可安装的专用 skill；每次运行另建 worktree 与 control 目录。不要把一次运行的路径和状态烘焙进可复用 skill。

生成目录包含 SKILL.md、dispatch.json、package.json、AGENTS.md、prompts/、skills/<key-skill>/SKILL.md、contracts/result.schema.json、scripts/run.py、references/source-lock.json、references/upstream/<source-path>。多阶段增加 workflows/task.flow.ts。技能内部 references/scripts/assets 按依赖闭包保存。

运行目录为 <runs>/<run-id>/，其中 state.json 记录状态，AGENTS.md 是精简运行契约，workspace/ 是独立分支上的 worktree。control/ 保存 task.md、prompts/、skills/、upstream/、contracts/、manifest.json、changes.diff、requested-checks.json、checks.json、flow-input.json、dispatch.stdout、dispatch.stderr、raw-result.json、result.json 和 report.md。最后几项仅在相应阶段产生。

AGENTS.md 用标准大写文件名。prompt 显式要求读取，并内联契约，不假定执行器支持自动加载。项目原有规则保留在 worktree；生成指令不得宣称覆盖更高优先级规则。

关键技能始终给出绝对路径及用途。复制到 control 后不依赖 plugin 缓存和网络。技能相对引用必须仍然成立；保留 LICENSE。提取后的方法作为工作指令，原始 agent/command 快照只作溯源。

来源 agent 与执行器分开。persona、步骤和验收可提取；原生工具声明不能跨 ACP 变成权限清单。调用方管理执行器，运行器只接收 agent 名称或 ACP command。

未执行、被拒绝、超时、解析失败必须显式报告。JSON 合法仅证明结构校验，不证明语义正确。内置模板处理本地已提交范围，不自动取 PR、发评论、安装依赖、运行来源 hooks 或合并结果。

## 生成包的运维事实

修改生成包内任一文件后，重算其 sha256 并更新 `references/source-lock.json` 对应条目，再派发：`scripts/run.py` 在 prepare 和 dispatch 都做完整性校验，散列失配报 "Package integrity failed"。run 进入 failed 状态后不接受重派（"Only a prepared run can be dispatched; no implicit replay"），须换新 run-id 重新 prepare 再 dispatch。派发包装命令带 `set -o pipefail`：裸管道接 `tail` 会吃掉非零退出码，后台通知会把失败的 run 显示成 exit 0。

worktree 共用 Git 对象库和 refs，不提供进程隔离。review 模式比较内容、模式、符号链接目标及 HEAD。忽略文件不在比对范围，允许检查产生缓存；更强隔离由调用方提供。目标仓库含 submodule 时当前明确拒绝，不隐式初始化。
