# Solver log reading (find the root cause fast)

## Reading order (do this every time)

1. Find the **first** FATAL/ERROR block (do not start guessing from the last line)
2. Record:
   - solver name and OpenFOAM version
   - case path
   - current time step / iteration
   - whether the failure is in `read`, `mesh`, or `solve`
3. If there is no explicit FATAL but the run diverges or stalls, use the signals below

## Key signals and what they mean

### 1) Residuals

Typical output (simplified):

```text
smoothSolver:  Solving for Ux, Initial residual = 0.12, Final residual = 0.001, No Iterations 3
```

- **Initial residual**: normalized residual at the start of this linear solve
- **Final residual**: residual at the end of this linear solve
- **No Iterations**: linear solver iterations

Heuristics:

- iteration counts increasing step-by-step often indicates mesh quality, discretization, or relaxation issues
- residuals not decreasing (or oscillating) usually means BC consistency, relaxation, and/or time-step/CFL issues

### 2) Continuity errors

```text
time step continuity errors : sum local = 1e-05, global = -2e-08, cumulative = 0.01
```

- if **cumulative** grows monotonically, suspect unstable pressure-velocity coupling and/or mesh/BC problems

### 3) Courant number / Co (transient)

```text
Courant Number mean: 0.2 max: 3.5
```

- if max Co is too high, reduce `deltaT` or enable adaptive time stepping

### 4) Floating point exception (FPE)

Common root causes:

- non-physical initial/boundary values (negative turbulence quantities, invalid thermo state, etc.)
- bad cells (negative volume)
- overly aggressive time step or schemes

Fix priority: `checkMesh` first, then verify `0/*`, then tune numerics.

## Minimal intervention strategy for non-convergence/divergence

Change only one category at a time:

1. Mesh: remove fatal issues in `checkMesh`
2. Boundary conditions: revert to a conservative baseline (inlet fixedValue, outlet zeroGradient, walls noSlip)
3. Numerical stability:
   - steady: reduce relaxation factors (in `fvSolution`)
   - transient: reduce `deltaT`, control maxCo
4. Discretization: use bounded/limited convection schemes

## Minimal inputs to request from the user

- `system/controlDict`, `system/fvSchemes`, `system/fvSolution`
- `checkMesh` summary (at least max non-orthogonality / skewness / negative volume)
- the first `FOAM FATAL` block (or a continuous residual/continuity/Co excerpt)
