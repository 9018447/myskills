# BioSTEAM Official Tutorial Examples (via Context7)

Canonical examples from BioSTEAM's official tutorial notebooks.
Library ID: `/biosteamdevelopmentgroup/biosteam` (292 code snippets)

## TEA: SugarcaneTEA (Official Example)

The canonical TEA subclass from the official tutorial. Demonstrates all 4 abstract methods:

```python
class SugarcaneTEA(bst.TEA):
    def __init__(self, system, IRR, duration, depreciation, income_tax,
                 operating_days, lang_factor, construction_schedule, WC_over_FCI,
                 labor_cost, fringe_benefits, property_tax,
                 property_insurance, supplies, maintenance, administration):
        super().__init__(system, IRR, duration, depreciation, income_tax,
                         operating_days, lang_factor, construction_schedule,
                         startup_months=0, startup_FOCfrac=0, startup_VOCfrac=0,
                         startup_salesfrac=0, finance_interest=0, finance_years=0,
                         finance_fraction=0, WC_over_FCI=WC_over_FCI)
        self.labor_cost = labor_cost
        self.fringe_benefits = fringe_benefits
        self.property_tax = property_tax
        self.property_insurance = property_insurance
        self.supplies = supplies
        self.maintenance = maintenance
        self.administration = administration

    def _DPI(self, installed_equipment_cost):
        return installed_equipment_cost

    def _TDC(self, DPI):
        return DPI

    def _FCI(self, TDC):
        return TDC

    def _FOC(self, FCI):
        return (FCI*(self.property_tax + self.property_insurance
                     + self.maintenance + self.administration)
                + self.labor_cost*(1+self.fringe_benefits+self.supplies))
```

TEA instantiation:
```python
tea = SugarcaneTEA(
    system=sc.sugarcane_sys,
    IRR=0.15, duration=(2018, 2038), depreciation='MACRS7',
    income_tax=0.21, operating_days=200, lang_factor=3,
    construction_schedule=(0.4, 0.6), WC_over_FCI=0.05,
    labor_cost=2.5e6, fringe_benefits=0.4,
    property_tax=0.001, property_insurance=0.005,
    supplies=0.20, maintenance=0.01, administration=0.005
)
tea.show()
tea.IRR = tea.solve_IRR()
```

NPV/IRR comparison:
```python
sugarcane_mode.simulate()
sc.sugarcane_tea.IRR = sc.sugarcane_tea.solve_IRR()
print(f'NPV: {round(sc.sugarcane_tea.NPV/1e6)} MMUSD')
print(f'IRR: {sc.sugarcane_tea.IRR:.0%}')
print(f'TCI: {sc.sugarcane_tea.TCI/1e6:.0f} MMUSD')
```

## Process Flowsheet with Recycle Loop

```python
recycle = bst.Stream('liquid_recycle')
feed = bst.Stream('feed', Methanol=100, Water=450)
M1 = bst.Mixer('M1', ins=(recycle, feed))
F1 = bst.Flash('F1',
    ins=M1-0,  # pipe notation
    outs=('vapor_product', 'liquid'),
    V=0.1, P=101325
)
S1 = bst.Splitter('S1',
    ins=F1-1,
    outs=(recycle, 'liquid_product'),
    split=0.5
)
```

## Process Specifications (Analytical)

### Corn Slurry Solids Content
```python
@M1.add_specification(run=True, args=[0.32])
def adjust_water_flow(solids_content):
    F_mass_moisture = corn_feed.imass['Water']
    F_mass_solids = corn_feed.F_mass - F_mass_moisture
    water_solids_ratio = (1 - solids_content) / solids_content
    dilution_water.imass['Water'] = F_mass_solids * water_solids_ratio
```

### Denaturant Flow Adjustment
```python
@M1.add_specification(run=True)
def adjust_denaturant_flow():
    denaturant_over_ethanol_flow = 0.02 / 0.98
    denaturant.imass['Octane'] = denaturant_over_ethanol_flow * dehydrated_ethanol.F_mass
```

### Specifications with Impacted Units
```python
M1.add_specification(
    adjust_water_flow,
    args=[0.32],
    run=True,
    impacted_units=[P1],  # guides simulation order in recycle loops
)
```

## Mixer Pressure Behavior

Outlet pressure defaults to minimum inlet pressure:
```python
s_in1 = bst.Stream('s_in1', Water=1, units='kg/hr', P=2*101325)
s_in2 = bst.Stream('s_in2', Water=1, units='kg/hr', P=101325)
M1 = bst.Mixer('M1', ins=[s_in1, s_in2], outs='s_out')
M1.simulate()
# Outlet pressure = min(inlet pressures) = 101325 Pa
```
