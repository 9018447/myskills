# Solver selection

## Decision points

- Compressible vs incompressible
- Steady vs transient
- Single-phase vs multiphase
- Isothermal vs heat transfer / CHT
- Turbulence model (laminar/RANS/LES)

## Practical decision tree

- If free surface/interface tracking is required:
  - Start from `interFoam`-family
- Else if incompressible:
  - Steady: `simpleFoam`
  - Transient: `pimpleFoam`
- Else (compressible/thermo):
  - Start from the compressible solver family in your installed version

If you are unsure, pick the simplest solver that matches the physics and confirm against a similar tutorial.

## Engineering defaults

- Incompressible, steady RANS: `simpleFoam`
- Incompressible, transient RANS: `pimpleFoam`
- VOF free-surface: `interFoam` (or a derived variant)

## Minimal run commands (examples)

These vary by OpenFOAM version and packaging.

```bash
# Common older style
simpleFoam

# Alternative style (depending on installation)
foamRun -solver incompressibleFluid
```

Always align run commands with what exists on PATH.

## Turbulence defaults

- If RANS and no strong reason: k-omega SST
- If fully laminar (low Re and expected): laminar model

### Minimal turbulence initialization (RANS)

If you use a RANS model, ensure `0/` contains the required fields for that model family (commonly `k`, `omega` or `epsilon`, and `nut`). Missing turbulence fields is a frequent early failure mode.

## Version note (ESI/OpenCFD v2412)

ESI/OpenCFD v2412 is the target for this repository. Commands can still vary by packaging and environment; always align run commands with what exists on PATH.
