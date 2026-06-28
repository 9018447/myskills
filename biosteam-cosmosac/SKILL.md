---
name: biosteam-cosmosac
description: >-
  End-to-end workflow for defining a new component in biosteam/thermosteam,
  generating its COSMO-RS sigma profile with compound-to-sigma (ADF COSMO + xtb),
  converting it to Clapeyron.jl COSMOSAC format, registering it in a thermosteam
  Chemicals object, and validating the backend. Use this skill whenever the user
  wants to add a custom chemical, compute sigma profiles, connect biosteam to
  Clapeyron.jl, use COSMO-SAC as a thermodynamic model, or handle ions / charged
  species in biosteam. Trigger even if the user only mentions one of these pieces
  (e.g. "new component", "sigma profile", "COSMOSAC", "Clapeyron backend").
---

# biosteam-cosmosac

End-to-end workflow: **biosteam/thermosteam custom component → COSMO-RS sigma profile → Clapeyron.jl COSMOSAC backend → validation**.

Use this skill when the user asks for anything involving:

- Defining a new chemical component in biosteam or thermosteam
- Generating COSMO-RS / COSMO-SAC sigma profiles
- Connecting biosteam to Clapeyron.jl or COSMOSAC
- Custom components, ions, or charged species in process simulation
- Validating activity coefficients or thermodynamic backends

## Pipeline overview

```
name/SMILES/xyz/coskf
        │
        ▼
[ADFCRS-2018 database lookup]  ──►  existing coskf
        │
        ▼
[compound-to-sigma]  ──►  xtb opt  ──►  ADF COSMO  ──►  coskf  ──►  sigma profile
        │
        ▼
[Clapeyron bridge]  ──►  A, V, Pnhb, POH, POT
        │
        ▼
[thermosteam YAML/JSON]  ──►  load_chemicals_from_yaml  ──►  compile  ──►  Thermo
        │
        ▼
[validation]  ──►  pytest / validation scripts
```

## What the skill does

1. **Define the component** in a thermosteam YAML file with `search_db: false`, formula, and (optionally) critical properties.
2. **Generate the sigma profile** using the `compound-to-sigma` package:
   - `from_name(name, charge, multiplicity)` for common names
   - `from_smiles(smiles, charge, multiplicity, name=...)` for explicit SMILES (recommended for ions)
   - `from_coskf(coskf_path)` if the user already has a coskf
3. **Convert to Clapeyron COSMOSAC format** with `compound_to_sigma.extract_clapeyron_profile()`.
4. **Write thermosteam YAML/JSON** that can be loaded with `tmo.load_chemicals_from_yaml()`.
5. **Register the backend** by compiling the chemicals and creating a `tmo.Thermo(chemicals)` with COSMOSAC.
6. **Validate** with pytest tests or standalone scripts:
   - YAML loads correctly
   - Profiles have 51 sigma points
   - Activity coefficients are finite and positive
   - For ions, the profile density sits on the correct side of the sigma axis

## Conventions

- Always run ADF / CRSJob steps with `amspython` (the AMS-bundled Python).
- Every compound needs explicit `charge` and `multiplicity`.
- For ions (`charge != 0`), the runner uses ADF COSMO single-point mode on the xtb-optimized geometry to avoid AMS input conflicts.
- If a component is not in the Clapeyron database, the backend falls back to `BasicIdeal` pure model for COSMOSAC (because ions lack critical properties).
- Keep generated artifacts:
  - `examples/<name>_cosmosac.yml`
  - `examples/<name>_cosmosac.json`
  - `sigma_profiles/<compound>/` with `.coskf`, `_sigma_profile.csv`, and geometry files

## Quick reference

### Python API

```python
from compound_to_sigma import from_smiles, extract_clapeyron_profile

# 1. Generate profile for an ion
result = from_smiles(
    smiles="C[N+](C)(C)CCO",
    charge=1,
    multiplicity=1,
    name="choline_cation",
    output_dir="sigma_profiles",
    method="COSMOSAC2013",
    verbose=1,
)

# 2. Convert to Clapeyron COSMOSAC profile
profile = extract_clapeyron_profile(result["coskf_path"], method="COSMOSAC2013")

# 3. Load in thermosteam
import thermosteam as tmo
chemicals = tmo.load_chemicals_from_yaml("examples/choline_chloride_cosmosac.yml")
chemicals.compile(skip_checks=True)
tmo.settings.set_thermo(chemicals)

# 4. Activity coefficients
thermo = tmo.settings.thermo
gamma = thermo._clapeyron_backend.activity_coefficient(101325, 298.15, [0.5, 0.5])
```

### CLI

```bash
# Generate profiles for a set of ions / neutral compounds
amspython scripts/generate_ion_clapeyron_profiles.py

# Validate existing YAML
python scripts/validate_ion_clapeyron_profiles.py

# Run tests
pytest tests/test_ion_clapeyron_profiles.py -v -p no:nbval -o addopts="" --disable-numba=1
```

## Input formats

Per compound, exactly one of:

| Field | Meaning |
| --- | --- |
| `name` | Common / IUPAC / CAS name; resolved to SMILES |
| `smiles` | Explicit SMILES string (best for ions) |
| `xyz_path` | Existing 3D geometry |
| `coskf_path` | Existing ADF coskf file |

Required for all except `coskf_path`:

- `charge` — integer molecular charge
- `multiplicity` — integer spin multiplicity

## YAML output format

```yaml
chemicals:
  choline_cation:
    search_db: false
    names:
      common_name: choline_cation
      formula: C5H14NO+
    cosmo:
      A: 151.263570
      V: 148.181002
      Pnhb: [ ... 51 values ... ]
      POH:  [ ... 51 values ... ]
      POT:  [ ... 51 values ... ]
```

## Validation checklist

- [ ] `tmo.load_chemicals_from_yaml()` succeeds
- [ ] `chemicals.compile(skip_checks=True)` succeeds
- [ ] `tmo.Thermo(chemicals)` builds a Clapeyron COSMOSAC backend
- [ ] `activity_coefficient(P, T, z)` returns finite, positive values
- [ ] For ions: formula includes charge (`C5H14NO+`, `Cl-`) and `chem.charge` is correct
- [ ] For ions: cation profile density is on the negative-sigma side, anion on the positive-sigma side

## Known limitations

- Custom components not in the Clapeyron database need critical properties for the default PR pure model. Ions lack these, so the backend falls back to `BasicIdeal`. This is fine for activity coefficients but limits VLE / real-fluid property accuracy.
- `pytest.ini` in this repo enables `nbval`; run targeted tests with `-p no:nbval -o addopts=""`.
- `import biosteam` may fail in the default Python due to local thermosteam signature mismatches; use `thermosteam` directly for validation.

## Dependencies

- AMS / ADF with COSMO-RS license (`amspython`, `scm.plams`)
- `xtb`, `obabel`
- `compound_to_sigma` (project-local)
- `thermosteam` (editable from `thermosteam/`)
- `pyclapeyron` and Julia with `Clapeyron.jl`
- `pytest`, `numpy`, `pyyaml`
