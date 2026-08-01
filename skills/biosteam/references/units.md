# BioSTEAM Unit Operations Reference

Full catalog of available unit operations with key constructor parameters.
Derived from the knowledge graph (984 nodes in units community).

## Class Hierarchy

All units inherit from `Unit`. The inheritance tree:

```
Unit
├── Facility → BoilerTurbogenerator, Boiler, CoolingTower, ProcessWaterCenter,
│              HeatExchangerNetwork, ChilledWaterPackage, RefrigerationPackage,
│              CIPpackage, FireWaterTank, ChemicalCapitalInvestment, BlowdownMixer,
│              AirDistributionPackage
├── Flash → Evaporator, SplitFlash
├── Distillation → BinaryDistillation, ShortcutColumn
├── MultiStageEquilibrium → AdiabaticMultiStageVLEColumn, MESHDistillation,
│                           MultiStageMixerSettlers
├── StageEquilibrium, SinglePhaseStage, PhasePartition, ReactivePhaseStage
├── Compressor → IsentropicCompressor, PolytropicCompressor,
│                IsothermalCompressor, MultistageCompressor
├── HX → HXutility, HXprocess
├── Tank → MixTank, StorageTank
│   └── MixTank → EnzymeTreatment, InternalCirculationRx
├── Splitter → Clarifier, VibratingScreen, MolecularSieve, SolidsSeparator
│   └── SolidsSeparator → CrushingMill, PressureFilter, RotaryVacuumFilter,
│                          ScrewPress, SolidsCentrifuge
├── PressureVessel → AbstractStirredTankReactor, SingleComponentAdsorptionColumn,
│                    LiquidsMixingTank, LiquidsSettler
│   └── AbstractStirredTankReactor → AeratedBioreactor, GasFedBioreactor,
│                                     AnaerobicBioreactor, EquilibriumReactor,
│                                     SinglePhaseReactor
├── Turbine → IsentropicTurbine
├── Valve → IsenthalpicValve
├── Pump, Junction, Scaler, Duplicator, MassBalance
├── BatchCrystallizer, MultiEffectEvaporator
├── AmineAbsorption, CO2Compression
└── Wastewater: AnMBR, PolishingFilter, SludgeHandling, WWTpump,
                BiogasUpgrading, CHP, ReverseOsmosis,
                AnaerobicDigestion, AerobicDigestion
```

## Mixing & Splitting

### Mixer
Mixes multiple inlet streams into one outlet.
```python
bst.Mixer('M1', ins=(s1, s2, s3), outs='mixed')
```

### Splitter
Splits one inlet stream by flow fraction.
```python
bst.Splitter('S1', ins=feed, outs=('top', 'bottom'), split=0.5)
# Or by component:
bst.Splitter('S1', ins=feed, split={'Water': 0.3, 'Ethanol': 0.9})
```

### MixerSettler
Liquid-liquid extraction with mixing and settling phases.
Design method: `_design` (criticality 0.61)
```python
bst.MixerSettler('MS1', ins=(feed, solvent), outs=('raffinate', 'extract'))
```

### PhaseSplitter
Separates phases based on thermodynamic equilibrium.
```python
bst.PhaseSplitter('PS1', ins=feed, outs=('vapor', 'liquid'))
```

## Heat Exchange

### HeatExchanger (HX)
General heat exchanger with hot/cold sides.
Design method: `HXutility._design` (criticality 0.54)
```python
bst.HeatExchanger('HX1', ins=(cold_in, hot_in), outs=('cold_out', 'hot_out'),
                   U=0.5, dT=10)
```

### HeatExchangerNetwork (in facilities/hxn)
Auto-design heat integration network via pinch analysis.
Key method: `synthesize_network`, `temperature_interval_pinch_analysis`
```python
from biosteam.facilities.hxn import HeatExchangeNetwork
HXN = HeatExchangeNetwork('HXN')
sys = bst.System('sys', path=(..., HXN))
```

## Separation

### BinaryDistillation
Two-product distillation column. Inherits from `Distillation`.
Key methods from knowledge graph: `hot_start`, `liquid_compositions`, `compute_tower_wall_thickness`
```python
bst.BinaryDistillation('D1', ins=feed,
    outs=('distillate', 'bottoms'),
    LHK=('Ethanol', 'Water'),  # Light/Heavy key components
    Lr=0.99, Hr=0.99,          # Recovery of LK/HK
    k=1.5,                      # Reflux ratio / minimum reflux ratio
    P=101325,                   # Pressure (Pa)
)
```

### Flash
Single-stage vapor-liquid equilibrium separation.
Design methods: `_run`, `_size_flash_vessel`, `_default_vessel_type`
```python
bst.Flash('F1', ins=feed, outs=('vapor', 'liquid'),
          V=0.5, P=101325)
```

### MultiEffectEvaporator
Concentration via multi-effect evaporation.
```python
bst.MultiEffectEvaporator('MEE1', ins=feed,
    outs=('condensate', 'concentrate'),
    P=(101325, 70000, 40000), V=0.5)
```

### LiquidLiquidExtraction
Countercurrent liquid-liquid extraction. 58 nodes in knowledge graph.
```python
bst.LiquidLiquidExtraction('LLE1', ins=(feed, solvent),
    outs=('raffinate', 'extract'), N_stages=5)
```

### SolidsSeparation
Separates solids from liquids (filtration, centrifugation).
Subclasses: CrushingMill, PressureFilter, RotaryVacuumFilter, ScrewPress, SolidsCentrifuge
```python
bst.SolidsSeparation('SS1', ins=slurry,
    outs=('filtrate', 'solids'), moisture_content=0.2)
```

## Reactors

### StoichiometricReactor
Fixed conversion reactor with defined reactions.
```python
bst.StoichiometricReactor('R1', ins=feed, outs='product',
    reaction={'A': -1, 'B': 1}, X=0.9)
```

### EquilibriumReactor
Reacts to chemical equilibrium. Inherits from AbstractStirredTankReactor.
Key method: `plot_Gibbs_equilibrium_reaction_surface`
```python
bst.EquilibriumReactor('ER1', ins=feed, outs='product',
    reaction=rxn, T=350 + 273.15)
```

### AeratedBioreactor
Fermentation with aeration and agitation. 45 nodes in knowledge graph.
Key method: `kLa_stirred_Galaction`
```python
bst.AeratedBioreactor('ABR1', ins=(feed, air),
    outs=('vent', 'product'), reaction=rxn, X=0.9, tau=48)
```

### AnaerobicBioreactor
Anaerobic digestion reactor.
```python
bst.AnaerobicBioreactor('AN1', ins=feed,
    outs=('biogas', 'effluent'), ...)
```

### SinglePhaseReactor
General-purpose reactor for single-phase reactions.
```python
bst.SinglePhaseReactor('R1', ins=feed, outs='product',
    reaction=rxn, X=0.85, tau=2)
```

## Mechanical

### Pump
```python
bst.Pump('P1', ins=feed, outs='pressurized', dP=1e5, eta=0.7)
```

### Compressor
46 nodes in knowledge graph. Subclasses: Isentropic, Polytropic, Isothermal, Multistage.
```python
bst.Compressor('C1', ins=feed, outs='compressed', P=5e5, eta=0.75)
```

### Turbine → IsentropicTurbine
```python
bst.Turbine('T1', ins=feed, outs='expanded', P=1e5, eta=0.85)
```

### Valve → IsenthalpicValve
```python
bst.Valve('V1', ins=feed, outs='depressurized', P=1e5)
```

## Solids Handling

### ConveyingBelt
```python
bst.ConveyingBelt('CB1', ins=solids, outs='conveyed')
```

### Drying
```python
bst.Drying('DR1', ins=(wet_solids, hot_air),
           outs=('dry_solids', 'humid_air'), moisture_content=0.05)
```

### BatchCrystallizer
Key properties: `N` (number of crystallizers), `V` (volume), `tau` (residence time)
```python
bst.BatchCrystallizer('BC1', ins=feed, outs=('crystals', 'mother_liquor'),
                       T=273.15 + 5, tau=4)
```

### SizeReduction
Subclasses: CrushingMill
```python
bst.SizeReduction('SR1', ins=feed, outs='ground', energy_consumption=0.02)
```

## Facilities

### BoilerTurbogenerator
Burns solid waste to generate steam and electricity. 491 lines in source.
Key properties: `fuel`, `air`, `makeup_water`, `emissions`, `ash_disposal`, `fuel_price`
```python
bst.BoilerTurbogenerator('BT1',
    ins=(solid_fuel, makeup_water, ...),
    outs=('emissions', 'blowdown'),
    boiler_efficiency=0.80, turbogenerator_efficiency=0.85)
```

### CoolingTower
Key properties: `blowdown_water`, `evaporation_water`
```python
bst.CoolingTower('CT1')
```

### ProcessWaterCenter
```python
bst.ProcessWaterCenter('PWC1')
```

### ChilledWaterPackage
Key method: `_load_chilled_water_utilities`
```python
bst.ChilledWaterPackage('CWP1')
```

## Special Purpose

### Junction
Converts between stream types or phases.
```python
bst.Junction('J1', ins=stream, outs='converted', ...)
```

### Balancer (MassBalance)
Balances flows to meet a specification. 127 lines in source.
```python
bst.MassBalance('B1', outs='balanced', chemical='Water')
```

### Scaler
Scales stream flows by a factor.
```python
bst.Scaler('SC1', ins=stream, outs='scaled', scale=2.0)
```

### Duplicator
Duplicates a stream's flow to multiple outlets.
```python
bst.Duplicator('D1', ins=stream, outs=('copy1', 'copy2'))
```

## Critical Execution Flows (from knowledge graph)

These are the highest-criticality design/cost methods — handle with care:

| Criticality | Method | Description |
|-------------|--------|-------------|
| 0.69 | `compute_vacuum_system_power_and_cost` | Vacuum system sizing |
| 0.61 | `DesignCenter.__call__` | Distillation design center |
| 0.61 | `PressureVessel._design_and_cost_pressure_vessel` | Pressure vessel sizing |
| 0.61 | `MixerSettler._design` | LLE design |
| 0.60 | `AbstractStirredTankReactor._design` | Bioreactor design |
| 0.54 | `HXutility._design` | Heat exchanger design |
| 0.53 | `GasFedBioreactor._design` | Gas-fed bioreactor |
| 0.52 | `SplitFlash._design` | Split flash design |

## Notes

- All units register in `bst.main_flowsheet` by their ID string.
- Access a unit by ID: `bst.main_flowsheet('unit_id')`.
- Each unit tracks `HeatUtility` and `PowerUtility` consumption automatically.
- Use `unit.show()` for detailed info, `unit.results()` for a summary DataFrame.
- Stream connections use the subtraction operator: `M1-0` means "first outlet of M1".
