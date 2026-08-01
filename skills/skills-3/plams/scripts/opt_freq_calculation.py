#!/usr/bin/env amspython
"""Optimize molecular structure and calculate vibrational frequencies using ADF/B3LYP/TZ2P.

Usage:
    amspython L-Proline_opt_freq.py [xyz_file]

Default xyz_file: L-Proline.xyz

Requirements:
    - AMS2023+ with ADF license
    - PLAMS Python library
"""

import scm.plams as plams
from scm.plams import Molecule, Settings, AMSJob
import sys

def main():
    plams.init()

    # Get XYZ file from command line argument or use default
    xyz_file = sys.argv[1] if len(sys.argv) > 1 else "L-Proline.xyz"

    # Read the molecule from XYZ file
    mol = Molecule(xyz_file)
    print(f"Loaded molecule with {len(mol)} atoms from {xyz_file}")

    # Geometry Optimization + Frequency Calculation (one step)
    settings = Settings()
    settings.input.ams.Task = "GeometryOptimization"
    settings.input.ams.Properties.NormalModes = "Yes"
    settings.input.ADF.Basis.Type = "TZ2P"
    settings.input.ADF.XC.Hybrid = "B3LYP"
    settings.input.ADF.NumericalQuality = "Good"
    settings.input.ADF.SYMMETRY = "NoSym"

    name = xyz_file.replace(".xyz", "").replace("/", "_")
    job = AMSJob(molecule=mol, settings=settings, name=f"{name}_opt_freq")
    results = job.run()

    if job.status != "successful":
        print(f"Job failed: {job.status}")
        plams.finish()
        exit(1)

    opt_mol = results.get_main_molecule()
    energy = results.get_energy(unit="kcal/mol")
    print(f"Optimization completed. Energy: {energy:.4f} kcal/mol")

    # Get frequencies
    frequencies = results.get_frequencies(unit="cm^-1")
    print(f"\nVibrational frequencies (cm^-1):")
    print(frequencies)

    # Check for imaginary frequencies
    imag_freqs = [f for f in frequencies if f < 0]
    if imag_freqs:
        print(f"\nWARNING: Found {len(imag_freqs)} imaginary frequency(s)")
    else:
        print("\nNo imaginary frequencies found - structure is a true minimum")

    # Save optimized geometry
    output_xyz = xyz_file.replace(".xyz", "_optimized.xyz")
    opt_mol.write(output_xyz)
    print(f"\nOptimized geometry saved to {output_xyz}")

    plams.finish()
    print("Done!")

if __name__ == "__main__":
    main()
