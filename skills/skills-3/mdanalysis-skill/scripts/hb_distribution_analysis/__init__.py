#!/usr/bin/env python3
"""Generic hydrogen-bond analysis package for MDAnalysis workflows.

Usage examples
--------------
    from scripts.hb_distribution_analysis import HBAnalyzer, load_config, run_analysis

    config = load_config("my_system.yaml")
    analyzer = HBAnalyzer("md.tpr", "md.xtc", config=config)
    run_analysis(analyzer, last_frames=100)
"""

import numpy as np

__version__ = "3.0.0"
__author__ = "Hydrogen Bond Analysis Team"

# 配置
from .config import (
    DEFAULT_ANGLE_CUTOFF,
    DEFAULT_DISTANCE_CUTOFF,
    DEFAULT_OUTPUT_DIR,
    GroupConfig,
    SystemConfig,
    default_config,
    load_config,
)

# 核心
from .core import EutecticSolventHBAnalyzer, HBAnalyzer

# 计算
from .calculators import calculate_hydrogen_bonds, calculate_lifetime_by_type

# 分析
from .analyzers import create_2d_density_map

# 可视化
from .visualization import (
    plot_2d_density_maps,
    plot_lifetime_autocorr,
    visualize_results,
)

# 导出
from .exporters import save_data_tables, save_density_maps, save_lifetime_data

__all__ = [
    # 配置
    "SystemConfig",
    "GroupConfig",
    "load_config",
    "default_config",
    "DEFAULT_DISTANCE_CUTOFF",
    "DEFAULT_ANGLE_CUTOFF",
    "DEFAULT_OUTPUT_DIR",
    # 核心类（新名 + 旧别名）
    "HBAnalyzer",
    "EutecticSolventHBAnalyzer",
    # 计算
    "calculate_hydrogen_bonds",
    "calculate_lifetime_by_type",
    # 分析
    "create_2d_density_map",
    # 可视化
    "visualize_results",
    "plot_2d_density_maps",
    "plot_lifetime_autocorr",
    # 导出
    "save_data_tables",
    "save_density_maps",
    "save_lifetime_data",
    # 便捷入口
    "run_analysis",
    "print_summary",
]


def run_analysis(
    analyzer,
    distance_cutoff=None,
    angle_cutoff=None,
    output_dir=None,
    create_plots=True,
    save_data=True,
    last_frames=None,
):
    """
    完整分析流水线：氢键检测 → 生命周期 ACF → 2D 密度图 → 绘图/导出。

    Parameters
    ----------
    analyzer : HBAnalyzer
    distance_cutoff, angle_cutoff : float, optional  覆盖 config 截断值
    output_dir : str, optional       输出目录（覆盖 config.output_dir）
    create_plots : bool              是否生成图片
    save_data : bool                 是否保存数据文件
    last_frames : int, optional      只分析末尾 N 帧；None 表示全轨迹
    """
    # 确定输出目录
    if output_dir is None:
        output_dir = analyzer.config.output_dir

    # 1. 计算氢键
    hba = calculate_hydrogen_bonds(
        analyzer,
        distance_cutoff=distance_cutoff,
        angle_cutoff=angle_cutoff,
        last_frames=last_frames,
    )

    # 2. 生命周期 ACF
    calculate_lifetime_by_type(hba, analyzer)

    # 3. 2D 密度图
    create_2d_density_map(analyzer)

    # 4. 可视化
    if create_plots:
        visualize_results(analyzer, output_dir=output_dir)

    # 5. 数据导出
    if save_data:
        save_data_tables(analyzer, output_dir=output_dir)

    return {
        "density_maps": getattr(analyzer, "density_maps", {}),
        "lifetime_data": getattr(analyzer, "lifetime_data", {}),
    }


def print_summary(analyzer):
    """打印分析摘要。"""
    print("\n" + "=" * 50)
    print("ANALYSIS SUMMARY")
    print("=" * 50)

    info = analyzer.get_system_info()
    print(f"System : {analyzer.config.system_name}")
    print(f"Frames : {info['total_frames']} total")

    if hasattr(analyzer, "hbonds_data") and analyzer.hbonds_data is not None:
        print(f"Total hydrogen bonds found: {len(analyzer.hbonds_data)}")

    if hasattr(analyzer, "density_maps") and analyzer.density_maps:
        print("\n2D Density Maps:")
        for itype, data in analyzer.density_maps.items():
            print(f"  {itype}: {data['count']} hbonds")

    if hasattr(analyzer, "lifetime_data") and analyzer.lifetime_data:
        print("\nLifetime ACF (τ at C(τ)=1/e):")
        for itype, data in analyzer.lifetime_data.items():
            acf, tau = data["acf"], data["tau"]
            idx = np.where(acf <= 1 / np.e)[0]
            tau_e = tau[idx[0]] if len(idx) > 0 else tau[-1]
            print(f"  {itype}: τ(1/e) ≈ {tau_e:.2f} ps  (N={data['count']})")
