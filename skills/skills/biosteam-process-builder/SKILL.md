---
name: biosteam-process-builder
description: Build and run BioSTEAM chemical process simulations from a free-form request. V2 implements a closed-loop DES absorption-regeneration flowsheet (Mixer + gas-liquid absorber + flash + recycle splitter) and is rigorous Clapeyron/COSMOSAC only. Always confirm the structured process spec before generating any code.
---

# biosteam-process-builder

## When to use

Activate when the user asks to build or simulate a chemical process in BioSTEAM, especially requests like:

- "Build a BioSTEAM flowsheet for DES dehydration with solvent regeneration."
- "Simulate choline chloride / glycerol dehydration in BioSTEAM, including a flash regenerator."
- "Create a BioSTEAM process for drying CO₂ with a deep eutectic solvent and recycling the DES."
- "BioSTEAM flowsheet for [chemical separation / solvent dehydration] with a closed-loop absorbent."

## Goal

Turn the user's request into:

1. An approved structured process spec.
2. A runnable BioSTEAM Python script (`process.py`).
3. A concise results brief (`brief.md`).

## Scope boundaries (V2)

V2 supports only:

- DES dehydration-regeneration base template (`des_dehydration_regeneration`).
- Fixed unit structure: `Mixer → MultiStageEquilibrium absorber → Flash → Splitter` with DES recycle.
- Rigorous Clapeyron/COSMOSAC thermodynamics.
- Varying DES components, feed mixture, column stages, flash T/P, regeneration target, and makeup fraction.

Do not promise or implement automatic unit-connection changes, optimization, PFD generation, non-DES templates, or auxiliary equipment (pumps, heat exchangers, compressors, valves) in V2.

## Fixed unit structure (V2)

V2 implements a **DES absorption column with solvent regeneration** for gas dehydration:

- **Mixer / ConditionedMixer**: combines fresh DES makeup and regenerated DES recycle into a single liquid feed at the absorber inlet T/P.
- **Absorber**: `biosteam.units.MultiStageEquilibrium` configured as a gas-liquid absorber.
  - Gas feed enters the bottom stage (stage `-1`) at specified T, P, and flow rate.
  - Mixed DES absorbent enters the top stage (stage `0`).
- **Flash**: `biosteam.units.Flash` that desorbs water from the water-rich DES liquid leaving the absorber bottom.
- **Splitter**: divides the regenerated flash liquid into a recycle stream (`(1 − makeup_fraction)`) and a purge stream (`makeup_fraction`) that closes the solvent mass balance.
- **Recycle**: regenerated DES recycle stream returns to the mixer.

**No reboiler / no condenser / no pump / no heat exchanger**: V2 models only the three core separation units plus the recycle loop.

**Products**:

- Top product of absorber: dehydrated CO₂ gas.
- Bottom product of absorber: water-rich DES liquid (sent to flash).
- Vapor product of flash: water-rich desorbed stream.
- Liquid product of flash: regenerated DES (split between recycle and purge).

**Default stages**: 3 equilibrium stages (configurable; 3 is the fast V2 default and gives ~94 % water removal for the baseline case).

**Equilibrium model**: **COSMOSAC2013** via the ThermoSTEAM Clapeyron backend (`tmo.settings.thermo_backend = 'clapeyron'`). V2 is **rigorous mode only**; there is no fast mode branch.

**Convergence**:

- `MultiStageEquilibrium` uses `algorithms=("sequential modular",)`.
- The recycle loop is converged by a BioSTEAM `System` over `Mixer → Absorber → Flash → Splitter`.
- Tear stream: splitter recycle outlet entering the mixer.
- Tear stream initial guess: same composition as fresh DES, flow = `absorbent.flow_rate × (1 − makeup_fraction)`, T/P equal to flash bottom conditions.
- Default tolerance: `1e-6`; default maximum iterations: `100`.

## Thermodynamic model and property data

### Model

V2 uses **COSMOSAC2013** via the ThermoSTEAM Clapeyron backend (`tmo.settings.thermo_backend = 'clapeyron'`). Both the absorber and the flash use the same Clapeyron/COSMOSAC model so that the absorption–desorption loop is thermodynamically consistent.

V2 does **not** support a fast mode with precomputed partition coefficients. If Clapeyron is unavailable, stop and report that V2 requires Julia/Clapeyron.

### Component representation

For a DES dehydration flowsheet, the simulation chemicals registered in ThermoSTEAM are:

1. **Feed components** (e.g., CO₂, Water) — ThermoSTEAM built-ins with COSMO-SAC profiles attached.
2. **DES pseudo-component** — a pre-mixed DES whose properties are derived from HBA + HBD at the requested mole ratio. The flowsheet stream uses this pseudo-component as the solvent.

HBA and HBD are **not** registered as separate simulation chemicals. Registering them together with the DES pseudo-component causes Clapeyron subset VLE calculations to receive composition arrays of inconsistent length. Their sigma profiles, critical properties, and heat capacities are still generated and stored so the DES pseudo-component can be rebuilt if the ratio changes.

### Property generation chain

For **HBA and HBD**:

1. `compound-to-sigma` skill → COSMO-SAC sigma profile (`Pnhb`, `POH`, `POT`), COSMO area `A`, and COSMO volume `V`.
2. `group-contribution-estimator` skill → `Tb`, `Tc`, `Pc`, `Vc`, `omega` (Lydersen-Joback-Reid; ionic HBA may need manual review).
3. `heat-capacity-ann` skill → molar heat capacity `Cp(T)` over 298–400 K.

For the **DES pseudo-component**:

1. Sigma profile: mole-fraction-weighted average of HBA and HBD sigma profiles.
2. COSMO area / volume: mole-fraction-weighted average of HBA and HBD `A` and `V`.
3. Pseudo-critical properties: `group-contribution-estimator` Lee–Kesler DES mixing rules from HBA/HBD critical properties and mole ratio.
4. `MW`: mole-fraction-weighted average of HBA/HBD molecular weights.
5. Heat capacity: `heat-capacity-ann` using the DES pseudo-critical properties as input, predicting `Cp(T)` over 298–400 K.

### Reference state and minimum scalar data

All custom chemicals use:

- `phase: l`
- `phase_ref: l`
- `Hf: 0 J/mol` (relative enthalpy basis; acceptable for non-reactive dehydration)

Minimum scalar data registered on each chemical:

| Property | Source |
| --- | --- |
| `MW` | Formula or weighted average |
| `Tc` | Group contribution or Lee–Kesler mixing |
| `Pc` | Group contribution or Lee–Kesler mixing |
| `Vc` | Group contribution or Lee–Kesler mixing |
| `Tb` | Group contribution or mole-fraction average |
| `omega` | Group contribution or mole-fraction average |

Temperature-dependent models:

| Property | Model |
| --- | --- |
| `Cn` (molar heat capacity) | Polynomial regression of ANN predictions over 298–400 K, applied via `chem.Cn.add_method(f, Tmin=298, Tmax=400)` |
| `V` (liquid molar volume) | Constant from COSMO volume `V` [Å³] converted to m³/mol |
| `Psat` | Constant `1e-6 Pa` (non-volatile DES / ionic liquid assumption) |
| `Hvap` | Constant `5e4 J/mol` |

Sigma profiles are stored in `thermosteam/thermosteam/equilibrium/cosmosac_database.json` via `add_cosmo_profile()`.

### Feed components

For non-DES feed chemicals (e.g., ethanol, water):

- Prefer ThermoSTEAM built-in database entries when available.
- If a built-in entry is missing or lacks COSMOSAC data, run `compound-to-sigma` and register the profile.

## Trigger

Event-driven: the user explicitly asks to build or simulate a chemical process in BioSTEAM.

Examples:

- "Build a BioSTEAM flowsheet for choline chloride / glycerol dehydration of CO₂ with solvent regeneration."
- "Simulate DES absorption dehydration of water-rich CO₂ in BioSTEAM, including a flash regenerator."
- "Create a BioSTEAM process for drying CO₂ with a deep eutectic solvent and recycling the DES."

## Input

Free-form natural language request. The user may specify any of:

- DES components and composition (HBA, HBD, mole ratio)
- Gas feed composition and conditions (CO₂, water, inerts)
- Total DES absorbent flow rate, temperature, and pressure
- Column operating conditions (T, P, number of stages)
- Flash operating conditions (T, P)
- Regeneration target: maximum water mole fraction in regenerated DES
- DES makeup fraction (fraction of total DES flow that is fresh makeup)
- Target dry-gas water content
- Costing / analysis basis (optional)

The canonical structured spec contains:

- `des` — `{hba: str, hbd: str, ratio: float}`
- `gas_feed` — `{CO2: float, Water: float, inert: {ID: str, flow: float} | None, T: float, P: float, flow_basis: str}`
  - V2 supports CO₂ + Water plus one optional inert gas (e.g., N₂). The inert is absorbed physically via Henry's law / activity coefficients; chemical absorption is out of scope. Other absorbable components are out of scope.
- `absorbent` — `{flow_rate: float, T: float, P: float}`
  - This is the **total DES flow rate entering the mixer** (fresh + recycled).
- `column` — `{N_stages: int, P: float}`
- `flash` — `{T: float, P: float}` (defaults: `T=100.0 °C`, `P=0.5 bar`)
- `regeneration_target` — `{max_water_molefrac: float}` (default: `0.02`)
- `makeup_fraction` — `float` (default: `0.05`)
- `target` — `{product: str, max_water_molefrac: float | None}` or equivalent. If `max_water_molefrac` is set, the script may automatically increase `N_stages` and/or total DES absorbent flow within configured limits until the target is met.
- `base_template` — `"des_dehydration_regeneration"` (default and only option in V2)

If the request cannot be parsed unambiguously, stop and ask for clarification. Do not guess.

## Pipeline steps

### 1. Parse request into structured process spec

Extract a canonical structured spec. Required fields are listed in **Input**.

### 2. Select base template

In V2, always use the `des_dehydration_regeneration` base template. Future versions may choose from a template library by matching the request semantics.

### 3. Checkpoint: present structured spec for approval

Present a tight, decision-ready brief of the parsed spec and wait for explicit approval or edits. Include:

- DES formulation and mole ratio
- Gas feed composition and conditions
- Total DES absorbent flow rate, temperature, and pressure
- Column operating conditions (N_stages, T, P)
- Flash operating conditions (T, P)
- Regeneration target (max water mole fraction in regenerated DES)
- DES makeup fraction
- Target dry-gas water content
- Selected base template

Do not generate any code until the user approves the spec. This is the only mandatory checkpoint in V2.

### 4. Resolve chemical components

For each component referenced in the approved spec:

1. Check whether the component is already registered in the local ThermoSTEAM / BioSTEAM chemical registry with sufficient data.
2. For **DES components (HBA, HBD)**:
   - Invoke `compound-to-sigma` to generate sigma profile + COSMO `A`/`V` if missing.
   - Invoke `group-contribution-estimator` to generate `Tb`, `Tc`, `Pc`, `Vc`, `omega` if missing.
   - Invoke `heat-capacity-ann` to generate `Cp(T)` over 298–400 K if missing.
3. For the **DES pseudo-component**:
   - Compute mole-fraction-weighted sigma profile, `A`, and `V` from HBA/HBD.
   - Invoke `group-contribution-estimator` DES mixing-rules script with HBA/HBD critical properties and mole ratio to obtain pseudo-critical properties.
   - Invoke `heat-capacity-ann` using the pseudo-critical properties to obtain `Cp(T)` over 298–400 K.
4. For **feed components** (e.g., ethanol, water):
   - Use ThermoSTEAM built-ins when available.
   - If built-in data is insufficient or missing COSMOSAC support, invoke `compound-to-sigma`.
5. Register **feed components and the DES pseudo-component** in the flowsheet's thermo object and add COSMO-SAC profiles to `cosmosac_database.json`. Do not register HBA/HBD as separate simulation chemicals.
6. Set `tmo.settings.thermo_backend = 'clapeyron'`.

If any skill fails, stop immediately and report the failure. Do not fall back to placeholder data.

### 5. Generate / adapt BioSTEAM script

Using the approved spec and resolved components, generate a single runnable Python script that:

- Loads the selected base template from `.claude/skills/biosteam-process-builder/templates/des_dehydration.py`.
- Registers feed components and the DES pseudo-component.
- Configures the ThermoSTEAM backend to Clapeyron.
- Creates the gas feed stream (bottom of column) and fresh DES makeup stream.
- Instantiates a `ConditionedMixer` that combines fresh DES and the recycle stream.
- Instantiates a `MultiStageEquilibrium` absorber with `phases=('g', 'l')`, gas feed at stage `-1`, mixed DES at stage `0`, `algorithms=("sequential modular",)`.
- Instantiates a `Flash` that receives the absorber bottom liquid.
- Adds a `Splitter` that recycles `(1 − makeup_fraction)` of the regenerated flash liquid and purges the rest.
- Defines the `System`, sets the tear stream (splitter recycle outlet) and initial guess, and simulates it.
- If the regenerated DES water mole fraction exceeds `regeneration_target.max_water_molefrac`, performs a bounded search:
  1. Decrease flash pressure from the default in steps of 0.1 bar down to 0.05 bar.
  2. If still not met, increase flash temperature from the default in steps of 10 °C up to 150 °C.
  3. Stop as soon as the target is met or all bounds are exhausted.
- Optionally runs a one-at-a-time sensitivity analysis using the custom OAT loop in the template.

Save the script to:

```
.claude/skills/biosteam-process-builder/outputs/<run_id>/process.py
```

### 6. Run simulation

Execute the generated script in a clean Python environment. Capture stdout and stderr to a log file.

```
.claude/skills/biosteam-process-builder/outputs/<run_id>/log.txt
```

Run from the repository root with the local ThermoSTEAM package on `PYTHONPATH`:

```bash
PYTHONPATH=thermosteam \
    python .claude/skills/biosteam-process-builder/templates/des_dehydration.py
```

Data preparation (`prepare_des_dehydration_data.py`) must be run with `amspython` because it imports `scm.plams` / `CRSJob`:

```bash
amspython .claude/skills/biosteam-process-builder/templates/prepare_des_dehydration_data.py
```

### 7. Generate results brief

Produce a concise brief saved as:

```
.claude/skills/biosteam-process-builder/outputs/<run_id>/brief.md
```

The brief must contain:

- Key metrics:
  - Absorber energy duty (if available)
  - Dry CO₂ product purity and water removal fraction
  - Regenerated DES water mole fraction and comparison to target
  - Regenerated DES recycle flow rate
  - Flash water recovery fraction
  - Final flash operating T/P
  - Recycle convergence iterations
  - Regeneration target status (✓ / ✗)
- Compact stream table summary including:
  - Absorber gas feed, dry CO₂ top product, bottom liquid
  - Mixer outlet
  - Flash vapor and liquid products
  - Recycle and purge streams
- Absolute path to `process.py`
- Caveats or assumptions

## Output format

Return a tight summary to the user, not the raw script or log. Include:

- What was built
- Where `process.py` and `brief.md` are located
- Top-line results
- Whether the regeneration target was met
- Next step or caveat

## Sensitivity analysis (optional)

The generated script may include a disabled-by-default one-at-a-time (OAT) sensitivity block. When enabled, it sweeps:

- `N_stages`
- `DES_total_flow`
- `P_column`
- `T_gas`
- `x_water`
- `T_flash`
- `P_flash`
- `makeup_fraction`

Metrics:

- Water removal fraction
- Dry CO₂ water mole fraction
- Regenerated DES water mole fraction

Results are saved to `sensitivity.csv`. Sensitivity is off by default. Each evaluation runs in ~30–90 s.

## Output directory layout

```
.claude/skills/biosteam-process-builder/
├── SKILL.md
├── templates/
│   ├── des_dehydration.py
│   └── prepare_des_dehydration_data.py
├── inputs/
│   └── des_dehydration_data.yml
├── outputs/
│   └── <run_id>/
│       ├── process.py
│       ├── brief.md
│       ├── log.txt
│       └── sensitivity.csv  (if enabled)
└── examples/
    └── run_001/
        ├── process.py
        ├── brief.md
        └── _chemicals.yml
```

## Base template files

V2 ships with two reusable template scripts under `.claude/skills/biosteam-process-builder/templates/`:

- `prepare_des_dehydration_data.py` — generates COSMO-SAC profiles and registers them. Must be run with `amspython` (AMS Python 3.8) because it imports `scm.plams` / `CRSJob`. V2 still uses this to prepare sigma profiles for new HBA/HBD/feed components.
- `des_dehydration.py` — loads component data, registers chemicals, builds the Mixer + `MultiStageEquilibrium` + Flash + Splitter flowsheet with recycle, simulates in Clapeyron mode, and writes `brief.md` / `process.py`.

## Failure handling

| Failure | Behavior |
| --- | --- |
| Request cannot be parsed | Ask for clarification; do not proceed. |
| Component missing and `compound-to-sigma` fails | Stop; report failure; wait for human fix. |
| Clapeyron backend unavailable | Stop; report that V2 requires Julia/Clapeyron and suggest installing the backend. |
| Simulation fails | Capture error in `brief.md` and `log.txt`; stop. |
| Recycle loop does not converge | Report in `brief.md` and `log.txt`; stop. |
| Regenerated DES water content exceeds target after bounded search | Report actual value, final flash T/P, and mark target as not met in `brief.md`; do not stop. |
| Flash unit calculation fails | Capture error in `brief.md` and `log.txt`; stop. |
| User rejects structured spec at checkpoint | Apply edits and re-present the spec. |
| User requests unsupported variation (e.g., new unit connections in V2) | Explain V2 limitation and offer to record as future work. |

## Dependencies

- BioSTEAM and ThermoSTEAM installed and importable
- Julia and Clapeyron.jl backend available (V2 is rigorous mode only)
- `compound-to-sigma` skill for sigma profiles
- `group-contribution-estimator` skill for critical properties and DES mixing rules
- `heat-capacity-ann` skill for heat-capacity predictions
- AMS / ADF with COSMO-RS license if new sigma profiles are required
- `amspython`, `xtb`, `obabel` if `compound-to-sigma` runs
- `rdkit` for `group-contribution-estimator`

## Non-goals

- Sensitivity analysis is supported in V2 via a custom OAT loop, but it is disabled by default.
- A simple target-seeking loop may increase `N_stages` and/or total DES flow to meet a dry-CO₂ water-mole-fraction target. It is disabled by default.
- A bounded search may adjust flash T/P to meet a regenerated-DES water-mole-fraction target. It is enabled by default but does not optimize beyond the stated bounds.
- Do not generate PFD / diagram images in V2.
- Do not support non-DES base templates in V2.
- Do not model pumps, heat exchangers, compressors, valves, or other auxiliary equipment in V2.
- Do not optimize pressure levels between the absorber and the flash in V2; the flash pressure is an input.
- Do not perform detailed economic analysis / TAC in V2; only energy and flow metrics are reported.

## Example interaction

User: "Build a BioSTEAM flowsheet for choline chloride / glycerol dehydration of CO₂, 1:2 mole ratio, gas feed is 1000 kmol/hr of 95 mol% CO₂ / 5 mol% water at 40 C and 10 bar, total DES absorbent is 500 kmol/hr at 25 C and 10 bar, include a flash regenerator at 0.5 bar and 100 C, regenerate DES below 2 mol% water."

Workflow brief at checkpoint:

```
DES: choline chloride (HBA) / glycerol (HBD), 1:2 mole ratio
Gas feed: 1000 kmol/hr, 95 mol% CO₂ / 5 mol% H₂O, 40 C, 10 bar
Total DES absorbent: 500 kmol/hr, 25 C, 10 bar
  - Fresh makeup fraction: 0.05 (25 kmol/hr)
  - Recycled DES: 475 kmol/hr (initial guess)
Column: 5 stages, 10 bar
Flash: 0.5 bar, 100 C
Regeneration target: regenerated DES < 2 mol% water
Dry-gas target: dry CO₂ < 0.1 mol% water
Base template: des_dehydration_regeneration

Approve? (yes / edit / cancel)
```

After approval, the workflow resolves components, generates `process.py`, runs it, and returns `brief.md`.
