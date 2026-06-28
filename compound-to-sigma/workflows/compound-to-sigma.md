# compound-to-sigma

## Purpose

End-to-end workflow that turns an ordinary compound identifier into a COSMO-RS sigma profile:

```
name/SMILES/xyz/coskf  →  [check ADFCRS-2018]  →  3D xyz  →  xtb-optimized geometry  →  ADF COSMO  →  coskf  →  sigma profile
```

If the compound already exists in the ADFCRS-2018 database, its coskf file is copied and used directly, skipping all expensive DFT/xtb steps.

The workflow is the source of truth for the `compound-to-sigma` Kimi skill and for any Python package / CLI that implements it.

## Trigger

Event-driven: a user supplies one or more compounds and asks for their sigma profiles.

- Single compound: `from_name(name, charge, multiplicity)`
- Batch: `from_names(compounds, n_jobs=N)`
- CLI: `cosmo-skill run config.yaml`

## Inputs

Four input types are supported. Exactly one of the following fields must be provided per compound:

| Field | Meaning |
| --- | --- |
| `name` | Common name, IUPAC name, or CAS. Resolved to SMILES via PubChem (primary) → CIR (fallback). |
| `smiles` | Canonical or isomeric SMILES string. |
| `xyz_path` | Path to an existing 3D xyz file. Skips name/SMILES resolution and obabel. |
| `coskf_path` | Path to an existing ADF coskf file. Skips all upstream steps and extracts sigma profile only. |

Every compound **must** also provide:

- `charge` — integer molecular charge
- `multiplicity` — integer spin multiplicity

Additional global settings:

- `database_path` — path to the ADFCRS-2018 database. Default: `$SCM_PKG_ADFCRSDIR/ADFCRS-2018`. If the variable is unset or the directory does not exist, database lookup is skipped with a warning.

## Pipeline steps

### 1. Environment check

Before any work, verify that the following are callable:

- `$AMSBIN/amspython`
- `xtb`
- `obabel`

If any are missing, fail fast with a clear message telling the user to source `amsbashrc.sh` and/or install the missing tool.

### 2. Name → SMILES (only for `name` input)

- Query PubChem PUG-REST by name.
- If PubChem fails or returns no match, query NCI/CADD Chemical Identifier Resolver (CIR).
- If multiple candidates are returned, apply heuristic filtering (e.g. match molecular formula implied by the name, prefer exact synonym match, prefer single-component results).
- If still ambiguous, record a failure for this compound and continue.

### 3. Query ADFCRS-2018 database (only when a SMILES is available)

- If `database_path` is valid, search the database for an existing coskf matching this compound.
- Matching strategy:
  1. **SMILES match (preferred):** read the SMILES metadata from each coskf file via `KFFile` and compare to the resolved/input SMILES.
  2. **Name match (fallback):** normalize the compound name and compare to normalized coskf filenames.
- If a match is found, copy the database coskf to `output_dir/<compound_name>/<compound_name>.coskf` and skip directly to sigma-profile extraction.
- If no match is found, continue with the full pipeline.

### 4. SMILES → 3D xyz (only for `name` or `smiles` input, and only if no database match)

- Use Open Babel with fixed arguments: `--gen3d -O <output>.xyz`
- Output: `output_dir/<compound_name>/<compound_name>.xyz`

### 5. xyz → xtb-optimized xyz (skipped if input is `xyz_path`, `coskf_path`, or a database match was found)

- Run `xtb <input>.xyz --opt --gfn 2 --chrg <charge> --uhf <multiplicity-1>` in the compound directory.
- Use the gas-phase GFN2-xTB method. No solvent model.
- Output: `output_dir/<compound_name>/<compound_name>_xtbopt.xyz`

### 6. xtb-optimized xyz → coskf (skipped if a database match was found)

- Run the ADF COSMO-RS compound workflow using the SCM `ADFCOSMORSCompoundJob` PLAMS recipe with `singlepoint=False`.
- This performs a **geometry optimization** in the gas phase (BP86/TZP) followed by a **single-point calculation with implicit solvation** (COSMO).
- The recipe applies the standard COSMO-RS compound settings (Delley surface, CRS solvent, Klamt/Allinger radii) and directly produces a `.coskf` file.
- These settings are fixed; no user override is allowed.
- Copy the resulting coskf to `output_dir/<compound_name>/<compound_name>.coskf`.

### 7. coskf → sigma profile

- Run a PLAMS `CRSJob` with `property._h = "SIGMAPROFILE"`.
- The `method` parameter is exposed to the user (e.g. `COSMO-RS`, `COSMOSAC2013`, `COSMOSAC2016`).
- Extract from the results:
  - `chdval` — charge density σ values
  - `profil` — total sigma profile
  - `hbprofil` — hydrogen-bond sigma profile (for COSMO-RS) or split profiles (for COSMO-SAC variants)

### 8. Output formatting

- Return the sigma profile as a pandas DataFrame with columns:
  - `sigma` (from `chdval`)
  - `total_profile` (from `profil`)
  - `hb_profile` (from `hbprofil` for COSMO-RS; for COSMO-SAC variants split into additional columns as returned by CRSJob)
- Save the same data to `output_dir/<compound_name>/<compound_name>_sigma_profile.csv`.

## Output directory layout

If the coskf came from the ADFCRS-2018 database, `xyz` and `xtbopt.xyz` are not present.

```
output_dir/
├── log.txt
├── ethanol/
│   ├── ethanol.xyz                 # present only if generated
│   ├── ethanol_xtbopt.xyz          # present only if xtb ran
│   ├── ethanol.coskf               # copied from DB or generated by ADF
│   └── ethanol_sigma_profile.csv
├── benzene/
│   ├── benzene.xyz
│   ├── benzene_xtbopt.xyz
│   ├── benzene.coskf
│   └── benzene_sigma_profile.csv
└── ...
```

## Resume behavior

If `output_dir/<compound_name>/<compound_name>.coskf` already exists, skip the compound and proceed directly to sigma-profile extraction. This takes precedence over database lookup.

If no local coskf exists, the pipeline first tries the ADFCRS-2018 database. Only if the database does not contain a match does it run xtb + ADF.

To force recomputation, the user must delete the existing coskf or output directory.

## Failure handling

Batch runs use a tolerant strategy:

- A failure in any step for one compound does not stop the batch.
- Failures are recorded in `output_dir/log.txt`.
- The Python API returns two lists:
  - `successes` — list of result objects
  - `failures` — list of `{name, input, step, error}` dictionaries
- The CLI exits with non-zero status if any compound failed, but still writes outputs for successful compounds.

## Python API

```python
from compound_to_sigma import from_name, from_names

# single compound
result = from_name(
    name="ethanol",
    charge=0,
    multiplicity=1,
    output_dir="./out",
    database_path="$SCM_PKG_ADFCRSDIR/ADFCRS-2018",  # optional
    method="COSMO-RS",
    verbose=1,
)
# result is a dict-like object with:
#   name, smiles, coskf_path, csv_path, source ("database" | "calculated"), sigma_profile (DataFrame)

# batch
results = from_names(
    compounds=[
        {"name": "ethanol", "charge": 0, "multiplicity": 1},
        {"smiles": "CCO", "charge": 0, "multiplicity": 1},
        {"xyz_path": "/path/to/benzene.xyz", "charge": 0, "multiplicity": 1},
        {"coskf_path": "/path/to/water.coskf"},
    ],
    output_dir="./out",
    database_path="$SCM_PKG_ADFCRSDIR/ADFCRS-2018",  # optional
    n_jobs=2,
    method="COSMO-RS",
    verbose=1,
)
# results = {"successes": [...], "failures": [...]}
```

## CLI

```bash
# run from YAML config
cosmo-skill run config.yaml

# dry-run: validate inputs, dependencies, and environment only
cosmo-skill run config.yaml --dry-run
```

### Example YAML config

```yaml
output_dir: ./sigma_profiles
database_path: $SCM_PKG_ADFCRSDIR/ADFCRS-2018  # optional; env vars expanded
n_jobs: 2
method: COSMO-RS
verbose: 1

compounds:
  - name: ethanol
    charge: 0
    multiplicity: 1

  - smiles: CCO
    charge: 0
    multiplicity: 1

  - xyz_path: /path/to/benzene.xyz
    charge: 0
    multiplicity: 1

  - coskf_path: /path/to/water.coskf
```

## Verbosity levels

- `0` — silent except for fatal errors
- `1` — normal progress, tqdm bar for batches, step labels
- `2` — print full underlying command stdout/stderr

## Key parameters

| Parameter | Meaning | Default |
| --- | --- | --- |
| `output_dir` | Directory for all outputs | `./compound-to-sigma-outputs` |
| `database_path` | Path to ADFCRS-2018 database; env vars expanded | `$SCM_PKG_ADFCRSDIR/ADFCRS-2018` if set |
| `method` | CRSJob method for sigma-profile extraction | `COSMO-RS` |
| `n_jobs` | Parallel compounds for batch runs | `1` |
| `verbose` | Output level: 0 silent, 1 progress, 2 full command output | `1` |

## Dependencies

- AMS / ADF with COSMO-RS license (`$AMSBIN` set, `amspython` available)
- xtb
- Open Babel (`obabel`)
- Python packages: `scm.plams`, `pandas`, `tqdm`, `requests`

## Testing

- Unit tests mock network calls, xtb, ADF, and CRSJob.
- Integration tests run the real pipeline on a small set of compounds (e.g. water, ethanol) and are marked `slow`.
- CI runs unit tests on every push; integration tests run manually or on schedule.

## Non-goals

- Do not optimize or fit sigma profiles to experimental data.
- Do not override ADF functional, basis, or solvation defaults.
- Do not perform conformer searching or averaging (single lowest-energy xtb geometry only).
- Do not automatically assign charge/multiplicity.
