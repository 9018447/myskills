# DES Dehydration-Regeneration Base Template — Results

**DES**: choline chloride / glycerol (1:2.0)

**Gas feed**: 1000.0 kmol/hr CO2/H2O, 95.0% CO2 / 5.0% H2O, 40.0 C, 10.0 bar

**Total DES flow**: 500.0 kmol/hr, makeup fraction = 0.05, fresh makeup = 25.0 kmol/hr

**Column**: 3 equilibrium stages (rigorous COSMOSAC)

**Flash**: 150.0 C, 0.50 bar

## Key metrics

- Dry CO2 flow: 955.69 kmol/hr
- Dry CO2 water mole fraction: 0.005998
- Water removed: 44.27 kmol/hr (88.54%)
- CO2 loss to DES: 0.04 kmol/hr (0.00%)
- Rich DES flow: 289.76 kmol/hr
- Regenerated DES flow: 230.04 kmol/hr
- Regenerated DES water mole fraction: 0.062781
- Recycle DES flow: 218.53 kmol/hr
- Recycle DES water mole fraction: 0.062781
- Flash water recovery: 75.15%
- Recycle convergence iterations: 0
- Dry-CO2 target: No target specified.
- Regeneration target: Target not met (0.062781 > 0.020000) within adjustment limits.
- Generated script: /home/smh/biosteam/.claude/skills/biosteam-process-builder/outputs/run_001_optimized/process.py

## Stream summary

### Dry CO2

```
[949.961   5.732   0.   ]
```

### Mixer outlet (to absorber)

```
[7.365e-02 1.384e+01 2.315e+02]
```

### Rich DES (to flash)

```
[1.128e-01 5.811e+01 2.315e+02]
```

### Flash vapor

```
[3.580e-02 4.367e+01 1.603e+01]
```

### Regenerated DES (before split)

```
[7.695e-02 1.444e+01 2.155e+02]
```

### Recycle DES (to mixer)

```
[7.311e-02 1.372e+01 2.047e+02]
```

### Purge DES (product)

```
[3.848e-03 7.221e-01 1.078e+01]
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
