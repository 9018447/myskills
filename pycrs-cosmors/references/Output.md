---
title: "Output"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/Output.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Output

This submodule provides functions to write output in kf format.

pyCRS.Output.write\_kf(*molecule: [pyCRS\_internal.Molecule](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS_internal.Molecule")*, *filename: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) → [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") [¶](Output.md#pyCRS.Output.write_kf)

writes a molecule to a kf file with the name <filename>. The saved file can then be used directly with AMS COSMO-RS/-SAC.

Parameters:

- **molecule** ([`pyCRS.Molecule`](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS.Molecule")) – the molecule to write to kf
- **filename** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – the filename for the output file. If the filename does not end with `.compkf`, then this extension is appended

Example

```python
import pyCRS
mol = pyCRS.Input.read_smiles("c1ccccc1(OCC)")
pyCRS.FastSigma.estimate(mol)
pyCRS.Output.write_kf(mol,"example.compkf")
```