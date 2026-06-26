#!/usr/bin/env python3
"""
Configuration Module for Hydrogen Bond Analysis
================================================

提供两种使用方式：
1. load_config(yaml_path)  : 从外部 YAML 文件加载体系配置
2. default_config()        : 使用内置的 ChCl:EG 默认配置（向后兼容）

SystemConfig 自动生成：
  - MDAnalysis 选择字符串（donors_sel / hydrogens_sel / acceptors_sel）
  - 所有相互作用类型对（interaction_types）
  - 残基名→标签的映射字典（resname_to_label）
  - 自动分配的颜色（interaction_colors）
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ── 默认几何截断（可被 YAML 或 CLI 参数覆盖）
DEFAULT_DISTANCE_CUTOFF = 3.5  # Å
DEFAULT_ANGLE_CUTOFF = 120  # degrees
DEFAULT_OUTPUT_DIR = "hb_analysis_output"
DEFAULT_DPI = 300
DEFAULT_N_BINS = 100

# ── 科学风格低饱和度配色板
# 参考 seaborn "muted" 风格，在 HLS 空间降低饱和度（~50%）并引入灰度感
# 避免纯色，适合出版级图表
_SCIENCE_PALETTE = [
    "#4C72B0",  # 钢蓝（muted blue）
    "#C44E52",  # 砖红（muted red）
    "#55A868",  # 鼠尾草绿（sage green）
    "#DD8452",  # 赭石橙（terracotta）
    "#8172B2",  # 薰衣草紫（muted purple）
    "#937860",  # 卡其棕（khaki brown）
    "#DA8BC3",  # 藕荷粉（dusty rose）
    "#818381",  # 中灰（medium gray）
    "#CCB974",  # 暗金（muted gold）
    "#64B5CD",  # 石板蓝（slate blue）
]


# ---------------------------------------------------------------------------
# GroupConfig ── 单个分子组的配置
# ---------------------------------------------------------------------------
@dataclass
class GroupConfig:
    """描述一类分子/离子的氢键参与能力。"""

    name: str  # 显示名称，例如 "Choline"
    resname: List[str]  # MDAnalysis resname 列表
    can_donate: bool = False  # 是否可作为供体（有 O-H/N-H）
    donor_heavy_sel: str = "name O*"  # 供体重原子选择（限定在 resname 内）
    can_accept: bool = False  # 是否可作为受体
    acceptor_sel: str = "name O*"  # 受体原子选择（限定在 resname 内）

    @property
    def resname_sel(self) -> str:
        """生成 resname 的 MDAnalysis 选择字符串。"""
        if len(self.resname) == 1:
            return f"resname {self.resname[0]}"
        parts = " or ".join(f"resname {r}" for r in self.resname)
        return f"({parts})"


# ---------------------------------------------------------------------------
# SystemConfig ── 完整的体系配置
# ---------------------------------------------------------------------------
@dataclass
class SystemConfig:
    """
    体系配置，由 load_config() 或 default_config() 生成。

    关键自动生成字段：
      - donors_sel, hydrogens_sel, acceptors_sel : MDAnalysis 选择字符串
      - interaction_types  : 所有 (donor, acceptor) 组合的列表
      - resname_to_label   : {resname_str → group display_name}
      - interaction_colors : {interaction_type → color_hex}
    """

    system_name: str = "Generic System"
    groups: List[GroupConfig] = field(default_factory=list)
    hydrogens_sel: str = "name H*"
    distance_cutoff: float = DEFAULT_DISTANCE_CUTOFF
    angle_cutoff: float = DEFAULT_ANGLE_CUTOFF
    output_dir: str = DEFAULT_OUTPUT_DIR
    n_bins: int = DEFAULT_N_BINS
    dpi: int = DEFAULT_DPI

    # ── 自动派生字段（由 __post_init__ 计算）
    donors_sel: str = field(init=False, default="")
    acceptors_sel: str = field(init=False, default="")
    interaction_types: List[str] = field(init=False, default_factory=list)
    resname_to_label: Dict[str, str] = field(init=False, default_factory=dict)
    interaction_colors: Dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self._build_selections()
        self._build_interaction_types()
        self._build_resname_map()
        self._build_colors()

    # ── 内部构建方法 ──────────────────────────────────────────────────────

    def _build_selections(self):
        """从各组配置拼接 MDAnalysis donors_sel 和 acceptors_sel。"""
        donor_parts = []
        acceptor_parts = []
        for g in self.groups:
            if g.can_donate:
                donor_parts.append(f"({g.resname_sel} and {g.donor_heavy_sel})")
            if g.can_accept:
                acceptor_parts.append(f"({g.resname_sel} and {g.acceptor_sel})")
        self.donors_sel = " or ".join(donor_parts) or "none"
        self.acceptors_sel = " or ".join(acceptor_parts) or "none"

    def _build_interaction_types(self):
        """生成所有 (donor_group, acceptor_group) 组合的 interaction type 列表。"""
        donors = [g for g in self.groups if g.can_donate]
        acceptors = [g for g in self.groups if g.can_accept]
        itypes = []
        for d, a in itertools.product(donors, acceptors):
            itypes.append(f"{d.name}-{a.name}")
        self.interaction_types = itypes

    def _build_resname_map(self):
        """构建 {resname_str → group display_name} 映射。"""
        mapping = {}
        for g in self.groups:
            for rn in g.resname:
                mapping[rn] = g.name
        self.resname_to_label = mapping

    def _build_colors(self):
        """为每种 interaction type 自动分配颜色。"""
        colors = {}
        for i, itype in enumerate(self.interaction_types):
            colors[itype] = _SCIENCE_PALETTE[i % len(_SCIENCE_PALETTE)]
        self.interaction_colors = colors

    # ── 覆盖截断参数（允许 CLI 参数覆盖 YAML 设置）───────────────────────

    def override_cutoffs(
        self,
        distance_cutoff: Optional[float] = None,
        angle_cutoff: Optional[float] = None,
    ):
        """用 CLI 参数覆盖 YAML 中的截断值（None 表示不覆盖）。"""
        if distance_cutoff is not None:
            self.distance_cutoff = distance_cutoff
        if angle_cutoff is not None:
            self.angle_cutoff = angle_cutoff

    def summary(self) -> str:
        """返回配置摘要字符串，用于打印。"""
        lines = [
            f"System: {self.system_name}",
            f"Groups ({len(self.groups)}):",
        ]
        for g in self.groups:
            roles = []
            if g.can_donate:
                roles.append(f"donor:{g.donor_heavy_sel}")
            if g.can_accept:
                roles.append(f"acceptor:{g.acceptor_sel}")
            lines.append(f"  {g.name} ({','.join(g.resname)}) [{'; '.join(roles)}]")
        lines.append(f"Interaction types: {', '.join(self.interaction_types)}")
        lines.append(f"Cutoffs: d={self.distance_cutoff} Å, angle={self.angle_cutoff}°")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 公开 API：load_config / default_config
# ---------------------------------------------------------------------------


def load_config(yaml_path: str | Path) -> SystemConfig:
    """
    从 YAML 文件加载体系配置。

    Parameters
    ----------
    yaml_path : str or Path
        指向 system.yaml（或任何符合格式的 YAML）的路径

    Returns
    -------
    SystemConfig
    """
    try:
        import yaml
    except ImportError as e:
        raise ImportError("需要安装 pyyaml：uv pip install pyyaml") from e

    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    groups = []
    for g_raw in raw.get("groups", []):
        # resname 支持单字符串或列表
        resname = g_raw["resname"]
        if isinstance(resname, str):
            resname = [resname]

        groups.append(
            GroupConfig(
                name=g_raw["name"],
                resname=resname,
                can_donate=g_raw.get("can_donate", False),
                donor_heavy_sel=g_raw.get("donor_heavy_sel", "name O*"),
                can_accept=g_raw.get("can_accept", False),
                acceptor_sel=g_raw.get("acceptor_sel", "name O*"),
            )
        )

    return SystemConfig(
        system_name=raw.get("system_name", "Unnamed System"),
        groups=groups,
        hydrogens_sel=raw.get("hydrogens_sel", "name H*"),
        distance_cutoff=float(raw.get("distance_cutoff", DEFAULT_DISTANCE_CUTOFF)),
        angle_cutoff=float(raw.get("angle_cutoff", DEFAULT_ANGLE_CUTOFF)),
        output_dir=raw.get("output_dir", DEFAULT_OUTPUT_DIR),
        n_bins=int(raw.get("n_bins", DEFAULT_N_BINS)),
        dpi=int(raw.get("dpi", DEFAULT_DPI)),
    )


def default_config() -> SystemConfig:
    """
    返回内置的 ChCl:EG 默认配置（不需要外部 YAML 文件）。

    仅用于向后兼容；推荐通过 load_config("scripts/hb_distribution_analysis/system.yaml") 使用。
    """
    _builtin = Path(__file__).parent / "system.yaml"
    if _builtin.exists():
        return load_config(_builtin)

    # 最终回退：硬编码默认值
    return SystemConfig(
        system_name="ChCl:EG Eutectic Solvent",
        groups=[
            GroupConfig(
                name="Choline",
                resname=["Cho"],
                can_donate=True,
                donor_heavy_sel="name O*",
                can_accept=True,
                acceptor_sel="name O*",
            ),
            GroupConfig(
                name="Chloride",
                resname=["Chl"],
                can_donate=False,
                can_accept=True,
                acceptor_sel="name CL*",
            ),
            GroupConfig(
                name="EthyleneGlycol",
                resname=["Eth"],
                can_donate=True,
                donor_heavy_sel="name O*",
                can_accept=True,
                acceptor_sel="name O*",
            ),
        ],
        hydrogens_sel="name H*",
    )


# ---------------------------------------------------------------------------
# 向后兼容常量（供未修改的调用方使用）
# ---------------------------------------------------------------------------
_defaults = None


def _get_defaults() -> SystemConfig:
    global _defaults
    if _defaults is None:
        _defaults = default_config()
    return _defaults


RESIDUE_NAMES = {"choline": "Cho", "chloride": "Chl", "ethylene_glycol": "Eth"}
INTERACTION_TYPES = property(lambda self: _get_defaults().interaction_types)
INTERACTION_COLORS = property(lambda self: _get_defaults().interaction_colors)
ATOM_SELECTIONS = {
    "choline_donors": "name H* and around 1.5 (name O*)",
    "choline_acceptors": "name O*",
    "chloride_acceptors": "name CL*",
    "eth_donors": "name H* and around 1.5 (name O*)",
    "eth_acceptors": "name O*",
}
PLOT_STYLE = {
    "figsize_density_maps": (15, 10),
    "alpha": 0.7,
    "grid_alpha": 0.3,
    "edgecolor": "black",
}
DEFAULT_CMAP = "viridis"
