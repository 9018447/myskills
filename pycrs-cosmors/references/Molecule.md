---
title: "Molecule"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Molecule

*class* pyCRS.Molecule [¶](Molecule.md##%20Molecule.md#pyCRS.Molecule)

This class stores inforation about a molecule and serves as the main interface for accessing estimated properties.

Attributes

| `area` | The COSMO surface area of the molecule |
| --- | --- |
| `bond_energy` | The Bond Energy (in Hartrees) for the molecule in the COSMO conductor phase. |
| `dispersion` | The dispersion energy |
| `formula` | The molecular formula |
| `gas_phase_bond_energy` | The Bond Energy (in Hartrees) for the molecule in the gas phase |
| `is_valid` | A bool that indicates whether the molecule is valid or if there were errors in processing it (e.g., invalid SMILESS) |
| `method` | The method (COSMO-RS, COSMO-SAC, etc.) for which the estimate is made. |
| `molar_mass` | The molar mass in g/mol |
| `nring` | The nring parameter used in COSMO-RS |
| `parameters` | A dictionary of parameters that can be used for certain models (e.g., vapor pressure model parameters) |
| `properties` | A dictionary of property values for temperature-independent properties |
| `properties_tdep` | A dictionary of (temperature,property) pairs for temperature-dependent properties |
| `smiles` | The SMILES string of a molecule, if available |
| `volume` | The COSMO volume of the molecule |

Methods

Returns a dictionary of sigma profiles values. For COSMO-RS, the dictionary has two entries (Total Profile and H-Bonding Profile). For COSMO-SAC, the dictionary has Total Profile, OH Profile, and OT Profile entries.

Example

```python
import pyCRS
mol = pyCRS.Input.read_smiles("CCCCCN")
pyCRS.FastSigma.estimate(mol, method='COSMO-RS', model = 'FS1', display=False)
for k,v in mol.get_sigma_profile().items():
    print(k, v)
```

```
H-Bonding Profile [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.051576871269907, 0.093772696234738, ... , 0.36159288378918, 0.14796979638662, 0.0]
Total Profile [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.051576871269907, 0.094440478268766, ... , 0.36159288378918, 0.147976661591423, 0.0]
```

get\_tdep\_values(*self:* , *arg0: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) → [tuple](https://docs.python.org/3.8/library/stdtypes.html#tuple "(in Python v3.8)") \[[list](https://docs.python.org/3.8/library/stdtypes.html#list "(in Python v3.8)") \[[float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")\], [list](https://docs.python.org/3.8/library/stdtypes.html#list "(in Python v3.8)") \[[float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")\]\] [¶](Molecule.md##%20Molecule.md#pyCRS.Molecule.get_tdep_values)

Returns a tuple of (temperatures, values) for a temperature-dependent property given as an argument to the function.

Example

```python
import pyCRS
mol = pyCRS.Input.read_smiles("OCCCCCC")
pyCRS.PropPred.estimate(mol, 'vaporpressure', temperatures=list(range(270,330,10)))
unit = pyCRS.PropPred.units['vaporpressure']
print( "Temperature (K)".rjust(15)+f'Vapor pressure ({unit})'.rjust(25) )
for temp, val in zip(*mol.get_tdep_values('vaporpressure')):
    print(f'{temp:>15.3f}{val:>25.3f}')
```

```
Temperature (K)     Vapor pressure (bar)
        270.000                    0.000
        280.000                    0.000
        290.000                    0.001
        300.000                    0.001
        310.000                    0.003
        320.000                    0.006
```

missing\_atoms(*self:* , *arg0: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) → [list](https://docs.python.org/3.8/library/stdtypes.html#list "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] [¶](Molecule.md##%20Molecule.md#pyCRS.Molecule.missing_atoms)

A list of atom symbols which could not be mapped to a descriptor