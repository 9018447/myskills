# fvSolution / fvSchemes patterns

Purpose: provide conservative, minimal templates for stable runs and debugging.

Target version: **ESI/OpenCFD OpenFOAM v2412**.

## Checklist (before tuning)

- Confirm solver matches physics (see [solver_selection.md](solver_selection.md)).
- Confirm mesh passes `checkMesh` without fatal issues.
- Start with conservative time step and relaxation, then tighten.
- Prefer bounded or limited convection schemes for stability.

## Pattern A: Incompressible steady RANS (simpleFoam baseline)

### `system/fvSolution`

```foam
solvers
{
    p
    {
        solver GAMG;
        tolerance 1e-7;
        relTol 0.1;
    }
    U
    {
        solver smoothSolver;
        smoother GaussSeidel;
        tolerance 1e-6;
        relTol 0.1;
    }
    "(k|omega|epsilon|nut)"
    {
        solver smoothSolver;
        smoother GaussSeidel;
        tolerance 1e-6;
        relTol 0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl
    {
        p 1e-3;
        U 1e-4;
        "(k|omega|epsilon)" 1e-4;
    }
}

relaxationFactors
{
    fields
    {
        p 0.3;
    }
    equations
    {
        U 0.7;
        "(k|omega|epsilon|nut)" 0.7;
    }
}
```

### `system/fvSchemes`

```foam
gradSchemes
{
    default Gauss linear;
}

divSchemes
{
    div(phi,U) bounded Gauss upwind;
    div(phi,k) bounded Gauss upwind;
    div(phi,omega) bounded Gauss upwind;
    div(phi,epsilon) bounded Gauss upwind;
}

laplacianSchemes
{
    default Gauss linear corrected;
}

interpolationSchemes
{
    default linear;
}
```

## Pattern B: Incompressible transient RANS (pimpleFoam baseline)

### `system/fvSolution`

```foam
solvers
{
    p
    {
        solver GAMG;
        tolerance 1e-7;
        relTol 0.1;
    }
    pFinal
    {
        $p;
        relTol 0;
    }
    U
    {
        solver smoothSolver;
        smoother GaussSeidel;
        tolerance 1e-6;
        relTol 0.1;
    }
    UFinal
    {
        $U;
        relTol 0;
    }
    "(k|omega|epsilon|nut)"
    {
        solver smoothSolver;
        smoother GaussSeidel;
        tolerance 1e-6;
        relTol 0.1;
    }
}

PIMPLE
{
    nOuterCorrectors 1;
    nCorrectors 2;
    nNonOrthogonalCorrectors 1;
}
```

### `system/fvSchemes`

```foam
ddtSchemes
{
    default backward;
}

divSchemes
{
    div(phi,U) bounded Gauss upwind;
    div(phi,k) bounded Gauss upwind;
    div(phi,omega) bounded Gauss upwind;
    div(phi,epsilon) bounded Gauss upwind;
}
```

## Common instability symptoms and fixes

- Residuals spike early -> reduce relaxation (steady) or `deltaT` (transient).
- Pressure oscillation -> increase non-orthogonal correctors or improve mesh.
- Turbulence fields diverge -> lower inlet turbulence or switch to bounded schemes.
- Slow convergence -> tighten tolerances after stability is reached.

## Related references

- [solver_selection.md](solver_selection.md)
- [troubleshooting.md](troubleshooting.md)
- [boundary_conditions.md](boundary_conditions.md)
