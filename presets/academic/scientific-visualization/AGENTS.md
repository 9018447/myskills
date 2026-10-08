---
name: scientific-visualization
description: 辅助创建符合期刊要求的出版级科学图表（matplotlib / seaborn / plotly）。提供样式预设、色彩调色板和导出工具，包含针对 Nature/Science/Cell 等期刊的一键配置与导出支持。
license: MIT
metadata:
  skill-author: K-Dense Inc.
  created: 2026-04-17
---

# scientific-visualization — Skill 指引（完整版）

> 目标：单一文档覆盖从样式配置、配色、绘图实践到导出、校验和 CI 自动化的全部工作流，使任意作者或自动化任务能用仓内脚本生成符合期刊要求的图表。

## 概述

本 Skill 用于生成投稿级别的科学图表，覆盖：
- 可复用的 matplotlib 样式预设（字体、线宽、刻度、颜色循环等）；
- 颜色盲友好调色板与便捷应用函数；
- 期刊特定的尺寸与导出工具，支持 PDF/EPS/TIFF/PNG 等格式；
- 示例脚本与参考文档，帮助保持图表一致性与可重复性。

核心实现文件（可验证）：
- `scripts/style_presets.py` — 样式预设与期刊配置（apply_publication_style, configure_for_journal, set_color_palette）
- `scripts/figure_export.py` — 导出与校验工具（save_publication_figure, save_for_journal, check_figure_size, verify_font_embedding）
- `assets/color_palettes.py` — 颜色盲友好调色板与 apply_palette、get_palette
- `references/` — 各类期刊要求、颜色与示例代码

说明：本文件包含可复制的命令与代码片段；所有陈述均可在上述源码与 `SKILL.md` 中验证。

## 何时使用此 Skill

- 需要为稿件生成符合目标期刊技术规范的图表时；
- 快速应用统一的 publication 风格（字体、大小、线宽、配色）以确保稿件图表一致性；
- 在导出时需要满足特定 DPI/格式要求（例如向 Nature/Science 提交）。

## 快速上手（3 步）

1. 在项目根目录创建并激活虚拟环境，安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # 或直接安装 matplotlib seaborn numpy PyPDF2
```

2. 应用期刊配置并绘图：

```python
from scripts.style_presets import configure_for_journal
configure_for_journal('nature', figure_width='single')
# 绘制图表（matplotlib / seaborn）
```

3. 导出并校验：

```python
from scripts.figure_export import save_for_journal, check_figure_size
# fig 为 matplotlib.figure.Figure
check_figure_size(fig, journal='nature')
save_for_journal(fig, 'figure1', journal='nature', figure_type='line_art')
```

## API 与实现要点（完整参考）

下面列出仓内关键函数、签名、行为和用法示例（直接对应 `scripts/*.py` 与 `assets/color_palettes.py`）。

### style_presets.py

- apply_publication_style(style_name: str = 'default') -> None
  - 应用基础 rcParams（font.size、axes.prop_cycle 等）。

- configure_for_journal(journal: str, figure_width: str = 'single') -> None
  - 根据 journal 配置样式并设置默认 `figure.figsize`（mm→inch）。

- set_color_palette(palette_name: str = 'okabe_ito') -> None
  - 设置 matplotlib 颜色循环（axes.prop_cycle）。

### assets/color_palettes.py

- apply_palette(palette_name: str = 'okabe_ito') -> list
  - 将指定 palette 应用于 matplotlib 并返回颜色列表。

### scripts/figure_export.py

- save_publication_figure(fig, filename, formats=['pdf','png'], dpi=300, **kwargs) -> list[Path]
  - 保存多格式文件，按格式调整 DPI（向量格式使用较低嵌入栅格 DPI）。

- save_for_journal(fig, filename, journal, figure_type='combination') -> list[Path]
  - 使用内置 journal_specs（nature/science/cell/...）选择格式与 DPI 并保存。

- check_figure_size(fig, journal='nature') -> dict
  - 检查尺寸（in/mm），判断是否匹配单/双栏并打印报告。

- verify_font_embedding(pdf_path) -> bool|None
  - 若安装 PyPDF2，则尝试读取 PDF 并返回是否可执行嵌入检查（简化）。

## 关键色盘与样式规范（详尽）

下面的色盘与 rcParams 来自仓内实现（`assets/color_palettes.py` 与 `scripts/style_presets.py`），是生成一致、可访问图表的核心规范。

1) 推荐色盘（拷贝自 `assets/color_palettes.py`）

- Okabe-Ito（推荐，8 色，可用于分类变量）：

  ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000']

- Wong（Nature Methods 推荐，8 色）：

  ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']

- Paul Tol（示例）：

  TOL_BRIGHT = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']

  TOL_MUTED = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']

2) 连续/发散色图建议

- 连续（优先）： 'viridis', 'plasma', 'inferno', 'magma', 'cividis'
- 发散（可访问）： 'PuOr', 'BrBG', 'RdBu'（避免直接使用红/绿组合如 'RdGn'）

3) 使用建议（代码片段）

```python
from assets.color_palettes import OKABE_ITO_LIST, apply_palette
import matplotlib.pyplot as plt

apply_palette('okabe_ito')  # 或 scripts.style_presets.set_color_palette('okabe_ito')
plt.rcParams['image.cmap'] = 'viridis'  # 连续数据
```

4) 样式（rcParams）关键字段与推荐值（来自 `get_base_style()`）

- figure.dpi: 100  (显示)
- figure.facecolor: 'white'
- font.size: 8
- font.family: 'sans-serif'
- font.sans-serif: ['Arial','Helvetica','DejaVu Sans']
- axes.linewidth: 0.5
- axes.labelsize: 9
- axes.titlesize: 9
- xtick.labelsize: 7
- ytick.labelsize: 7
- lines.linewidth: 1.5
- lines.markersize: 4
- legend.fontsize: 7
- savefig.dpi: 300
- savefig.bbox: 'tight'
- image.cmap: 'viridis'

5) 期刊样式调整（示例，来自 `apply_publication_style`）

- Nature / Science 精简版：
  - font.size: 7
  - axes.labelsize: 8
  - xtick/ytick.labelsize: 6
  - legend.fontsize: 6
  - savefig.dpi: 600

6) 可访问性提示

- 始终使用颜色盲友好色盘，并在必要时通过线型/标记提供冗余编码；
- 对热图/连续数据使用感知均匀色图（viridis/plasma/cividis）；
- 在最终尺寸下检查文本可读性（轴标签 ≥6 pt）；
- 在 CI（或本地）使用灰度/模拟器检查对比度。

证据：`assets/color_palettes.py`、`scripts/style_presets.py` 中定义的常量与 `get_base_style()`、`apply_publication_style()` 的实现。

## 完整示例（从样式到导出）

单个脚本即可生成并保存符合期刊要求的图表：

```python
import matplotlib.pyplot as plt
from scripts.style_presets import configure_for_journal, set_color_palette
from scripts.figure_export import save_for_journal, check_figure_size
import numpy as np

configure_for_journal('nature', 'single')
set_color_palette('okabe_ito')

fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.5))
x = np.linspace(0, 10, 100)
for ax in axes.ravel():
    ax.plot(x, np.sin(x) + np.random.normal(scale=0.05, size=x.shape))
    ax.set_xlabel('Time (h)')
    ax.set_ylabel('Signal (AU)')

info = check_figure_size(fig, journal='nature')
print('compliant:', info['compliant'])
save_for_journal(fig, 'figure_multi_panel', journal='nature', figure_type='combination')
```

## 运行脚本与演示

- 演示样式与颜色板（交互/图例演示）：

```bash
python3 scripts/style_presets.py
```

- 导出示例并校验尺寸：

```bash
python3 scripts/figure_export.py
```

## 推荐依赖与 `requirements.txt`（示例）

建议在仓库根添加 `requirements.txt`，便于 CI 与重现。示例内容：

```
matplotlib>=3.5
seaborn>=0.12
numpy>=1.24
pandas>=2.0
PyPDF2>=3.0
pytest>=7.0
plotly>=5.15  # 可选
```

安装：

```bash
python -m pip install -r requirements.txt
```

## 无头 CI（GitHub Actions）示例

将下列片段保存为 `.github/workflows/ci.yaml` 以在 Push/PR 时执行无头导出与 artifact 上传。

```yaml
name: CI — figure export

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run headless export tests
        env:
          MPLBACKEND: Agg
        run: |
          python -c "import matplotlib; matplotlib.use('Agg'); print('matplotlib backend', matplotlib.get_backend())"
          python scripts/figure_export.py
      - name: Upload artifacts (figures)
        uses: actions/upload-artifact@v4
        with:
          name: exported-figures
          path: '**/*.pdf'
```

提示：在 CI 中设置 `MPLBACKEND=Agg` 可避免 GUI 依赖；或在测试脚本最上方调用 `matplotlib.use('Agg')`。

## Minimal pytest 测试示例（文件示例）

把下面内容放入 `tests/test_export.py`：

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.style_presets import apply_publication_style
from scripts.figure_export import save_publication_figure

def test_save_publication_figure(tmp_path):
    apply_publication_style('default')
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot([0, 1], [0, 1])
    out = tmp_path / 'tst_fig'
    files = save_publication_figure(fig, str(out), formats=['pdf','png'], dpi=300)
    assert any(str(f).endswith('.pdf') for f in files)

```

该测试可在 CI 中用于回归检测导出功能。

## 导出与可访问性提交清单（提交前检查）

1. 图像格式：优先向量（PDF/EPS）；照片类使用 TIFF/PNG。
2. 分辨率（DPI）：照片 300 DPI 起步，线稿按期刊常要求 600—1000 DPI。
3. 字体：嵌入字体并（如需）使用 `verify_font_embedding` 检查。
4. 颜色：使用 `assets/color_palettes.py` 的颜色盲友好调色板；为关键对比添加线型/标记冗余编码。
5. 灰度兼容：测试灰度可读性。
6. 字号与可读性：轴标签 ≥6–7 pt（最终尺寸）。
7. 图例：清晰可见并避免重叠。
8. 面板标签：A, B, C…（加粗）并一致化位置。

## 常见问题与注意事项

- 无 `requirements.txt`：不同环境会有差异，建议添加并固定版本以保证可重复性。
- 交互式示例会弹出窗口：在无头环境（CI）需设置 `matplotlib.use('Agg')`。
- `verify_font_embedding` 依赖 PyPDF2，可选，如需严格验证请引入更专业的 PDF 工具链。
- 期刊规范在代码中有硬编码（`save_for_journal`），若期刊更新应同步修改代码或迁移为配置文件。

## 文件与证据索引

实现与示例代码来源（仓内文件）：

- `SKILL.md`
- `scripts/style_presets.py`
- `scripts/figure_export.py`
- `assets/color_palettes.py`
- `references/publication_guidelines.md`
- `references/color_palettes.md`
- `references/matplotlib_examples.md`

## [ASK USER] 可选项（执行建议）

1. 我可以把上述 `requirements.txt` 添加到仓库并提交（推荐）；是否同意？
2. 我可以添加 `tests/test_export.py` 和 `.github/workflows/ci.yaml`（示例 CI）到仓库以立即开启自动验证；是否同意？

---

(End of SKILL_SUMMARY.md)
