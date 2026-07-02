#!/usr/bin/env amspython
"""Prepare thermodynamic data for the DES dehydration base template.

This script extracts COSMO-SAC sigma profiles from ADF coskf files,
generates critical properties via group contribution, predicts heat
capacities via the IK-CAPE ANN, and writes a single YAML file that the
simulation template can load.

Run with amspython (required for scm.plams / KFFile / CRSJob):

    amspython .claude/skills/biosteam-process-builder/templates/prepare_des_dehydration_data.py

Output:
    ../../inputs/des_dehydration_data.yml
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml

# Make compound_to_sigma importable
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
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "compound_to_sigma"))

from compound_to_sigma.clapeyron import extract_clapeyron_profile

SKILL_GC = SKILL_DIR.parent / "group-contribution-estimator"
SKILL_HC = SKILL_DIR.parent / "heat-capacity-ann"
JOBACK_SCRIPT = SKILL_GC / "scripts" / "joback_calculator.py"
CP_SCRIPT = SKILL_HC / "scripts" / "predict_cp.py"

OUTPUT_DIR = SKILL_DIR / "inputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "des_dehydration_data.yml"

# Source coskf files
GLYCEROL_COSKF = REPO_ROOT / "sigma_profiles_glycerol" / "glycerol" / "glycerol.coskf"
CO2_COSKF = REPO_ROOT / "sigma_profiles_co2" / "carbon dioxide" / "carbon dioxide.coskf"
WATER_COSKF = REPO_ROOT / "sigma_profiles" / "water" / "water.coskf"
ION_YAML = REPO_ROOT / "examples" / "choline_chloride_cosmosac.yml"

# DES formulation: choline chloride (HBA) : glycerol (HBD) = 1 : 2
HBA_HBD_MOLE_RATIO = 2.0

# Temperature range for Cp polynomial fit
CP_T_MIN = 298.15
CP_T_MAX = 400.0
CP_N_POINTS = 11


def _run_joback(smiles: str) -> dict[str, float]:
    """Run group-contribution estimator and return critical properties."""
    result = subprocess.run(
        [sys.executable, str(JOBACK_SCRIPT), smiles, "--unmatched"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    props = data["properties"]
    return {
        "MW": float(props["molecular_weight_g_mol"]),
        "Tb": float(props["normal_boiling_point_K"]),
        "Tc": float(props["critical_temperature_K"]),
        "Pc": float(props["critical_pressure_bar"]) * 1e5,  # bar -> Pa
        "Vc": float(props["critical_volume_cm3_mol"]) * 1e-6,  # cm3/mol -> m3/mol
        "omega": float(props["acentric_factor"]),
    }


def _predict_cp(props: dict[str, float], temperatures: list[float]) -> list[float]:
    """Predict Cp at given temperatures using the heat-capacity-ANN skill."""
    props_json = json.dumps(
        {
            "M": props["MW"],
            "Vc": props["Vc"] * 1e6,  # m3/mol -> cm3/mol
            "Tc": props["Tc"],
            "Pc": props["Pc"] / 1e5,  # Pa -> bar
            "omega": props["omega"],
        }
    )
    t_str = ",".join(str(t) for t in temperatures)
    result = subprocess.run(
        [sys.executable, str(CP_SCRIPT), "--properties", props_json, "--temperature", t_str],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return [p["Cp_J_K-1_mol-1"] for p in data["predictions"]]


def _fit_cp_polynomial(temperatures: list[float], cp_values: list[float], degree: int = 3) -> list[float]:
    """Fit Cp(T) polynomial and return coefficients [a0, a1, a2, ...].

    Cp = a0 + a1*T + a2*T**2 + ...
    """
    coeffs = np.polyfit(temperatures, cp_values, degree)[::-1].tolist()
    return coeffs


def _combine_ion_pair(cation: dict, anion: dict, name: str) -> dict:
    """Combine cation and anion profiles into a neutral ion-pair pseudo-component."""
    return {
        "name": name,
        "formula": cation["names"]["formula"] + anion["names"]["formula"],
        "A": cation["cosmo"]["A"] + anion["cosmo"]["A"],
        "V": cation["cosmo"]["V"] + anion["cosmo"]["V"],
        "Pnhb": [a + b for a, b in zip(cation["cosmo"]["Pnhb"], anion["cosmo"]["Pnhb"])],
        "POH": [a + b for a, b in zip(cation["cosmo"]["POH"], anion["cosmo"]["POH"])],
        "POT": [a + b for a, b in zip(cation["cosmo"]["POT"], anion["cosmo"]["POT"])],
    }


def _combine_binary_mixture(
    comp1: dict,
    comp2: dict,
    name: str,
    moles1: float,
    moles2: float,
    formula: str | None = None,
) -> dict:
    """Mole-fraction-weighted combination of two profiles."""
    total = moles1 + moles2
    x1 = moles1 / total
    x2 = moles2 / total
    return {
        "name": name,
        "formula": formula or f"{comp1['name']}_{comp2['name']}",
        "A": x1 * comp1["A"] + x2 * comp2["A"],
        "V": x1 * comp1["V"] + x2 * comp2["V"],
        "Pnhb": [x1 * a + x2 * b for a, b in zip(comp1["Pnhb"], comp2["Pnhb"])],
        "POH": [x1 * a + x2 * b for a, b in zip(comp1["POH"], comp2["POH"])],
        "POT": [x1 * a + x2 * b for a, b in zip(comp1["POT"], comp2["POT"])],
    }


def _combine_critical_properties(
    comp1: dict[str, float],
    comp2: dict[str, float],
    moles1: float,
    moles2: float,
) -> dict[str, float]:
    """Lee-Kesler style mixing of critical properties for a binary mixture."""
    total = moles1 + moles2
    x1 = moles1 / total
    x2 = moles2 / total

    # Cross parameters
    Tc12 = math.sqrt(comp1["Tc"] * comp2["Tc"])
    Vc12 = (1.0 / 8.0) * (comp1["Vc"] ** (1.0 / 3.0) + comp2["Vc"] ** (1.0 / 3.0)) ** 3

    Vc = x1**2 * comp1["Vc"] + x2**2 * comp2["Vc"] + 2 * x1 * x2 * Vc12
    Tc = (
        x1**2 * comp1["Tc"] * (comp1["Vc"] ** 0.25)
        + x2**2 * comp2["Tc"] * (comp2["Vc"] ** 0.25)
        + 2 * x1 * x2 * Tc12 * (Vc12 ** 0.25)
    ) / (Vc**0.25)
    omega = x1 * comp1["omega"] + x2 * comp2["omega"]
    Zc = 0.2905 - 0.085 * omega
    Pc = Zc * 8.314462618 * Tc / Vc  # Pa (using R = 8.314... J/mol/K)
    Tb = x1 * comp1["Tb"] + x2 * comp2["Tb"]
    MW = x1 * comp1["MW"] + x2 * comp2["MW"]

    return {
        "MW": MW,
        "Tb": Tb,
        "Tc": Tc,
        "Pc": Pc,
        "Vc": Vc,
        "omega": omega,
    }


def _ion_pair_critical_properties(
    cation_props: dict[str, float],
    anion_props: dict[str, float],
) -> dict[str, float]:
    """Approximate critical properties of a 1:1 ion pair from ion properties."""
    return {
        "MW": cation_props["MW"] + anion_props["MW"],
        "Tb": 0.5 * (cation_props["Tb"] + anion_props["Tb"]),
        "Tc": 0.5 * (cation_props["Tc"] + anion_props["Tc"]),
        "Pc": 0.5 * (cation_props["Pc"] + anion_props["Pc"]),
        "Vc": cation_props["Vc"] + anion_props["Vc"],
        "omega": 0.5 * (cation_props["omega"] + anion_props["omega"]),
    }


def _eval_polynomial(coeffs: list[float], T: float) -> float:
    """Evaluate Cp polynomial at temperature T."""
    return sum(c * (T ** i) for i, c in enumerate(coeffs))


def _build_chemical_yaml(
    ID: str,
    common_name: str,
    formula: str,
    props: dict[str, float],
    profile: dict,
    cp_coeffs: list[float],
    phase: str = "l",
) -> dict:
    """Build a thermosteam YAML chemical definition."""
    cp_ref = _eval_polynomial(cp_coeffs, CP_T_MIN)
    cp_ref = max(cp_ref, 1.0)  # guard against unphysical negative values
    vol_ref = props["Vc"] * (0.25 if phase == "l" else 1.0)
    return {
        "search_db": False,
        "phase": phase,
        "phase_ref": phase,
        "names": {"common_name": common_name, "formula": formula},
        "data": {
            "MW": props["MW"],
            "Tb": props["Tb"],
            "Tc": props["Tc"],
            "Pc": props["Pc"],
            "Vc": props["Vc"],
            "omega": props["omega"],
            "Hf": 0.0,
        },
        "properties": {
            "V": {phase: {"constant": vol_ref}},
            "Cn": {phase: {"constant": cp_ref}},
            "Psat": {"constant": 1e-6 if phase == "l" else 1e5},
            "Hvap": {"constant": 5e4 if phase == "l" else 1.5e4},
        },
        "cosmo": {
            "A": profile["A"],
            "V": profile["V"],
            "Pnhb": profile["Pnhb"],
            "POH": profile["POH"],
            "POT": profile["POT"],
        },
        "cp_polynomial": cp_coeffs,
    }


def _build_builtin_chemical_yaml(common_name: str, profile: dict) -> dict:
    """Build a YAML definition for a built-in chemical with an added COSMO profile."""
    return {
        "search_db": True,
        "names": {"common_name": common_name},
        "cosmo": {
            "A": profile["A"],
            "V": profile["V"],
            "Pnhb": profile["Pnhb"],
            "POH": profile["POH"],
            "POT": profile["POT"],
        },
    }


def main() -> None:
    print("Extracting glycerol profile...")
    glycerol_profile = extract_clapeyron_profile(GLYCEROL_COSKF, method="COSMOSAC2013", verbose=1)

    print("Extracting CO2 profile...")
    co2_profile = extract_clapeyron_profile(CO2_COSKF, method="COSMOSAC2013", verbose=1)

    print("Extracting Water profile...")
    water_profile = extract_clapeyron_profile(WATER_COSKF, method="COSMOSAC2013", verbose=1)

    print("Loading choline cation and chloride profiles...")
    with open(ION_YAML) as f:
        ion_data = yaml.safe_load(f)
    cation = {
        "names": ion_data["chemicals"]["choline_cation"]["names"],
        "cosmo": ion_data["chemicals"]["choline_cation"]["cosmo"],
    }
    anion = {
        "names": ion_data["chemicals"]["chloride"]["names"],
        "cosmo": ion_data["chemicals"]["chloride"]["cosmo"],
    }

    print("Combining ion pair and DES profiles...")
    choline_chloride_profile = _combine_ion_pair(cation, anion, "choline_chloride")
    des_profile = _combine_binary_mixture(
        choline_chloride_profile,
        glycerol_profile,
        "DES_choline_chloride_glycerol",
        moles1=1.0,
        moles2=HBA_HBD_MOLE_RATIO,
        formula="C8H21ClNO4",
    )

    print("Estimating critical properties...")
    glycerol_props = _run_joback("OCC(O)CO")
    cation_props = _run_joback("C[N+](C)(C)CCO")
    anion_props = _run_joback("[Cl-]")
    choline_chloride_props = _ion_pair_critical_properties(cation_props, anion_props)
    des_props = _combine_critical_properties(
        choline_chloride_props,
        glycerol_props,
        moles1=1.0,
        moles2=HBA_HBD_MOLE_RATIO,
    )

    print("Predicting heat capacities...")
    temperatures = np.linspace(CP_T_MIN, CP_T_MAX, CP_N_POINTS).tolist()
    glycerol_cp = _predict_cp(glycerol_props, temperatures)
    cation_cp = _predict_cp(cation_props, temperatures)
    anion_cp = _predict_cp(anion_props, temperatures)

    # Ion pair Cp is the sum of ion Cps (per mole of ion pair)
    choline_chloride_cp = [a + b for a, b in zip(cation_cp, anion_cp)]

    # DES Cp is mole-fraction weighted average of ion pair and glycerol Cps
    x_hba = 1.0 / (1.0 + HBA_HBD_MOLE_RATIO)
    x_hbd = HBA_HBD_MOLE_RATIO / (1.0 + HBA_HBD_MOLE_RATIO)
    des_cp = [x_hba * a + x_hbd * b for a, b in zip(choline_chloride_cp, glycerol_cp)]

    glycerol_cp_coeffs = _fit_cp_polynomial(temperatures, glycerol_cp)
    choline_chloride_cp_coeffs = _fit_cp_polynomial(temperatures, choline_chloride_cp)
    des_cp_coeffs = _fit_cp_polynomial(temperatures, des_cp)

    print("Building YAML...")
    # V1 simulation chemicals: only those actually present in streams.
    # Registering HBA/HBD separately causes the Clapeyron backend to receive
    # composition arrays of inconsistent length during subset VLE calculations.
    chemicals = {
        # Feed components: use built-in properties, add COSMO profile
        "CO2": _build_builtin_chemical_yaml("carbon dioxide", co2_profile),
        "Water": _build_builtin_chemical_yaml("water", water_profile),
        # DES pseudo-component used as the absorbent
        "DES_choline_chloride_glycerol": _build_chemical_yaml(
            ID="DES_choline_chloride_glycerol",
            common_name="des_choline_chloride_glycerol",
            formula="C8H21ClNO4",
            props=des_props,
            profile=des_profile,
            cp_coeffs=des_cp_coeffs,
        ),
    }

    data = {
        "des_dehydration_data": {
            "hba": "choline_chloride",
            "hbd": "glycerol",
            "hba_hbd_mole_ratio": HBA_HBD_MOLE_RATIO,
            "chemicals": chemicals,
            "cp_temperature_range": {"Tmin": CP_T_MIN, "Tmax": CP_T_MAX},
            # Keep HBA/HBD reference data for traceability, but do not register them.
            "hba_profile": choline_chloride_profile,
            "hbd_profile": {
                "name": "glycerol",
                "A": glycerol_profile["A"],
                "V": glycerol_profile["V"],
                "Pnhb": glycerol_profile["Pnhb"],
                "POH": glycerol_profile["POH"],
                "POT": glycerol_profile["POT"],
            },
        }
    }

    with open(OUTPUT_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
