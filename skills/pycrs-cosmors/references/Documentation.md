---
title: " pyCRS: Conformer usage for Database and CRSManager"
source: "https://www.scm.com/doc/COSMO-RS/Examples/conformer_CRSManager.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## pyCRS: Conformer usage for Database and CRSManager

## Generating multiple conformers for a compound

Different conformers of a molecule can have significantly different sigma profiles, which can lead to big differences in predicted properties with COSMO-RS. For this reason, it’s important for COSMO-RS calculations to use geometries corresponding to the lowest-energy conformer or a set of low-energy conformers when it’s possible several conformers may exist in significant amounts. The script shows how to use the adfcosmorsconformers recipe based on the ConformerTools functionality in AMS to generate a set of low-energy conformers, refine the geometries with a semi-empirical method and finally perform the ADF and COSMO calculations necessary to produce `.coskf` files.

\[show/hide code\]

```python
from scm.plams import Settings, init, finish, from_smiles
from scm.plams.recipes.adfcosmorsconformers import ADFCOSMORSConfJob, ADFCOSMORSConfFilter
from scm.conformers import ConformersJob

init()

mol = from_smiles("CC(=O)O")

conf_sett = Settings()
conf_sett.input.AMS.Generator.RDKit
conf_sett.input.AMS.Generator.RDKit.InitialNConformers = 50
conf_job = ConformersJob(name="conformers_uff", molecule=mol, settings=conf_sett)

dftb_sett = Settings()
dftb_sett.input.AMS.Task = "Optimize"
dftb_sett.input.DFTB

# ADFCOSMORSConfFilter(max number of conformers, max energy range)
fil1 = ADFCOSMORSConfFilter(20, 22)  # applied to UFF
fil2 = ADFCOSMORSConfFilter(10, 12)  # applied to DFTB
fil3 = ADFCOSMORSConfFilter(5, 7)  # applied to ADF gas phase

mol_info = {"CAS": "64-19-7", "IUPAC": "Acetic acid", "SMILES": "CC(=O)O"}

job = ADFCOSMORSConfJob(
    mol,
    conf_gen=conf_job,
    first_filter=fil1,
    additional=[(dftb_sett, fil2)],
    final_filter=fil3,
    coskf_name="acetic_acid",
    coskf_dir="coskf_acetic_acid",
    mol_info=mol_info,
)
job.run()

finish()
```

## Adding conformers to the database

This script shows how to add multiple conformers into the database, retrive the `ConformerRow` and visulize conformers for a given compound. Please generate the conformers for acetic acid using above script or download the files from the below link before running the below script.

[`Download relevant coskf file`](https://www.scm.com/doc/COSMO-RS/_downloads/64d1bd42d5be46b2ed41a9a181d00b8a/coskf_acetic_acid.zip)

\[show/hide code\]

```python
from pyCRS.Database import COSKFDatabase
import os

##################  Note: Ensure to download the coskf_acetic_acid or generating conformers for acetic acid before running the script  ##################

conformer_path = os.path.join(os.getcwd(), "coskf_acetic_acid")

db = COSKFDatabase("my_coskf_db.db")

db.add_compound("acetic_acid_0.coskf", coskf_path=conformer_path)
db.add_compound("acetic_acid_1.coskf", coskf_path=conformer_path)

print("Displaying all ConformerRow of acetic acid")
for key, rows in db.get_conformers("Acetic acid").items():
    for row in rows:
        print(f" {row}")

print("Displaying the CompoundRow of acetic acid with the lowest energy structure (default)")
for key, rows in db.get_compounds("Acetic acid").items():
    for row in rows:
        print(f" {row}")

db.visualize_conformers(identifier="acetic acid")
```

The output produced is the following

```
Displaying all ConformerRow of acetic acid
 ConformerRow(conformer_id=16, compound_id=16, name='acetic acid', cas='64-19-7', identifier=None, smiles='CC(=O)O', resolved_smiles='CC(=O)O', coskf='acetic_acid_0.coskf', Egas=-1061.604, Ecosmo=-1068.355, nring=0)
 ConformerRow(conformer_id=17, compound_id=16, name='acetic acid', cas='64-19-7', identifier=None, smiles='CC(=O)O', resolved_smiles='CC(=O)O', coskf='acetic_acid_1.coskf', Egas=-1056.642, Ecosmo=-1066.721, nring=0)
Displaying the CompoundRow of acetic acid with the lowest energy structure (default)
 CompoundRow(compound_id=16, conformer_id=16, name='acetic acid', cas='64-19-7', identifier=None, smiles='CC(=O)O', resolved_smiles='CC(=O)O', coskf='acetic_acid_0.coskf', Egas=-1061.604, Ecosmo=-1068.355, nring=0)
name=acetic acid; cas=64-19-7; identifier=None
conformer_id=16, coskf=acetic_acid_0.coskf, Egas=-1061.604, Ecosmo=-1068.355
conformer_id=17, coskf=acetic_acid_1.coskf, Egas=-1056.642, Ecosmo=-1066.721
```

## Activity coefficient calculation considering conformers

This calculation models acetic acid as a mixture of conformers and plots activity coefficients and the conformer distribution over the mole fraction range. Please generate the conformers for acetic acid using above script or download the files from the below link before running the below script.

[`Download relevant coskf file`](https://www.scm.com/doc/COSMO-RS/_downloads/64d1bd42d5be46b2ed41a9a181d00b8a/coskf_acetic_acid.zip)

\[show/hide code\]

```python
from scm.plams import Settings, init, finish
from pyCRS.Database import COSKFDatabase
from pyCRS.CRSManager import CRSSystem
import matplotlib.pyplot as plt
import numpy as np
import os

########  Note: Please ensure to install the ADFCRS-2018 database via amspackages (SCM->Packages) before running the below script  ########

db = COSKFDatabase("my_coskf_db.db")

db.add_compound("Water.coskf")

cal = CRSSystem()

mixture = {}
x_range = np.linspace(0, 1, 11)
for x in x_range:
    mixture["Acetic acid"] = x
    mixture["Water"] = 1 - x
    cal.add_Mixture(mixture, database="my_coskf_db.db", temperature=298.15, problem_type="activitycoef", conformer=True)

init()
cal.runCRSJob()
finish()

gamma_water = []
gamma_acid = []
comp_acetic = {}
for out in cal.outputs:
    res = out.get_results()
    gamma_acid.append(res["gamma"][0])
    gamma_water.append(res["gamma"][1])
    if comp_acetic == {}:
        comp_acetic = out.get_multispecies_dist()[0]
    else:
        tmp_comp_acetic = out.get_multispecies_dist()[0]
        for key in comp_acetic:
            comp_acetic[key].extend(tmp_comp_acetic[key])

fig, axs = plt.subplots(2)
axs[0].plot(x_range, gamma_acid, label="$\gamma_1$ (acetic)")
axs[0].plot(x_range, gamma_water, label="$\gamma_2$ (water)")

for struct, val in comp_acetic.items():
    axs[1].plot(x_range, val, label=os.path.basename(struct))

plt.setp(axs[0], ylabel="Activity coefficients")
plt.setp(axs[1], ylabel="Distribution")
for i in range(2):
    axs[i].legend()
    axs[i].grid()

plt.xlabel("$x_1$ (acetic acid)")
# plt.savefig('./pyCRS_activitycoef_conformer',dpi=300)
plt.show()
```

This code produces the following figure which plots activity coefficients and the distribution of two conformers.