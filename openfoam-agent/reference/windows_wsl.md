# Windows / WSL notes
 
## Recommended setup
 
- Use WSL2 with a Linux OpenFOAM install for most workflows.
- Keep case directories inside the Linux filesystem (not on `/mnt/c`) for performance.

## Target version

This repository targets **ESI/OpenCFD OpenFOAM v2412**.

## Environment self-check (copy/paste)

Run these in the same shell you will use to run OpenFOAM:

```bash
echo "$WM_PROJECT_DIR"
echo "$WM_PROJECT_VERSION"
which blockMesh || true
which checkMesh || true
which simpleFoam || true
foamVersion || true
```

If `foamVersion` is not available, use whatever your installation provides to report version.
 
## Path pitfalls
 
- OpenFOAM tools assume POSIX paths.
- Avoid spaces in case paths.

## Filesystem pitfalls (WSL)

- Prefer working under your Linux home (e.g. `~/cases/...`) rather than `/mnt/c/...`.
- If you must use `/mnt/c`, expect slower IO and occasional permission quirks.
 
## What to ask the user to confirm
 
- OpenFOAM version and how it is sourced
- Whether they run in WSL2, Docker, or native Linux
- Whether `blockMesh`, `checkMesh`, and the target solver are on PATH
