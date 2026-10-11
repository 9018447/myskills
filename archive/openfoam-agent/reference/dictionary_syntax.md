# OpenFOAM dictionary syntax and common IO errors

## Facts to confirm before debugging

- Dictionary parsing is strict: missing `;`, unbalanced brackets, or misspelled keywords often fail fast with `FOAM FATAL IO ERROR`.
- Many “case does not run” issues come from dictionary syntax problems in `system/*` or `0/*`, or from patch name mismatches.

## Minimal syntax rules (must know)

- Statements must end with `;`
- Blocks use `{ ... }`
- Lists use `( ... )`
- Strings usually do not require quotes (use quotes only if needed)
- `#include` / `#includeIfPresent` allow reuse

### Common data types

- **Scalar**: `1e-5;`
- **Vector**: `(1 0 0);`
- **Boolean**: `true;` / `false;`
- **Uniform field**:

```text
internalField   uniform (0 0 0);
```

- **Nonuniform list** (common for spatial boundary distributions):

```text
value nonuniform List<scalar>
3
(
  0
  1
  2
);
```

### Dimensions (dimensionSet)

Many properties/fields include dimensions:

```text
nu      [0 2 -1 0 0 0 0] 1e-05;
```

Dimension mismatches can trigger runtime errors or produce non-physical results.

## Most common `FOAM FATAL IO ERROR` cases

### 1) `Expected a ';'` / `Unexpected token`

- **Root cause**: missing semicolon, bracket mismatch, copy/paste artifacts
- **Fix**: inspect ~20 lines around the reported location for `;`, `{}`, and `()` balance

### 2) `keyword ... is undefined in dictionary` / `cannot find entry`

- **Root cause**: missing required entry (often `application`, `startFrom`, `deltaT`, `solvers`)
- **Fix**: compare with a similar tutorial case and restore required keys

### 3) `Cannot find patchField entry for ...`

- **Root cause**: a patch is missing from a field file (e.g. `0/U`, `0/p`), or patch names differ from the mesh
- **Fix**:
  - read patch list from `constant/polyMesh/boundary`
  - ensure every `0/*` has `boundaryField` entries for the same patch set

### 4) `Unknown patchField type ...`

- **Root cause**: misspelled patch field type, or type not valid for the solver/physics
- **Fix**: revert to a conservative, known-good combination (`fixedValue` / `zeroGradient` / `noSlip`) and iterate

## Minimal runnable snippets (templates)

### `system/controlDict` (minimal skeleton)

```text
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application     simpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1000;

deltaT          1;
writeControl    timeStep;
writeInterval   100;

purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;

timeFormat      general;
timePrecision   6;

runTimeModifiable true;
```

### `0/U` (typical baseline)

```text
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            noSlip;
    }
}
```
