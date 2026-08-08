---
name: rigorous-flash
description: >-
  Set up physically correct VLE flash calculations in thermosteam/Clapeyron
  when pseudo-components (DES, ionic liquids, non-volatile solvents) with
  locked_state are present. Use this skill whenever building a flash unit,
  running tp_flash, debugging flash separation results, or investigating
  why flash pressure/temperature changes have no effect on separation.
  Trigger on: "flash not working", "wrong VLE", "DES excluded from flash",
  "activity coefficient not applied", "bubble pressure wrong", or any
  flash calculation involving locked or pseudo-components.
---

# rigorous-flash

The **flash trap**: `bst.units.Flash` → `VLE._setup()` classifies any
chemical with `locked_state` as heavy/light and **excludes it from the
composition vector** passed to Clapeyron's `tp_flash`. The COSMO-SAC model
never sees that chemical — its activity coefficients are silently ignored.

This produces physically wrong results: the volatile component (e.g. water)
flashes at its pure-component saturation pressure instead of the mixture
bubble pressure $\gamma_i x_i P_{sat,i}$, giving a binary on/off switch
with no gradual transition.

## When the trap fires

Check every chemical in the system:

```python
for c in chemicals:
    if c.locked_state:
        print(f"{c.ID}: locked_state={c.locked_state}")
```

If **any** chemical has `locked_state` (typically `'l'` for DES pseudo-
components, ionic liquids, or non-volatile solvents), the trap is active.

## The bypass

Do **not** use `bst.units.Flash` or `ms.vle()`. Call the Clapeyron backend
directly:

```python
import numpy as np
from thermosteam.equilibrium.clapeyron_backend import ClapeyronBackend

# Build backend — locked_state='l' triggers DIPPR101Sat with ultra-low Psat
backend = ClapeyronBackend(tuple(chemicals), "COSMOSAC")

# Full composition vector INCLUDING the locked pseudo-component
nc = len(chemicals)
z = np.zeros(nc)
z[chemicals.index("Water")] = water_mol / total
z[chemicals.index("DES_choline_chloride_glycerol")] = des_mol / total

# Direct tp_flash — COSMO-SAC sees all components
x_comp, n_per_phase, G = backend.tp_flash(P_flash, T_flash, z)
n_liq = np.maximum(np.asarray(n_per_phase[0]), 0.0)
n_vap = np.maximum(np.asarray(n_per_phase[1]), 0.0)
```

Why this works:
- `ClapeyronBackend._build_model()` detects `locked_state='l'` and applies
  `DIPPR101Sat` with the chemical's Psat (e.g. 1e-6 Pa), keeping it in the
  liquid phase via thermodynamics, not a heuristic.
- `tp_flash` receives the full `z` vector — COSMO-SAC computes real
  $\gamma_i$ for every pair, including water-DES interactions.

## Why NOT unlock the pseudo-component

Setting `_locked_state = None` looks tempting but **loses the DIPPR101Sat
pure model** — ClapeyronBackend only sets up the ultra-low Psat when it
detects `locked_state='l'`. Without it, the pseudo-component vaporises
freely at high T, giving 100% loss.

| Approach | COSMO-SAC active? | Psat constrained? | Result |
|---|---|---|---|
| `bst.units.Flash` (default) | No (DES excluded) | Yes | Wrong: pure-water bubble pressure |
| Unlock + `bst.units.Flash` | Yes | **No** | Wrong: DES vaporises |
| **Direct `tp_flash`** | **Yes** | **Yes** | **Correct** |

## Verification checklist

🔴 **STOP — do not report flash results until all 4 checks pass.**

| # | Check | Expected | If FAILS |
|---|---|---|---|
| 1 | DES loss ≈ 0 | `n_vap[des_index]` ≈ 0 (Psat=1e-6 Pa) | DIPPR101Sat pure model missing → check `locked_state` is still `'l'` |
| 2 | Gradual transition | Water recovery changes smoothly with P | Binary on/off at pure-water Psat → trap active, switch to direct `tp_flash` |
| 3 | Bubble P < pure-water Psat | Mixture P_bub ≈ γ·x·Psat, far below pure water | Equal to pure-water Psat → COSMO-SAC not engaged, DES excluded from z |
| 4 | Temperature sensitivity | Raising T at fixed P increases water recovery | No T effect → `tp_flash` not receiving pseudo-component in z vector |

## DO NOT (blacklist)

- **DO NOT** use `bst.units.Flash` when any chemical has `locked_state` — it silently excludes that chemical from VLE.
- **DO NOT** set `_locked_state = None` to "fix" the exclusion — you lose DIPPR101Sat and the pseudo-component vaporises.
- **DO NOT** trust `ms.vle()` results without cross-checking against direct `tp_flash` — the PH-flash fallback gives spurious 50/50 splits.
- **DO NOT** report separation metrics without running the 4-point verification checklist above.

## Symptom → diagnosis → fix

| Symptom | Root cause | Fix |
|---|---|---|
| Binary on/off at pure-water Psat | DES excluded from VLE (locked as heavy) | Switch to direct `backend.tp_flash` with full `z` vector |
| 50/50 split regardless of T/P | VLE wrapper `bubble_pressure` fallback fails → defaults to 0.5 | Bypass `ms.vle()`, call `tp_flash` directly |
| DES loss > 0 at moderate T | DIPPR101Sat pure model missing (DES was unlocked) | Restore `locked_state='l'`, rebuild `ClapeyronBackend` |
| Flash P has no effect on separation | `tp_flash` not receiving pseudo-component in `z` | Verify `z[des_index] > 0` before calling |
| `ms.vle()` wrong but `tp_flash` correct | VLE wrapper PH-flash fallback to legacy solver | Use `tp_flash` only; do not use `ms.vle()` or `bst.units.Flash` |
