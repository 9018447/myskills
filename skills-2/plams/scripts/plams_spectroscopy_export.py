#!/usr/bin/env amspython
"""Generic PLAMS spectroscopy workflow with data export.

This script accepts a molecular structure (XYZ file or SMILES string), runs a
PLAMS/AMS calculation for a selected spectral property, and exports the results
to JSON/CSV files.

Supported properties:
    - frequencies : vibrational frequencies only
    - ir          : IR spectrum + discrete vibrational data
    - raman       : Raman spectrum + discrete vibrational data
    - vcd         : VCD spectrum + discrete vibrational data
    - uvvis       : excitation energies + oscillator strengths

Examples:
    amspython plams_spectroscopy_export.py --input molecule.xyz --property ir
    amspython plams_spectroscopy_export.py --smiles "CCO" --property raman
    amspython plams_spectroscopy_export.py --input molecule.xyz --property uvvis --output-dir results
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np
import scm.plams as plams
from scm.plams import AMSJob, Molecule, Settings, Units, from_smiles

try:
    from scm.plams.tools.postprocess_results import broaden_results as _broaden_results
except ImportError:
    _broaden_results = None


def broaden_results(
    centers: np.ndarray,
    areas: np.ndarray,
    broadening_type: str = "gaussian",
    broadening_width: float = 20.0,
    x_data: tuple | None = None,
    post_process: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    if _broaden_results is not None:
        return _broaden_results(
            centers=centers,
            areas=areas,
            broadening_type=broadening_type,
            broadening_width=broadening_width,
            x_data=x_data,
            post_process=post_process,
        )

    if x_data is None:
        x_data = (0.0, 4000.0, 1.0)
    min_x, max_x, x_spacing = x_data
    x = np.arange(min_x, max_x + x_spacing, x_spacing)

    sigma = broadening_width / 2.0
    y = np.zeros_like(x, dtype=float)
    for center, area in zip(centers, areas):
        if broadening_type == "gaussian":
            y += (
                area
                * np.exp(-0.5 * ((x - center) / sigma) ** 2)
                / (sigma * np.sqrt(2.0 * np.pi))
            )
        else:
            gamma = broadening_width / 2.0
            y += area * (gamma / np.pi) / ((x - center) ** 2 + gamma**2)

    if post_process == "max_to_1":
        max_y = np.max(y)
        if max_y > 0:
            y /= max_y

    return x, y


VIBRATIONAL_PROPERTIES = {"frequencies", "ir", "raman", "vcd"}
SUPPORTED_PROPERTIES = VIBRATIONAL_PROPERTIES | {"uvvis"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate and export molecular spectral properties with PLAMS."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--input", help="Path to an input structure file such as .xyz or .mol"
    )
    source.add_argument("--smiles", help="SMILES string for the input molecule")

    parser.add_argument(
        "--property",
        choices=sorted(SUPPORTED_PROPERTIES),
        default="ir",
        help="Spectral property to calculate",
    )
    parser.add_argument(
        "--name",
        default="spectroscopy_job",
        help="Base name for job and exported files",
    )
    parser.add_argument(
        "--output-dir",
        default="spectroscopy_output",
        help="Directory for exported files",
    )

    parser.add_argument(
        "--engine",
        choices=["dftb", "adf", "uff"],
        default="dftb",
        help="Engine for vibrational calculations. Raman and UV/Vis use ADF regardless of this option.",
    )
    parser.add_argument(
        "--dftb-model",
        default="GFN1-xTB",
        help="DFTB model for vibrational calculations",
    )
    parser.add_argument(
        "--adf-basis", default="TZ2P", help="ADF basis for vibrational calculations"
    )
    parser.add_argument(
        "--adf-xc", default="B3LYP", help="ADF XC hybrid for vibrational calculations"
    )
    parser.add_argument(
        "--adf-quality",
        default="Good",
        help="ADF numerical quality for vibrational calculations",
    )

    parser.add_argument(
        "--uvvis-lowest",
        type=int,
        default=10,
        help="Number of lowest excitations for UV/Vis",
    )
    parser.add_argument(
        "--uvvis-basis",
        default="TZP",
        help="ADF basis for UV/Vis excitation calculation",
    )
    parser.add_argument(
        "--uvvis-xc",
        default="PBE",
        help="ADF XC functional for UV/Vis excitation calculation",
    )
    parser.add_argument(
        "--uvvis-quality", default="Basic", help="ADF numerical quality for UV/Vis"
    )

    parser.add_argument(
        "--broadening-type", choices=["gaussian", "lorentzian"], default="gaussian"
    )
    parser.add_argument(
        "--broadening-width",
        type=float,
        default=20.0,
        help="Spectrum broadening width in cm^-1",
    )
    parser.add_argument(
        "--min-frequency",
        type=float,
        default=0.0,
        help="Minimum spectrum x-axis value in cm^-1",
    )
    parser.add_argument(
        "--max-frequency",
        type=float,
        default=4000.0,
        help="Maximum spectrum x-axis value in cm^-1",
    )
    parser.add_argument(
        "--x-spacing", type=float, default=1.0, help="Spectrum x-axis spacing in cm^-1"
    )
    return parser.parse_args()


def load_molecule(args: argparse.Namespace) -> Molecule:
    if args.smiles:
        return from_smiles(args.smiles)
    return Molecule(args.input)


def sanitize_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in name)


def ensure_success(job: AMSJob) -> None:
    if job.status == "successful" or job.ok():
        return

    error_message = ""
    try:
        error_message = job.get_errormsg()
    except Exception:
        error_message = "Unknown AMS/PLAMS error"
    raise RuntimeError(
        f"Job '{job.name}' failed with status '{job.status}': {error_message}"
    )


def effective_engine(args: argparse.Namespace) -> str:
    if args.property == "raman" and args.engine != "adf":
        return "adf"
    return args.engine


def build_vibrational_settings(args: argparse.Namespace) -> Settings:
    settings = Settings()
    settings.input.ams.Task = "GeometryOptimization"
    settings.input.ams.Properties.NormalModes = "Yes"

    engine = effective_engine(args)
    if engine != args.engine:
        print(
            f"Notice: Raman intensities require the ADF engine. Overriding '--engine {args.engine}' to '--engine adf'."
        )

    if args.property == "raman":
        settings.input.ams.Properties.Raman = "Yes"

    if engine == "dftb":
        settings.input.DFTB.Model = args.dftb_model
    elif engine == "uff":
        settings.input.ForceField.Type = "UFF"
    elif engine == "adf":
        settings.input.ADF.Basis.Type = args.adf_basis
        settings.input.ADF.XC.Hybrid = args.adf_xc
        settings.input.ADF.NumericalQuality = args.adf_quality
        settings.input.ADF.Symmetry = "NoSym"

    return settings


def build_uvvis_go_settings() -> Settings:
    settings = Settings()
    settings.input.ams.Task = "GeometryOptimization"
    settings.input.ams.GeometryOptimization.Convergence.Gradients = 1.0e-4
    settings.input.ADF.Basis.Type = "DZP"
    settings.input.ADF.NumericalQuality = "Basic"
    settings.input.ADF.Symmetry = "NoSym"
    return settings


def build_uvvis_excitation_settings(args: argparse.Namespace) -> Settings:
    settings = Settings()
    settings.input.ams.Task = "SinglePoint"
    settings.input.ADF.Basis.Type = args.uvvis_basis
    settings.input.ADF.XC.GGA = args.uvvis_xc
    settings.input.ADF.NumericalQuality = args.uvvis_quality
    settings.input.ADF.Symmetry = "NoSym"
    settings.input.ADF.Excitations.lowest = args.uvvis_lowest
    settings.input.ADF.Excitations.OnlySing = ""
    return settings


def write_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def molecule_to_xyz_string(molecule: Molecule) -> str:
    lines = [str(len(molecule)), "Generated by PLAMS spectroscopy export script"]
    for atom in molecule:
        x, y, z = atom.coords
        lines.append(f"{atom.symbol:2s} {x:16.8f} {y:16.8f} {z:16.8f}")
    return "\n".join(lines) + "\n"


def norm_in_debye(dipole_au: np.ndarray) -> float:
    return float(np.linalg.norm(dipole_au) * Units.convert(1.0, "au", "debye"))


def safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def rkf_array(
    results: Any, section: str, variable: str, file: str = "engine"
) -> np.ndarray:
    values = results.readrkf(section, variable, file=file)
    if values is None:
        raise KeyError(f"Missing RKF field {section}%{variable} in {file}.rkf")
    return np.asarray(values, dtype=float).reshape(-1)


def _try_method_then_rkf(
    results: Any,
    method_name: str,
    section: str,
    variable: str,
    file: str = "engine",
) -> np.ndarray | None:
    method = getattr(results, method_name, None)
    if callable(method):
        try:
            return np.asarray(method(), dtype=float).reshape(-1)
        except Exception:
            pass
    try:
        return rkf_array(results, section, variable, file=file)
    except Exception:
        return None


def get_frequencies_array(results: Any) -> np.ndarray:
    method = getattr(results, "get_frequencies", None)
    if callable(method):
        try:
            return np.asarray(method(unit="cm^-1"), dtype=float).reshape(-1)
        except Exception:
            pass
    return rkf_array(results, "Vibrations", "Frequencies[cm-1]")


def get_reduced_masses_array(results: Any, n_modes: int) -> np.ndarray | None:
    result = _try_method_then_rkf(
        results, "get_reduced_masses", "Vibrations", "ReducedMasses"
    )
    if result is None:
        return None
    return result[:n_modes]


def get_normal_modes_array(
    results: Any, n_modes: int, n_atoms: int
) -> np.ndarray | None:
    method = getattr(results, "get_normal_modes", None)
    if callable(method):
        try:
            return np.asarray(method(), dtype=float)
        except Exception:
            pass
    try:
        mode_list = []
        for index in range(1, n_modes + 1):
            mode_values = rkf_array(
                results, "Vibrations", f"NoWeightNormalMode({index})"
            )
            mode_list.append(mode_values.reshape(n_atoms, 3))
        return np.asarray(mode_list, dtype=float)
    except Exception:
        return None


def get_zpe(results: Any, unit: str = "kcal/mol") -> float | None:
    method = getattr(results, "get_zero_point_energy", None)
    if callable(method):
        try:
            return safe_float(method(unit=unit))
        except Exception:
            pass
    try:
        zpe_au = results.readrkf("Vibrations", "ZeroPointEnergy", file="engine")
        if zpe_au is not None:
            return safe_float(float(zpe_au) * Units.conversion_ratio("au", unit))
    except Exception:
        pass
    return None


def broaden_vibrational_spectrum(
    frequencies: np.ndarray,
    intensities: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    x_data, y_data = broaden_results(
        centers=frequencies,
        areas=intensities,
        broadening_width=args.broadening_width,
        broadening_type=args.broadening_type,
        x_data=(args.min_frequency, args.max_frequency, args.x_spacing),
    )
    return np.asarray(x_data, dtype=float), np.asarray(y_data, dtype=float)


def extract_vibrational_data(job: AMSJob, args: argparse.Namespace) -> Dict[str, Any]:
    results = job.results
    frequencies = get_frequencies_array(results)
    n_modes = len(frequencies)
    n_atoms = len(results.get_main_molecule())
    reduced_masses = get_reduced_masses_array(results, n_modes)
    normal_modes = get_normal_modes_array(results, n_modes, n_atoms)

    discrete_rows: List[Dict[str, Any]] = []

    ir_intensities = _try_method_then_rkf(
        results, "get_ir_intensities", "Vibrations", "Intensities[km/mol]"
    )
    raman_intensities = _try_method_then_rkf(
        results, "get_raman_intensities", "Vibrations", "RamanIntens[A^4/amu]"
    )
    if raman_intensities is None:
        raman_intensities = _try_method_then_rkf(
            results, "get_raman_intensities", "Vibrations", "RamanActivities"
        )
    if raman_intensities is None:
        raman_intensities = _try_method_then_rkf(
            results, "get_raman_intensities", "Vibrations", "RamanDepolRatio"
        )
    if raman_intensities is None:
        raman_intensities = _try_method_then_rkf(
            results, "get_raman_intensities", "Vibrations", "RamanScattering"
        )
    vcd_strengths = _try_method_then_rkf(
        results, "get_vcd_rotational_strength", "Vibrations", "RotationalStrength"
    )

    for index, frequency in enumerate(frequencies, start=1):
        row: Dict[str, Any] = {
            "mode": index,
            "frequency_cm-1": float(frequency),
        }
        if reduced_masses is not None and index - 1 < len(reduced_masses):
            row["reduced_mass_amu"] = float(reduced_masses[index - 1])
        if ir_intensities is not None and index - 1 < len(ir_intensities):
            row["ir_intensity_km_per_mol"] = float(ir_intensities[index - 1])
        if raman_intensities is not None and index - 1 < len(raman_intensities):
            row["raman_intensity_A4_per_amu"] = float(raman_intensities[index - 1])
        if vcd_strengths is not None and index - 1 < len(vcd_strengths):
            row["vcd_rotational_strength"] = float(vcd_strengths[index - 1])
        discrete_rows.append(row)

    spectrum_x: np.ndarray | None = None
    spectrum_y: np.ndarray | None = None
    if args.property == "ir":
        if ir_intensities is None:
            raise RuntimeError(
                "IR intensities were not found in the results, so the IR spectrum cannot be built."
            )
        spectrum_x, spectrum_y = broaden_vibrational_spectrum(
            frequencies, ir_intensities, args
        )
    elif args.property == "raman":
        if raman_intensities is None:
            raise RuntimeError(
                "Raman intensities were not found in the results, so the Raman spectrum cannot be built."
            )
        spectrum_x, spectrum_y = broaden_vibrational_spectrum(
            frequencies, raman_intensities, args
        )
    elif args.property == "vcd":
        if vcd_strengths is None:
            raise RuntimeError(
                "VCD rotational strengths were not found in the results, so the VCD spectrum cannot be built."
            )
        spectrum_x, spectrum_y = broaden_vibrational_spectrum(
            frequencies, vcd_strengths, args
        )

    optimized_molecule = results.get_main_molecule()
    energy_kcal = float(results.get_energy(unit="kcal/mol"))
    zpe_kcal = get_zpe(results, unit="kcal/mol")

    dipole_debye = None
    try:
        dipole_debye = norm_in_debye(
            np.asarray(results.get_dipolemoment(), dtype=float)
        )
    except Exception:
        dipole_debye = None

    payload: Dict[str, Any] = {
        "property": args.property,
        "job_name": job.name,
        "engine": effective_engine(args),
        "energy_kcal_per_mol": energy_kcal,
        "zero_point_energy_kcal_per_mol": zpe_kcal,
        "dipole_moment_debye": dipole_debye,
        "imaginary_frequency_count": int(np.sum(frequencies < 0.0)),
        "discrete_data": discrete_rows,
        "normal_modes": normal_modes.tolist() if normal_modes is not None else None,
        "optimized_xyz": molecule_to_xyz_string(optimized_molecule),
    }

    if spectrum_x is not None and spectrum_y is not None:
        payload["spectrum"] = {
            "x_unit": "cm^-1",
            "x": np.asarray(spectrum_x, dtype=float).tolist(),
            "y": np.asarray(spectrum_y, dtype=float).tolist(),
        }

    return payload


def extract_uvvis_data(job: AMSJob, args: argparse.Namespace) -> Dict[str, Any]:
    results = job.results
    energies_au = results.readrkf("Excitations SS A", "excenergies", file="engine")
    oscillator_strengths_au = results.readrkf(
        "Excitations SS A", "oscillator strengths", file="engine"
    )

    if energies_au is None or oscillator_strengths_au is None:
        raise RuntimeError(
            "Could not extract UV/Vis excitations from the engine RKF file."
        )

    excitation_energies = np.asarray(
        Units.convert(energies_au, "au", "eV"), dtype=float
    ).reshape(-1)
    oscillator_strengths = np.asarray(oscillator_strengths_au, dtype=float).reshape(-1)

    discrete_rows = []
    for index, (energy, strength) in enumerate(
        zip(excitation_energies, oscillator_strengths), start=1
    ):
        row = {
            "state": index,
            "excitation_energy_eV": float(energy),
            "oscillator_strength_au": float(strength),
        }
        wavelength_nm = 1239.841984 / float(energy) if energy > 0 else None
        row["wavelength_nm"] = wavelength_nm
        discrete_rows.append(row)

    optimized_molecule = results.get_main_molecule()

    return {
        "property": args.property,
        "job_name": job.name,
        "engine": "adf",
        "discrete_data": discrete_rows,
        "optimized_xyz": molecule_to_xyz_string(optimized_molecule),
    }


def export_payload(payload: Dict[str, Any], output_dir: Path, base_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    write_json(output_dir / f"{base_name}.json", payload)

    discrete_rows = payload.get("discrete_data", [])
    if discrete_rows:
        write_csv(output_dir / f"{base_name}_discrete.csv", discrete_rows)

    spectrum = payload.get("spectrum")
    if spectrum:
        spectrum_rows = [
            {"x": float(x_val), "y": float(y_val)}
            for x_val, y_val in zip(spectrum["x"], spectrum["y"])
        ]
        write_csv(output_dir / f"{base_name}_spectrum.csv", spectrum_rows)

    optimized_xyz = payload.get("optimized_xyz")
    if optimized_xyz:
        (output_dir / f"{base_name}_optimized.xyz").write_text(
            optimized_xyz, encoding="utf-8"
        )


def run_vibrational_workflow(
    molecule: Molecule, args: argparse.Namespace, base_name: str
) -> Dict[str, Any]:
    settings = build_vibrational_settings(args)
    job = AMSJob(molecule=molecule, settings=settings, name=base_name)
    job.run()
    ensure_success(job)
    return extract_vibrational_data(job, args)


def run_uvvis_workflow(
    molecule: Molecule, args: argparse.Namespace, base_name: str
) -> Dict[str, Any]:
    optimization_job = AMSJob(
        molecule=molecule, settings=build_uvvis_go_settings(), name=f"{base_name}_opt"
    )
    optimization_job.run()
    ensure_success(optimization_job)

    optimized_molecule = optimization_job.results.get_main_molecule()
    excitation_job = AMSJob(
        molecule=optimized_molecule,
        settings=build_uvvis_excitation_settings(args),
        name=f"{base_name}_uvvis",
    )
    excitation_job.run()
    ensure_success(excitation_job)
    return extract_uvvis_data(excitation_job, args)


def main() -> None:
    args = parse_args()
    property_name = args.property.lower()
    output_dir = Path(args.output_dir).resolve()
    input_label = Path(args.input).stem if args.input else "smiles_input"
    base_name = sanitize_name(f"{args.name}_{property_name}_{input_label}")

    workdir = output_dir / "plams_workdir"
    workdir.mkdir(parents=True, exist_ok=True)
    plams.init(path=str(workdir))
    try:
        molecule = load_molecule(args)
        if property_name in VIBRATIONAL_PROPERTIES:
            payload = run_vibrational_workflow(molecule, args, base_name)
        else:
            payload = run_uvvis_workflow(molecule, args, base_name)
        export_payload(payload, output_dir, base_name)
    finally:
        plams.finish()

    print(f"Finished {property_name} calculation.")
    print(f"Export directory: {output_dir}")
    print(f"JSON summary: {output_dir / f'{base_name}.json'}")


if __name__ == "__main__":
    main()
