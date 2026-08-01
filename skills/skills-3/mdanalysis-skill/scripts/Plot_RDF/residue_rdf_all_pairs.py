#!/usr/bin/env python3
"""Export residue-type RDFs for all residue pairs to a single CSV."""

from __future__ import annotations

import argparse
from collections import OrderedDict
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Sequence

import MDAnalysis as mda
import numpy as np
import pandas as pd
from MDAnalysis.core.groups import ResidueGroup
from MDAnalysis.lib.distances import capped_distance, self_capped_distance
from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute residue-type RDFs for all residue pairs in a trajectory."
    )
    parser.add_argument(
        "-s", "--structure", required=True, help="Topology/structure file"
    )
    parser.add_argument("-f", "--trajectory", required=True, help="Trajectory file")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file")
    parser.add_argument(
        "--nbins", type=int, default=200, help="Number of RDF bins (default: 200)"
    )
    parser.add_argument(
        "--rmax-nm",
        type=float,
        default=None,
        help="Maximum distance in nm (default: half of the shortest box edge from first frame)",
    )
    parser.add_argument("--start", type=int, default=None, help="Start frame")
    parser.add_argument("--stop", type=int, default=None, help="Stop frame")
    parser.add_argument("--step", type=int, default=1, help="Frame step")
    parser.add_argument(
        "--resnames",
        nargs="+",
        default=None,
        help="Explicit residue names to include, e.g. --resnames SOL NA CL",
    )
    return parser.parse_args()


def unique_residue_names(universe) -> list[str]:
    ordered: OrderedDict[str, None] = OrderedDict()
    for resname in universe.atoms.resnames:
        ordered.setdefault(str(resname), None)
    return list(ordered.keys())


def resolve_residue_names(
    universe, requested_resnames: Sequence[str] | None
) -> list[str]:
    available_residue_names = unique_residue_names(universe)
    if requested_resnames is None:
        return available_residue_names

    ordered: OrderedDict[str, None] = OrderedDict()
    for resname in requested_resnames:
        ordered.setdefault(str(resname), None)

    residue_names = list(ordered.keys())
    missing_residue_names = [
        resname for resname in residue_names if resname not in available_residue_names
    ]
    if missing_residue_names:
        raise ValueError(
            "Residue names not found in the system: "
            f"{missing_residue_names}. Available residue names: {available_residue_names}"
        )

    return residue_names


def get_residue_groups(universe, residue_names: list[str]) -> dict[str, ResidueGroup]:
    groups: dict[str, ResidueGroup] = {}
    for resname in residue_names:
        groups[resname] = universe.select_atoms(f"resname {resname}").residues
    return groups


def shell_volumes(bin_edges_angstrom: np.ndarray) -> np.ndarray:
    return (
        (4.0 / 3.0)
        * np.pi
        * (bin_edges_angstrom[1:] ** 3 - bin_edges_angstrom[:-1] ** 3)
    )


def main() -> None:
    args = parse_args()

    structure_path = Path(args.structure)
    trajectory_path = Path(args.trajectory)
    output_path = Path(args.output)

    universe = mda.Universe(str(structure_path), str(trajectory_path))
    residue_names = resolve_residue_names(universe, args.resnames)
    residue_groups = get_residue_groups(universe, residue_names)

    first_dimensions = universe.trajectory[0].dimensions[:3]
    rmax_angstrom = (
        args.rmax_nm * 10.0
        if args.rmax_nm is not None
        else float(np.min(first_dimensions) / 2.0)
    )
    bin_edges_angstrom = np.linspace(0.0, rmax_angstrom, args.nbins + 1)
    radius_centers_nm = (bin_edges_angstrom[:-1] + bin_edges_angstrom[1:]) / 2.0 / 10.0
    shell_volumes_angstrom3 = shell_volumes(bin_edges_angstrom)

    pair_keys = list(combinations_with_replacement(residue_names, 2))
    pair_histograms = {
        pair: np.zeros(args.nbins, dtype=np.float64) for pair in pair_keys
    }
    pair_counts = {}
    for resname_a, resname_b in pair_keys:
        count_a = len(residue_groups[resname_a])
        count_b = len(residue_groups[resname_b])
        if resname_a == resname_b:
            pair_counts[(resname_a, resname_b)] = count_a * (count_a - 1) / 2.0
        else:
            pair_counts[(resname_a, resname_b)] = count_a * count_b

    volume_sum = 0.0
    frame_slice = universe.trajectory[args.start : args.stop : args.step]
    n_frames = 0

    print(f"Residue types: {residue_names}")
    print(f"RDF pairs: {[f'{a}-{b}' for a, b in pair_keys]}")
    print(f"Using r_max = {rmax_angstrom / 10.0:.4f} nm, nbins = {args.nbins}")

    for ts in tqdm(frame_slice, desc="Computing residue RDF"):
        box = ts.dimensions
        box_volume = float(np.prod(box[:3]))
        volume_sum += box_volume
        n_frames += 1

        centers = {
            resname: residue_group.atoms.center_of_geometry(compound="residues")
            for resname, residue_group in residue_groups.items()
        }

        for resname_a, resname_b in pair_keys:
            coords_a = centers[resname_a]
            coords_b = centers[resname_b]

            if resname_a == resname_b:
                _, distances = self_capped_distance(
                    coords_a,
                    max_cutoff=rmax_angstrom,
                    min_cutoff=0.0,
                    box=box,
                )
            else:
                _, distances = capped_distance(
                    coords_a,
                    coords_b,
                    max_cutoff=rmax_angstrom,
                    min_cutoff=0.0,
                    box=box,
                )

            histogram, _ = np.histogram(
                distances,
                bins=bin_edges_angstrom,
            )
            pair_histograms[(resname_a, resname_b)] += histogram

    if n_frames == 0:
        raise ValueError("No frames selected for RDF calculation.")

    rdf_data = {"r_nm": radius_centers_nm}
    mean_number_density = n_frames / volume_sum
    for pair in pair_keys:
        pair_factor = pair_counts[pair]
        normalization = (
            pair_factor * shell_volumes_angstrom3 * n_frames * mean_number_density
        )
        rdf = np.divide(
            pair_histograms[pair],
            normalization,
            out=np.zeros_like(pair_histograms[pair]),
            where=normalization > 0,
        )
        rdf_data[f"rdf_{pair[0]}_{pair[1]}"] = rdf

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rdf_data)
    df.to_csv(output_path, index=False)

    print(f"Processed {n_frames} frames")
    print(f"Saved CSV: {output_path}")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
