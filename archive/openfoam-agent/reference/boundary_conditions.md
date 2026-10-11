# Boundary conditions

Purpose: provide baseline, conservative boundary-condition combinations for common OpenFOAM cases.

Target version: **ESI/OpenCFD OpenFOAM v2412**.

## Checklist (before running)

- Confirm all patches listed in `constant/polyMesh/boundary` appear in every `0/*` field.
- Confirm patch types match geometry intent: inlet/outlet/wall/symmetry/empty.
- Confirm turbulence model fields exist for RANS/LES (`k`, `omega` or `epsilon`, `nut`).
- For compressible/thermo cases, confirm temperature/enthalpy fields and thermo patches.
- Keep initial values conservative and physically consistent.

## Baseline combinations (incompressible internal flow)

Use these as a conservative starting point and adapt to physics.

### Velocity `U`

```foam
boundaryField
{
    inlet
    {
        type fixedValue;
        value uniform (1 0 0);
    }
    outlet
    {
        type zeroGradient;
    }
    walls
    {
        type noSlip;
    }
    symmetry
    {
        type symmetry;
    }
}
```

### Pressure `p`

```foam
boundaryField
{
    inlet
    {
        type zeroGradient;
    }
    outlet
    {
        type fixedValue;
        value uniform 0;
    }
    walls
    {
        type zeroGradient;
    }
    symmetry
    {
        type symmetry;
    }
}
```

### Turbulence (RANS example: `k`, `omega`, `nut`)

```foam
boundaryField
{
    inlet
    {
        type fixedValue;
        value uniform 0.1;
    }
    outlet
    {
        type zeroGradient;
    }
    walls
    {
        type kqRWallFunction;
        value uniform 0.0;
    }
}
```

## External flow baselines (far-field)

- Use `freestream`-type patches when available in your installation.
- If unavailable, model as inlet + outlet with sufficient distance from the body.
- Keep turbulence fields consistent with inlet turbulence intensity/length scale.

## Patch type rules of thumb

- `wall`: use `noSlip` for `U` and wall functions for turbulence fields.
- `symmetry`: use `symmetry` across all fields.
- `empty`: for 2D cases, ensure front/back patches are `empty` for all fields.
- `outlet`: use `zeroGradient` for `U` and fixed reference `p`.

## Common failure modes and fixes

- Missing patch entry in `0/*` -> add `boundaryField` entries for every patch.
- Backflow at outlet -> move outlet farther away or switch to more robust outlet BC.
- Turbulence blow-up -> reduce inlet turbulence or start from lower `k`/`omega`.
- 2D case behaving as 3D -> ensure `empty` patches for all fields.

## Related references

- [case_layout.md](case_layout.md)
- [solver_selection.md](solver_selection.md)
- [fv_solution_patterns.md](fv_solution_patterns.md)
