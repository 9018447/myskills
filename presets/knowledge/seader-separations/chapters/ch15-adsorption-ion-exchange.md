# Chapter 15: Adsorption, Ion Exchange, and Chromatography

## Core Idea
All three operations exploit a solid sorbent (adsorbent, ion-exchange resin, or chromatographic stationary phase) that preferentially holds solutes, with design hinging on (1) the equilibrium isotherm (how much a solute loads at a given fluid concentration) and (2) mass-transfer rates that smear the ideal sharp front into a mass-transfer zone — so real fixed-bed capacity is always less than equilibrium capacity.

## Frameworks Introduced
- **Adsorbent characterization (Table 15.2, BET method)**: specific surface area S_g via N2 adsorption at -195.8°C (BET equation, 15-6 to 15-8); pore volume by He/Hg displacement (15-9); pore-size distribution by Hg porosimetry (>100 Å, Kelvin-equation N2 desorption 15–250 Å, molecular sieving <15 Å). IUPAC: micropore <20 Å, mesopore 20–500 Å, macropore >500 Å. Capacity relates more to pore *volume* than surface area.
  - When to use: screening/selecting adsorbents and predicting monolayer vs capillary-condensation behavior.
- **Adsorption isotherms**: linear (q = kp), Freundlich (q = kp^(1/n), n between 1 and 5, no saturation limit), Langmuir (q = Kq_m p/(1+Kp), Type I with asymptote q_m), three-parameter Toth and UNILAN; Brunauer's five isotherm types (I/II desirable; III/IV/V involve capillary condensation and hysteresis). Mixture forms: extended-Langmuir (Markham–Benton, 15-32) and Langmuir–Freundlich (Yon–Turnock, 15-33) — both "constant-selectivity"/nonstoichiometric; IAS theory (Myers–Prausnitz) is more accurate but iterative. Liquid-phase versions use concentration (15-35, 15-36); full-range binary-liquid data give composite isotherms (surface excess, Kipling).
  - When to use: fit pure-component data first; choose Langmuir vs Freundlich by whether data plateau at high pressure; use extended forms for mixtures, IAS when accuracy matters.
- **Fixed-bed breakthrough framework**: ideal stoichiometric front with LES/LUB (length of equilibrium/unused bed section) and WES/WUB; nonideal S-shaped breakthrough curve with MTZ (mass-transfer zone, bounded by c/c_F = 0.05 and 0.95), breakthrough time t_b and stoichiometric time t_e. Wave-front velocity u_c = u/[1 + ((1-ε_b)/ε_b)(dq/dc)] (15-109) — isotherm shape controls front sharpening or broadening.
  - How: LDF model (Glueckauf–Coates, 15-99/15-100) + Klinkenberg erf-based solution (15-101) for computed breakthrough curves; Collins constant-pattern scale-up L_B = LES + LUB from lab breakthrough data.
- **PSA/TSA/VSA cycles**: TSA (heat/cool bed, purge desorption; cycle hours–days; best for dilute contaminants/purification), PSA/VSA (pressure swing; cycle seconds–minutes; best for bulk gas separations; Skarstrom two-bed cycle with pressurization/adsorption/blowdown/purge; cyclic steady state may need tens–hundreds of cycles), plus inert-purge swing and displacement-purge; Purasiv fluidized-bed adsorption + moving-bed desorption.
  - When to use: TSA for purification with cheap heat and condensable adsorbates; PSA/VSA for air separation (zeolite = equilibrium control favors N2; carbon molecular sieve = kinetic control, O2 diffuses ~25x faster → N2 product).
- **Simulated moving bed (SMB / Sorbex)**: four-section TMB idealization (I desorb A, II desorb B, III adsorb A, IV adsorb B) with port switching; triangle method with flow-rate ratios m_j = Q_j/Q_S and safety margin β (√(K_A/K_B) ≥ β ≥ 1, pick β ≈ 1.05); TMB→SMB conversion (15-163) and switching time t* = L_k/u_s.
  - When to use: bulk liquid separations (p-xylene from C8 aromatics, fructose/glucose, n-paraffins) needing near-binary splits in one device.
- **Ion exchange**: stoichiometric exchange on equivalent basis, molar selectivity coefficient K_A,B by law of mass action (15-38/15-44) and Bonner–Smith relative selectivities (Table 15.5/15.6); favorable loading requires (Q/C)K >> 1; regeneration uses concentrated salt to reverse it. Four-step cycle: loading, displacement, regeneration, washing.
- **Chromatography (elution) theory**: solute pulse waves at u_i = u/[1+((1-ε_b)/ε_b)K_i]; equilibrium square pulses vs rate-based Gaussian peaks; Carta's LDF analytical solution (15-175) for periodic rectangular pulses; band overlap fixed by lengthening column or shortening feed pulse.

## Key Concepts
- **Equilibrium capacity / loading q**: amount adsorbed per mass adsorbent, set by the isotherm at feed conditions.
- **Breakthrough**: rise of c_out/c_F past a set limit (e.g., 0.05) at time t_b; operation must stop and regenerate.
- **MTZ (mass-transfer zone / MTZ width)**: bed region between saturated and fresh adsorbent where all adsorption occurs; wider MTZ = less capacity used.
- **LUB / LES**: length of unused bed (wasted length, ≈ MTZ/2 under constant-pattern) plus length of equilibrium section; L_B = LES + LUB (15-110).
- **LDF model**: ∂q̄/∂t = k(q* − q̄) with 1/kK = R_p/3k_c + R_p²/15D_e — combines film + pore resistance.
- **Constant-pattern front (CPF)**: self-sharpening front from a favorable (Type I) isotherm; enables Collins scale-up.
- **Regeneration**: TSA (hot purge), PSA/VSA (pressure swing), inert-purge, displacement-purge; delta loading = usable cyclic capacity left after incomplete desorption.
- **Cation/anion exchanger, selectivity coefficient**: strong-acid (–SO3–) / strong-base resins; exchange on equivalents; K_i from Table 15.5/15.6.
- **Effective diffusivity D_e**: pore + Knudsen + surface diffusion, (15-74); surface diffusion can dominate for strongly adsorbed species.
- **Resolution / band overlap**: solute wave-velocity differences set minimum column length; mass transfer broadens pulses into Gaussian peaks that may overlap.

## Mental Models
- **Wave-front picture**: adsorption in a fixed bed is a concentration wave traveling far slower than the fluid (u_c/u ~ 0.0002 for a strongly adsorbed trace); everything upstream of the front is spent, downstream is fresh. Design = predicting where the front is when breakthrough occurs.
- **Equilibrium sets the ceiling, rates set the penalty**: the isotherm gives ideal (stoichiometric) capacity; mass-transfer resistance converts some of that into unusable LUB. Bigger beds recover most of it (62% → 82% utilization going from 6 ft to 30 ft in Ex. 15.11).
- **Isotherm shape = front shape**: favorable (Langmuir/Freundlich) isotherms self-sharpen fronts to constant pattern; linear or unfavorable isotherms broaden without limit — this decides whether simple scale-up methods work.
- **Swing the operating variable the solute loves**: temperature or pressure is cycled to make loading high during adsorption and low during desorption; TSA trades time for heat, PSA trades mechanical work for speed.

## Anti-patterns
- **Sizing the bed by equilibrium capacity alone**: ignoring MTZ/LUB means breakthrough arrives well before the "ideal" time (Ex. 15.11: 97 min vs 155 min ideal); always add LUB from real or Klinkenberg-based breakthrough data.
- **Assuming local equilibrium / plug flow everywhere**: axial dispersion (low flow, shallow beds) and internal diffusion can dominate; LUB grows if you ignore them.
- **Using Langmuir/Freundlich blindly for mixtures**: extended forms are nonstoichiometric and not thermodynamically consistent (Broughton); expect deviations (Ex. 15.6: −29% on one component) — use IAS theory or multicomponent data when accuracy matters.
- **Down-flow regeneration mirroring down-flow adsorption**: desorbed solute re-adsorbs in the clean section; regenerate counter-current (upward) so the unused portion never sees desorbate.
- **Ignoring cyclic steady state in PSA**: incomplete regeneration compounds over cycles; tens–hundreds of cycles may pass before the loading profile stabilizes — single-cycle clean-bed calculations mislead.
- **Applying Klinkenberg's closed-form equations to desorption**: they assume a clean, uniformly loaded initial bed; desorption starts from the nonuniform end-of-adsorption profile and needs the method of lines (stiff ODE solver, e.g., ode15s).
- **Assuming ion-exchange rate is reaction-controlled**: usually film- or particle-diffusion controlled (external <0.01 N, internal >1.0 N); resin cross-linking and ion charge set gel diffusivities orders of magnitude below liquid values.

## Reference Tables
**Isotherm equations (gas p or liquid c):**

| Isotherm | Equation | Use when |
|---|---|---|
| Linear | q = kp (15-16) | Low loading (<25 cm³/g), trace solutes, Henry's-law region |
| Freundlich | q = kp^(1/n), 1≤n≤5 (15-19) | No plateau in data; heterogeneous surface; empirical fit |
| Langmuir | q = Kq_m p/(1+Kp) (15-24) | Data plateau at q_m (Type I); monolayer; mass-action basis |
| Toth | q = mp/(b+p^t)^(1/t) (15-26) | 3-parameter fit, reduces to Langmuir at t=1 |
| UNILAN | q = (n/2s)ln[(c+pe^s)/(c+pe^-s)] (15-27) | 3-parameter fit, reduces to Langmuir at s=0 |
| Extended-Langmuir (mixture) | q_i = (q_i)_m K_i p_i/(1+ΣK_j p_j) (15-32) | Nonpolar mixtures; constant selectivity; simple, not rigorous |
| BET | P/[v(P0−P)] linear plot (15-6) | Measuring S_g by N2 adsorption, multilayer regions |

**Adsorbent selection (Table 15.2 highlights):**

| Adsorbent | Character | d_p (Å) | S_g (m²/g) | Best for |
|---|---|---|---|---|
| Activated alumina | Hydrophilic, amorphous | 10–75 | ~320 | Drying gases/liquids to <1 ppm H2O |
| Silica gel (small pore) | Hydrophilic | 22–26 | 750–850 | Water + polar removal |
| Activated carbon | Hydrophobic | 10–25 | 400–1200 | Nonpolar/weakly polar organics; easy regeneration (low heat of adsorption) |
| Molecular-sieve carbon | Hydrophobic | 2–10 | ~400 | Kinetic air separation (N2 product) |
| Zeolite molecular sieves (3A/4A/5A/10X/13X) | Polar-hydrophilic, crystalline, uniform apertures 2.9–8.4 Å | 3–10 | 600–700 | Size/shape + polarity selectivity; drying, CO2 removal, air separation, n-paraffins |
| Polymeric adsorbents | Tunable hydrophilic→hydrophobic | 30–400 | 50–700 | Organics from water; solvent-leachable regeneration |

**Regeneration cycle selection:**

| Cycle | Swing | Cycle time | Feed phase | Application |
|---|---|---|---|---|
| TSA | Temperature (heat + purge) | Hours–days | Gas or liquid | Purification, dilute contaminants |
| PSA | Pressure (high ads / ambient des) | Seconds–minutes | Gas only | Bulk gas separations (air, H2) |
| VSA | Vacuum desorption | Seconds–minutes | Gas only | Large air plants (energy-efficient) |
| Inert-purge swing | None (same T, P) | — | Gas | Weakly adsorbed, worthless solute |
| Displacement-purge | Adsorbing displacer | — | Gas/liquid | C10–C18 paraffins on 5A zeolite (NH3 purge) |

## Worked Example
**Example 15.12 — Collins scale-up of a fixed-bed dryer (water vapor on 4A molecular sieve).**
Given: lab bed 0.88 ft deep, G = 29.6 lbmol/h-ft² N2, 1440 ppmv H2O in, q_F = 0.186 lb H2O/lb solid (initial loading 0.01), ρ_b = 44.5 lb/ft³, breakthrough data to 1440 ppm; target: 20 h run at ≤9 ppm outlet.
Method: (1) LES from material balance, LES = c_F·G·t/[q_F·ρ_b] = (0.02592)(29.6)(20)/[(0.186−0.01)(44.5)] = 1.96 ft. (2) LUB from lab curve: t_b = 9.4 h (9 ppm), t_e = 12.8 h (1440 ppm); integrate (15-113) to get stoichiometric time t_s = 10.93 h; LUB = (L_e/t_s)(t_s − t_b) = (0.88/10.93)(1.53) = 0.12 ft. (3) L_B = LES + LUB = 2.08 ft → bed utilization 94.2%.
Result: a 2.08-ft commercial bed; the shortcut (t_s midpoint of 5%/95% points, LUB = MTZ/2) gives 2.06 ft — nearly identical.

## Key Takeaways
1. Sorbent selection is driven by selectivity + capacity + regenerability; zeolites separate by size AND polarity (uniform apertures), carbon by hydrophobicity with easy desorption.
2. Fit pure-component isotherms first; the plateau test decides Langmuir vs Freundlich; extend to mixtures with constant-selectivity forms and accept their inaccuracy, or use IAS theory.
3. Fixed-bed design = LES (equilibrium) + LUB (kinetics); never quote equilibrium capacity as run time — breakthrough comes early, and the fraction of ideal time (62–82% in Ex. 15.11) is the real answer.
4. Favorable isotherms self-sharpen fronts (constant pattern → Collins scale-up valid); linear/unfavorable isotherms broaden, so lab curves can't be scaled simply.
5. Match the regeneration cycle to the job: TSA for dilute purification (long cycles), PSA/VSA for bulk gas separations (short cycles, cyclic steady state), displacement when neither swing works.
6. Ion exchange runs on equivalents and mass-action selectivity, not isotherms; load when (Q/C)K >> 1, regenerate with concentrated brine to make it << 1.
7. Chromatography separates multicomponent feeds in one device; wave velocity u_i = u/[1+((1-ε_b)/ε_b)K_i] sizes the equilibrium column, but mass-transfer-broadened peaks (Carta LDF solution) force a longer column or shorter pulses.

## Connects To
- **Ch 3**: mass-transfer coefficients, Chilton–Colburn j-factors, and Sherwood/Nusselt correlations (Ranz–Marshall, Wakao–Funazkri 15-65/15-66) reused for external transport in packed sorbent beds.
- **Ch 14**: membrane-style effective diffusivity (14-14, 14-18) and Knudsen diffusion reappear as intraparticle transport mechanisms in porous adsorbents.
- **Ch 6/8**: absorption and extraction equilibrium relations feed the chromatography equilibrium toolbox (any sorption mechanism is chromatography).
- **Ch 13 (batch distillation analogy)**: batch elution chromatography produces product cuts plus recycled slop cuts, operating like a batch column; Sorbex pairs SMB with distillation columns to recover desorbent.
- **Aspen tools (process simulators theme)**: Aspen Adsorption (TSA/PSA/VSA cycles), Aspen Chromatography (TMB/SMB rate-based models, DAE solution) — the chapter's simulator-integrated examples.
