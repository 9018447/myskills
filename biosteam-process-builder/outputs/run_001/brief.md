# DES Dehydration-Regeneration Base Template — Results

**DES**: choline chloride / glycerol (1:2.0)

**Gas feed**: 1000.0 kmol/hr CO2/H2O, 95.0% CO2 / 5.0% H2O, 40.0 C, 10.0 bar

**Total DES flow**: 500.0 kmol/hr, makeup fraction = 0.05, fresh makeup = 25.0 kmol/hr

**Column**: 3 equilibrium stages (rigorous COSMOSAC)

**Flash**: 100.0 C, 0.50 bar

## Key metrics

- Dry CO2 flow: 953.09 kmol/hr
- Dry CO2 water mole fraction: 0.003391
- Water removed: 46.77 kmol/hr (93.54%)
- CO2 loss to DES: 0.14 kmol/hr (0.02%)
- Rich DES flow: 948.87 kmol/hr
- Regenerated DES flow: 923.11 kmol/hr
- Regenerated DES water mole fraction: 0.457030
- Recycle DES flow: 876.96 kmol/hr
- Recycle DES water mole fraction: 0.457030
- Flash water recovery: 5.74%
- Recycle convergence iterations: 0
- Dry-CO2 target: No target specified.
- Regeneration target: Target not met (0.457030 > 0.020000); no adjustment enabled.
- Generated script: /home/smh/biosteam/.claude/skills/biosteam-process-builder/outputs/run_001/process.py

## Stream summary

### Dry CO2

```
[949.856   3.232   0.   ]
```

### Mixer outlet (to absorber)

```
[  1.163 400.791 500.   ]
```

### Rich DES (to flash)

```
[  1.307 447.559 500.   ]
```

### Flash vapor

```
[8.488e-02 2.567e+01 2.905e-16]
```

### Regenerated DES (before split)

```
[  1.222 421.89  500.   ]
```

### Recycle DES (to mixer)

```
[  1.161 400.796 475.   ]
```

### Purge DES (product)

```
[ 0.061 21.095 25.   ]
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
