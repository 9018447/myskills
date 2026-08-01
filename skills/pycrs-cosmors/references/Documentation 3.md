---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/Changing_parameters.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Changing the default parameters or re-parameterizing the COSMO-RS/-SAC methods

There are many situations for which changing the default COSMO-RS/-SAC parameters may be useful. Most commonly, users may wish to try a certain parameterization that is not available from the program. Alternatively, some users may have a customized or proprietary dataset which they would like to use to re-fit the main model parameters. All of these tasks are straightforward via python scripting.

The following scripts will demonstrate how to alter parameters for COSMO-RS and COSMO-SAC.

## Python code (COSMO-RS parameters)

\[show/hide code\]

```python
import os
from scm.plams import Settings, init, finish, CRSJob, config

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

init()
# suppress plams output
config.log.stdout = 0

# our system of interest
files = ["Acetone.coskf", "Water.coskf"]
fracs = [0.3, 0.7]

# initialize settings object
settings = Settings()
settings.input.property._h = "ACTIVITYCOEF"
settings.input.temperature = 298.15

compounds = [Settings() for i in range(len(files))]
for i, (name, frac) in enumerate(zip(files, fracs)):
    compounds[i]._h = os.path.join(database_path, name)
    compounds[i].frac1 = frac

settings.input.compound = compounds

# Here, we will change the method parameters specific to COSMO-RS
# Main CRS parameters
settings.input.CRSParameters.rav = 0.400
settings.input.CRSParameters.aprime = 1510.0
settings.input.CRSParameters.fcorr = 2.802
settings.input.CRSParameters.chb = 8850.0
settings.input.CRSParameters.sigmahbond = 0.00854
settings.input.CRSParameters.aeff = 6.94
settings.input.CRSParameters.Lambda = 0.130
settings.input.CRSParameters.omega = -0.212
settings.input.CRSParameters.eta = -9.65
settings.input.CRSParameters.chortf = 0.816
settings.input.CRSParameters.HB_HNOF = ""  # hb for only H,N,O,F
# settings.input.CRSParameters.HB_ALL     = "" # hb for all elements
settings.input.CRSParameters.HB_TEMP = ""  # temperature-dependent H-bond
# settings.input.CRSParameters.HB_NOTEMP  = "" # non-temperature-dependent H-bond
settings.input.CRSParameters.COMBI2005 = ""  # default combinatorial term
# settings.input.CRSParameters.COMBI1998  = ""

# Dispersion parameters
settings.input.Dispersion.H = -0.0340
settings.input.Dispersion.C = -0.0356
settings.input.Dispersion.N = -0.0224
settings.input.Dispersion.O = -0.0333
settings.input.Dispersion.F = -0.026
settings.input.Dispersion.Si = -0.04
settings.input.Dispersion.P = -0.045
settings.input.Dispersion.S = -0.052
settings.input.Dispersion.Cl = -0.0485
settings.input.Dispersion.Br = -0.055
settings.input.Dispersion.I = -0.062

# Technical and accuracy parameters
settings.input.Technical.rsconv = 1e-7
settings.input.Technical.maxiter = 10000
settings.input.Technical.bpconv = 1e-6
settings.input.Technical.bpmaxiter = 40
settings.input.Technical.solconv = 1e-5
settings.input.Technical.solmaxiter = 40
settings.input.Technical.solxilarge = 0.99
settings.input.Technical.ehdeltaT = 1.0

# We will vary the chb parameter (default value 8850.0)
# and observe the effect on activity coefficients

print("Resulting Activity Coefficients:")
print("chb value".ljust(15), "activity coefficients".ljust(20))
hbvals = [8700.0 + 50 * i for i in range(7)]
for hbval in hbvals:

    settings.input.CRSParameters.chb = hbval
    # create a job that can be run by COSMO-RS
    my_job = CRSJob(settings=settings)
    # run the job
    out = my_job.run()
    # convert all the results into a python dict
    res = out.get_results()

    print(str(hbval).ljust(15), str(res["gamma"].flatten()).ljust(20))

finish()
```

## Python code (COSMO-SAC parameters)

\[show/hide code\]

```python
import os
from scm.plams import Settings, init, finish, CRSJob, config

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

init()
# suppress plams output
config.log.stdout = 0

# our system of interest
files = ["Acetone.coskf", "Water.coskf"]
fracs = [0.3, 0.7]

# initialize settings object
settings = Settings()
settings.input.property._h = "ACTIVITYCOEF"
settings.input.temperature = 298.15

compounds = [Settings() for i in range(len(files))]
for i, (name, frac) in enumerate(zip(files, fracs)):
    compounds[i]._h = os.path.join(database_path, name)
    compounds[i].frac1 = frac

settings.input.compound = compounds

# Here, we will change the method parameters specific to COSMO-SAC
# First, change the method to COSMOSAC2013
settings.input.method = "COSMOSAC2013"

# Main SAC parameters
settings.input.SACParameters.aeff = 6.4813
settings.input.SACParameters.fdecay = 0.0
settings.input.SACParameters.sigma0 = 0.01233
settings.input.SACParameters.rn = 0.0
settings.input.SACParameters.qn = 79.532
settings.input.SACParameters.aes = 7877.13
settings.input.SACParameters.bes = 0.0
settings.input.SACParameters.cohoh = 5786.72
settings.input.SACParameters.cotot = 2739.58
settings.input.SACParameters.cohot = 4707.75
settings.input.SACParameters.rav = 0.51
settings.input.SACParameters.qs = 0.57
settings.input.SACParameters.rhbcut = 0.0
settings.input.SACParameters.omega = 0.0
settings.input.SACParameters.eta = 0.0
settings.input.SACParameters.HB_NOTEMP = ""  # non-temperature-dependent H-bonding (default)
# settings.input.SACParameters.HB_TEMP = "" # temperature-dependent H-bonding

# Epsilon Constants
settings.input.Epsilon.H = 338.13
settings.input.Epsilon["C.sp3"] = 29160.92
settings.input.Epsilon["C.sp2"] = 30951.83
settings.input.Epsilon["C.sp"] = 20685.98
settings.input.Epsilon["N.sp3"] = 23488.54
settings.input.Epsilon["N.sp2"] = 22663.38
settings.input.Epsilon["N.sp"] = 6390.40
settings.input.Epsilon["O.sp3-H"] = 8527.06
settings.input.Epsilon["O.sp3"] = 8484.38
settings.input.Epsilon["O.sp2"] = 6736.85
settings.input.Epsilon["O.sp2-N"] = 12145.28
settings.input.Epsilon.F = 8435.13
settings.input.Epsilon.P = 82512.21
settings.input.Epsilon.S = 56067.81
settings.input.Epsilon.Cl = 45065.19
settings.input.Epsilon.Br = 62947.83
settings.input.Epsilon.I = 105910.88

# Technical and accuracy parameters
settings.input.Technical.sacconv = 1e-7
settings.input.Technical.maxiter = 10000
settings.input.Technical.bpconv = 1e-6
settings.input.Technical.bpmaxiter = 40
settings.input.Technical.solconv = 1e-5
settings.input.Technical.solmaxiter = 40
settings.input.Technical.solxilarge = 0.99
settings.input.Technical.ehdeltaT = 1.0

# We will vary the cohot parameter (default value 4707.75)
# and observe the effect on activity coefficients
print("Resulting Activity Coefficients:")
print("cohot value".ljust(15), "activity coefficients".ljust(20))
cohot_vals = [4707.75 + 50 * i for i in range(-3, 4)]
for cohot in cohot_vals:

    settings.input.SACParameters.cohot = cohot
    # create a job that can be run by COSMO-RS
    my_job = CRSJob(settings=settings)
    # run the job
    out = my_job.run()
    # convert all the results into a python dict
    res = out.get_results()

    print(str(cohot).ljust(15), str(res["gamma"].flatten()).ljust(20))

finish()
```