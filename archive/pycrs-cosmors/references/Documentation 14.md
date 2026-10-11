---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS_Overview.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## General Information

> [!note] Attention
> Windows and Mac users may find it helpful to first read the *Getting Started* guides for scripting: [scripting with Windows](https://www.scm.com/doc/Scripting/GettingStarted.html#windows) | [scripting with MacOS](https://www.scm.com/doc/Scripting/GettingStarted.html#macos)

It is recommended to use the version of python that is shipped with AMS. This version ensures that all the necessary libraries (e.g., [PLAMS](https://www.scm.com/doc/plams/index.html)) are properly imported and are mutually compatible. The best way to do this is to run the `amspython` program. That can be executed from the command line as follows:

```bash
$AMSBIN/amspython <your_program.py>
```

Furthermore, interactive usage of the amsipython program can be beneficial. To do so, execute the following command in your terminal:

```bash
$AMSBIN/amsipython     # in terminal
```

```bash
run <your_program.py>  # in interactive python
```

where `<your_program.py>` should of course be replaced by the name of your program.

## Overview

The `pyCRS` Python library offers a convenient wrapper for various thermodynamic calculations, providing the following utilities:

| Modules | API | Description |
| --- | --- | --- |
|  | [API](https://www.scm.com/doc/COSMO-RS/pyCRS/Database.html#pycrs-database) | Provides an interface to a SQL database for managing COSKF files with conformers. |
|  | [API](https://www.scm.com/doc/COSMO-RS/pyCRS/CRSManager.html#pycrs-crsmanager) | It’s a python wrapper based on PLAMS library for facilitating the COSMO-RS calculation. It is designed to be used in conjunction with Database. |
| PropPred | [API](https://www.scm.com/doc/COSMO-RS/pyCRS/PropPred.html#pycrs-proppred) | Predicts physical properties based on QSPR descriptors derived from SMILES. |
| FastSigma | [API](https://www.scm.com/doc/COSMO-RS/pyCRS/FastSigma.html#pycrs-fastsigma) | Predicts sigma profiles based on QSPR descriptors derived from SMILES. |

Future releases will incorporate more functionality.

In addition to introducing the Database and CRSManager in the following section, the [examples section](https://www.scm.com/doc/COSMO-RS/Python_Examples.html#crs-examples) contains various template scripts and helpful examples. Exploring the example section is one of the simplest ways to get started with the module.

## Database

### Introduction

The sql database contains the following tables.

| Table name | Description |
| --- | --- |
| Compound | contains unique compounds along with their COSKF file based on either CAS number or any preferred identifier |
| Conformer | contains multiple conformers along with their COSKF file |
| PhysicalProperty | contains the physical properties input by user |
| PropPred | contains the estimated physical properties using QSPR methods based on SMILES |

These tables can be visualized using open-source tools like [DB Browser](https://sqlitebrowser.org/) or accessed directly through methods within the COSKFDatabase class.

> [!note] Attention
> This module currently does not support charged species, polymers, or multiple-species with dissociation and association. While it’s feasible to add these compounds to the database, it’s worth noting that the SMILES generated from the coordinates using OpenBabel might be inaccurate. Additionally, the PropPred tool should not be utilized for charged species and polymers.

> [!note] Note
> Currently, the `.coskf` files themselves are stored as raw `.coskf` files in a directory called `SCM_PYCRS_COSKF_DB`, which will be created in the parent directory of the `path` variable. This database will not be overwritten or deleted by this `COSKFDatabase` class. This directory exists for the convenience of the user, but it is best to access all files via the API below as the exact format of the database may evolve over time.

### Basic Usage

In this brief example, we’ll demonstrate how to interact with the database. This includes adding a compound, searching for a compound, specifying experimental physical properties, and utilizing PropPred to estimate physical properties.

There are a few important points to note when using the add\_compound method:

1\. If the `coskf_path` parameter is not provided by the user, the method will attempt to locate the ADFCRS-2018 database path if it’s available. Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script.

2\. If the `cas` parameter is not provided by the user, the method will attempt to use the value stored in the ‘Compound Data’ section within the.coskf file if it’s available.

3\. If the `name` parameter is not provided by the user, the method will prioritize using the IUPAC name, CAS number, identifier, or the name of the.coskf file. The IUPAC name will be attempted to be retrieved from the ‘Compound Data’ section within the.coskf file.

```python
from pyCRS.Database import COSKFDatabase

#Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script  #

db = COSKFDatabase("my_coskf_db.db")
db.add_compound("Water.coskf", name="Water", cas="7732-18-5")
db.add_compound("Methanol.coskf")
db.add_compound("Ethanol.coskf")
db.add_compound("Benzene.coskf")
db.add_compound("Ibuprofen.coskf")

rows = db.get_compounds(["7732-18-5","Ibuprofen"])
for key, row in rows.items():
    print(row[0])

db.add_physical_property("Ibuprofen","meltingpoint",347.6)
db.add_physical_property("Ibuprofen","hfusion",27.94,unit="kJ/mol")
db.estimate_physical_property("Ibuprofen")

EXP = db.get_physical_properties("Ibuprofen")[0]
QSPR = db.get_physical_properties("Ibuprofen",source="PropPred")[0]

print("experimental value = ", EXP.hfusion, " estimated value = ",QSPR.hfusion)
```

The output produced is the following:

```
CompoundRow(compound_id=1, conformer_id=1, name='water', cas='7732-18-5', identifier=None, smiles='O', resolved_smiles='O', coskf='Water_1.coskf', Egas=-323.935, Ecosmo=-330.386, nring=0)
CompoundRow(compound_id=4, conformer_id=4, name='ibuprofen', cas='15687-27-1', identifier=None, smiles='CC(Cc1ccc(cc1)[C@@H](C(=O)O)C)C', resolved_smiles='CC(Cc1ccc(cc1)[C@@H](C(=O)O)C)C', coskf='Ibuprofen_1.coskf', Egas=-4486.784, Ecosmo=-4494.859, nring=6)
experimental value =  6.678  estimated value =  5.744
```

### Adding multiple conformers

When adding multiple conformers (i.e. multiple COSKF files) of a compound to the database using `add_compound` method, three confirmation steps are attempted:

1\. Initially, the set of conformers in the database is retrieved by matching the CAS number or identifier. If it’s not found the compound will be added to the database as a new compound.

2\. Subsequently, it attempts to generate the canonical SMILES from its coordinates to confirm that the compound matches the one in the database. If this resolution fails, one can bypass this check by setting ignore\_smiles\_check=True.

3\. Lastly, it conducts duplicate recognition using UniqueConformersCrest in AMSConformer tool to ensure that it’s not a duplicate in the database. If this recognition fails, one can skip this step by setting ignore\_duplicates=True.

By default, the conformer with the lowest gas phase bond energy is stored in the COMPOUND TABLE. However, a specific conformer can be chosen using its conformer ID through the `update_compound_by_conformer_id` method.

For detailed information on these methods, please refer to the [Database API documentation](https://www.scm.com/doc/COSMO-RS/pyCRS/Database.html#pycrs-database).

## CRSManager

### Introduction

The module provides a user-friendly approach for configuring standard crsJob setups via Python scripting.

For instance, here is an example how we set up the solid solubility calculation using CRSManager once the database has been set up in advance. This approach provides a more convenient method for conducting high-throughput calculations without the need for specific handling, such as [solubility screening](https://www.scm.com/doc/COSMO-RS/Examples/Solubility_screening.html#metatag-scripting-solubility-screening).

*Python code using pyCRS*

\[show/hide code\]

```python
from pyCRS.CRSManager import CRSSystem
cal = CRSSystem()
mixture = {}
mixture["Water"] = 1.0
mixture["Ibuprofen"] = 0
cal.add_Mixture( mixture,
                database="my_coskf_db.db",
                temperature=298.15,
                problem_type="solubility",
                solute="solid")
print(cal.get_input(0))
```

Alternatively, the same calculation can be set up through PLAMS, as demonstrated below. This approach requires users to input correct settings but provides greater flexibility in managing complex workflows. For example, the [advanced scripting example section](https://www.scm.com/doc/COSMO-RS/Examples/Advanced_examples_index.html#crs-advance-scripting) demonstrates various tasks, such as eutectic and ionic liquid calculations, and more.

*Python code using PLAMS*

\[show/hide code\]

```python
from scm.plams import Settings, init, finish, CRSJob
import os

########  Note: Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script  ########

coskf_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"] , "ADFCRS-2018")

settings = Settings()
settings.input.property._h = "SOLUBILITY"
settings.input.method = "COSMORS"

num_compounds = 2
compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(coskf_path, "Water.coskf" )
compounds[0].frac1 = 1.0
compounds[1]._h = os.path.join(coskf_path, "Ibuprofen.coskf" )
compounds[1].frac1 = 0.0
compounds[1].nring = 6
compounds[1].hfusion = 27.94/4.184
compounds[1].meltingpoint = 347.6

settings.input.temperature = 298.15

# specify the compounds as the compounds to be used in the calculation
settings.input.compound = compounds
# create a job that can be run by COSMO-RS
my_job = CRSJob(settings=settings)
print(my_job.get_input())
```

> [!note] Attention
> This module currently does not support charged species, polymers, or multiple-species with dissociation and association.

### Basic Usage

In this example, we’ll create a database containing ethanol and benzene from the ADFCRS-2018 database. Then, we’ll instantiate a CRSSystem and generate several CRSMixture instances using the add\_Mixture method. After executing the calculation with the runCRSJob method, the corresponding CRSResults instances will be generated and stored in the outputs attribute. Finally, we can retrieve the.crskf file and the activity coefficient using methods provided by CRSResults.

\[show/hide code\]

```python
from scm.plams import Settings, init, finish, CRSJob, config
from pyCRS.CRSManager import CRSSystem
from pyCRS.Database import COSKFDatabase
import numpy as np
import os, sys

init()
config.log.stdout = 0  # suppress plams output default=3

#create a database containing ethanol and benzene. please ensure install the ADFCRS-2018 database first via amspackages (SCM -> Packages)
db = COSKFDatabase("my_coskf_db.db")
db.add_compound("Ethanol.coskf")
db.add_compound("Benzene.coskf",cas="71-43-2")

#create a CRSSystem instance
cal = CRSSystem()

#generate several CRSMixture instance
for i, x in enumerate(np.linspace(0, 1, 11)):
    mixture = {}
    mixture["ethanol"] = x
    mixture["71-43-2"] = 1-x
    cal.add_Mixture(mixture,database="my_coskf_db.db",temperature=298.15,problem_type="ACTIVITYCOEF",method="COSMORS")

#print out the first calculation setting in the CRSSystem class
#print(cal.get_input(0))

#execution calculation for all CRSMixture
cal.runCRSJob()

gamma_ethanol = []
gamma_benzene = []
#retrieve result using methods provided by CRSResults
for out in cal.outputs:
    crskf = out.kfpath()
    res = out.get_results()
    gamma_ethanol.append(res["gamma"][0][0])
    gamma_benzene.append(res["gamma"][1][0])

print(f"the last crskf file = {os.path.basename(crskf)}")
print(f"activity coefficient of ethanol = {gamma_ethanol}")
print(f"activity coefficient of benzene = {gamma_benzene}")

finish()
```

This generates the following output:

```
the last crskf file = crsJob_10.crskf
activity coefficient of ethanol = [41.59625151549539, 3.539543443573337, 2.234237060852824, 1.712495443157569, 1.4321494593043322, 1.2612087014707123, 1.1507589807729406, 1.0784886266786704, 1.0329501218595156, 1.0079137778145097, 1.0]
activity coefficient of benzene = [1.0, 1.0632078891234995, 1.1497425466225775, 1.2547602114699132, 1.3804970769948137, 1.5309168719748845, 1.7115353244885652, 1.9297200775482874, 2.1952374886461046, 2.521062652267439, 2.9247536001030006]
```

### Additional Keywords

Additional keywords can be used in conjunction with certain problem types:

| Keywords name | Description |
| --- | --- |
| `vp_corr` | When set to True, it attempts to use the vapor pressure of pure compounds to adjust the gas phase chemical potential, potentially increasing vapor pressures in a mixture. The default value is False. |
| `density_corr` | When set to True, it attempts to utilize the volume of a pure compound derived from its density instead of the cavity volume used in the COSMO calculation. The default value is False. |
| `solute` | This parameter allows you to specify ‘solid’, ‘gas’, or ‘liquid,’ applicable to SOLUBILITY and PURESOLUBILITY problem types. The default value is ‘solid’. |
| `iso` | This parameter offers the choice between ‘isotherm’, ‘isobar’ or ‘flashpoint’, applicable to BINMIXCOEF, TERNARYMIX, and COMPOSITIONLINE. The default value is ‘isotherm’. |
| `additional_sett` | This parameter provides the PLAMS approach to set up various parameters such as the VolumeQuotient in LOP, DensitySolvent in SOLUBILITY, Nfrac in BINMIXCOEF/TERNARYMIX/COMPOSITIONLINE, Nprofile/SigmaMax in SIGMAPROFILE/SIGMAPOTENTIAL. |

For certain problem types, necessary physical properties are retrieved from the PhysicalProperty TABLE and PropPred TABLE in the database. The value from the PhysicalProperty TABLE is prioritized; if unavailable, the system attempts to use the value from the PropPred TABLE instead. Failure to obtain either value may result in calculation failure.

For instance, you can find the following examples.

```python
# Solid solubility calculation
db.add_physical_property("Benzene","hfusion",2.37,unit="kcal/mol")
db.add_physical_property("Benzene","meltingpoint",278.7)
mixture = {}
mixture["Water"]   = 1
mixture["Benzene"] = 0
cal.add_Mixture( mixture,
                database="my_coskf_db.db",
                temperature="273.15 373.15 10",
                problem_type="SOLUBILITY",
                solute="solid")

# Binary isobar VLE using the vapor pressure from PropPred
mixture = {}
mixture["methanol"] = 0.5
mixture["ethanol"] = 0.5
db.estimate_physical_property(["methanol","ethanol"])
additional_sett = Settings()
additional_sett.input.property.Nfrac = 10
cal.add_Mixture( mixture,
                database="my_coskf_db.db",
                pressure=1.01325,
                problem_type="BINMIXCOEF",
                iso="isobar",
                additional_sett=additional_sett,
                vp_corr=True)

# Partition Coefficient for benzene/water
mixture = {}
mixture["benzene"] = [1, 0]  #[mole fraction in phase1, mole fraction in phase2]
mixture["water"]   = [0, 1]  #[mole fraction in phase1, mole fraction in phase2]
mixture["ethanol"] = [0, 0]  #[0, 0] for solute
additional_sett = Settings()
additional_sett.input.property.VolumeQuotient = 4.93
cal.add_Mixture( mixture,
                database="my_coskf_db.db",
                problem_type="LOGP",
                additional_sett=additional_sett)

# Sigma profile
mixture = {}
mixture["benzene"] = 1
additional_sett = Settings()
additional_sett.input.property.Nprofile = 100
additional_sett.input.property.SigmaMax = 0.05
cal.add_Mixture( mixture,
                database = "my_coskf_db.db",
                problem_type="PURESIGMAPROFILE",
                method="COSMORS",
                additional_sett=additional_sett)
```

The available problem types is listed below.

| `problem_type` value | Problem type |
| --- | --- |
| ACTIVITYCOEF | Activity Coefficient |
| BINMIXCOEF | Binary mixture LLE/VLE |
| TERNARYMIX | Ternary mixture LLE/VLE |
| COMPOSITIONLINE | Solvent composition line interpolation |
| SOLUBILITY | Solubility calculation in a mixed solvent |
| PURESOLUBILITY | Solubility calculation in a pure solvent |
| LOGP | Partition coefficient calculation |
| VAPORPRESSURE | Vapor pressure calculation for a mixed solvent |
| PUREVAPORPRESSURE | Vapor pressure calculation for a pure solvent |
| BOILINGPOINT | Boiling point calculation for a mixture |
| PUREBOILINGPOINT | Boiling point calculation for a pure solvent(s) |
| FLASHPOINT | Flashpoint calculation for a mixture |
| SIGMAPROFILE | Sigma profile calculation for a mixture |
| PURESIGMAPROFILE | Sigma profile calculation for a pure component(s) |
| SIGMAPOTENTIAL | Sigma potential calculation for a mixture |
| PURESIGMAPOTENTIAL | Sigma potential calculation for a pure component(s) |

For detailed information on these methods, please refer to the [CRSManager API documentation](https://www.scm.com/doc/COSMO-RS/pyCRS/CRSManager.html#pycrs-crsmanager).