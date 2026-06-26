---
title: "PropPred"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/PropPred.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## PropPred

An interface to the PropPred program for the prediction of physical properties.

pyCRS.PropPred.units [¶](PropPred.md#pyCRS.PropPred.units)

a dictionary which maps property names to strings representing the units

pyCRS.PropPred.available\_properties [¶](PropPred.md#pyCRS.PropPred.available_properties)

a list of the property names available in PropPrediction

PropPred.estimate(*molecule: [pyCRS\_internal.Molecule](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS_internal.Molecule")*, *properties: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [list](https://docs.python.org/3.8/library/stdtypes.html#list "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] = 'all'*, *temperatures: [list](https://docs.python.org/3.8/library/stdtypes.html#list "(in Python v3.8)") \[[float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")\] = \[298.1499938964844\]*, *show\_errors: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*) → [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") [¶](PropPred.md#pyCRS.PropPred.estimate)

Estimates one or more properties with PropPrediction. The results are written to the pyCRS.Molecule object provided to the function.

Parameters:

- **molecule** ([`pyCRS.Molecule`](https://www.scm.com/doc/COSMO-RS/pyCRS/Molecule.html#pyCRS.Molecule "pyCRS.Molecule")) – A pyCRS.Molecule object
- **properties** (`str or list(str)`) – a string naming a property for calculating a single property value or a list of strings naming all the desired properties to calculate
- **temperatures** (`list(float)`) – a list of temperature values with which to calculate the temperature-dependent properties
- **show\_errors** ([`bool`](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)")) – indicate whether errors should be shown in std out

Example

```python
import pyCRS
mol = pyCRS.Input.read_smiles("c1ccccc1(OCC)")
# estimate all properties by default
pyCRS.PropPred.estimate(mol, temperatures=[290,295,300,305])

for prop, value in mol.properties.items():
    unit = pyCRS.PropPred.units[prop]
    print(f'{prop:<20s}: {value:.3f} {unit}')

for prop, value in mol.properties_tdep.items():
    print(f'{prop:<20s}:')
    unit = pyCRS.PropPred.units[prop]
    propunit = f'{prop} ({unit})'
    print("T (K)".rjust(30)+f'{propunit:>30s}')
    for t,v in value:
        print(f'{t:>30.3f}{v:>30.8g}')
```

```
boilingpoint        : 432.028 K
criticalpressure    : 34.205 bar
criticaltemp        : 569.012 K
criticalvol         : 0.376 L/mol
density             : 0.958 kg/L (298.15 K)
dielectricconstant  : -3.824
entropygas          : 366.424 J/(mol K)
flashpoint          : 319.734 K
gidealgas           : 29.448 kJ/mol
hcombust            : -4173.723 kJ/mol
hformstd            : -165.241 kJ/mol
hfusion             : 10.622 kJ/mol
hidealgas           : -115.682 kJ/mol
hsublimation        : 66.720 kJ/mol
meltingpoint        : 202.182 K
molarvol            : 0.127 L/mol
parachor            : 305.809
solubilityparam     : 9.356 √(cal/cm^3)
synacc              : 1.042
tpt                 : 201.439 K
vdwarea             : 161.566 Å²
vdwvol              : 122.256 Å³
liquidviscosity     :
                         T (K)        liquidviscosity (Pa-s)
                       290.000                  0.0014622948
                       295.000                  0.0013171559
                       300.000                  0.0011921719
                       305.000                  0.0010839762
vaporpressure       :
                         T (K)           vaporpressure (bar)
                       290.000                  0.0010699197
                       295.000                  0.0015221786
                       300.000                  0.0021369822
                       305.000                  0.0029624981
```