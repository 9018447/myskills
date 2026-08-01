---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/IL_screening.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Automated screening of ionic liquids

[`Download python script and relevant file`](https://www.scm.com/doc/COSMO-RS/_downloads/80eed3e67ac907d738a57234ce6eac5e/IL_screening.zip)

In this example, we provide a template for the high-throughput screening with ionic liquid. The script will automates the screening of the infinite dilution activity coefficient (IDAC) of a solute among all combinations of available ionic liquids in the directory. The *set\_CRSJob\_IL* in this script adopt the same structure as *set\_CRSJob\_Hex\_conf* in previous example but have an additional input variable, *comp\_stoichiometric*, to specify the stoichiometric number of cation and anion. The stoichiometric number will be determined from their charge, and it is crucial to ensure that the **IL\_list.csv** file contains the minimum required information for each ion, such as abbreviation, charge and coskf file name. Furthermore, if the vapor pressure of the solute (Pvap) is provided, you can calculate the Henry’s constant and solute solubility at 1 bar under the assumption of ideal gas by setting cal\_Henry=True.

This figure (produced by the code) illustrates the screening outcomes for carbon dioxide involving 7 cations and 5 anions which have proven to be useful tool for searching good candidates.

## Python code

\[show/hide code\]

```python
import os, sys, time, glob
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from scm.plams import Settings, init, finish, CRSJob, config, JobRunner
import pandas as pd
from math import gcd

#######  Note: Ensure to download the coskf_IL before running the script  #######

"""
The Python script automates the screening of the infinite dilution activity coefficient (IDAC) 
of a solute among all combinations of available ionic liquids in the corresponding directory.

To run the script, ensure that the coskf file of ions and solute is stored in the database_path 
and the coskf file of ions follows a specific naming convention, such as IL_*cation_*.coskf or IL_*anion_*.coskf. 
For example, you should have files like IL_cation_1-butyl-3-methyl-imidazolium.coskf, 
IL_anion_hexafluorophosphate.coskf and Carbon_dioxide.coskf in ./coskf-IL/

Additionally, you need to provide the ion's information in the IL_list.csv file as input including:
    name, [abbreviation], type, charge, coskf, smiles(optional)
    1-butyl-3-methyl-imidazolium, [C4MIM ; C4C1im ; BMIM], cation, 1.0, IL_cation_1-butyl-3-methyl-imidazolium.coskf, CCCCn1cc[n+](C)c1
The IL_list.csv file contain the information of 80 cations and 56 anions in the ADFCRS-IL-2014 database.

Furthermore, if the vapor pressure of the solute (Pvap) is provided, you can calculate the Henry's constant and 
solute solubility at 1 bar under the assumption of ideal gas by setting cal_Henry=True.
    H(bar) = IDAC*Pvap
    x(1bar)= 1bar/H

The parallel calculation can be enabled by setting the Parallel_run=True and maxjobs=numners_of_processes.

The calculated result will be saved in a pandas dataframe (df) and a csv file (result_csv='IL_screening.csv').

The visualization of the result using a contour plot can be enable by setting Plot_option=True.

AMS2026 and later include the Pandas library by default. On older AMS versions, install it through AMSpackages.
    "${AMSBIN}/amspackages" install pandas
"""

init()

def set_CRSJob_IL(
    index,
    ncomp,
    coskf,
    database_path,
    cal_type,
    method,
    temperature,
    comp_input={},
    comp_type=[],
    comp_stoichiometric=[],
):

    s = Settings()  # initialize a settings object
    s.input.property._h = cal_type  # specify problem type
    s.input.method = method  # specify method
    s.input.temperature = temperature  # specify temperature

    compounds = [Settings() for i in range(ncomp)]  # initialization of compounds
    for i in range(ncomp):
        if len(comp_type) > i:
            if "conf" in comp_type[i]:
                form = [Settings() for i in range(len(coskf[i]))]  # initialize compound in multiple form
                for j in range(len(coskf[i])):
                    form[j]._h = os.path.join(
                        database_path, coskf[i][j]
                    )  # specify conformer's coskf file for each form
                compounds[i].form = form
            elif "IL" in comp_type[i]:
                form = [Settings() for j in range(1)]  # initialize IL in one form: dissociated IL
                species = [Settings() for j in range(2)]  # initialize dissociated IL in two species: cation and anion
                for j in range(2):
                    struct = [Settings() for k in range(1)]  # initialize cation and anion in one structure
                    struct[0]._h = os.path.join(database_path, coskf[i][j])
                    struct[0].count = comp_stoichiometric[i][j]  # specify the Stoichiometric number of cation and anion
                    species[j] = struct
                form[0].species = species
                compounds[i].form = form
            else:
                compounds[i]._h = os.path.join(database_path, coskf[i])  # specify absolute directory of coskf file
        else:
            compounds[i]._h = os.path.join(database_path, coskf[i])  # specify absolute directory of coskf file

        for column, value in comp_input.items():  # specify compound's information through comp_input, for example
            if value[i] != None:  # column: frac1, meltingpoint, hfusion
                compounds[i][column] = value[i]

    s.input.compound = compounds

    my_job = CRSJob(settings=s)  # create jobs
    my_job.name = cal_type + "_" + str(index)  # specify job name

    return my_job

Parallel_run = True  # If True -> parallel calculation
cal_Henry = True  # If True -> calculation of Henry's constant using IDAC*Pvap
Plot_option = True  # If True -> visualization of the results with a contour plot

if Parallel_run:
    config.default_jobrunner = JobRunner(
        parallel=True, maxjobs=8
    )  # Set jobrunner to be parallel and specify the numbers of jobs run simutaneously (eg. multiprocessing.cpu_count())
    config.default_jobmanager.settings.hashing = None  # Disable rerun prevention
    config.job.runscript.nproc = 1  # Number of cores for each job
    config.log.stdout = 1  # suppress plams output default=3

###----INPUT YOUR DATA HERE----###

database_path = os.path.join(os.getcwd(), "coskf_IL")
cal_type = "activitycoef"
method = "COSMORS"
ncomp = 2
solute = "Carbon_dioxide.coskf"
solute_abb = "CO2"
temperature = 298.15

# Retrive all coskf file for cation and anion in database_path. Note the file must be named as: IL_*cation_*.coskf and IL_*anion*.coskf
cations_coskf = [os.path.basename(x) for x in glob.glob(os.path.join(database_path, "IL_*cation_*.coskf"))]
anions_coskf = [os.path.basename(x) for x in glob.glob(os.path.join(database_path, "IL_*anion_*.coskf"))]

# store input data along with the necessary thermal property in comp_input dictionary
comp_input = {}
comp_input["frac1"] = [1.0, 0.0]

# enter 'IL' for ionic liquid; 'conf' for compound with multiple conformers; '' for compound with single structure
comp_type = ["IL", ""]

# Read ion's information from IL_list.csv where contain name, [abbreviation], type, charge, coskf, smiles(optional)
df_IL = pd.read_csv("IL_list.csv")

# Write the screening result
result_csv = "result_IL_screening.csv"

###----INPUT END----###

index = 0
outputs = []
df = pd.DataFrame()
for cation in cations_coskf:
    for anion in anions_coskf:

        cur_df = df_IL.loc[df_IL["coskf"] == cation]
        cation_abb = cur_df["abbreviation"].values[0].split(";")[0].rstrip()  # abbreviation
        cation_charge = int(cur_df["charge"].values[0])  # charge

        cur_df = df_IL.loc[df_IL["coskf"] == anion]
        anion_abb = cur_df["abbreviation"].values[0].split(";")[0].rstrip()  # abbreviation
        anion_charge = int(cur_df["charge"].values[0])  # charge

        # find the Least Common Multiple of cation charge and anion charge
        IL_lcm = cation_charge * anion_charge / gcd(cation_charge, anion_charge)
        cation_v = -IL_lcm / cation_charge  # stoichiometric number of cation
        anion_v = IL_lcm / anion_charge  # stoichiometric number of anion

        IL_abb = [cation_abb, anion_abb]  # abbreviation
        IL_coskf = [cation, anion]
        IL_v = [cation_v, anion_v]  # stoichiometric number

        coskf = [IL_coskf, solute]
        comp_stoichiometric = [IL_v, 1.0]  # stoichiometric number used for multi-species

        comp_input["name"] = [cation_abb + "_" + anion_abb, solute_abb]

        df.loc[index, "cation"] = cation_abb
        df.loc[index, "anion"] = anion_abb
        df.loc[index, "solute"] = solute.replace(".coskf", "")
        df.loc[index, "charge_c"] = int(cation_charge)
        df.loc[index, "charge_a"] = int(anion_charge)

        job = set_CRSJob_IL(
            index,
            ncomp,
            coskf,
            database_path,
            cal_type,
            method,
            temperature,
            comp_input,
            comp_type,
            comp_stoichiometric,
        )
        outputs.append(job.run())

        index = index + 1

# In a parallel run, the get_results function will wait for the completion of the corresponding jobs.
results = []
for index, out in enumerate(outputs):
    res = out.get_results()
    results.append(res)
    df.loc[index, "IDAC"] = res["gamma"][-1][0]

if cal_Henry:
    if solute == "Carbon_dioxide.coskf":
        Pvap = np.power(10, 6.35537 - 2067.0 / (temperature + 156.462))
        # antonie equation(unit in bar), parameters are fitted by SCM in temperature range 260-305K
    else:
        Pvap = np.nan
        print("The vapor pressure of the solute is not defined")
    if not np.isnan(Pvap):
        df["H(bar)"] = df["IDAC"] * Pvap
        df["x(1bar)"] = 1 / (df["IDAC"] * Pvap)

df.to_csv(result_csv, index=None)

if Plot_option:
    # contour visulization
    nx = len(cations_coskf)
    ny = len(anions_coskf)

    # Extract the 1st abbreviation of the ions. For instance, [C4MIM ; C4C1im ; BMIM] -> C4MIM
    cation_name = [df_IL.loc[df_IL["coskf"] == x]["abbreviation"].values[0].split(";")[0] for x in cations_coskf]
    anion_name = [df_IL.loc[df_IL["coskf"] == x]["abbreviation"].values[0].split(";")[0] for x in anions_coskf]

    x = [i for i in range(nx)]
    y = [i for i in range(ny)]

    if cal_Henry and not np.isnan(Pvap):
        cal_data = df["H(bar)"].values
        sub_title = "ln(H[bar]) of " + solute_abb + " in IL at " + str(temperature) + "K"
        fig_title = "IL_screening_lnH.png"
    else:
        cal_data = df["IDAC"].values
        sub_title = "ln(IDAC) of " + solute_abb.replace("_", " ") + " in IL at " + str(temperature) + "K"
        fig_title = "IL_screening_lnIDAC.png"

    plt_data = np.zeros((ny, nx))
    for i in range(ny):
        for j in range(nx):
            plt_data[i][j] = np.log(cal_data[j * ny + i])

    fig, ax = plt.subplots()

    plt.imshow(plt_data, cmap="RdGy", interpolation="nearest")
    if len(x) > 10:
        x = [0 + 5 * n for n in range((len(x) // 5) + 1)]
        plt.xticks(x, x, rotation=70)
    else:
        plt.xticks(x, cation_name, rotation=70)
    if len(y) > 10:
        y = [0 + 5 * n for n in range((len(y) // 5) + 1)]
        plt.yticks(y, y)
    else:
        plt.yticks(y, anion_name)
    plt.colorbar()
    plt.title(sub_title)
    plt.tight_layout()
    # plt.savefig(fig_title)
    plt.show()

finish()
```