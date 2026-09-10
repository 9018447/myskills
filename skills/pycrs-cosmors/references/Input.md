---
title: "Input"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/Input.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Input

This submodule provides functions used to initialize a pyCRS.Molecule.

Input.read\_smiles(*smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) → [pyCRS\_internal.Molecule](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS_internal.Molecule") [¶](Input.md#pyCRS.Input.read_smiles)

Parameters:

**smiles** (`string`) – the SMILES string to be used

Example

```python
import pyCRS
mol = pyCRS.Input.read_smiles("c1ccccc1(OCC)")
mol = pyCRS.Input.read_smiles("c1cccccdfg1(OCC)")
print ("Check if the molecule is valid:", mol.is_valid)
```

Input.read\_sdf(*filename: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) → [pyCRS\_internal.Molecule](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS_internal.Molecule") [¶](Input.md#pyCRS.Input.read_sdf)

Parameters:

**filename** (`string`) – the.sdf file containing the input molecule

Example

```python
import pyCRS
mol = pyCRS.Input.read_sdf("molecule.sdf")
```