#!/usr/bin/env python3
"""Analyze water-like molecular orientation relative to the z-axis.

The orientation vector is defined from the selected oxygen atom to the midpoint
of the two selected hydrogen atoms within each residue.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import MDAnalysis as mda
import numpy as np
from tqdm import tqdm

DEFAULT_OUTPUT_PREFIX = "water_orientation_z"
DEFAULT_WATER_RESNAME = "Wat"
DEFAULT_OXYGEN_SELECTION = "name O"
DEFAULT_HYDROGEN_SELECTION = "name H"
DEFAULT_Z_BINS = 100
DEFAULT_THETA_BINS = 90
DEFAULT_STEP = 1


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze z-resolved orientation of water-like molecules from an MD "
            "trajectory."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--structure",
        required=True,
        help="Topology or structure file readable by MDAnalysis",
    )
    parser.add_argument(
        "-f",
        "--trajectory",
        required=True,
        help="Trajectory file readable by MDAnalysis",
    )
    parser.add_argument(
        "--water-resname",
        default=DEFAULT_WATER_RESNAME,
        help="Residue name used to identify the target molecules",
    )
    parser.add_argument(
        "--oxygen-selection",
        default=DEFAULT_OXYGEN_SELECTION,
        help="Atom selection applied within each target residue to find the oxygen atom",
    )
    parser.add_argument(
        "--hydrogen-selection",
        default=DEFAULT_HYDROGEN_SELECTION,
        help="Atom selection applied within each target residue to find the two hydrogen atoms",
    )
    parser.add_argument(
        "-o",
        "--output-prefix",
        default=DEFAULT_OUTPUT_PREFIX,
        help="Prefix for generated output files",
    )
    parser.add_argument(
        "--z-bins",
        type=positive_int,
        default=DEFAULT_Z_BINS,
        help="Number of bins along the z axis",
    )
    parser.add_argument(
        "--theta-bins",
        type=positive_int,
        default=DEFAULT_THETA_BINS,
        help="Number of bins along the theta axis",
    )
    parser.add_argument("--start", type=int, default=None, help="Start frame")
    parser.add_argument("--stop", type=int, default=None, help="Stop frame")
    parser.add_argument(
        "--step",
        type=positive_int,
        default=DEFAULT_STEP,
        help="Frame step",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip PNG plot generation and export only text/NumPy outputs",
    )
    return parser.parse_args()


def wrap_delta(delta: np.ndarray, box_lengths: np.ndarray) -> np.ndarray:
    wrapped = delta.copy()
    valid = box_lengths > 0.0
    wrapped[:, valid] -= box_lengths[valid] * np.round(
        wrapped[:, valid] / box_lengths[valid]
    )
    return wrapped


def build_water_index_arrays(
    universe: mda.Universe,
    water_resname: str,
    oxygen_selection: str,
    hydrogen_selection: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    oxygen_indices: list[int] = []
    h1_indices: list[int] = []
    h2_indices: list[int] = []

    for residue in universe.select_atoms(f"resname {water_resname}").residues:
        oxygen = residue.atoms.select_atoms(oxygen_selection)
        hydrogens = residue.atoms.select_atoms(hydrogen_selection)
        if len(oxygen) != 1 or len(hydrogens) != 2:
            continue
        oxygen_indices.append(int(oxygen.indices[0]))
        h1_indices.append(int(hydrogens.indices[0]))
        h2_indices.append(int(hydrogens.indices[1]))

    if not oxygen_indices:
        raise ValueError(
            "No valid molecules found with the requested selections: "
            f"resname={water_resname!r}, oxygen_selection={oxygen_selection!r}, "
            f"hydrogen_selection={hydrogen_selection!r}."
        )

    return (
        np.asarray(oxygen_indices, dtype=np.int64),
        np.asarray(h1_indices, dtype=np.int64),
        np.asarray(h2_indices, dtype=np.int64),
    )


def analyze_orientation(
    universe: mda.Universe,
    oxygen_indices: np.ndarray,
    h1_indices: np.ndarray,
    h2_indices: np.ndarray,
    n_z_bins: int,
    n_theta_bins: int,
    start: int | None,
    stop: int | None,
    step: int,
) -> dict[str, np.ndarray | float | int]:
    first_ts = universe.trajectory[0]
    box = first_ts.dimensions[:3].astype(np.float64)
    z_min_nm = 0.0
    z_max_nm = float(box[2] / 10.0)
    area_nm2 = float((box[0] * box[1]) / 100.0)

    z_edges = np.linspace(z_min_nm, z_max_nm, n_z_bins + 1)
    z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])
    z_bin_width_nm = float(z_edges[1] - z_edges[0])
    theta_edges_deg = np.linspace(0.0, 180.0, n_theta_bins + 1)
    theta_centers_deg = 0.5 * (theta_edges_deg[:-1] + theta_edges_deg[1:])
    theta_bin_width_deg = float(theta_edges_deg[1] - theta_edges_deg[0])
    bin_volume_nm3 = area_nm2 * z_bin_width_nm

    count_sum = np.zeros(n_z_bins, dtype=np.float64)
    cos_sum = np.zeros(n_z_bins, dtype=np.float64)
    theta_sum = np.zeros(n_z_bins, dtype=np.float64)
    orient2d_counts = np.zeros((n_z_bins, n_theta_bins), dtype=np.float64)

    frame_slice = universe.trajectory[start:stop:step]
    n_frames = 0
    atoms = universe.atoms
    assert atoms is not None

    for ts in tqdm(frame_slice, desc="Analyzing water orientation"):
        box_lengths = ts.dimensions[:3].astype(np.float64)
        oxygen_positions = atoms[oxygen_indices].positions.astype(np.float64)
        h1_positions = atoms[h1_indices].positions.astype(np.float64)
        h2_positions = atoms[h2_indices].positions.astype(np.float64)

        oh1 = wrap_delta(h1_positions - oxygen_positions, box_lengths)
        oh2 = wrap_delta(h2_positions - oxygen_positions, box_lengths)
        bisector = 0.5 * (oh1 + oh2)
        norms = np.linalg.norm(bisector, axis=1)
        valid = norms > 1.0e-8
        if not np.any(valid):
            continue

        unit_vectors = bisector[valid] / norms[valid, None]
        cos_theta = np.clip(unit_vectors[:, 2], -1.0, 1.0)
        theta_deg = np.degrees(np.arccos(cos_theta))
        z_nm = oxygen_positions[valid, 2] / 10.0

        z_indices = np.asarray(
            np.searchsorted(z_edges, z_nm, side="right") - 1, dtype=np.int64
        )
        z_valid = (z_indices >= 0) & (z_indices < n_z_bins)
        if not np.any(z_valid):
            continue

        z_indices = z_indices[z_valid]
        cos_theta = cos_theta[z_valid]
        theta_deg = theta_deg[z_valid]

        np.add.at(count_sum, z_indices, 1.0)
        np.add.at(cos_sum, z_indices, cos_theta)
        np.add.at(theta_sum, z_indices, theta_deg)

        theta_indices = np.asarray(
            np.searchsorted(theta_edges_deg, theta_deg, side="right") - 1,
            dtype=np.int64,
        )
        theta_indices = np.clip(theta_indices, 0, n_theta_bins - 1)
        np.add.at(orient2d_counts, (z_indices, theta_indices), 1.0)
        n_frames += 1

    if n_frames == 0:
        raise ValueError("No frames were analyzed.")

    with np.errstate(divide="ignore", invalid="ignore"):
        mean_cos_theta = np.divide(
            cos_sum, count_sum, out=np.full_like(cos_sum, np.nan), where=count_sum > 0
        )
        mean_theta_deg = np.divide(
            theta_sum,
            count_sum,
            out=np.full_like(theta_sum, np.nan),
            where=count_sum > 0,
        )

    number_density_nm3 = count_sum / (n_frames * bin_volume_nm3)
    orient_number_density = orient2d_counts / (
        n_frames * bin_volume_nm3 * theta_bin_width_deg
    )

    return {
        "z_edges_nm": z_edges,
        "z_centers_nm": z_centers,
        "theta_edges_deg": theta_edges_deg,
        "theta_centers_deg": theta_centers_deg,
        "mean_cos_theta": mean_cos_theta,
        "mean_theta_deg": mean_theta_deg,
        "count_per_z": count_sum,
        "number_density_nm3": number_density_nm3,
        "orientation_number_density": orient_number_density,
        "n_frames": n_frames,
        "bin_volume_nm3": bin_volume_nm3,
        "theta_bin_width_deg": theta_bin_width_deg,
        "z_bin_width_nm": z_bin_width_nm,
    }


def save_profile_data(
    results: dict[str, np.ndarray | float | int], prefix: str
) -> None:
    profile_path = Path(f"{prefix}_profile.dat")
    hist2d_path = Path(f"{prefix}_hist2d.dat")
    archive_path = Path(f"{prefix}_raw.npz")

    z_centers_nm = np.asarray(results["z_centers_nm"])
    mean_cos_theta = np.asarray(results["mean_cos_theta"])
    mean_theta_deg = np.asarray(results["mean_theta_deg"])
    count_per_z = np.asarray(results["count_per_z"])
    number_density_nm3 = np.asarray(results["number_density_nm3"])
    theta_centers_deg = np.asarray(results["theta_centers_deg"])
    orientation_number_density = np.asarray(results["orientation_number_density"])

    with profile_path.open("w", encoding="utf-8") as handle:
        handle.write(
            "# z_center_nm count_per_z mean_cos_theta mean_theta_deg number_density_nm^-3\n"
        )
        for values in zip(
            z_centers_nm,
            count_per_z,
            mean_cos_theta,
            mean_theta_deg,
            number_density_nm3,
        ):
            z_nm, count, mean_cos, mean_theta, density = values
            handle.write(
                f"{z_nm:.6f} {count:.6f} {mean_cos:.6f} {mean_theta:.6f} {density:.6f}\n"
            )

    with hist2d_path.open("w", encoding="utf-8") as handle:
        handle.write(
            "# z_center_nm theta_center_deg orientation_number_density_nm^-3_deg^-1\n"
        )
        for z_nm, row in zip(z_centers_nm, orientation_number_density):
            for theta_deg, density in zip(theta_centers_deg, row):
                handle.write(f"{z_nm:.6f} {theta_deg:.6f} {density:.10f}\n")
            handle.write("\n")

    np.savez(archive_path, **results)
    print(f"Saved: {profile_path}")
    print(f"Saved: {hist2d_path}")
    print(f"Saved: {archive_path}")


def plot_results(results: dict[str, np.ndarray | float | int], prefix: str) -> None:
    z_edges_nm = np.asarray(results["z_edges_nm"])
    theta_edges_deg = np.asarray(results["theta_edges_deg"])
    z_centers_nm = np.asarray(results["z_centers_nm"])
    mean_cos_theta = np.asarray(results["mean_cos_theta"])
    mean_theta_deg = np.asarray(results["mean_theta_deg"])
    number_density_nm3 = np.asarray(results["number_density_nm3"])
    orientation_number_density = np.asarray(results["orientation_number_density"])

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.5,
        }
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    mesh = ax.pcolormesh(
        z_edges_nm,
        theta_edges_deg,
        orientation_number_density.T,
        shading="auto",
        cmap="viridis",
    )
    ax.set_xlabel("z (nm)")
    ax.set_ylabel(r"$\theta$ (deg)")
    ax.set_title("Water orientation number density vs z")
    cbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    cbar.set_label(r"Number density (nm$^{-3}$ deg$^{-1}$)")
    fig.tight_layout()
    heatmap_path = Path(f"{prefix}_heatmap.png")
    fig.savefig(heatmap_path, dpi=400, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {heatmap_path}")

    fig, axes = plt.subplots(2, 1, figsize=(8.4, 7.0), sharex=True)
    axes[0].plot(z_centers_nm, mean_cos_theta, color="#0072B2")
    axes[0].axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    axes[0].set_ylabel(r"$\langle \cos\theta \rangle$")
    axes[0].set_title("Water orientation profile along z")
    axes[0].grid(True, alpha=0.25, linestyle="--")

    ax2 = axes[1]
    ax2.plot(
        z_centers_nm, mean_theta_deg, color="#D55E00", label=r"$\langle \theta \rangle$"
    )
    ax2.set_ylabel(r"$\langle \theta \rangle$ (deg)")
    ax2.grid(True, alpha=0.25, linestyle="--")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(
        z_centers_nm, number_density_nm3, color="#009E73", label="Number density"
    )
    ax2_twin.set_ylabel(r"$\rho$ (nm$^{-3}$)")
    ax2.set_xlabel("z (nm)")

    profile_path = Path(f"{prefix}_profile.png")
    fig.tight_layout()
    fig.savefig(profile_path, dpi=400, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {profile_path}")


def main() -> None:
    args = parse_args()

    print("=" * 68)
    print("Water orientation vs z analysis")
    print("Vector definition: O -> midpoint(H1, H2)")
    print("=" * 68)
    print(f"Topology:   {args.structure}")
    print(f"Trajectory: {args.trajectory}")

    universe = mda.Universe(args.structure, args.trajectory)
    oxygen_indices, h1_indices, h2_indices = build_water_index_arrays(
        universe,
        water_resname=args.water_resname,
        oxygen_selection=args.oxygen_selection,
        hydrogen_selection=args.hydrogen_selection,
    )

    print(f"Frames available: {len(universe.trajectory)}")
    print(f"Water molecules:  {len(oxygen_indices)}")
    print(f"Selected resname: {args.water_resname}")
    print(f"Oxygen selection: {args.oxygen_selection}")
    print(f"Hydrogen selection: {args.hydrogen_selection}")

    results = analyze_orientation(
        universe,
        oxygen_indices,
        h1_indices,
        h2_indices,
        n_z_bins=args.z_bins,
        n_theta_bins=args.theta_bins,
        start=args.start,
        stop=args.stop,
        step=args.step,
    )

    save_profile_data(results, args.output_prefix)
    if args.no_plots:
        print("Skipping plot generation (--no-plots).")
    else:
        plot_results(results, args.output_prefix)

    mean_cos = np.asarray(results["mean_cos_theta"])
    mean_theta = np.asarray(results["mean_theta_deg"])
    number_density = np.asarray(results["number_density_nm3"])
    count_per_z = np.asarray(results["count_per_z"])
    valid = count_per_z > 0
    global_mean_cos = float(np.nanmean(mean_cos[valid])) if np.any(valid) else math.nan
    global_mean_theta = (
        float(np.nanmean(mean_theta[valid])) if np.any(valid) else math.nan
    )
    peak_density_index = int(np.nanargmax(number_density))

    print("\nSummary")
    print("-" * 68)
    print(f"Analyzed frames: {results['n_frames']}")
    print(f"z bin width:     {results['z_bin_width_nm']:.4f} nm")
    print(f"theta bin width: {results['theta_bin_width_deg']:.4f} deg")
    print(f"Global <cos(theta)> over occupied z bins: {global_mean_cos:.6f}")
    print(f"Global <theta> over occupied z bins:      {global_mean_theta:.6f} deg")
    print(
        "Peak water number density: "
        f"{number_density[peak_density_index]:.6f} nm^-3 at z = {np.asarray(results['z_centers_nm'])[peak_density_index]:.6f} nm"
    )
    print("Analysis complete.")


if __name__ == "__main__":
    main()
