---
name: heat-capacity-ann
description: |
  Predict the heat capacity (Cp) of a pure compound using critical properties
  and the IK-CAPE feed-forward ANN model. Activate this skill whenever the user
  asks to predict heat capacity, calculate Cp, estimate molar heat capacity, or
  wants an ANN-based Cp prediction from critical properties or a SMILES string.
  Use it even if the user only mentions Cp, heat capacity, or ANN without
  explicitly naming this skill.
compatibility: |
  Requires Python 3. For SMILES inputs, the bundled group-contribution-estimator
  skill (and RDKit) must be available. For Excel output, pandas and openpyxl are
  required.
---

# Heat Capacity ANN Predictor

Use this skill to predict molar heat capacity `Cp` (J K⁻¹ mol⁻¹) with the
ANN model extracted from `回归IK-CAPE.xlsx`.

## When to use

- The user asks for a heat-capacity prediction from critical properties.
- The user gives a SMILES string or chemical name and wants Cp.
- The user mentions ANN, IK-CAPE, Cp, heat capacity, or molar heat capacity.
- The user wants a Cp vs. temperature table or plot.

## Model

- Inputs: `M` (g/mol), `Vc` (mL/mol), `Tc` (K), `Pc` (bar), `ω`, `T` (K).
- Architecture: 6 inputs → 8 tanh hidden nodes → 7 tanh hidden nodes →
  absolute-value output.
- Activation forms:
  - Hidden layers: `tanh(0.5 × (Σ w·x + b))`
  - Output: `abs(Σ w·x + b)`
- Parameters are bundled in `<skill-dir>/assets/ann_parameters_ik_cape.json`.

## Input

Accept either:

1. **Critical properties directly** as a JSON string or JSON file path containing
   `M`, `Vc`, `Tc`, `Pc`, `omega`.
2. **SMILES string**, e.g. `CCO`. Critical properties are estimated via the
   `group-contribution-estimator` skill before the ANN run.

Temperature can be:

- A single value: `300`
- A comma-separated list: `300,350,400`
- A range: `300:500:10` (start:end:step)

## Workflow

1. Locate the bundled script:
   `<skill-dir>/scripts/predict_cp.py`.
2. If the user provided a SMILES string, first use the
   `group-contribution-estimator` skill to obtain `M`, `Vc`, `Tc`, `Pc`, `ω`.
3. Run the prediction script:
   ```bash
   python <skill-dir>/scripts/predict_cp.py \
     --properties '{"M": 86.58, "Vc": 254.37, "Tc": 644.444, "Pc": 49.538, "omega": 0.6509}' \
     --temperature 300:500:20
   ```
   For a SMILES input:
   ```bash
   python <skill-dir>/scripts/predict_cp.py \
     --smiles "CCO" \
     --temperature 298.15
   ```
   For Excel output:
   ```bash
   python <skill-dir>/scripts/predict_cp.py \
     --properties props.json \
     --temperature 300:500:10 \
     --output excel --output-file cp_table.xlsx
   ```
4. Present the JSON or Excel result to the user. Include the critical properties
   used, the temperature(s), and the predicted Cp value(s).

## Output format

Default is JSON:

```json
{
  "model": "IK-CAPE ANN",
  "critical_properties": {
    "M": 86.58,
    "Vc": 254.37,
    "Tc": 644.444,
    "Pc": 49.538,
    "omega": 0.6509
  },
  "predictions": [
    {"T_K": 300.0, "Cp_J_K-1_mol-1": 145.32},
    {"T_K": 320.0, "Cp_J_K-1_mol-1": 148.91}
  ]
}
```

When `--output excel` is used, an `.xlsx` file with columns `T_K` and
`Cp_J_K-1_mol-1` is written.

## Limitations to communicate

- The ANN was trained and parameterized for the specific class of compounds in
  the IK-CAPE study. Extrapolation far outside the training domain may give
  unreliable results.
- Critical properties estimated from SMILES use the Lydersen-Joback-Reid method,
  which has its own approximations (see the group-contribution-estimator skill).
- The model predicts the molar heat capacity of a pure compound, not mixtures.

## Safety and assumptions

- Do not overwrite existing files unless the user asks.
- If dependencies are missing, tell the user how to install them rather than
  performing a system-wide install.
- Keep predictions deterministic: use only the bundled ANN weights and biases.
