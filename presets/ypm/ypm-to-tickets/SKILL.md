---
name: ypm-to-tickets
description: 大臣通过 acpx 命常务秘书把计划、spec 或对话拆成 tracer-bullet tickets；草案先经首相批准，再发布到项目 issue tracker。
disable-model-invocation: true
---

# YPM · 拆分 Tickets

## 任务定位

大臣负责交代目标、忠实转述首相意图、写 Prompt、派发和验收；常务秘书负责独立研究并实际拆分 ticket、设计阻塞关系。

本命令把计划、spec 或对话拆成 tracer-bullet ticket。大臣不分析代码、不拆 ticket、不设计阻塞边、不编写验收标准，也不发布 issue。遵守 `ypm-dispatch` 的统一派发纪律。

## 前置条件

- 项目的 issue tracker 与分类标签词汇应已提供；缺失时提示运行 `/setup-matt-pocock-skills` 并停止。不猜测 tracker、项目或标签。

## 派发流程

1. **确认常务秘书**
   - 从 `~/cabinet.yaml` 读取首相任命的常务秘书及其 Agent CLI。
   - 尚未任命时请首相指定；不得自行选择 Agent。

2. **写和派发 Prompt**
   - 按 `ypm-dispatch` 的 acpx 规范派发；大臣不代写。
  
   - Prompt 必须明确说明：
     1. 常务秘书首先调用执行侧无前缀的 `to-tickets` Skill，把输入拆分为 tracer-bullet issue 并生成阻塞关系。
     2. 拆票草案直接落盘到项目目录，无需回询确认；
     3. 常务秘书为执行末端：不得再通过 acpx 或子 Agent 转派。

   🔴反例： 

   - 不得替代常务秘书做决定
   - 不得设定限制和硬性输出标准
   - 不要额外做决定或指定目标
   - 不得设定步骤/过程和输出目标 
   - 不得没触发`/ypm-dispatch`就继续 


3. **报告首相**

   - 写完即报告首相，不验收，不修改，不检查
  
   🔴反例： 
    - 不得重读其产出
    - 不得认为有错误
    - 不得完成后没有立即报告首相

## 完成标准

- 草案落盘且未经首相批准未发布；批准后已实际发布并拿到 issue 链接，或明确报告为什么无法发布。
