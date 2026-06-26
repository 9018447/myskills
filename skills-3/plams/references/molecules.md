# Molecules Reference

## Table of Contents
1. [Creating Molecules](#creating-molecules)
2. [ASE Integration](#ase-integration)
3. [RDKit Integration](#rdkit-integration)
4. [Conformer Generation](#conformer-generation)
5. [File I/O](#file-io)
6. [Solvation with PackMol](#solvation-with-packmol)

---

## Creating Molecules

### From SMILES
```python
water = plams.from_smiles("O")
ethanol = plams.from_smiles("CCO")
benzene = plams.from_smiles("c1ccccc1")
```

### From PDB File
```python
mol = plams.readpdb("molecule.pdb")
```

### Build Manually
```python
mol = plams.Molecule()
mol.add_atom(plams.Atom(symbol="O", coords=(0, 0, 0)))
mol.add_atom(plams.Atom(symbol="H", coords=(1, 0, 0)))
mol.add_atom(plams.Atom(symbol="H", coords=(0, 1, 0)))
```

### From XYZ File
```python
mol = plams.Molecule("water.xyz")
```

---

## ASE Integration

### Convert ASE Atoms to PLAMS Molecule
```python
from scm.plams import fromASE
ase_atoms = ...  # ASE Atoms object
mol = fromASE(ase_atoms)
```

### Convert PLAMS Molecule to ASE Atoms
```python
from scm.plams import toASE
ase_atoms = toASE(mol)
```

---

## RDKit Integration

```python
from scm.plams.interfaces.molecule.rdkit import (
    from_smiles, to_smiles, from_rdmol, to_rdmol,
    add_Hs, get_conformations, canonicalize_mol
)
```

### Basic RDKit Operations
```python
# Create from SMILES
mol = from_smiles("c1ccccc1")  # benzene

# Add hydrogens
mol_with_H = add_Hs(mol)

# Get canonical form
mol_canonical = canonicalize_mol(mol)

# Convert to RDKit molecule for further manipulation
rdmol = to_rdmol(mol)

# Convert back to PLAMS
plams_mol = from_rdmol(rdmol)
```

---

## Conformer Generation

```python
from scm.plams.interfaces.molecule.rdkit import get_conformations

# Generate multiple conformers
mol = plams.from_smiles("CCCC")  # butane
conformers = get_conformations(mol, n_confs=50)

# Optimize each conformer
for i, conf in enumerate(conformers):
    job = plams.AMSJob(molecule=conf, settings=settings, name=f"butane_conf_{i}")
    job.run()
```

---

## File I/O

### Reading Molecules
```python
# Single molecule
mol = plams.Molecule("water.xyz")

# Multiple frames (trajectory)
mols = plams.read_molecules("trajectory.xyz")
```

### Writing Molecules
```python
mol.write("output.xyz")
mol.write("output.pdb")
mol.write("output.gro")  # GROMACS format
```

### Trajectory Files
```python
from scm.plams.trajectories import RKFTrajectoryFile, XYZTrajectoryFile

# Read RKF trajectory
traj = RKFTrajectoryFile("simulation.rkf")
frames = traj.read()

# Read XYZ trajectory
traj_xyz = XYZTrajectoryFile("trajectory.xyz")
frames_xyz = traj_xyz.read()
```

---

## Solvation with PackMol

```python
from scm.plams.interfaces.molecule.packmol import packmol_around, packmol_microsolvation

# Solvate a protein/molecule in a water box
solvated = packmol_around(
    solute=protein,
    n_solecules=1000,
    box_distance=10.0  # Angstrom padding
)

# Microsolvation (sphere of water)
microsolvated = packmol_microsolvation(
    solute=mol,
    n_molecules=50,
    radius=15.0
)

# Use solvated molecule for MD
job = AMSMDJob(molecule=solvated, settings=settings)
```
