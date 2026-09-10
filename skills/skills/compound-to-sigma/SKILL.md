---
name: compound-to-sigma
description: Use this skill whenever the user wants to compute, generate, run, explain, debug, plot, or convert COSMO-RS sigma profiles for ordinary compounds via the compound-to-sigma pipeline. Trigger for requests involving compound names, SMILES strings, xyz files, coskf files, ADFCRS-2018, ADF COSMO, xtb optimization, sigma-profile CSVs, or the `cosmo-skill` CLI — even if the user doesn't explicitly mention the skill name.
---

# compound-to-sigma

## Pipeline

```
name/SMILES/xyz/coskf → [check ADFCRS-2018] → 3D xyz → xtb opt → ADF COSMO → coskf → sigma profile
```

The pipeline is **database-first**: if ADFCRS-2018 already contains a matching coskf, the expensive steps are skipped. Authoritative defaults, parameter tables, and file layouts live in `workflows/compound-to-sigma.md`; read it when the user asks for exact behavior.

## Branches

- **Compute** — run the pipeline for one compound (`from_name` / `from_smiles`) or a batch (`from_names` / `cosmo-skill run config.yaml`).
  - Completion: every compound has a `*_sigma_profile.csv`, successes are returned, and failures are listed (not silent).
- **Explain** — summarize how the pipeline works or what a step does.
  - Completion: the user has an accurate summary drawn from `workflows/compound-to-sigma.md`.
- **Configure** — write a YAML config for the CLI.
  - Completion: the YAML is valid, each compound has exactly one of `name`/`smiles`/`xyz_path`/`coskf_path`, and `charge`/`multiplicity` are present where required.
- **Debug** — interpret errors or a failed run.
  - Completion: the failing step is identified and the user has a concrete next action. See `references/TROUBLESHOOTING.md`.
- **Plot/convert** — render or reformat an existing `*_sigma_profile.csv`.
  - Completion: the requested plot or file is produced from the CSV.

## Conventions

- Every compound needs explicit `charge` and `multiplicity`, except `coskf_path` inputs, which skip upstream steps.
- Valid input fields per compound: `name`, `smiles`, `xyz_path`, `coskf_path`. Exactly one.
- Before running, verify the environment: `$AMSBIN/amspython`, `xtb`, and `obabel` must be callable. If not, stop and tell the user to source `amsbashrc.sh` or install the missing tool.
- If `output_dir/<name>/<name>.coskf` already exists, skip that compound (resume behavior). To force recomputation, delete the file or output directory.
- Batch failures are collected; the CLI exits non-zero but still writes successful outputs.

## Quick reference

**Python API**

```python
from compound_to_sigma import from_name, from_smiles, from_names, from_coskf

from_name(name="ethanol", charge=0, multiplicity=1, output_dir="./out")
from_smiles(smiles="C[N+](C)(C)CCO", charge=1, multiplicity=1, name="choline_cation", output_dir="./out")
from_names(compounds=[...], output_dir="./out", n_jobs=2)
from_coskf(coskf_path="/path/to/water.coskf", output_dir="./out")
```

**CLI**

```bash
cosmo-skill run config.yaml
cosmo-skill run config.yaml --dry-run
```

For the step-by-step debugging checklist, see `references/TROUBLESHOOTING.md`. For the full spec, see `workflows/compound-to-sigma.md`.
