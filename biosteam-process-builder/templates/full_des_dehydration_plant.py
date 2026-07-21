#!/usr/bin/env python3
"""DES dehydration-regeneration full plant template (V2).

This template closes the DES loop with a stripping column regeneration train:
absorber bottom rich DES is pre-heated by hot regenerated DES, brought to
stripper feed temperature, and fed to the top of a stripping column. The
stripper has only a stripping section (reflux = 0); boilup at the bottom
provides stripping vapor. Internal stage temperatures are determined by the
energy balance, not fixed externally. Water stripped from the DES leaves with
the CO2-rich top vapor;
the regenerated lean DES is cooled and recycled to the absorber with a small
purge / fresh makeup split.

Because the absorber and stripper operate at the same pressure (1 bar), no
valve or pump is required between them.

The template is rigorous-mode only (Clapeyron/COSMOSAC2013).  If Clapeyron is
not available it fails early with setup guidance.

Run from the repository root:

    PYTHONPATH=thermosteam \
        python .claude/skills/biosteam-process-builder/templates/full_des_dehydration_plant.py

Inputs:
    ../../inputs/des_dehydration_data.yml

Outputs:
    ../../outputs/<RUN_ID>/brief.md
    ../../outputs/<RUN_ID>/stream_table.csv
"""
from __future__ import annotations

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

# Cp polynomial coefficients by chemical ID, kept for possible range extension.
_CP_POLYNOMIALS: dict[str, list[float]] = {}

# Module-level cache for the configured chemicals object.  Reusing the same
# Clapeyron backend across builds avoids the ~20 s Julia/model startup cost
# when the same DES chemistry is simulated repeatedly in one process.
_THERMO_CACHE: dict[str, tmo.Chemicals] = {}

import biosteam as bst
import thermosteam as tmo
import warnings


class ConditionedMixer(bst.units.Mixer):
    """Mixer that forces outlet T/P to fixed values.

    This represents the conditioning of the combined fresh DES makeup and
    regenerated DES recycle stream to the absorber inlet conditions.
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
RUN_ID = "run_full_plant_001"

GAS_FEED = {
    "T": 40.0 + 273.15,
    "P": 10.0 * 1e5,
    "flow": 1000.0,
    "CO2": 0.95,
    "Water": 0.05,
}

ABSORBENT = {
    "T": 25.0 + 273.15,
    "P": 10.0 * 1e5,
    "flow": 5000.0,
}

MAKEUP_FRACTION = 0.05

INERT = {
    "ID": None,
    "flow": 0.0,
}

COLUMN = {
    "N_stages": 5,
}

STRIPPER = {
    "T": 150.0 + 273.15,  # Heater outlet / stripper feed temperature [K]
    "P": 1.0 * 1e5,
    "N_stages": 5,
    "feed_stage": 0,
    "reflux": 0.0,
    "boilup": 0.5,
    "LHK": ("Water", "DES_choline_chloride_glycerol"),
}

HX = {
    "approach_dT": 5.0,
    "fallback_duty_kw": 500.0,
    "use_process_hx": True,
}

COOLER = {
    "outlet_T": 25.0 + 273.15,
}

RECYCLE = {
    "tolerance": 1e-6,
    "maxiter": 100,
}

OPTIMIZATION = {
    "use_cache": True,
    "tolerance": 1e-2,
    "relative_tolerance": 1e-2,
    "maxiter": 15,
}

# ---------------------------------------------------------------------------
# Chemical / thermo helpers (reused from des_dehydration.py)
# ---------------------------------------------------------------------------
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
            # Keep coefficients for possible range extension in validate_property_ranges.
            _CP_POLYNOMIALS[ID] = coeffs

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


def _thermo_cache_key(data: dict[str, Any], inert_id: str | None) -> str:
    """Stable cache key for a given chemistry + inert configuration."""
    chemicals_spec = data["des_dehydration_data"]["chemicals"]
    return yaml.dump(chemicals_spec, sort_keys=True) + f"\ninert={inert_id}"


def load_and_configure_thermo(data: dict[str, Any], inert_id: str | None) -> tmo.Chemicals:
    """Register chemicals and set the thermo backend to Clapeyron (V2 only).

    A module-level cache keeps the configured ``Chemicals`` object (and the
    associated warm Clapeyron backend) alive across repeated calls in the same
    process.  This avoids paying the Julia/model initialization cost for every
    ``ProcessState.build()`` when the chemistry does not change.
    """
    key = _thermo_cache_key(data, inert_id)
    cached = _THERMO_CACHE.get(key)
    if cached is not None:
        # Re-activate the cached thermo object.  The Clapeyron model itself is
        # cached at the backend class level, so this is cheap.
        tmo.settings.thermo_backend = "clapeyron"
        tmo.settings.thermo_safeguards = False
        tmo.settings.set_thermo(cached)
        return cached

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
    _THERMO_CACHE[key] = chemicals
    return chemicals


def validate_property_ranges(state: "ProcessState") -> None:
    """Ensure required chemical property ranges cover stripper T (423 K).

    For heat-capacity polynomials, the range is extended to 423 K when the
    underlying coefficients are available.  When extension is not possible,
    a warning is appended to ``state.extrapolation_warnings`` and reported in
    the brief; it does not raise an exception.
    """
    target_T = state.stripper_T
    ids = [state.des_id, "Water", "CO2"]
    if state.inert_id:
        ids.append(state.inert_id)

    for cid in ids:
        if cid not in state.chemicals:
            continue
        chem = state.chemicals[cid]
        for prop_name in ("Cn", "Psat"):
            prop = getattr(chem, prop_name, None)
            if prop is None:
                continue
            sub = getattr(prop, "l", None)
            if sub is None:
                continue
            tmax = getattr(sub, "Tmax", None)
            if tmax is None:
                continue
            if tmax < target_T:
                extended = False
                if prop_name == "Cn":
                    coeffs = _CP_POLYNOMIALS.get(cid)
                    if coeffs:
                        _apply_cp_polynomial(chem, coeffs, 298.15, target_T)
                        extended = True
                        state.extrapolation_warnings.append(
                            f"{cid}.{prop_name}.l range extended from "
                            f"{tmax:.1f} K to {target_T:.1f} K using the fitted polynomial."
                        )
                if not extended:
                    state.extrapolation_warnings.append(
                        f"{cid}.{prop_name}.l.Tmax = {tmax:.1f} K (< {target_T:.1f} K); "
                        f"properties may be extrapolated above fitted range."
                    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(state: "ProcessState") -> dict[str, float]:
    """Compute mass and energy metrics from the converged full-plant flowsheet."""
    gas_feed = state.gas_feed
    dry_co2 = state.absorber.outs[0]
    rich_des = state.absorber.outs[1]
    stripper = state.stripper
    stripper_vapor = stripper.outs[0]
    regenerated_des = stripper.outs[1]
    co2_vent = stripper.outs[0]
    recycle = state.recycle
    purge = state.splitter.outs[1]

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
    water_stripped = max(0.0, water_in_rich_des - regenerated_des.imol["Water"])
    water_recovery = (
        water_stripped / water_in_rich_des if water_in_rich_des > 0 else 0.0
    )

    # Energy metrics
    if not state._hx_fallback and state.hx is not None and hasattr(state.hx, "total_heat_transfer"):
        hx_duty = abs(float(state.hx.total_heat_transfer))
    else:
        # Fallback: compute from cold-stream enthalpy rise across the HX block.
        if state._hx_fallback:
            cold_in = state.absorber.outs[1]
            cold_out = state.hx_cold.outs[0]
        else:
            cold_in = state.absorber.outs[1]
            cold_out = state.hx.outs[0]
        hx_duty = max(0.0, cold_out.H - cold_in.H)

    heater_in = state.heater.ins[0]
    heater_out = state.heater.outs[0]
    heater_duty = heater_out.H - heater_in.H

    cooler_in = state.cooler.ins[0]
    cooler_out = state.cooler.outs[0]
    cooler_duty = cooler_out.H - cooler_in.H

    # Reboiler duty from the stripper. For MESHDistillation compute it from
    # the reboiler (last) stage energy balance: Q = H_out - H_in.
    reboiler_stage = stripper.stages[-1]
    reboiler_duty = sum(o.H for o in reboiler_stage.outs) - sum(i.H for i in reboiler_stage.ins)

    # No-HX baseline: sensible heating of the absorber-bottom rich DES to stripper T.
    cp_molar = rich_des.Cn  # kJ/kmol/K
    duty_without_hx = rich_des.F_mol * cp_molar * (state.stripper_T - rich_des.T)
    # Self-consistent heat-recovery definition: HX share of total heating.
    total_heating = hx_duty + heater_duty
    heat_recovery_fraction = hx_duty / total_heating if total_heating > 0 else 0.0

    vent_flow = co2_vent.F_mol
    vent_water_flow = co2_vent.imol["Water"]
    vent_CO2_flow = co2_vent.imol["CO2"]

    return {
        # Mass metrics
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
        "stripper_T": stripper.stages[-1].T,
        "stripper_P": state.stripper_P,
        "stripper_stages": state.stripper_stages,
        # BioSTEAM exposes no public recycle-iteration accessor; read the
        # private System._iter slot that is populated after simulate().
        "recycle_iterations": state.system._iter if state.system is not None else 0,
        # Energy metrics
        "hx_duty": hx_duty,
        "heater_duty": heater_duty,
        "cooler_duty": cooler_duty,
        "reboiler_duty": reboiler_duty,
        "heat_recovery_fraction": heat_recovery_fraction,
        "duty_without_hx": duty_without_hx,
        "vent_flow": vent_flow,
        "vent_water_flow": vent_water_flow,
        "vent_CO2_flow": vent_CO2_flow,
    }


# ---------------------------------------------------------------------------
# Process state
# ---------------------------------------------------------------------------
class ProcessState:
    """Mutable container for the full-plant process state."""

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
        stripper_spec: dict[str, float],
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
        self.stripper_T = stripper_spec["T"]
        self.stripper_P = stripper_spec["P"]
        self.stripper_stages = stripper_spec["N_stages"]
        self.stripper_feed_stage = stripper_spec.get("feed_stage", 0)
        self.stripper_reflux = stripper_spec.get("reflux", 0.0)
        self.stripper_boilup = stripper_spec.get("boilup", 0.5)
        self.stripper_LHK = tuple(stripper_spec.get("LHK", ("Water", des_id)))
        self.gas_total_flow = gas_spec["flow"] + inert_flow

        self.N_stages = N_stages if N_stages is not None else COLUMN["N_stages"]
        self.des_total_flow = absorbent_spec["flow"]
        self.P = gas_spec["P"]
        self.T_gas = gas_spec["T"]
        self.x_water = (
            gas_spec["flow"] * gas_spec["Water"] / self.gas_total_flow
            if self.gas_total_flow > 0 else 0.0
        )

        # Mutable references updated by build()
        self.system: Any = None
        self.gas_feed: Any = None
        self.fresh_des: Any = None
        self.recycle: Any = None
        self.mixer: Any = None
        self.absorber: Any = None
        self.hx: Any = None
        self.heater: Any = None
        self.stripper: Any = None
        self.cooler: Any = None
        self.splitter: Any = None

        # Fallback HX utility blocks (populated when HXprocess is disabled / fails)
        self.hx_cold: Any = None
        self.hx_hot: Any = None
        self._hx_fallback = False

        # True when a structural parameter (N_stages, P, stripper T) changes
        # and the System object must be rebuilt before the next converge().
        self._needs_rebuild = False

        # Property-extrapolation warnings collected during build()
        self.extrapolation_warnings: list[str] = []

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
        self.recycle.imol["Water"] = recycle_flow * 0.001
        self.recycle.T = self.COOLER_outlet_T if hasattr(self, "COOLER_outlet_T") else COOLER["outlet_T"]
        self.recycle.P = self.P
        self.recycle.phase = "l"

    def _update_stripper_bottoms_guess(self, stream: tmo.Stream) -> None:
        """Provide a non-empty initial guess for the stripper bottoms stream.

        This is needed because the HXprocess is placed before the Stripper in
        the system path and would otherwise see an empty hot-side inlet on the
        first sequential-modular pass.
        """
        lean_flow = self.des_total_flow * (1.0 - self.makeup_fraction)
        stream.imol[self.des_id] = lean_flow
        stream.imol["Water"] = lean_flow * 0.05
        stream.T = self.stripper_T
        stream.P = self.stripper_P
        stream.phase = "l"

    def build(self) -> None:
        """Create fresh streams, units, and system from the current state."""
        n = self._instance_id

        self._hx_fallback = False
        self.extrapolation_warnings = []
        validate_property_ranges(self)

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

        # Tear stream: splitter recycle outlet (also mixer inlet)
        self.recycle = bst.Stream(f"recycle_{n}")
        self._update_recycle_guess()

        self.mixer = ConditionedMixer(
            f"mixer_{n}",
            ins=[self.fresh_des, self.recycle],
            outlet_T=self.absorbent_spec["T"],
            outlet_P=self.P,
        )

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

        # Process-to-process heat recovery (rich/lean)
        hx_cold_out = bst.Stream(f"hx_cold_out_{n}", phase="l")
        hx_hot_out = bst.Stream(f"hx_hot_out_{n}", phase="l")
        regenerated_des = bst.Stream(f"regenerated_des_{n}", phase="l")
        self._update_stripper_bottoms_guess(regenerated_des)

        if HX.get("use_process_hx", True):
            try:
                self.hx = bst.units.HXprocess(
                    f"hx_{n}",
                    ins=[rich_des_product, regenerated_des],
                    outs=[hx_cold_out, hx_hot_out],
                    dT=HX["approach_dT"],
                    phase0="l",
                    phase1="l",
                )
                # Early simulation to decide whether we can rely on process HX.
                self.hx.simulate()
            except Exception:
                self._hx_fallback = True
                self.hx = None
        else:
            self._hx_fallback = True

        if self._hx_fallback:
            duty_kj_hr = HX["fallback_duty_kw"] * 3600.0
            self.hx_cold = bst.HXutility(
                f"hx_cold_{n}",
                ins=rich_des_product,
                outs=hx_cold_out,
                H=rich_des_product.H + duty_kj_hr,
                rigorous=False,
            )
            self.hx_hot = bst.HXutility(
                f"hx_hot_{n}",
                ins=regenerated_des,
                outs=hx_hot_out,
                H=regenerated_des.H - duty_kj_hr,
                rigorous=False,
            )

        heater_out = bst.Stream(f"heater_out_{n}", phase="l")
        self.heater = bst.HXutility(
            f"heater_{n}",
            ins=hx_cold_out,
            outs=heater_out,
            T=self.stripper_T,
            rigorous=False,
        )

        co2_vent = bst.Stream(f"co2_vent_{n}", phase="g")
        # Use MESHDistillation as a reflux-free stripper (feed at the top,
        # boilup at the bottom). The tower is adiabatic: internal stage
        # temperatures are determined by the energy balance, not fixed.
        self.stripper = bst.units.MESHDistillation(
            f"stripper_{n}",
            ins=[heater_out],
            outs=[co2_vent, regenerated_des],
            N_stages=self.stripper_stages,
            feed_stages=[self.stripper_feed_stage],
            reflux=self.stripper_reflux,
            boilup=self.stripper_boilup,
            P=self.stripper_P,
            LHK=self.stripper_LHK,
            full_condenser=False,
            algorithms=("sequential modular",),
            maxiter=OPTIMIZATION.get("maxiter", 15),
            max_attempts=5,
            use_cache=OPTIMIZATION.get("use_cache", True),
        )

        cooler_out = bst.Stream(f"cooler_out_{n}", phase="l")
        self.cooler = bst.HXutility(
            f"cooler_{n}",
            ins=hx_hot_out,
            outs=cooler_out,
            T=self.absorbent_spec["T"],
            rigorous=False,
        )

        purge = bst.Stream(f"purge_{n}", phase="l")
        self.splitter = bst.units.Splitter(
            f"splitter_{n}",
            ins=cooler_out,
            outs=[self.recycle, purge],
            split=1.0 - self.makeup_fraction,
        )

        path: list[Any] = [self.mixer, self.absorber]
        if self._hx_fallback:
            path.append(self.hx_cold)
        else:
            path.append(self.hx)
        path.extend([self.heater, self.stripper])
        if self._hx_fallback:
            path.append(self.hx_hot)
        path.extend([self.cooler, self.splitter])

        self.system = bst.System(
            f"des_full_plant_{n}",
            path=path,
            recycle=self.recycle,
            maxiter=RECYCLE.get("maxiter", 100),
            molar_tolerance=RECYCLE.get("tolerance", 1e-6),
        )
        # MESHDistillation's _design()/_actual_stages() requires both LHK
        # chemicals to be in the VLE chemical list. DES is locked as a
        # non-volatile liquid, so skip equipment design and only converge
        # mass/energy balances.
        self.system.simulate(design_and_cost=False)
        self._needs_rebuild = False

    # -----------------------------------------------------------------------
    # Incremental update API (keeps the System alive for warm starts)
    # -----------------------------------------------------------------------
    # ``update_*`` methods change parameters in-place and mark structural
    # changes for rebuild.  Call ``converge()`` to re-run without rebuilding
    # the whole flowsheet when only stream conditions changed.
    # -----------------------------------------------------------------------
    def update_N_stages(self, N: float) -> None:
        N_int = int(round(N))
        if self.N_stages == N_int:
            return
        self.N_stages = N_int
        self._needs_rebuild = True

    def update_DES_total_flow(self, flow: float) -> None:
        if self.des_total_flow == flow:
            return
        self.des_total_flow = flow
        if self.fresh_des is not None:
            self.fresh_des.imol[self.des_id] = flow * self.makeup_fraction

    def update_makeup_fraction(self, frac: float) -> None:
        if self.makeup_fraction == frac:
            return
        self.makeup_fraction = frac
        if self.fresh_des is not None:
            self.fresh_des.imol[self.des_id] = self.des_total_flow * frac
        if self.splitter is not None:
            self.splitter.split = 1.0 - frac

    def update_P(self, P: float) -> None:
        if self.P == P:
            return
        self.P = P
        self.stripper_P = P
        self._needs_rebuild = True

    def update_T_gas(self, T: float) -> None:
        if self.T_gas == T:
            return
        self.T_gas = T
        if self.gas_feed is not None:
            self.gas_feed.T = T

    def update_x_water(self, x: float) -> None:
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

    def update_stripper_T(self, T: float) -> None:
        if self.stripper_T == T:
            return
        self.stripper_T = T
        self._needs_rebuild = True

    def update_stripper_P(self, P: float) -> None:
        if self.stripper_P == P:
            return
        self.stripper_P = P
        self._needs_rebuild = True

    def converge(self) -> None:
        """Re-converge the existing System if possible; otherwise rebuild.

        When only stream conditions changed (flow, T, composition), the same
        System object and its last recycle state are reused.  This avoids the
        cost of reconstructing every unit.  Because the recycle stream starts
        from the previously converged state, small parameter perturbations
        converge quickly, though the final recycle state may differ from a fresh
        rebuild by an amount comparable to the convergence tolerance.

        To keep incremental results consistent with a fresh rebuild, unit-level
        caches (notably MESHDistillation stage profiles) are reset before the
        re-convergence while the recycle stream keeps its warm start.
        """
        if self.system is None or self._needs_rebuild:
            self.build()
        else:
            self.system.reset_cache()
            self.system.simulate(design_and_cost=False)

    # -----------------------------------------------------------------------
    # Legacy setters: rebuild from scratch each time (slower but safe)
    # -----------------------------------------------------------------------
    def set_N_stages(self, N: float) -> None:
        self.update_N_stages(N)
        self.build()

    def set_DES_total_flow(self, flow: float) -> None:
        self.update_DES_total_flow(flow)
        self.build()

    def set_makeup_fraction(self, frac: float) -> None:
        self.update_makeup_fraction(frac)
        self.build()

    def set_P(self, P: float) -> None:
        self.update_P(P)
        self.build()

    def set_T_gas(self, T: float) -> None:
        self.update_T_gas(T)

    def set_x_water(self, x: float) -> None:
        self.update_x_water(x)

    def set_stripper_T(self, T: float) -> None:
        self.update_stripper_T(T)
        self.build()

    def set_stripper_P(self, P: float) -> None:
        self.update_stripper_P(P)
        self.build()


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------
def _unit_duty_or_power(unit: Any) -> float:
    """Return a representative duty (kW) or power (kW) for a unit."""
    if unit is None:
        return 0.0
    name = type(unit).__name__
    if name in ("HXutility",):
        # Net duty is outlet - inlet enthalpy; sign indicates heating/cooling.
        return (unit.outs[0].H - unit.ins[0].H) / 3600.0
    if name in ("HXprocess",):
        return abs(float(unit.total_heat_transfer)) / 3600.0 if unit.total_heat_transfer is not None else 0.0
    return 0.0


def _unit_T_in(unit: Any) -> float:
    """Representative inlet temperature (C) for the equipment table."""
    if unit is None or not unit.ins:
        return 0.0
    return unit.ins[0].T - 273.15


def _unit_T_out(unit: Any) -> float:
    """Representative outlet temperature (C) for the equipment table."""
    if unit is None or not unit.outs:
        return 0.0
    return unit.outs[0].T - 273.15


def _unit_P_in(unit: Any) -> float:
    if unit is None or not unit.ins:
        return 0.0
    return unit.ins[0].P / 1e5


def _unit_P_out(unit: Any) -> float:
    if unit is None or not unit.outs:
        return 0.0
    return unit.outs[0].P / 1e5


def _equipment_rows(state: ProcessState) -> list[dict[str, Any]]:
    """Build rows for the equipment Markdown table."""
    logical_units = [
        ("Mixer", state.mixer),
        ("Absorber", state.absorber),
        ("HXprocess (rich/lean)", state.hx if not state._hx_fallback else state.hx_cold),
        ("Heater", state.heater),
        ("Stripper", state.stripper),
        ("Cooler", state.cooler),
        ("Splitter", state.splitter),
    ]
    if state._hx_fallback:
        # Insert the hot-side fallback HX before the cooler.
        logical_units.insert(5, ("HXutility (lean cooler)", state.hx_hot))

    rows = []
    for label, unit in logical_units:
        value = _unit_duty_or_power(unit)
        kind = "duty"
        rows.append({
            "Unit": label,
            "T_in (C)": f"{_unit_T_in(unit):.2f}",
            "T_out (C)": f"{_unit_T_out(unit):.2f}",
            "P_in (bar)": f"{_unit_P_in(unit):.3f}",
            "P_out (bar)": f"{_unit_P_out(unit):.3f}",
            "duty/power (kW)": f"{value:.3f}",
            "_kind": kind,
        })
    return rows


def _write_brief(
    run_dir: Path,
    data: dict[str, Any],
    inert_id: str | None,
    metrics: dict[str, float],
    state: ProcessState,
) -> Path:
    """Write the Markdown summary to ``brief.md``."""
    brief_path = run_dir / "brief.md"
    dry_co2 = state.absorber.outs[0]
    rich_des = state.absorber.outs[1]
    regenerated_des = state.stripper.outs[1]
    recycle = state.recycle
    purge = state.splitter.outs[1]
    co2_vent = state.stripper.outs[0]

    target = 1e-3  # 0.1 mol %
    dry_pass = metrics["water_molefrac_out"] <= target
    regen_pass = metrics["regen_water_molefrac"] <= target
    dry_gap = metrics["water_molefrac_out"] - target
    regen_gap = metrics["regen_water_molefrac"] - target

    with open(brief_path, "w") as f:
        f.write("# DES Dehydration-Regeneration Full Plant — Results\n\n")
        f.write(f"**DES**: choline chloride / glycerol (1:{data['des_dehydration_data']['hba_hbd_mole_ratio']})\n\n")
        f.write("**Gas feed**: ")
        f.write(f"{GAS_FEED['flow']:.1f} kmol/hr CO2/H2O, ")
        f.write(f"{GAS_FEED['CO2']*100:.1f}% CO2 / {GAS_FEED['Water']*100:.1f}% H2O")
        if inert_id:
            f.write(f" + {INERT['flow']:.1f} kmol/hr {inert_id}")
        f.write(f", {GAS_FEED['T']-273.15:.1f} C, {GAS_FEED['P']/1e5:.2f} bar\n\n")
        f.write(f"**Total DES flow**: {ABSORBENT['flow']:.1f} kmol/hr, ")
        f.write(f"makeup fraction = {MAKEUP_FRACTION:.2f}, ")
        f.write(f"fresh makeup = {ABSORBENT['flow'] * MAKEUP_FRACTION:.1f} kmol/hr\n\n")
        f.write(f"**Column**: {state.N_stages} equilibrium stages (rigorous COSMOSAC) at {state.P/1e5:.2f} bar\n\n")
        top_stage = state.stripper.stages[0]
        bot_stage = state.stripper.stages[-1]
        f.write(f"**Stripper**: {state.stripper_stages} stages, {metrics['stripper_P']/1e5:.3f} bar, reflux = {state.stripper_reflux}, boilup = {state.stripper_boilup}\n\n")
        f.write(f"**Stripper operating mode**: adiabatic equilibrium stages; temperatures are determined by the energy balance, not fixed. Top stage {top_stage.T-273.15:.1f} C, bottom stage {bot_stage.T-273.15:.1f} C.\n\n")
        f.write(f"**Tear stream**: splitter recycle outlet → mixer (closes DES recycle loop)\n\n")
        if state._hx_fallback:
            f.write(
                "**Heat integration note**: process/process HX was disabled or failed to converge; "
                "fallback utility HX blocks are being used (no heat recovery).\n\n"
            )

        if state.extrapolation_warnings:
            f.write("## Extrapolation warnings\n\n")
            for w in state.extrapolation_warnings:
                f.write(f"- ⚠️ {w}\n")
            f.write("\n")

        f.write("## Equipment table\n\n")
        rows = _equipment_rows(state)
        if rows:
            headers = ["Unit", "T_in (C)", "T_out (C)", "P_in (bar)", "P_out (bar)", "duty/power (kW)"]
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
            for r in rows:
                f.write(
                    f"| {r['Unit']} | {r['T_in (C)']} | {r['T_out (C)']} | "
                    f"{r['P_in (bar)']} | {r['P_out (bar)']} | {r['duty/power (kW)']} |\n"
                )
            f.write("\n")

        f.write("## Mass metrics\n\n")
        f.write(f"- Dry CO2 flow: {metrics['dry_co2_flow']:.2f} kmol/hr\n")
        f.write(f"- Dry CO2 water mole fraction: {metrics['water_molefrac_out']:.6f}\n")
        f.write(f"- Water removed: {metrics['water_removed']:.2f} kmol/hr ({metrics['removal']:.2%})\n")
        f.write(f"- CO2 loss to DES: {metrics['co2_loss']:.2f} kmol/hr ({metrics['co2_loss_fraction']:.2%})\n")
        f.write(f"- Rich DES flow: {metrics['rich_des_flow']:.2f} kmol/hr\n")
        f.write(f"- Regenerated DES flow: {metrics['regen_des_flow']:.2f} kmol/hr\n")
        f.write(f"- Regenerated DES water mole fraction: {metrics['regen_water_molefrac']:.6f}\n")
        f.write(f"- Recycle DES flow: {metrics['recycle_des_flow']:.2f} kmol/hr\n")
        f.write(f"- Recycle DES water mole fraction: {metrics['recycle_water_molefrac']:.6f}\n")
        f.write(f"- Water stripped from DES: {metrics['water_recovery']:.2%}\n")
        f.write(f"- Vent flow: {metrics['vent_flow']:.2f} kmol/hr\n")
        f.write(f"- Vent water flow: {metrics['vent_water_flow']:.2f} kmol/hr\n")
        f.write(f"- Vent CO2 flow: {metrics['vent_CO2_flow']:.2f} kmol/hr\n")
        f.write(f"- Recycle convergence iterations: {metrics['recycle_iterations']}\n\n")

        f.write("## Energy metrics\n\n")
        f.write(f"- HX duty (heat recovery): {metrics['hx_duty']/3600.0:.3f} kW\n")
        f.write(f"- Heater duty: {metrics['heater_duty']/3600.0:.3f} kW\n")
        f.write(f"- Cooler duty: {abs(metrics['cooler_duty'])/3600.0:.3f} kW\n")
        f.write(f"- Reboiler duty: {metrics['reboiler_duty']/3600.0:.3f} kW\n")
        f.write(f"- Heat recovery fraction: {metrics['heat_recovery_fraction']:.3f}\n\n")

        f.write("## Target check (< 0.1 mol % water)\n\n")
        f.write("| Stream | Target | Actual | Pass | Gap |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        f.write(f"| Dry CO2 | <= {target:.4f} | {metrics['water_molefrac_out']:.6f} | {'PASS' if dry_pass else 'FAIL'} | {dry_gap:+.6f} |\n")
        f.write(f"| Regenerated DES | <= {target:.4f} | {metrics['regen_water_molefrac']:.6f} | {'PASS' if regen_pass else 'FAIL'} | {regen_gap:+.6f} |\n\n")

        f.write("## Water balance\n\n")
        water_in_total = state.gas_feed.imol["Water"]
        water_dry = dry_co2.imol["Water"]
        water_vent = co2_vent.imol["Water"]
        water_regen_des = regenerated_des.imol["Water"]
        water_purge = purge.imol["Water"]
        water_recycle = recycle.imol["Water"]
        # Only count net outputs: dry CO2 and purge.  The recycle portion of
        # the regenerated DES is internal to the loop; vent water is counted
        # as an output.
        water_out_total = water_dry + water_vent + water_purge
        f.write(f"- Water in gas feed: {water_in_total:.4f} kmol/hr\n")
        f.write(f"- Water in dry CO2: {water_dry:.4f} kmol/hr\n")
        f.write(f"- Water in vent: {water_vent:.4f} kmol/hr\n")
        f.write(f"- Water in purge DES: {water_purge:.4f} kmol/hr\n")
        f.write(f"- Water in regenerated DES (before split): {water_regen_des:.4f} kmol/hr\n")
        f.write(f"  - of which in recycle DES: {water_recycle:.4f} kmol/hr\n")
        f.write(f"  - of which in purge DES: {water_purge:.4f} kmol/hr\n")
        f.write(f"- Accounted outputs (dry + vent + purge): {water_out_total:.4f} kmol/hr\n")
        if water_in_total > 0:
            f.write(f"- Closure: {water_out_total / water_in_total:.4%}\n\n")
        else:
            f.write("\n")

        f.write("## Attribution\n\n")
        f.write("- Thermodynamic backend: Clapeyron/COSMOSAC2013 (V2 rigorous mode only).\n")
        f.write("- DES represented as a single pseudo-component (choline chloride / glycerol).\n")
        f.write("- Architecture decision records: ADR-0001, ADR-0002, ADR-0003, ADR-0007.\n")
    return brief_path


def _write_stream_table(run_dir: Path, state: ProcessState) -> Path:
    """Write ``stream_table.csv`` with all unit inlet/outlet streams."""
    csv_path = run_dir / "stream_table.csv"
    chemical_ids = list(state.chemicals.IDs)
    rows: list[dict[str, Any]] = []

    units = [
        state.mixer, state.absorber,
        state.hx if not state._hx_fallback else state.hx_cold,
        state.heater, state.stripper,
        state.cooler, state.splitter,
    ]
    if state._hx_fallback:
        units.insert(5, state.hx_hot)

    for unit in units:
        if unit is None:
            continue
        for kind, streams in (("inlet", unit.ins), ("outlet", unit.outs)):
            for s in streams:
                if s is None:
                    continue
                row: dict[str, Any] = {
                    "stream_ID": s.ID,
                    "source_unit": unit.ID,
                    "kind": kind,
                }
                for cid in chemical_ids:
                    row[cid] = s.imol[cid]
                row["total_mol_flow_kmol_hr"] = s.F_mol
                row["T_C"] = s.T - 273.15
                row["P_bar"] = s.P / 1e5
                row["phase"] = str(s.phase)
                rows.append(row)

    df = pd.DataFrame(rows)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    run_dir = OUTPUT_DIR / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("DES dehydration-regeneration full plant template (V2)")
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
    print("V2: using rigorous Clapeyron/COSMOSAC backend for absorber and stripper.")
    print(f"HX heat recovery: {'enabled' if HX.get('use_process_hx', True) else 'fallback HXutility'}")

    print("Creating streams and building flowsheet...")
    state = ProcessState(
        chemicals,
        inert_id,
        inert_flow,
        GAS_FEED,
        ABSORBENT,
        des_id,
        makeup_fraction=MAKEUP_FRACTION,
        stripper_spec=STRIPPER,
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
    print(f"Water stripped from DES: {metrics['water_recovery']:.2%}")
    print(f"Vent water flow: {metrics['vent_water_flow']:.2f} kmol/hr")
    print(f"Vent CO2 flow: {metrics['vent_CO2_flow']:.2f} kmol/hr")
    print(f"Reboiler duty: {metrics['reboiler_duty']/3600.0:.3f} kW")
    print(f"Heat recovery fraction: {metrics['heat_recovery_fraction']:.3f}")
    print(f"Recycle convergence iterations: {metrics['recycle_iterations']}")

    if state._hx_fallback:
        print("\nNote: HXprocess was disabled or failed; fallback HXutility blocks used.")

    brief_path = _write_brief(run_dir, data, inert_id, metrics, state)
    csv_path = _write_stream_table(run_dir, state)

    print(f"\nWrote brief to {brief_path}")
    print(f"Wrote stream table to {csv_path}")


if __name__ == "__main__":
    main()
