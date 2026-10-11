#!/usr/bin/env python3
"""
Exporters Module for Hydrogen Bond Analysis
============================================

只导出两类数据：
- save_density_maps   : 2D 密度图矩阵 → .npz
- save_lifetime_data  : 生命周期 ACF → CSV
"""

import os

import numpy as np
import pandas as pd

from .config import DEFAULT_OUTPUT_DIR


def save_density_maps(analyzer, output_dir=None):
    """
    将各分子对的 2D 密度矩阵保存为 NumPy .npz 文件。

    文件名：hb_density_maps.npz
    内容：各 interaction_type 的 density (n_bins×n_bins)，及 x_edges, y_edges

    Parameters
    ----------
    analyzer : EutecticSolventHBAnalyzer
    output_dir : str, optional
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    if not hasattr(analyzer, "density_maps") or not analyzer.density_maps:
        print("  No density map data to save.")
        return

    arrays = {}
    for itype, data in analyzer.density_maps.items():
        key = itype.replace("-", "_")
        arrays[f"{key}_density"] = data["density"]
        arrays[f"{key}_x_edges"] = data["x_edges"]
        arrays[f"{key}_y_edges"] = data["y_edges"]

    out_path = os.path.join(output_dir, "hb_density_maps.npz")
    np.savez_compressed(out_path, **arrays)
    print(f"  Density maps saved: {out_path}")


def save_lifetime_data(analyzer, output_dir=None):
    """
    将各分子对的生命周期 ACF 数据保存为 CSV 文件。

    文件名：hb_lifetime_data.csv
    列：tau_ps, <InteractionType1>, <InteractionType2>, ...

    Parameters
    ----------
    analyzer : EutecticSolventHBAnalyzer
    output_dir : str, optional
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    if not hasattr(analyzer, "lifetime_data") or not analyzer.lifetime_data:
        print("  No lifetime data to save.")
        return

    # 找出最长公共 tau 轴
    df_dict = {}
    max_len = max(len(v["tau"]) for v in analyzer.lifetime_data.values())
    # 用第一个类型的 tau 作为时间轴（步长相同）
    first = next(iter(analyzer.lifetime_data.values()))
    tau_col = first["tau"]
    df_dict["tau_ps"] = tau_col

    for itype, data in analyzer.lifetime_data.items():
        acf = data["acf"]
        # 若长度不同则填 NaN
        if len(acf) == len(tau_col):
            df_dict[itype] = acf
        else:
            arr = np.full(len(tau_col), np.nan)
            arr[:len(acf)] = acf
            df_dict[itype] = arr

    df = pd.DataFrame(df_dict)
    out_path = os.path.join(output_dir, "hb_lifetime_data.csv")
    df.to_csv(out_path, index=False, float_format="%.6f")
    print(f"  Lifetime data saved: {out_path}")


def save_data_tables(analyzer, output_dir=None):
    """统一入口：依次保存密度图和生命周期数据。"""
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    print(f"\nSaving data to {output_dir}...")
    save_density_maps(analyzer, output_dir)
    save_lifetime_data(analyzer, output_dir)
    print(f"Data saved to {output_dir}/")
