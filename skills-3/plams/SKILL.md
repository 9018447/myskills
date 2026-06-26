---
name: plams
description: PLAMS (Python Library for Automating Molecular Simulation) skill for computational chemistry workflows. Use when working with molecular modeling, computational chemistry calculations, AMS (Amsterdam Modeling Suite), DFTB, force fields, molecular dynamics, geometry optimization, conformer generation, solvation boxes, or automating chemistry simulation workflows. Trigger whenever the user mentions molecular simulation, computational chemistry, AMS, DFTB, GFN-xTB, ADF, BAND, or wants to create/run/analyze chemistry calculations programmatically.
author: SCM (Software for Chemistry and Materials)
source: https://github.com/SCM-NV/PLAMS
version: 2023.10.1
based_on_commit: 55cedba2
---

# PLAMS - Python Library for Automating Molecular Simulation

PLAMS is a flexible toolkit for automating computational chemistry calculations including geometry optimization, molecular dynamics, property prediction, and multi-step reaction pathways.

> **Version Policy:** This skill targets **PLAMS 2023.105** interfaces. The official documentation in `references/plams_2023.105/` reflects this version. Newer PLAMS versions may have different APIs - always check your installed version first.

## Key Capabilities

- **AMS Engine Integration**: DFTB, GFN-xTB, Force Fields via `AMSJob`
- **Third-Party Interfaces**: RDKit, ASE, ORCA, CP2K, VASP, and more
- **Parallel Processing**: Run multiple jobs concurrently
- **PackMol Integration**: Generate solvation boxes and microsolvation spheres
- **Automatic File Organization**: Manages job directories and restarts
- **Pre-built Workflows**: Fragment analysis, redox potentials, conformer generation

For full capabilities and detailed reference, see `references/` directory.

## Quick Start

### Initialization
```python
import scm.plams as plams
plams.init()
# ... your code ...
plams.finish()
```

### Create Molecule
```python
mol = plams.from_smiles("CCO")  # ethanol
```

### Configure and Run Job
```python
settings = plams.Settings()
settings.input.ams.Task = "GeometryOptimization"
settings.input.DFTB.Model = "GFN1-xTB"

job = plams.AMSJob(molecule=mol, settings=settings, name="ethanol_opt")
results = job.run()

# Get results
energy = results.get_energy(unit="kcal/mol")
optimized = results.get_main_molecule()
```

## Core Patterns

### Molecules
```python
# From SMILES, PDB, XYZ, or ASE
mol = plams.from_smiles("O")          # water
mol = plams.readpdb("protein.pdb")    # from file
mol = plams.Molecule("structure.xyz")  # XYZ file
```

### Settings (nested dict)
```python
settings = plams.Settings()
settings.input.ams.Task = "GeometryOptimization"
settings.input.DFTB.Model = "GFN1-xTB"
settings.input.ams.Properties.NormalModes = "Yes"
```

### Jobs
```python
job = plams.AMSJob(molecule=mol, settings=settings, name="opt")
results = job.run()
print(job.status)  # SUCCESS / RUNNING / FAILED
```

### Result Extraction
```python
results.get_main_molecule()      # optimized geometry
results.get_energy(unit="eV")    # energy
results.get_frequencies(unit="cm^-1")  # vibrational frequencies
results.get_dipolemoment(unit="debye")  # dipole
results.readrkf("Section", "Var")  # raw RKF data
```

### MultiJob (sequential or parallel)
```python
multi = MultiJob(children=[job1, job2, job3])
all_results = multi.run()
```

## Common Workflows

### Geometry Optimization (most common)
```python
mol = plams.from_smiles("CCO")
settings = plams.Settings()
settings.input.ams.Task = "GeometryOptimization"
settings.input.DFTB.Model = "GFN1-xTB"

job = plams.AMSJob(molecule=mol, settings=settings, name="opt")
results = job.run()
print(f"Energy: {results.get_energy(unit='kcal/mol')} kcal/mol")
```

### Molecular Dynamics
```python
settings.input.ams.Task = "MolecularDynamics"
settings.input.ams.MD.TimeStep = 1.0      # fs
settings.input.ams.MD.NSteps = 10000
settings.input.ams.MD.Temperature = 300    # K
settings.input.ams.MD.Thermostat.Type = "NVT"

job = AMSMDJob(molecule=solvated, settings=settings, name="md")
results = job.run()
```

## Detailed Reference

**For advanced topics, see `references/` directory:**

| Topic | File |
|-------|------|
| Molecules, RDKit, conformers, file I/O | `references/molecules.md` |
| Engine-specific settings, MD parameters | `references/settings.md` |
| Result extraction methods | `references/referencesults.md` |
| All recipes (fragment, NBO, MD, redox) | `references/recipes.md` |
| Error handling and debugging | `references/troubleshooting.md` |
| Parallel execution, ASE, NEB, MD analysis | `references/cookbook.md` |

## Engine Selection

```python
# DFTB (GFN1-xTB or GFN2-xTB)
settings.input.DFTB.Model = "GFN1-xTB"

# Force Field (UFF, DFFA)
settings.input.ForceField.Type = "UFF"

# GFN2-xTB (AMS2024+ default)
settings.input.GFN2xTB
```

## Troubleshooting

### Job failed?
```python
if not job.check():
    print(f"Error: {job.get_errormsg()}")
    print(job.results.get_output())
```

## Examples Directory

The `examples/` subdirectory contains working examples:
- `examples/ADFFrag/` - Fragment analysis
- `examples/ConformersGeneration/` - Conformer workflows
- `examples/BasicMDAnalysis/` - MD post-analysis
- `examples/PackMolExample/` - Solvation boxes
- See `examples/README.md` for full listing

## Key Imports

```python
from scm.plams import from_smiles, Settings, AMSJob, Molecule
from scm.plams.recipes.md.amsmdjob import AMSMDJob
from scm.plams.recipes.adffragment import ADFFragmentJob
from scm.plams.interfaces.molecule.packmol import packmol_around
from scm.plams.interfaces.molecule.rdkit import get_conformations
from scm.plams.tools.units import Units
```
## Running Scripts

All PLAMS scripts should be run with `amspython` (provided by AMS installation):

```bash
amspython script.py [arguments]
```

Example:
```bash
amspython scripts/opt_freq_calculation.py molecule.xyz
```

## Available Scripts

- `scripts/opt_freq_calculation.py` - Geometry optimization and frequency calculation
