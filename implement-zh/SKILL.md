---
name: implement
description: "基于 spec 或一组 tickets 实现工作内容。"
tags: [user]
disable-model-invocation: true
---

根据用户在 spec 或 tickets 中描述的内容实现工作。

尽可能在预先约定的 seam 处使用 /tdd。

定期运行类型检查，定期运行单个测试文件

每完成一个ticket, 提交一次jj或git commit,并使用 /open-code-review 审查这次提交。

最后运行一次完整测试套件。

将你的工作提交到当前分支。
