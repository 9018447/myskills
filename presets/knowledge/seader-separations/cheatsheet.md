# Cheatsheet — Separation Process Principles (Seader, Henley & Roper, 4th ed.)

## Operation choice (pick the first that works)

| Situation | Operation | Why |
|---|---|---|
| Wide-boiling binary/multicomponent, thermally stable | Distillation | Cheapest per unit capacity, no MSA penalty |
| Close boilers, α→1, thermally fragile | Liquid–liquid extraction | Solvent selectivity beats volatility |
| Azeotrope | Extractive / pressure-swing / hetero-azeotropic (Ch 11) | Breaks Kᵢ=1 barrier |
| Dilute solute from gas | Absorption (+ reactive absorbent for acid gases) | Liquid-phase control |
| Dilute solute from liquid | Stripping / adsorption | Vapor or solid MSA |
| Trace PPM polishing, drying, gas splitting | Adsorption (PSA/TSA) or membranes | Solid/barrier selectivity |
| Desalination / large-scale molecule sorting | RO / membranes | No phase change |
| Small batches, multiproduct | Batch distillation | Flexibility |

**MSA penalty (avoid MSA when ESA suffices)**: 1) extra recovery separator, 2) solvent makeup losses, 3) product contamination, 4) harder design.

## Distillation design thresholds

- Operating reflux: **R ≈ 1.2–1.5 × R_min** (optimum ≈ 1.3; N ≈ 2×N_min)
- Column pressure: total condenser **< 215 psia**; partial 215–365; refrigerant above; ΔP ≈ **0.1 psi/tray**
- Condenser selection order: total → partial → refrigerated, by overhead dew point
- Tray design: **80–85% of flood**; sieve turndown ≈ 2:1, valve ≈ 4:1; ΔP ≈ 0.1 psi/tray
- Efficiency: **O'Connell** E_o = 50.3(αμ)⁻⁰·²²⁶ (μ in cP); Drickamer–Bradford if only μ known; Oldershaw data for scale-up
- Absorber: operate **1.1–2× L_min**, 𝒜 ≈ 1.4 target; stripper 𝒮 > 1
- Packed column: load at **~70% flood** (preloading region); ΔP_flood ≈ 0.115·F_P^0.7 in H₂O/ft; HETP: structured ≈ 0.4 m, random ≈ 0.6–0.9 m (rule of thumb, verify with Billet–Schultes)
- Feed stage: **Kirkbride** equation (not Brown–Martin)

## Thermodynamic model choice (simulator property method)

| System | Model |
|---|---|
| Hydrocarbons/light gases, ≤10 bar | SRK or PR EOS (K = φL/φV) |
| High-pressure hydrocarbons | PR (better liquid density/critical region) |
| Ideal-ish liquids (benzene–toluene) | Raoult / ideal K |
| Polar organics, non-electrolyte | NRTL / Wilson / UNIQUAC (γ-φ) |
| Missing binary data | UNIFAC (predictive) / PSRK / VTPR |
| LLE prediction | NRTL or UNIQUAC (Wilson can NOT do LLE) |
| Electrolytes | e-NRTL / electrolyte models |
| Polymer solutions | Flory–Huggins / UNIFAC-FV |
| H-bond classes (Ewell): I+I → negative dev., I+II → positive (may split) | sanity-check γ before fitting |

**Azeotrope red flag**: min-boiling when γᵢ>1 both components; Kᵢ=1 at azeotrope means distillation ceiling → go to Ch 11 toolkit.

**Azeotrope escape ladder**: pressure-swing (needs ≥5 mol% shift) → extractive (solvent/feed ≈1, pick by γ^∞) → salt → heterogeneous + decanter → reactive distillation → pervaporation/membrane hybrid. **Always check residue-curve map / DRD before simulating entrainers.**

## Rigorous solver selection (Ch 10)

| System | Method |
|---|---|
| Narrow-boiling, near-ideal | BP (Wang–Henke) — now an initializer |
| Wide-boiling absorber/stripper | SR (Burningham–Otto) |
| Polar/nonideal, difficult | SC (Naphtali–Sandholm) Newton |
| Default in simulators | Inside-out (Boston–Sullivan) |
| LLE column | ISR (Tsuboka–Katayama) |
| Efficiency unpredictable / tight spec | Rate-based (Ch 12), back-calc E_MV/HETP |

**Spec discipline**: start simulations with standard pairs (R + B flow, or D + R); exotic specs rarely converge; N must exceed N_min for specified purities.

## Degrees-of-freedom quick counts

- Single equilibrium stage (2 products, C components): N_D = C + 4
- Gibbs phase rule (intensive): C − P + 2
- Cascade/flowsheet: Kwauk N_D = N_V − N_E, subtract N_R(C+3) redundancies per interconnecting stream
- Distillation column (C components): spec P, R (or D), plus C−2 compositions/flows → count before simulating

## Flash / stage calculations (Ch 4)

- Isothermal flash: Rachford–Rice f(Ψ)=Σzᵢ(Kᵢ−1)/(1+Ψ(Kᵢ−1))=0, Newton on Ψ; check f(0), f(1) signs for phase existence
- Bubble point: ΣzᵢKᵢ = 1; dew point: Σzᵢ/Kᵢ = 1
- Two liquid phases: modified Rachford–Rice with K_D = γ⁽²⁾/γ⁽¹⁾; three-phase flash: Henley–Rosen
- Extraction single stage: ℰ = K′_D·S/F; multiple crosscurrent: ℰ per stage; countercurrent wins (Ch 5)

## Extraction numbers (Ch 8)

- Operate at **S ≈ 1.5·S_min**; S_min from pinch tie line
- Solvent screens: selectivity β (must >1), distribution coefficient, capacity, density difference (needs Δρ for columns), recoverability
- Robbins chart 12-class +/−/0 for initial screen; UNIFAC to refine
- Type I ternary (one pair miscible): no extract reflux; Type II: reflux OK, sharp splits possible
- Watch solutropy (tie-line reversal) — invalidates simple stepping

## Packed/tray mass transfer (Ch 6)

- Overall resistance: 1/K_OG = 1/k_G + (KV/L)/k_L; gas-controlled (NH₃/air/H₂O): k_L term negligible; liquid-controlled (O₂, CO₂): k_G negligible
- k_L·a ∝ D_L^0.5·u_L^0.75 (penetration theory + preloading data)
- Reactive absorption: fast irreversible (NaOH) or reversible (amines, MEA/DEA); enhancement factor E; Hatta number N_Ha decides regime
- Distributors: >25 points/m² for structured packing

## Batch distillation (Ch 13)

- Rayleigh: ln(W₀/W) integration for simple stills
- Constant reflux (Smoker–Rose) vs constant composition (Bogart); slop cuts between products
- Holdup degrades sharpness; optimum reflux policy via Pontryagin/Bellman (Diwekar)

## Adsorption (Ch 15)

- Bed sizing: **L_B = LES + LUB** (never equilibrium capacity alone); LUB = MTZ/2 + safety
- Breakthrough: Klinkenberg erf / LDF models; wave velocity from isotherm slope
- Cycle choice: PSA (gas separations, fast), TSA (deep drying), displacement-purge (weakly adsorbed)
- SMB: triangle method, flow ratios mⱼ, safety β ≈ 1.05–1.2

## Membranes (Ch 14)

- Solution–diffusion: P_M = S·D (dense); porous: Knudsen/viscous regimes
- Real selectivity ≤ pressure-ratio limit α_eff ≤ p_R/p_P
- Countercurrent module > crossflow > cocurrent selectivity
- Design killers: concentration polarization, fouling, swelling (pervaporation)
- Robeson tradeoff: high permeability ⟺ low selectivity — go hybrid/cascade for purity

## Red flags (smells like trouble)

- K-values all ≈ 1 → wrong pressure or azeotrope ceiling
- γ from Wilson used to predict LLE → impossible (Wilson can't split phases)
- Single converged azeotropic-column run accepted → multiplicity likely; re-verify from multiple inits
- Gilliland used for stripping-dominated split → wrong; check with rigorous model
- Bed sized on equilibrium capacity only → breakthrough earlier than designed (MTZ ignored)
- Membrane purity promised by α alone → pressure-ratio cap ignored
- Efficiency correlation reused outside its viscosity/α range → ±30% error becomes ±100%
