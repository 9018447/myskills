---
title: "CRSManager"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/CRSManager.html#pycrs-crsmanager"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## CRSManager

This submodule facilitate the creation, execution, and output processes for mutiple `crsJob` and is intended to be used in conjunction with the pyCRS.database module.

*class* pyCRS.CRSManager.CRSSystem(*iteration=False*) [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem)

This class manages multiple CRSMixture instances, handling their creation, execution, and result collection. Use add\_Mixture() to append CRSMixture objects to the mixture list; results are stored in outputs with the same order. Requires pyCRS.database for COSKF access.

iteration [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.iteration)

Enable iteration mode; mixtures will manage CRSIteration instead of a single CRSJob.

Type:

[`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")

num\_mix [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.num_mix)

Number of mixtures managed by this CRSSystem.

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

mixture [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.mixture)

Ordered list of mixtures in this system.

Type:

`list[CRSMixture]`

outputs [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.outputs)

Results aligned to mixture order.

Type:

`list[CRSResults]`

Architecture

CRSSystem ├─ mixture: list\[CRSMixture\] │ ├─ (iteration=False) ──> crs\_job \[CRSJob\] │ └─ (iteration=True) ──> crs\_iteration \[CRSIteration\] ──> crs\_job \[CRSJob\] └─ outputs: list\[CRSResults\]

Notes

Use runCRSJob() when iteration is False; use runCRSIteration() when iteration is True.

Example

```python
db = COSKFDatabase("my_coskf_db.db")
crs = CRSSystem()
crs.add_Mixture(mixture={"ethanol": 0.0, "water":1.0}, database=db)
crs.runCRSJob()
res = crs.outputs[0].get_results()
print(f"{res['temperature']} : {res['gamma']}")
```

```python
db = COSKFDatabase("my_coskf_db.db")
crs = CRSSystem(iteration=True)
crs.add_Mixture(mixture={"ethanol": 0.0, "water":1.0}, database=db)
crs.runCRSIteration()
act = cal.get_activity_coefficients()
print(f"activity coefficient of mixture0: comp0: point0={act[0][0][0]:.4f}")

parameter_sett = Settings()
parameter_sett.input.CRSParameters.aeff = 6.5
cal.runCRSIteration(parameter_sett=parameter_sett)
act = cal.get_activity_coefficients()
print(f"activity coefficient of mixture0: comp0: point0={act[0][0][0]:.4f}")
```

add\_Mixture(*mixture: [dict](https://docs.python.org/3.8/library/stdtypes.html#dict "(in Python v3.8)")*, *temperature: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)") | [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 298.15*, *problem\_type: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'activitycoef'*, *database: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [COSKFDatabase](https://www.scm.com/doc/COSMO-RS/pyCRS/Database.html#pyCRS.Database.COSKFDatabase "pyCRS.Database.COSKFDatabase.COSKFDatabase") = 'my\_coskf\_db.db'*, *method: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'COSMORS'*, *pressure: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)") | [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 1.01325*, *jobname: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *conformer: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*, *massfraction: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*, *density\_corr: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*, *vp\_corr: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*, *solute: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'solid'*, *iso: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'isotherm'*, *additional\_sett: Settings | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *multi\_species: [dict](https://docs.python.org/3.8/library/stdtypes.html#dict "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.add_Mixture)

Adds a new `CRSMixture` to the **mixture** attribute of the `CRSSystem`.

Parameters:

**mixture** ([`dict`](https://docs.python.org/3.8/library/stdtypes.html#dict "(in Python v3.8)")) – Composition as {Identifier: mole/mass fraction}

Keyword Arguments:

- **temperature** (`float or str`) – Temp in Kelvin (default 298.15). If str, format can be “T1” or “T1 T2 ntemp”. Where T1 is the starting temperature, T2 is the ending temperature, and ntemp is the number of intervals between T1 and T2.
- **problem\_type** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Calculation type (default “activitycoef”).
- **database** (`str or COSKFDatabase`) – Path or instance of COSKFDatabase (default “my\_coskf\_db.db”).
- **method** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Version of COSMORS or COSMOSAC (default “COSMORS”).
- **pressure** (`float or str`) – Pressure in bar (default 1.01325). If str, format can be “P1” or “P1 P2 npress”. Where P1 is the starting pressure, P2 is the ending pressure, and npress is the number of intervals between P1 and P2.
- **jobname** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Job name in plam\_workdir (defaults “crsJob\_n”).
- **conformer** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – Use multiple conformers in COSMO-RS (default False).
- **massfraction** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – Input fraction as mass (default False).
- **density\_corr** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – Use pure compound density for volume. Default to False (uses COSMO volume).
- **vp\_corr** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – Correct gas phase chemical potential with vapor pressure (default False).
- **solute** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Solute state (“solid”, “gas”, “liquid”) in SOLUBILITY and PURESOLUBILITY. Default is “solid”.
- **iso** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Condition (“isotherm”, “isobar”, “flashpoint”) for BINMIXCOEF, TERNARYMIX, and COMPOSITIONLINE. Default is “isotherm”.
- **additional\_sett** (`Settings`) – Optional custom settings (default None).
- **multi\_species** ([`dict`](https://docs.python.org/3.8/library/stdtypes.html#dict "(in Python v3.8)")) – Multi-species settings as {Identifier: Settings} (default None).

> [!note] Note
> The identifiers for a compound can be the name, CAS number, or identifier in the pyCRS.database. When searching in the database, the input string will be converted to lowercase, except when it starts with ‘InChI’.

The available problem types are listed below.

| `problem_type` value | Problem type |
| --- | --- |
| ACTIVITYCOEF | Activity Coefficient |
| SOLUBILITY | Solubility calculation in a mixed solvent |
| PURESOLUBILITY | Solubility calculation in a pure solvent |
| LOGP | Partition coefficient calculation |
| VAPORPRESSURE | Vapor pressure calculation for a mixed solvent |
| PUREVAPORPRESSURE | Vapor pressure calculation for a pure solvent |
| BOILINGPOINT | Boiling point calculation for a mixture |
| PUREBOILINGPOINT | Boiling point calculation for a pure solvent(s) |
| FLASHPOINT | Flashpoint calculation for a mixture |
| LLE | Liquid-Liquid Equilibrium calculation |
| STABILITY | Phase stablity test |
| BINMIXCOEF | Binary mixture LLE/VLE |
| TERNARYMIX | Ternary mixture LLE/VLE |
| COMPOSITIONLINE | Solvent composition line interpolation |
| SIGMAPROFILE | Sigma profile calculation for a mixture |
| PURESIGMAPROFILE | Sigma profile calculation for a pure component(s) |
| SIGMAPOTENTIAL | Sigma potential calculation for a mixture |
| PURESIGMAPOTENTIAL | Sigma potential calculation for a pure component(s) |

get\_activity\_coefficients(*idx: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) → [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[ndarray\] [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.get_activity_coefficients)

Returns activity coefficients for all `CRSMixture` or the specified ones.

Keyword Arguments:

**idx** (`int or List[int], optional`) – Index or list of indices of `CRSMixture` to return. If None, returns for all mixtures. Default is None.

Returns:

Activity coefficients as a list of numpy arrays.

Return type:

List\[np.ndarray\])

runCRSIteration(*parameter\_sett=None*, *history=False*) [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.runCRSIteration)

Run CRS iterations for all `CRSMixture` objects when `iteration=True`.

Each mixture executes `CRSIteration.do_iteration` with the base settings plus any overrides in `parameter_sett`. When `history` is True, each iteration is kept as a distinct CRSJob; otherwise only the last iteration is retained.

Keyword Arguments:

- **parameter\_sett** (`Settings, optional`) – Settings to merge into the base CRS job settings for this iteration.
- **history** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – Keep all iterations as `children["iteration_N"]` when True; keep only `children["iteration_last"]` when False.

runCRSJob() [¶](CRSManager.md#pyCRS.CRSManager.CRSSystem.runCRSJob)

Run all `CRSJob` in each `CRSMixture`

*class* pyCRS.CRSManager.CRSMixture(*\*\*kwargs*) [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture)

Build a CRSJob (or CRSIteration when enabled) from mixture input and settings.

This class builds a CRSJob from mixture composition/conditions, thermodynamic settings, and database inputs. When iteration is True, it creates a CRSIteration instead of a single CRSJob.

crs\_job [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.crs_job)

Created when iteration is False.

Type:

`CRSJob`

crs\_iteration [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.crs_iteration)

Created when iteration is True.

Type:

`CRSIteration`

iteration [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.iteration)

Enable iterative runs by applying different settings across iterations (default False).

Type:

[`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")

mixture [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.mixture)

Composition as {Identifier: mole/mass fraction}

Type:

[`dict`](https://docs.python.org/3.8/library/stdtypes.html#dict "(in Python v3.8)")

temperature [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.temperature)

Temp in Kelvin (default 298.15). If str, format can be “T1” or “T1 T2 ntemp”. Where T1 is the starting temperature, T2 is the ending temperature, and ntemp is the number of intervals between T1 and T2.

Type:

`float or str`

problem\_type [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.problem_type)

Calculation type (default “activitycoef”).

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

database [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.database)

Path or instance of COSKFDatabase (default “my\_coskf\_db.db”).

Type:

`str or COSKFDatabase`

method [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.method)

Version of COSMORS or COSMOSAC (default “COSMORS”).

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

pressure [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.pressure)

Pressure in bar (default 1.01325). If str, format can be “P1” or “P1 P2 npress”. Where P1 is the starting pressure, P2 is the ending pressure, and npress is the number of intervals between P1 and P2.

Type:

`float or str`

jobname [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.jobname)

Job name in plam\_workdir (defaults “crsJob\_n”).

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

conformer [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.conformer)

Use multiple conformers in COSMO-RS (default False).

Type:

[`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")

massfraction [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.massfraction)

Input fraction as mass (default False).

Type:

[`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")

density\_corr [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.density_corr)

Use pure compound density for volume. Default to False (uses COSMO volume).

Type:

[`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")

vp\_corr [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.vp_corr)

Correct gas phase chemical potential with vapor pressure (default False).

Type:

[`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")

solute [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.solute)

Solute state (“solid”, “gas”, “liquid”) in SOLUBILITY and PURESOLUBILITY. Default is “solid”.

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

iso [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.iso)

Condition (“isotherm”, “isobar”, “flashpoint”) for BINMIXCOEF, TERNARYMIX, and COMPOSITIONLINE. Default is “isotherm”.

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

multi\_species [¶](CRSManager.md#pyCRS.CRSManager.CRSMixture.multi_species)

Multi-species settings as {Identifier: Settings} (default None).

Type:

[`dict`](https://docs.python.org/3.8/library/stdtypes.html#dict "(in Python v3.8)")

**Reference**