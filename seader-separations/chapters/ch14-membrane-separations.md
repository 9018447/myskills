# Chapter 14: Membrane Separations

## Core Idea
A membrane separator partially separates a mixture by driving selected species through a thin semipermeable barrier (feed splits into retentate + permeate); the rate of transport is the product of a **permeance** (permeability / membrane thickness) and a driving force (concentration, partial pressure, ΔP − Δπ, or fugacity), and the art of design is choosing a membrane material and module that balance flux against selectivity.

## Frameworks Introduced
- **Solution-diffusion model** (Lonsdale, Merten, Riley): species absorb/dissolve into a dense (nonporous) membrane at equilibrium with the adjacent fluid, diffuse through it by Fick's law, and desorb downstream. Permeability = solubility × diffusivity: `P_M = K_i D_i` (liquids) or `P_M = H_i D_i` (gases). Basis for reverse osmosis, gas permeation, and pervaporation.
  - Use when the membrane is dense/nonporous (the dominant industrial mechanism).
- **Porous-membrane transport**: bulk flow (Hagen–Poiseuille/Kozeny–Carman, non-selective), liquid diffusion with a restrictive factor `K_r = (1 − d_m/d_p)^4` (size exclusion/sieving when d_m ≥ d_p), and gas diffusion with ordinary + Knudsen diffusion in series: `D_e = (ε/τ)[1/(1/D_i + 1/D_Ki)]`, `D_K = 4850 d_p (T/M)^{1/2}`.
  - Knudsen-dominated selectivity is only √(M_B/M_A) — impractical except for UF₆ isotopes (α = 1.0043, thousands of stages).
- **Reverse osmosis (RO)**: solvent transport against osmosis requires ΔP > Δπ. Osmotic pressure from activity: `π ≈ RT·c_B` (dilute) or Applegate's `π = 1.12 T Σ m̄_i` (psia). Water flux `N = (P_M/l_M)(ΔP − Δπ)`; salt flux independent of ΔP, so higher ΔP → purer permeate.
- **Gas permeation (GP)**: partial-pressure driving force on dense membranes; ideal separation factor `α* = P_MA/P_MB = H_A D_A / (H_B D_B)`. Largest applications: H₂/CH₄, CO₂/CH₄ (natural gas), air (N₂ generators).
- **Dialysis**: concentration-driven solute transfer through a microporous membrane (small solute A passes, large solute B/colloids retained); overall coefficient `1/K = 1/k_F + l_M/P_M + 1/k_P`; solvent counter-transport reported as a water-transport number (ideally < +1.0). Applications: acid recovery, hemodialysis (artificial kidney).
- **Electrodialysis (ED)**: DC field + alternating cation-selective (fixed −SO₃⁻) and anion-selective (fixed −NR₃⁺) membranes in a plate-and-frame stack; Donnan effect excludes co-ions (>90%). Area from Faraday's law `A_M = FQΔc/(iξ)`, not from permeability; operate at ~80% of limiting current density.
- **Pervaporation (PV)**: liquid feed, vapor permeate (vacuum below dew point) — "permeation + evaporation." Driving force `γ_i x_i P_i^s − y_i P_P` (Wijmans–Baker). Permeance depends on feed composition because the permeant swells the polymer. Used to break azeotropes (ethanol–water) and remove VOCs from water.
- **Module flow patterns & cascades**: perfect mixing, countercurrent, cocurrent, crossflow (Naylor–Backer model, analogous to the Rayleigh equation). Countercurrent gives the best separation for a given cut; crossflow is a conservative approximation of spiral-wound modules. Beyond a single stage: two-stage stripping (purer retentate) or enriching (purer permeate) cascades, analyzed like McCabe–Thiele with a selectivity curve.
- **Permeability/selectivity tradeoff (Robeson-type)**: "a high permeability is not compatible with a high separation factor" — rubbery PDMS has high permeance/low α, glassy polycarbonate the reverse. Resolved structurally by **anisotropic (asymmetric) membranes** (Loeb–Sourirajan thin dense skin on porous support), **caulked membranes** (Henis–Tripodi silicone-rubber defect sealing), and **thin-film composites** (Wrasidlo).

## Key Concepts
- **Permeability (P_M) vs permeance (P̄_M = P_M/l_M)**: material property vs as-fabricated mass-transfer coefficient; Barrer = 10⁻¹⁰ cm³(STP)·cm/(cm²·s·cmHg).
- **Separation factor α** (like relative volatility, but y and x are not in equilibrium) vs **ideal separation factor α*** (reached when permeate pressure ≈ 0); actual α is degraded by the pressure ratio r = P_P/P_F.
- **Cut, θ = n_P/n_F**: fraction of feed permeated; separation always worsens as θ → 1.
- **Osmotic pressure π**: thermodynamic driver set by solute concentration; defines the ΔP − Δπ net driving force in RO.
- **Salt rejection SR = 1 − SP** (salt passage SP = c_perm/c_feed).
- **Concentration polarization** (accumulation of rejected species at the feed-side surface; polarization factor Γ = N_w·SR/k_s; significant if Γ > 0.2) and **fouling** (gel/scale/particle deposits — distinct, irreversible).
- **Restrictive (hindered) diffusion factor K_r** and **tortuosity τ** (~2.5) / porosity ε in effective diffusivity.
- **Dual-mode sorption** (Barrer): Henry-law dissolution + Langmuir hole-filling in glassy polymers.
- **Limiting current density** in ED (diluate-side concentration hits zero at the membrane).
- **Water-transport number** in dialysis (ratio of solvent flux to solute flux).

## Mental Models
- **Resistances in series**: flux = total driving force / (1/k_F + l_M/P_M + 1/k_P). For gases the film terms are negligible; for liquids they and polarization matter.
- **α vs r**: the achievable separation is set by the membrane's permeability ratio degraded by the pressure ratio — one membrane equation, solved implicitly (quadratic) for α.
- **Selectivity inversion / concentration-dependence**: in PV, swelling and cross-diffusion make permeance a function of feed composition — measure, don't extrapolate.
- **Modularity**: membrane plants scale by adding parallel modules (fixed unit size), unlike distillation's economy of scale; recompression/pretreatment costs often dominate.

## Anti-patterns
- **Ignoring concentration polarization and fouling**: liquid-phase operations (RO, UF, dialysis) lose flux and salt purity if feed-side accumulation or gel formation is unaddressed — pretreat (screen, filter, soften, chlorinate/ozonate) and keep Γ < 0.2.
- **Expecting high permeability and high selectivity from one material**: they trade off; use asymmetric/composite architecture (thin selective skin + porous support) instead of a thick dense film.
- **Assuming Knudsen flow will separate ordinary gases**: α ≈ √MW ratio is too small — separation of gases by microporous membranes at equal pressures is almost always impractical.
- **Driving the cut too high**: at θ → 1, permeate composition approaches the feed and area explodes (Example 14.5: 22,000 → 2,567,000 ft² as θ goes 0.01 → 0.99).
- **Heating/condensation neglect in GP**: retentate enriches in heavy components — preheat above the retentate dew point to avoid condensation on the membrane.
- **Sizing ED from permeability**: electrodialysis area comes from Faraday's law and current density, with current efficiency < 1.

## Reference Tables

**Membrane module selection** (Table 14.4):

| Module | Packing density (m²/m³) | Fouling resistance | Cleaning | Cost | Main uses |
|---|---|---|---|---|---|
| Plate-and-frame | 30–500 | Good | Good | High | ED, PV, RO, UF/MF (high-value) |
| Spiral-wound | 200–800 | Moderate | Fair | Low | RO, GP, UF/MF, D — most popular |
| Tubular | 30–200 | Very good | Excellent | High | RO, UF where fouling/cleaning critical |
| Hollow-fiber | 500–9,000 | Poor | Poor | Low | D, RO, GP, UF when feeds are clean |

**Pore-size ladder**: MF 200–100,000 Å (bacteria/yeast); UF 10–200 Å (proteins/viruses); NF 1–10 Å (RO/PV regime).

**Typical operating windows**: seawater RO: π ≈ 350–385 psia, feed 800–1,000 psia, flux ~9 gal/ft²-day, ~99.95 wt% purity, spiral-wound polyamide TFC (FT30-type); brackish RO: π < 50 psi, < 250 psia, up to 20 gal/ft²-day, hollow fibers. GP feed 300–1,650 psia; O₂/N₂ α* = 3–7 commercially. ED for 500–5,000 ppm brackish water (ion exchange below, RO above).

**Polymer classes**: glassy (polysulfone T_g 190°C, polyimide, polycarbonate — low permeability, high selectivity) vs rubbery (PDMS, natural rubber T_g −70°C — high permeability, low selectivity) vs crystalline (cellulose triacetate, PTFE); inorganic (alumina, silica, Pd, carbon) above 200°C or with reactive feeds.

## Worked Example
**Example 14.5 — Air separation by gas permeation (perfect mixing).**
- *Given*: 20,000 scfm air (21% O₂) at 150 psia feed / 15 psia permeate (r = 0.1); low-density polyethylene membrane 0.2 μm skin; from Table 14.6, P_M(O₂) = 16.2×10⁻¹² and P_M(N₂) = 5.43×10⁻¹² lbmol·ft/ft²·h·psia → permeances 24.55 and 8.23×10⁻⁶ lbmol/ft²·h·psia; α* = 2.98.
- *Method*: with cut θ specified, retentate composition from overall balance `x_R = (x_F − y_P θ)/(1 − θ)`; actual α from the implicit equation (14-43); membrane area from the O₂ transport equation using permeance × partial-pressure driving force.
- *Result*: permeate O₂ peaks at 40.6 mol% at θ = 0.01 and falls to 21.1% at θ = 0.99; α stays ≈ 2.55–2.60 (~86% of ideal); area grows from 22,000 ft² (θ=0.01) to 2.57 M ft² (θ=0.99). At θ = 0.4 the retentate N₂ is only 85.4 mol% — impractical. Crossflow (Ex. 14.6) does better (retentate 87.8% N₂, stage α up to 5.4 at θ=0.6); to reach 95% N₂ you need α* ≈ 5 or a cascade.

## Key Takeaways
1. Membrane flux = permeance × driving force; permeance = permeability/thickness, so anisotropic (skin + support) or thin-film-composite architecture is what makes industrial fluxes possible.
2. For dense membranes, P_M = solubility × diffusivity — both matter, and they often move in opposite directions with molecular size (D falls, H/S rises with MW), capping selectivity.
3. α* is an upper bound: the real separation factor shrinks with pressure ratio r and cut θ; countercurrent > crossflow > cocurrent > perfect mixing for a given cut.
4. Single stages give modest separations — use cascades (stripping/enriching, with pre-membrane stage when feed is dilute in the permeating species) or hybrids (distillation + PV for azeotropes).
5. Liquids bring external-film resistance, concentration polarization (Γ > 0.2 needs redesign), and fouling; gases bring essentially none — but demand compression and feed preheating.
6. Each operation has its own design kernel: RO (ΔP − Δπ with osmotic pressure), GP (partial pressure), dialysis (log-mean Δc with overall K), ED (Faraday's law and limiting current), PV (γxPˢ − yP with composition-dependent permeance).
7. Always verify with experimental permeability data for the actual membrane/feed pair — swelling, interactions, and pore-size distributions make a priori prediction unreliable (Teplyakov–Meares correlations only ±20–30%).

## Connects To
- **Ch 3 (Mass Transfer/Fick's Law)**: diffusion fundamentals, film coefficients, and the Sherwood correlations (14-55) used for boundary-layer resistances.
- **Ch 2 (Thermodynamics)**: activity coefficients, Henry's law, fugacity/Poynting correction behind π, solution-diffusion, and the PV driving force.
- **Ch 7 (Distillation) & Ch 13 (Batch Distillation)**: cascades are analyzed with McCabe–Thiele-type diagrams (selectivity curve replaces equilibrium curve); the crossflow model is the Rayleigh equation in membrane form.
- **Ch 5 (Cascades §5.4)**: general countercurrent cascade/recycle concept reused for membrane stages.
- **Ch 15 (Adsorption/Ion Exchange)**: next sorption-based operation; ED ion-selective membranes share the ion-exchange chemistry (fixed charges, Donnan exclusion); membrane contactors link to absorption/stripping.
