---
name: ypm-to-spec
description: 大臣通过 acpx 命常务秘书把当前对话整理成 spec 并发布到项目 issue tracker。用于把首相已确认的需求固化为 spec，产出不含 tickets。
disable-model-invocation: true
---

# YPM · 对话转 Spec

## 任务定位

大臣负责交代目标、忠实转述首相意图、写 Prompt、派发和验收；常务秘书负责独立研究并实际撰写与发布 spec。

本命令把当前对话中首相已确定的需求转成 spec。产出只包含 spec，不含 tickets。遵守 `ypm-dispatch` 的统一派发纪律。

## 派发流程

1. **确认常务秘书**
   - 从 `~/cabinet.yaml` 读取首相任命的常务秘书及其 Agent CLI。
   - 尚未任命时请首相指定；不得自行选择 Agent。

2. **写和派发 Prompt**

   - 按 `ypm-dispatch` 的 acpx 规范派发；大臣不代写领域文档。

   - Prompt 必须明确说明：
     1. 常务秘书首先调用执行侧无前缀的 `to-spec` Skill。
     2. 产出只包含 spec，不含 tickets；直接落盘并发布到项目 issue tracker，无需回询确认。
     3. 在产出的`spec`中链接指向合适的`playbooks`和`principles`, 数量不限。
     4. 常务秘书为执行末端：不得再通过 acpx 或子 Agent 转派。

   🔴反例： 
   - 不得没触发`/ypm-dispatch`就继续 
   - 不得替代常务秘书做决定
   - 不得设定限制和硬性输出标准
   - 不要额外做决定或指定目标


3. **报告首相**

   - 写完即报告首相，不验收，不修改，不检查
  
   🔴反例： 
    - 不得重读其产出
    - 不得认为有错误
    - 不得完成后没有立即报告首相

## 完成标准

- spec 已实际发布到 issue tracker 并拿到链接，或明确报告为什么无法发布。

