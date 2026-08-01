#!/usr/bin/env python3
"""DES dehydration-regeneration base template (V2): CO2 drying with a DES
absorbent and a closed-loop solvent regeneration flash.

This script loads a pre-generated YAML data file (created by
prepare_des_dehydration_data.py), registers all chemicals and COSMO-SAC
profiles, builds a Mixer + gas-liquid absorption column + Flash flowsheet in
BioSTEAM, closes the DES recycle loop, and simulates it.

V2 is rigorous-mode only: both the absorber and the flash use the Clapeyron
backend with COSMOSAC2013.  If Clapeyron is not available the script fails
early with a clear message.

Run from the repository root with the default Python environment:

    PYTHONPATH=thermosteam \
        python .claude/skills/biosteam-process-builder/templates/des_dehydration.py

Inputs:
    ../../inputs/des_dehydration_data.yml

Outputs:
    ../../outputs/<run_id>/process.py     (this script, copied)
    ../../outputs/<run_id>/brief.md       (decision-ready summary)
    ../../outputs/<run_id>/log.txt        (execution log)
    ../../outputs/<run_id>/sensitivity.csv  (if sensitivity is enabled)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

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
    """Locate the skill root by looking for the template marker file."""
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

import biosteam as bst
import thermosteam as tmo
import warnings


class ConditionedMixer(bst.units.Mixer):
    """Mixer that forces outlet T/P to fixed values.

    V2 does not model separate pumps or heat exchangers.  The regenerated DES
    recycle stream leaves the flash at low pressure and high temperature; this
    mixer represents the implicit pressure increase and cooling required to
    return it to the absorber inlet conditions.  The outlet is set to the
    fresh-DES feed temperature and the column pressure.
    """

    def _init(self, *args, outlet_T: float | None = None,
              outlet_P: float | None = None, **kwargs):
        self.outlet_T = outlet_T
        self.outlet_P = outlet_P
        super()._init(*args, **kwargs)

    def _run(self):
        super()._run()
        out, = self.outs
        if self.outlet_P is not None:
            out.P = self.outlet_P
        if self.outlet_T is not None:
            out.T = self.outlet_T

warnings.filterwarnings("ignore", message=".*CO2 has no defined Dortmund groups.*")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_PATH = SKILL_DIR / "inputs" / "des_dehydration_data.yml"
OUTPUT_DIR = SKILL_DIR / "outputs"
RUN_ID = "run_001"

# Process specification (V2: editable directly in this script)
GAS_FEED = {
    "T": 40.0 + 273.15,      # K
    "P": 10.0 * 1e5,         # Pa
    "flow": 1000.0,          # kmol/hr
    "CO2": 0.95,             # mole fraction
    "Water": 0.05,           # mole fraction
}

# Total DES flow entering the mixer (fresh makeup + regenerated recycle).
ABSORBENT = {
    "T": 25.0 + 273.15,      # K
    "P": 10.0 * 1e5,         # Pa
    "flow": 500.0,           # kmol/hr total DES pseudo-component
}

# Fraction of total DES flow that is fresh makeup.  The remainder is supplied
# by the flash-bottom recycle stream.
MAKEUP_FRACTION = 0.05

# Optional inert gas (e.g., N2). Set ID to None or empty string to disable.
INERT = {
    "ID": None,              # e.g. "N2"
    "flow": 0.0,             # kmol/hr
}

COLUMN = {
    "N_stages": 3,
}

FLASH = {
    "T": 100.0 + 273.15,     # K
    "P": 0.5 * 1e5,          # Pa
}

# Regeneration target: maximum water mole fraction in the regenerated DES
# liquid leaving the flash.  If the baseline run does not meet the target, the
# script performs a bounded search on flash pressure and then flash temperature.
REGENERATION_TARGET = {
    "max_water_molefrac": 0.02,
    "adjust_flash_P": True,
    "P_min_bar": 0.05,
    "P_step_bar": 0.1,
    "adjust_flash_T": True,
    "T_max_C": 150.0,
    "T_step_C": 10.0,
}

# Target dry CO2 water mole fraction.  If the baseline run does not meet the
# target, the script automatically increases N_stages and/or total DES flow
# within the limits below.  Set to None to disable target-seeking.
TARGET = {
    "max_water_molefrac": None,   # e.g. 0.001 for 0.1 mol% water
    "adjust_N_stages": True,
    "max_N_stages": 15,
    "adjust_DES_flow": True,
    "max_DES_flow": 1500.0,  # kmol/hr
}

# Absorber convergence options.
OPTIMIZATION = {
    "use_cache": True,
    "tolerance": 1e-2,
    "relative_tolerance": 1e-2,
    "maxiter": 15,
}

# Recycle loop convergence options.
RECYCLE = {
    "tolerance": 1e-6,
    "maxiter": 100,
}

# Feasibility scan configuration (V2: 1 bar absorber feasibility).
# When enabled, the script skips the single-point baseline run and performs a
# brute-force grid scan over N_stages x DES_total_flow at a fixed column
# pressure P_column.  Default grid is coarse for quick turnaround.
FEASIBILITY_SCAN = {
    "enabled": False,
    "P_column": 1.0 * 1e5,          # Pa (fixed absorber pressure during scan)
    "N_stages_min": 3,
    "N_stages_max": 12,
    "N_stages_step": 2,
    "DES_flow_min": 500.0,          # kmol/hr
    "DES_flow_max": 1500.0,
    "DES_flow_step": 250.0,
    # Dry-gas target (water mole fraction). Set to None to skip feasibility check.
    "dry_gas_max_water": 0.001,     # 0.1 mol%
    # Regeneration target (water mole fraction in flash liquid).
    "regen_max_water": 0.001,       # 0.1 mol%
    # If True, each grid point also runs the flash T/P target-seeking loop
    # from REGENERATION_TARGET before recording metrics.
    "seek_regen_per_point": False,
}

# Sensitivity analysis configuration (OAT).  Each variable list should include
# its baseline value so that the response can be read directly from the CSV.
SENSITIVITY = {
    "enabled": False,
    "variables": {
        "N_stages": [3, 5],
        "DES_total_flow": [500.0, 600.0],
        "P_column": [10.0e5, 12.0e5],
        "T_gas": [40.0 + 273.15, 50.0 + 273.15],
        "x_water": [0.05, 0.06],
        "T_flash": [100.0 + 273.15, 120.0 + 273.15],
        "P_flash": [0.5e5, 0.2e5],
        "makeup_fraction": [0.05, 0.10],
    },
}


def _apply_cp_polynomial(chem: tmo.Chemical, coeffs: list[float], Tmin: float, Tmax: float) -> None:
    """Apply a Cp polynomial to a Chemical's Cn handle."""
    def cp_model(T):
        return sum(c * (T ** i) for i, c in enumerate(coeffs))

    phase = getattr(chem, "_locked_state", None) or chem._phase_ref
    cn_handle = getattr(chem.Cn, phase, chem.Cn)
    cn_handle.add_method(cp_model, Tmin=Tmin, Tmax=Tmax)


def _patch_co2_liquid_cp(co2: tmo.Chemical) -> None:
    """Allow CO2 liquid Cp to be evaluated above its critical temperature."""
    co2.Cn.l.add_method(lambda T: co2.Cn.g(T), Tmin=216.59, Tmax=1000.0)


def _load_chemicals(data: dict[str, Any], inert_id: str | None = None) -> tmo.Chemicals:
    """Load chemicals from YAML and register COSMO-SAC profiles."""
    chemicals_spec = {"chemicals": data["des_dehydration_data"]["chemicals"]}
    tmp_yaml = OUTPUT_DIR / RUN_ID / "_chemicals.yml"
    tmp_yaml.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_yaml, "w") as f:
        yaml.dump(chemicals_spec, f, default_flow_style=False, sort_keys=False)

    chemicals = tmo.load_chemicals_from_yaml(str(tmp_yaml))

    cp_range = data["des_dehydration_data"].get("cp_temperature_range", {"Tmin": 298.15, "Tmax": 400.0})
    Tmin = cp_range["Tmin"]
    Tmax = cp_range["Tmax"]
    for ID, spec in chemicals_spec["chemicals"].items():
        coeffs = spec.get("cp_polynomial")
        if coeffs:
            chem = chemicals[ID]
            _apply_cp_polynomial(chem, coeffs, Tmin, Tmax)

    if inert_id:
        inert_chem = tmo.Chemical(inert_id)
        inert_name = (inert_chem.common_name or inert_chem.ID).lower()
        from thermosteam.equilibrium.fast_sigma import estimate_sigma_profiles
        try:
            estimate_sigma_profiles([inert_chem])
        except KeyError as exc:
            raise RuntimeError(
                f"Inert gas '{inert_id}' has no COSMO-SAC sigma profile. "
                f"Add it to cosmosac_database.json (key '{inert_name}') via "
                f"compound-to-sigma before running with an inert."
            ) from exc
        chemicals = tmo.Chemicals([*chemicals, inert_chem])

    return chemicals


def load_and_configure_thermo(data: dict[str, Any], inert_id: str | None) -> tmo.Chemicals:
    """Register chemicals and set the thermo backend to Clapeyron (V2 only)."""
    try:
        tmo.settings.thermo_backend = "clapeyron"
    except Exception as exc:
        raise RuntimeError(
            "V2 requires the Clapeyron backend. "
            "Install pyclapeyron / Julia / Clapeyron.jl or use the V1 template."
        ) from exc

    tmo.settings.thermo_safeguards = False
    chemicals = _load_chemicals(data, inert_id=inert_id)
    _patch_co2_liquid_cp(chemicals["CO2"])
    chemicals.compile(skip_checks=True)
    tmo.settings.set_thermo(chemicals)
    return chemicals


def compute_metrics(state: "ProcessState") -> dict[str, float]:
    """Compute process metrics from the converged flowsheet."""
    gas_feed = state.gas_feed
    dry_co2 = state.absorber.outs[0]
    rich_des = state.absorber.outs[1]
    flash_vapor = state.flash.outs[0]
    regenerated_des = state.flash.outs[1]
    recycle = state.recycle

    water_in = gas_feed.imol["Water"]
    water_out = dry_co2.imol["Water"]
    water_removed = water_in - water_out
    removal = water_removed / water_in if water_in > 0 else 0.0

    co2_in = gas_feed.imol["CO2"]
    co2_out = dry_co2.imol["CO2"]
    co2_loss = co2_in - co2_out

    dry_co2_flow = dry_co2.F_mol
    water_molefrac_out = water_out / dry_co2_flow if dry_co2_flow > 0 else 0.0

    rich_des_flow = rich_des.F_mol

    regen_des_flow = regenerated_des.F_mol
    regen_water_molefrac = (
        regenerated_des.imol["Water"] / regen_des_flow if regen_des_flow > 0 else 0.0
    )

    recycle_des_flow = recycle.F_mol
    recycle_water_molefrac = (
        recycle.imol["Water"] / recycle_des_flow if recycle_des_flow > 0 else 0.0
    )

    water_in_rich_des = rich_des.imol["Water"]
    water_recovery = (
        flash_vapor.imol["Water"] / water_in_rich_des if water_in_rich_des > 0 else 0.0
    )

    return {
        "removal": removal,
        "water_molefrac_out": water_molefrac_out,
        "water_removed": water_removed,
        "co2_loss": co2_loss,
        "co2_loss_fraction": co2_loss / co2_in if co2_in > 0 else 0.0,
        "dry_co2_flow": dry_co2_flow,
        "rich_des_flow": rich_des_flow,
        "regen_des_flow": regen_des_flow,
        "regen_water_molefrac": regen_water_molefrac,
        "recycle_des_flow": recycle_des_flow,
        "recycle_water_molefrac": recycle_water_molefrac,
        "water_recovery": water_recovery,
        "flash_T": state.flash.T,
        "flash_P": state.flash.P,
        "recycle_iterations": state.system.recycle_iterations
            if hasattr(state.system, "recycle_iterations") else 0,
    }


class ProcessState:
    """Mutable container for the process state used by the sensitivity model."""

    _next_instance_id = 1

    def __init__(
        self,
        chemicals: tmo.Chemicals,
        inert_id: str | None,
        inert_flow: float,
        gas_spec: dict[str, float],
        absorbent_spec: dict[str, float],
        des_id: str,
        makeup_fraction: float,
        flash_spec: dict[str, float],
        N_stages: int | None = None,
    ):
        self._instance_id = ProcessState._next_instance_id
        ProcessState._next_instance_id += 1

        self.chemicals = chemicals
        self.inert_id = inert_id
        self.inert_flow = inert_flow
        self.gas_spec = gas_spec
        self.absorbent_spec = absorbent_spec
        self.des_id = des_id
        self.makeup_fraction = makeup_fraction
        self.flash_T = flash_spec["T"]
        self.flash_P = flash_spec["P"]
        self.gas_total_flow = gas_spec["flow"] + inert_flow

        # Baseline operating point
        self.N_stages = N_stages if N_stages is not None else COLUMN["N_stages"]
        self.des_total_flow = absorbent_spec["flow"]
        self.P = gas_spec["P"]
        self.T_gas = gas_spec["T"]
        self.x_water = (
            gas_spec["flow"] * gas_spec["Water"] / self.gas_total_flow
            if self.gas_total_flow > 0 else 0.0
        )

        # Mutable references updated by build().  Typed as Any because the
        # BioSTEAM stubs do not expose all unit/stream attributes we need.
        self.system: Any = None
        self.gas_feed: Any = None
        self.fresh_des: Any = None
        self.recycle: Any = None
        self.mixer: Any = None
        self.absorber: Any = None
        self.flash: Any = None
        self.splitter: Any = None
        self.model: Any = None

    def _gas_feed_kwargs(self) -> dict[str, Any]:
        co2_flow = self.gas_total_flow * (1.0 - self.x_water) - self.inert_flow
        water_flow = self.gas_total_flow * self.x_water
        kwargs = {
            "T": self.T_gas,
            "P": self.P,
            "units": "kmol/hr",
            "CO2": co2_flow,
            "Water": water_flow,
            "phase": "g",
        }
        if self.inert_id:
            kwargs[self.inert_id] = self.inert_flow
        return kwargs

    def _update_recycle_guess(self) -> None:
        """Set the tear stream initial guess for the recycle loop."""
        if self.recycle is None:
            return
        recycle_flow = self.des_total_flow * (1.0 - self.makeup_fraction)
        self.recycle.imol[self.des_id] = recycle_flow
        # Small residual water helps convergence; will be overwritten by the
        # tear stream solver in any case.
        self.recycle.imol["Water"] = recycle_flow * 0.001
        # The tear stream leaves the flash at flash conditions.
        self.recycle.T = self.flash_T
        self.recycle.P = self.flash_P
        self.recycle.phase = "l"

    def build(self) -> None:
        """Create fresh streams, units, and system from the current state."""
        n = self._instance_id

        self.gas_feed = bst.Stream(f"gas_feed_{n}", **self._gas_feed_kwargs())

        fresh_flow = self.des_total_flow * self.makeup_fraction
        self.fresh_des = bst.Stream(
            f"fresh_des_{n}",
            T=self.absorbent_spec["T"],
            P=self.absorbent_spec["P"],
            units="kmol/hr",
            **{self.des_id: fresh_flow},
            phase="l",
        )

        # Tear stream: splitter recycle outlet (also mixer inlet).
        self.recycle = bst.Stream(f"recycle_{n}")
        self._update_recycle_guess()

        self.mixer = ConditionedMixer(
            f"mixer_{n}",
            ins=[self.fresh_des, self.recycle],
            outlet_T=self.absorbent_spec["T"],
            outlet_P=self.P,
        )

        # Explicit product streams keep the absorber top as vapor and bottom
        # as liquid.  Without this, BioSTEAM may create a multi-phase
        # SuperpositionOutlet for the bottom product and hot_start fails on
        # later system simulations.
        dry_co2_product = bst.Stream(f"dry_CO2_{n}", phase="g")
        rich_des_product = bst.Stream(f"rich_DES_{n}", phase="l")

        self.absorber = bst.units.MultiStageEquilibrium(
            f"absorber_{n}",
            N_stages=self.N_stages,
            ins=[self.gas_feed, self.mixer.outs[0]],
            outs=[dry_co2_product, rich_des_product],
            phases=("g", "l"),
            feed_stages=(-1, 0),
            P=self.P,
            algorithms=("sequential modular",),
            maxiter=OPTIMIZATION.get("maxiter", 15),
            max_attempts=5,
            use_cache=OPTIMIZATION.get("use_cache", True),
        )
        self.absorber.tolerance = OPTIMIZATION.get("tolerance", 1e-2)
        self.absorber.relative_tolerance = OPTIMIZATION.get("relative_tolerance", 1e-2)

        self.flash = bst.units.Flash(
            f"flash_{n}",
            ins=rich_des_product,
            outs=[f"flash_vapor_{n}", f"flash_liquid_{n}"],
            P=self.flash_P,
            T=self.flash_T,
        )

        # Splitter closes the DES mass balance: only (1 - makeup_fraction) of
        # the regenerated flash liquid is recycled; the remainder is a purge
        # product equal to the fresh makeup flow.
        self.splitter = bst.units.Splitter(
            f"splitter_{n}",
            ins=self.flash.outs[1],
            outs=[self.recycle, f"purge_{n}"],
            split=1.0 - self.makeup_fraction,
        )

        self.system = bst.System(
            f"des_regen_{n}",
            path=[self.mixer, self.absorber, self.flash, self.splitter],
            recycle=self.recycle,
            maxiter=RECYCLE.get("maxiter", 100),
            molar_tolerance=RECYCLE.get("tolerance", 1e-6),
        )
        self.system.simulate()

        if self.model is not None:
            self.model._system = self.system

    def set_N_stages(self, N: float) -> None:
        N_int = int(round(N))
        if self.N_stages == N_int and self.system is not None:
            return
        self.N_stages = N_int
        self.build()

    def set_DES_total_flow(self, flow: float) -> None:
        if self.des_total_flow == flow:
            return
        self.des_total_flow = flow
        if self.fresh_des is not None:
            self.fresh_des.imol[self.des_id] = flow * self.makeup_fraction
        self._update_recycle_guess()

    def set_makeup_fraction(self, frac: float) -> None:
        if self.makeup_fraction == frac:
            return
        self.makeup_fraction = frac
        if self.fresh_des is not None:
            self.fresh_des.imol[self.des_id] = self.des_total_flow * frac
        if self.splitter is not None:
            self.splitter.split = 1.0 - frac
        self._update_recycle_guess()

    def set_P(self, P: float) -> None:
        if self.P == P and self.system is not None:
            return
        self.P = P
        self.build()

    def set_T_gas(self, T: float) -> None:
        if self.T_gas == T:
            return
        self.T_gas = T
        if self.gas_feed is not None:
            self.gas_feed.T = T

    def set_x_water(self, x: float) -> None:
        if self.x_water == x:
            return
        self.x_water = x
        if self.gas_feed is None:
            return
        co2_flow = self.gas_total_flow * (1.0 - x) - self.inert_flow
        water_flow = self.gas_total_flow * x
        flows = [co2_flow, water_flow]
        IDs = ["CO2", "Water"]
        if self.inert_id:
            flows.append(self.inert_flow)
            IDs.append(self.inert_id)
        self.gas_feed.set_flow(flows, "kmol/hr", IDs)

    def set_flash_T(self, T: float) -> None:
        if self.flash_T == T and self.system is not None:
            return
        self.flash_T = T
        self.build()

    def set_flash_P(self, P: float) -> None:
        if self.flash_P == P and self.system is not None:
            return
        self.flash_P = P
        self.build()


def _make_state_for_sensitivity(
    baseline: ProcessState,
    param_name: str,
    value: float,
) -> ProcessState:
    """Build a fresh ProcessState for one sensitivity evaluation."""
    gas_spec = dict(baseline.gas_spec)
    absorbent_spec = dict(baseline.absorbent_spec)
    flash_spec = {"T": baseline.flash_T, "P": baseline.flash_P}
    N_stages = baseline.N_stages
    makeup_fraction = baseline.makeup_fraction

    if param_name == "N_stages":
        N_stages = int(round(value))
    elif param_name == "DES_total_flow":
        absorbent_spec["flow"] = float(value)
    elif param_name == "P_column":
        gas_spec["P"] = float(value)
        absorbent_spec["P"] = float(value)
    elif param_name == "T_gas":
        gas_spec["T"] = float(value)
    elif param_name == "x_water":
        x = float(value)
        gas_spec["CO2"] = 1.0 - x
        gas_spec["Water"] = x
    elif param_name == "T_flash":
        flash_spec["T"] = float(value)
    elif param_name == "P_flash":
        flash_spec["P"] = float(value)
    elif param_name == "makeup_fraction":
        makeup_fraction = float(value)
    else:
        raise ValueError(f"Unknown sensitivity parameter: {param_name}")

    return ProcessState(
        baseline.chemicals,
        baseline.inert_id,
        baseline.inert_flow,
        gas_spec,
        absorbent_spec,
        baseline.des_id,
        makeup_fraction,
        flash_spec,
        N_stages=N_stages,
    )


def _print_sensitivity_table(results: list[dict], metric_names: list[str]) -> None:
    """Print a simple ASCII table of sensitivity results."""
    columns = ["parameter", "value"] + metric_names
    widths = [max(len(str(row.get(col, ""))) for row in results + [{col: col}]) for col in columns]
    header = " | ".join(col.ljust(w) for col, w in zip(columns, widths))
    print("\nSensitivity results:")
    print(header)
    print("-" * len(header))
    for row in results:
        print(" | ".join(str(row.get(col, "")).ljust(w) for col, w in zip(columns, widths)))


def run_sensitivity_analysis(state: ProcessState, run_dir: Path) -> None:
    """Run one-at-a-time sensitivity and write ``sensitivity.csv``."""
    print("\n" + "=" * 60)
    print("Sensitivity analysis (one-at-a-time)")
    print("=" * 60)

    variable_map = SENSITIVITY.get("variables", {})
    metric_names = ["water_removal", "dry_CO2_water_molefrac", "regen_DES_water_molefrac"]
    results: list[dict[str, Any]] = []

    for param_name, values in variable_map.items():
        if not values:
            print(f"  Skipping {param_name}: no values configured")
            continue
        print(f"\nSweeping {param_name}...")
        for value in values:
            trial = _make_state_for_sensitivity(state, param_name, value)
            trial.build()
            metrics = compute_metrics(trial)
            row = {"parameter": param_name, "value": value}
            for name in metric_names:
                row[name] = metrics[_METRIC_KEY_MAP[name]]
            results.append(row)
            print(
                f"  {param_name} = {value:.6g} -> "
                + ", ".join(f"{name} = {row[name]:.6g}" for name in metric_names)
            )

    df = pd.DataFrame(results)
    csv_path = run_dir / "sensitivity.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nWrote sensitivity results to {csv_path}")
    _print_sensitivity_table(results, metric_names)


_METRIC_KEY_MAP = {
    "water_removal": "removal",
    "dry_CO2_water_molefrac": "water_molefrac_out",
    "regen_DES_water_molefrac": "regen_water_molefrac",
}


def _write_brief(
    run_dir: Path,
    data: dict[str, Any],
    inert_id: str | None,
    metrics: dict[str, float],
    state: ProcessState,
    target_note: str,
    regen_target_note: str,
) -> Path:
    """Write the Markdown summary to ``brief.md``."""
    brief_path = run_dir / "brief.md"
    dry_co2 = state.absorber.outs[0]
    rich_des = state.absorber.outs[1]
    flash_vapor = state.flash.outs[0]
    regenerated_des = state.flash.outs[1]
    recycle = state.recycle
    purge = state.splitter.outs[1]
    mixer_out = state.mixer.outs[0]

    with open(brief_path, "w") as f:
        f.write("# DES Dehydration-Regeneration Base Template — Results\n\n")
        f.write(f"**DES**: choline chloride / glycerol (1:{data['des_dehydration_data']['hba_hbd_mole_ratio']})\n\n")
        f.write("**Gas feed**: ")
        f.write(f"{GAS_FEED['flow']:.1f} kmol/hr CO2/H2O, ")
        f.write(f"{GAS_FEED['CO2']*100:.1f}% CO2 / {GAS_FEED['Water']*100:.1f}% H2O")
        if inert_id:
            f.write(f" + {INERT['flow']:.1f} kmol/hr {inert_id}")
        f.write(f", {GAS_FEED['T']-273.15:.1f} C, {GAS_FEED['P']/1e5:.1f} bar\n\n")
        f.write(f"**Total DES flow**: {ABSORBENT['flow']:.1f} kmol/hr, ")
        f.write(f"makeup fraction = {MAKEUP_FRACTION:.2f}, ")
        f.write(f"fresh makeup = {ABSORBENT['flow'] * MAKEUP_FRACTION:.1f} kmol/hr\n\n")
        f.write(f"**Column**: {COLUMN['N_stages']} equilibrium stages (rigorous COSMOSAC)\n\n")
        f.write(f"**Flash**: {metrics['flash_T']-273.15:.1f} C, {metrics['flash_P']/1e5:.2f} bar\n\n")

        f.write("## Key metrics\n\n")
        f.write(f"- Dry CO2 flow: {metrics['dry_co2_flow']:.2f} kmol/hr\n")
        f.write(f"- Dry CO2 water mole fraction: {metrics['water_molefrac_out']:.6f}\n")
        f.write(f"- Water removed: {metrics['water_removed']:.2f} kmol/hr ({metrics['removal']:.2%})\n")
        f.write(f"- CO2 loss to DES: {metrics['co2_loss']:.2f} kmol/hr ({metrics['co2_loss_fraction']:.2%})\n")
        f.write(f"- Rich DES flow: {metrics['rich_des_flow']:.2f} kmol/hr\n")
        f.write(f"- Regenerated DES flow: {metrics['regen_des_flow']:.2f} kmol/hr\n")
        f.write(f"- Regenerated DES water mole fraction: {metrics['regen_water_molefrac']:.6f}\n")
        f.write(f"- Recycle DES flow: {metrics['recycle_des_flow']:.2f} kmol/hr\n")
        f.write(f"- Recycle DES water mole fraction: {metrics['recycle_water_molefrac']:.6f}\n")
        f.write(f"- Flash water recovery: {metrics['water_recovery']:.2%}\n")
        f.write(f"- Recycle convergence iterations: {metrics['recycle_iterations']}\n")
        f.write(f"- Dry-CO2 target: {target_note}\n")
        f.write(f"- Regeneration target: {regen_target_note}\n")
        f.write(f"- Generated script: {(run_dir / 'process.py').resolve()}\n\n")

        f.write("## Stream summary\n\n")
        f.write("### Dry CO2\n\n")
        f.write(f"```\n{dry_co2.get_flow('kmol/hr')}\n```\n\n")
        f.write("### Mixer outlet (to absorber)\n\n")
        f.write(f"```\n{mixer_out.get_flow('kmol/hr')}\n```\n\n")
        f.write("### Rich DES (to flash)\n\n")
        f.write(f"```\n{rich_des.get_flow('kmol/hr')}\n```\n\n")
        f.write("### Flash vapor\n\n")
        f.write(f"```\n{flash_vapor.get_flow('kmol/hr')}\n```\n\n")
        f.write("### Regenerated DES (before split)\n\n")
        f.write(f"```\n{regenerated_des.get_flow('kmol/hr')}\n```\n\n")
        f.write("### Recycle DES (to mixer)\n\n")
        f.write(f"```\n{recycle.get_flow('kmol/hr')}\n```\n\n")
        f.write("### Purge DES (product)\n\n")
        f.write(f"```\n{purge.get_flow('kmol/hr')}\n```\n\n")

        f.write("## Caveats\n\n")
        f.write("- V2 is rigorous-mode only; both absorber and flash use COSMOSAC2013 via Clapeyron.\n")
        f.write("- DES regeneration is modeled as a single isothermal flash; pumps, heat exchangers,\n")
        f.write("  compressors, and valves are not included.\n")
        f.write("- A splitter divides the regenerated flash liquid into a recycle stream and a purge\n")
        f.write("  stream equal to the fresh DES makeup, closing the solvent mass balance.\n")
        f.write("- Critical properties for the DES pseudo-component are estimates.\n")
        f.write("- Clapeyron falls back to BasicIdeal for the DES pure model because the\n")
        f.write("  estimated critical properties are outside the Peng-Robinson correlation range.\n")
        f.write("- CO2 liquid heat capacity is patched to use the gas Cp above the normal\n")
        f.write("  liquid range so the supercritical CO2 enthalpy model does not fail.\n")
        f.write("- Sequential modular convergence is used; other algorithms may not converge\n")
        f.write("  for this supercritical CO2 / heavy DES system.\n")
        if SENSITIVITY["enabled"]:
            f.write(f"- One-at-a-time sensitivity results saved to ``{run_dir / 'sensitivity.csv'}``.\n")
    return brief_path


def _seek_dry_co2_target(
    chemicals: tmo.Chemicals,
    inert_id: str | None,
    inert_flow: float,
    des_id: str,
    state: ProcessState,
    metrics: dict[str, float],
) -> tuple[bool, str, ProcessState, dict[str, float]]:
    """Adjust operating variables until the dry-CO2 water target is met."""
    target = TARGET.get("max_water_molefrac")
    if target is None:
        return True, "No target specified.", state, metrics

    current = metrics["water_molefrac_out"]
    if current <= target:
        return True, f"Target met (<= {target:.6f}).", state, metrics

    if not TARGET.get("adjust_N_stages") and not TARGET.get("adjust_DES_flow"):
        return False, f"Target not met ({current:.6f} > {target:.6f}); no adjustment enabled.", state, metrics

    original_N = state.N_stages
    original_des_flow = state.des_total_flow
    final_state = state
    final_metrics = metrics

    if TARGET.get("adjust_N_stages"):
        max_N = TARGET["max_N_stages"]
        for N in range(original_N + 1, max_N + 1):
            print(f"\nTarget-seeking: trying N_stages = {N}...")
            trial_state = ProcessState(
                chemicals,
                inert_id,
                inert_flow,
                state.gas_spec,
                state.absorbent_spec,
                des_id,
                state.makeup_fraction,
                {"T": state.flash_T, "P": state.flash_P},
                N_stages=N,
            )
            trial_state.build()
            trial_metrics = compute_metrics(trial_state)
            current = trial_metrics["water_molefrac_out"]
            print(f"  dry CO2 water mole fraction = {current:.6f}")
            if current <= target:
                return True, f"Target met by increasing N_stages to {N}.", trial_state, trial_metrics
            final_state = trial_state
            final_metrics = trial_metrics

    if TARGET.get("adjust_DES_flow"):
        max_flow = TARGET["max_DES_flow"]
        current_N = final_state.N_stages
        for flow in range(int(original_des_flow) + 100, int(max_flow) + 1, 100):
            print(f"\nTarget-seeking: trying DES total flow = {flow} kmol/hr...")
            absorbent_spec = dict(state.absorbent_spec, flow=float(flow))
            trial_state = ProcessState(
                chemicals,
                inert_id,
                inert_flow,
                state.gas_spec,
                absorbent_spec,
                des_id,
                state.makeup_fraction,
                {"T": state.flash_T, "P": state.flash_P},
                N_stages=current_N,
            )
            trial_state.build()
            trial_metrics = compute_metrics(trial_state)
            current = trial_metrics["water_molefrac_out"]
            print(f"  dry CO2 water mole fraction = {current:.6f}")
            if current <= target:
                return True, f"Target met by increasing DES total flow to {flow} kmol/hr.", trial_state, trial_metrics
            final_state = trial_state
            final_metrics = trial_metrics

    return False, f"Target not met ({current:.6f} > {target:.6f}) within adjustment limits.", final_state, final_metrics


def _seek_regeneration_target(
    chemicals: tmo.Chemicals,
    inert_id: str | None,
    inert_flow: float,
    des_id: str,
    state: ProcessState,
    metrics: dict[str, float],
) -> tuple[bool, str, ProcessState, dict[str, float]]:
    """Adjust flash P then flash T until the regenerated-DES water target is met."""
    target = REGENERATION_TARGET.get("max_water_molefrac")
    if target is None:
        return True, "No regeneration target specified.", state, metrics

    current = metrics["regen_water_molefrac"]
    if current <= target:
        return True, f"Target met (<= {target:.6f}).", state, metrics

    if not REGENERATION_TARGET.get("adjust_flash_P") and not REGENERATION_TARGET.get("adjust_flash_T"):
        return False, f"Target not met ({current:.6f} > {target:.6f}); no adjustment enabled.", state, metrics

    baseline_P_bar = state.flash_P / 1e5
    baseline_T_C = state.flash_T - 273.15
    final_state = state
    final_metrics = metrics

    if REGENERATION_TARGET.get("adjust_flash_P"):
        P_min = REGENERATION_TARGET["P_min_bar"]
        P_step = REGENERATION_TARGET["P_step_bar"]
        P = baseline_P_bar - P_step
        while P >= P_min - 1e-9:
            print(f"\nRegeneration target-seeking: trying flash P = {P:.2f} bar...")
            trial_state = ProcessState(
                chemicals,
                inert_id,
                inert_flow,
                state.gas_spec,
                state.absorbent_spec,
                des_id,
                state.makeup_fraction,
                {"T": state.flash_T, "P": P * 1e5},
                N_stages=state.N_stages,
            )
            trial_state.build()
            trial_metrics = compute_metrics(trial_state)
            current = trial_metrics["regen_water_molefrac"]
            print(f"  regenerated DES water mole fraction = {current:.6f}")
            if current <= target:
                return True, f"Target met by decreasing flash P to {P:.2f} bar.", trial_state, trial_metrics
            final_state = trial_state
            final_metrics = trial_metrics
            P -= P_step

    if REGENERATION_TARGET.get("adjust_flash_T"):
        T_max = REGENERATION_TARGET["T_max_C"]
        T_step = REGENERATION_TARGET["T_step_C"]
        T = baseline_T_C + T_step
        while T <= T_max + 1e-9:
            print(f"\nRegeneration target-seeking: trying flash T = {T:.1f} C...")
            trial_state = ProcessState(
                chemicals,
                inert_id,
                inert_flow,
                state.gas_spec,
                state.absorbent_spec,
                des_id,
                state.makeup_fraction,
                {"T": T + 273.15, "P": state.flash_P},
                N_stages=state.N_stages,
            )
            trial_state.build()
            trial_metrics = compute_metrics(trial_state)
            current = trial_metrics["regen_water_molefrac"]
            print(f"  regenerated DES water mole fraction = {current:.6f}")
            if current <= target:
                return True, f"Target met by increasing flash T to {T:.1f} C.", trial_state, trial_metrics
            final_state = trial_state
            final_metrics = trial_metrics
            T += T_step

    return False, f"Target not met ({current:.6f} > {target:.6f}) within adjustment limits.", final_state, final_metrics



# ---------------------------------------------------------------------------
# Feasibility scan
# ---------------------------------------------------------------------------

def run_feasibility_scan(
    chemicals: tmo.Chemicals,
    inert_id: str | None,
    inert_flow: float,
    des_id: str,
    gas_spec: dict[str, float],
    absorbent_spec: dict[str, float],
    makeup_fraction: float,
    flash_spec: dict[str, float],
    grid: dict[str, Any],
) -> pd.DataFrame:
    """Brute-force grid scan over N_stages x DES_total_flow at fixed P_column.

    Parameters
    ----------
    grid : dict with keys:
        P_column : float      — fixed absorber pressure (Pa)
        N_stages_min, _max, _step : int
        DES_flow_min, _max, _step : float
        seek_regen_per_point : bool — run flash T/P search at each point

    Returns
    -------
    DataFrame with one row per grid point.
    """
    P_column = grid["P_column"]
    N_min = grid["N_stages_min"]
    N_max = grid["N_stages_max"]
    N_step = grid["N_stages_step"]
    f_min = grid["DES_flow_min"]
    f_max = grid["DES_flow_max"]
    f_step = grid["DES_flow_step"]
    seek_regen = grid.get("seek_regen_per_point", False)

    N_values = range(N_min, N_max + 1, N_step)
    f_vals: list[float] = []
    fv = f_min
    while fv <= f_max + 1e-9:
        f_vals.append(fv)
        fv += f_step

    total = len(N_values) * len(f_vals)
    print(f"\nFeasibility scan: {len(N_values)} N_stages x {len(f_vals)} DES_flow = {total} points")
    print(f"  Column P = {P_column / 1e5:.1f} bar")
    print(f"  N_stages: {list(N_values)}")
    print(f"  DES_total_flow: {f_vals}")
    if seek_regen:
        print("  Flash T/P target-seeking: ENABLED per point")

    rows: list[dict[str, Any]] = []
    for N in N_values:
        for des_flow in f_vals:
            print(f"\n--- Scan point: N_stages={N}, DES_total_flow={des_flow:.0f} kmol/hr ---")
            try:
                # Adjust absorbent spec for this point's DES flow
                point_absorbent = dict(absorbent_spec, flow=des_flow)
                point_flash = dict(flash_spec)

                # Use the grid's P_column as the absorber pressure
                point_gas = dict(gas_spec, P=P_column)

                state = ProcessState(
                    chemicals,
                    inert_id,
                    inert_flow,
                    point_gas,
                    point_absorbent,
                    des_id,
                    makeup_fraction=makeup_fraction,
                    flash_spec=point_flash,
                    N_stages=N,
                )
                state.build()

                # Optional: run regeneration target-seeking per point
                if seek_regen and REGENERATION_TARGET.get("max_water_molefrac") is not None:
                    metrics = compute_metrics(state)
                    _, _, state, metrics = _seek_regeneration_target(
                        chemicals, inert_id, inert_flow, des_id,
                        state, metrics,
                    )
                else:
                    metrics = compute_metrics(state)

                row = {
                    "N_stages": N,
                    "DES_total_flow": des_flow,
                    "P_column": P_column,
                    "converged": True,
                    "error": "",
                    "dry_co2_water_molefrac": metrics["water_molefrac_out"],
                    "regen_des_water_molefrac": metrics["regen_water_molefrac"],
                    "removal": metrics["removal"],
                    "co2_loss_fraction": metrics["co2_loss_fraction"],
                    "recycle_iterations": metrics["recycle_iterations"],
                }
                print(f"  dry CO2 H2O mole frac: {row['dry_co2_water_molefrac']:.6f}")
                print(f"  regen DES H2O mole frac: {row['regen_des_water_molefrac']:.6f}")
                print(f"  converged: True")

            except Exception as exc:
                row = {
                    "N_stages": N,
                    "DES_total_flow": des_flow,
                    "P_column": P_column,
                    "converged": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "dry_co2_water_molefrac": None,
                    "regen_des_water_molefrac": None,
                    "removal": None,
                    "co2_loss_fraction": None,
                    "recycle_iterations": None,
                }
                print(f"  FAILED: {row['error']}")

            rows.append(row)

    df = pd.DataFrame(rows)
    # Determine feasibility for each point
    dry_target = FEASIBILITY_SCAN.get("dry_gas_max_water")
    regen_target = FEASIBILITY_SCAN.get("regen_max_water")
    feas = [False] * len(df)
    for i, r in df.iterrows():
        if not r["converged"]:
            continue
        dry_ok = True if dry_target is None else (r["dry_co2_water_molefrac"] <= dry_target)
        regen_ok = True if regen_target is None else (r["regen_des_water_molefrac"] <= regen_target)
        feas[i] = dry_ok and regen_ok
    df["feasible"] = feas
    return df


def _write_feasibility_report(
    df: pd.DataFrame,
    run_dir: Path,
    grid: dict[str, Any],
    gas_spec: dict[str, float],
) -> Path:
    """Analyze the scan DataFrame and write feasibility.md + feasibility.csv."""
    csv_path = run_dir / "feasibility.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nWrote scan data to {csv_path}")

    dry_target = FEASIBILITY_SCAN.get("dry_gas_max_water")
    regen_target = FEASIBILITY_SCAN.get("regen_max_water")

    converged = df[df["converged"]]
    failed = df[~df["converged"]]
    feasible = converged[converged["feasible"]]

    lines: list[str] = []
    lines.append("# 1 bar Absorber Feasibility Scan — Report")
    lines.append("")
    lines.append(f"**Column pressure**: {grid.get('P_column', 0) / 1e5:.1f} bar")
    lines.append(f"**Gas feed**: {gas_spec.get('flow', 0):.0f} kmol/hr, "
                 f"{gas_spec.get('Water', 0)*100:.1f}% H2O at "
                 f"{gas_spec.get('T', 0) - 273.15:.0f} C")
    lines.append(f"**DES**: choline chloride / glycerol (2:1)")
    lines.append(f"**Flash**: {grid.get('flash_T_C', 100):.0f} C, "
                 f"{grid.get('flash_P_bar', 0.5):.2f} bar")
    lines.append("")

    N_range = f"{grid.get('N_stages_min', '?')} – {grid.get('N_stages_max', '?')}"
    F_range = f"{grid.get('DES_flow_min', '?'):.0f} – {grid.get('DES_flow_max', '?'):.0f} kmol/hr"
    lines.append(f"**Scan grid**: {len(converged)} converged / {len(df)} total "
                 f"(N_stages ∈ {{{N_range}}}, DES_total_flow ∈ {{{F_range}}})")
    if len(failed):
        lines.append(f"**Failed points**: {len(failed)} — see `feasibility.csv` for details.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Feasibility verdict")
    lines.append("")

    if len(feasible) > 0:
        # Select recommended point: min DES_total_flow, then min N_stages
        best = feasible.loc[
            feasible["DES_total_flow"].idxmin()
        ]
        # If multiple have the same flow, pick min N_stages
        min_flow = best["DES_total_flow"]
        candidates = feasible[feasible["DES_total_flow"] == min_flow]
        best = candidates.loc[candidates["N_stages"].idxmin()]

        lines.append("**FEASIBLE** — at least one grid point satisfies both targets.")
        lines.append("")
        lines.append("### Recommended operating point")
        lines.append("")
        lines.append(f"- **N_stages**: {int(best['N_stages'])}")
        lines.append(f"- **DES_total_flow**: {best['DES_total_flow']:.0f} kmol/hr")
        lines.append(f"- **Dry CO2 water mole fraction**: {best['dry_co2_water_molefrac']:.6f}")
        lines.append(f"- **Regen DES water mole fraction**: {best['regen_des_water_molefrac']:.6f}")
        lines.append(f"- **Water removal**: {best['removal']:.2%}")
        lines.append(f"- **Selection rule**: lowest DES flow, then fewest stages.")
    else:
        lines.append("**INFEASIBLE** — no grid point satisfies both targets simultaneously.")
        lines.append("")

        # Find min achievable values
        if len(converged) > 0:
            best_dry_row = converged.loc[converged["dry_co2_water_molefrac"].idxmin()]
            best_regen_row = converged.loc[converged["regen_des_water_molefrac"].idxmin()]

            lines.append("### Minimum achievable values within scan range")
            lines.append("")
            lines.append(f"- **Min dry CO2 water mole fraction**: "
                         f"{best_dry_row['dry_co2_water_molefrac']:.6f} "
                         f"(N_stages={int(best_dry_row['N_stages'])}, "
                         f"DES={best_dry_row['DES_total_flow']:.0f} kmol/hr)")
            lines.append(f"- **Min regen DES water mole fraction**: "
                         f"{best_regen_row['regen_des_water_molefrac']:.6f} "
                         f"(N_stages={int(best_regen_row['N_stages'])}, "
                         f"DES={best_regen_row['DES_total_flow']:.0f} kmol/hr)")
            lines.append("")

            lines.append("### Candidate constraints to relax")
            lines.append("")
            if dry_target is not None and best_dry_row["dry_co2_water_molefrac"] > dry_target:
                lines.append(f"- **Dry gas target** (current: {dry_target}): "
                             f"relax to ≥ {best_dry_row['dry_co2_water_molefrac']:.6f}")
            if regen_target is not None and best_regen_row["regen_des_water_molefrac"] > regen_target:
                lines.append(f"- **Regen DES target** (current: {regen_target}): "
                             f"relax to ≥ {best_regen_row['regen_des_water_molefrac']:.6f}")
            lines.append("- **Column pressure**: increase above 1 bar")
            lines.append(f"- **Flash pressure**: lower below {grid.get('flash_P_bar', 0.5):.2f} bar")
            lines.append(f"- **Flash temperature**: raise above {grid.get('flash_T_C', 100):.0f} C")
        else:
            lines.append("All grid points failed to converge — no data for bottleneck analysis.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Raw data")
    lines.append("")
    lines.append("See `feasibility.csv` for the full grid (all converged and failed points).")
    lines.append("")
    lines.append(f"- Converged: {len(converged)} / {len(df)}")
    lines.append(f"- Feasible: {len(feasible)}")
    lines.append(f"- Failed: {len(failed)}")
    lines.append("")

    md_path = run_dir / "feasibility.md"
    md_path.write_text("\n".join(lines))
    print(f"Wrote feasibility report to {md_path}")
    return md_path

def main() -> None:
    run_dir = OUTPUT_DIR / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "log.txt"

    class Tee:
        def __init__(self, *streams):
            self.streams = streams
        def write(self, data):
            for s in self.streams:
                s.write(data)
                s.flush()
        def flush(self):
            for s in self.streams:
                s.flush()

    log_file = open(log_path, "w")
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    try:
        print("=" * 60)
        print("DES dehydration-regeneration base template (V2)")
        print("=" * 60)

        print(f"Loading thermodynamic data from {DATA_PATH}")
        with open(DATA_PATH) as f:
            data = yaml.safe_load(f)

        inert_id = (INERT.get("ID") or "").strip() or None
        inert_flow = float(INERT.get("flow", 0.0) or 0.0)
        chemicals = load_and_configure_thermo(data, inert_id)

        des_id = "DES_choline_chloride_glycerol"
        if des_id not in chemicals.IDs:
            raise ValueError(f"DES pseudo-component '{des_id}' not found in chemical data")

        print(f"Chemicals: {chemicals.IDs}")
        print("V2: using rigorous Clapeyron/COSMOSAC backend for absorber and flash.")

        # Feasibility scan mode — skip single-point baseline
        if FEASIBILITY_SCAN.get("enabled"):
            print("\nFeasibility scan mode enabled — skipping single-point baseline.")
            scan_grid = dict(FEASIBILITY_SCAN)
            # Fill in flash conditions from the main config for the report
            scan_grid["flash_T_C"] = FLASH["T"] - 273.15
            scan_grid["flash_P_bar"] = FLASH["P"] / 1e5
            df = run_feasibility_scan(
                chemicals,
                inert_id,
                inert_flow,
                des_id,
                GAS_FEED,
                ABSORBENT,
                makeup_fraction=MAKEUP_FRACTION,
                flash_spec=FLASH,
                grid=scan_grid,
            )
            _write_feasibility_report(df, run_dir, scan_grid, GAS_FEED)
            print("\nFeasibility scan complete.")
            return

        print("Creating streams and building flowsheet...")
        state = ProcessState(
            chemicals,
            inert_id,
            inert_flow,
            GAS_FEED,
            ABSORBENT,
            des_id,
            makeup_fraction=MAKEUP_FRACTION,
            flash_spec=FLASH,
        )
        state.build()

        metrics = compute_metrics(state)

        print("\n" + "=" * 60)
        print("Baseline results")
        print("=" * 60)
        print(f"Dry CO2 flow: {metrics['dry_co2_flow']:.2f} kmol/hr")
        print(f"Dry CO2 water mole fraction: {metrics['water_molefrac_out']:.6f}")
        print(f"Water removed: {metrics['water_removed']:.2f} kmol/hr ({metrics['removal']:.2%})")
        print(f"CO2 loss to DES: {metrics['co2_loss']:.2f} kmol/hr ({metrics['co2_loss_fraction']:.2%})")
        print(f"Regenerated DES flow: {metrics['regen_des_flow']:.2f} kmol/hr")
        print(f"Regenerated DES water mole fraction: {metrics['regen_water_molefrac']:.6f}")
        print(f"Recycle DES flow: {metrics['recycle_des_flow']:.2f} kmol/hr")
        print(f"Recycle DES water mole fraction: {metrics['recycle_water_molefrac']:.6f}")
        print(f"Flash water recovery: {metrics['water_recovery']:.2%}")
        print(f"Recycle convergence iterations: {metrics['recycle_iterations']}")
        print("\nDry CO2 stream:")
        state.absorber.outs[0].show()
        print("\nRegenerated DES stream:")
        state.flash.outs[1].show()
        print("\nRecycle stream:")
        state.recycle.show()

        # Target-seeking loops
        target_met, target_note, state, metrics = _seek_dry_co2_target(
            chemicals, inert_id, inert_flow, des_id, state, metrics
        )
        regen_met, regen_target_note, state, metrics = _seek_regeneration_target(
            chemicals, inert_id, inert_flow, des_id, state, metrics
        )

        # Write brief
        brief_path = _write_brief(
            run_dir, data, inert_id, metrics, state, target_note, regen_target_note
        )

        # Copy this script into the output directory
        this_script = Path(__file__).resolve()
        shutil.copy2(this_script, run_dir / "process.py")

        print(f"\nWrote brief to {brief_path}")
        print(f"Wrote process script to {run_dir / 'process.py'}")

        # Optional sensitivity analysis
        if SENSITIVITY["enabled"]:
            run_sensitivity_analysis(state, run_dir)
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()


if __name__ == "__main__":
    main()
