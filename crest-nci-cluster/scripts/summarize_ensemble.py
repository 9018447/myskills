#!/usr/bin/env python3
"""Summarize a CREST ensemble XYZ (crest_conformers.xyz / crest_rotamers.xyz).

Reads a multi-structure XYZ whose comment line carries the energy in Hartree
(CREST convention), ranks structures by energy, prints relative energies in
kcal/mol and Boltzmann populations at the requested temperature. When the
comment line also carries CREST's own population fraction (crest_rotamers.xyz
convention), that value is printed alongside the recomputed one.

Usage:
  summarize_ensemble.py crest_conformers.xyz [--temp 298.15] [--top 20]
                          [--ewin 6.0] [--json]
"""
import argparse
import json
import math
import os
import sys

EH_TO_KCAL = 627.5094740631
KB_KCAL = 0.00198720425864083  # Boltzmann constant in kcal/(mol*K)


def floats_in(line):
    """Extract all numeric tokens from a string (handles D exponents too)."""
    out = []
    token = ""
    for ch in line.strip().replace("D", "E").replace("d", "e"):
        if ch.isdigit() or ch in "+-.eE":
            token += ch
        elif token:
            try:
                out.append(float(token))
            except ValueError:
                pass
            token = ""
    if token:
        try:
            out.append(float(token))
        except ValueError:
            pass
    return out


def read_ensemble(path):
    """Parse a multi-structure XYZ.

    Comment line convention (CREST 3):
      crest_conformers.xyz -> "<energy Eh>"
      crest_rotamers.xyz   -> "<energy Eh>  <Boltzmann fraction>  !"
    """
    structures = []
    skipped = 0
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    i = 0
    idx = 0
    while i < len(lines):
        header = lines[i].strip()
        if not header:
            i += 1
            continue
        try:
            nat = int(header)
        except ValueError:
            skipped += 1
            i += 1
            continue
        if i + 1 >= len(lines):
            break
        fields = floats_in(lines[i + 1])
        if not fields:
            skipped += 1
            i += nat + 2
            continue
        idx += 1
        s = {"index": idx, "energy": fields[0], "crest_pop": None}
        # A second field in (0, 1] is CREST's own Boltzmann population fraction.
        if len(fields) >= 2 and 0.0 < fields[1] <= 1.0000001:
            s["crest_pop"] = 100.0 * fields[1]
        structures.append(s)
        i += nat + 2
    return structures, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ensemble", help="multi-structure XYZ from CREST")
    ap.add_argument("--temp", type=float, default=298.15,
                    help="temperature in K for Boltzmann weights (default: 298.15)")
    ap.add_argument("--top", type=int, default=0,
                    help="print only the N lowest structures (default: all)")
    ap.add_argument("--ewin", type=float, default=None,
                    help="ignore structures more than N kcal/mol above the minimum")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    if not os.path.isfile(args.ensemble):
        sys.exit(f"error: file not found: {args.ensemble}")

    structures, skipped = read_ensemble(args.ensemble)
    if not structures:
        sys.exit("error: no structures with parseable energies found in " + args.ensemble)

    structures.sort(key=lambda s: s["energy"])
    e_min = structures[0]["energy"]
    for s in structures:
        s["de_kcal"] = (s["energy"] - e_min) * EH_TO_KCAL

    windowed = structures
    if args.ewin is not None:
        windowed = [s for s in structures if s["de_kcal"] <= args.ewin]

    weights = [math.exp(-s["de_kcal"] / (KB_KCAL * args.temp)) for s in windowed]
    wsum = sum(weights)
    for s, w in zip(windowed, weights):
        s["pop"] = 100.0 * w / wsum

    shown = windowed[: args.top] if args.top else windowed
    has_crest_pop = any(s["crest_pop"] is not None for s in structures)

    if args.json:
        print(json.dumps({
            "file": args.ensemble,
            "temperature_K": args.temp,
            "n_parsed": len(structures),
            "n_in_window": len(windowed),
            "skipped": skipped,
            "e_min_hartree": e_min,
            "note": ("crest_population_pct is CREST's own value read from the file; "
                     "boltzmann_population_pct is recomputed here at the given T"
                     if has_crest_pop else
                     "file carries no populations; boltzmann_population_pct assumes "
                     "equal degeneracy per entry"),
            "structures": [{
                "rank": r + 1, "index": s["index"],
                "energy_hartree": s["energy"],
                "de_kcal_mol": round(s["de_kcal"], 4),
                "boltzmann_population_pct": round(s["pop"], 3),
                **({"crest_population_pct": round(s["crest_pop"], 3)}
                   if s["crest_pop"] is not None else {}),
            } for r, s in enumerate(shown)],
        }, indent=2, ensure_ascii=False))
        return

    print(f"file: {args.ensemble}   T = {args.temp:g} K")
    print(f"structures parsed: {len(structures)}"
          + (f", within {args.ewin:g} kcal/mol window: {len(windowed)}"
             if args.ewin is not None else "")
          + (f", skipped (no energy): {skipped}" if skipped else ""))
    print(f"lowest energy: {e_min:.8f} Eh")
    if has_crest_pop:
        print("note: crest/% is CREST's population from the file (rotamer level);")
        print("      calc/% is recomputed Boltzmann weight at the given T.")
        print(f"{'rank':>4} {'#':>5} {'E/Eh':>15} {'dE/(kcal/mol)':>14} "
              f"{'crest/%':>9} {'calc/%':>8}")
        for r, s in enumerate(shown):
            cp = f"{s['crest_pop']:>9.3f}" if s["crest_pop"] is not None else f"{'-':>9}"
            print(f"{r + 1:>4} {s['index']:>5} {s['energy']:>15.8f} "
                  f"{s['de_kcal']:>14.4f} {cp} {s['pop']:>8.3f}")
    else:
        print("note: file has no population field; weights assume equal degeneracy "
              "per entry.")
        print("      CREST's conformer populations are degeneracy-averaged over "
              "member rotamers;")
        print("      for official populations use crest_rotamers.xyz or the run "
              "log summary.")
        print(f"{'rank':>4} {'#':>5} {'E/Eh':>15} {'dE/(kcal/mol)':>14} "
              f"{'pop/%':>8} {'cumul/%':>8}")
        cumul = 0.0
        for r, s in enumerate(shown):
            cumul += s["pop"]
            print(f"{r + 1:>4} {s['index']:>5} {s['energy']:>15.8f} "
                  f"{s['de_kcal']:>14.4f} {s['pop']:>8.3f} {cumul:>8.3f}")


if __name__ == "__main__":
    main()
