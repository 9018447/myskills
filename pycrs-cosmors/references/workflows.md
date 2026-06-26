# Workflow Coverage Map

## Foundational guides

| Source file | Main topic | Use when the user asks for |
| --- | --- | --- |
| `pyCRS Basic Usage.md` | database setup, activity coefficients, solid solubility, database bootstrap | the most common starting examples using pyCRS database + CRSManager |
| `Python scripting for COSMO-RS with PLAMS.md` | direct COSMO-RS scripting with PLAMS, command-line execution, problem types, compounds | explicit PLAMS settings or direct scripting instead of database-centric pyCRS examples |
| `Documentation.md` | conformer workflows for database and CRSManager | conformer generation, storing multiple conformers, or activity coefficients with conformers |
| `Documentation 14.md` | general information, overview, database, CRSManager | broad orientation or a quick "how is pyCRS organized?" answer |

## Property prediction and sigma workflows

| Source file | Main topic | Use when the user asks for |
| --- | --- | --- |
| `Documentation 1.md` | basic `PropPred` and `FastSigma` usage | physical-property estimation or fast sigma examples |
| `PropPred.md` | `PropPred.estimate(...)` API | exact property-prediction API behavior |
| `FaseSigma.md` | `FastSigma.estimate(...)` API | exact FastSigma API behavior |
| `Documentation 8.md` | calculating and estimating sigma profiles | sigma profile workflows, direct vs estimated profiles |
| `Documentation 9.md` | sigma moments | sigma moments and their calculation options |

## Phase equilibrium and mixture workflows

| Source file | Main topic | Use when the user asks for |
| --- | --- | --- |
| `Documentation 2.md` | partition coefficient via PLAMS | partitioning between phases such as octanol/water |
| `Documentation 4.md` | solubility screening for a solid solute | batch solubility calculations and screening |
| `Documentation 5.md` | screening for cocrystals | cocrystal screening via pyCRS or PLAMS |
| `Documentation 10.md` | eutectic systems | eutectic composition and temperature workflows |
| `Documentation 11.md` | binodal and spinodal curves | phase-diagram generation for binary or ternary mixtures |
| `Documentation 12.md` | multispecies distribution | distribution of species in multispecies calculations |

## Advanced screening and fitting workflows

| Source file | Main topic | Use when the user asks for |
| --- | --- | --- |
| `Documentation 3.md` | changing default parameters or re-parameterizing COSMO-RS / COSMO-SAC | custom parameter tuning or reparameterization |
| `Documentation 6.md` | regression of NRTL parameters | fitting NRTL parameters from reference activity-coefficient data |
| `Documentation 7.md` | automated screening of ionic liquids | ionic-liquid data prep and large screening workflows |
| `Documentation 13.md` | automated pKa calculation | pKa-oriented automation |

## Module/API source files

| Source file | Main topic |
| --- | --- |
| `Database API.md` | database classes and row objects |
| `CRSManager.md` | `CRSSystem` and `CRSMixture` |
| `Input.md` | molecule initialization helpers |
| `Molecule.md` | molecule object usage |
| `Output.md` | output writing helpers |
