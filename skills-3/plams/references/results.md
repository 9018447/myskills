# Results Reference

## Table of Contents
1. [Getting Results](#getting-results)
2. [Geometry](#geometry)
3. [Energy](#energy)
4. [Frequencies and Hessian](#frequencies-and-hessian)
5. [Dipole and Polarizability](#dipole-and-polarizability)
6. [Orbitals](#orbitals)
7. [IR Spectrum](#ir-spectrum)
8. [Reading RKF Files Directly](#reading-rkf-files-directly)

---

## Getting Results

```python
results = job.run()

# Check status
print(job.status)  # JobStatus.SUCCESS / RUNNING / FAILED

# Get output if job failed
if not job.check():
    print(f"Job failed: {job.get_errormsg()}")
    print(job.results.get_output())
```

---

## Geometry

```python
# Optimized molecule
optimized_mol = results.get_main_molecule()

# Input molecule (for comparison)
input_mol = results.get_input_molecule()

# Get geometry as dictionary
coords = results.get_coordinates()  # returns list of (x, y, z) tuples
```

---

## Energy

```python
# Default returns atomic units (Hartree)
energy_au = results.get_energy()

# Specify unit
energy_kcal = results.get_energy(unit="kcal/mol")
energy_ev = results.get_energy(unit="eV")
energy_gh = results.get_energy(unit="kcal/mol")  # Gibbs free energy

# Different energy components
energy_components = results.get_energy_components()
```

---

## Frequencies and Hessian

```python
# Get vibrational frequencies
freqs = results.get_frequencies(unit="cm^-1")

# Get Hessian matrix
hessian = results.get_hessian()

# Get normal modes
modes = results.get_normal_modes()

# Check if molecule is stable (no imaginary frequencies)
has_imaginary = any(f < 0 for f in freqs)
```

---

## Dipole and Polarizability

```python
# Dipole vector
dipole = results.get_dipole_vector(unit="au")

# Dipole moment in Debye
dipole_debye = results.get_dipolemoment(unit="debye")

# Polarizability
polarizability = results.get_polarizability(unit="au")
```

---

## Orbitals (AMS2023+)

```python
# HOMO energies
homo_energies = results.get_homo_energies(unit="eV")

# LUMO energies
lumo_energies = results.get_lumo_energies(unit="eV")

# HOMO-LUMO gap
gap = results.get_smallest_homo_lumo_gap(unit="eV")

# All orbital energies
orbital_energies = results.get_orbitals_energy(unit="eV")

# Orbital coefficients (for visualization)
orbital_coeffs = results.get_orbitals_coefficients()
```

---

## IR Spectrum

```python
# Get IR spectrum
ir = results.get_ir_spectrum()

# Spectrum is dict with 'frequencies' and 'intensities'
frequencies = ir['frequencies']
intensities = ir['intensities']

# Wavenumber range for plots
wavenumbers = frequencies  # in cm^-1
```

---

## Reading RKF Files Directly

For properties not exposed by PLAMS methods:

```python
# Read arbitrary RKF data
value = results.readrkf("SectionName", "VariableName", file="ams")
# file can be: "ams", "adf", "band", "dftb", "forcefield", etc.

# Example: read energy from ADF result
energy = results.readrkf("ADF", "ETOTAL", file="adf")

# List available sections
sections = results.listrkf(file="ams")
```

---

## Fragment Analysis Results

```python
from scm.plams.recipes.adffragment import ADFFragmentJob

job = ADFFragmentJob(fragment1=frag1, fragment2=frag2, settings=settings)
results = job.run()

# Get all properties
props = results.get_properties()

# Key properties
print(f"Interaction energy: {props['E_int']}")
print(f"BSSE corrected energy: {props['E_int_BSSE']}")
print(f"Fragment energies: {props['E_frag1']}, {props['E_frag2']}")
```
