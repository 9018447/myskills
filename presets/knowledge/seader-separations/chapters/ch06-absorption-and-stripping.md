# Chapter 6: Absorption and Stripping

## Core Idea
Absorption selectively transfers solutes from a gas into a liquid absorbent; stripping (desorption) reverses it. Design reduces to (1) an equilibrium/operating-line framework (graphical or Kremser algebraic) for stages and (2) a rate-based HTU-NTU / HETP framework for packed height — with hydraulic correlations (flooding, loading, pressure drop) fixing the diameter for both trayed and packed columns.

## Frameworks Introduced

- **Graphical McCabe-Thiele-style method for absorption/stripping (§6.3)**: On a Y–X plot (mole ratios, solute-free flows L′, V′), draw the equilibrium curve (Eq. 6-1) and the operating line (Eq. 6-3 absorber / 6-5 stripper, slope L′/V′); step off stages.
  - When to use: dilute, essentially isothermal, single-solute systems; absorber stages numbered top-down, stripper bottom-down. Absorber operating line sits above the equilibrium curve (driving force for absorption); stripper line sits below. Cannot cross the equilibrium line — that violates the second law (pinch at L′_min).

- **Minimum absorbent / stripping-agent flow (§6.3.3)**: L′_min corresponds to X_N in equilibrium with Y_N+1 at the pinch (infinite stages). Dilute cases: (6-10), and with pure absorbent, **L′_min = V′K_N(fraction absorbed)** (Eq. 6-11); stripper analog **V′_min = (L′/K_N)(fraction stripped)** (Eq. 6-12).
  - How: operate at 1.1–2× L′_min (≈1.5× typical); optimal stripping factor S ≈ 1.4. Fundamental stages-vs-solvent trade-off.

- **Kremser group method (§6.4, Eqs. 6-29, 6-31)**: relates fraction not absorbed to average absorption factor **𝒜 = L/KV** (6-18): φ_A = (𝒜_e − 1)/(𝒜_e^(N+1) − 1); stripping analog with **𝒮 = KV/L = 1/𝒜** (6-32). Edmister plot (Fig. 6.15) gives any third variable given two of (φ, 𝒜_e, N).
  - When to use: multicomponent dilute absorption/stripping, single-section countercurrent cascades; great for initializing rigorous simulators. Component appearing in both entering vapor and liquid: v₁ = v_{N+1}φ_A + l₀(1−φ_S) (6-35). Key behavior: components with 𝒜 > 1.4 absorb easily (more stages pay off); for 𝒜 < 0.5, max fraction absorbed ≈ 𝒜 itself — extra stages do nothing.

- **K-value selection for dilute systems (6-37 to 6-40)**: Raoult's law (ideal, subcritical); modified Raoult's law K = γP^s/P (nonideal, γ at infinite dilution — e.g. acetone in water, γ ≈ 6.7); Henry's law K = H/P (supercritical solutes, O₂/N₂/CO₂); solubility form K = P^s/(x^s P) (sparingly soluble, subcritical).

- **Stage efficiency and column height for trayed columns (§6.5)**: Overall efficiency E_o = N_t/N_a (6-41). **Drickamer–Bradford** correlation (6-42): E_o = 19.2 − 57.8 log μ_L (%, cP; hydrocarbon oils only). **O'Connell** correlation (6-43, Fig. 6.19): E_o vs parameter K·M_L·μ_L/ρ_L — handles solubility variation; longer liquid flow paths raise efficiency (multipass trays prevent hydraulic gradients). **Murphree vapor efficiency** E_MV = (y_{n+1} − y_n)/(y_{n+1} − y_n*) = 1 − e^(−N_OG) (6-49); point efficiency E_OV (6-51); Gerster partial-mixing model with Peclet number (6-54); Lewis relation E_o vs E_MV with λ = mV/L (6-56). **Oldershaw column** (1–2 in glass sieve-tray) scale-up: measure point efficiency at ~60% flooding, correct for mixing.
  - Why absorber efficiencies are low: high K (low solubility) and viscous oil absorbents — often < 50%, sometimes ~10%.

- **Tray hydraulics: flooding and diameter (§6.6)**: Two flooding mechanisms — **entrainment (jet) flooding** at high vapor rate (usually the design limit) and **downcomer (choke) flooding** at high liquid rate (critical at high P; rarely dominant if A_d/A ≥ 0.1 and spacing ≥ 24 in). Weeping at low vapor rate sets turndown. **Souders–Brown** droplet-settling model (6-60): u_f = C[(ρ_L−ρ_V)/ρ_V]^0.5; **Fair correlation** (Fig. 6.27) gives C_F vs F_LV kinetic-energy ratio (6-97), corrected C = F_ST·F_F·F_HA·C_F (6-61); diameter from (6-63) at f ≈ 0.80 of flooding. Stupin–Kister ultimate capacity (6-64 to 6-67) — design-independent ceiling.

- **Rate-based packed-column design: HTU–NTU (§6.7)**: HETP = l_T/N_t (6-68) — no theoretical basis; better: l_T = **H_OG·N_OG** (6-84, Chilton–Colburn), H_OG = V/(K_y a A_T) (6-85), N_OG = ∫dy/(y−y*) (6-86), Colburn's closed form (6-88) with absorption factor 𝒜. Two-film resistances: 1/K_y a = 1/k_y a + K/k_x a (6-79); H_OG = H_G + (KV/L)H_L (6-110). NTU ≠ N_t unless operating and equilibrium lines are straight and parallel; conversions (6-89)/(6-90).
  - When to use: gas-film-controlled systems (soluble solutes like NH₃) → use K_y a; liquid-film-controlled (slightly soluble: CO₂, O₂) → K_x a; sensitive when 𝒜 < 0.9.

- **Packed-column hydraulics: holdup, loading, flooding, ΔP (§6.8)**: **Billet–Schultes** liquid holdup h_L = (12·Fr_L/Re_L)^(1/3)·(a_h/a)^(2/3) (6-92) with Re_L (6-93), Fr_L (6-94), hydraulic-area ratios (6-95/6-96). Below the **loading point** (~70% of flooding velocity), holdup is independent of gas rate; between loading and flooding, operation is unstable — design in the preloading region at 50–70% of flooding. **Sherwood–Shipley–Holloway** F_LV kinetic-energy ratio; **GPDC charts** (Strigle Fig. 6.36 random, Kister–Gill Fig. 6.37 structured) with capacity factor F_C (6-98); Kister–Gill flooding ΔP: **ΔP_flood = 0.115 F_P^0.7** in H₂O/ft (6-99). Diameter from (6-100). Billet–Schultes HTU correlations (6-119 H_L, 6-120 H_G) with packing constants C_h, C_L, C_V and interfacial-area ratio a_ph/a (6-123). HETP rules of thumb (6-101 to 6-103): ≈1.5·D_P(in) for random packing; 100/a + 4/12 ft for structured.

- **Reactive (chemical) absorption (§6.9)**: Irreversible (CO₂ + NaOH) vs reversible (CO₂/H₂S + MEA/DEA amines, regenerable). Reaction enhances rate by cutting liquid-film resistance: rate expression (6-130) with **enhancement factor E** as function of **Hatta number** N_Ha = (D_A k c_B)^0.5/k_L (6-131) and E_i (6-132). Instantaneous reaction ⇒ liquid interfacial concentration of A is zero ⇒ gas-film controlled (6-129), equilibrium curve collapses to zero slope, N_OG = ln(p_in/p_out) (6-133).

## Key Concepts
- **Absorption factor 𝒜 = L/KV** (6-18) — component's ease of absorption; **stripping factor 𝒮 = KV/L** (6-32); both ≈1.4 optimal (practical design point).
- **Operating line vs equilibrium curve**: passing streams vs leaving streams; pinch at L_min.
- **Rich/lean solvent**: solute-loaded liquid leaving an absorber (rich oil) vs regenerated absorbent returning (lean oil).
- **Theoretical stage, overall efficiency E_o, Murphree tray (E_MV) and point (E_OV) efficiencies** — efficiency ladder from point → tray → overall (6-41, 6-49, 6-51, 6-56).
- **HETP/HETS vs HTU/NTU**: stage-equivalent height vs transfer-unit height; equal only for straight parallel lines (6-89/6-90).
- **Loading point vs flooding point**: gas begins hindering liquid flow (holdup rises, instability) vs liquid becomes continuous (column dumps). Loading ≈ 70% of flooding velocity.
- **Turndown ratio**: max/min vapor capacity — bubble-cap ≈ 5, valve ≈ 4, sieve ≈ 2.
- **Souders–Brown C-factor / Fair correlation / F_LV kinetic-energy ratio** — tray sizing language.
- **Packing factor F_P, F-factor F_V = u_V(ρ_V)^0.5** — packed-column capacity language.
- **Enhancement factor E, Hatta number** — reactive absorption language.

## Mental Models
- **Absorbers want high P, low T; strippers want low P, high T** — but compression, refrigeration, and vacuum cost money, so most absorbers run at feed-gas pressure/ambient T and strippers just above ambient. Check phase changes with bubble/dew points.
- **Stages vs solvent trade-off**: every design sits between infinite solvent (zero stages) and infinite stages (L_min); 1.5× L_min is the customary working point. Same logic for stripper gas rate at S ≈ 1.4.
- **Which film controls?** Low K (very soluble: NH₃, HCl, ethanol in water) → gas-film controlled, use H_OG; high K (slightly soluble: CO₂, O₂, SO₂ at K=40) → liquid-film controlled, use H_OL. Trays are usually liquid-phase-limiting; packed beds gas-phase-limiting.
- **Two ways to get column height**: equilibrium stages × efficiency / tray spacing (trays) vs N_OG × H_OG or N_t × HETP (packing) — the equilibrium-line/operating-line geometry is identical either way.

## Anti-patterns
- **Designing a trayed column at >80% of flooding**: entrainment (e) grows rapidly; keep e < 10% of L; leave margin for load swings.
- **Operating a packed column in the loading region**: unstable operation, sharp pressure-drop rise; stay at or below the loading point (50–70% of flooding).
- **Exceeding pressure-drop limits**: keep packed ΔP below ~2 in H₂O/ft; tray ΔP ≤ ~0.15 psi at high pressure (0.05 psi vacuum).
- **Applying Drickamer–Bradford outside its range**: valid only for hydrocarbon oils, 0.2 < μ_L < 1.6 cP; use O'Connell when K-values span a wide solubility range.
- **Using structured packing at >200 psia or >10 gpm/ft²**: HETP degrades badly; pick trays (Kister's caution).
- **Ignoring liquid maldistribution**: packed sections > ~20 ft (6 m) between redistributors channel to the wall and blow up HETP; also nominal packing size must be < 1/8 column diameter.
- **Believing HETP is theory**: it has no theoretical basis; prefer H_OG·N_OG from Billet–Schultes when possible, and use HETP only with back-calculated/vendor data.
- **Letting Kremser carry concentrated systems**: it assumes constant molar flows and per-stage-constant K; for concentrated mixtures or reversible-reaction absorption use a process simulator (Ch. 10/12).

## Reference Tables

| Method | Use when | Output |
|---|---|---|
| Graphical Y–X stepping (§6.3) | 1–2 solutes, dilute, isothermal; need insight | N stages, L_min |
| Kremser equations (6-29/6-31) | multicomponent dilute, N fixed or recovery fixed | φ_A/φ_S per component |
| HTU–NTU (6-84 to 6-88) | packed column, rate data/correlations available | packed height l_T |
| HETP (6-68, 6-101–6-103) | quick packed estimate, vendor data | packed height |
| Murphree/O'Connell (6-43, 6-49–6-56) | tray efficiency | E_o, N_a |

| Equipment | Prefer | Notes |
|---|---|---|
| Sieve trays | lowest cost, highest capacity | turndown only ~2 |
| Valve trays | flexibility needed | turndown ~4, best efficiency/cost compromise |
| Bubble-cap | residence time for reaction; no weeping | obsolete otherwise |
| Random packing | D < 2 ft, corrosive, foaming, high liquid rates | reload redistributors every ~20 ft |
| Structured packing | vacuum / low ΔP, revamps | avoid >200 psia, >10 gpm/ft² |

## Worked Example
**Ethanol recovery from CO₂ with water (Examples 6.1/6.2).** Given: 180 kmol/h gas, 2 mol% ethanol, 30 °C, 110 kPa; pure-water absorbent; 97% recovery; K = γP^s/P = (6)(10.5)/110 = 0.57.
- **Minimum absorbent** (Eq. 6-11): L′_min = V′K(fraction absorbed) = 176.4 × 0.57 × 0.97 ≈ 97.5–99.5 kmol/h; run at 1.5× → L ≈ 146–149 kmol/h, giving 𝒜_e = L/KV = 1.45.
- **Stages** (Kremser, 6-29): φ_A = 0.03 = (1.45 − 1)/(1.45^(N+1) − 1) → **N = 6.46** (graphical stepping gives ~6.1).
- **Packed height** (6-84): N_OG from (6-88) = 7.5 transfer units; with H_OG = 2.0 ft (1.5-in Pall rings) → l_T = 15 ft; via Billet–Schultes H_OG = H_G + (KV/L)H_L = 3.37 + 0.69(1.01) = 4.07 ft → l_T ≈ 30.5 ft, HETP ≈ 4.9 ft.
- **Tray column**: O'Connell parameter K·M_L·μ_L/ρ_L = 2(18)(0.89)/62.2 = 0.52 → E_o ≈ 44% → ~28 actual trays; Fair flooding check gives D_T ≈ 2.7 ft at 80% flooding.

## Key Takeaways
1. Absorption factor 𝒜 = L/KV (stripping factor 𝒮 = KV/L) is the single number that governs recovery; design near 1.4, remember the ceiling (1 − φ_A)_max = 𝒜 for 𝒜 < 1.
2. L_min is set by a pinch at the rich end (X_N in equilibrium with feed gas Y_N+1); operate 1.1–2× L_min — there is always an optimal stages-vs-solvent trade-off.
3. Absorber efficiencies are low (10–50%, driven by K and liquid viscosity — O'Connell correlation); never assume equilibrium trays.
4. Size trays from entrainment flooding (Souders–Brown C-factor + Fair correlation, design at f ≈ 0.8); check weeping for turndown and downcomer backup at high pressure.
5. Size packing from l_T = H_OG·N_OG (theoretically grounded) or N_t·HETP (pragmatic); they agree only for straight parallel lines — convert with (6-89)/(6-90).
6. Operate packed columns in the preloading region (50–70% of flooding); the loading point is ~70% of flooding and ΔP_flood ≈ 0.115 F_P^0.7 in H₂O/ft.
7. Chemical absorption (amines, caustic) raises capacity and rate via the enhancement factor E (Hatta number); irreversible reactions give gas-film control and a zero-slope equilibrium curve; reversible amine systems enable absorbent recycle and are the basis of carbon capture.

## Connects To
- **Ch 2**: K-values from Raoult / modified Raoult / Henry's law (6-37–6-40) feed directly into absorption factors.
- **Ch 3**: two-film theory, volumetric mass-transfer coefficients (k_y a, k_L a), penetration theory (Billet–Schultes H_L, H_G), Table 6.5 groupings.
- **Ch 4**: Henry's law constants (Fig. 4.18) for supercritical solutes (CO₂, O₂, N₂).
- **Ch 5**: single-section cascade degrees of freedom and countercurrent cascade structure reused for absorbers/strippers.
- **Ch 7**: the same tray efficiency, flooding, and GPDC machinery applied to distillation; Oldershaw scale-up and multipass-tray rules shared.
- **Ch 10/12**: rigorous simulator treatment of concentrated systems, reversible reactive absorption (amine treating), and multicomponent mass-transfer coupling (negative Murphree efficiencies).
