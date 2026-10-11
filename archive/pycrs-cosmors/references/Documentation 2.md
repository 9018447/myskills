---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/PLAMS_examples.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Examples using PLAMS

## Partition coefficient

In this example, we calculate the logP of Ibuprofen. We use the standard octanol/water system. The code is as follows:

\[show/hide code\]

```python
from scm.plams import Settings, init, finish, CRSJob
import os

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

# initialize settings object
settings = Settings()
settings.input.property._h = "LOGP"

# set the number of compounds
num_compounds = 3

compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(database_path, "1-Octanol.coskf")
compounds[1]._h = os.path.join(database_path, "Water.coskf")
compounds[2]._h = os.path.join(database_path, "Ibuprofen.coskf")

# phase1 (octanol phase)
compounds[0].frac1 = 0.725
compounds[1].frac1 = 0.275

# phase2 (water phase)
compounds[0].frac2 = 0
compounds[1].frac2 = 1

# set temperature (range)
# to specify a range, use 3 numbers: (1) the lowest temperature,
# (2) the highest temperature, and (3) the steps taken between these temperatures
settings.input.temperature = "298.15"

# specify the compounds as the compounds to be used in the calculation
settings.input.compound = compounds
# create a job that can be run by COSMO-RS
my_job = CRSJob(settings=settings)
# run the job
init()
out = my_job.run()
finish()

# convert all the results into a python dict
res = out.get_results()

# print the logP of Ibuprofen
print("logP of Ibuprofen:", res["logp"][2])
```

This generates the following output:

```bash
logP of Ibuprofen: [ 4.67381309]
```

## Binary mixture

In this example, we calculate a binary mixture of water and 2-Hexanone and plot the vapor pressures as a function of composition. We also show how to change the method and calculate the binary mixture with the COSMO-SAC2013-Xiong model.

\[show/hide code\]

```python
from scm.plams import Settings, init, finish, CRSJob
import os

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

# initialize settings object
settings = Settings()
settings.input.property._h = "BINMIXCOEF"

# let's also change to the COSMOSAC2013 method
settings.input.method = "COSMOSAC2013"

# set the number of compounds
num_compounds = 2

compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(database_path, "Water.coskf")
compounds[1]._h = os.path.join(database_path, "2-Hexanone.coskf")

# use the vapor pressures from the VPM1 model
compounds[0].vp_equation = "VPM1"
compounds[0].vp_params = "-6093.40215895 -3.09584608667 0.000498622924643 34.47450247140318 0.0"
compounds[1].vp_equation = "VPM1"
compounds[1].vp_params = "-6474.348470271438 -6.057589837807771 0.003390587477679571 51.07134238467479 0.0"

# set temperature (range)
# to specify a range, use 3 numbers: (1) the lowest temperature,
# (2) the highest temperature, and (3) the steps taken between these temperatures
settings.input.temperature = "298.15"

# specify the compounds as the compounds to be used in the calculation
settings.input.compound = compounds
# create a job that can be run by COSMO-RS
my_job = CRSJob(settings=settings)
# run the job
init()
out = my_job.run()
finish()

# convert all the results into a python dict
res = out.get_results()

# plot all the pressures as a function of mole fraction of water
out.plot(
    "vapor pressure",
    "pressure",
    x_axis=res["molar fraction"][0],
    x_label="mole fraction water",
    y_label="Pressure (bar)",
)
```

The code generates the following plot:

Fig. 6 A plot showing the total and partial vapor pressures for the water/2-Hexanone system.[¶](#id1 "Permalink to this image")

Water and 2-Hexanone do not mix so well, thus there will be a miscibility gap, which is not taken into account in the graph. COSMO-SAC calculates the miscibility gap for the water/2-Hexanone system for molar fraction of water between around 0.29 and around 0.998. Within the miscibility gap the results shown in the graph use the unphysical condition that the two liquids are forced to mix.

## Solid solubility

In this example, we calculate the solubility of ibuprofen in water at 298.15K. When considering a compound in its solid state, it’s essential to account for the energy change of a compound from the subcooled liquid state to the ordered solid state. The energy change can be estimated using its heat of fusion and melting point. The heat capacity of fusion, while beneficial, is often not readily available.

\[show/hide code\]

```python
from scm.plams import Settings, init, finish, CRSJob
import os

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

settings = Settings()
settings.input.property._h = "SOLUBILITY"
settings.input.method = "COSMORS"

num_compounds = 2
compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(database_path, "Water.coskf")
compounds[0].frac1 = 1.0
compounds[1]._h = os.path.join(database_path, "Ibuprofen.coskf")
compounds[1].frac1 = 0.0
compounds[1].nring = 6
compounds[1].hfusion = 27.94 / 4.184  # kcal/mol
compounds[1].meltingpoint = 347.6  # K
# compounds[1].cpfusion =           #kcal/mol-K

settings.input.temperature = 298.15

# specify the compounds as the compounds to be used in the calculation
settings.input.compound = compounds
# create a job that can be run by COSMO-RS
my_job = CRSJob(settings=settings)
# print out the input file
# print(my_job.get_input())

# run the job
init()
out = my_job.run()
finish()

# convert all the results into a python dict
res = out.get_results()

# print the solubility of Ibuprofen in water
print("Solubility of Ibuprofen in water [g/L]:", res["solubility g_per_L_solvent"][1])
```

This generates the following output:

```bash
Solubility of Ibuprofen in water [g/L]: [0.02799089]
```