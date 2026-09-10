#!/usr/bin/env python3
"""
Analyzers Module for Hydrogen Bond Analysis
============================================

create_2d_density_map : XY 平面氢键数密度映射（单位 Å⁻²）
通过 analyzer.config 自动适配任意分子体系。
"""

import numpy as np

from .config import DEFAULT_N_BINS


def create_2d_density_map(analyzer, n_bins=None):
    """
    从 hba.results.hbonds 构建各分子对的 XY 平面氢键数密度矩阵。

    分类标签和 interaction_types 来自 analyzer.config，无硬编码。

    Parameters
    ----------
    analyzer : HBAnalyzer
    n_bins : int, optional  格点数，默认 DEFAULT_N_BINS

    Returns
    -------
    dict  {itype: {"density": ndarray, "x_edges": ndarray,
                   "y_edges": ndarray, "count": int}}
    """
    if n_bins is None:
        n_bins = analyzer.config.n_bins if hasattr(analyzer.config, "n_bins") else DEFAULT_N_BINS

    print("\nCreating 2D hydrogen bond density maps...")

    if not hasattr(analyzer, "hbonds_data") or len(analyzer.hbonds_data) == 0:
        print("  No hydrogen bond data available.")
        analyzer.density_maps = {}
        return {}

    cfg = analyzer.config

    # 读取末帧盒子尺寸
    analyzer.u.trajectory[-1]
    box = analyzer.u.dimensions
    Lx, Ly = float(box[0]), float(box[1])

    x_edges  = np.linspace(0, Lx, n_bins + 1)
    y_edges  = np.linspace(0, Ly, n_bins + 1)
    bin_area = (Lx / n_bins) * (Ly / n_bins)

    # 初始化计数矩阵
    count_maps = {itype: np.zeros((n_bins, n_bins), dtype=np.float64)
                  for itype in cfg.interaction_types}

    # 预读属性数组（避免热循环 MDAnalysis 调用）
    all_resnames = np.array(analyzer.u.atoms.resnames)
    all_positions = analyzer.u.atoms.positions  # 末帧坐标

    hbonds = analyzer.hbonds_data
    d_indices = hbonds[:, 1].astype(np.int32)
    a_indices = hbonds[:, 3].astype(np.int32)

    d_resnames = all_resnames[d_indices]
    a_resnames = all_resnames[a_indices]
    label_map  = cfg.resname_to_label

    d_labels = np.array([label_map.get(r, "") for r in d_resnames])
    a_labels = np.array([label_map.get(r, "") for r in a_resnames])

    d_pos = all_positions[d_indices]   # (N, 3)
    a_pos = all_positions[a_indices]   # (N, 3)
    mid_x = ((d_pos[:, 0] + a_pos[:, 0]) / 2) % Lx
    mid_y = ((d_pos[:, 1] + a_pos[:, 1]) / 2) % Ly

    xi = np.clip((mid_x / Lx * n_bins).astype(np.int32), 0, n_bins - 1)
    yi = np.clip((mid_y / Ly * n_bins).astype(np.int32), 0, n_bins - 1)

    for itype in cfg.interaction_types:
        d_label, a_label = itype.split("-")
        sel = (d_labels == d_label) & (a_labels == a_label)
        if not np.any(sel):
            continue
        np.add.at(count_maps[itype], (yi[sel], xi[sel]), 1)

    density_maps = {}
    for itype in cfg.interaction_types:
        cnt   = count_maps[itype]
        total = int(np.sum(cnt))
        if total == 0:
            continue
        density_maps[itype] = {
            "density": cnt / bin_area,
            "x_edges": x_edges,
            "y_edges": y_edges,
            "count":   total,
        }
        print(f"  {itype}: {total} hbonds mapped")

    analyzer.density_maps = density_maps
    return density_maps
