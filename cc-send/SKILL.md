---
name: cc-send
description: 通过 cc-connect 向用户的微信发送消息（发送前先给用户过目草稿，可跳过）。用户说"发消息给我/通知我/发到微信"时使用。
---

# 通过 cc-connect 发消息

把消息送达用户微信。通道是 cc-connect（已在 `~/.cc-connect/config.toml` 配好 btxs 项目 + weixin 平台）。配置或安装问题用 `cc-connect-setup` skill，本文只管发送。

## Fact（本机实测，2026-09-21）

- 发送命令：`cc-connect send -m "<文本>" -p btxs`，成功输出 `Message sent successfully.`
- 只能发往**活跃**会话；无活跃会话报 `no active session found`。修复：用户先在微信里发一条消息激活，或用 `-s "<session key>"` 显式指定（key 从 `cc-connect sessions list` 的 Group/Chat 列查，形如 `weixin:dm:<user>@im.wechat`）。
- 长文本/多行/特殊字符用 `cc-connect send --stdin <<'EOF' ... EOF`；附件用 `--image/--file <绝对路径>`。

## Invariant

- **发送前最好先在对话里给用户看草稿并获得同意**，因为发送是外部可见动作。跳过审阅仅当用户本轮明确说过（如"直接发""不用审了"）；一次"直接发"只豁免本轮，不构成默认豁免。
- 发送后以命令输出为准：退出码 0 + `Message sent successfully.` 才算送达；失败如实报告，不得声称已发送。
- 不发送未给用户看过的内容；修改草稿后重新过目。

## 流程

1. **拟稿**：按消息模板写正文。通知类默认模板：

   ```
   [结果] 一句话结论（有数字给数字）
   [依据] 关键事实/数据出处，1-3 条
   [下一步] 需要用户做什么（无则省略此行）
   ```

2. **过目**：把草稿原文贴在对话里，问"发送？"（或 AskUserQuestion：发送 / 修改 / 取消）。用户同意后才进第 3 步。
3. **发送**：`cc-connect send -m "<草稿全文>" -p btxs`。多行用 `--stdin` heredoc，不要用 `-m` 塞换行。
4. **验证**：见 Invariant 输出标准。报 `no active session found` → 让用户微信发条消息后重试，不要静默丢弃。

## 停止条件

- `cc-connect sessions list` 无任何会话且用户不在线激活 → 停止，告知用户消息已备好、待激活后发送。
- 用户取消 → 不发送，保留草稿在对话里。
