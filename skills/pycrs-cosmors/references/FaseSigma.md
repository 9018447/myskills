---
title: "FastSigma"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/FastSigma.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## FastSigma

This submodule provides an interface to the FastSigma program.

pyCRS.FastSigma.estimate(*molecule: [pyCRS\_internal.Molecule](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS_internal.Molecule")*, *method: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'COSMO-RS'*, *model: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'FS1'*, *display: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*) → [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") [¶](FaseSigma.md#pyCRS.FastSigma.estimate)

Uses the FastSigma program to estimate a sigma profile. The results are written to the pyCRS.Molecule object provided to the function.

Parameters:

- **molecule** ([`pyCRS.Molecule`](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS.Molecule")) – the molecule to estimate
- **method** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – the COSMO-RS/-SAC method to use. Available options are (COSMO-RS,COSMOSAC2013,COSMOSAC2016). Not every method is available for every model.
- **model** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – the estimation technique for the sigma profile. Available options are (FS1, SG1). FS1 is a QSPR approach and SG1 uses a database of sigma profiles and matches the query molecule’s substructures against substructures in that database.
- **display** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – whether to display the results to standard out

Example

```python
import pyCRS
mol = pyCRS.Input.read_smiles("c1ccccc1(OCC)")
pyCRS.FastSigma.estimate(mol, method='COSMO-RS', model='SG1', display=True)
```

```
sigma value       Total profile          HB profile
            ...                 ...                  ...
            -0.002              10.689               0.000
            -0.001               9.453               0.000
             0.000               9.216               0.000
             0.001              10.264               0.000
             0.002              12.356               0.000
             0.003              12.007               0.000
             0.004              13.050               0.000
             0.005              11.818               0.000
             0.006               7.250               0.000
             0.007               2.643               0.000
             0.008               1.218               0.101
             0.009               1.131               0.890
             0.010               1.248               1.185
             0.011               1.209               1.181
             0.012               1.251               1.239
             0.013               1.233               1.228
             0.014               0.422               0.420
             0.015               0.025               0.024
            ...                  ...                 ...
       Molecular Mass =       122.0731649400 g/mol
           COSMO Area =       174.8609437511 Angstrom**2
         COSMO Volume =       165.2344104876 Angstrom**3
Gas Phase Bond Energy =        -4.1647328138 Hartree
          Bond Energy =        -4.1720958091 Hartree
           ...                  ...
```