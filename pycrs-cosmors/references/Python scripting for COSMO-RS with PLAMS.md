---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/PLAMS_COSMO-RS_scripting.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Python scripting for COSMO-RS with PLAMS

## General Information

> [!note] Attention
> Windows and Mac users may find it helpful to first read the *Getting Started* guides for scripting: [scripting with Windows](https://www.scm.com/doc/Scripting/GettingStarted.html#windows) | [scripting with MacOS](https://www.scm.com/doc/Scripting/GettingStarted.html#macos)

Python and the [PLAMS library](https://www.scm.com/doc/plams/index.html) can be used for scripting with COSMO-RS. Due to the speed of COSMO-RS calculations, these jobs can be run interactively from the python interpreter. Larger numbers of jobs or high-throughput calculations can also easily be automated with python scripting. All results are returned as a python object, meaning the properties calculated with COSMO-RS can immediately be post-processed or used directly in other python functions.

> [!note] Note
> COSMO-RS calculations require the COSMO result file, either a `.coskf` or `.compkf` file, for each compound in the system. These files only need to be calculated once and then can be stored in a database for reuse in any further calculation involving the same compound.

## Generating COSMO result file

The generation of a `.coskf` file involves calculating calculating the COSMO surface with ADF, which requires a relatively expensive DFT calculation. In contrast, a `.compkf` file provide an estimated sigma profile based on the group contribution method. However, the use of a `.coskf` file is generally recommended for better accuracy.

Before performing a COSMO-RS calculation, ensure the COSMO result files are available for all species involed. If any required files are missing, they can be generated via the GUI or using the following tools:

- **.coskf**: Use the PLAMS recipe, [adfcosmorscompound](https://www.scm.com/doc/PythonExamples/cosmo-rs-compound/index.html) or the command-line tool [amsprep](https://www.scm.com/doc/COSMO-RS/Scripting_Examples.html#tutorial-cosmo-files)
- **.coskf for conformers**: Use the PLAMS recipe, [adfcosmorsconformers](https://www.scm.com/doc/PythonExamples/cosmo-rs-conformers/index.html)
- **.compkf**: Generating using the command-line tool [fastsigma](https://www.scm.com/doc/COSMO-RS/Scripting_Examples.html#tutorial-cosmo-files)

## Executing the code from the command line

It is recommended to use the version of python that is shipped with AMS. This version ensures that all the necessary libraries (e.g., [PLAMS](https://www.scm.com/doc/plams/index.html)) are properly imported and are mutually compatible. The best way to do this is to run the `amspython` program. That can be executed from the command line as follows:

```bash
$AMSBIN/amspython <your_program.py>
```

where `<your_program.py>` should of course be replaced by the name of your program.

## Specifying a problem type

To run COSMO-RS, the user must first provide a problem type for the calculation. This can be done by first creating a `Settings` object and then specifying the `.input.property._h` attribute. For example, to set up an activity coefficient calculation, we do the following:

```python
from scm.plams import Settings, init, finish, CRSJob
import os

settings = Settings()
settings.input.property._h = 'ACTIVITYCOEF'
```

For other problem types, the `.input.property._h` attribute must be set to other values. The other options for this value are summarized below:

| `._h` value | Problem type |
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

## Inputting Compounds

In PLAMS, each compound is also input as a `Settings` object. Additional information about the compounds required for the calculation (e.g., mole fraction) can be specified as an attribute of the compound’s `Settings` object. Ensure the [ADFCRS-2018 Database](https://www.scm.com/doc/COSMO-RS/COSMO-RS_Databases.html#adfcrs-2018) is installed beforehand. An example for a calculation with two compounds is given below.

```python
########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

# set the number of compounds
num_compounds = 2

compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(database_path, "Water.coskf")
compounds[1]._h = os.path.join(database_path, "1-Hexanol.coskf")
```

### User-provided compound files

In addition to the default `.coskf` files, user-provided compound files can also be used.

To use a `.compkf` file generated with [FASTSIGMA](https://www.scm.com/doc/COSMO-RS/Fast_Sigma_QSPR_COSMO_sigma-profiles.html#fastsigma)

```python
compounds[1]._h = os.path.join(compkf_path, "1-Hexanol.compkf")
compounds[1].compkffile = True
```

To use a `.cosmo` file:

```python
compounds[1]._h = os.path.join(cosmo_path, "1-Hexanol.cosmo")
compounds[1].cosmofile = True
```

> [!note] Note
> For the best accuracy, we recommend using an ADF-generated `.coskf` file whenever possible.

## Specifying mole fractions, temperatures, and pressures

Mole fractions are attributes of the compound `Settings` object. There are two types of mole fractions used in COSMO-RS. `frac1` is for standard specification of mole fractions in most problem types. `frac2` is used when the problem type requires two distinct liquid phases (COMPOSITIONLINE or LOGP). Additionally, the temperature can be specified using the `input.temperature` attribute of the `Settings` object. An example of this is shown below:

```python
#set compound mole fractions
compounds[0].frac1 = 0.3
compounds[1].frac1 = 0.7

#set temperature (range)
#to specify a range, use 3 numbers: (1) the lowest temperature,
#(2) the highest temperature, and (3) the steps taken between these temperatures
settings.input.temperature = "298.15"
```

To specify a temperature range, set the `input.temperature` object equal to a python `str` which contains the lower temperature, upper temperature, and number of steps taken between the temperatures. These values should simply be separated by spaces. For example, to specify that a calculation should go over the temperature range 298.15K to 398.15K with 10 temperature steps, do the following:

Note: Temperature range is only used for calculation of vapor pressure and solubility.

```python
settings.input.temperature = "298.15 398.15 10"
```

Pressure works in much the same way. To input the system pressure (in bar), do the following:

```python
settings.input.pressure = "1.5"
```

Note: Pressure is only used in calculation of boiling temperature, gas solubility, isobar binary mixture and isobar ternary mixture.

## Running jobs

To run a job with COSMO-RS, first assign the `input.compound` attribute to the list of compound `Settings` objects used previously. Then, simply create the job using `CRSJob(settings=<your previously defined Settings object>)`. Once a job is created, you can run it with the `.run()` function. An example of this is given below:

```python
# specify the compounds as the compounds to be used in the calculation
settings.input.compound = compounds
# create a job that can be run by COSMO-RS
my_job = CRSJob(settings=settings)
# run the job
init()
out = my_job.run()
finish()
```

## Reading the results of a job

Once a job has finished running, we can access the results directly in python. First, we can check to see which properties are available. We can do this using the `get_prop_names()` function on the output. For example, adding the line:

```python
# check for the available properties
print( "Available properties:", out.get_prop_names() )
```

gives us the available properties as a python `set` for our calculation type (“ACTIVITYCOEF” in this case). The result of the print statement is the following:

```
Available properties: {'henrycnodim', 'property', 'deltag', 'henryc', 'nitems', 'gamma',
'ncomp', 'filename', 'temperature', 'frac1', 'G solute', 'mu gas', 'molmass', 'E gas',
'mu', 'usepolyunits', 'mu pure', 'method'}
```

We can also convert all of the calculation results to a python `dict` using the `get_results()` function. For example, to collect all of the results and then print the activity coefficient values (“gamma”), we write the following code:

```python
# convert all the results into a python dict
res = out.get_results()
print( "Activity coef values:\n", res["gamma"] )
```

This results in the following program output:

```
Activity coef values:
 [[ 3.71486   ]
 [ 1.04484607]]
```

Here the two activity coefficient values are returned as elements in a `numpy.ndarray`. Properties with multiple values are always stored as a numpy array.

> [!note] Note
> For properties with multiple values, the dictionary values are stored as a `numpy.ndarray`. If applicable to the calculation, the rows of the array represent different compounds and the columns represent different steps of the calculation (e.g., different temperatures/pressures or different mole fractions for a binary/ternary mixture calculation).

Putting all the previous code together, we have the following working example for calculating activity coefficients for 2 components:

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
settings.input.property._h = "ACTIVITYCOEF"

# set the number of compounds
num_compounds = 2

compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(database_path, "Water.coskf")
compounds[1]._h = os.path.join(database_path, "1-Hexanol.coskf")

# set compound mole fractions
compounds[0].frac1 = 0.3
compounds[1].frac1 = 0.7

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

# check for the available properties
print("Available properties:", out.get_prop_names())

# convert all the results into a python dict
res = out.get_results()
print("Activity coef values:\n", res["gamma"])
```

## Plotting results

2D graphs can also be generated to visualize the results with the `plot` function. The `plot` function takes as a first argument any (or multiple) of the following:

- a `numpy.ndarray` object. This can be passed to the function as a dictionary value after calling the `get_results()` function.
- the name of a property. This property is read from the results and plotted. For a list of available properties, use the `get_prop_names()` function.

Additionally, the `plot` function takes the following keyword arguments:

- `x_axis`. This can be the name of a property or a `numpy.ndarray` object. This represents the independent variable in the plot. This value must be one dimensional, meaning it cannot be indexed over both compounds and temperatures.
- `x_label`. This can be used to label the x axis in the plot.
- `y_label`. This can be used to label the y axis in the plot.
- `plot_fig`. This is set to True/False to indicate whether a plotted figure should be displayed. The default is True.

The results of `plot` are returned as a `matplotlib.pyplot` object and can be further modified.

To demonstrate the use of plot, we do an example in which we calculate the solubility of methane gas in 1-Octanol and Ethanol across the temperature range from 298.15K to 398.15K. We also include the vapor pressure of methane using the VPM1 model. The code is shown below:

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
settings.input.property._h = "PURESOLUBILITY"

# this indicates we're calculating gas solubility
settings.input.property.isobar = ""

# set the number of compounds
num_compounds = 3

compounds = [Settings() for i in range(num_compounds)]
compounds[0]._h = os.path.join(database_path, "Methane.coskf")
compounds[1]._h = os.path.join(database_path, "1-Octanol.coskf")
compounds[2]._h = os.path.join(database_path, "Ethanol.coskf")

# set compound mole fractions
# for pure solubility the solvent gets a mole fraction of 1
# and the solute does not have the frac1 attribute
compounds[1].frac1 = 1
compounds[2].frac1 = 1

# specify the vapor pressure equation for methane
compounds[0].vp_equation = "VPM1"
compounds[0].vp_params = "-1039.67755001 -0.183945615995 0.00061368649128 10.1113503603315 0.0"

# set temperature (range)
# to specify a range, use 3 numbers: (1) the lowest temperature,
# (2) the highest temperature, and (3) the steps taken between these temperatures
settings.input.temperature = "298.15 398.15 10"

# 1 atm = 1.01325 bar
settings.input.pressure = "1.01325"

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

# plot the solubilities in g/L solution
# the [1:] indicates that we're not plotting the values for methane (these are automatically set to 0)
plt = out.plot(
    res["solubility g_per_L_solution"][1:],
    x_axis="temperature",
    x_label="Temperature",
    y_label="solubility g/L solution",
)
# plt.savefig("./PLAMS_gas_solubility.png")
```

This code generates the following plot:

Fig. 3 The output of the `plot` function for a gas solubility calculation.[¶](Python%20scripting%20for%20COSMO-RS%20with%20PLAMS.md#id1)