#!/usr/bin/env python3
"""DES dehydration-regeneration full-plant sensitivity analysis.

This module performs One-At-A-Time (OAT) sensitivity analysis on the
full_des_dehydration_plant template.  It reuses the same ProcessState,
compute_metrics(), and incremental update_*() API so that chemistry setup
and the System object are cached across perturbations.

Run from the repository root::

    PYTHONPATH=thermosteam \
        python .claude/skills/biosteam-process-builder/templates/full_des_dehydration_sensitivity.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any

import importlib.util

import numpy as np
import pandas as pd
import yaml

# ---------------------------------------------------------------------------
# Local development import fix
# ---------------------------------------------------------------------------
def _find_repo_root(start: Path) -> Path:
    """Locate the repository root by looking for thermosteam + biosteam packages."""
    for parent in start.resolve().parents:
        if (parent / "thermosteam").is_dir() and (parent / "biosteam").is_dir():
            return parent
    raise FileNotFoundError("Could not locate repository root")


def _find_skill_dir(start: Path) -> Path:
    """Locate the skill root by looking for the V2 base template marker file."""
    for parent in start.resolve().parents:
        if (parent / "templates" / "des_dehydration.py").is_file():
            return parent
    raise FileNotFoundError("Could not locate biosteam-process-builder skill directory")


REPO_ROOT = _find_repo_root(Path(__file__))
SKILL_DIR = _find_skill_dir(Path(__file__))
THERMO_PATH = REPO_ROOT / "thermosteam"
if str(THERMO_PATH) not in sys.path:
    sys.path.insert(0, str(THERMO_PATH))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the full-plant template as a module.  We avoid a top-level import so
# that this file can be syntax-checked even when Clapeyron is not available.
PLANT_TEMPLATE_PATH = SKILL_DIR / "templates" / "full_des_dehydration_plant.py"
_spec = importlib.util.spec_from_file_location("full_des_dehydration_plant", str(PLANT_TEMPLATE_PATH))
PLANT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PLANT)


# ---------------------------------------------------------------------------
# Sensitivity configuration
# ---------------------------------------------------------------------------
SENSITIVITY = {
    "gas_feed_T": {
        "unit": "K",
        "baseline": PLANT.GAS_FEED["T"],
        "range": (30.0 + 273.15, 60.0 + 273.15),
        "points": 5,
        "update": "update_T_gas",
    },
    "gas_water_molefrac": {
        "unit": "-",
        "baseline": PLANT.GAS_FEED["Water"],
        "range": (0.03, 0.10),
        "points": 5,
        "update": "update_x_water",
    },
    "absorber_P": {
        "unit": "Pa",
        "baseline": PLANT.GAS_FEED["P"],
        "range": (1.0 * 1e5, 5.0 * 1e5),
        "points": 5,
        "update": "update_P",
    },
    "N_stages": {
        "unit": "-",
        "baseline": float(PLANT.COLUMN["N_stages"]),
        "range": (2.0, 8.0),
        "points": 5,
        "update": "update_N_stages",
    },
    "DES_total_flow": {
        "unit": "kmol/hr",
        "baseline": PLANT.ABSORBENT["flow"],
        "range": (300.0, 1200.0),
        "points": 5,
        "update": "update_DES_total_flow",
    },
    "makeup_fraction": {
        "unit": "-",
        "baseline": PLANT.MAKEUP_FRACTION,
        "range": (0.01, 0.15),
        "points": 5,
        "update": "update_makeup_fraction",
    },
    "stripper_T": {
        "unit": "K",
        "baseline": PLANT.STRIPPER["T"],
        "range": (120.0 + 273.15, 180.0 + 273.15),
        "points": 5,
        "update": "update_stripper_T",
    },
    "boilup": {
        "unit": "-",
        "baseline": PLANT.STRIPPER["boilup"],
        "range": (0.2, 1.0),
        "points": 5,
        "update": None,  # handled specially via stripper_spec
    },
}

OUTPUT_DIR = SKILL_DIR / "outputs"
RUN_ID = "run_full_plant_sensitivity_001"

# Re-export configuration seams from the full-plant template so callers can
# locate inputs and outputs without importing both modules.
DATA_PATH = PLANT.DATA_PATH

TARGETS = {
    "dry_gas_max": 1e-3,  # 0.1 mol%
    "regen_max": 1e-3,    # 0.1 mol%
}


# ---------------------------------------------------------------------------
# Baseline construction
# ---------------------------------------------------------------------------
def create_baseline_state(data: dict[str, Any]) -> Any:
    """Build and return a converged baseline ProcessState.

    Parameters
    ----------
    data : dict
        Parsed ``des_dehydration_data.yml``.

    Returns
    -------
    ProcessState
        A converged full-plant ProcessState ready for incremental updates.
    """
    inert_id = (PLANT.INERT.get("ID") or "").strip() or None
    inert_flow = float(PLANT.INERT.get("flow", 0.0) or 0.0)

    chemicals = PLANT.load_and_configure_thermo(data, inert_id)
    PLANT.HX["use_process_hx"] = True

    des_id = "DES_choline_chloride_glycerol"
    state = PLANT.ProcessState(
        chemicals,
        inert_id,
        inert_flow,
        PLANT.GAS_FEED,
        PLANT.ABSORBENT,
        des_id,
        makeup_fraction=PLANT.MAKEUP_FRACTION,
        stripper_spec=PLANT.STRIPPER,
        N_stages=PLANT.COLUMN["N_stages"],
    )
    state.build()
    return state


# ---------------------------------------------------------------------------
# Single-point evaluation
# ---------------------------------------------------------------------------
def evaluate_point(
    state: Any,
    parameter_name: str,
    value: float,
) -> dict[str, Any]:
    """Apply one parameter perturbation and return metrics.

    Parameters
    ----------
    state : ProcessState
        A previously converged baseline state.  This function mutates the
        state and re-converges it; the caller is responsible for restoring
        the baseline afterwards if needed.
    parameter_name : str
        Key in ``SENSITIVITY``.
    value : float
        New parameter value.

    Returns
    -------
    dict
        Row dictionary suitable for appending to the sensitivity DataFrame.
    """
    _apply_parameter(state, parameter_name, value)
    state.converge()
    metrics = PLANT.compute_metrics(state)
    return {
        "parameter": parameter_name,
        "value": value,
        "converged": True,
        "error": None,
        **metrics,
    }


def _apply_parameter(state: Any, parameter_name: str, value: float) -> None:
    """Apply a single parameter perturbation to ``state`` without converging."""
    config = SENSITIVITY[parameter_name]
    update_method_name = config.get("update")

    if parameter_name == "boilup":
        # boilup is part of the stripper spec and requires a rebuild.
        state.stripper_boilup = value
        state._needs_rebuild = True
    elif update_method_name is not None:
        update_method = getattr(state, update_method_name)
        update_method(value)
    else:
        raise ValueError(f"No update method configured for {parameter_name}")


# ---------------------------------------------------------------------------
# Full OAT sweep
# ---------------------------------------------------------------------------
def _parameter_grid(parameter_name: str, config: dict[str, Any]) -> list[float]:
    """Return linearly spaced values for a sensitivity parameter."""
    lo, hi = config["range"]
    points = int(config["points"])
    if points < 2:
        return [float(config["baseline"])]
    raw = np.linspace(lo, hi, points)
    # Keep integer parameters as integers where appropriate.
    if parameter_name == "N_stages":
        return sorted(set(int(round(v)) for v in raw))
    return raw.tolist()


def run_sensitivity_analysis(
    state: Any,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Run an OAT sensitivity sweep and return the results as a DataFrame.

    Parameters
    ----------
    state : ProcessState
        A converged baseline state.  The function restores the parameter to
        its baseline value after each parameter sweep.
    config : dict, optional
        Override for ``SENSITIVITY``.  Defaults to the module-level config.

    Returns
    -------
    pd.DataFrame
        One row per scanned point with columns ``parameter``, ``value``,
        ``converged``, ``error`` and all metrics keys.
    """
    config = config or SENSITIVITY
    rows: list[dict[str, Any]] = []

    for parameter_name, cfg in config.items():
        grid = _parameter_grid(parameter_name, cfg)
        baseline_value = float(cfg["baseline"])

        for value in grid:
            try:
                row = evaluate_point(state, parameter_name, value)
                rows.append(row)
            except Exception as exc:
                rows.append({
                    "parameter": parameter_name,
                    "value": value,
                    "converged": False,
                    "error": f"{type(exc).__name__}: {exc}",
                })

        # Restore this parameter to baseline before moving to the next one.
        try:
            _apply_parameter(state, parameter_name, baseline_value)
            state.converge()
        except Exception:
            # Best-effort cleanup; if restoring fails we still want to continue
            # scanning the remaining parameters.
            pass

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Recommendation and reporting
# ---------------------------------------------------------------------------
def recommend_operating_point(
    df: pd.DataFrame,
    targets: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Select the best operating point from a sensitivity DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Output from ``run_sensitivity_analysis``.
    targets : dict, optional
        ``{"dry_gas_max": float, "regen_max": float}``.

    Returns
    -------
    dict
        Recommendation summary including the selected row and feasibility flag.
    """
    targets = targets or TARGETS
    dry_max = targets["dry_gas_max"]
    regen_max = targets["regen_max"]

    converged = df[df["converged"] == True].copy()
    if converged.empty:
        return {
            "feasible": False,
            "reason": "No converged points in sensitivity DataFrame.",
            "row": None,
        }

    feasible = converged[
        (converged["water_molefrac_out"] <= dry_max)
        & (converged["regen_water_molefrac"] <= regen_max)
    ].copy()

    if not feasible.empty:
        feasible.sort_values(
            by=["removal", "reboiler_duty", "DES_total_flow"],
            ascending=[False, True, True],
            inplace=True,
        )
        row = feasible.iloc[0].to_dict()
        return {
            "feasible": True,
            "row": row,
            "targets": targets,
        }

    # No feasible point: report the closest candidates.
    best_dry = converged.loc[converged["water_molefrac_out"].idxmin()].to_dict()
    best_regen = converged.loc[converged["regen_water_molefrac"].idxmin()].to_dict()
    return {
        "feasible": False,
        "reason": "No scanned point simultaneously satisfies both < 0.1 mol% targets.",
        "closest_dry": best_dry,
        "closest_regen": best_regen,
        "targets": targets,
    }


def write_sensitivity_report(
    run_dir: Path,
    df: pd.DataFrame,
    recommended: dict[str, Any],
    targets: dict[str, float] | None = None,
    state: Any | None = None,
) -> tuple[Path, Path]:
    """Write sensitivity.csv and sensitivity.md to ``run_dir``.

    Returns
    -------
    tuple[Path, Path]
        Paths to (csv_path, md_path).
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    targets = targets or TARGETS

    csv_path = run_dir / "sensitivity.csv"
    df.to_csv(csv_path, index=False)

    md_path = run_dir / "sensitivity.md"
    converged = df[df["converged"] == True]

    with open(md_path, "w") as f:
        f.write("# DES Dehydration Full-Plant Sensitivity Analysis\n\n")
        f.write("**Backend**: Clapeyron/COSMOSAC2013 (rigorous thermodynamics)\n\n")
        f.write("**DES**: choline chloride / glycerol pseudo-component\n\n")
        f.write(f"**Converged points**: {len(converged)} / {len(df)}\n\n")

        if state is not None and state.extrapolation_warnings:
            f.write("## Extrapolation warnings\n\n")
            for warning in state.extrapolation_warnings:
                f.write(f"- ⚠️ {warning}\n")
            f.write("\n")

        f.write("## Sensitivity summary\n\n")
        f.write("| Parameter | Points | Min removal | Max removal | Min dry H2O | Min regen H2O |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for parameter_name in df["parameter"].unique():
            sub = converged[converged["parameter"] == parameter_name]
            if sub.empty:
                continue
            f.write(
                f"| {parameter_name} | {len(sub)} | "
                f"{sub['removal'].min():.4f} | {sub['removal'].max():.4f} | "
                f"{sub['water_molefrac_out'].min():.6f} | {sub['regen_water_molefrac'].min():.6f} |\n"
            )
        f.write("\n")

        f.write("## Recommendation\n\n")
        if recommended["feasible"]:
            row = recommended["row"]
            f.write("**Status**: ✅ Feasible (both targets < 0.1 mol%)\n\n")
            f.write(f"- Parameter: `{row['parameter']}` = {row['value']:.4f}\n")
            f.write(f"- Water removal: {row['removal']:.4%}\n")
            f.write(f"- Dry CO2 water mole fraction: {row['water_molefrac_out']:.6f} "
                    f"(target <= {targets['dry_gas_max']:.6f})\n")
            f.write(f"- Regenerated DES water mole fraction: {row['regen_water_molefrac']:.6f} "
                    f"(target <= {targets['regen_max']:.6f})\n")
            f.write(f"- Reboiler duty: {row['reboiler_duty'] / 3600.0:.3f} kW\n")
            if "DES_total_flow" in row:
                f.write(f"- DES total flow: {row['DES_total_flow']:.2f} kmol/hr\n")
        else:
            f.write("**Status**: ❌ No feasible point found\n\n")
            f.write(f"Reason: {recommended.get('reason', '')}\n\n")
            if "closest_dry" in recommended:
                row = recommended["closest_dry"]
                f.write("### Closest to dry-gas target\n\n")
                f.write(f"- Parameter: `{row['parameter']}` = {row['value']:.4f}\n")
                f.write(f"- Dry CO2 water mole fraction: {row['water_molefrac_out']:.6f} "
                        f"(gap {row['water_molefrac_out'] - targets['dry_gas_max']:+.6f})\n")
            if "closest_regen" in recommended:
                row = recommended["closest_regen"]
                f.write("### Closest to regenerated-DES target\n\n")
                f.write(f"- Parameter: `{row['parameter']}` = {row['value']:.4f}\n")
                f.write(f"- Regenerated DES water mole fraction: {row['regen_water_molefrac']:.6f} "
                        f"(gap {row['regen_water_molefrac'] - targets['regen_max']:+.6f})\n")
        f.write("\n")

        f.write("## Notes\n\n")
        f.write("- This is an OAT (One-At-A-Time) sensitivity scan: each row varies one parameter "
                "while all others remain at their baseline values.\n")
        f.write("- The recommendation rule prioritizes highest water removal, then lowest reboiler duty, "
                "then lowest DES total flow among feasible points.\n")
        f.write("- Convergence failures are recorded in `sensitivity.csv` with `converged=False`.\n\n")

        f.write("## Raw data\n\n")
        f.write("See [`sensitivity.csv`](sensitivity.csv) for the complete set of scanned points.\n")

    return csv_path, md_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the default sensitivity analysis and write reports."""
    with open(DATA_PATH) as f:
        data = yaml.safe_load(f)

    state = create_baseline_state(data)
    df = run_sensitivity_analysis(state)
    recommended = recommend_operating_point(df)

    run_dir = OUTPUT_DIR / RUN_ID
    csv_path, md_path = write_sensitivity_report(
        run_dir, df, recommended, targets=TARGETS, state=state
    )

    print(f"Sensitivity analysis complete.")
    print(f"  CSV: {csv_path}")
    print(f"  Report: {md_path}")
    print(f"  Converged points: {df['converged'].sum()} / {len(df)}")
    if recommended["feasible"]:
        row = recommended["row"]
        print(f"  Recommended: {row['parameter']} = {row['value']:.4f}")
        print(f"    Removal: {row['removal']:.4%}")
        print(f"    Dry H2O: {row['water_molefrac_out']:.6f}")
        print(f"    Regen H2O: {row['regen_water_molefrac']:.6f}")
    else:
        print("  No feasible operating point found in the scanned range.")


if __name__ == "__main__":
    main()
