# Chapter 7: Distillation of Binary Mixtures

## Core Idea
Continuous binary distillation achieves a sharp LK/HK split when alpha > ~1.05 and no azeotrope forms; the McCabe-Thiele graphical method — built on constant molar overflow — turns the design into five construction lines (45-degree line, equilibrium curve, rectifying operating line, stripping operating line, q-line) from which N, N_min, R_min, and the optimal feed stage can be read off, with tray efficiency and hydraulics converting equilibrium stages into real hardware.

## Frameworks Introduced

- **McCabe-Thiele graphical method (five construction lines)**: Combines the y-x equilibrium curve with material-balance operating lines on a single diagram to step off equilibrium stages.
  - When to use: Design case — given F, z_F, P, feed phase, x_D, x_B, and R/R_min, find N, R_min, N_min, optimal feed stage. Assumes constant molar overflow (equal latent heats, negligible sensible heats/heat of mixing, insulated column, no pressure drop). Step stages top-down from (x_D, x_D); transfer from rectifying to stripping operating line at the first staircase horizontal passing the q-line/operating-line intersection P (optimal feed stage). Delayed or early transfer costs extra stages (Example 7.1: optimal = 5 stages vs 6.4 when delayed).
  - Rectifying operating line: y = [R/(R+1)]x + x_D/(R+1) — slope L/V = R/(R+1) < 1, intersects 45-degree line at y = x_D.
  - Stripping operating line: y = [(V_B+1)/V_B]x − x_B/V_B — slope L-bar/V-bar = (V_B+1)/V_B > 1, intersects 45-degree line at y = x_B. Partial reboiler counts as one equilibrium stage.
  - R and V_B are not independent — linked through the feed condition via the q-line.
- **q-line (feed line)**: y = [q/(q−1)]x − z_F/(q−1); passes through (z_F, z_F) on the 45-degree line with slope q/(q−1), where q = (L-bar − L)/F.
  - When to use: Locates the intersection of the two operating lines and encodes feed thermal condition: subcooled liquid q > 1 (slope positive); saturated liquid q = 1 (vertical line); partially vaporized 0 < q < 1 (q = L_F/F = 1 − vaporized fraction); saturated vapor q = 0 (horizontal); superheated vapor q < 0. For subcooled/superheated feeds compute q from enthalpy: q = [ΔH_vap + C_P,L(T_b − T_F)]/ΔH_vap (liquid) or q = C_P,V(T_d − T_F)/ΔH_vap (vapor).
- **Limiting-condition analysis (total reflux and minimum reflux)**:
  - Total reflux: R → ∞, both operating lines coincide with the 45-degree line; feed condition irrelevant; staircase is farthest from the equilibrium curve → N_min. Steady state easily achieved, so total reflux is how tray efficiency is measured industrially.
  - Minimum reflux: R_min → pinch point where operating lines meet the equilibrium curve → infinite stages. For near-ideal systems the pinch sits at the q-line intersection with the equilibrium curve (feed stage); for nonideal systems the pinch can occur in the rectifying section alone. R_min from the limiting slope: R_min = (L/V)_min / [1 − (L/V)_min]. Perfect-split closed forms for saturated liquid: R_min = 1/[z_F(α−1)]; saturated vapor: R_min = α/[z_F(α−1)] − 1.
- **Column pressure / condenser-type selection algorithm**: Set reflux-drum pressure so distillate can be condensed with available coolant (target ≥ 10–50°F above cooling-water supply, up to ~415 psia); assume 0–2 psi condenser ΔP and ~0.1 psi/tray column ΔP (0.05 psi/tray vacuum). Total condenser to ~215 psia; partial condenser 215–365 psia (also gives an extra equilibrium stage and/or vapor distillate); refrigerant above ~365 psia. Drop pressure (vacuum + refrigerant) only if bottoms temperature risks decomposition/polymerization/corrosion (e.g., ethylbenzene/styrene).
- **Reboiler selection**: Kettle (or vertical thermosyphon fed from the downcomer) = one full equilibrium stage; vertical thermosyphon fed from the bottom sump = fraction of a stage, take no credit. Thermosyphons favored for thermally sensitive bottoms, high pressure, small ΔT, or fouling.
- **Tray efficiency estimation** (Chapter 6 relations, adapted to distillation — efficiencies run higher than absorption because both components are near their boiling points so viscosity is low; >70% typical, can exceed 100% in large-diameter crossflow columns):
  - Drickamer-Bradford: E_o = 13.3 − 66.8 log μ (E_o in %, μ in cP, feed molar-average liquid viscosity at average tower T). Valid for hydrocarbon-like systems, μ ≈ 0.066–0.355 cP.
  - O'Connell (Lockhart-Leggett form): E_o = 50.3(αμ)^−0.226 (percent), with corrections for liquid flow path > 3 ft (Table 7.4: +10% at 4 ft up to +27% at 15 ft, for 0.1 ≤ αμ ≤ 1.0). Preferred when α is large; conservative 10–20% vs FRI valve-tray data.
  - Syeda-Afacan-Chuang (2007) point-efficiency model: partitions tray vapor into jets, small bubbles (E_SB = 1, at equilibrium), and large bubbles via a modified Froude number; E_OV = f_J·E_J + (1−f_J)[f_SB·E_SB + (1−f_SB)·E_LB], each from N_OG = −ln(1−E). Example 7.5 predicts E_OV = 0.782 vs FRI 0.818 for i-butane/n-butane at 165 psia. Available in ChemSep; Chan-Fair (1984) is the one in most simulators.
  - Oldershaw column scale-up: 1-in glass / 2-in metal Oldershaw data give E_OV that matches 4-ft FRI sieve-tray data (Fair, Null, Bolles) — use for nonideal/azeotrope-forming systems.
- **Tray hydraulics and column diameter**: Reuse Chapter 6 flooding (Fair) method at top and bottom trays; if diameters differ ≤ 1 ft use the larger, otherwise swage the column. Industrial columns run 80–85% of flood.
- **Reflux-drum sizing (flash-drum analog)**: Diameter from entrainment/flooding at f = 0.85 with F_ST = F_HA = F_F = 1.0; volume from 5-min liquid residence time, vessel half full: V_V = 2L·M_L·t/ρ_L. If H/D_T > 4, redimension to H = 4D_T, D_T = (V_V/π)^(1/3). Vertical drums for partial condensers (vapor-liquid disengagement); horizontal for total condensers. Keep ≥ 4 ft disengaging height, wire-mesh mist eliminator.
- **Rate-based packed-column methods (HETP and HTU)**: Unlike dilute absorption, λ = mV/L uses m = dy/dx, the local slope of the curved equilibrium line (not a constant K), and HETP varies across the feed where vapor/liquid traffic jumps.
  - HETP method: step off stages on McCabe-Thiele (EMD), get H_OG = H_G + λH_L per stage, HETP = H_OG·ln λ/(λ − 1), sum per section (Example 7.7: ~10 ft packing per section for the benzene-toluene split).
  - HTU method: no stepping; integrate V dy/[k_y a(y_I − y)] between sections, finding interfacial compositions by drawing tie lines of slope −k_x a/k_y a from the operating line to the equilibrium curve. Integrate in y when k_x a > k_y a (vapor-controlled), in x otherwise.
- **Not here: Fenske / Underwood / Gilliland / Kirkbride.** Those shortcut equations belong to multicomponent distillation (Ch 9). The binary analogs in this chapter are graphical: N_min from the total-reflux staircase, R_min from the pinch-point construction, feed stage from the staircase transfer point.

## Key Concepts
- **Reflux ratio (R = L/D)** and **boilup ratio (V_B = V̄/B)**: the two internal-circulation knobs; R is traditionally specified because distillate is usually the key product. Operating design range R/R_min ≈ 1.05–1.5 (low end for hard separations, high for easy; ~1.1–1.5 cited in the summary).
- **Constant molar overflow**: L and V constant within each section — the assumption that makes the operating lines straight and lets material balances alone drive the design; energy balances are then needed only for condenser/reboiler duties.
- **q-line**: encodes feed phase condition; pivot for locating the stripping operating line.
- **Pinch point**: operating line touching the equilibrium curve — infinite stages; at minimum reflux. Nonideal systems can pinch away from the feed stage; operating lines must never cross the equilibrium curve (a second-law violation, analogous to temperature crossover in a heat exchanger).
- **Total reflux / minimum stages**: D = B = 0, operating lines on the 45-degree line; also the standard condition for measuring tray efficiency.
- **Relative volatility α**: α = P₁ˢ/P₂ˢ for ideal systems (function of T only); y = αx/[1 + x(α−1)]; separation infeasible at or above the convergence pressure where α = 1.
- **Murphree vapor efficiency (E_MV)** and **point efficiency (E_OV)**: tray-by-tray vs local; linked through liquid mixing assumptions (complete mix / plug flow / partial mixing). Overall efficiency E_o = equilibrium stages / actual trays.
- **Subcooled reflux**: internal reflux exceeds external reflux — R_internal = R[1 + C_P,L ΔT_sub/ΔH_vap]; use the internal value or you overestimate stages (conservative, since subcooling actually helps).
- **Flooding velocity / percent of flood**: diameter-determining; design point 70–85%.
- **HETP / H_OG / HTU**: packed-height currency; HETP = H_OG ln λ/(λ−1) replaces the constant-m value used for absorption.

## Mental Models
- **Design vs simulation case**: McCabe-Thiele answers "what N and R achieve this split?" (design); the simulator answers "what split does this N, R, feed stage produce?" (simulation). Run McCabe-Thiele first, then use it to audit the simulator's feed-stage choice — ChemSep even overlays McCabe-Thiele plots on simulations.
- **The trade-off dial**: R and N are two ends of one dial anchored at the two limiting conditions (R_min at N = ∞, N_min at R = ∞). Every design is a point between them; economics picks it (optimal R/R_min ≈ 1.05–1.5, total annual cost minimum is flat, so design for flexibility above optimum).
- **The staircase never crosses the equilibrium curve**: any construction that would cross it is physically impossible — use this as the built-in sanity check for R_min and for nonideal pinch points.
- **Count what is an equilibrium stage**: partial reboiler = 1 stage, kettle reboiler = 1, sump-fed thermosyphon = 0, partial condenser = 1, total condenser = 0.

## Anti-patterns
- **Applying McCabe-Thiele outside its assumptions**: constant molar overflow requires equal latent heats, negligible sensible heat/heat of mixing, adiabatic column, uniform P. Outside that (or with a curved-equilibrium, nonideal system), trust a rigorous simulator — but still sketch the diagram to check feed-stage placement.
- **Specifying R and V_B independently**: they are coupled through the feed q; overspecifying both is inconsistent.
- **Ignoring feed-stage optimality in a simulator**: a wrong feed stage silently inflates N (Figure 7.10: 6.4 vs 5 stages); a McCabe-Thiele plot of the simulation reveals it immediately.
- **Using Drickamer-Bradford for large-α or non-hydrocarbon systems**: it fails for large α — use O'Connell (αμ form) instead.
- **Crediting a sump-fed thermosyphon reboiler as a stage**: it delivers only a fraction of a stage; taking credit under-designs the column.
- **Using absorption-style constant HETP/λ for distillation packing**: the equilibrium line is curved and traffic changes at the feed — λ = mV/L must be evaluated stage by stage.
- **Trusting total-reflux efficiency data at design reflux**: E_o measured at total reflux (L/V = 1) can differ from design-reflux efficiency; percent-of-flood matters.
- **Letting vacuum-limit decisions slide**: bottoms decomposition/polymerization forces vacuum (e.g., styrene); forgetting ethylene's critical temperature (48.6°F) means cooling water can never condense it — refrigerant required.

## Reference Tables

| Task | Method | Notes |
|---|---|---|
| N, feed stage for a binary split | McCabe-Thiele staircase | Design case; constant molar overflow |
| N_min | Staircase at total reflux | Operating lines on 45-degree line |
| R_min | Pinch-point construction; R_min = (L/V)_min/[1−(L/V)_min] | Closed form for perfect split, q = 1: 1/[z_F(α−1)] |
| Stage → trays | E_o (Drickamer-Bradford or O'Connell) or E_MV/E_OV models | Distillation E_o typically 70–100%+ |
| Diameter | Ch 6 flooding method, top and bottom trays | 80–85% of flood; swage if ΔD > 1 ft |
| Reflux/flash drum | Flooding dia. + 5-min residence time, half full | Vertical for partial condenser; H/D = 4 target |
| Packed height | HETP (stage-by-stage) or HTU (integration) | λ = mV/L with local slope m; prefer HTU |
| Multicomponent shortcuts | Fenske/Underwood/Gilliland/Kirkbride | NOT in this chapter — see Ch 9 |

Representative difficulty scale (Table 7.1): o-xylene/m-xylene α = 1.17 needs 130 trays at R/R_min = 1.12; benzene/toluene α = 3.09 needs 34 trays at 1.15; water/ethylene glycol α = 81 needs 16 trays. Rule of thumb: α < 1.05 → hundreds of trays; seek another separation method.

## Worked Example
**Example 7.1 — McCabe-Thiele for benzene-toluene at 1 atm.**
Given: F = 450 lbmol/h, z_F = 0.60 benzene (LK); x_D = 0.95, x_B = 0.05; feed % vaporized = D/F; Raoult's law VLE (α ≈ 2.35–2.6).
- Material balances: D = F(z_F − x_B)/(x_D − x_B) = 275 lbmol/h, B = 175; D/F = 0.611, so q = 1 − 0.611 = 0.389.
- q-line slope = q/(q−1) = −0.637 through (0.60, 0.60).
- (a) N_min: staircase between equilibrium curve and 45-degree line → **6.7 stages**.
- (b) R_min: rectifying line through (0.95, 0.95) and the q-line/equilibrium-curve intersection (x = 0.465, y = 0.684); slope 0.55 = R/(R+1) → **R_min = 1.22**.
- (c) R = 1.3 R_min = 1.59; operating-line slope 0.614; step off stages → **N = 13.2** (feed stage 7 from top; 12.2 trays + partial reboiler). At E_o = 0.8 → 16 actual trays.
- (d) CHEMCAD check with Raoult/Wilson/NRTL: 14 stages, feed at 8, x_D ≈ 0.955–0.957, x_B ≈ 0.068–0.070 — near-ideal system so all three K-value models agree closely.

## Key Takeaways
1. Binary distillation is economically viable when α > ~1.05 and no azeotrope blocks the split; distillation remains the most mature, most energy-hungry separation operation (40–60% of chemical/refining energy use).
2. The five McCabe-Thiele construction lines encode everything: equilibrium curve (VLE), two operating lines (material balances under constant molar overflow), q-line (feed condition), and the 45-degree reference.
3. Design is bounded by two asymptotes — N_min at total reflux, R_min at infinite stages — and the economic optimum lies at R/R_min ≈ 1.05–1.5, chosen low for hard (low-α) splits.
4. Feed thermal condition enters only through q; the optimal feed stage is where the staircase first passes the operating-line intersection P, and misplacing it costs stages even in a simulator.
5. Convert stages to hardware: O'Connell's E_o = 50.3(αμ)^−0.226 for overall efficiency, Oldershaw scale-up for nonideal systems, mass-transfer models (Syeda et al.) for point efficiency.
6. Set pressure first (coolant vs critical pressure vs bottoms decomposition limits), then condenser type (total ≤ 215 psia, partial 215–365 psia, refrigerant above), then reboiler type (kettle/downcomer-fed thermosyphon = 1 stage; sump-fed = 0).
7. Packed columns are sized with Chapter 6 hydraulics but distillation-specific HETP/HTU: λ = mV/L with the local equilibrium slope, and packing per rectifying and stripping section summed separately.

## Connects To
- **Ch 2**: Raoult's law / g^E / EOS models supply the y-x equilibrium curve and α that anchor the whole construction.
- **Ch 5**: cascade staging and the design-vs-simulation distinction (§5.6.4) that McCabe-Thiele instantiates.
- **Ch 6**: tray hydraulics, flooding, diameter sizing, Murphree efficiency definitions (6-41, 6-49), packed-column H_G/H_L correlations, and flash-drum sizing — all reused directly for distillation.
- **Ch 9-10**: Fenske-Underwood-Gilliland-Kirkbride shortcut and rigorous simulator methods extend these ideas to multicomponent systems; run McCabe-Thiele first even there.
- **Ch 13**: batch distillation, the historical form of the operation (alcoholic beverages, 11th century).
