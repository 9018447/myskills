---
name: group-contribution-estimator
description: |
  Estimate critical properties (Tb, Tc, Pc, Vc) of ordinary molecules using the
  Lydersen-Joback-Reid group-contribution method. Activate this skill whenever
  the user asks to partition a molecule into functional groups, calculate
  critical properties from group contributions, estimate Tb/Tc/Pc/Vc from a
  SMILES or molecular structure file, or wants a group-contribution report for
  a molecule.
compatibility: |
  Requires RDKit (`pip install rdkit`). Accepts SMILES strings or `.mol`/`.sdf`
  file paths. Output is JSON or YAML.
---

# Group Contribution Critical-Property Estimator

Use this skill to decompose a molecule into functional groups and estimate its
normal boiling point (Tb), critical temperature (Tc), critical pressure (Pc),
and critical volume (Vc) with the Lydersen-Joback-Reid method.

## When to use

- A user gives a SMILES string or molecule file and asks for critical properties.
- A user wants to see which functional groups a molecule contains.
- A user wants a group-contribution weighted calculation.
- A user mentions Tb, Tc, Pc, Vc, Joback, Lydersen, Reid, or group contribution.

## Input

Accept either:

1. A SMILES string, e.g. `CCO`, `C1CCCCC1`, `[Zn](Cl)Cl`.
2. A path to a `.mol` or `.sdf` file.

If the input is ambiguous, ask the user to clarify or assume SMILES if it does
not look like a file path.

## Workflow

1. **Locate the bundled script**: it lives at
   `<skill-dir>/scripts/joback_calculator.py`.
2. **Run the script** with the user's input:
   ```bash
   python <skill-dir>/scripts/joback_calculator.py "<SMILES>" --unmatched
   ```
   For a file:
   ```bash
   python <skill-dir>/scripts/joback_calculator.py /path/to/molecule.mol --unmatched
   ```
3. **Capture the JSON output** and present it to the user.
4. **Warn about unmatched atoms**: if `unmatched_atoms` is non-empty, explain
   that those atoms were not covered by the group-contribution parameter set.
   Common cases: aromatic carbons, heteroaromatic rings, and some metal centers
   not listed in the source table.
5. **Optional: convert to YAML** if the user prefers YAML over JSON.

## Output format

Return a concise report. Use JSON by default; produce YAML only if the user
explicitly asks for it. The report should include:

- Input SMILES/string
- Molecular weight
- Estimated Tb, Tc, Pc, Vc with units
- Acentric factor ω (estimated from Tb/Tc/Pc via the Valderrama correlation)
- The matched groups, their counts, and their contributions
- Any unmatched atoms (with a brief explanation)

Example:

```json
{
  "input": "CCO",
  "smiles": "CCO",
  "properties": {
    "molecular_weight_g_mol": 46.069,
    "normal_boiling_point_K": 337.54,
    "critical_temperature_K": 500.791,
    "critical_pressure_bar": 55.486,
    "critical_volume_cm3_mol": 161.07,
    "acentric_factor": 0.4152
  },
  "groups": [
    {"name": "-OH(alcohol)", "category": "Without Rings", "count": 1},
    {"name": "-CH2-",        "category": "Without Rings", "count": 1},
    {"name": "-CH3",         "category": "Without Rings", "count": 1}
  ],
  "unmatched_atoms": []
}
```

## Limitations to communicate

- The parameter set is the 49-group table from `DES_properties.xlsx`. Aromatic
  atoms are treated as their aliphatic-ring analogues (e.g., aromatic CH uses
  the `=CH-(ring)` contribution), which is an approximation. Results for
  aromatic/heteroaromatic molecules should be interpreted as estimates.
- The method is an estimation; results can deviate significantly from
  experimental data, especially for complex or multifunctional molecules.
- Heavy atoms not in the table (e.g., some transition metals, Si, B in exotic
  environments) may be unmatched.

## Safety and assumptions

- Do not overwrite existing files unless the user asks.
- If RDKit is missing, tell the user to install it rather than attempting an
  automated system-wide install.
- Keep the output deterministic: do not invent new group-contribution
  parameters; use only the values embedded in the bundled script.
