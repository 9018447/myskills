# 链接方式

只将本包放在稳定目录。用户级链接指向这里，移动或删除本包会使链接失效。无需安装完整 YPM 插件副本，也无需再次生成 Playbooks 和 Principles。

链接全部用普通 `ln -s` 命令完成，不再用脚本管理。执行前核实目标 CLI 真实使用的用户级 Skills 目录与指令文件路径。目标已存在时先 `readlink` 检查：已指向本包同源链接视为完成；确认是软链接的旧链接改链替换（`ln -sfn`）；真实文件或指向别处的链接是冲突，报告待裁，不覆盖。

公务员（以常务秘书为例，路径替换为已核实的真实目标；三个公务员角色各自链各自的）：

```bash
for src in /path/to/ypm-init/archives/permanent-secretary/skills/*; do
  [ -f "$src/SKILL.md" ] && ln -s "$src" /verified/secretary/skills/"$(basename "$src")"
done
```

剧本与原则链接给大臣和公务员（2026-10-24 首相裁定，推翻早前"只链大臣"的裁决）：

```bash
for src in /path/to/ypm-init/library/playbooks/* /path/to/ypm-init/library/principles/*; do
  [ -f "$src/SKILL.md" ] && ln -s "$src" /verified/minister/skills/"$(basename "$src")"
done
```

移除时只删除指向本包的软链接，不删外部 Skill 原件、业务文件或其他来源配置。最后仍需用目标 CLI 验证发现与读取；本机没有相应 CLI 时只能报告链接建立、等待验证。
