# Recipes Reference

## Table of Contents
1. [Overview](#overview)
2. [ADF Fragment Analysis](#adf-fragment-analysis)
3. [ADF NBO Analysis](#adf-nbo-analysis)
4. [Molecular Dynamics Jobs](#molecular-dynamics-jobs)
5. [Numerical Gradients](#numerical-gradients)
6. [Numerical Hessian](#numerical-hessian)
7. [Redox Potential Screening](#redox-potential-screening)
8. [Reorganization Energy](#reorganization-energy)
9. [Reaction Energies](#reaction-energies)

---

## Overview

PLAMS recipes are pre-built workflows in `scm.plams.recipes`:

```python
from scm.plams.recipes.adffragment import ADFFragmentJob
from scm.plams.recipes.adfnbo import ADFNBOJob
from scm.plams.recipes.md.amsmdjob import AMSMDJob, AMSNVTJob, AMSNPTJob, AMSNVEJob
from scm.plams.recipes.numgrad import NumGradJob
from scm.plams.recipes.numhess import NumHessJob
from scm.plams.recipes.redox import AMSRedoxScreeningJob
from scm.plams.recipes.reorganization_energy import ReorganizationEnergyJob
```

---

## ADF Fragment Analysis

Calculates interaction energy between two fragments (e.g., for non-covalent interactions):

```python
from scm.plams.recipes.adffragment import ADFFragmentJob

# Define two fragments
frag1 = plams.from_smiles("CCO")  # ethanol
frag2 = plams.from_smiles("c1ccccc1")  # benzene

settings = plams.Settings()
settings.input.ams.Task = "FragmentAnalysis"

job = ADFFragmentJob(fragment1=frag1, fragment2=frag2, settings=settings)
results = job.run()

# Get interaction energy
props = results.get_properties()
print(f"Interaction energy: {props['E_int']}")
print(f"BSSE: {props.get('E_int_BSSE', 'N/A')}")
```

---

## ADF NBO Analysis

Natural Bond Orbital analysis:

```python
from scm.plams.recipes.adfnbo import ADFNBOJob

settings = plams.Settings()
settings.input.ams.Task = "SinglePoint"
settings.input.ADF.NBO = "Yes"

job = ADFNBOJob(molecule=mol, settings=settings)
results = job.run()
```

---

## Molecular Dynamics Jobs

```python
from scm.plams.recipes.md.amsmdjob import AMSMDJob, AMSNVTJob, AMSNPTJob, AMSNVEJob
```

### Basic MD Job
```python
settings = plams.Settings()
settings.input.ams.Task = "MolecularDynamics"
settings.input.ams.MD.TimeStep = 1.0  # fs
settings.input.ams.MD.NSteps = 10000
settings.input.ams.MD.Temperature = 300
settings.input.DFTB.Model = "GFN1-xTB"

job = AMSMDJob(molecule=mol, settings=settings, name="md_run")
results = job.run()
```

### Pre-defined Ensemble Jobs
```python
# NVT ensemble (canonical)
job = AMSNVTJob(molecule=mol, settings=settings, name="nvt_run")

# NPT ensemble (isothermal-isobaric)
job = AMSNPTJob(molecule=mol, settings=settings, name="npt_run")

# NVE ensemble (microcanonical)
job = AMSNVEJob(molecule=mol, settings=settings, name="nve_run")
```

---

## Numerical Gradients

```python
from scm.plams.recipes.numgrad import NumGradJob

settings = plams.Settings()
settings.input.ams.Task = "SinglePoint"
settings.input.DFTB.Model = "GFN1-xTB"

job = NumGradJob(molecule=mol, settings=settings)
results = job.run()

# Get gradient
gradient = results.get_gradient()
```

---

## Numerical Hessian

```python
from scm.plams.recipes.numhess import NumHessJob

settings = plams.Settings()
settings.input.ams.Task = "SinglePoint"
settings.input.DFTB.Model = "GFN1-xTB"

job = NumHessJob(molecule=mol, settings=settings)
results = job.run()

# Get Hessian and frequencies
hessian = results.get_hessian()
frequencies = results.get_frequencies(unit="cm^-1")
```

---

## Redox Potential Screening

Screen redox potentials for a series of molecules:

```python
from scm.plams.recipes.redox import AMSRedoxScreeningJob

settings = plams.Settings()
settings.input.ams.Task = "SinglePoint"
settings.input.DFTB.Model = "GFN1-xTB"

# Create job for multiple molecules
molecules = [mol1, mol2, mol3]
job = AMSRedoxScreeningJob(molecules=molecules, settings=settings)
results = job.run()

# Get redox potentials
potentials = results.get_redox_potentials()
```

---

## Reorganization Energy

Calculate hole/electron reorganization energy:

```python
from scm.plams.recipes.reorganization_energy import ReorganizationEnergyJob

settings = plams.Settings()
settings.input.ams.Task = "SinglePoint"
settings.input.DFTB.Model = "GFN1-xTB"

job = ReorganizationEnergyJob(molecule=mol, settings=settings)
results = job.run()

# Get reorganization energies
reorg_energy = results.get_reorganization_energy()
```

---

## Reaction Energies

```python
from scm.plams.tools.reaction_energies import reaction_energy, balance_equation

# Balance a reaction automatically
equation = balance_equation(
    reactants=["C", "H", "O"],
    products=["C", "H", "O"],
    reaction=[2, 2, 1],  # 2 H2 + O2 -> 2 H2O
)

# Or specify equation string directly
equation = "2 H2 + O2 -> 2 H2O"

# Calculate reaction energy
energy = reaction_energy(equation, job_settings=settings)
```
