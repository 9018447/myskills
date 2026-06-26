---
name: openfoam-agent
description: OpenFOAM CFD workflow playbook for AI coding assistants. Use to plan and implement OpenFOAM cases, choose solvers, generate/validate meshes, run/debug simulations, and standardize post-processing.
argument-hint: "[task] [case_path(optional)]"
license: Complete terms in LICENSE.txt
---

# OpenFOAM Agent Skill

This skill is an AI-facing OpenFOAM manual.

When invoked, follow the workflow below.

## 0) First clarify (don’t guess)

Ask for the minimum set of facts required to avoid non-physical or unstable setups:

- Physics: incompressible/compressible, single/multiphase, heat transfer/CHT, reacting?
- Regime: laminar/RANS/LES, steady/transient
- Geometry & scale: key dimensions, 2D vs 3D assumption
- Fluid properties: ρ, ν (or μ), cp, k, etc.
- Boundary conditions: inlets/outlets/walls/symmetry, turbulence quantities if RANS
- Outputs: forces, pressure drop, temperature, y+, probes
- Resources: target runtime, cores, memory

If any item is unknown, propose 1-3 concrete options and request confirmation.

## 1) Use standard case structure

Enforce the canonical OpenFOAM layout:

- `0/`: initial conditions and boundary fields
- `constant/`: mesh and physical properties
- `system/`: numerics and runtime controls
- `Allrun` / `Allclean`: reproducible run scripts (recommended)

Detailed reference: [reference/case_layout.md](reference/case_layout.md)

Boundary condition baselines: [reference/boundary_conditions.md](reference/boundary_conditions.md)

## 2) Mesh workflow (always validate)

- Pick the path:
  - `blockMesh` (structured / simple)
  - `snappyHexMesh` (STL-based)
  - `gmshToFoam` (Gmsh `.msh`)
- Always run `checkMesh` and address quality issues before solver runs.
- Ensure boundary patch names match what `0/` expects.

Detailed reference: [reference/meshing.md](reference/meshing.md)

## 3) Solver & turbulence selection (engineering defaults)

- Prefer the simplest solver that matches physics.
- For RANS, default to k-omega SST unless there’s a reason not to.
- Target version is ESI/OpenCFD OpenFOAM v2412. Ensure run commands match the installed environment.

Detailed reference: [reference/solver_selection.md](reference/solver_selection.md)

Numerics templates: [reference/fv_solution_patterns.md](reference/fv_solution_patterns.md)

## 4) Run, monitor, and iterate

- Start with conservative numerics (time step / relaxation) and then tighten.
- Track:
  - residual trends
  - continuity errors
  - CFL / Co number (transient)
  - forces / Δp stabilization
- Prefer small, explainable changes per iteration.

Debug playbook: [reference/troubleshooting.md](reference/troubleshooting.md)

Parallel workflow: [reference/parallel_run.md](reference/parallel_run.md)

## 5) Post-processing as first-class output

- Use `functionObjects` / `postProcess` for repeatable outputs.
- Output concise, decision-oriented summaries (e.g., drag coefficient, Δp, max T, y+ stats).

Cheatsheet: [reference/command_cheatsheet.md](reference/command_cheatsheet.md)

## 6) Repository-local helper scripts

- `scripts/case_audit.py`: static audit of a case directory (structure + presence of key dictionaries)
- `scripts/skill_quality_check.py`: validate skill docs (broken links + length limits)

## Additional resources

- [reference/windows_wsl.md](reference/windows_wsl.md)
- [reference/version_notes_v2412.md](reference/version_notes_v2412.md)
- [reference/dictionary_syntax.md](reference/dictionary_syntax.md)
- [reference/solver_log_reading.md](reference/solver_log_reading.md)
- [reference/openfoam_cpp_dev.md](reference/openfoam_cpp_dev.md)
- [reference/boundary_conditions.md](reference/boundary_conditions.md)
- [reference/fv_solution_patterns.md](reference/fv_solution_patterns.md)
- [reference/parallel_run.md](reference/parallel_run.md)
- [reference/quality_and_maintenance.md](reference/quality_and_maintenance.md)
