# DES Dehydration-Regeneration Base Template — Results

**DES**: choline chloride / glycerol (1:2.0)

**Gas feed**: 1000.0 kmol/hr CO2/H2O, 95.0% CO2 / 5.0% H2O, 40.0 C, 10.0 bar

**Total DES flow**: 500.0 kmol/hr, makeup fraction = 0.05, fresh makeup = 25.0 kmol/hr

**Column**: 3 equilibrium stages (rigorous COSMOSAC)

**Flash**: 100.0 C, 0.50 bar

## Key metrics

- Dry CO2 flow: 953.25 kmol/hr
- Dry CO2 water mole fraction: 0.003546
- Water removed: 46.62 kmol/hr (93.24%)
- CO2 loss to DES: 0.13 kmol/hr (0.01%)
- Rich DES flow: 589.04 kmol/hr
- Regenerated DES flow: 544.52 kmol/hr
- Regenerated DES water mole fraction: 0.081536
- Recycle DES flow: 517.29 kmol/hr
- Recycle DES water mole fraction: 0.081536
- Flash water recovery: 50.00%
- Recycle convergence iterations: 0
- Dry-CO2 target: No target specified.
- Regeneration target: Target met (<= 1.000000).
- Generated script: /home/smh/biosteam/.claude/skills/biosteam-process-builder/outputs/test_audit_baseline/process.py

## Stream summary

### Dry CO2

```
[949.872   3.38    0.   ]
```

### Mixer outlet (to absorber)

```
[1.145e-01 4.218e+01 5.000e+02]
```

### Rich DES (to flash)

```
[2.422e-01 8.880e+01 5.000e+02]
```

### Flash vapor

```
[ 0.121 44.398  0.   ]
```

### Regenerated DES (before split)

```
[1.211e-01 4.440e+01 5.000e+02]
```

### Recycle DES (to mixer)

```
[1.150e-01 4.218e+01 4.750e+02]
```

### Purge DES (product)

```
[6.054e-03 2.220e+00 2.500e+01]
```

## Caveats

- V2 is rigorous-mode only; both absorber and flash use COSMOSAC2013 via Clapeyron.
- DES regeneration is modeled as a single isothermal flash; pumps, heat exchangers,
  compressors, and valves are not included.
- A splitter divides the regenerated flash liquid into a recycle stream and a purge
  stream equal to the fresh DES makeup, closing the solvent mass balance.
- Critical properties for the DES pseudo-component are estimates.
- Clapeyron falls back to BasicIdeal for the DES pure model because the
  estimated critical properties are outside the Peng-Robinson correlation range.
- CO2 liquid heat capacity is patched to use the gas Cp above the normal
  liquid range so the supercritical CO2 enthalpy model does not fail.
- Sequential modular convergence is used; other algorithms may not converge
  for this supercritical CO2 / heavy DES system.
