---
name: biosteam
description: >
  Design, simulate, and analyze biorefinery and chemical process systems using BioSTEAM.
  Use this skill whenever the user mentions BioSTEAM, biosteam, biorefinery, bioethanol,
  biodiesel, butanol, biochemicals, process simulation, techno-economic analysis (TEA),
  life cycle assessment (LCA), unit operations, distillation, reactor design, heat exchanger
  networks, or wants to create/fix/optimize a Python script for chemical/bioprocess simulation.
  Also trigger when the user asks about BioSTEAM convergence issues, unit operation errors,
  or wants to generate a complete process flowsheet template.
---

# BioSTEAM Skill

You are an expert in BioSTEAM — a Python framework for biorefinery simulation and
techno-economic analysis. You help users design, simulate, and analyze chemical/bioprocess
systems. BioSTEAM builds on `thermosteam` (its thermodynamic engine) and re-exports
everything via `from thermosteam import *`.

## How to Work

**Assess complexity first.** For simple tasks (e.g., "create a mixer with two feeds"),
generate the script directly. For complex tasks (e.g., "design a lignocellulosic ethanol
biorefinery"), discuss the approach with the user first — clarify feedstock, products,
scale, and key assumptions before writing code.

**Use the knowledge base.** Three knowledge sources are available, in priority order:

1. **Context7** (official tutorials, 292 snippets): Use `mcp__plugin_context7_context7__query-docs` with library ID `/biosteamdevelopmentgroup/biosteam` for canonical examples. Pre-extracted key examples in `references/context7-examples.md`.
2. **Wiki** (code knowledge graph): Consult `references/wiki/` for class hierarchies, method signatures, and dependency graphs.
3. **Units/Templates** (hand-curated): `references/units.md` and `references/templates.md` for quick reference.

Key wiki files:

| Wiki File | Content |
|-----------|---------|
| `wiki/biosteam-cost.md` | Core classes: System, Unit, TEA, Settings, Flowsheet |
| `wiki/units-cost.md` | All unit operations with class members and design/cost methods |
| `wiki/facilities-water.md` | Facilities: BoilerTurbogenerator, CoolingTower, ProcessWaterCenter, HXN |
| `wiki/evaluation-repr.md` | Model, Parameter, Indicator, ConvergenceModel, Response |
| `wiki/process-tools-load.md` | ProcessModel, ReactorSpecification, UnitGroup, SystemFactory |
| `wiki/high-rate-design.md` | Wastewater: AnMBR, InternalCirculationRx, PolishingFilter |
| `wiki/tutorial-flow.md` | Tutorial patterns: create_system, CellulosicEthanolBiorefinery |

**Generate runnable code.** Every script you produce should be complete and executable:
import statements, chemical definitions, `set_thermo()`, streams, units, system, and
`simulate()` call. Include comments only where the "why" is non-obvious.

## Core Workflow Pattern

Every BioSTEAM simulation follows this sequence:

```python
import biosteam as bst

# 1. ALWAYS FIRST — set thermodynamic package
chemicals = bst.Chemicals([bst.Chemical('Water'), bst.Chemical('Ethanol')])
bst.settings.set_thermo(chemicals)

# 2. Define material streams
feed = bst.Stream('feed', Water=1000, Ethanol=500, units='kg/hr')

# 3. Instantiate unit operations
M1 = bst.Mixer('M1', ins=(feed, recycle))
D1 = bst.BinaryDistillation('D1', ins=M1-0, outs=('distillate', 'bottoms'),
                             LHK=('Ethanol', 'Water'), ...)

# 4. Create system and simulate
sys = bst.System('sys', path=(M1, D1))
sys.simulate()

# 5. (Optional) TEA
tea = MyTEA(system=sys, IRR=0.10, duration=(2024, 2044), ...)
```

**Critical rule:** `bst.settings.set_thermo()` must be called before creating any streams
or units. Almost every user error traces back to skipping this step.

## Unit Operations Reference

When the user needs a specific unit operation, consult `references/units.md` for the full
catalog with constructor signatures. The class hierarchy (from knowledge graph):

- `Unit` — base class, 40+ direct subclasses
  - `Facility` → BoilerTurbogenerator, CoolingTower, ProcessWaterCenter, HeatExchangerNetwork, ChilledWaterPackage, RefrigerationPackage
  - `Flash` → Evaporator, SplitFlash
  - `Distillation` → BinaryDistillation, ShortcutColumn
  - `MultiStageEquilibrium` → AdiabaticMultiStageVLEColumn, MESHDistillation, MultiStageMixerSettlers
  - `Compressor` → IsentropicCompressor, PolytropicCompressor, IsothermalCompressor, MultistageCompressor
  - `HX` → HXutility, HXprocess
  - `Tank` → MixTank, StorageTank
  - `Splitter` → Clarifier, VibratingScreen, MolecularSieve, SolidsSeparator
  - `PressureVessel` → AbstractStirredTankReactor, SingleComponentAdsorptionColumn
  - `AbstractStirredTankReactor` → AeratedBioreactor, GasFedBioreactor, AnaerobicBioreactor, EquilibriumReactor, SinglePhaseReactor
  - `Turbine` → IsentropicTurbine; `Valve` → IsenthalpicValve

Commonly used:

| Category | Units |
|----------|-------|
| Mixing/Splitting | `Mixer`, `Splitter`, `MixerSettler`, `PhaseSplitter` |
| Heat Exchange | `HeatExchanger`, `HeatExchangerNetwork` |
| Separation | `BinaryDistillation`, `Flash`, `MultiEffectEvaporator`, `LiquidLiquidExtraction`, `SolidsSeparation` |
| Reactors | `StoichiometricReactor`, `EquilibriumReactor`, `AeratedBioreactor`, `AnaerobicBioreactor`, `SinglePhaseReactor` |
| Mechanical | `Pump`, `Compressor`, `Turbine`, `Valve` |
| Solids | `ConveyingBelt`, `ScrewFeeder`, `Drying`, `BatchCrystallizer`, `SizeReduction` |
| Facilities | `BoilerTurbogenerator`, `CoolingTower`, `ProcessWaterCenter`, `ChilledWaterPackage` |
| Special | `Junction`, `Balancer`, `Scaler`, `Duplicator` |

## TEA (Techno-Economic Analysis)

TEA class (from knowledge graph) provides these key properties/methods:

- `NPV` — net present value
- `solve_IRR()` — break-even internal收益率
- `solve_price(stream)` — break-even product price [USD/kg]
- `PBP` — payback period
- `ROI` — return on investment
- `CAPEX_table`, `FOC_table`, `VOC_table` — cost breakdown tables
- `DPI`, `TDC`, `FCI`, `TCI` — capital investment hierarchy

Subclass `bst.TEA` and implement 4 abstract methods:

```python
class MyTEA(bst.TEA):
    def _FOC(self, FCI):      # Fixed operating cost
        return FCI * 0.10
    def _DPI(self, installed_cost):  # Direct permanent investment
        return installed_cost * 1.18
    def _TDC(self, DPI):      # Total depreciable capital
        return DPI * 1.14
    def _FCI(self, TDC):      # Fixed capital investment
        return TDC

tea = MyTEA(system=sys, IRR=0.10, duration=(2024, 2044),
            depreciation='MACRS7', income_tax=0.21,
            operating_days=350, lang_factor=3.0)
tea.show()
print(f"NPV: {tea.NPV:.0f}")
print(f"Bare module cost: ${tea.installed_equipment_cost:.0f}")
# Break-even price:
tea.solve_IRR()
```

Cost hierarchy: `purchase_cost → installed_equipment_cost → DPI → TDC → FCI → TCI`

## LCA (Life Cycle Assessment)

LCA is configured through `bst.settings` and stream-level impact items:

```python
bst.settings.impact_indicators = {'GWP': 'kg CO2-eq'}
# Characterization factors per utility agent:
bst.settings.utility_characterization_factors = {
    ('Cooling water', 'Cooling'): {'GWP': 0.0005},
    ('Steam', 'Low pressure'): {'GWP': 0.04},
}
# Per-stream impacts:
stream.impact_item = bst.StreamImpactItem(stream, GWP=1.5)
```

Report generation: `lca_inventory_table`, `lca_displacement_allocation_table` (from report module).

## Uncertainty & Sensitivity Analysis

Use `bst.Model` for Monte Carlo analysis (from knowledge graph: 192 nodes in evaluation module):

```python
model = bst.Model(sys)

@model.parameter(distribution=dist.Uniform(0.8, 1.2), bounds=[0.8, 1.2])
def set_yield(yield_factor):
    reactor.reaction.X = yield_factor

@model.metric(name='MESP', units='USD/gal')
def get_MESP():
    return tea.solve_price(product)

samples = model.sample(N=1000, rule='L')
model.load_samples(samples)
model.evaluate()
model.table  # results DataFrame
```

Requires `chaospy` for distributions. Sensitivity: `model.spearman()`, `model.pearson_r()`,
`model.kendall_tau()`, `model.kolmogorov_smirnov_d()`.

## Debugging Common Issues

When the user reports errors, check these in order:

1. **"Missing thermo package"** → User forgot `bst.settings.set_thermo()`. This is the #1 error.
2. **Convergence failure** → Recycle loops need attention. Default method is Aitken (sequential modular). Try switching to Wegstein: `sys.method = 'wegstein'`. Or increase `sys.maxiter` (default 200). Or relax tolerance: `sys.set_tolerance(mol=1e-3, rmol=1e-3, T=1.0, rT=1e-3)`.
3. **Empty inlet warnings** → Set `bst.settings.skip_simulation_of_units_with_empty_inlets = True` or connect a dummy stream.
4. **Phase issues** → Streams default to liquid. Set `phase='g'` for gas, `phase='s'` for solids.
5. **Unit not found** → Units register in `bst.main_flowsheet`. Access by ID: `bst.main_flowsheet('unit_id')`.
6. **Import errors** → BioSTEAM re-exports thermosteam. Use `bst.Chemical`, not `thermosteam.Chemical`.

High-risk areas from knowledge graph (untested, many callers):
- `HeatUtility.sum`, `RecycleData.update`, `System.copy`, `Unit.addkey`

Use `sys.diagram()` to visualize flowsheet, `sys.show()` for text summary, and
`unit.show()` for individual unit details.

## Process Templates

When the user wants a complete biorefinery template, read `references/templates.md` for
pre-built process configurations (corn ethanol, lignocellulosic ethanol, biodiesel, etc.)
and adapt to their specific requirements. Tutorial patterns from knowledge graph:
`create_system`, `CellulosicEthanolBiorefinery`, `SugarcaneTEA`.

## Knowledge Base Structure

The skill includes a complete knowledge graph extracted from the BioSTEAM codebase:

```
references/
├── units.md              # Unit operations catalog with constructor signatures
├── templates.md          # Pre-built process templates
├── context7-examples.md  # Canonical examples from official tutorials (Context7)
└── wiki/                 # Auto-generated documentation from code knowledge graph
    ├── index.md          # Master table of all 14 communities
    ├── biosteam-cost.md  # Core: System, Unit, TEA, Settings, Flowsheet (629 nodes)
    ├── units-cost.md     # All unit operations (984 nodes)
    ├── facilities-water.md  # Facilities (119 nodes)
    ├── evaluation-repr.md   # Model, Parameter, Indicator (192 nodes)
    ├── process-tools-load.md  # ProcessModel, UnitGroup, SystemFactory (150 nodes)
    ├── tutorial-flow.md     # Tutorial patterns (50 nodes)
    ├── high-rate-design.md  # Wastewater treatment (254 nodes)
    ├── report-table.md      # Report generation (32 nodes)
    ├── plots-plot.md        # Visualization (111 nodes)
    └── ...                  # Additional community docs
```

The wiki contains 3,019 nodes (262 classes, 2,458 functions) and 16,360 edges
documenting call relationships, inheritance hierarchies, and test coverage.
