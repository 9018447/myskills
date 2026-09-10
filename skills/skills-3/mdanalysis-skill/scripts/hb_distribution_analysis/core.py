#!/usr/bin/env python3
"""
Core Module for Hydrogen Bond Analysis
=======================================

通用分析器类 HBAnalyzer，通过 SystemConfig 适配任意分子体系。
"""

import MDAnalysis as mda

from .config import SystemConfig, default_config


class HBAnalyzer:
    """
    通用氢键分析器。

    通过传入不同的 `config`（SystemConfig）即可适配不同分子体系，
    无需修改代码。

    Parameters
    ----------
    topology_file : str
        拓扑文件路径（.tpr、.gro、.pdb 等）
    trajectory_file : str
        轨迹文件路径（.xtc、.trr、.dcd 等）
    config : SystemConfig, optional
        体系配置对象。若为 None，使用 default_config()（ChCl:EG 默认值）。
    distance_cutoff : float, optional
        覆盖 config 中的 D-A 截断距离（Å）
    angle_cutoff : float, optional
        覆盖 config 中的 D-H-A 最小角度（°）

    Attributes
    ----------
    u : MDAnalysis.Universe
    config : SystemConfig
    distance_cutoff, angle_cutoff : float
    groups : dict  {group_name → AtomGroup}  各分子组原子集合
    hbonds_data, density_maps, lifetime_data : 分析结果存储
    """

    def __init__(
        self,
        topology_file: str,
        trajectory_file: str,
        config: SystemConfig | None = None,
        distance_cutoff: float | None = None,
        angle_cutoff: float | None = None,
    ):
        self.topology_file    = topology_file
        self.trajectory_file  = trajectory_file

        # 加载配置，允许 CLI 参数覆盖
        self.config = config if config is not None else default_config()
        self.config.override_cutoffs(distance_cutoff, angle_cutoff)

        self.distance_cutoff = self.config.distance_cutoff
        self.angle_cutoff    = self.config.angle_cutoff

        # 初始化 MDAnalysis Universe
        self.u = mda.Universe(topology_file, trajectory_file)

        # 按配置选择各分子组
        self.groups: dict = {}
        print("System composition:")
        for g in self.config.groups:
            ag = self.u.select_atoms(g.resname_sel)
            self.groups[g.name] = ag
            print(f"  {g.name} ({', '.join(g.resname)}): {len(ag.residues)} residues")

        # 打印原子选择信息
        self._print_hbond_atom_info()

        # 数据存储
        self.hbonds_data   = None
        self.density_maps  = None
        self.lifetime_data = None

    def _print_hbond_atom_info(self):
        """打印供体/受体原子数（用于验证选择是否正确）。"""
        print("\nHydrogen bond atom selections:")
        for g in self.config.groups:
            ag = self.groups[g.name]
            if g.can_donate:
                donors = ag.select_atoms(g.donor_heavy_sel)
                print(f"  {g.name} donors ({g.donor_heavy_sel}): {len(donors)} atoms")
            if g.can_accept:
                acceptors = ag.select_atoms(g.acceptor_sel)
                print(f"  {g.name} acceptors ({g.acceptor_sel}): {len(acceptors)} atoms")

    def get_system_info(self) -> dict:
        """返回体系基本信息字典。"""
        info = {"total_frames": len(self.u.trajectory)}
        for name, ag in self.groups.items():
            info[f"total_{name}"] = len(ag.residues)
        return info


# 向后兼容别名（旧代码仍可用 EutecticSolventHBAnalyzer）
EutecticSolventHBAnalyzer = HBAnalyzer
