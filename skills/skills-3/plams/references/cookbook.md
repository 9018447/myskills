# Cookbook - Common Patterns

## Table of Contents
1. [Parallel Job Execution](#parallel-job-execution)
2. [Unit Conversion](#unit-conversion)
3. [ASE Calculator Interface](#ase-calculator-interface)
4. [Transition State Search](#transition-state-search)
5. [MD Analysis](#md-analysis)
6. [Batch Processing](#batch-processing)

---

## Parallel Job Execution

### MultiJob (Run Jobs in Sequence)
```python
from scm.plams.core.basejob import MultiJob

multi = MultiJob(children=[
    (preopt_job, optimize_job, final_job)
])
results = multi.run()
```

### MultiJob (Run Jobs in Parallel)
```python
# Create multiple jobs
jobs = []
for i, mol in enumerate(molecules):
    job = plams.AMSJob(molecule=mol, settings=settings, name=f"job_{i}")
    jobs.append(job)

# Run all in parallel
multi = MultiJob(children=jobs)
all_results = multi.run()
```

### GridRunner (Large-scale Parallelization)
```python
from scm.plams.core.jobrunner import GridRunner

runner = GridRunner(parallel=True, maxjobs=8)

# Submit jobs to the runner
for mol in molecules:
    job = plams.AMSJob(molecule=mol, settings=settings)
    runner.submit(job)

# Collect results
results = runner.wait()
```

---

## Unit Conversion

```python
from scm.plams.tools.units import Units

# Energy conversion
energy_au = results.get_energy()  # atomic units (Hartree)
energy_kcal = Units.convert(energy_au, "au", "kcal/mol")
energy_ev = Units.convert(energy_au, "au", "eV")
energy_j = Units.convert(energy_au, "au", "J")

# Length conversion
length_ang = Units.convert(5.0, "au", "angstrom")
length_bohr = Units.convert(1.0, "angstrom", "au")

# Angle conversion
angle_deg = Units.convert(3.14159, "rad", "degree")
angle_rad = Units.convert(180.0, "degree", "rad")

# Temperature
temp_k = Units.convert(298.15, "K", "K")  # already in K

# Pressure
pressure_pa = Units.convert(1.0, "bar", "Pa")
```

---

## ASE Calculator Interface

Use AMS engines through ASE:

```python
from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator
from ase.build import molecule
from ase.optimize import LBFGS, QuasiNewton
from ase.neb import NEB

# Water optimization via ASE
atoms = molecule("H2O")
atoms.set_calculator(AMSCalculator(settings=settings))

# Optimize
dyn = LBFGS(atoms)
dyn.run(fmax=0.05)

# Get results
energy = atoms.get_potential_energy()
forces = atoms.get_forces()
```

### NEB (Nudged Elastic Band) for Reaction Paths
```python
from ase.neb import NEB
from ase.optimize import MDMin

# Initial and final states
initial = plams.from_smiles("CCO").toASE()  # ethanol
final = plams.from_smiles("CC=O").toASE()   # acetaldehyde

# Create NEB
images = [initial]
for i in range(5):
    images.append(initial.copy())
images.append(final)

neb = NEB(images, climb=True)
neb.attach(AMSCalculator(settings=settings), images=range(1, len(images)-1))

# Optimize reaction path
optimizer = MDMin(neb, dt=0.1)
optimizer.run(fmax=0.05)
```

---

## Transition State Search

### Using Sella Interface
```python
from scm.plams.interfaces.molecule.sella import SellaTSJob

settings = plams.Settings()
settings.input.ams.Task = "SinglePoint"
settings.input.DFTB.Model = "GFN1-xTB"

# Create TS job from initial guess
job = SellaTSJob(
    molecule=initial_guess,
    settings=settings,
    reaction_coordinate="distance"
)
results = job.run()

# Verify with frequency calculation
freq_job = plams.AMSJob(molecule=results.get_main_molecule(), settings=settings)
freq_results = freq_job.run()
freqs = freq_results.get_frequencies()
has_single_imaginary = sum(1 for f in freqs if f < 0) == 1
```

---

## MD Analysis

### Basic Trajectory Analysis
```python
from scm.plams.trajectories import RKFTrajectoryFile

# Load trajectory
traj = RKFTrajectoryFile("simulation.rkf")
frames = traj.read()

# Analyze each frame
for i, frame in enumerate(frames):
    energy = frame.get_energy()
    print(f"Frame {i}: E = {energy}")

# Get RMSD from reference
import numpy as np
ref_coords = frames[0].get_coordinates()
for frame in frames[1:]:
    coords = frame.get_coordinates()
    rmsd = np.sqrt(np.mean(np.sum((coords - ref_coords)**2, axis=1)))
    print(f"RMSD: {rmsd}")
```

### Radial Distribution Function
```python
from scm.plams.trajectories import RKFTrajectoryFile

traj = RKFTrajectoryFile("simulation.rkf")
frames = traj.read()

# Simple RDF calculation
def compute_rdf(frames, r_max=10.0, n_bins=100):
    rdf = np.zeros(n_bins)
    dr = r_max / n_bins

    for frame in frames:
        coords = frame.get_coordinates()
        for i in range(len(coords)):
            for j in range(i+1, len(coords)):
                r = np.linalg.norm(coords[i] - coords[j])
                if r < r_max:
                    bin_idx = int(r / dr)
                    rdf[bin_idx] += 2  # Pair count

    # Normalize
    r = np.linspace(0, r_max, n_bins)
    rdf = rdf / (len(frames) * r**2)  # Simplified normalization
    return r, rdf
```

---

## Batch Processing

### Process Multiple Molecules
```python
molecules = [plams.from_smiles(smi) for smi in smiles_list]

settings = plams.Settings()
settings.input.ams.Task = "GeometryOptimization"
settings.input.DFTB.Model = "GFN1-xTB"

results_dict = {}
for i, mol in enumerate(molecules):
    job = plams.AMSJob(molecule=mol, settings=settings, name=f"mol_{i}")
    results = job.run()
    results_dict[i] = {
        'energy': results.get_energy(),
        'geometry': results.get_main_molecule()
    }
```

### Batch Conformational Analysis
```python
from scm.plams.interfaces.molecule.rdkit import get_conformations

mol = plams.from_smiles("CCCCCCCC")  # octane

# Generate conformers
conformers = get_conformations(mol, n_confs=100)

# Optimize all conformers
settings = plams.Settings()
settings.input.ams.Task = "GeometryOptimization"
settings.input.DFTB.Model = "GFN1-xTB"

jobs = []
for i, conf in enumerate(conformers):
    job = plams.AMSJob(molecule=conf, settings=settings, name=f"octane_conf_{i}")
    jobs.append(job)

# Run in batches
batch_size = 10
all_results = []
for i in range(0, len(jobs), batch_size):
    batch = jobs[i:i+batch_size]
    multi = MultiJob(children=batch)
    all_results.extend(multi.run().children)
```

---

## Common Helper Patterns

### Check Molecule Validity
```python
def validate_molecule(mol):
    """Check if molecule is valid for calculation."""
    if mol is None:
        return False, "Molecule is None"
    if len(mol) == 0:
        return False, "Molecule has no atoms"
    # Check for duplicate atoms
    coords = mol.get_coordinates()
    if len(np.unique(coords, axis=0)) != len(coords):
        return False, "Duplicate atom coordinates"
    return True, "OK"
```

### Energy Comparison
```python
def compare_energies(results1, results2, unit="kcal/mol"):
    """Compare energies between two results objects."""
    e1 = results1.get_energy(unit=unit)
    e2 = results2.get_energy(unit=unit)
    diff = e1 - e2
    return {
        'e1': e1,
        'e2': e2,
        'difference': diff,
        'percent_diff': abs(diff / e2) * 100 if e2 != 0 else float('inf')
    }
```
