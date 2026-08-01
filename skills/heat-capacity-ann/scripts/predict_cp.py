#!/usr/bin/env python3
"""Predict heat capacity (Cp) with the IK-CAPE ANN model."""

import argparse
import json
import math
import os
import subprocess
import sys


def load_ann_params():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    params_path = os.path.join(skill_dir, "assets", "ann_parameters_ik_cape.json")
    with open(params_path, encoding="utf-8") as f:
        return json.load(f)


def predict_single(inputs, params):
    """Return Cp in J K-1 mol-1 for one set of inputs."""
    h1 = {}
    for node, data in params["layer1"].items():
        s = data["bias"] + sum(data["weights"][k] * inputs[k] for k in data["weights"])
        h1[node] = math.tanh(0.5 * s)

    h2 = {}
    for node, data in params["layer2"].items():
        s = data["bias"] + sum(data["weights"][k] * h1[k] for k in data["weights"])
        h2[node] = math.tanh(0.5 * s)

    out = params["output"]
    s = out["bias"] + sum(out["weights"][k] * h2[k] for k in out["weights"])
    return abs(s)


def parse_temperatures(value):
    """Accept a single value, comma list, or start:end:step range."""
    value = str(value).strip()
    if ":" in value:
        parts = [p.strip() for p in value.split(":")]
        if len(parts) != 3:
            raise ValueError("range must be start:end:step")
        start, end, step = (float(p) for p in parts)
        if step <= 0:
            raise ValueError("step must be positive")
        result = []
        current = start
        while current <= end + 1e-9:
            result.append(current)
            current += step
        return result
    parts = [p.strip() for p in value.split(",")]
    nums = [float(p) for p in parts]
    return nums


def get_properties_from_smiles(smiles):
    """Estimate critical properties via the bundled group-contribution skill."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    joback_script = os.path.join(
        this_dir, "..", "..", "group-contribution-estimator", "scripts", "joback_calculator.py"
    )
    if not os.path.exists(joback_script):
        raise FileNotFoundError(
            f"Group-contribution estimator not found at {joback_script}. "
            "Provide critical properties directly with --properties."
        )
    result = subprocess.run(
        [sys.executable, joback_script, smiles, "--unmatched"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    props = data.get("properties", {})
    return {
        "M": props["molecular_weight_g_mol"],
        "Vc": props["critical_volume_cm3_mol"],
        "Tc": props["critical_temperature_K"],
        "Pc": props["critical_pressure_bar"],
        "omega": props["acentric_factor"],
    }


def parse_properties(value):
    """Parse a JSON string or JSON file path into a property dict."""
    if os.path.exists(value):
        with open(value, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.loads(value)

    if "properties" in data:
        data = data["properties"]

    required = {"M", "Vc", "Tc", "Pc", "omega"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"missing critical properties: {missing}")
    return {k: float(data[k]) for k in required}


def main():
    parser = argparse.ArgumentParser(description="Predict Cp with the IK-CAPE ANN")
    parser.add_argument("--smiles", help="SMILES string; critical properties estimated via group contribution")
    parser.add_argument("--properties", help="JSON string or path with M, Vc, Tc, Pc, omega")
    parser.add_argument("--temperature", required=True, help="single T, comma-separated list, or start:end:step range")
    parser.add_argument("--output", choices=["json", "excel"], default="json")
    parser.add_argument("--output-file", help="path for Excel output")
    args = parser.parse_args()

    if not args.smiles and not args.properties:
        parser.error("provide either --smiles or --properties")

    params = load_ann_params()

    if args.smiles:
        base_props = get_properties_from_smiles(args.smiles)
    else:
        base_props = parse_properties(args.properties)

    temperatures = parse_temperatures(args.temperature)

    predictions = []
    for T in temperatures:
        inputs = {**base_props, "T": T}
        cp = predict_single(inputs, params)
        predictions.append({"T_K": T, "Cp_J_K-1_mol-1": cp})

    result = {
        "model": "IK-CAPE ANN",
        "critical_properties": base_props,
        "predictions": predictions,
    }
    if args.smiles:
        result["smiles"] = args.smiles

    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for Excel output: pip install pandas") from exc
        df = pd.DataFrame(predictions)
        out_path = args.output_file or "cp_predictions.xlsx"
        df.to_excel(out_path, index=False, sheet_name="Cp")
        print(json.dumps({"saved": out_path, **result}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
