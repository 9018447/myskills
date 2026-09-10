# Command cheatsheet

## Mesh

- `blockMesh`
- `snappyHexMesh -overwrite`
- `gmshToFoam geometry.msh`
- `checkMesh`

## Run

- `simpleFoam` / `pimpleFoam` (depends on version)
- `foamRun -solver <solverName>` (available in some distributions; verify in your v2412 environment)

## Environment / version

- `foamVersion` (if available)
- `echo $WM_PROJECT_VERSION`

## Parallel

- `decomposePar`
- `mpirun -np <N> <solver> -parallel`
- `reconstructPar`

## Post-processing

- `paraFoam`
- `postProcess -func <name>`

## Housekeeping

- `foamCleanTutorials` (tutorial cleanup)
- `rm -rf [time directories]` (manual cleanup; use with care)
