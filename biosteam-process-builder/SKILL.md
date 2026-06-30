---
name: biosteam-process-builder
description: Build and run BioSTEAM chemical process simulations from a free-form request. V1 starts from a DES dehydration base template and supports varying DES components, feed mixture, and operating conditions. Always confirm the structured process spec before generating any code.
---

# biosteam-process-builder

## When to use

Activate when the user asks to build or simulate a chemical process in BioSTEAM, especially requests like:

- "Build a BioSTEAM flowsheet for DES dehydration."
- "Simulate choline chloride / glycerol dehydration in BioSTEAM."
- "Create a BioSTEAM process for separating water with a deep eutectic solvent."
- "BioSTEAM flowsheet for [chemical separation / solvent dehydration]."

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
  - V1 supports CO₂ + Water plus one optional inert gas (e.g., N₂). The inert is absorbed physically via Henry's law / activity coefficients; chemical absorption is out of scope. Other absorbable components are out of scope.
- `absorbent`: `{flow_rate, T, P}`
- `column`: `{N_stages, P}`
- `target`: `{product, max_water_molefrac}` or equivalent
- `base_template`: `"des_dehydration"` in V1

If anything is ambiguous, ask one clarifying question at a time.

### 2. Checkpoint: present the structured spec

Push the checkpoint right: do all parsing first, then present a tight brief for approval. Do not write code before approval.

The brief must include:

- DES formulation and ratio
- Gas feed composition and conditions
- DES absorbent flow rate and conditions
- Column conditions (N_stages, P)
- Target dry-gas water content
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

Produce a single runnable Python script that starts from:

```
workflows/biosteam-process-builder/templates/des_dehydration.py
```

It should:

- Load `../inputs/des_dehydration_data.yml` (created by `prepare_des_dehydration_data.py`)
- Registers feed components and the DES pseudo-component
- Uses **fast mode** by default: native ThermoSTEAM backend with precomputed constant partition coefficients from the YAML (runs in <10 s per case)
- Optionally uses **rigorous mode**: COSMOSAC2013 via the Clapeyron backend (slower, more general; set `OPTIMIZATION["rigorous"] = True`)
- Creates the gas feed stream (bottom stage `-1`) and DES absorbent stream (top stage `0`)
- Instantiates a `MultiStageEquilibrium` absorber with `phases=('g', 'l')` and `algorithms=("sequential modular",)`
- Defines and simulates the `System`
- Saves results

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

- Key metrics (energy duty, purity, recovery, TAC if available)
- Compact stream table
- Path to `process.py`
- Caveats

## Output format

Return a tight summary to the user, not the raw script or log. Include:

- What was built
- Where `process.py` and `brief.md` are located
- Top-line results
- Speed/accuracy mode used (fast constant-K vs rigorous COSMOSAC)
- Next step or caveat

## Error handling

- Parsing failure: ask the user for clarification.
- Missing component + `compound-to-sigma` failure: stop and report.
- Simulation failure: capture error in `log.txt`, then stop. `brief.md` is only written on success.
- User rejects spec: edit and re-present.
- User asks for unsupported V1 scope (new unit connections, non-DES templates): explain the limitation and offer to record it.

## Thermodynamics

- **Fast mode (default)**: native ThermoSTEAM backend with constant gas/liquid partition coefficients extracted from a rigorous COSMOSAC run at the default operating point. Runs in <10 s per case.
- **Rigorous mode (optional)**: **COSMOSAC2013** via ThermoSTEAM Clapeyron backend. Runs in ~30–90 s per case. Toggle with `OPTIMIZATION["rigorous"]` in the generated script.
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

V1 supports only:

- DES dehydration base template
- Varying DES components, feed mixture, and operating conditions
- Fixed unit structure

Do not promise or implement automatic unit-connection changes, optimization, PFD generation, or non-DES templates in V1.
