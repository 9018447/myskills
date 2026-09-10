# Settings Reference

## Table of Contents
1. [Settings Basics](#settings-basics)
2. [AMS Task Settings](#ams-task-settings)
3. [DFTB Engine](#dftb-engine)
4. [Force Field Engine](#force-field-engine)
5. [GFN-xTB Engine](#gfn-xtb-engine)
6. [GFN-NDO Engine](#gfn-ndo-engine)
7. [Molecular Dynamics Settings](#molecular-dynamics-settings)
8. [Properties Settings](#properties-settings)

---

## Settings Basics

`Settings` is a nested dictionary for configuring jobs:

```python
settings = plams.Settings()

# Dot notation creates nested keys automatically
settings.input.ams.Task = "GeometryOptimization"
settings.input.ams.Properties.NormalModes = "Yes"
settings.input.DFTB.Model = "GFN1-xTB"
```

---

## AMS Task Settings

```python
settings = plams.Settings()

# Geometry Optimization
settings.input.ams.Task = "GeometryOptimization"

# Single Point Energy
settings.input.ams.Task = "SinglePoint"

# Molecular Dynamics
settings.input.ams.Task = "MolecularDynamics"

# Fragment Analysis
settings.input.ams.Task = "FragmentAnalysis"

# Transition State Search
settings.input.ams.Task = "TransitionStateSearch"
```

---

## DFTB Engine

```python
settings.input.ams.Task = "GeometryOptimization"
settings.input.DFTB.Model = "GFN1-xTB"  # or "GFN2-xTB"
settings.input.DFTB.Resources = []  # No external resources needed
```

---

## Force Field Engine

```python
settings.input.ams.Task = "GeometryOptimization"
settings.input.ForceField.Type = "UFF"  # Universal Force Field
# or
settings.input.ForceField.Type = "DFFA"  # Distance Field Force Field
```

---

## GFN-xTB Engine

GFN2-xTB is the default when using AMS2024+:

```python
settings.input.ams.Task = "GeometryOptimization"
# GFN2-xTB is used by default in AMS2024+
settings.input.GFN2xTB
```

For GFN1-xTB (legacy):
```python
settings.input.DFTB.Model = "GFN1-xTB"
```

---

## GFN-NDO Engine

For excited states and TD-DFTB calculations:

```python
settings.input.ams.Task = "SinglePoint"
settings.input.GFNDO
```

---

## Molecular Dynamics Settings

```python
settings.input.ams.Task = "MolecularDynamics"

# Time step and duration
settings.input.ams.MD.TimeStep = 1.0  # femtoseconds
settings.input.ams.MD.NSteps = 5000

# Temperature
settings.input.ams.MD.Temperature = 300  # Kelvin
settings.input.ams.MD.TemperatureTop = 300  # for NPT

# Thermostats
settings.input.ams.MD.Thermostat.Type = "NVT"  # or "NPT", "NVE"
settings.input.ams.MD.Thermostat.Tau = 100  # thermostat coupling time (fs)

# Initial velocities
settings.input.ams.MD.InitialVelocities.Type = "Maxwell"

# NPT specific
settings.input.ams.MD.Pressure = 1.0  # bar
settings.input.ams.MD.PressureCoupling = "ISO"  # ISO, ANISO, or FULL
```

### Ensemble Options
- `NVT` - Canonical (constant N, V, T)
- `NPT` - Isothermal-isobaric (constant N, P, T)
- `NVE` - Microcanonical (constant N, V, E)

---

## Properties Settings

```python
# Enable normal modes (frequencies)
settings.input.ams.Properties.NormalModes = "Yes"

# Enable Hessian
settings.input.ams.Properties.Hessian = "Yes"

# Enable IR spectrum
settings.input.ams.Properties.IR = "Yes"

# Enable Raman
settings.input.ams.Properties.Raman = "Yes"

# Enable dipole moments
settings.input.ams.Properties.DipoleMoment = "Yes"

# Enable orbitals
settings.input.ams.Properties.Orbitals = "Yes"
```
