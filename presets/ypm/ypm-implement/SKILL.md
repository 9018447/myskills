---
name: ypm-implement
description: 大臣通过 acpx 命多名常务次官把 spec 及其 tickets 实现为集成分支上的代码，含合并、全量测试、评审修复与 PR 交付。
disable-model-invocation: true
---

# YPM · 实现 Spec

## 任务定位

本命令把已发布的 spec 及其关联 tickets 实现为集成分支上的代码。ticket 是一张**任务图**而非步骤清单，票间存在阻塞关系，因此始终存在可立即领走的**前沿（frontier）**。与常务次官的通信保持精简，上下文指向 spec、ticket、研究笔记与历史 commit。

## 前置条件

- spec 与关联 tickets 已就绪；issue tracker 已提供。缺失时提示运行 `/setup-matt-pocock-skills` 并停止。
- 从 `~/cabinet.yaml` 读取首相任命的常务次官（可多名）与私人秘书及其 Agent CLI；尚未任命时请首相指定。某公务员的 Agent 无法通过 acpx 使用时报阻塞，请首相重新指定，不改成本地执行。



## 派发流程

1. **随工记录**

   - 触发`/show-me-your-work`
   🔴反例： 
   - 不得没触发`/show-me-your-work`就继续 
  
2. **创建集成分支**
   - 大臣创建集成分支。若 issue tracker 通过 PR 关闭工作、或首相要求 PR，在第一次合并之后开 draft PR（main 之上没有 commit 的分支开不了 PR），并标记为关闭对应的 spec 与 tickets。

  
 3. **派发实现票**
   
   - 触发`/ypm-dispatch`
  
   - 每张票派一名**常务次官**，在独立 worktree、自有分支上后台运行，保证最大并发。另Prompt 还必须写明：
     1. 开工前确认 worktree 基于集成分支，不是则重置到该分支；
     2. 本ticket所属ADR和Spec
     3. 用 `/implement` Skill 构建 ticket；
     4. 用`/no-comments` 清理自己构建的无用注释和废弃代码
   
🔴反例：
     - 直接写`prompts`
     - 规定步骤/目标/验收标准

1. **合并回主分支**
    - 触发`/ypm-dispatch`
     1. 编写**私人秘书**的prompts，让其将**worktree**合并, 另Prompt 必须要求私人秘书实际依次触发:
     - 合并所有PR
     - 如果存在冲突,使用`/fix-merge-conflicts`
     1. 使用`/unslop`写向首相的tickets小结报告
     2. 使用`/technical-witing`写所有必要的`docs`
     3. 使用`/jev-code-review`进行工作验证,如果存在问题,报告给大臣而非修复.
     4. 清理无用测试. 维护票面信息和decision状态
     5. 清理无用文档，检查已有文档的决策冲突，新文档覆盖旧文档，旧文档直接删除冲突或已过时决策。禁止额外标注
   
   🔴反例： 
   - 自己提交PR或合并worktree
   - 这轮结束还有工作内新建立的worktree
  
2. **循环直至票仓清空**
   - 循环范围是第 1→5 步：每当有票完成或阻塞解除（前沿发生变化），就从第 1 步随工记录重新开始新一轮循环，不跳步。
   - 退出条件：issue tracker 中该 spec 关联的 tickets 全部闭环（无任何待办票残留）时停止循环，继续执行第 6 步。
   - 第 6、7 步不参与循环：只在票仓清空后各执行一次。

3. **评审与修复**
   - 全部票闭环后，对集成分支调用 `open-code-review-delegate`，再派一名常务次官一次性修复全部问题；修复后重跑受影响的测试。

4. **交付并报告首相**
   - 存在 draft PR 则转 ready for review；否则按 issue tracker 的方式逐张解决 ticket，报告集成分支位置；清理所有 worktree。
   - 派**私人秘书**撰写交付报告：Prompt 必须要求其在自己的会话中实际触发 `/unslop`，结合过程记录与验收证据撰写，落盘为交付文档并返回路径。
   - 大臣核对交付文档与真实证据后使用`/show-me`呈报首相：文档路径、哪些票闭环、测试结果、遗留问题。


## 完成标准

- 整份 spec 在集成分支上实现完成，每张 ticket 按 issue tracker 关闭工作的方式解决。
- 全量测试与 code review 修复有真实运行证据；大臣不把"已派发"当作"已完成"。
- 所有 worktree 已清理，派发记录完整可追踪。
- 过程记录与交付报告已落盘为文档，向首相报告了路径与真实状态。
