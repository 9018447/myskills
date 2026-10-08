---
name: seader-separations
description: "Knowledge base from \"Separation Process Principles with Applications Using Process Simulators, 4th ed.\" by J.D. Seader, E.J. Henley & D.K. Roper. Use when designing or simulating separation processes: distillation (binary/multicomponent/enhanced/batch), absorption & stripping, liquid-liquid extraction, membrane separations, adsorption, thermodynamic model selection (K-values, activity coefficients), degrees-of-freedom analysis, and Aspen Plus/CHEMCAD/ChemSep workflow."
---

# Separation Process Principles (4th ed.) — Seader, Henley & Roper

**Author**: J.D. Seader, Ernest J. Henley, D. Keith Roper | **~530 pages** | **15 chapters** | **Generated**: 2026-10-04

## How to Use This Skill

- **No arguments** — core frameworks below
- **Topic** — e.g. "minimum reflux", "Kremser", "membrane module", "which property method" → I read the mapped chapter file first
- **Chapter** — "ch09" → loads that chapter file
- **Browse** — "what chapters are covered?"

---

## Core Frameworks & Mental Models

### 1. Separation taxonomy (Ch 1)
Every separator = **ESA** (energy-separating agent: heat/work creates a phase) or **MSA** (mass-separating agent: added selective phase), realized by **phase creation / phase addition / barrier / external field**. Prefer ESA — MSA carries 4 penalties (recovery separator, makeup, contamination, harder design). Specify any separator by **product purity + component recovery**, closed with component balances. Sequence distillation trains by heuristics: hardest/most hazardous split first, easiest last; sequence counts grow combinatorially (5 products → 42 sequences).

### 2. Thermodynamics backbone (Ch 2)
Equilibrium = **fugacity equality** across phases. K-value model ladder: **EOS (SRK/PR)** for hydrocarbons/light gases; **γ-φ (NRTL/Wilson/UNIQUAC)** for polar organics; **Raoult/Henry** as limiting cases; **UNIFAC/PSRK** when data are missing. Ewell H-bond classes predict deviation signs before fitting. Azeotrope ⇔ Kᵢ=1 → distillation barrier → Ch 11 escape ladder. Second-law lens: W_actual = W_min + LW, LW = T₀ΔS_irr; real distillations run below 10% second-law efficiency.

### 3. Equilibrium-stage engineering (Ch 4–5)
**Degrees of freedom first** (Gibbs phase rule; Kwauk element method for flowsheets; single stage N_D = C+4). Flash: **Rachford–Rice** single-root iteration; bubble ΣzK=1, dew Σz/K=1; three-phase via Henley–Rosen. Cascades: **countercurrent > crosscurrent > cocurrent**; closed-form **extraction/absorption factor** 𝒜 = L/KV, ℰ = K′_D S/F, stripping factor 𝒮 = KV/L govern dilute multistage behavior (Kremser).

### 4. Distillation design stack (Ch 7, 9, 10)
Binary: **McCabe–Thiele** (45° line, equilibrium curve, q-line, two operating lines; total reflux → N_min; pinch → R_min). Multicomponent: **FUG** — Fenske N_min → non-key distribution (or Winn, wide-boiling) → **Underwood** θ-roots → R_min → **Gilliland** (fits: Molokanov/Eduljee) → **Kirkbride** feed stage; operate R ≈ 1.3 R_min. Rigorous: **MESH equations** solved by BP (narrow-boiling), SR (absorbers), SC/Naphtali–Sandholm (difficult), **inside-out** (simulator default), ISR (LLE). Fenske/Underwood/Gilliland live in Ch 9 — not Ch 7.

### 5. Rate methods (Ch 3, 6, 12)
Transport backbone: Fick/Stefan diffusion, **film / penetration / surface-renewal** theories, two-film resistance 1/K = 1/k₁ + m/k₂. Columns: tray design via **Souders–Brown/Fair flooding** at 80–85% flood; efficiency by **O'Connell** E_o=50.3(αμ)^-0.226; packed height Z = **H_OG·N_OG** (Billet–Schultes coefficients), loading ≈70% flood. **Rate-based (nonequilibrium) models** — Maxwell–Stefan interfacial flux, equilibrium only at the interface, 5C+5 equations/stage — replace efficiency guesses when systems are polar or specs are tight.

### 6. Enhanced & specialized operations (Ch 11, 13, 14, 15)
Azeotrope escape ladder: pressure-swing (≥5 mol% shift) → extractive (solvent/feed≈1, pick by γ^∞) → salt → heterogeneous+decanter → reactive distillation. **Always check residue-curve maps / DRD singular-point topology before simulating entrainers**; azeotropic columns have steady-state multiplicity. Batch: Rayleigh equation; constant-reflux vs constant-composition policies; slop cuts. Membranes: solution–diffusion P=S·D; countercurrent modules best; α capped by pressure ratio; polarization/fouling are the real design constraints. Adsorption: size beds by **LUB = L_B − LES**, never equilibrium capacity; PSA/TSA cycles; SMB triangle method.

---

## Chapter Index

| # | File | Topic | Key frameworks |
|---|------|-------|----------------|
| 1 | [ch01](chapters/ch01-separation-processes.md) | Separation Processes | ESA/MSA, phase creation/addition/barrier/field, sequencing heuristics |
| 2 | [ch02](chapters/ch02-thermodynamics-of-separations.md) | Thermodynamics | K-value models, g^E (Wilson/NRTL/UNIQUAC), UNIFAC, exergy/W_min |
| 3 | [ch03](chapters/ch03-mass-transfer-and-diffusion.md) | Mass Transfer & Diffusion | Fick/Stefan, film/penetration/renewal, diffusivity estimation, j-factors |
| 4 | [ch04](chapters/ch04-equilibrium-stages-and-flash.md) | Equilibrium Stages & Flash | Phase rule, DOF, Rachford–Rice, bubble/dew, ternary LLE |
| 5 | [ch05](chapters/ch05-cascades-and-hybrid-systems.md) | Cascades & Hybrids | Cascade configs, extraction-factor formulas, Kwauk DOF, hybrids |
| 6 | [ch06](chapters/ch06-absorption-and-stripping.md) | Absorption & Stripping | Kremser, HTU/NTU, Fair flooding, tray efficiency, reactive absorption |
| 7 | [ch07](chapters/ch07-binary-distillation.md) | Binary Distillation | McCabe–Thiele, q-line, R_min/N_min limits, efficiencies, hydraulics |
| 8 | [ch08](chapters/ch08-liquid-liquid-extraction.md) | LLE with Ternaries | Hunter–Nash, tie lines, solvent selection (Robbins), extractor types |
| 9 | [ch09](chapters/ch09-approximate-multicomponent-methods.md) | Shortcut Multicomponent | Fenske/Winn, Underwood, Gilliland, Kirkbride, FUG algorithm |
| 10 | [ch10](chapters/ch10-equilibrium-multicomponent-methods.md) | Rigorous Equilibrium Methods | MESH, BP/SR/SC/inside-out, tridiagonal solvers |
| 11 | [ch11](chapters/ch11-enhanced-distillation.md) | Enhanced Distillation & SCFE | Residue curves/DRD, extractive/PSD/azeotropic/reactive, SCFE |
| 12 | [ch12](chapters/ch12-rate-based-models.md) | Rate-Based Models | Maxwell–Stefan, nonequilibrium stages, back-calculated E_MV/HETP |
| 13 | [ch13](chapters/ch13-batch-distillation.md) | Batch Distillation | Rayleigh, constant-R vs constant-x_D, slop cuts, DAE/optimization |
| 14 | [ch14](chapters/ch14-membrane-separations.md) | Membrane Separations | Solution–diffusion, RO/gas permeation/pervaporation, modules, cascades |
| 15 | [ch15](chapters/ch15-adsorption-ion-exchange.md) | Adsorption, Ion Exchange, Chromatography | Isotherms, breakthrough/LUB, PSA/TSA, SMB, ion exchange |

## Topic Index

- **Absorption factor / Kremser** → ch06
- **Activity coefficient models (Wilson/NRTL/UNIQUAC)** → ch02
- **Adsorption fixed-bed / breakthrough / LUB / SMB** → ch15
- **Azeotropes** → ch02, ch11
- **Batch distillation / Rayleigh** → ch13
- **Degrees of freedom** → ch04, ch05
- **Distillation sequencing heuristics** → ch01, ch09
- **Efficiency (Murphree, O'Connell, Oldershaw)** → ch06, ch07
- **Enhanced distillation (extractive/PSD/azeotropic/reactive)** → ch11
- **Exergy / minimum work** → ch02
- **Extractive distillation / entrainers** → ch11
- **Fenske / Underwood / Gilliland / Kirkbride (FUG)** → ch09
- **Flash calculations (Rachford–Rice, bubble/dew)** → ch04
- **Flooding / column diameter (Fair, Souders–Brown, GPDC)** → ch06, ch07
- **Hunter–Nash / solvent selection** → ch08
- **Inside-out / BP / SR / SC (Naphtali–Sandholm)** → ch10
- **Ion exchange** → ch15
- **Kremser / Edmister group methods** → ch06, ch09
- **Mass-transfer coefficients / film, penetration, renewal theories** → ch03
- **MESH equations / tridiagonal solvers** → ch10
- **McCabe–Thiele** → ch07
- **Membranes (RO, gas permeation, pervaporation, dialysis)** → ch14
- **Minimum reflux / pinch point** → ch07, ch09
- **Packed columns / HTU-NTU / HETP / Billet–Schultes** → ch06, ch07
- **Property-method selection (simulator)** → ch02
- **Rate-based (nonequilibrium) models / Maxwell–Stefan** → ch12
- **Residue-curve maps / distillation boundaries** → ch11
- **Reactive distillation** → ch11
- **Reactive absorption / amines / Hatta** → ch06
- **Supercritical-fluid extraction** → ch11
- **Thermodynamic model selection (EOS vs γ-φ)** → ch02
- **Tray hydraulics / diameter sizing** → ch06, ch07

## Supporting Files

- [glossary.md](glossary.md) — all key terms, alphabetized
- [patterns.md](patterns.md) — design patterns: when/how/trade-offs per operation
- [cheatsheet.md](cheatsheet.md) — decision tables, thresholds & defaults, red flags

---

## Scope & Limits

Synthesized chapter summaries (not the book text) generated from the 4th edition. Covers equilibrium-stage, rate-based, enhanced, batch, membrane, and adsorption separations with simulator workflow (Aspen Plus / CHEMCAD / ChemSep). For full derivations, data tables, and problem sets, consult the book; images/figures were not retained by the converter. Combine with project-specific simulator knowledge for hands-on design work.
