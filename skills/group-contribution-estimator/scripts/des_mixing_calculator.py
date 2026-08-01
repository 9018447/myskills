#!/usr/bin/env python3
"""DES critical-property estimator using Lee-Kesler mixing rules.

Takes two pure components (typically HBA and HBD) with their mole numbers and
critical properties, then computes the pseudo-critical properties of the
resulting Deep Eutectic Solvent (DES).
"""

import argparse
import json
import math
from pathlib import Path

R = 83.1447  # cm3·bar / (mol·K)


def compute_des_mixing(hba: dict, hbd: dict) -> dict:
    """Apply Lee-Kesler mixing rules for a two-component DES.

    Each component dict must contain: moles, MW, Tb, Tc, Pc, Vc, omega.
    Returns mole fractions, cross parameters, and DES properties.
    """
    n1, n2 = hba["moles"], hbd["moles"]
    y1 = n1 / (n1 + n2)
    y2 = n2 / (n1 + n2)

    tc1, vc1 = hba["Tc"], hba["Vc"]
    tc2, vc2 = hbd["Tc"], hbd["Vc"]
    omega1, omega2 = hba["omega"], hbd["omega"]
    mw1, mw2 = hba["MW"], hbd["MW"]
    tb1, tb2 = hba["Tb"], hbd["Tb"]

    tcij = math.sqrt(tc1 * tc2)
    vcij = (1 / 8) * (vc1 ** (1 / 3) + vc2 ** (1 / 3)) ** 3

    vc_d = y1 ** 2 * vc1 + y2 ** 2 * vc2 + 2 * y1 * y2 * vcij
    tc_d = (1 / vc_d ** 0.25) * (
        y1 ** 2 * vc1 ** 0.25 * tc1
        + y2 ** 2 * vc2 ** 0.25 * tc2
        + 2 * y1 * y2 * vcij ** 0.25 * tcij
    )
    omega_d = y1 * omega1 + y2 * omega2
    pc_d = (0.2905 - 0.085 * omega_d) * R * tc_d / vc_d
    zc = pc_d * vc_d / (tc_d * R)
    tb = y1 * tb1 + y2 * tb2
    mw = y1 * mw1 + y2 * mw2

    return {
        "components": {
            "HBA": {k: v for k, v in hba.items()},
            "HBD": {k: v for k, v in hbd.items()},
        },
        "mole_fractions": {"Y1_HBA": round(y1, 6), "Y2_HBD": round(y2, 6)},
        "cross_parameters": {
            "Tcij_K": round(tcij, 6),
            "Vcij_cm3_mol": round(vcij, 6),
        },
        "properties": {
            "molecular_weight_g_mol": round(mw, 6),
            "normal_boiling_point_K": round(tb, 3),
            "critical_temperature_K": round(tc_d, 6),
            "critical_volume_cm3_mol": round(vc_d, 6),
            "critical_pressure_bar": round(pc_d, 6),
            "acentric_factor": round(omega_d, 6),
            "critical_compressibility_factor": round(zc, 6),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Estimate DES critical properties by Lee-Kesler mixing rules."
    )
    parser.add_argument(
        "input",
        help="JSON file with keys 'HBA' and 'HBD', each containing "
             "moles, MW, Tb, Tc, Pc, Vc, omega",
    )
    parser.add_argument("-o", "--output", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = compute_des_mixing(data["HBA"], data["HBD"])

    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    main()
