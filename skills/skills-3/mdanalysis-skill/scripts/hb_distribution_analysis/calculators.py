#!/usr/bin/env python3
"""
Calculators Module for Hydrogen Bond Analysis
==============================================

核心计算模块，通过 analyzer.config 自动适配任意分子体系：
1. calculate_hydrogen_bonds  — 氢键检测（支持 last_frames 截取末尾帧）
2. calculate_lifetime_by_type — 按分子对类型计算氢键生命周期自相关函数
                                （向量化 + FFT 加速，O(n log n) 复杂度）
"""

import numpy as np
from MDAnalysis.analysis.hydrogenbonds.hbond_analysis import HydrogenBondAnalysis
from scipy.signal import fftconvolve


def calculate_hydrogen_bonds(analyzer, distance_cutoff=None, angle_cutoff=None, last_frames=None):
    """
    检测轨迹中的氢键，选择字符串从 analyzer.config 自动获取。

    Parameters
    ----------
    analyzer : HBAnalyzer
    distance_cutoff : float, optional  覆盖 config 的 D-A 截断距离（Å）
    angle_cutoff : float, optional     覆盖 config 的 D-H-A 最小角度（°）
    last_frames : int, optional        只分析末尾 N 帧；None 表示全轨迹

    Returns
    -------
    HydrogenBondAnalysis  已运行完毕的氢键分析对象
    """
    cfg = analyzer.config
    if distance_cutoff is None:
        distance_cutoff = cfg.distance_cutoff
    if angle_cutoff is None:
        angle_cutoff = cfg.angle_cutoff

    # 确定分析帧范围
    total_frames = len(analyzer.u.trajectory)
    if last_frames is not None:
        start_frame = max(0, total_frames - int(last_frames))
        stop_frame  = total_frames
    else:
        start_frame = None
        stop_frame  = None

    print("\nCalculating hydrogen bonds with:")
    print(f"  Distance cutoff: {distance_cutoff} Å")
    print(f"  Angle cutoff: {angle_cutoff}°")
    if start_frame is not None and stop_frame is not None:
        n_actual = stop_frame - start_frame
        print(f"  Analyzing frames: {start_frame} ~ {stop_frame - 1} (last {n_actual} frames)")
    else:
        print(f"  Analyzing all {total_frames} frames")

    # ── 选择字符串来自 config（自动生成，无硬编码）
    print(f"  Donors   : {cfg.donors_sel}")
    print(f"  Acceptors: {cfg.acceptors_sel}")

    hba = HydrogenBondAnalysis(
        universe=analyzer.u,
        donors_sel=cfg.donors_sel,
        hydrogens_sel=cfg.hydrogens_sel,
        acceptors_sel=cfg.acceptors_sel,
        d_a_cutoff=distance_cutoff,
        d_h_a_angle_cutoff=180 - angle_cutoff,
    )

    hba.run(start=start_frame, stop=stop_frame)

    analyzer.hbonds_data = hba.results.hbonds
    print(f"Total hydrogen bonds found: {len(analyzer.hbonds_data)}")

    return hba


def _acf_fft(signal: np.ndarray) -> np.ndarray:
    """FFT 计算单信号的非归一化自相关（正延迟，长度 = len(signal)）。"""
    n = len(signal)
    full_corr = fftconvolve(signal, signal[::-1], mode="full")
    return full_corr[n - 1:]


def calculate_lifetime_by_type(hba, analyzer):
    """
    按分子对类型分别计算氢键生命周期连续时间自相关函数（ACF）。

    类型标签和分类映射全部来自 analyzer.config，无硬编码体系信息。

    算法：预读 numpy 属性数组 + FFT（O(n log n)），消除 MDAnalysis API 热循环。

    Parameters
    ----------
    hba : HydrogenBondAnalysis  已完成 run() 的氢键分析对象
    analyzer : HBAnalyzer

    Returns
    -------
    dict  {itype: {"tau": ndarray(ps), "acf": ndarray(归一化), "count": int}}
    """
    print("\nCalculating hydrogen bond lifetimes by interaction type...")

    cfg    = analyzer.config
    results = {}
    hbonds  = hba.results.hbonds

    if len(hbonds) == 0:
        print("  No hydrogen bonds to analyze.")
        analyzer.lifetime_data = results
        return results

    try:
        dt = float(analyzer.u.trajectory.dt)
    except Exception:
        dt = 1.0

    analyzed_frames = hba.frames
    n_frames = len(analyzed_frames)
    if n_frames < 2:
        print("  Too few frames for lifetime analysis (need >= 2).")
        analyzer.lifetime_data = results
        return results

    # 帧号 → 帧索引快速查找
    max_frame = int(analyzed_frames.max())
    frame_to_idx = np.full(max_frame + 1, -1, dtype=np.int32)
    for i, f in enumerate(analyzed_frames):
        frame_to_idx[int(f)] = i

    # ── 预读所有原子属性（一次性批量，消除 MDAnalysis 热循环）
    all_resnames = np.array(analyzer.u.atoms.resnames)
    all_resids   = np.array(analyzer.u.atoms.resids, dtype=np.int32)

    # ── 提取 hbonds 各列
    hb_frame_nums = hbonds[:, 0].astype(np.int32)
    d_indices     = hbonds[:, 1].astype(np.int32)
    a_indices     = hbonds[:, 3].astype(np.int32)

    d_resnames = all_resnames[d_indices]
    a_resnames = all_resnames[a_indices]
    d_resids   = all_resids[d_indices]
    a_resids   = all_resids[a_indices]

    hb_fidx_raw = np.clip(hb_frame_nums, 0, max_frame)
    hb_fidx = frame_to_idx[hb_fidx_raw]
    valid   = hb_fidx >= 0

    # ── 向量化映射：resname → group label（来自 config）
    label_map = cfg.resname_to_label             # {resname_str → display_name}
    d_labels  = np.array([label_map.get(r, "") for r in d_resnames])
    a_labels  = np.array([label_map.get(r, "") for r in a_resnames])

    # ── 对每种 interaction type 计算 ACF
    for itype in cfg.interaction_types:
        d_label, a_label = itype.split("-")

        sel = valid & (d_labels == d_label) & (a_labels == a_label)
        if not np.any(sel):
            print(f"  {itype}: no hydrogen bonds found, skipping.")
            continue

        s_fidx  = hb_fidx[sel]
        s_d_res = d_resids[sel]
        s_a_res = a_resids[sel]

        # pair 编号
        pairs_raw = np.stack([s_d_res, s_a_res], axis=1)
        _, pair_ids = np.unique(pairs_raw, axis=0, return_inverse=True)
        n_pairs = int(pair_ids.max()) + 1

        # 存在矩阵 E[n_frames, n_pairs]
        E = np.zeros((n_frames, n_pairs), dtype=np.float32)
        E[s_fidx, pair_ids] = 1.0

        # FFT 自相关累加
        acf_sum = np.zeros(n_frames, dtype=np.float64)
        batch   = 256
        for start in range(0, n_pairs, batch):
            end   = min(start + batch, n_pairs)
            chunk = E[:, start:end]
            for col in range(chunk.shape[1]):
                acf_sum += _acf_fft(chunk[:, col].astype(np.float64))

        acf = acf_sum / acf_sum[0] if acf_sum[0] > 0 else acf_sum
        tau_axis = np.arange(n_frames) * dt
        count    = int(np.sum(sel))

        results[itype] = {"tau": tau_axis, "acf": acf, "count": count}
        print(f"  {itype}: {count} hbond entries, tau_max={tau_axis[-1]:.1f} ps")

    analyzer.lifetime_data = results
    return results
