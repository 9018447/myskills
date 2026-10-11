# MDAnalysis API Reference

## Core Classes

### `MDAnalysis.Universe`

Main class for loading and manipulating molecular systems.

```python
u = mda.Universe(topology, trajectory)
```

**Parameters:**
- `topology`: Path to topology file (PDB, PSF, etc.)
- `trajectory`: Path to trajectory file (DCD, XTC, etc.)

**Key attributes:**
- `u.atoms`: All atoms in the system
- `u.trajectory`: Trajectory iterator
- `u.dimensions`: Box dimensions

### `MDAnalysis.AtomGroup`

Group of atoms selected from a Universe.

```python
ag = u.select_atoms('selection string')
```

**Key methods:**
- `ag.center_of_mass()`: Calculate center of mass
- `ag.positions`: Get atomic positions
- `ag.velocities`: Get atomic velocities
- `ag.forces`: Get atomic forces

## Analysis Modules

### `MDAnalysis.analysis.align`
Structural alignment and RMSD fitting

### `MDAnalysis.analysis.hydrogenbonds`
Hydrogen bond analysis

### `MDAnalysis.analysis.rms`
Root-mean-square deviation calculations

### `MDAnalysis.analysis.pca`
Principal component analysis

### `MDAnalysis.analysis.msd`
Mean square displacement

### `MDAnalysis.analysis.rdf`
Radial distribution functions

### `MDAnalysis.analysis.contacts`
Contact analysis

### `MDAnalysis.analysis.dihedrals`
Dihedral angle analysis

## Selection Syntax

MDAnalysis supports powerful atom selection strings:

```python
# By name
u.select_atoms('name CA')

# By residue
u.select_atoms('resname ARG')

# By atom ID
u.select_atoms('byres id 1:100')

# By property
u.select_atoms('prop x > 10')

# Combined selections
u.select_atoms('protein and name CA')
u.select_atoms('resname ARG and (name NH1 or name NH2)')
```

## Supported Formats

### Trajectory Formats
- DCD, XTC, TRR (Gromacs)
- NCDF (NetCDF)
- H5MD (HDF5 molecular data)
- LAMMPS data files
- GSD (HOOMD-blue)
- MMTF (Macromolecular Transmission Format)

### Topology Formats
- PDB, PQR, PDBQT
- PSF, TOP
- GRO
- MOL2
- TPR (Gromacs)
- ITP, CRD

## Transformations

```python
from MDAnalysis.transformations import translate, rotate

# Shift coordinates by 10 Å in x-direction
u.trajectory.add_transformations(translate([10, 0, 0]))

# Rotate around z-axis
u.trajectory.add_transformations(rotate(45, [0, 0, 1]))
```

## Distance Library (`MDAnalysis.lib.distances`)

C-optimized distance functions that work with raw NumPy arrays (no Universe required):

- **`distance_array(ref, conf, box=None)`** — Full (N, M) distance matrix between two groups
- **`self_distance_array(coords, box=None)`** — Compressed distance matrix for a single group
- **`capped_distance(ref, conf, max_cutoff, min_cutoff=None, box=None, method='bruteforce')`** — Efficient neighbor pair search within cutoff; returns `(pairs, distances)`. Methods: `'bruteforce'`, `'pkdtree'`, `'nsgrid'`
- **`self_capped_distance(coords, max_cutoff, ...)`** — Same-group neighbor search
- **`calc_angles(coords1, coords2, coords3, box=None)`** — Three-atom angles in radians
- **`calc_dihedrals(coords1, coords2, coords3, coords4, box=None)`** — Four-atom dihedral angles in radians

The `box` parameter accepts `[a, b, c, alpha, beta, gamma]` to apply minimum image convention.

## LAMMPS Format Loading

```python
# Load LAMMPS DUMP file as both topology and trajectory
u = mda.Universe('dump.lammpstrj', topology_format='LAMMPSDUMP')

# Atom types are accessible via selection strings
type1 = u.select_atoms('type 1')

# Masses and charges may need manual assignment
u.select_atoms('type 1').masses = 58.69  # Ni
```
