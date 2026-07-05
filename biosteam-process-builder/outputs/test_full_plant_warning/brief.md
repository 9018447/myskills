# DES Dehydration-Regeneration Full Plant — Results

**DES**: choline chloride / glycerol (1:2.0)

**Gas feed**: 1000.0 kmol/hr CO2/H2O, 95.0% CO2 / 5.0% H2O, 40.0 C, 1.00 bar

**Total DES flow**: 500.0 kmol/hr, makeup fraction = 0.05, fresh makeup = 25.0 kmol/hr

**Column**: 3 equilibrium stages (rigorous COSMOSAC) at 1.00 bar

**Flash**: 200.0 C, 0.050 bar

**Tear stream**: splitter recycle outlet → mixer (closes DES recycle loop)

## Extrapolation warnings

- ⚠️ Water.Cn.l.Tmax = 300.0 K (< 473 K); properties may be extrapolated above fitted range.

## Equipment table

| Unit | T_in (C) | T_out (C) | P_in (bar) | P_out (bar) | duty/power (kW) |
| --- | --- | --- | --- | --- | --- |
| Mixer | 25.00 | 25.00 | 1.000 | 1.000 | 0.000 |
| Absorber | 40.00 | 28.40 | 1.000 | 1.000 | 0.000 |
| Valve | 33.08 | 32.74 | 1.000 | 0.050 | 0.000 |
| HXprocess (rich/lean) | 32.74 | 194.91 | 0.050 | 0.050 | 6302.600 |
| Heater | 194.91 | 194.37 | 0.050 | 0.050 | 209.381 |
| Flash | 194.37 | 200.00 | 0.050 | 0.050 | 115.028 |
| Condenser | 200.00 | 30.00 | 0.050 | 0.050 | -155.020 |
| Pump | 37.74 | 37.74 | 0.050 | 1.000 | 2.042 |
| Cooler | 37.74 | 25.00 | 1.000 | 1.000 | -415.025 |
| Splitter | 25.00 | 25.00 | 1.000 | 1.000 | 0.000 |

## Mass metrics

- Dry CO2 flow: 988.25 kmol/hr
- Dry CO2 water mole fraction: 0.038707
- Water removed: 11.75 kmol/hr (23.50%)
- CO2 loss to DES: 0.00 kmol/hr (0.00%)
- Rich DES flow: 504.27 kmol/hr
- Regenerated DES flow: 492.94 kmol/hr
- Regenerated DES water mole fraction: 0.022961
- Recycle DES flow: 467.24 kmol/hr
- Recycle DES water mole fraction: 0.023242
- Flash water recovery: 50.00%
- Condensate flow: 11.30 kmol/hr
- Condensate water mole fraction: 0.999997
- CO2 vent flow: 0.02 kmol/hr
- Recycle convergence iterations: 12

## Energy metrics

- HX duty (heat recovery): 6302.600 kW
- Heater duty: 209.381 kW
- Cooler duty: 415.025 kW
- Condenser duty: 155.020 kW
- Pump power: 2.042 kW
- Heat recovery fraction: 0.968

## Target check (< 0.1 mol % water)

| Stream | Target | Actual | Pass | Gap |
| --- | --- | --- | --- | --- |
| Dry CO2 | <= 0.0010 | 0.038707 | FAIL | +0.037707 |
| Regenerated DES | <= 0.0010 | 0.022961 | FAIL | +0.021961 |

## Water balance

- Water in gas feed: 50.0000 kmol/hr
- Water in dry CO2: 38.2523 kmol/hr
- Water in condensate: 11.2982 kmol/hr
- Water in purge DES: 0.5716 kmol/hr
- Water in regenerated DES (before split): 11.3184 kmol/hr
  - of which in recycle DES: 10.8596 kmol/hr
  - of which in purge DES: 0.5716 kmol/hr
- Accounted outputs (dry + condensate + purge): 50.1221 kmol/hr
- Closure: 100.2441%

## Attribution

- Thermodynamic backend: Clapeyron/COSMOSAC2013 (V2 rigorous mode only).
- DES represented as a single pseudo-component (choline chloride / glycerol).
- Architecture decision records: ADR-0001, ADR-0002, ADR-0003, ADR-0006.
