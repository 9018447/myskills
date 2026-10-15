# Chapter 9: Approximate Methods for Multicomponent Distillation

## Core Idea
The Fenske–Underwood–Gilliland (FUG, Shortcut) method gives fast preliminary estimates of minimum stages, minimum reflux, actual stages, and feed-stage location for a multicomponent distillation from a specified split of two key components — still the standard first pass (in every process simulator) before rigorous stage-by-stage methods.

## Frameworks Introduced
- **FUG (Shortcut) method overall algorithm**: pick keys and splits → set pressure/condenser type → Fenske for N_min → non-key distribution at total reflux → Underwood for R_min → Gilliland for N at chosen R/R_min → Kirkbride for feed stage; iterate if non-key splits were guessed wrong (usually only 2–3 iterations).
  - When to use / How: preliminary design, parametric/synthesis studies, and initial guesses for rigorous simulator calculations. Specified variables: feed rate/composition/condition, stage pressures, LK and HK splits, R/R_min, condenser type.
- **Fenske equation (9-10/9-11/9-12)**: N_min at total reflux from the split ratio of LK vs HK and the geometric-mean relative volatility: N_min = log[(d_LK/d_HK)(b_HK/b_LK)] / log[(α_N·α_1)^(1/2)]. Independent of feed condition (no feed at total reflux); exact for N_min = 2. Also applied to every non-key component (vs. the HK as reference) to get product distributions at total reflux (9-14 to 9-16) — compute the smaller of d_i, b_i directly, the other by material balance.
- **Winn equation (9-13)**: improved Fenske for wide-boiling feeds where α varies strongly, using K_i = ζ·K_j^φ with constants fitted over the column T/P range (Aspen's DSTWU uses it as its default N_min method).
- **Underwood equations for R_min**: Class 1 (Shiras/Hanson/Gibson classification) — all feed components distribute, single pinch bridges the feed stage; equation (9-21) gives (L_∞)_min/F directly from feed composition and α at feed conditions, with (9-22) giving non-key distribution. Class 2 — solve Σ α_i,r f_i /(α_i,r − θ) = F(1−q) (9-28) for the required root(s) of θ (α_LK,HK > θ > 1 for keys only; one additional root between each adjacent pair of distributing components), then Σ α_i,r d_i/(α_i,r − θ) = D + (L_∞)_min (9-29) for R_min and unknown distributing d_i's. Internal → external R_min via enthalpy balance (9-23); equals internal under constant molar overflow.
  - When to use / How: Class 1 fits narrow-boiling feeds or non-sharp splits; wide-boiling "dumbbell" feeds are typically Class 2. Even when invalid, Class 1 R_min is a true upper bound (distributing non-keys only increase reflux demand).
- **Gilliland correlation (9-33 Molokanov fit; 9-35 Eduljee fit)**: empirical X–Y relation between (R−R_min)/(R+1) and (N−N_min)/(N+1), fitted to 61 rigorous-calculation data points, converting N_min and R_min into actual stages N at the chosen R. Molokanov: Y = 1 − exp[((1+54.4X)/(11+117.2X))·((X−1)/X^0.5)].
- **Kirkbride equation (9-37)**: empirical feed-stage split N_R/N_S = [(z_HK,F/z_LK,F)(x_LK,B/x_HK,D)²(B/D)]^0.206. Beats the Fenske-ratio method of Brown & Martin (9-36), but still rough — real columns get multiple feed nozzles.
- **Group (Kremser/Edmister) methods**: single-section cascade shortcut for absorption/stripping/extraction — covered in Ch 6; this chapter's FUG is the distillation counterpart.
- **Edmister method**: referenced approximate method for absorbers/strippers (Ch 6).

## Key Concepts
- **Light key (LK) / heavy key (HK)**: the two components bracketing the desired split; LK recovered mostly in distillate, HK mostly in bottoms. Splits of both must be specified for the design degrees of freedom.
- **Distributed vs. non-distributed components**: at total reflux all components distribute between products; at minimum reflux none or only a few non-keys distribute.
- **LLK / HHK (lighter-than-LK / heavier-than-HK non-keys)**: at minimum reflux they are stripped out before the pinch zones; stages between feed and each pinch exist mainly to remove them.
- **Class 1 vs. Class 2 separation (Shiras, Hanson, Gibson)**: Class 1 — all feed components appear in both products, single pinch at the feed; Class 2 — some components appear in only one product, two pinch points away from the feed (or the stripping pinch moves to the feed if all bottoms-side components appear there).
- **Mean/geometric-average relative volatility (α_i,j)_m**: square root of the product of top- and bottom-stage (or pinch-region) α values; the averaging that makes Fenske and the non-key distribution equations usable.
- **Pinch-point zone**: region of infinite stages at minimum reflux where passing-stream compositions equal equilibrium compositions; location determines which Underwood equation form applies.
- **Split ratio s_i = d_i/f_i**: recovery fraction form in which Fenske (9-12) and simulator recovery specs are written.
- **Dumbbell feed**: feed dominated by two widely different volatility components with traces of intermediates (e.g., the debutanizer: nC4 and nC8 are 82 mol%); a severe, ill-behaved test of FUG.
- **Internal vs. external reflux ratio**: Underwood gives the internal (pinch-zone) ratio L_∞/D; external reflux differs via an enthalpy balance (9-23) — can be substantially higher for wide-boiling feeds (Bachelor cites 55% higher).
- **Optimal R/R_min ≈ 1.3** (rule of thumb; ~1.10 for superfractionators, ~1.50 for easy splits); corresponding N/N_min ≈ 2. Fair & Bolles' true optimum ≈ 1.05 but the cost curve is flat above it.

## Mental Models
- **The FUG ladder**: three limiting calculations — N_min (total reflux, zero products), R_min (infinite stages), then interpolation (Gilliland) between them for the real design. Each step is independent of the details the others ignore.
- **Pinch-point geometry dictates the math**: where the operating line touches equilibrium decides whether one equation (Class 1, pinch at feed) or a root-finding scheme (Class 2, pinch away from feed) is needed.
- **Non-key distribution is a moving target**: Fenske (total reflux) says everything distributes; Underwood (minimum reflux) says almost nothing does; at the practical R/R_min ≈ 1.3 the Fenske total-reflux estimate is a good approximation (Stupin & Lockhart: at high R the non-key splits can even fall *outside* the two limits).
- **All shortcut answers are starting points**: FUG exists to seed rigorous simulator methods (Ch 10); a good initial guess of N (about 2×N_min) is essential because N must be fixed to force a split, whereas R can simply be varied during rigorous simulation.

## Anti-patterns
- **Applying Class 1 Underwood to a Class 2 system without checking**: Example 9.4 shows the Class 1 equation predicting negative distillate flows for heavy non-keys and iC4 distillate exceeding its feed — always test (9-22); if it fails, use the Class 2 root-finding procedure.
- **Trusting Underwood R_min for wide-boiling feeds**: constant-α and constant-molar-overflow assumptions between pinches can be badly violated (0.521 computed vs. 0.637 rigorous for the debutanizer — the hot feed vaporizes across the feed zone, effectively lowering q).
- **Using Gilliland when stripping dominates rectifying**: the correlation is built on reflux, ignores boilup; Oliver's example errs 34% low (10.3 vs. 15.7 exact) for a dilute bottoms-specified separation.
- **Using the Fenske-ratio (Brown & Martin) feed-stage rule**: badly wrong for asymmetric splits (0.64 vs. 0.083 exact in Oliver's test); prefer Kirkbride, but verify with rigorous runs and multiple feed nozzles.
- **Applying Fenske/Underwood to nonideal, azeotrope-forming systems**: constant-α assumptions break down; FUG is for ideal/nearly ideal mixtures.
- **Assuming internal R_min = external R_min**: only true under constant molar overflow; otherwise an enthalpy balance (9-23) is required.

## Reference Tables

| Method | Gives | Requires | Applies when |
|---|---|---|---|
| Fenske (9-11/9-12) | N_min; non-key splits at total reflux | LK/HK splits, geometric-mean α | Ideal/near-ideal; any feed state (no feed) |
| Winn (9-13) | N_min (better for wide-boiling) | ζ, φ constants from K-value fits | α varies strongly top-to-bottom |
| Underwood Class 1 (9-21) | R_min (internal), non-key splits | feed composition, α at feed | All components distribute (narrow-boiling / non-sharp split) |
| Underwood Class 2 (9-28/9-29) | R_min + unknown distributing d_i | roots θ in intervals between distributing α's | Not all components distribute |
| Gilliland (9-33 Molokanov / 9-35 Eduljee) | N at specified R | N_min, R_min, R/R_min | Preliminary only; fails when stripping ≫ rectifying |
| Kirkbride (9-37) | N_R/N_S feed split | feed/product compositions, B/D | Better than Fenske ratio, still approximate |

Typical Gilliland fit accuracy: 61 data points (Gilliland, Brown–Martin, Van Winkle–Todd) spanning 2–11 components, α 1.11–4.05, q 0.28–1.42, R_min 0.53–9.09, N_min 3.4–60.3. Eduljee's Y = 0.75(1 − X^0.5668) fits everywhere except the end points.

## Worked Example
Debutanizer of Figure 9.3 (alkylation-unit effluent; feed 876.3 lbmol/h, 13.4 mol% vaporized at 74 psia; LK = nC4, HK = iC5; specified: d/b of nC4 = 442/6, iC5 = 13/23; SRK K-values):

1. **Pressure/condenser (Ex 9.1)**: distillate bubble point at 120°F → 70 psia → total condenser; bottoms 77 psia bubble point 334°F (acceptable).
2. **Fenske (Ex 9.2)**: α top = 1.009/0.458 = 2.203, α bottom = 5.425/3.440 = 1.577 → (α)_m = 1.864. N_min = log[(442/6)(23/13)]/log(1.864) = 2.115/0.2704 = **7.82**.
3. **Non-key distribution at total reflux (Ex 9.3)**: via (9-15)/(9-16) vs. the HK — e.g., iC4 bottoms 0.028 lbmol/h, nC5 distillate 1.97 lbmol/h; totals D = 468.95, B = 407.35.
4. **Underwood Class 2 (Ex 9.5)**: Class 1 check (Ex 9.4) fails (negative d's for heavy non-keys), so only nC5 distributes besides the keys → two roots: θ₁ = 1.0443 (between α_LK,HK 1.864 and 1.0), θ₂ = 0.8587 (between 1.0 and 0.845). Solve three linear equations (9-29 twice + Σd_i = D): d_nC5 = 3.5, D = 470.5, (L_∞)_min = 244 → **R_min = 0.521** (rigorous: 0.637; Bachelor).
5. **Gilliland (Ex 9.6)** at R/R_min = 1.3: X = (0.677−0.521)/(0.677+1) = 0.0932 → Y = 0.5607 → **N = 19.1** equilibrium stages (including partial reboiler). Notably, N = 17.8–19.1 across all three R_min estimates — N is insensitive to R_min error.
6. **Kirkbride (Ex 9.7)**: N_R/N_S = [(0.0411/0.5112)(0.0147/0.0278)²(407.35/468.95)]^0.206 = 0.444 → 5.6 stages above, 12.5 below the feed (reboiler + 13 stripping + 6 rectifying) — more stripping stages because the LK split is much sharper than the HK split.
7. **Simulator check (Ex 9.8)**: Aspen DSTWU / CHEMCAD SHOR / ChemSep FUG at R/R_min = 1.3 give N_min ≈ 7.6–8.8, R_min ≈ 0.545–0.608, N ≈ 16.2–19.9, feed stage ≈ 4.6–5.9 from top — consistent with hand calculations.

## Key Takeaways
1. FUG = Fenske (N_min at total reflux) → Underwood (R_min at infinite stages) → Gilliland (N at R > R_min) → Kirkbride (feed stage); the standard preliminary design pass and the standard initial guess for rigorous simulation.
2. The Fenske equation uses only the LK/HK split and geometric-mean α, and doubles as a non-key distribution estimator at total reflux — compute the smaller product flow directly, the other by material balance.
3. Classify the separation before Underwood: Class 1 (single pinch at feed, all distribute) vs. Class 2 (solve for roots θ, one per distributing component pair); a Class 1 R_min is still a valid upper bound even for Class 2 systems.
4. Underwood's R_min is an *internal* pinch ratio sensitive to q and the constant-molar-overflow assumption; wide-boiling/hot feeds make it low — convert to external with (9-23) and treat results skeptically.
5. N is remarkably insensitive to errors in R_min (19.1 vs. 17.8 over a 40% R_min spread in the debutanizer), which is why the FUG method tolerates its own approximations.
6. Rule of thumb: R/R_min ≈ 1.3 (giving N/N_min ≈ 2), R ≈ 1.10 for superfractionators, 1.50 for easy splits; the cost optimum curve is flat, so precision in R_min matters less than stage count.
7. Know the failure modes: Gilliland under-predicts when stripping dominates (ignores boilup); Kirkbride and the Fenske-ratio feed-stage rules are rough for asymmetric splits; all FUG equations assume near-ideal VLE.

## Connects To
- **Ch 6**: Kremser and Edmister group methods — the same shortcut spirit applied to absorption/stripping/extraction cascades.
- **Ch 7**: binary McCabe–Thiele background for pinch points, minimum reflux, and R/R_min economics; Figure 7.17 for pressure/condenser selection and Figure 7.18 for condenser types.
- **Ch 5**: degrees-of-freedom analysis (2N + C + 9 specifications for the design case) that dictates which splits must be specified.
- **Ch 10**: the rigorous destination — FUG results seed sum-rates, inside-out, and simultaneous-correction methods; the debutanizer is solved rigorously there.
- **Ch 1 (§1.8.2)**: sequencing heuristics (Heuristics 2–4) that determine which column and which keys come first in the separation sequence.
