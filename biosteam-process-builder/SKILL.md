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

## Workflow

Follow `workflows/biosteam-process-builder.md` as the source of truth.

### 1. Parse the request

Extract a structured spec with at least:

- `des`: `{hba, hbd, ratio}`
- `gas_feed`: `{CO2, Water, inert: {ID, flow} | None, T, P, flow_basis}`
  - V2 supports CO₂ + Water plus one optional inert gas (e.g., N₂). The inert is absorbed physically via Henry's law / activity coefficients; chemical absorption is out of scope. Other absorbable components are out of scope.
- `absorbent`: `{flow_rate, T, P}`
  - This is the **total DES flow entering the mixer** (fresh makeup + regenerated recycle).
- `column`: `{N_stages, P}`
- `flash`: `{T, P}` (defaults: `T=100 °C`, `P=0.5 bar`)
- `regeneration_target`: `{max_water_molefrac}` (default: `0.02`)
- `makeup_fraction`: `float` (default: `0.05`)
- `target`: `{product, max_water_molefrac}` or equivalent (dry-CO₂ water target; optional)
- `base_template`: `"des_dehydration_regeneration"` in V2

If anything is ambiguous, ask one clarifying question at a time.

### 2. Checkpoint: present the structured spec

Push the checkpoint right: do all parsing first, then present a tight brief for approval. Do not write code before approval.

The brief must include:

- DES formulation and ratio
- Gas feed composition and conditions
- Total DES absorbent flow rate, temperature, and pressure
- Makeup fraction and implied fresh makeup / recycle split
- Column conditions (N_stages, P)
- Flash conditions (T, P)
- Regeneration target (max water mole fraction in regenerated DES)
- Target dry-gas water content (if specified)
- Selected base template

Wait for explicit `yes`, `edit`, or `cancel`.

### 3. Resolve chemical components

For each component in the approved spec:

- Check whether it is already registered in the local ThermoSTEAM / BioSTEAM registry.
- For HBA/HBD:
  - Invoke `compound-to-sigma` for sigma profile + COSMO `A`/`V`.
  - Invoke `group-contribution-estimator` for `Tb`, `Tc`, `Pc`, `Vc`, `omega`.
  - Invoke `heat-capacity-ann` for `Cp(T)` over 298–400 K.
  - **Do not register HBA/HBD as separate simulation chemicals**; only the DES pseudo-component and feed components are registered.
- For the DES pseudo-component:
  - Compute mole-fraction-weighted sigma profile, `A`, and `V` from HBA/HBD.
  - Invoke `group-contribution-estimator` Lee–Kesler DES mixing rules for pseudo-critical properties.
  - Invoke `heat-capacity-ann` using pseudo-critical properties for `Cp(T)`.
- For feed components, use ThermoSTEAM built-ins when possible; otherwise invoke `compound-to-sigma`.
- If any skill fails, stop and report clearly.

### 4. Generate the BioSTEAM script

Produce a single runnable Python script starting from:

```
workflows/biosteam-process-builder/templates/des_dehydration.py
```

(V2 uses the `des_dehydration_regeneration` base template implemented in that file.)

It should:

- Load `../inputs/des_dehydration_data.yml` (created by `prepare_des_dehydration_data.py`)
- Register feed components and the DES pseudo-component
- Set the ThermoSTEAM backend to Clapeyron (`COSMOSAC2013`)
- Create the gas feed stream (bottom stage `-1`) and fresh DES makeup stream
- Instantiate a `ConditionedMixer` that combines fresh DES and the regenerated recycle stream
- Instantiate a `MultiStageEquilibrium` absorber with `phases=('g', 'l')` and `algorithms=("sequential modular",)`
- Instantiate a `Flash` that receives the absorber bottom liquid
- Add a `Splitter` that recycles `(1 - makeup_fraction)` of the regenerated flash liquid and purges the rest
- Define and converge the recycle `System` with the splitter recycle outlet as the tear stream
- Save results

Save to:

```
workflows/biosteam-process-builder/outputs/<run_id>/process.py
```

### 5. Run the simulation

Execute the script and capture stdout/stderr to:

```
workflows/biosteam-process-builder/outputs/<run_id>/log.txt
```

Run from the repository root with the local ThermoSTEAM package on `PYTHONPATH`:

```bash
PYTHONPATH=/home/smh/biosteam/thermosteam \
    python workflows/biosteam-process-builder/templates/des_dehydration.py
```

Data preparation (`prepare_des_dehydration_data.py`) must be run with `amspython` because it imports `scm.plams` / `CRSJob`.

### 6. Deliver the brief

Write `brief.md` with:

- Key metrics:
  - Dry CO₂ product purity and water removal fraction
  - Regenerated DES water mole fraction and comparison to target
  - Regenerated DES recycle flow rate
  - Flash water recovery fraction
  - Final flash operating T/P
  - Recycle convergence iterations
  - Dry-CO₂ target status (if specified)
- Compact stream table including absorber feed/products, mixer outlet, flash products, recycle, and purge
- Path to `process.py`
- Caveats

## Output format

Return a tight summary to the user, not the raw script or log. Include:

- What was built
- Where `process.py` and `brief.md` are located
- Top-line results
- Whether the regeneration target was met
- Next step or caveat

## Error handling

- Parsing failure: ask the user for clarification.
- Missing component + `compound-to-sigma` failure: stop and report.
- Simulation failure: capture error in `log.txt`, then stop. `brief.md` is written when possible.
- Regenerated DES water content exceeds target after bounded flash T/P search: report the actual value and mark the target as not met; do not stop.
- Recycle loop does not converge: report in `brief.md` and `log.txt`; stop.
- User rejects spec: edit and re-present.
- User asks for unsupported V2 scope (new unit connections, non-DES templates, pumps/HX/compressors): explain the limitation and offer to record it as future work.

## Thermodynamics

- Default model: **COSMOSAC2013** via ThermoSTEAM Clapeyron backend. V2 is rigorous-mode only.
- DES is modeled as a **pseudo-component** derived from HBA + HBD at the requested mole ratio.
- Only the DES pseudo-component and feed components are registered in the flowsheet. HBA/HBD properties are generated and stored, but they are not separate simulation chemicals because mixed composition lengths break the Clapeyron subset VLE backend.
- Property generation:
  - `compound-to-sigma` → sigma profile + COSMO `A`/`V` for HBA/HBD.
  - `group-contribution-estimator` → `Tb`, `Tc`, `Pc`, `Vc`, `omega` for HBA/HBD; Lee–Kesler mixing rules for DES pseudo-critical properties.
  - `heat-capacity-ann` → `Cp(T)` over 298–400 K for HBA/HBD and DES.
- DES sigma profile: mole-fraction-weighted average of HBA/HBD profiles.
- Reference state: `phase: l`, `phase_ref: l`, `Hf: 0`.
- Non-volatile assumption for DES: `Psat = 1e-6 Pa`, `Hvap = 5e4 J/mol`.

## Scope boundaries

V2 supports only:

- DES dehydration-regeneration base template (`des_dehydration_regeneration`)
- Fixed unit structure: `Mixer → MultiStageEquilibrium absorber → Flash → Splitter` with DES recycle
- Rigorous Clapeyron/COSMOSAC thermodynamics
- Varying DES components, feed mixture, column stages, flash T/P, regeneration target, and makeup fraction

Do not promise or implement automatic unit-connection changes, optimization, PFD generation, non-DES templates, or auxiliary equipment (pumps, heat exchangers, compressors, valves) in V2.
