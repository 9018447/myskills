# Troubleshooting

This is a decision-oriented playbook. Always classify the failure first, then apply the smallest change that can validate the hypothesis.

Target version: **ESI/OpenCFD OpenFOAM v2412**.

## 0) Classify the failure (pick one)

- **A. Dictionary / IO parse error**: `FOAM FATAL IO ERROR`
- **B. Patch mismatch**: `Cannot find patchField entry` / missing patch in `0/*`
- **C. Mesh invalid**: `checkMesh` failures / negative volume / severe quality
- **D. Divergence / blow-up**: residuals explode, continuity cumulative grows rapidly
- **E. Floating point exception**: `SIGFPE` / `floating point exception`
- **F. Parallel issues**: decompose/reconstruct errors, inconsistent times

If you cannot classify, request the first `FOAM FATAL` block (or a continuous excerpt of residuals + continuity + Co).

## First pass triage

- Confirm case structure: `0/`, `constant/`, `system/`
- Confirm mesh: `checkMesh` passes (or at least no fatal issues)
- Confirm patch names match across mesh and `0/`

Recommended one-liners:

```bash
python skills/openfoam-agent/scripts/case_audit.py /path/to/case
```

## A) `FOAM FATAL IO ERROR` (parse / missing entry)

- Root causes:
  - missing `;`, mismatched `{}`/`()`
  - missing required keyword in a dictionary
- Fix path:
  - go to [dictionary_syntax.md](dictionary_syntax.md)
  - compare the failing file against a similar tutorial

## B) Patch mismatch (`Cannot find patchField entry`)

- Root causes:
  - patch exists in mesh but missing in `0/*`
  - patch spelling differs between mesh and fields
- Fix path:
  - treat `constant/polyMesh/boundary` as the source of truth
  - ensure every relevant `0/<field>` contains `boundaryField` entries for all mesh patches

Minimal verification:

```bash
python skills/openfoam-agent/scripts/case_audit.py /path/to/case --json
```

## C) Mesh invalid (`checkMesh` failures)

- Fix mesh first. Do not tune numerics to compensate for negative volumes.
- Re-run: `checkMesh` after every meshing change.

## D) Divergence / blow-up (no single FATAL, but unstable)

Apply fixes in this order (one category at a time):

1. Mesh quality (especially non-orthogonality / skewness hot spots)
2. Boundary condition consistency (use conservative baselines)
3. Numerical stability:
   - steady: reduce relaxation factors (in `fvSolution`)
   - transient: reduce `deltaT`, control maxCo (if applicable)
4. Discretization: use bounded/limited schemes for convection

## E) Floating point exception (FPE)

- Root causes:
  - non-physical initial fields (e.g. negative turbulence quantities)
  - invalid thermo setup (for thermo cases)
  - mesh issues that survived initial checks
- Fix path:
  - `checkMesh` first
  - validate `0/*` initial/boundary values
  - then reduce time step / relax numerics

## Divergence / blowing up

- Reduce time step (transient) or tighten relaxation (steady)
- Check BCs for consistency (e.g. inlet/outlet combinations)
- Inspect mesh quality hot spots (high skewness, non-orthogonality)

## Non-convergence / oscillating residuals

- Switch numerics to more robust schemes (bounded, limited)
- Adjust under-relaxation / PIMPLE controls
- Check turbulence initialization and inlet turbulence quantities

## Common OpenFOAM-specific issues

- "Cannot find patchField entry" → patch name mismatch
- `FOAM FATAL IO ERROR` in dictionaries → syntax / missing keyword
- `floating point exception` early → invalid field values or mesh issues

## Minimal debugging output to request

- `system/controlDict`, `fvSchemes`, `fvSolution`
- `checkMesh` summary
- solver log header + first fatal error block

See also: [solver_log_reading.md](solver_log_reading.md)
