# Case layout

A standard OpenFOAM case is organized as:

- `0/`: fields and boundary conditions (e.g., `U`, `p`, `T`, `k`, `omega`)
- `constant/`: material models + mesh (`polyMesh/`) + turbulence
- `system/`: numerics and runtime controls
- `Allrun`, `Allclean`: reproducible scripts (recommended)

## Minimal expected files

- `system/controlDict`
- `system/fvSchemes`
- `system/fvSolution`

Plus one of:

- `constant/transportProperties` (many incompressible setups)
- `constant/thermophysicalProperties` (thermo/compressible)

## Patch naming invariant

Boundary patch names must be consistent across:

- `constant/polyMesh/boundary` (mesh)
- every field file under `0/` (boundaryField entries)

If patch names differ, the solver will fail early.
