---
name: markdown-to-typst
description: 将 Markdown 整理为 Typst 并编译 PDF。用于 .md 转 .typ、中文排版、表格公式图片迁移，以及用 TypeSafe 辅助整理引用块。
---

# Markdown to Typst

用 Pandoc 保留 Markdown 结构，用 Typst 生成 PDF。代码负责转换，TypeSafe 只判断普通引用块的语义，正文文字始终来自输入。

## 转换文档

1. 确认 Markdown 文件、项目根目录和输出位置。脚本默认在输入文件旁生成同名 `.typ` 与 `.pdf`，已有文件需要用户同意后才能用 `--force` 覆盖。
2. 从任意工作目录运行默认转换。`<skill-dir>` 是本文件所在目录。

   ```sh
   python "<skill-dir>/scripts/md2typst.py" INPUT.md
   ```

3. 需要目录或指定字体时添加 `--toc`、`--font FAMILY`。其他参数以 `--help` 为准。
4. 脚本成功后检查交付文件。用 MinerU 解析 PDF 并读取关键内容，再把所有页面渲染为图片并检查字体、公式、表格、图片、分页和裁切。编译成功不能代替页面检查。
5. 交付 `.typ`、`.pdf` 和实际运行的命令。说明未支持的输入特性或尚未完成的检查。

Typst API、字体和编译错误使用 `typst` 技能。不要升级用户的编译器，也不要为模板添加外部包。

## 整理普通引用块

显式的 `[!NOTE]`、`[!TIP]`、`[!IMPORTANT]`、`[!WARNING]`、`[!CAUTION]` 已由代码处理，不需要模型。

只有用户要求语义整理时才使用 `--semantic`。先说明脚本会发送普通引用块原文及邻近标题，取得用户许可，再运行：

```sh
python "<skill-dir>/scripts/md2typst.py" INPUT.md --semantic
```

默认端点是本机 magpie 网关，模型别名是 `decision-models`。脚本保存 `<输出名>.semantic-receipt.json`，其中包含请求、真实模型、概率和代码决策。`unresolved` 保持普通引用。API 失败会终止转换，不能当成否定答案。

TypeSafe 请求形状、网关能力和模型切换使用 `typesafe-ai` 技能。更换模型后用代表性、困难和否定用例重新检查阈值。

## 输入边界

- 支持 Pandoc Markdown、GFM 常用语法、YAML 元数据和 TeX 数学标记。
- 本地图片必须位于项目根目录内。远程图片、任意 HTML 和其他原始格式需要先转换。
- 嵌套引用块需要先展开。
- 输出必须位于项目根目录内。脚本会改写图片相对路径，并在编译时限制为单任务运行。
