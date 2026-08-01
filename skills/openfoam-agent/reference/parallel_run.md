# Parallel run

Purpose: provide a safe, repeatable parallel workflow for OpenFOAM cases.

Target version: **ESI/OpenCFD OpenFOAM v2412**.

## Checklist (before parallel)

- Confirm the case runs in serial first.
- Confirm `system/decomposeParDict` exists and matches mesh topology.
- Confirm patch names are consistent across mesh and `0/*`.
- Confirm `Allrun` uses `-parallel` and reconstruction steps.

## Minimal command sequence

Run in case root:

```bash
decomposePar
mpirun -np 4 simpleFoam -parallel
reconstructPar
```

If `foamRun` is preferred in your environment, use:

```bash
mpirun -np 4 foamRun -solver incompressibleFluid -parallel
```

## `system/decomposeParDict` baseline

```foam
numberOfSubdomains 4;

method scotch;

distributed no;

roots
(
);
```

## Common failure modes and fixes

- `Cannot find patchField entry` after decompose -> fix patch names in `0/*`.
- Missing processor directories -> `decomposePar` failed; check dictionary syntax.
- `inconsistent times` -> remove partial time directories and rerun.
- Slow scaling -> reduce `nNonOrthogonalCorrectors` or simplify mesh.

## Reconstruction tips

- Prefer `reconstructPar` after a successful run.
- For large cases, reconstruct only latest time with `-latestTime`.

## Related references

- [troubleshooting.md](troubleshooting.md)
- [case_layout.md](case_layout.md)
- [command_cheatsheet.md](command_cheatsheet.md)
