# Chapter 3: Mass Transfer and Diffusion

## Core Idea
Mass transfer occurs by molecular diffusion, eddy (turbulent) diffusion, and bulk flow; all flux expressions are built from Fick's law plus a frame-of-reference correction, and practical rates are packaged as mass-transfer coefficients (k_c, k_p, k_y, k_x) tied to dimensionless groups (Sh, Sc, Re) and estimated from theory (laminar) or analogies/correlations (turbulent).

## Frameworks Introduced
- **Fick's first law (3-3a)**: `J_A = -D_AB dc_A/dz` — flux relative to molar-average velocity; analog of Fourier's law (3-2). Alternative driving forces: `J_A = -c D_AB dx_A/dz` (3-4), mass form (3-5), partial pressure (gas), activity (nonideal liquid; thermodynamic correction (3-44) with `dlnγ_A/dlnx_A`).
- **Flux decomposition / bulk flow (3-12)**: `N_A = x_A N - c D_AB (dx_A/dz)` = bulk-flow term + diffusion term. Two limiting cases:
  - **EMD (equimolar counter diffusion)**: N = 0, J_A = -J_B, linear profiles (3-18); implies D_AB = D_BA (3-23). Approaches distillation of near-ideal binaries.
  - **UMD (unimolecular diffusion through stagnant B)**: N_B = 0; `N_A = -[c D_AB/(1-x_A)] dx_A/dz` (3-27); integrated with log-mean driving force (3-33)–(3-35). The (1-x_A) factor doubles flux at equimolar composition.
- **Diffusivity estimation correlations**:
  - Gas, low P: **Fuller–Schettler–Giddings (3-36)**, D ∝ T^1.75/P with atomic diffusion volumes (Table 3.1), ~5% avg deviation. Adjust experimental values by T^1.75/P.
  - Gas, high P: **Takahashi corresponding-states chart (Fig 3.3)** for D_AB·P relative to low-pressure value.
  - Liquid, dilute: **Stokes–Einstein (3-38)** (theoretical base), **Wilke–Chang (3-39)** (solvent association factor φ_B: water 2.6, methanol 1.9, ethanol 1.5), **Hayduk–Minhas (3-40, 3-42)** (parachor-based; better for nonaqueous; double P_A and ν_A for organic-acid dimers).
  - Liquid, full composition: **Vignes equations (3-45, 3-46)** — geometric mean of infinite-dilution D's times thermodynamic correction; predicts non-linear D vs composition (often a minimum).
  - Electrolyte: **Nernst–Haskell (3-47)** from limiting ionic conductances λ±, corrected by T/334μ_B.
  - Porous solids: **effective diffusivity `D_eff = D_AB ε/τ` (3-49)** (porosity/tortuosity); mechanisms: molecular, Knudsen, surface diffusion, bulk flow.
- **Fick's second law (3-63, 3-64)**: `∂c_A/∂t = D_AB ∇²c_A`. **Semi-infinite medium solution (3-66)**: θ = erfc(z/2√(D_AB t)); surface flux (3-68) `n_A = √(D_AB/πt)·A·Δc`; **penetration depth** z = 4√(D_AB t) (θ ≈ 0.005 there). Steady-state geometries: plane wall (3-53), cylinder with log-mean area (3-55), sphere with geometric-mean area (3-57).
- **Laminar-flow solutions (theory gives k_c exactly)**:
  - **Falling laminar film**: parabolic profile (3-71), film thickness (3-74), Re_film = 4Γ/μ (3-75); general solution via parameter η (3-82) with **Schmidt number** Sc = μ/ρD_AB (3-83) and **Peclet (mass)** Pe_M = Re·Sc. Limits: Sh_avg = 3.414 (long contact, fully developed, 3-93) or Sh_avg = √(4/πη) (short contact → semi-infinite behavior, 3-104).
  - **Flat-plate boundary layer (Blasius/Pohlhausen)**: local Sh_x = 0.332 Re_x^0.5 Sc^1/3 (3-114); avg Sh = 0.664 Re_L^0.5 Sc^1/3 (3-119); δ/x = 4.96/Re_x^0.5 (3-111); **δ_c/δ = Sc^(-1/3)** (3-117); laminar up to Re_x = 5×10^5.
  - **Fully developed tube flow (Graetz/Leveque)**: entry length Le/D = 0.0575 Re (3-121); Sh_x → 3.656 (fully developed) or Leveque `Sh_x = 1.077[Pe_M/(x/D)]^(1/3)` (3-130); Hausen average (3-132). Patch limiting solutions (Churchill–Usagi) when no closed form exists.
- **Turbulent flow — analogies**:
  - Eddy diffusivity form (3-135, 3-138): `N_A = -(D_AB + ε_D) dc_A/dz`; approximate ε_M = ε_H = ε_D.
  - **Reynolds analogy (3-144)**: f/2 = St_H = St_M — valid only for Pr = Sc = 1; rarely useful.
  - **Chilton–Colburn analogy (3-147)**: `j_M = f/2 = j_H = (h/GC_P)Pr^(2/3) = j_D = (k_c ρ/G)Sc^(2/3)`; j-factor correlations for tube (3-148, 0.023Re^-0.2), flat plate (3-149), cylinder (3-150/151), sphere (3-152), packed bed (3-153). Valid Pr, Sc ≈ 0.5–10; **fails at high Sc/Pr**.
  - **Friend–Metzner (3-154/155)** for high Sc/Pr (up to 3000); **Churchill–Zajic (3-157, 3-158)** most accurate for smooth tubes up to Re = 10^8 — recommended via heat/mass analogy (Sh ↔ Nu, Sc ↔ Pr).
- **Fluid–fluid interface models**:
  - **Film theory (Nernst, 1904)**: all resistance in a stagnant film of thickness δ: `N_A = (D_AB/δ)(c_I - c_b)` (3-163), or with bulk flow `c D_AB/[δ(1-x_A)_LM]·Δx` (3-164). Predicts k_c ∝ D_AB (data say D^0.5–0.75); still widely used in design because δ is absorbed into empirical k_c.
  - **Penetration theory (Higbie, 1935)**: eddies sit at interface for fixed contact time t_c; unsteady diffusion into semi-infinite medium → `k_c = 2√(D_AB/πt_c)` (3-169), k_c ∝ D^0.5. Good for bubbles (t_c = d_bubble/u_rise), sprays, packing (t_c ≈ 1 s per packing piece).
  - **Surface-renewal theory (Danckwerts, 1951)**: residence-time distribution φ{t} = s·e^(-st) (3-173); `k_c = √(D_AB·s)` (3-178); same D^0.5 dependence; s = fractional renewal rate (as elusive as t_c). Toor–Marchello film-penetration theory unifies all three.
- **Two-film theory (Whitman, 1923)**: two films in series, equilibrium at interface (c_A_I = H_A p_A_I). Overall coefficients: `1/K_L = H_A/k_p + 1/k_c` (3-187); `1/K_G = 1/k_p + 1/(H_A k_c)` (3-191); mole-fraction versions (3-198/199) with K-value. Resistance ratios H_A/k_p vs 1/k_c identify the controlling phase → pick K_L or K_G accordingly. Large driving forces / curved equilibrium line: replace K_A by local slopes m_x, m_y (3-215/216). UMD correction: `k' = k/(y_B)_LM` or `(x_B)_LM` (3-202/203). Liquid–liquid: use K_D (distribution ratio) instead of K-value (3-204–206).

## Key Concepts
- **Diffusivity (D_AB)**: mutual/binary diffusion coefficient; magnitude ladder ≈ 10^-1 (gas), 10^-5 (liquid), 10^-9 cm²/s (amorphous solid). Liquids diffuse ~10^5× slower per unit D, but only ~10^2× slower in rate because liquid molar density is ~10^3× gas.
- **Flux N_i vs J_i**: total flux (stationary coordinates) = bulk-flow term + diffusion flux (molar-average frame); v_i = v_M + v_iD (3-9 to 3-11).
- **Bulk-flow effect**: factor 1/(1-x_A) in UMD; negligible when dilute.
- **(1-x_A)_LM / (x_B)_LM**: log-mean inert fraction — the correct driving-force normalizer for UMD.
- **Schmidt number Sc = μ/ρD_AB** (momentum/mass diffusivity ratio; analog of Prandtl); **Sherwood number Sh = k_c L/D_AB** (analog of Nusselt); **Pe_M = Re·Sc** (convective/molecular mass transport).
- **Penetration depth** 4√(D_AB t): thickness actually penetrated by diffusion; valid approximation for finite media thicker than this.
- **Contact time t_c (Higbie)** and **fractional renewal rate s (Danckwerts)**: the fitted parameters of unsteady interfacial models.
- **Film thickness δ**: fictitious stagnant-layer thickness giving the same resistance; D_AB/δ ≡ k_c.
- **j-factor (j_D = St_M·Sc^(2/3))**: Colburn's normalized transport coefficient for analogy use.
- **Eddy diffusivity ε_D**: turbulent contribution, position- and velocity-dependent, not a fluid property.
- **Marangoni effect**: interfacial-tension gradients create interfacial turbulence (raises k) or, with surfactants, an interfacial resistance (lowers k) — violates the equilibrium-at-interface assumption.

## Mental Models
- **Use Fick's first law + geometry when medium is stagnant or laminar** — rates are computable from first principles; pick EMD vs UMD by whether bulk flow exists (distillation vs absorption/evaporation).
- **Use D ∝ T^1.75/P scaling when adjusting a known gas diffusivity**; use correlations (Fuller, Wilke–Chang, Hayduk–Minhas, Nernst–Haskell) only when measurement is unavailable — solids must be measured.
- **Use Sherwood-number correlations via the Chilton–Colburn analogy when flow is turbulent and Sc is moderate**; switch to Friend–Metzner or Churchill–Zajic at high Sc (viscous liquids) or very high Re.
- **Use penetration/surface-renewal thinking when turbulence persists to the interface** (bubbles, drops, packing); the k_c ∝ D^0.5 exponent is the experimental lower bound, film theory's D^1.0 the upper.
- **Use two-film + overall coefficient (resistances in series) for any design involving two contacting fluids**: compute H_A/k_p and 1/k_c, identify the controlling resistance, choose the matching K.

## Anti-patterns
- **Applying the Reynolds analogy outside Pr = Sc = 1**: predicts St_M = f/2, grossly overpredicting k_c for liquids (Sc ~ 10^3); use Chilton–Colburn or better.
- **Using Chilton–Colburn at high Schmidt/Prandtl numbers**: deviates 30–70% vs Churchill–Zajic for Pr ≳ 1000; the constant 0.8 exponent on Re also fails at extreme Re.
- **Assuming liquid diffusivity is composition-independent or linear in x**: Vignes analysis shows strong nonlinearity (e.g., methanol–water minimum at x = 0.3, ~40% below linear interpolation); use infinite-dilution values + activity corrections.
- **Ignoring the bulk-flow term in UMD at nondilute compositions**: flux error up to 2× at x_A = 0.5; use k' = k/(x_B)_LM when film-controlled and nondilute.
- **Treating film-theory δ as physical or k_c ∝ D_AB as exact**: δ is a fitting fiction; experimental k_c scales as D^0.5–0.75.
- **Assuming equilibrium at the interface blindly**: Marangoni interfacial turbulence or surfactant films can add/remove interfacial resistance.
- **Letting a semi-infinite solution run past the penetration depth**: (3-66) applies to finite media only while thickness > 4√(D_AB t).

## Reference Tables
| System | Correlation | Form / inputs | When to use |
|---|---|---|---|
| Binary gas, low P | Fuller et al. (3-36) | T^1.75/P, atomic diffusion volumes ΣV | Default estimate; ~5% avg error, 195–1068 K |
| Binary gas, high P | Takahashi chart (Fig 3.3) | Tr, Pr, low-P D·P | Supercritical / compressed gases; D drops sharply |
| Dilute liquid | Wilke–Chang (3-39) | T, μ_B, ν_A, φ_B | Quick aqueous + organic estimates, small solutes |
| Dilute liquid | Hayduk–Minhas (3-40, 3-42) | parachor P, ν, μ_B | Better for nonaqueous; paraffin–paraffin (3-40), general (3-42); μ_B < 30 cP; double acid parachor (dimer) |
| Full-range liquid | Vignes (3-45/46) | (D_AB)_∞, (D_BA)_∞, γ(x) | Nonideal binaries; combine with UNIFAC/γ data |
| Electrolyte (aq.) | Nernst–Haskell (3-47) | λ± (Table 3.7), valences | Dilute salts/acids/bases; correct λ by T/334μ_B |
| Porous solid | D_eff = D_AB ε/τ (3-49) | porosity ε (~0.5), tortuosity τ (1–3) | Molecular diffusion dominates in pores (Knudsen when mean free path ≳ pore d) |
| Nonporous polymer | c = S·P (3-48) + Fick's law | solubility S, D in polymer | Membrane permeation (solution–diffusion) |

Typical D_AB (cm²/s): gas 0.1–1; liquid 10^-6–10^-4; amorphous solid ~10^-9.

## Worked Example
**Example 3.2 — Evaporation of benzene from an open beaker (UMD):**
- Given: beaker 6 cm tall, benzene 0.5 cm below rim, 25 °C, 1 atm, dry air across mouth; P_A^s = 0.131 atm, D_AB = 0.0905 cm²/s, SG = 0.874.
- Theory: stagnant air layer → UMD, N_B = 0. x_A1 = 0.131 at interface (Raoult), x_A2 = 0 at top; (1-x_A)_LM = 0.131/ln[(1)/(0.869)] = 0.933. Flux from (3-35): N_A = (c D_AB/Δz)·Δx/(x_B)_LM = (4.09×10^-5)(0.0905)/0.5 · (0.131/0.933) = **1.04×10^-6 mol/cm²·s**. Profile (3-32): x_A = 1 - 0.869·exp(0.281z) — slightly curved (nonlinear) because of bulk flow; molecular diffusion and bulk-flow fluxes are equal/opposite for B, confirming N_B = 0. Time to drop 2 cm: integrate N_A = (ρ_L/M_L)(dz/dt) → t = 21,530 × 3 cm² = **64,590 s ≈ 18 h** — slow because no turbulence; agitation would collapse this.

## Key Takeaways
1. All fluxes decompose as bulk flow + Fickian diffusion (3-12); choosing EMD vs UMD sets the whole calculation. EMD → linear profiles; UMD → exponential profiles and log-mean correction.
2. Diffusivity spans ~8 orders of magnitude (gas → solid), but rates differ less because c·D governs the flux for a given mole-fraction gradient.
3. Diffusion in liquids/solids is so slow that separations depend on agitation (turbulence/eddies) or on reducing particle size — never on molecular diffusion alone at scale.
4. Mass-transfer coefficients are framed by dimensionless groups: Sh = k_c L/D_AB, correlated against Re and Sc; laminar cases (film, plate, tube) have exact theoretical solutions with limiting Sh values (3.414 film; 3.656 tube; 0.664Re^0.5Sc^1/3 plate).
5. The Chilton–Colburn j-factor analogy (j_D = f/2·Sc-correction) is the workhorse for turbulent k_c; at high Sc or Re use Friend–Metzner or Churchill–Zajic instead.
6. Interfacial models bracket reality: film theory k_c ∝ D^1.0 (upper), penetration/surface-renewal k_c ∝ D^0.5 (lower); data fall at D^0.5–0.75. Their parameters (δ, t_c, s) are fitted, not predicted.
7. Two-film theory reduces a two-phase problem to resistances in series with interfacial equilibrium; identify the controlling phase via 1/K = H/k_p + 1/k_c — this structure carries into all packed/contacting-device design.

## Connects To
- **Ch 2**: phase equilibria (Henry's law, K-values, Raoult's law) supply the interfacial-concentration anchors used in every two-film calculation here.
- **Ch 6 (Absorption/Stripping)**: applies film/penetration theory and K_L, K_G, and volumetric coefficients K_y·a to packed-column design.
- **Ch 7 (Distillation)**: EMD is the vapor-film limit in trays/packing; stage efficiencies depend on these coefficients.
- **Ch 8 (Liquid–Liquid Extraction)**: two-liquid-film theory with distribution coefficient K_D (3-204–206).
- **Ch 14 (Membranes)**: solution–diffusion through nonporous polymers (c = SP, 3-48) and porous-membrane D_eff (3-49).
- **Ch 15 (Adsorption)**: diffusion in porous adsorbent pores (Knudsen, surface diffusion, D_eff).
- **Ch 17/18 (homogeneous/heterogeneous reactions)**: penetration-theory contact times and D_eff set reaction–mass-transfer interplay (Damköhler-type limits) in catalytic reactors.
