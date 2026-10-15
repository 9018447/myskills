# Chapter 4: Single Equilibrium Stages and Flash Calculations

## Core Idea
A single equilibrium stage's outlet phases are fixed entirely by thermodynamics (T, P, K-values) plus material/energy balances; this chapter gives the degrees-of-freedom bookkeeping and the standard calculation algorithms (bubble point, dew point, isothermal/adiabatic flash via Rachford–Rice) for vapor–liquid, liquid–liquid, liquid–solid, gas–liquid, gas–solid, and three-phase systems.

## Frameworks Introduced

- **Gibbs' Phase Rule (intensive)**: `N_D = C − N_P + 2`, derived from `N_V = N_P(C+2)` variables minus `N_E = N_P + (C+2)(N_P − 1)` equations (summations per phase + equality of T, P, and C compositions across each phase pair).
  - When to use: count how many intensive variables (usually T, P, or one composition) can be independently specified before the equilibrium state is fixed. Example: V–L–L ternary → N_D = 2; specify T and P and one component composition fixes everything via tie lines.
- **Extended Gibbs' Phase Rule (extensive variables)**: add feed/product flows and Q. For N_P product phases: `N_V = N_P(C+2) + (C + N_P + 4)`, `N_E = N_P + (C+2)(N_P−1) + (C+2)`, giving **`N_D = C + 4`** for any number of product phases (two-phase: 3C+10 variables, 2C+6 equations).
  - How: specify feed completely (F, T_F, P_F, and C−1 mole fractions = C+2 specs), then two more variables — which pair you pick names the calculation (see Reference Tables).
- **Modified Raoult's Law K-values**: `K_i = y_i/x_i = γ_iL P_i^s / P` (ideal: Raoult's law `K_i = P_i^s/P`). For non-condensable gases, Henry's law replaces it: `K_i = H_i/P`.
  - When: near-ambient pressure VLE. γ < 1 ⇒ negative deviation (max-boiling azeotrope risk, e.g. acetone–chloroform); γ > 1 ⇒ positive deviation (min-boiling azeotrope, e.g. isopropyl ether–isopropanol). Azeotrope ⇔ α = 1 at the azeotropic composition.
- **q-line (phase-fraction) equation** for binary partial vaporization on a y–x diagram: `y = [(V/F) − 1]/(V/F) · x + z/(V/F)` (Eq. 4-11), derived from total + component balances. Slope = (Ψ−1)/Ψ through the point (z, z) on the 45° line.
  - How: from (z, z) draw a line of slope [(V/F)−1]/(V/F) to the equilibrium curve; the intersection gives (x, y). Horizontal T–y–x tie lines + inverse-lever-arm rule give phase amounts: V/L = (distance to liquid side)/(distance to vapor side).
- **Rachford–Rice (RR) isothermal flash algorithm**: reduces the 2C+6 nonlinear equations to ONE nonlinear equation in Ψ = V/F:
  `f{Ψ} = Σ z_i(1−K_i) / [1 + Ψ(K_i − 1)] = 0` (4-26); then `x_i = z_i/[1+Ψ(K_i−1)]`, `y_i = K_i x_i`.
  - Steps: (1) pre-check phase condition (below); (2) solve f{Ψ}=0 by Newton's method, Ψ^(1) = 0.5, update `Ψ^(k+1) = Ψ^(k) − f/f′` with `f′ = Σ z_i(1−K_i)²/[1+Ψ(K_i−1)]²` (4-28), converge when relative change < 0.0001; (3) back out V = ΨF, L = F−V, compositions; (4) energy balance for Q if needed.
  - Phase-condition checks (valid for ideal K-values): Check 1 — all K_i > 1 ⇒ superheated vapor; all K_i < 1 ⇒ subcooled liquid. Check 2 — mixed K signs: f{0} > 0 ⇒ below bubble point; f{1} < 0 ⇒ above dew point; else two phases exist (0 < Ψ < 1).
- **Bubble- and dew-point equations**: bubble `Σ z_i K_i = 1` (4-30, Ψ=0); dew `Σ z_i/K_i = 1` (4-31, Ψ=1). Iterate on T at fixed P (moderately nonlinear) or P at fixed T (nearly linear except near convergence pressure).
- **Adiabatic / nonadiabatic / percent-vaporization flashes**: nested loops on the RR procedure — outer loop guesses T_V, inner RR loop solves Ψ, then check energy balance `F h_F + Q = V h_V + L h_L` (4-17). Close-boiling mixtures may need T inside and Ψ outside.
- **Ternary LLE triangular diagrams**: equilateral-triangle plots of ternary LLE data; binodal (miscibility boundary) curve separates one-liquid from two-liquid regions; tie lines connect equilibrium extract/raffinate compositions; plait point where phases merge.
  - How: plot feed F and solvent S, find mixing point M (overall composition of F+S) on line FS; interpolate a tie line through M; inverse-lever-arm rule gives E/(E+R) = MR/ER; compositions read at the tie-line ends.
- **Immiscible single-stage extraction with extraction factor**: carrier A and solvent C insoluble; solute balance in mass ratios `X_B^(F) F_A = Y_B^(E) S + X_B^(R) F_A` with `Y_B = K′_D X_B` gives fraction unextracted `X_B^(R)/X_B^(F) = 1/(1+ℰ)` where **extraction factor `ℰ = K′_D S/F_A`**.
- **Modified Rachford–Rice for multicomponent LLE**: symbol map V→E, L→R, y→x⁽¹⁾, x→x⁽²⁾, K→K_D = γ_i⁽²⁾/γ_i⁽¹⁾ (from `γ_i⁽¹⁾x_i⁽¹⁾ = γ_i⁽²⁾x_i⁽²⁾`, NRTL/UNIQUAC/UNIFAC), Ψ = E/(F+S); outer loop updates compositions/γ's until converged.
- **Solid–fluid stage balances**: adsorption — solute balance `c_B^(F) Q = c_B Q + q*_B S` is a straight line (slope −Q/S) intersected with the adsorption isotherm (Freundlich: `q* = A c^(1/n)`); desublimation — set gas partial pressure equal to solid vapor pressure and combine with Dalton's law + total balance; gas adsorption — y–x equilibrium plot plus adsorbate loading curve gives an adsorption separation index `(y_A/x_A)/[(1−y_A)/(1−x_A)]`, analogous to α.
- **Three-phase (V–L–L) isothermal flash** (Henley–Rosen): two coupled RR-type equations in Ψ = V/F and ξ = L⁽¹⁾/(L⁽¹⁾+L⁽²⁾), Eqs. (4-49)/(4-50), with K⁽¹⁾, K⁽²⁾ (or K_D); five possible phase states (VLL, VL¹, L¹L², V, L¹) must be tested.

## Key Concepts
- **Equilibrium stage**: a contact device whose exiting phases are in physical equilibrium (dynamic — molecules cross both ways, but T, P, compositions stop changing). Phase compositions differ (except azeotropes), which is what enables separation on disengagement.
- **Degrees of freedom (N_D)**: variables − independent equations; the number of specifications you may make.
- **K-value / distribution coefficient**: `K_i = y_i/x_i` (VLE) or `K_D,i = x_i^(1)/x_i^(2)` (LLE); a thermodynamic property, not a counted variable.
- **Relative volatility** `α_A,B = (y_A/x_A)/((1−y_A)/(1−x_A))` (4-10): the separation index for partial vaporization/condensation/distillation. Sets single-stage feasibility: water–glycerol (α huge) works in one stage; methanol–water needs ~30 stages; p-/m-xylene (α ≈ 1.01) is impractical by distillation → crystallization/adsorption.
- **Bubble point / dew point**: first vapor bubble (Ψ=0, liquid at bubble point) / last liquid droplet (Ψ=1, vapor at dew point). In any two-phase flash, the vapor is at its dew point and the liquid at its bubble point.
- **Zeotropic vs. azeotropic**: zeotropic mixtures never have y = x; azeotropes do (K = α = 1 there). Minimum-boiling (positive deviation, γ > 1) most common; maximum-boiling (negative deviation, γ < 1) rarer. Heterogeneous azeotropes add a second liquid phase.
- **Flash drum / flash**: single-equilibrium-stage distillation — partial vaporization of a liquid (or partial condensation of a vapor) followed by phase disengagement.
- **Ψ = V/F**: vapor fraction; the single unknown of the RR function. q-line: the material-balance line on a y–x diagram carrying the Ψ specification.
- **Tie line / binodal curve / plait point**: ternary LLE diagram features — equilibrium phase-pair connector, one-phase/two-phase boundary, and the convergence point where the phases become identical.
- **Extraction factor ℰ, adsorption isotherm, Henry's law constant H_i**: the equilibrium "lever" for extraction, adsorption, and gas absorption stages respectively.

## Mental Models
- **Degrees of freedom as a specification budget**: N_D = C + 4 for any flash; feed consumes C+2, so you have exactly 2 specs left — naming them picks the algorithm (T,P → isothermal flash; Q=0,P → adiabatic; V/F,P → percent vaporization; V/F=0 → bubble point; V/F=1 → dew point).
- **One equation, one unknown**: RR's insight — collapse C component balances into a single monotone function of Ψ; everything else back-calculates. When stuck on a multicomponent equilibrium problem, look for the equivalent scalar root.
- **Every equilibrium stage problem = equilibrium relation + material balance (+ energy balance)**: graphical (tie lines, y–x curves, isotherms) when binary/ternary; iterative simulator when multicomponent/nonideal.
- **Equilibrium tells you the ceiling, not the time**: thermodynamics fixes compositions/amounts; diffusion rates and kinetics fix how close you get (and leaching/ crystallization rarely reach equilibrium; solids never separate cleanly from liquid).

## Anti-patterns
- **Trusting the phase-condition checks for nonideal mixtures**: the f{0}/f{1} checks are only valid when K-values are composition-independent (Raoult's law). For nonideal systems K must be recomputed each iteration and RR may fail to converge — use the modified RR / simulator three-phase routine.
- **Specifying irrational product mole fractions**: e.g. demanding x_N2 = 0.8 in water at 100°F, 15 psia is infeasible regardless of solver convergence. Always feasibility-check simulator specs and results.
- **Inverting the lever arm**: on a T–y–x diagram, V/L = (feed-to-liquid-side segment)/(feed-to-vapor-side segment) — i.e. the phase amount is proportional to the distance to the OTHER phase's boundary. Same on triangular diagrams: E/(E+R) = MR/ER.
- **Using Raoult/modified Raoult for non-condensables or high-solubility gases**: if T > T_c of the component, no vapor pressure exists — use Henry's law (and Henry's law fails for highly soluble gases like NH₃ in water or at high P; need experimental data).
- **Assuming a single stage suffices**: α close to 1 (isomer pairs) means thousands of stages; check α before committing to distillation — crystallization or adsorption may have a far higher separation index.
- **Ignoring azeotrope barriers**: at the azeotrope y = x, so distillation cannot cross it; boundary crossing requires azeotropic/extractive distillation or hybrid schemes (Ch. 11).

## Reference Tables

### Which calculation to run (two-phase flash, N_D = C+4; after full feed spec, choose 2)

| Specifications | Calculation | Method |
|---|---|---|
| T_V, P_V | Isothermal flash | RR on Ψ (Newton) |
| Q = 0, P_V | Adiabatic flash | Outer loop T, inner RR; check h-balance |
| Q, P_V | Nonadiabatic flash | Same as adiabatic with Q spec |
| V/F, P_V | Percent vaporization flash | Outer loop T to hit Ψ target |
| V/F = 0, P_V (or T_L, Ψ=0 for P) | Bubble-point T (or P) | Σ z_i K_i = 1 |
| V/F = 1, P_V (or T_V, Ψ=1 for P) | Dew-point T (or P) | Σ z_i/K_i = 1 |

### Degrees-of-freedom quick counts
- Gibbs (intensive): N_D = C − N_P + 2 (water: 1 phase→2, 2 phases→1, triple point→0).
- Process (with flows/heat): N_D = C + 4 regardless of number of product phases.
- Two-phase VLE at fixed P (binary, table form): fixing P + x_A fixes T and y_A.

## Worked Example — Isothermal Rachford–Rice Flash (Example 4.3)
Feed: 100 kmol/h at 690 kPa, 93°C: propane 10%, n-butane 20%, n-pentane 30%, n-hexane 40%. Given K = [4.2, 1.75, 0.74, 0.34] (composition-independent).

1. **Phase check**: mixed K signs, so evaluate f{Ψ}. f{0} = Σz_i(1−K_i) = −0.128 (not > 0 ⇒ above bubble point); f{1} = +0.720 (not < 0 ⇒ below dew point). Two phases confirmed.
2. **Solve** f{Ψ} = Σ z_i(1−K_i)/[1+Ψ(K_i−1)] = 0 by Newton from Ψ = 0.5: iterates 0.50 → 0.0982 → 0.1211 → 0.1219 → converged 0.1219 (4 iterations).
3. **Back-calculate**: V = 12.19 kmol/h, L = 87.81 kmol/h; x = [0.0719, 0.1833, 0.3098, 0.4350], y = [0.3021, 0.3207, 0.2293, 0.1479] from x_i = z_i/[1+Ψ(K_i−1)], y_i = K_i x_i. Both sum to 1 — a built-in check.

Companion results from the chapter: single-stage extraction of acetic acid from water with MIBK (K′_D = 0.657, target 8 → 1 wt%) needs ℰ = 7.61 ⇒ S = 144,000 kg/h — pushing toward multistage or a better solvent (1-butanol, K′_D = 1.613, halves it); SO₂ absorption in water via Henry's law (H = 37 atm at 25°C, P = 10 atm) absorbs 57.8% of SO₂ in one stage.

## Key Takeaways
1. Gibbs' phase rule (N_D = C − N_P + 2) counts intensive specs; its process extension (N_D = C + 4) counts flash specs — after the feed, exactly two specifications remain, and the pair chosen defines the flash type.
2. The Rachford–Rice function reduces a multicomponent isothermal flash to one scalar root in Ψ = V/F; bubble (ΣzK = 1) and dew (Σz/K = 1) points are its Ψ = 0 and Ψ = 1 limits.
3. Always pre-check the phase condition (all K > 1, all K < 1, f{0}, f{1}) before iterating — and remember the checks are strict only for ideal K-values.
4. Relative volatility is the go/no-go index for distillation-based separation; azeotropes (α = 1 points) cap what distillation can do.
5. Ternary LLE is solved graphically (mixing point → interpolated tie line → lever arm); quaternary+ LLE is the modified RR with K_D = γ⁽²⁾/γ⁽¹⁾ and an outer composition loop.
6. Every solid–fluid single-stage problem is the same pattern: linear material balance intersected with the appropriate equilibrium curve (isotherm, triangular tie line, y–x adsorption curve, solid vapor pressure).
7. Three-phase V–L–L flashes (two coupled RR equations in Ψ and ξ) and nonideal multicomponent flashes are simulator territory (Henley–Rosen algorithm, UNIFAC/NRTL K-values, Henry's law for light gases); water + organics can produce three phases even on distillation trays.

## Connects To
- **Ch 2**: supplies the thermodynamic backbone — K-value models (Raoult, modified Raoult, EOS), activity-coefficient models (Wilson, NRTL, UNIQUAC, UNIFAC), Antoine vapor pressure, enthalpies; the flash algorithms here are consumers of those property models.
- **Ch 5**: extends the single-stage degrees-of-freedom analysis (N_D = C + 4) to multistage countercurrent cascades and hybrid systems; a single stage (e.g. 69% methanol recovery) is rarely enough — cascades buy purity and recovery.
- **Ch 7 (distillation) / Ch 8**: the bubble/dew/flash routines and q-line constructions here are the per-stage building blocks of column rating and the McCabe–Thiele method.
- **Ch 11**: azeotrope structure (min/max-boiling, homogeneous/heterogeneous) diagnosed in this chapter drives azeotropic and extractive distillation design.
- **DDB / process simulators (Aspen Plus, CHEMCAD, ProSimPlus, ChemSep)**: the chapter's explicit stance — graphical methods for binaries/ternaries, simulators with DDB-backed property data for everything multicomponent or strongly nonideal.
