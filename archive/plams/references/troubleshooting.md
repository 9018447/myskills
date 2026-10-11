# Troubleshooting Reference

## Table of Contents
1. [Job Failures](#job-failures)
2. [Missing Optional Packages](#missing-optional-packages)
3. [Running Outside AMS](#running-outside-ams)
4. [Memory Issues](#memory-issues)
5. [Convergence Problems](#convergence-problems)

---

## Job Failures

### Check Job Status
```python
if not job.check():
    print(f"Job failed: {job.get_errormsg()}")

    # Get error details
    print(job.results.get_output())

    # Check specific error file
    import os
    if os.path.exists(job.path + "/stderr.out"):
        with open(job.path + "/stderr.out") as f:
            print(f.read())
```

### Restart a Failed Job
```python
# Delete old results and rerun
job.delete()

# Or use restart method
results = job.restart()
```

### Investigate Output Files
```python
# List all files in job directory
import os
print(os.listdir(job.path))

# Read output file
with open(job.path + "/ams.out") as f:
    print(f.read())
```

---

## Missing Optional Packages

### RDKit
```python
try:
    from scm.plams.interfaces.molecule.rdkit import from_smiles
except plams.MissingOptionalPackageError:
    print("RDKit not installed. Install with: pip install rdkit")
```

### ASE
```python
try:
    from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator
except plams.MissingOptionalPackageError:
    print("ASE not installed. Install with: pip install ase")
```

### PackMol
```python
try:
    from scm.plams.interfaces.molecule.packmol import packmol_around
except plams.MissingOptionalPackageError:
    print("PackMol not installed. See AMS documentation for installation.")
```

---

## Running Outside AMS

### Standalone PLAMS Installation
```bash
pip install plams
pip install 'plams[chem,analysis,ams]'  # optional deps
```

### AMSPipe (for running AMS jobs outside amspython)
```bash
pip install $AMSHOME/scripting/scm/amspipe
```

### Verify PLAMS Installation
```python
import scm.plams as plams
print(plams.__version__)
```

---

## Memory Issues

### Reduce Memory Usage
```python
# Disable backup files
settings = plams.Settings()
settings.input.ams.Backup = "No"

# Use smaller cache
plams.config.memory_cache_size = 100  # MB
```

### Clear Cache
```python
# Clear molecule cache
plams.Molecule._cache.clear()

# Clear job cache
plams.Job._cache.clear()
```

---

## Convergence Problems

### Geometry Optimization
```python
# Increase iterations
settings.input.ams.GeometryOptimization.MaxIterations = 500

# Tighten convergence criteria
settings.input.ams.GeometryOptimization.Convergence.Energy = 1e-6
settings.input.ams.GeometryOptimization.Convergence.Grad = 1e-3

# Use different optimizer
settings.input.ams.GeometryOptimization.Optimizer.Type = "LBFGS"
```

### SCF Convergence
```python
# For ADF
settings.input.ADF.SCF.Conververge = 1e-6
settings.input.ADF.SCF.Iterations = 500

# For DFTB
settings.input.DFTB.SCF.Converge = 1e-5
```

### Molecular Dynamics
```python
# Reduce time step if unstable
settings.input.ams.MD.TimeStep = 0.5  # fs instead of 1.0

# Adjust thermostat
settings.input.ams.MD.Thermostat.Tau = 50  # shorter coupling
```

---

## Common Error Messages

### "Could not find AMSResults"
```python
# Job may not have completed
if job.status == JobStatus.SUCCESS:
    results = job.results
else:
    print("Job did not complete successfully")
```

### "No such file or directory" (RKF file)
```python
# Check if file exists
import os
if os.path.exists(job.path + "/ams.rkf"):
    results = job.results
else:
    print("RKF file not found - job may have failed early")
```

### "Dimension mismatch"
Usually indicates corrupted trajectory or molecule object. Try re-reading:
```python
mol = plams.Molecule("input.xyz")
```
