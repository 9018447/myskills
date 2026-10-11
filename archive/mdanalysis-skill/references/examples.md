# MDAnalysis Quick Start Examples

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Building a Universe](#building-a-universe)
3. [RMSD Calculation](#rmsd-calculation)
4. [Distance Analysis](#distance-analysis)
5. [Hydrogen Bond Analysis](#hydrogen-bond-analysis)
6. [Parallel Analysis](#parallel-analysis)
7. [Custom Analysis Class](#custom-analysis-class)
8. [Distance Library Functions](#distance-library-functions)
9. [LAMMPS and XYZ Format Loading](#lammps-and-xyz-format-loading)
10. [Memory Optimization](#memory-optimization)

---

## Basic Usage

```python
import MDAnalysis as mda

# Load simulation results with a single line
u = mda.Universe('topol.tpr', 'traj.trr')

# Select atoms
ag = u.select_atoms('name OH')

# Atom data made available as Numpy arrays
print(ag.positions)
print(ag.velocities)
print(ag.forces)

# Iterate through trajectories
for ts in u.trajectory:
    print(ag.center_of_mass())
```

## Building a Universe

```python
import MDAnalysis

# Build a universe from topology and trajectory
PSF = 'protein.psf'
DCD = 'trajectory.dcd'
u = MDAnalysis.Universe(PSF, DCD)

# Select C-alpha atoms
ca = u.select_atoms('name CA')
print(f"Number of CA atoms: {len(ca)}")

# Calculate center of mass
com = ca.center_of_mass()
print(f"CA center of mass: {com}")

# Calculate all atoms center of mass
all_com = u.atoms.center_of_mass()
print(f"All atoms center of mass: {all_com}")
```

## RMSD Calculation

```python
import MDAnalysis as mda
from MDAnalysis.analysis import align

# Load universe
u = mda.Universe('topology.pdb', 'trajectory.xtc')

# Select backbone
mobile = u.select_atoms('backbone')
reference = u.select_atoms('backbone')

# Align to first frame
aligner = align.AlignTraj(u, u, select='backbone', in_memory=True)
aligner.run()
```

## Distance Analysis

```python
import MDAnalysis as mda

u = mda.Universe('topology.pdb', 'trajectory.xtc')

# Select two groups
group1 = u.select_atoms('resname ARG')
group2 = u.select_atoms('resname ASP')

# Calculate distances
for ts in u.trajectory:
    dist = mda.lib.distances.distance_array(
        group1.positions, 
        group2.positions
    )
    min_dist = dist.min()
    print(f"Frame {ts.frame}: minimum distance = {min_dist:.2f} Å")
```

## Hydrogen Bond Analysis

```python
import MDAnalysis as mda
from MDAnalysis.analysis.hydrogenbonds import HydrogenBondAnalysis

u = mda.Universe('topology.pdb', 'trajectory.xtc')

# Set up hydrogen bond analysis
hbonds = HydrogenBondAnalysis(
    universe=u,
    donors_sel='name H',
    hydrogens_sel='name H',
    acceptors_sel='name O',
    d_h_cutoff=3.0,
    d_a_cutoff=3.5,
    angle_cutoff=120
)

# Run analysis
hbonds.run()
```

## Bundled Script Examples

### Generic hydrogen-bond analysis package

```bash
python -m scripts.hb_distribution_analysis \
  --topology topol.tpr \
  --trajectory traj.xtc \
  --config scripts/hb_distribution_analysis/system.yaml \
  --last-frames 100
```

### Residue RDF export for all residue-type pairs

```bash
python scripts/Plot_RDF/residue_rdf_all_pairs.py \
  --structure topol.tpr \
  --trajectory traj.xtc \
  --output rdf_all_pairs.csv \
  --resnames SOL NA CL
```

### Z-resolved orientation profile for water-like molecules

```bash
python scripts/plot_orientation/water_orientation_z_analysis.py \
  --structure topol.tpr \
  --trajectory traj.trr \
  --water-resname SOL \
  --oxygen-selection "name OW" \
  --hydrogen-selection "name HW1 HW2" \
  --output-prefix sol_orientation
```

## Parallel Analysis

```python
from MDAnalysis.analysis import pca

# Use multiple cores
pca_analysis = pca.PCA(u, select='protein', n_components=10)
pca_analysis.run(n_jobs=4)  # Use 4 cores
```

## Custom Analysis Class

```python
import MDAnalysis
from MDAnalysis.analysis.base import AnalysisBase

class CustomAnalysis(AnalysisBase):
    def __init__(self, universe, **kwargs):
        super().__init__(universe, **kwargs)
        # Initialize your analysis
        
    def _prepare(self):
        # Setup before running
        pass
        
    def _single_frame(self):
        # Process each frame
        pass
        
    def _conclude(self):
        # Finalize results
        pass

# Run custom analysis
analysis = CustomAnalysis(u)
analysis.run()
```

## Distance Library Functions

```python
from MDAnalysis.lib.distances import capped_distance, calc_angles, calc_dihedrals
import numpy as np

# Efficient neighbor search with cutoff (avoids computing full distance matrix)
pairs, distances = capped_distance(
    group1.positions, group2.positions,
    max_cutoff=5.0, box=u.dimensions
)

# Calculate angles from coordinate arrays (B is the vertex)
angles_rad = calc_angles(
    atom_A.positions, atom_B.positions, atom_C.positions,
    box=u.dimensions
)
angles_deg = np.degrees(angles_rad)

# Calculate dihedral angles
dihedrals = calc_dihedrals(
    atom_A.positions, atom_B.positions,
    atom_C.positions, atom_D.positions,
    box=u.dimensions
)

# Coordination number using capped_distance + bincount
def count_cn(center, neighbors, cutoff, box=None):
    pairs, _ = capped_distance(center, neighbors, max_cutoff=cutoff, box=box)
    return np.bincount(pairs[:, 0], minlength=len(center))
```

## LAMMPS and XYZ Format Loading

```python
import MDAnalysis as mda

# Load LAMMPS DUMP file
u = mda.Universe('dump.lammpstrj', topology_format='LAMMPSDUMP')
# Set masses for atom types (LAMMPS DUMP may not include mass info)
u.select_atoms('type 1').masses = 114.0
u.select_atoms('type 2').masses = 35.5

# Load XYZ file (no topology info, no box dimensions)
u = mda.Universe('coords.xyz')
# Manually set box dimensions (required for PBC-aware calculations)
u.dimensions = [50.0, 50.0, 50.0, 90.0, 90.0, 90.0]
# Set timestep (XYZ files don't contain timing info)
u.trajectory.ts.dt = 0.0005  # in ps
```

## Memory Optimization

```python
# Process in chunks - every 10th frame
for ts in u.trajectory[::10]:
    # Analysis code
    pass
```
