#!/usr/bin/env python3
"""
Visualization Module for Hydrogen Bond Analysis
================================================

科学出版级图表，特点：
- 低饱和度 muted 配色（避免纯色）
- 密度图使用 "cividis" colormap（感知均匀，灰度友好）
- ACF 衰减曲线带半透明置信填充区
- 统一 rcParams：Arial 字体、细边框、柔和网格
"""

import os
from string import ascii_uppercase

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from .config import DEFAULT_DPI, DEFAULT_OUTPUT_DIR

# ---------------------------------------------------------------------------
# Okabe-Ito 色盲友好色盘 (推荐用于科学出版)
# ---------------------------------------------------------------------------
OKABE_ITO_COLORS = [
    "#E69F00",  # 橙色
    "#56B4E9",  # 天蓝
    "#009E73",  # 蓝绿
    "#F0E442",  # 黄色
    "#0072B2",  # 蓝色
    "#D55E00",  # 朱红
    "#CC79A7",  # 藕荷
    "#000000",  # 黑色
]

from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------------------
# 自定义色盘：晨曦岩火 (Slate & Ember) - 数据驱动型学术配色
# ---------------------------------------------------------------------------
def _make_starry_cmap():
    """
    针对 0-600 密度区间优化的三色渐变。
    #999999 (中灰/背景) -> #ffffff (白色/过渡) -> #ef8a62 (橙色/峰值)。
    特点：
    - 针对数据分布优化：99% 的密度数据在 600 以内，该色盘在此区间提供极大的对比度。
    - 视觉清晰度：通过中间的白色层，强制拉开了背景(灰)与峰值(橙)的视觉距离。
    - 专业美感：去除了发霉感，色彩明快且逻辑清晰，符合顶级化学期刊的审美。
    """
    colors = [
        "#999999",   # 中灰 (Stable background for low density)
        "#ffffff",   # 纯白 (High-contrast transition at mid density)
        "#ef8a62",   # 珊瑚橙 (Vibrant peak for high density)
    ]
    return LinearSegmentedColormap.from_list("slate_and_ember", colors, N=256)

_STAR_MAP = _make_starry_cmap()

# ---------------------------------------------------------------------------
# 全局 rcParams：核心科学出版风格 (Nature/Science)
# ---------------------------------------------------------------------------
# 特点：内向刻度、全框 (Box Frame)、Arial 字体、细线宽
_RC = {
    "font.family":         "sans-serif",
    "font.sans-serif":     ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size":           8,
    "axes.labelsize":      9,
    "axes.titlesize":      9,
    "axes.linewidth":      0.5,
    "axes.spines.top":     True,    # 开启全框
    "axes.spines.right":   True,
    "axes.grid":           False,   # 默认关闭网格，仅在需要时开启
    "axes.axisbelow":      True,
    "xtick.major.size":    3.0,
    "xtick.minor.size":    2.0,
    "xtick.major.width":   0.5,
    "xtick.minor.width":   0.5,
    "xtick.direction":     "in",    # 刻度向内
    "xtick.top":           True,    # 顶部显示刻度
    "xtick.minor.visible": True,
    "ytick.major.size":    3.0,
    "ytick.minor.size":    2.0,
    "ytick.major.width":   0.5,
    "ytick.minor.width":   0.5,
    "ytick.direction":     "in",    # 刻度向内
    "ytick.right":         True,    # 右侧显示刻度
    "ytick.minor.visible": True,
    "legend.fontsize":     7,
    "legend.frameon":      False,   # 无边框图例
    "figure.dpi":          150,
    "savefig.dpi":         600,     # 高分辨率输出
    "savefig.bbox":        "tight",
    "savefig.pad_inches":  0.05,
    "lines.linewidth":     1.2,
}


def _apply_rc():
    """应用出版级 rcParams。"""
    mpl.rcParams.update(_RC)


def _restore_rc():
    """恢复默认。"""
    mpl.rcdefaults()


def _add_panel_label(ax, i, x=-0.12, y=1.08):
    """为子图添加 bold 面板标签 (A, B, C...)。"""
    ax.text(x, y, ascii_uppercase[i], transform=ax.transAxes,
            fontsize=11, fontweight="bold", va="top", ha="right")


def _save_multi_format(fig, base_path, dpi=600):
    """同时保存 PNG 和 PDF 格式。"""
    for fmt in ["png", "pdf"]:
        out = f"{base_path}.{fmt}"
        fig.savefig(out, dpi=dpi)
        print(f"  Saved: {out}")


# ---------------------------------------------------------------------------
# 主绘图函数
# ---------------------------------------------------------------------------

def plot_2d_density_maps(analyzer, output_dir=None):
    """
    绘制各分子对在 XY 平面的氢键数密度热图 (Nature 风格多面板)。

    特点：
    - Perceptually uniform "cividis" colormap
    - 全框 (Box Frame) + 内向刻度
    - 面板标签 A, B, C...
    - 统一的 Colorbar 范围
    """
    if output_dir is None:
        output_dir = getattr(analyzer.config, "output_dir", DEFAULT_OUTPUT_DIR)
    dpi = getattr(analyzer.config, "dpi", DEFAULT_DPI)
    os.makedirs(output_dir, exist_ok=True)

    if not hasattr(analyzer, "density_maps") or not analyzer.density_maps:
        return

    active = {k: v for k, v in analyzer.density_maps.items() if v["count"] > 0}
    if not active:
        return

    _apply_rc()
    try:
        n = len(active)
        ncols = min(n, 3)
        nrows = (n + ncols - 1) // ncols

        fig, axes = plt.subplots(
            nrows, ncols,
            figsize=(3.0 * ncols, 2.8 * nrows),
            squeeze=False,
        )

        vmax = max(v["density"].max() for v in active.values())
        vmin = 0.0

        for idx, (itype, data) in enumerate(active.items()):
            row, col = divmod(idx, ncols)
            ax = axes[row][col]

            density = data["density"]
            x_edges = data["x_edges"]
            y_edges = data["y_edges"]

            im = ax.imshow(
                density,
                extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
                origin="lower",
                cmap=_STAR_MAP,
                aspect="equal",
                vmin=vmin,
                vmax=vmax,
                interpolation="gaussian",
            )

            # 面板标签
            _add_panel_label(ax, idx)

            # 标注 HB 相互作用
            ax.set_title(f"{itype}\n(N = {data['count']:,})", fontsize=8, pad=3)
            ax.set_xlabel("X (Å)", fontsize=8)
            ax.set_ylabel("Y (Å)", fontsize=8)
            ax.tick_params(labelsize=7)

        # 统一添加右侧 Colorbar (如果空间允许，或在最右侧子图添加)
        fig.subplots_adjust(right=0.88)
        cbar_ax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        cb = fig.colorbar(im, cax=cbar_ax)
        cb.set_label("HB density (Å⁻²)", fontsize=8)
        cb.ax.tick_params(labelsize=7)
        cb.outline.set_linewidth(0.5)

        # 隐藏空子图
        for idx in range(n, nrows * ncols):
            axes[divmod(idx, ncols)].set_visible(False)

        plt.tight_layout(rect=[0, 0, 0.9, 0.95])
        fig.suptitle(f"{analyzer.config.system_name} - HB 2D Density Maps",
                     fontsize=9, fontweight="bold", y=0.98)

        base_path = os.path.join(output_dir, "hb_2d_density_maps")
        _save_multi_format(fig, base_path, dpi=dpi)
        plt.close()
    finally:
        _restore_rc()


def plot_lifetime_autocorr(analyzer, output_dir=None):
    """
    绘制氢键生命周期自相关函数 C(τ) 衰减曲线 (出版级单面板)。

    特点：
    - Okabe-Ito 色盲友好色盘
    - 全框 (Box Frame) + 内向刻度
    - 带有 C(τ)=1/e 参考虚线
    - 线下半透明填充
    """
    if output_dir is None:
        output_dir = getattr(analyzer.config, "output_dir", DEFAULT_OUTPUT_DIR)
    dpi = getattr(analyzer.config, "dpi", DEFAULT_DPI)
    os.makedirs(output_dir, exist_ok=True)

    if not hasattr(analyzer, "lifetime_data") or not analyzer.lifetime_data:
        return

    _apply_rc()
    try:
        # Nature 单栏建议宽度 ~3.5 inch
        fig, ax = plt.subplots(figsize=(3.5, 2.8))

        for i, (itype, data) in enumerate(analyzer.lifetime_data.items()):
            tau = data["tau"]
            acf = data["acf"]
            color = OKABE_ITO_COLORS[i % len(OKABE_ITO_COLORS)]

            idx_e = np.where(acf <= 1 / np.e)[0]
            tau_e = tau[idx_e[0]] if len(idx_e) > 0 else tau[-1]

            label = f"{itype} (τ={tau_e:.0f} ps)"
            ax.plot(tau, acf, color=color, linewidth=1.2, label=label)
            ax.fill_between(tau, 0, acf, color=color, alpha=0.05)

        # 1/e 参考线
        ax.axhline(1 / np.e, color="#666666", linewidth=0.6, linestyle="--", alpha=0.8)
        ax.text(ax.get_xlim()[1]*0.98, 1/np.e + 0.02, "1/e",
                fontsize=7, color="#666666", ha="right")

        ax.set_xlabel("Correlation time τ (ps)", fontsize=9)
        ax.set_ylabel("Autocorrelation function C(τ)", fontsize=9)
        ax.set_ylim(-0.02, 1.05)
        ax.set_xlim(left=0)

        # 设置图例
        ax.legend(fontsize=7, loc="upper right")

        # 添加面板标签 (假设这是第二个主图)
        # _add_panel_label(ax, 0)

        plt.tight_layout()
        base_path = os.path.join(output_dir, "hb_lifetime_autocorr")
        _save_multi_format(fig, base_path, dpi=dpi)
        plt.close()
    finally:
        _restore_rc()


def visualize_results(analyzer, output_dir=None):
    """统一绘图入口。"""
    if output_dir is None:
        output_dir = getattr(analyzer.config, "output_dir", DEFAULT_OUTPUT_DIR)
    print(f"\nCreating publication-quality visualizations in {output_dir}...")
    plot_2d_density_maps(analyzer, output_dir)
    plot_lifetime_autocorr(analyzer, output_dir)
    print(f"Visualizations (PNG + PDF) saved to {output_dir}/")
