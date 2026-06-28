---
name: group-contribution-estimator
description: |
  Estimate critical properties (Tb, Tc, Pc, Vc) of ordinary molecules using the
  Lydersen-Joback-Reid group-contribution method, and estimate DES pseudo-critical
  properties from two pure components (HBA + HBD) using Lee-Kesler mixing rules.
  Activate this skill whenever the user asks to partition a molecule into functional
  groups, calculate critical properties from group contributions, estimate
  Tb/Tc/Pc/Vc from a SMILES or molecular structure file, wants a group-contribution
  report for a molecule, or asks to estimate DES critical properties from HBA/HBD
  mixing rules.
compatibility: |
  Requires RDKit (`pip install rdkit`) for the group-contribution script. The
  DES mixing-rules script is pure Python. Accepts SMILES strings, `.mol`/`.sdf`
  file paths, or JSON input files. Output is JSON or YAML.
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

## DES mixing rules (Lee–Kesler)

Use this skill to estimate the pseudo-critical properties of a Deep Eutectic
Solvent (DES) from two pure components, typically a Hydrogen Bond Acceptor
(HBA) and a Hydrogen Bond Donor (HBD). The method is taken from the
`混合规则` sheet of `DES_properties.xlsx`.

### When to use

- A user provides HBA + HBD critical properties and asks for DES critical
  properties.
- A user mentions DES, eutectic solvent, HBA/HBD mixing rules, or
  Lee–Kesler mixing rules.

### Input

Create a JSON file with `HBA` and `HBD` objects. Each object must contain:

| Field  | Description                  | Unit      |
|--------|------------------------------|-----------|
| `moles`| mole number of the component | mol       |
| `MW`   | molecular weight             | g/mol     |
| `Tb`   | normal boiling point         | K         |
| `Tc`   | critical temperature         | K         |
| `Pc`   | critical pressure            | bar       |
| `Vc`   | critical volume              | cm³/mol   |
| `omega`| acentric factor              | -         |

Example (`choline_urea.json`):

```json
{
  "HBA": {
    "name": "Choline",
    "moles": 1,
    "MW": 139.627,
    "Tb": 457.45,
    "Tc": 622.97,
    "Pc": 30.543,
    "Vc": 440.58,
    "omega": 0.761
  },
  "HBD": {
    "name": "urea",
    "moles": 2,
    "MW": 60.057,
    "Tb": 439.63,
    "Tc": 666.638,
    "Pc": 87.22,
    "Vc": 174.71,
    "omega": 0.5959
  }
}
```

### Workflow

1. **Locate the DES mixing-rules script**:
   `<skill-dir>/scripts/des_mixing_calculator.py`.
2. **Run the script** with the JSON input:
   ```bash
   python <skill-dir>/scripts/des_mixing_calculator.py choline_urea.json
   ```
3. **Capture the JSON output** and present it to the user.

### Mixing equations

Mole fractions:

$$Y_1 = \frac{n_1}{n_1 + n_2}, \quad Y_2 = \frac{n_2}{n_1 + n_2}$$

Cross parameters:

$$T_{c,ij} = \sqrt{T_{c,1} T_{c,2}}$$
$$V_{c,ij} = \frac{1}{8}\left(V_{c,1}^{1/3} + V_{c,2}^{1/3}\right)^3$$

DES pseudo-critical properties:

$$V_c^D = Y_1^2 V_{c,1} + Y_2^2 V_{c,2} + 2Y_1Y_2 V_{c,ij}$$

$$T_c^D = \frac{1}{(V_c^D)^{0.25}}\left[Y_1^2 V_{c,1}^{0.25}T_{c,1} + Y_2^2 V_{c,2}^{0.25}T_{c,2} + 2Y_1Y_2 V_{c,ij}^{0.25}T_{c,ij}\right]$$

$$\omega^D = Y_1\omega_1 + Y_2\omega_2$$

$$P_c^D = \frac{(0.2905 - 0.085\omega^D) \cdot 83.1447 \cdot T_c^D}{V_c^D}$$

$$Z_c = \frac{P_c^D V_c^D}{T_c^D \cdot 83.1447}$$

$$T_b = Y_1 T_{b,1} + Y_2 T_{b,2}$$

$$M = Y_1 M_1 + Y_2 M_2$$

### Output format

Return a JSON report. Example for Choline/urea (1:2):

```json
{
  "components": {
    "HBA": {"name": "Choline", "moles": 1, ...},
    "HBD": {"name": "urea", "moles": 2, ...}
  },
  "mole_fractions": {
    "Y1_HBA": 0.333333,
    "Y2_HBD": 0.666667
  },
  "cross_parameters": {
    "Tcij_K": 644.434228,
    "Vcij_cm3_mol": 287.469782
  },
  "properties": {
    "molecular_weight_g_mol": 86.580333,
    "normal_boiling_point_K": 445.57,
    "critical_temperature_K": 644.444426,
    "critical_volume_cm3_mol": 254.36657,
    "critical_pressure_bar": 49.538535,
    "acentric_factor": 0.650933,
    "critical_compressibility_factor": 0.235171
  }
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
- The DES mixing-rules model assumes a binary DES and uses the Lee–Kesler
  pseudo-critical mixing rules from `DES_properties.xlsx`. It is not a
  thermodynamic activity model and should be used only for initial property
  screening.

## Safety and assumptions

- Do not overwrite existing files unless the user asks.
- If RDKit is missing, tell the user to install it rather than attempting an
  automated system-wide install.
- Keep the output deterministic: do not invent new group-contribution
  parameters; use only the values embedded in the bundled script.
