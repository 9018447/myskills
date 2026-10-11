# Version notes (ESI/OpenCFD OpenFOAM v2412)

This repository targets **ESI/OpenCFD OpenFOAM v2412**.

The goal is to provide guidance that works reliably in v2412, while remaining explicit about places where packaging and environment can differ.

## What to do when commands differ

When documentation mentions a tool or solver command, always verify what exists in your shell:

```bash
echo "$WM_PROJECT_VERSION"
which blockMesh || true
which checkMesh || true
which simpleFoam || true
which pimpleFoam || true
foamVersion || true
```

If a command is not found:

- Prefer the installed equivalent (as reported by your OpenFOAM environment)
- Fall back to running the solver executable directly (when available)
- Avoid guessing a command name based on another distribution

## Documentation style rule

- Docs should describe the intent (e.g., "run the steady incompressible RANS solver")
- Then give one or two command patterns, clearly labeled as environment-dependent

## Where to keep v2412-specific differences

- Keep generic workflow in `SKILL.md`
- Put v2412-specific notes in this file and link to it from `SKILL.md`
