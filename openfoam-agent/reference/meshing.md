# Meshing

## Choose a meshing path

- `blockMesh`: structured/simple parametric domains
- `snappyHexMesh`: STL surface-based mesh with refinement and snapping
- `gmshToFoam`: import Gmsh `.msh` (common for CAD-driven workflows)

## Checklist (before you mesh)

- Confirm the intended mesh generator (`blockMesh` / `snappyHexMesh` / `gmshToFoam`)
- Confirm case path has `system/` and `constant/`
- Confirm your target patch names (inlet/outlet/walls/etc.)
- Confirm 2D vs 3D (2D requires front/back `empty` patches)

## Always validate

Run:

- `checkMesh`

Treat mesh validation as a gate:

- Fix non-orthogonality / skewness / negative volumes before solver runs
- Confirm patch names and patch types

## Minimal command sequences

### `blockMesh`

Run in case root:

```bash
blockMesh
checkMesh
```

### `snappyHexMesh` (typical)

Run in case root:

```bash
blockMesh
surfaceFeatures
snappyHexMesh -overwrite
checkMesh
```

If you see `defaultFaces` in the mesh boundary list, your surfaces/regions are not assigned correctly.

### `gmshToFoam` (import)

Assuming `geometry.msh` is in case root:

```bash
gmshToFoam geometry.msh
checkMesh
```

Then confirm patches in `constant/polyMesh/boundary` match `0/*`.

## Reading `checkMesh` quickly

Prioritize these:

- Any mention of negative volumes or failed mesh checks
- Max non-orthogonality (very high values correlate with instability)
- Skewness hot spots

If `checkMesh` reports failures, fix mesh first before tuning numerics.

## Common failure modes

- Missing or unexpected patches (e.g. `defaultFaces` after `snappyHexMesh`)
- 2D cases not setting front/back to `empty`
- Excessive non-orthogonality causing divergence

## Practical defaults

- Start coarse, confirm physics and BCs, then refine
- Refine near walls and strong gradients (separation, jets, shocks, interfaces)
- For RANS wall functions: target y+ consistent with model choice (don’t mix)
