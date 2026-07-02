# DES Dehydration-Regeneration Base Template — Results

**DES**: choline chloride / glycerol (1:2.0)

**Gas feed**: 1000.0 kmol/hr CO2/H2O, 95.0% CO2 / 5.0% H2O, 40.0 C, 40.0 bar

**Total DES flow**: 1000.0 kmol/hr, makeup fraction = 0.05, fresh makeup = 50.0 kmol/hr

**Column**: 7 equilibrium stages (rigorous COSMOSAC)

**Flash**: 200.0 C, 0.02 bar

## Key metrics

- Dry CO2 flow: 950.64 kmol/hr
- Dry CO2 water mole fraction: 0.000776
- Water removed: 49.26 kmol/hr (98.52%)
- CO2 loss to DES: 0.10 kmol/hr (0.01%)
- Rich DES flow: 1050.93 kmol/hr
- Regenerated DES flow: 1001.65 kmol/hr
- Regenerated DES water mole fraction: 0.000957
- Recycle DES flow: 951.57 kmol/hr
- Recycle DES water mole fraction: 0.000957
- Flash water recovery: 98.09%
- Recycle convergence iterations: 0
- Dry-CO2 target: No target specified.
- Regeneration target: Target met (<= 1.000000).
- Generated script: /home/smh/biosteam/.claude/skills/biosteam-process-builder/outputs/test_baseline/process.py

## Stream summary

### Dry CO2

```
[9.499e+02 7.381e-01 0.000e+00]
```

### Mixer outlet (to absorber)

```
[6.592e-01 9.105e-01 1.000e+03]
```

### Rich DES (to flash)

```
[7.552e-01 5.017e+01 1.000e+03]
```

### Flash vapor

```
[6.140e-02 4.921e+01 2.460e-14]
```

### Regenerated DES (before split)

```
[6.938e-01 9.584e-01 1.000e+03]
```

### Recycle DES (to mixer)

```
[6.591e-01 9.105e-01 9.500e+02]
```

### Purge DES (product)

```
[3.469e-02 4.792e-02 5.000e+01]
```

## Caveats

- V2 is rigorous-mode only; both absorber and flash use COSMOSAC2013 via Clapeyron.
- DES regeneration is modeled as a single isothermal flash; pumps, heat exchangers,
  compressors, and valves are not included.
- A splitter divides the regenerated flash liquid into a recycle stream and a purge
  stream equal to the fresh DES makeup, closing the solvent mass balance.
- Critical properties for the DES pseudo-component are estimates.
- DES is treated as non-volatile by supplying a constant, extremely low
  saturation pressure via the DIPPR101Sat pure-component model in Clapeyron;
  this enforces negligible DES volatility inside the flash equilibrium
  calculation rather than by post-processing the flash result.
- CO2 liquid heat capacity is patched to use the gas Cp above the normal
  liquid range so the supercritical CO2 enthalpy model does not fail.
- Sequential modular convergence is used; other algorithms may not converge
  for this supercritical CO2 / heavy DES system.
