# Overview

## Purpose

This repository documents pyCRS usage across two main modes:

1. **pyCRS database-driven workflows** using `pyCRS.Database`, `pyCRS.CRSManager`, `PropPred`, and `FastSigma`
2. **Direct COSMO-RS scripting with PLAMS** where settings and problem types are built explicitly

## Common environment assumptions

- pyCRS is used with SCM/AMS tooling.
- COSMO calculations typically rely on `.coskf` inputs.
- Many examples require an installed `ADFCRS-2018` database or a user-specified database path.
- Some workflows require additional downloaded COSKF bundles called out by the docs.

## Common script shape

Use this structure when building or adapting examples:

```python
from scm.plams import Settings, init
import pyCRS

# 1. Configure environment / database path
DATABASE_PATH = "/path/to/database-or-coskf-dir"

# 2. Initialize PLAMS if needed
init()

# 3. Define molecules, database, or mixture/problem settings
# 4. Run the pyCRS / PLAMS workflow
# 5. Extract results and optionally plot them
```

## Frequent user intents

- add compounds or conformers to a COSKF database
- estimate properties from structure or from molecule objects
- calculate activity coefficients or partition coefficients
- build solubility / cocrystal / ionic-liquid screening workflows
- generate sigma profiles or sigma moments
- derive phase diagrams such as eutectic or binodal/spinodal curves
- script COSMO-RS jobs directly with PLAMS

## Common caveats to mention

- Database paths are often placeholders in the docs; keep them explicit.
- If a workflow names a required dataset such as `coskf_solubility`, `coskf_Hex`, `coskf_IL`, or `coskf_acetic_acid`, mention that requirement.
- Result structures may differ between direct jobs and `CRSManager` iteration workflows; explain what object or container the user should inspect.

## Fast route for answers

- Need a module summary: read `api-modules.md`
- Need the best example file: read `workflows.md`
- Need exact source provenance: read `source-map.md`
