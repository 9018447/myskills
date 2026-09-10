#!/usr/bin/env python3
"""Group-contribution estimator for critical properties (Tb, Tc, Pc, Vc).

Uses the Lydersen-Joback-Reid parameters embedded in this script and
RDKit SMARTS matching to decompose a molecule into functional groups.
"""

import argparse
import json
import math
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
except ImportError as exc:
    raise SystemExit("RDKit is required. Install it first: pip install rdkit") from exc


# ---------------------------------------------------------------------------
# Group contribution database
#
# SMARTS patterns match ONLY the atoms that belong to the group.
# Larger fragments are placed first so their atoms are claimed before
# smaller fragments try to claim overlapping atoms.
# ---------------------------------------------------------------------------
GROUP_DB = {
    "source": "Lydersen-Joback-Reid group contributions from DES_properties.xlsx",
    "units": {
        "delta_Tb": "K",
        "delta_Tc": "K",
        "delta_P": "bar",
        "delta_V": "cm3/mol"
    },
    "groups": [
        # -- Without Rings: larger fragments first --
        {"name": "-COOH",       "category": "Without Rings", "smarts": "[CX3](=O)[OX2H1]",            "delta_Tb": 169.06, "delta_Tc": 0.0853, "delta_P": 0.4537, "delta_V": 88.6},
        {"name": "-COO-",       "category": "Without Rings", "smarts": "[CX3](=O)[OX2H0]",            "delta_Tb": 81.1,  "delta_Tc": 0.0377, "delta_P": 0.4139, "delta_V": 84.76},
        {"name": "HCOO-",       "category": "Without Rings", "smarts": "[OX2H0][CH]=O",               "delta_Tb": 169.06, "delta_Tc": 0.036,  "delta_P": 0.4752, "delta_V": 97.77},
        {"name": "-CHO",        "category": "Without Rings", "smarts": "[CH]=O",                      "delta_Tb": 72.24, "delta_Tc": 0.0294, "delta_P": 0.3128, "delta_V": 77.46},
        {"name": ">C=O",        "category": "Without Rings", "smarts": "[CX3;!R](=O)[#6]",            "delta_Tb": 94.97, "delta_Tc": 0.0247, "delta_P": 0.2341, "delta_V": 69.76},
        {"name": "-NO2",        "category": "Without Rings", "smarts": "[N+](=O)[O-]",                "delta_Tb": 152.54,"delta_Tc": 0.0448, "delta_P": 0.4529, "delta_V": 123.62},
        {"name": "-CN",         "category": "Without Rings", "smarts": "C#N",                         "delta_Tb": 125.66,"delta_Tc": 0.0506, "delta_P": 0.3697, "delta_V": 89.32},
        {"name": "-SO2",        "category": "Without Rings", "smarts": "[SX4](=O)(=O)",               "delta_Tb": 147.24,"delta_Tc": -0.0563,"delta_P": -0.0606,"delta_V": 112.19},
        {"name": "-NH3",        "category": "Without Rings", "smarts": "[NH3+]",                      "delta_Tb": 73.23, "delta_Tc": 0.0364, "delta_P": 0.1692, "delta_V": 49.1},
        {"name": "-NH2",        "category": "Without Rings", "smarts": "[NH2;!R]",                    "delta_Tb": 73.23, "delta_Tc": 0.0364, "delta_P": 0.1692, "delta_V": 49.1},
        {"name": ">NH",         "category": "Without Rings", "smarts": "[NH;!R]",                     "delta_Tb": 50.17, "delta_Tc": 0.0119, "delta_P": 0.0322, "delta_V": 78.96},
        {"name": ">N-",         "category": "Without Rings", "smarts": "[N;!R]",                      "delta_Tb": 11.74, "delta_Tc": -0.0028,"delta_P": 0.0304, "delta_V": 26.7},
        {"name": "-N=",         "category": "Without Rings", "smarts": "[N;!R]=[#6]",                 "delta_Tb": 74.6,  "delta_Tc": 0.0172, "delta_P": 0.1541, "delta_V": 45.54},
        {"name": "-OH(alcohol)","category": "Without Rings", "smarts": "[OH;!$(Oa)]",                 "delta_Tb": 92.88, "delta_Tc": 0.0723, "delta_P": 0.1343, "delta_V": 30.4},
        {"name": "-O-",         "category": "Without Rings", "smarts": "[OX2;!R]",                    "delta_Tb": 22.42, "delta_Tc": 0.0051, "delta_P": 0.13,   "delta_V": 15.61},
        {"name": "=O(others)",  "category": "Without Rings", "smarts": "[*]=[O;X1]",                  "delta_Tb": -10.5, "delta_Tc": 0.0273, "delta_P": 0.2042, "delta_V": 44.03},
        {"name": "=C=",         "category": "Without Rings", "smarts": "[*]=[C]=[*]",                 "delta_Tb": 26.15, "delta_Tc": -0.0029,"delta_P": 0.0934, "delta_V": 33.85},
        {"name": "≡C-",         "category": "Without Rings", "smarts": "[*]#[C]",                     "delta_Tb": 18.18, "delta_Tc": 0.0078, "delta_P": 0.1429, "delta_V": 43.97},
        {"name": "≡CH",         "category": "Without Rings", "smarts": "[*]#[CH]",                    "delta_Tb": 21.74, "delta_Tc": 0.0078, "delta_P": 0.1429, "delta_V": 43.97},
        {"name": "=C<",         "category": "Without Rings", "smarts": "[C;!R](=*)[*]",               "delta_Tb": 24.14, "delta_Tc": -0.0003,"delta_P": 0.0832, "delta_V": 34.9},
        {"name": "=CH-",        "category": "Without Rings", "smarts": "[CH;!R]=*",                   "delta_Tb": 18.25, "delta_Tc": 0.0182, "delta_P": 0.1866, "delta_V": 49.92},
        {"name": "=CH2",        "category": "Without Rings", "smarts": "[CH2;!R]=*",                  "delta_Tb": 24.96, "delta_Tc": 0.017,  "delta_P": 0.2493, "delta_V": 60.37},
        {"name": ">C<",         "category": "Without Rings", "smarts": "[C;!R;H0]([#6])[#6]",         "delta_Tb": 18.18, "delta_Tc": -0.0206,"delta_P": 0.0539, "delta_V": 21.78},
        {"name": ">CH-",        "category": "Without Rings", "smarts": "[CH;!R]",                     "delta_Tb": 21.74, "delta_Tc": 0.0002, "delta_P": 0.114,  "delta_V": 45.7},
        {"name": "-CH2-",       "category": "Without Rings", "smarts": "[CH2;!R]",                    "delta_Tb": 22.88, "delta_Tc": 0.0159, "delta_P": 0.2165, "delta_V": 57.11},
        {"name": "-CH3",        "category": "Without Rings", "smarts": "[CH3;!R]",                    "delta_Tb": 23.58, "delta_Tc": 0.0275, "delta_P": 0.3031, "delta_V": 66.81},
        {"name": "-F",          "category": "Without Rings", "smarts": "F",                           "delta_Tb": -0.03, "delta_Tc": 0.0228, "delta_P": 0.2912, "delta_V": 31.47},
        {"name": "-Cl",         "category": "Without Rings", "smarts": "Cl",                          "delta_Tb": 38.13, "delta_Tc": 0.0188, "delta_P": 0.3738, "delta_V": 62.08},
        {"name": "-Br",         "category": "Without Rings", "smarts": "Br",                          "delta_Tb": 66.86, "delta_Tc": 0.0124, "delta_P": 0.5799, "delta_V": 76.6},
        {"name": "-I",          "category": "Without Rings", "smarts": "I",                           "delta_Tb": 93.84, "delta_Tc": 0.0148, "delta_P": 0.9174, "delta_V": 100.79},
        {"name": "-P",          "category": "Without Rings", "smarts": "[P]",                         "delta_Tb": 34.86, "delta_Tc": -0.0084,"delta_P": 0.1776, "delta_V": 67.01},
        {"name": "-S-",         "category": "Without Rings", "smarts": "[S;!R]",                      "delta_Tb": 117.52,"delta_Tc": 0.0006, "delta_P": 0.6901, "delta_V": 184.67},
        {"name": "-Al",         "category": "Without Rings", "smarts": "[Al]",                        "delta_Tb": 22.55, "delta_Tc": -0.0316,"delta_P": -0.363, "delta_V": 96.92},
        {"name": "-Cu",         "category": "Without Rings", "smarts": "[Cu]",                        "delta_Tb": -49.02,"delta_Tc": -0.1518,"delta_P": -0.3342,"delta_V": 126.2},
        {"name": "-Zn",         "category": "Without Rings", "smarts": "[Zn]",                        "delta_Tb": 227.14,"delta_Tc": -0.0877,"delta_P": -1.0705,"delta_V": 150.35},

        # -- With Rings --
        {"name": ">C=O(ring)", "category": "With Rings",    "smarts": "[CX3;R](=O)[#6]",            "delta_Tb": 94.97, "delta_Tc": 0.0343, "delta_P": 0.2751, "delta_V": 59.32},
        {"name": "-OH(phenol)", "category": "With Rings",    "smarts": "[OH;$(Oa)]",                  "delta_Tb": 76.34, "delta_Tc": 0.0291, "delta_P": 0.0493, "delta_V": -17.44},
        {"name": ">NH(ring)",  "category": "With Rings",    "smarts": "[NH;R]",                      "delta_Tb": 52.82, "delta_Tc": 0.0244, "delta_P": 0.0724, "delta_V": 27.61},
        {"name": ">N-(ring)",  "category": "With Rings",    "smarts": "[N;R]",                       "delta_Tb": None, "delta_Tc": 0.0063, "delta_P": 0.0538, "delta_V": 25.17},
        {"name": "-N=(ring)",  "category": "With Rings",    "smarts": "[N;R]=[#6]",                  "delta_Tb": 57.55, "delta_Tc": -0.0011,"delta_P": 0.0559, "delta_V": 42.15},
        {"name": "=C<(ring)",  "category": "With Rings",    "smarts": "[C;R](=*)[*]",                "delta_Tb": 31.01, "delta_Tc": 0.0051, "delta_P": 0.0955, "delta_V": 31.28},
        {"name": "=CH-(ring)", "category": "With Rings",    "smarts": "[CH;R]=*",                    "delta_Tb": 26.73, "delta_Tc": 0.0114, "delta_P": 0.1693, "delta_V": 42.55},
        {"name": ">C<(ring)",  "category": "With Rings",    "smarts": "[C;R;H0]([#6])[#6]",          "delta_Tb": 21.32, "delta_Tc": -0.018, "delta_P": 0.0139, "delta_V": 17.62},
        {"name": ">CH-(ring)", "category": "With Rings",    "smarts": "[CH;R]",                      "delta_Tb": 21.78, "delta_Tc": 0.0081, "delta_P": 0.1773, "delta_V": 30.56},
        {"name": "-CH2-(ring)","category": "With Rings",    "smarts": "[CH2;R]",                     "delta_Tb": 27.15, "delta_Tc": 0.0116, "delta_P": 0.1982, "delta_V": 51.64},
        {"name": "-O-(ring)",  "category": "With Rings",    "smarts": "[OX2;R]",                     "delta_Tb": 31.22, "delta_Tc": 0.0138, "delta_P": 0.1371, "delta_V": 17.41},

        # -- Aromatic fallback (treat aromatic atoms as their ring analogues) --
        {"name": "aromatic CH -> =CH-(ring)",  "category": "Aromatic fallback", "smarts": "[cH]",  "delta_Tb": 26.73, "delta_Tc": 0.0114, "delta_P": 0.1693, "delta_V": 42.55},
        {"name": "aromatic C -> =C<(ring)",   "category": "Aromatic fallback", "smarts": "[cH0]", "delta_Tb": 31.01, "delta_Tc": 0.0051, "delta_P": 0.0955, "delta_V": 31.28},
        {"name": "aromatic NH -> >NH(ring)",  "category": "Aromatic fallback", "smarts": "[nH]",  "delta_Tb": 52.82, "delta_Tc": 0.0244, "delta_P": 0.0724, "delta_V": 27.61},
        {"name": "aromatic N -> -N=(ring)",   "category": "Aromatic fallback", "smarts": "[nH0]", "delta_Tb": 57.55, "delta_Tc": -0.0011,"delta_P": 0.0559, "delta_V": 42.15},

        # -- Other Groups --
        {"name": "-B",          "category": "Other Groups",  "smarts": "[B]",                         "delta_Tb": -24.56,"delta_Tc": 0.0352, "delta_P": 0.0348, "delta_V": 22.45},
    ]
}


def load_molecule(input_str: str):
    """Load from SMILES or a file path (.mol/.sdf)."""
    p = Path(input_str)
    if p.is_file():
        if input_str.lower().endswith('.mol'):
            mol = Chem.MolFromMolFile(str(p))
        elif input_str.lower().endswith('.sdf'):
            suppl = Chem.SDMolSupplier(str(p))
            mol = next(suppl)
        else:
            mol = Chem.MolFromSmiles(input_str)
    else:
        mol = Chem.MolFromSmiles(input_str)
    if mol is None:
        raise ValueError(f"Could not parse molecule: {input_str!r}")
    return mol


def match_groups(mol):
    """Return list of matched groups with counts and atom indices."""
    matched_atoms = set()
    results = []

    for grp in GROUP_DB["groups"]:
        patt = Chem.MolFromSmarts(grp["smarts"])
        if patt is None:
            continue
        matches = mol.GetSubstructMatches(patt, uniquify=True, useChirality=False)
        kept = []
        for match in matches:
            if not any(a in matched_atoms for a in match):
                kept.append(match)
                matched_atoms.update(match)
        if kept:
            results.append({
                "name": grp["name"],
                "category": grp["category"],
                "count": len(kept),
                "delta_Tb": grp["delta_Tb"],
                "delta_Tc": grp["delta_Tc"],
                "delta_P": grp["delta_P"],
                "delta_V": grp["delta_V"],
                "atom_indices": [list(m) for m in kept],
            })
    return results


def estimate_properties(groups, mol):
    """Apply Lydersen-Joback-Reid equations."""
    sum_Tb = sum(g["count"] * (g["delta_Tb"] or 0) for g in groups)
    sum_Tc = sum(g["count"] * (g["delta_Tc"] or 0) for g in groups)
    sum_Pc = sum(g["count"] * (g["delta_P"] or 0) for g in groups)
    sum_Vc = sum(g["count"] * (g["delta_V"] or 0) for g in groups)

    mw = Descriptors.MolWt(mol)
    Tb = 198.2 + sum_Tb
    Tc = Tb / (0.5703 + 1.0121 * sum_Tc - sum_Tc ** 2)
    Pc = mw / ((0.2573 + sum_Pc) ** 2)
    Vc = 6.75 + sum_Vc

    # Acentric factor from the Valderrama/Lee-Kesler-type correlation
    # (matches the omega calculation in DES_properties.xlsx)
    Pb = 1.01325  # 1 atm in bar
    log_pc_pb = math.log10(Pc / Pb)
    term1 = ((Tb - 43) * (Tc - 43)) / ((Tc - Tb) * (0.7 * Tc - 43)) * log_pc_pb
    term2 = (Tc - 43) / (Tc - Tb) * log_pc_pb
    omega = term1 - term2 + log_pc_pb - 1

    return {
        "molecular_weight_g_mol": round(mw, 3),
        "normal_boiling_point_K": round(Tb, 3),
        "critical_temperature_K": round(Tc, 3),
        "critical_pressure_bar": round(Pc, 3),
        "critical_volume_cm3_mol": round(Vc, 3),
        "acentric_factor": round(omega, 4),
        "sums": {
            "delta_Tb": round(sum_Tb, 4),
            "delta_Tc": round(sum_Tc, 4),
            "delta_P": round(sum_Pc, 4),
            "delta_V": round(sum_Vc, 4),
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Estimate critical properties by group contribution.")
    parser.add_argument("input", help="SMILES string or path to .mol/.sdf file")
    parser.add_argument("-o", "--output", help="Output JSON file path (default: stdout)")
    parser.add_argument("--unmatched", action="store_true", help="Report unmatched atoms")
    args = parser.parse_args()

    mol = load_molecule(args.input)
    groups = match_groups(mol)
    props = estimate_properties(groups, mol)

    report = {
        "input": args.input,
        "smiles": Chem.MolToSmiles(mol),
        "properties": props,
        "groups": groups,
    }

    if args.unmatched:
        matched = {a for g in groups for m in g["atom_indices"] for a in m}
        report["unmatched_atoms"] = [i for i in range(mol.GetNumAtoms()) if i not in matched]
        report["num_atoms"] = mol.GetNumAtoms()
        report["num_matched_atoms"] = len(matched)

    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    main()
