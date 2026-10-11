---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/basic_CRSManager.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## pyCRS: Basic usage for Database and CRSManager

## Adding compound to a pyCRS database

First, we’ll add ethanol and water to the database and search for a list of compounds. When adding a compound, along with the COSKF file, it is necessary to provide a compound name and an unique chemical identifier. If only the COSKF file is provided, the method will attempt to utilize the IUPAC as the compound name and the CAS number as the chemical identifier, extracted from the Compound Data section within the COSKF file. In case such data is unavailable in the COSKF file, the user can specify the name parameter to define the compound name and either cas or identifier as the chemical identifier.

\[show/hide code\]

```python
from pyCRS.Database import COSKFDatabase

########  Note: Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script  ########

db = COSKFDatabase("my_coskf_db.db")
db.add_compound("1-Hexanol.coskf", cas="111-27-3")
db.add_compound("Water.coskf", identifier="InChI=1S/H2O/h1H2")

compounds = db.get_compounds(["111-27-3", "Water"])
for key, rows in compounds.items():
    for row in rows:
        print(f"{key}: {row}")
```

The output produced is the following

```
Successfully add new COMPOUND :compound_id=1  conformer_id=1  name=1-hexanol
Successfully add new COMPOUND :compound_id=2  conformer_id=2  name=water
111-27-3: CompoundRow(compound_id=1, conformer_id=1, name='1-hexanol', cas='111-27-3', identifier=None, smiles='CCCCCCO', resolved_smiles='CCCCCCO', coskf='1-Hexanol.coskf', Egas=-2562.042, Ecosmo=-2567.322, nring=0)
Water: CompoundRow(compound_id=2, conformer_id=2, name='water', cas='7732-18-5', identifier='InChI=1S/H2O/h1H2', smiles='O', resolved_smiles='O', coskf='Water.coskf', Egas=-323.939, Ecosmo=-330.389, nring=0)
```

## Activity coefficient calculation

\[show/hide code\]

```python
from scm.plams import Settings, init, finish
from pyCRS.Database import COSKFDatabase
from pyCRS.CRSManager import CRSSystem

db = COSKFDatabase("my_coskf_db.db")
cal = CRSSystem()

mixture = {}
mixture["7732-18-5"] = 0.3
mixture["111-27-3"] = 0.7

cal.add_Mixture(mixture, database="my_coskf_db.db", temperature=298.15, problem_type="activitycoef")

init()
cal.runCRSJob()
finish()

for out in cal.outputs:
    print(f"Property = {out.section}")
    res = out.get_results()
    for name, x, gamma in zip(res["name"], res["frac1"], res["gamma"]):
        print(name, x, gamma)
```

The output produced is the following

```
Property = ACTIVITYCOEF
water [0.3] [3.71486029]
1-hexanol [0.7] [1.04484603]
```

## Solid Solubility calculation

Next, we can add the melting point and heat of fusion if experimental data is available or estimate these values using PropPred and then perform the solid solubility calculation. In addition, it also shows the way to either use the pure compound density or solvent density in the calculation which will only affect the volume dependent properties.

\[show/hide code\]

```python
from scm.plams import Settings, init, finish
from pyCRS.Database import COSKFDatabase
from pyCRS.CRSManager import CRSSystem

########  Note: Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script  ########

db = COSKFDatabase("my_coskf_db.db")

db.add_compound("Ibuprofen.coskf")
db.add_compound("Water.coskf")
db.add_physical_property("Ibuprofen", "hfusion", 27.94, unit="kJ/mol")
db.add_physical_property("Ibuprofen", "meltingpoint", 347.6)
db.estimate_physical_property("Ibuprofen")

EXP = db.get_physical_properties("Ibuprofen")[0]
QSPR = db.get_physical_properties("Ibuprofen", source="PropPred")[0]

print("experimental value = ", EXP.hfusion, " estimated value = ", QSPR.hfusion)

mixture = {}
mixture["Water"] = 1.0
mixture["Ibuprofen"] = 0

init()

cal = CRSSystem()
cal.add_Mixture(
    mixture, database="my_coskf_db.db", temperature=293.15, problem_type="solubility", solute="solid", jobname="default"
)

db.add_physical_property("Water", "density", 0.997)
cal.add_Mixture(
    mixture,
    database="my_coskf_db.db",
    temperature=293.15,
    problem_type="solubility",
    solute="solid",
    density_corr=True,
    jobname="compound_density",
)

solvent_density = 0.9982067
additional_sett = Settings()
additional_sett.input.property.DensitySolvent = solvent_density
cal.add_Mixture(
    mixture,
    database="my_coskf_db.db",
    temperature=293.15,
    problem_type="solubility",
    solute="solid",
    additional_sett=additional_sett,
    jobname="solvent_density",
)

cal.runCRSJob()

for out in cal.outputs:
    res = out.get_results()
    print(f"Jobname = {out.job.name}; Property = {out.section}")
    print(
        f"{res['name'][1]} in {res['name'][0]} x= {res['molar fraction'][1][0]:.3e}; (g/L)= {res['solubility g_per_L_solvent'][1][0]:.5f}"
    )

finish()
```

The output produced is the following

```
experimental value =  6.678  estimated value =  5.744
Jobname = default; Property = SOLUBILITY
ibuprofen in water x= 1.647e-06; (g/L)= 0.02207
Jobname = compound_density; Property = SOLUBILITY
ibuprofen in water x= 1.647e-06; (g/L)= 0.01880
Jobname = solvent_density; Property = SOLUBILITY
ibuprofen in water x= 1.647e-06; (g/L)= 0.01882
```

## Establishment of a pyCRS database from the ADFCRS-2018 database

The script facilitates the automatic creation of a sql database utilizing the COSKF file from the [ADFCRS-2018 database](https://www.scm.com/doc/COSMO-RS/COSMO-RS_Databases.html#adfcrs-2018).

\[show/hide code\]

```python
from pyCRS.Database import COSKFDatabase
from pathlib import Path

########  Note: Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script  ########

db = COSKFDatabase("ADFCRS-2018.db")
path = Path(db.ADFCRS2018_path)

for x in path.glob("*.coskf"):
    if not x.name.startswith("IL_"):
        db.add_compound(x)
```