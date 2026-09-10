# BioSTEAM Process Templates

Pre-built process configurations for common biorefinery systems.
Adapt these to the user's specific feedstock, scale, and product requirements.

## 1. Corn Ethanol Biorefinery

**Feedstock:** Corn grain
**Product:** Fuel-grade ethanol (anhydrous)
**Key steps:** Milling → Liquefaction → Saccharification → Fermentation → Distillation → Dehydration

```python
import biosteam as bst

# Chemicals
chemicals = bst.Chemicals([
    bst.Chemical('Water'),
    bst.Chemical('Ethanol'),
    bst.Chemical('Glucose'),
    bst.Chemical('CO2'),
    bst.Chemical('Starch', phase='s'),
    bst.Chemical('Cellulose', phase='s'),
    bst.Chemical('Oil'),
])
bst.settings.set_thermo(chemicals)

# Feed
corn = bst.Stream('corn', Starch=10000, Water=1500, Oil=400, units='kg/hr')

# Process units
M1 = bst.Mixer('M1', ins=(corn, ...))  # Add water, enzymes
# Liquefaction reactor (converts starch to dextrins)
# Saccharification reactor (converts dextrins to glucose)
# Fermentation (glucose → ethanol + CO2)
R1 = bst.AeratedBioreactor('R1', ins=(..., air), outs=('vent', 'beer'),
                             reaction={'Glucose': -1, 'Ethanol': 0.51, 'CO2': 0.49},
                             X=0.90, tau=48)
# Distillation
D1 = bst.BinaryDistillation('D1', ins=R1-1, outs=('dist', 'stillage'),
                             LHK=('Ethanol', 'Water'), Lr=0.99, Hr=0.01, k=1.5)
# Molecular sieve dehydration
MS1 = bst.MolecularSieve('MS1', ins=D1-0, outs=('anhydrous', 'wet'),
                          split={'Ethanol': 0.995, 'Water': 0.01})

# System
sys = bst.System('ethanol_plant', path=(M1, R1, D1, MS1))
sys.simulate()

# TEA
class CornEthanolTEA(bst.TEA):
    def _FOC(self, DPI): return DPI * 0.04
    def _DPI(self, installed): return installed * 1.18
    def _TDC(self, DPI): return DPI * 1.14
    def _FCI(self, TDC): return TDC

tea = CornEthanolTEA(system=sys, IRR=0.10, duration=(2024, 2044),
                      depreciation='MACRS7', income_tax=0.21,
                      operating_days=350, lang_factor=3.0)
tea.show()
MESP = tea.solve_price(MS1-0)
print(f"MESP: ${MESP:.2f}/gal")
```

## 2. Lignocellulosic (Cellulosic) Ethanol

**Feedstock:** Corn stover, switchgrass, or wood chips
**Product:** Fuel-grade ethanol
**Key steps:** Pretreatment → Enzymatic Hydrolysis → Fermentation → Distillation

```python
# Chemicals
chemicals = bst.Chemicals([
    bst.Chemical('Water'),
    bst.Chemical('Ethanol'),
    bst.Chemical('Glucose'),
    bst.Chemical('Xylose'),
    bst.Chemical('Cellulose', phase='s'),
    bst.Chemical('Hemicellulose', phase='s'),
    bst.Chemical('Lignin', phase='s'),
    bst.Chemical('CO2'),
])
bst.settings.set_thermo(chemicals)

# Feed (corn stover)
stover = bst.Stream('stover',
    Cellulose=3500, Hemicellulose=2200, Lignin=1800,
    Water=500, units='kg/hr')

# Dilute acid pretreatment
# Converts hemicellulose → xylose
pretreatment = bst.StoichiometricReactor('pretreatment',
    ins=stover, outs='pretreated',
    reaction={'Hemicellulose': -1, 'Xylose': 0.9},
    X=0.90, tau=0.5)

# Enzymatic hydrolysis
# Converts cellulose → glucose
hydrolysis = bst.StoichiometricReactor('hydrolysis',
    ins=pretreatment-0, outs='hydrolysate',
    reaction={'Cellulose': -1, 'Glucose': 0.95},
    X=0.90, tau=72)

# Co-fermentation (glucose + xylose → ethanol)
fermentation = bst.AeratedBioreactor('fermentation',
    ins=(hydrolysis-0, ...), outs=('vent', 'beer'),
    tau=60)

# Distillation + dehydration (same as corn ethanol)
# ...

# Lignin-rich bottoms → boiler for steam/power
# bst.BoilerTurbogenerator('BT', ins=(lignin_stream, ...))
```

## 3. Biodiesel (Transesterification)

**Feedstock:** Soybean oil, waste cooking oil, or algae oil
**Product:** Fatty acid methyl esters (FAME / biodiesel)
**Key steps:** Esterification → Transesterification → Separation → Washing

```python
chemicals = bst.Chemicals([
    bst.Chemical('Water'),
    bst.Chemical('Methanol'),
    bst.Chemical('Glycerol'),
    bst.Chemical('TAG', formula='C57H104O6', phase='l'),  # Triglyceride
    bst.Chemical('FAME', formula='C19H36O2', phase='l'),   # Biodiesel
    bst.Chemical('NaOH'),
])
bst.settings.set_thermo(chemicals)

oil = bst.Stream('oil', TAG=1000, units='kg/hr')
methanol = bst.Stream('methanol', Methanol=150, units='kg/hr')
catalyst = bst.Stream('catalyst', NaOH=10, Water=50, units='kg/hr')

# Transesterification reactor
# TAG + 3 MeOH → 3 FAME + Glycerol
R1 = bst.StoichiometricReactor('R1',
    ins=bst.Mixer('M_in', ins=(oil, methanol, catalyst))-0,
    outs='crude_biodiesel',
    reaction={'TAG': -1, 'Methanol': -3, 'FAME': 3, 'Glycerol': 1},
    X=0.98, tau=2)

# Gravity separation (FAME on top, glycerol on bottom)
S1 = bst.MixerSettler('S1', ins=R1-0,
    outs=('biodiesel_crude', 'glycerol_crude'))

# Wash and purify biodiesel
# ...

# TEA
tea = BiodieselTEA(system=sys, IRR=0.10, duration=(2024, 2044), ...)
```

## 4. Succinic Acid Fermentation

**Feedstock:** Glucose (from corn or lignocellulose)
**Product:** Succinic acid
**Key steps:** Fermentation → Separation → Purification

```python
chemicals = bst.Chemicals([
    bst.Chemical('Water'),
    bst.Chemical('Glucose'),
    bst.Chemical('SuccinicAcid', formula='C4H6O4'),
    bst.Chemical('CO2'),
])
bst.settings.set_thermo(chemicals)

glucose_feed = bst.Stream('glucose', Glucose=500, Water=2000, units='kg/hr')

# Anaerobic fermentation
R1 = bst.AnaerobicBioreactor('R1', ins=glucose_feed,
    outs=('biogas', 'broth'),
    reaction={'Glucose': -1, 'SuccinicAcid': 1.1, 'CO2': 0.2},
    X=0.85, tau=72)

# Reactive crystallization
# Or: electrodialysis, ion exchange, esterification-hydrolysis
# ...

# TEA for MESP (minimum ethanol selling price) analog:
# solve_price(product_stream)
```

## 5. Simple TEA Template

For any process that just needs a quick economic assessment:

```python
class QuickTEA(bst.TEA):
    def _FOC(self, DPI):
        # Labor + overhead + maintenance
        return DPI * 0.04 + 1e6  # 4% of DPI + $1M labor
    def _DPI(self, installed):
        return installed * 1.18  # 18% for piping, instruments, etc.
    def _TDC(self, DPI):
        return DPI * 1.14  # 14% for land, startup, etc.
    def _FCI(self, TDC):
        return TDC

tea = QuickTEA(
    system=sys,
    IRR=0.10,           # 10% return rate
    duration=(2024, 2044),  # 20-year project life
    depreciation='MACRS7',  # 7-year MACRS
    income_tax=0.21,    # US federal corporate tax
    operating_days=350,
    lang_factor=3.0,    # Bare module to total plant cost
)
tea.show()
print(f"NPV: ${tea.NPV:,.0f}")
print(f"Bare module cost: ${tea.installed_equipment_cost:,.0f}")
print(f"Break-even price: ${tea.solve_price(product_stream):.4f}/kg")
```

## 6. Uncertainty Analysis Template

```python
import chaospy as cp

model = bst.Model(sys)

@model.parameter(
    name='Feed flow rate',
    distribution=cp.Uniform(0.8, 1.2),
    units='-',
    baseline=1.0,
)
def set_feed(flow_factor):
    feed.set_total_flow(flow_factor * base_flow, 'kg/hr')

@model.parameter(
    name='Reactor conversion',
    distribution=cp.Triangle(0.75, 0.90, 0.95),
    units='-',
    baseline=0.90,
)
def set_conversion(X):
    reactor.X = X

@model.metric(name='Product price', units='USD/kg')
def product_price():
    return tea.solve_price(product)

@model.metric(name='GWP', units='kg CO2-eq/kg')
def gwp():
    return get_GWP_per_kg(product)

N = 1000
samples = model.sample(N, rule='L')  # Latin hypercube
model.load_samples(samples)
model.evaluate()

# Results
model.table  # DataFrame with all samples and metrics
model.spearman()  # Sensitivity analysis
```

## Notes

- These templates are starting points. Adapt chemicals, reactions, and units to match
  the user's specific process.
- Always check the actual BioSTEAM API for current parameter names and defaults.
- For processes in the Bioindustrial-Park repository, check if there's already a
  flowsheet module that can be imported directly.
