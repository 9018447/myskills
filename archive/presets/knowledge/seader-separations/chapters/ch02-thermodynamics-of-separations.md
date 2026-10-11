# Chapter 2: Thermodynamics of Separation Operations

## Core Idea
Every separation is limited by phase equilibrium: at equilibrium the chemical potential (surrogated by fugacity) of each species is equal in all phases, and the practical job of the engineer is to pick the right thermodynamic model — EOS, γ-φ (g^E), or predictive — to compute K-values, then use first- and second-law analysis (exergy) to quantify the energy cost of actually achieving that separation.

## Frameworks Introduced
- **Fugacity equality condition (2-8)**: phase equilibrium ⇔ f̄ᵢ⁽¹⁾ = f̄ᵢ⁽²⁾ = ... across all phases, with T and P equal across phases (2-9, 2-10). Fugacity (Lewis, 1901) replaces chemical potential μᵢ, which goes to −∞ as P→0 and has no absolute scale.
  - When to use: basis of every VLE/LLE/SLE calculation; derive any K-value model from it.
  - How: set f̄ᵢV = f̄ᵢL (2-22), express each side via φ, γ, or P^s, and solve for Kᵢ = yᵢ/xᵢ.
- **K-value formulations (Table 2.2)**: rigorous EOS form Kᵢ = φ̄ᵢL/φ̄ᵢV (2-26); rigorous γ-φ form Kᵢ = γᵢL·φᵢL/φ̄ᵢV (2-27); approximate Raoult Kᵢ = Pᵢ^s/P (2-28); modified Raoult Kᵢ = γᵢL·Pᵢ^s/P (2-29); Poynting-corrected form (2-30); Henry's law Kᵢ = Hᵢ/P (2-31) for species above T_c.
  - When to use: hydrocarbon/light-gas → EOS; polar chemicals at low P → modified Raoult; supercritical gas (T > T_c, e.g. CH₄, H₂ in water) → Henry's law.
- **Relative volatility & relative selectivity**: αᵢ,ⱼ = Kᵢ/Kⱼ (2-20) for VLE; βᵢ,ⱼ = K_Dᵢ/K_Dⱼ (2-21) for LLE. Ideal α is pressure-independent (Raoult's law). Separation easy for large α, impractical near 1.00.
- **g^E (excess Gibbs free energy) models (Table 2.8)**: g = Σxᵢgᵢ + RTΣxᵢln xᵢ + g^E (2-60); ln γᵢ = ∂(N_t g^E/RT)/∂Nᵢ (2-61). Local-composition concept (Wilson, 1964).
  - When to use: highly nonideal liquid solutions of dissimilar polar species where EOS mixing rules fail.
  - How: pick Wilson (miscible only, no phase split), NRTL or UNIQUAC (predict liquid–liquid splitting), with binary interaction parameters from data banks (DECHEMA, DDB).
- **EOS models (Table 2.4)**: RK, SRK (adds acentric factor ω via f_ω, fits vapor pressure), PR (better critical region and liquid density). Cubic in Z (e.g. RK: Z³ − Z² + (A−B−B²)Z − AB = 0, (2-49)); largest root = vapor, smallest = liquid. Departure integrals (Table 2.5) give h, s, φ, φ̄ from the EOS.
  - When to use: nonpolar/light-gas mixtures, cryogenic to critical region; SRK limited to T > ~−140°C, PR usable to ~0 K.
- **Ewell–Harrison–Berg H-bond classification (Tables 2.6/2.7)**: Classes I–V by active-H/donor-atom potential predicts sign of deviation from Raoult's law (γ > 1 or < 1) and immiscibility before any data fitting.
  - When to use: first qualitative screen of a polar binary pair.
- **Azeotrope criteria (2-70)–(2-76)**: minimum-boiling when γᵢ ≥ 1 for both and γ₁/γ₂ < P₂^s/P₁^s (2-73); maximum-boiling (rarer) for negative deviations. At the azeotrope Kᵢ = 1 — ordinary distillation cannot pass it. Wilson/NRTL parameters can be back-calculated from a single azeotrope point (Example 2.4).
- **Exergy / second-law analysis (Table 2.11)**: energy balance (1); entropy balance with ΔS_irr (2); exergy balance giving Lost Work = T₀ΔS_irr (2-95); stream availability b = h − T₀s (2-94); W_min = Σ(out)nb − Σ(in)nb (4); second-law efficiency η = W_min/(LW + W_min) (5).
  - When to use: sizing the energy penalty of any separation; heat Q at T_s counts only by Carnot factor (1 − T₀/T_s).
- **Predictive models**: UNIFAC (group-contribution UNIQUAC, r/q from group sums (2-85/2-86), residual ln γ^R via group activity coefficients Γ_k (2-87/2-88)); modified UNIFAC (Dortmund, 290–420 K); PSRK (SRK + UNIFAC mixing rule (2-92) for polar + supercritical gases); VTPR / PR-UNIFAC (Huron–Vidal, Wong–Sandler mixing rules). Use when binary parameters are unavailable — only ~2% of the ~500,000 industrially relevant binary pairs have VLE data.
- **Special systems**: electrolyte NRTL (Chen) or Pitzer for aqueous electrolytes (chemical + physical equilibrium together, e.g. sour water); electrolyte NRTL also handles mixed solvents; modified NRTL of Chen (Flory–Huggins + local composition) for polymer solutions.

## Key Concepts
- **K-value** (2-18): vapor–liquid equilibrium ratio Kᵢ = yᵢ/xᵢ; **distribution coefficient** K_Dᵢ = xᵢ⁽¹⁾/xᵢ⁽²⁾ (2-19) for LLE.
- **Fugacity coefficient** φ: ratio of fugacity to (partial) pressure; = 1 for ideal gas; captures pressure-driven nonideality.
- **Activity coefficient** γ (2-16/2-17): ratio of activity to mole fraction; = 1 for ideal solution; captures composition-driven nonideality. γ > 1 positive deviation, γ < 1 negative.
- **Azeotrope**: composition where yᵢ = xᵢ (Kᵢ = 1), so relative volatility → 1 and distillation cannot cross it (e.g. ethanol/n-hexane, x_E = 0.332, 58°C, minimum-boiling).
- **Convergence pressure**: pressure at which all K-values of a mixture approach 1.0 — the mixture analog of critical pressure.
- **Acentric factor ω** (2-48): third parameter (Pitzer) from the vapor-pressure curve at T_r = 0.7 accounting for molecular shape; ω = 0 for symmetric molecules.
- **Local composition** (Wilson): local mole/volume fractions around a molecule differ from bulk composition due to unequal interaction energies — basis of Wilson, NRTL, UNIQUAC.
- **NRTL α (nonrandomness parameter)**: 0.2–0.47 by molecule class; α > 0.426 predicts phase splitting.
- **Exergy (availability) b = h − T₀s** (2-94): maximum shaft work obtainable from a stream; like g = h − Ts but with T₀ (surroundings, ~300 K) replacing stream T.
- **Lost work LW = T₀ΔS_irr** (2-95): destroyed exergy, always positive, units of energy; actual work = W_min + LW.

## Mental Models
- Use fugacity, not chemical potential, when doing any phase-equilibrium math — μ is unusable at low P.
- Use an EOS (SRK/PR) when nonideality comes from pressure (hydrocarbons, light gases); use a g^E model (Wilson/NRTL/UNIQUAC) when it comes from liquid-phase molecular interactions (polar organics); use PSRK/VTPR when you have both polar compounds and supercritical gases.
- Think of a real separation's energy bill as two parts: the irreducible W_min (set by feed/product states, independent of the equipment) plus LW (set by your driving forces — finite ΔT, ΔP, Δcomposition). Improving efficiency = shrinking driving forces until economics object.
- Screen nonideality with the H-bond class pair before fitting anything: H-bonds broken only → strong positive deviations; formed only → negative; both broken and formed → mixed/odd curves.

## Anti-patterns
- **Using Raoult's law (2-28) for polar/nonideal systems**: only valid for similar-structure components at near-ambient pressure; wildly wrong for alcohol–hydrocarbon pairs (γ^∞ can exceed 20).
- **Using the Wilson equation where two liquid phases can form**: Wilson mathematically cannot predict immiscibility or maxima/minima in γ–x curves; use NRTL or UNIQUAC.
- **Using EOS models for strongly associating polar liquids without modified mixing rules**: preferred practice is γ-φ models at near-ambient conditions.
- **Applying Henry's law outside low-to-moderate P or forgetting it depends on composition, T, and P** — it replaces vapor pressure only for species with T_c below system T.
- **Reading converged material balances as proof of correctness**: Example 2.3 explicitly warns to verify simulator outputs independently.
- **Mixing enthalpy datums across simulators/streams**: elemental vs component reference state differ by the heat of formation (water example: −12,920 vs 508 kJ/kg); use the elemental datum whenever reactions occur (and always for electrolytes).

## Reference Tables
K-value / thermodynamic model selection (condensed from Tables 2.2, 2.4, 2.8, 2.10 and §2.11.1):

| Situation | Model | Key relation |
|---|---|---|
| Hydrocarbons + light gases, cryogenic → critical | PR (all T, P); SRK (T > −140°C); LKP (wide boiling range) | Kᵢ = φ̄ᵢL/φ̄ᵢV (2-26) |
| Ideal solutions, near-ambient P | Raoult's law | Kᵢ = Pᵢ^s/P (2-28) |
| Nonideal liquid, near-ambient P | Modified Raoult + g^E model | Kᵢ = γᵢL Pᵢ^s/P (2-29) |
| Moderate P, nonideal liquid | γ-φ with Poynting correction (2-30) | Kᵢ = γᵢL φᵢL/φ̄ᵢV (2-27) |
| Supercritical species (T > T_c) at low–moderate P | Henry's law | Kᵢ = Hᵢ/P (2-31) |
| Polar organics, miscible, no phase split | Wilson | Table 2.8 (1); multicomponent (2-67) |
| Polar organics, possible LLE / VLLE | NRTL (α ≈ 0.2–0.47 by class) or UNIQUAC | Table 2.8 (2),(3) |
| No binary parameters available | Modified UNIFAC (Dortmund), 290–420 K | group contribution (2-85)–(2-91) |
| Polar + supercritical gases | PSRK, VTPR, PR-UNIFAC (HV or WS rules) | (2-92) |
| Aqueous electrolytes (sour water, amines) | Pitzer or electrolyte NRTL (Chen); mixed solvents → Chen only | chemical + physical equilibrium |
| Polymer solutions | Modified NRTL (Chen, Flory–Huggins based) | segment interactions |
| Refrigerant mixtures | Lee–Kesler–Plöcker | corresponding states |

NRTL α quick rules: 0.20 hydrocarbons/polar nonassociated; 0.30 nonpolar pairs, water + polar nonassociated, moderate deviations; 0.40 saturated hydrocarbons/perfluorocarbons; 0.47 self-associated (alcohols) with nonpolar species.

## Worked Example
**Example 2.5 — Second-law efficiency of propylene/propane distillation** (a hard split: 150 theoretical stages, R/D ≈ 15). Given simulator stream h, s, b for F (272.2 kmol/h), D (159.2), B (113); condenser coolant T₀ = 303 K, reboiler steam T_s = 378 K.
- Q_C = n_OV(h_OV − h_R) = 29.81×10⁶ kJ/h; Q_R from overall energy balance = 29.79×10⁶ kJ/h.
- Entropy balance: ΔS_irr = 18,246 kJ/h·K → LW = T₀ΔS_irr = 5.53×10⁶ kJ/h (same answer from the exergy balance, as it must).
- W_min = Σ(out)nb − Σ(in)nb = 3.82×10⁵ kJ/h.
- η = W_min/(LW + W_min) = 382,100/5,911,100 = **6.5%** — lost work dwarfs the thermodynamic minimum, typical of difficult distillations.

## Key Takeaways
1. All phase-equilibrium calculations rest on equality of partial fugacity (and T, P) across phases; K-values are just bookkeeping of that equality.
2. Only two rigorous K-value forms exist — EOS (φ̄ᵢL/φ̄ᵢV) and γ-φ (γᵢL φᵢL/φ̄ᵢV); everything else (Raoult, modified Raoult, Henry) is a limit of these.
3. Match the model to the nonideality source: pressure → SRK/PR; liquid composition → Wilson/NRTL/UNIQUAC; both/supercritical gas → PSRK/VTPR; electrolytes → Pitzer/electrolyte NRTL.
4. Wilson fits strongly nonideal miscible binaries but cannot predict phase splitting — NRTL and UNIQUAC can.
5. One azeotrope point (T, x) suffices to back-calculate Wilson parameters; an azeotrope (K = 1) is a hard barrier to ordinary distillation.
6. Binary data are scarce (~2% of interesting pairs) — group-contribution predictive models fill the gap, trading accuracy for coverage (UNIFAC can't distinguish isomers).
7. W_min is fixed by feed and product states; your design only adds lost work. Second-law efficiency of real separations is often < 10%.

## Connects To
- **Ch 1**: defines the separation operations whose energy and equilibrium limits this chapter quantifies.
- **Ch 3 (Mass Transfer and Diffusion)**: rapid mass transfer drives systems toward the phase equilibrium defined here — equilibrium-stage design assumes it is reached.
- **Ch 4/5 (single- and multicomponent distillation/flash)**: every stage calculation consumes the K-value models selected here (esp. Table 2.2).
- **Ch on azeotropic/extractive distillation & liquid–liquid extraction**: LLE uses K_Dᵢ (2-19) and requires NRTL/UNIQUAC phase-split capability.
- **Ch 12+ (rate-based/multicomponent mass transfer)**: rigorous EOS fugacities are the thermodynamic input to rate models.
