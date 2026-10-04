# Chapter 10: Equilibrium-Based Methods for Multicomponent Separations

## Core Idea
Rigorous multicomponent, multistage separations are modeled by the MESH equations (Material balances, Equilibrium relations, mole-fraction Summations, entHalpy balance) written for a generalized equilibrium stage, then solved iteratively by equation-tearing (tridiagonal matrix, BP/SR methods) or simultaneous-correction (Newton–Raphson, SC method) procedures — with the inside-out method as the practical workhorse of modern simulators.

## Frameworks Introduced
- **MESH equation framework (generalized equilibrium stage, Figs. 10.1–10.2)**: N(2C+3) equations per N-stage cascade; each stage may carry a feed F, heat duty Q, liquid sidestream U, vapor sidestream W. Same stage model maps to absorbers, strippers, distillation, and (with liquid symbols swapped) extraction.
  - When to use / How: the universal starting point — every rigorous method is a different way of ordering and solving these same equations.
- **Degrees-of-freedom analysis and specification strategy**: simulators refuse to run until the fixed number of design variables is specified; condenser/reboiler type, N, stage locations, feed conditions (2 of T, P, vaporized fraction), pressure profile are mandatory; distillation takes two more specs (e.g., distillate rate + reflux ratio, or two key splits).
  - When to use / How: before every run; use Kremser (absorbers/strippers) or FUG/shortcut (distillation) to pick feasible specs and good initial guesses.
- **Tridiagonal-matrix (Thomas) algorithm**: substituting E into M and eliminating L via the total balance gives C linear N×N tridiagonal systems A_j x_{i,j-1} + B_j x_{i,j} + C_j x_{i,j+1} = D_j; solved by forward elimination (p_j, q_j recursions) and backward substitution.
  - When to use / How: the computational backbone of BP, SR, and inside-out inner loops; numerically stable because no subtraction of nearly equal quantities; fails only for extreme cases (many stages, absorption factor crossing unity) — Boston–Sullivan modification covers those.
- **Bubble-point (BP) method (Wang–Henke, 1966)**: after the tridiagonal solve, normalize x, update T_j by bubble-point calculations, then update flows by enthalpy balances. Works only for narrow-boiling, near-ideal systems (T insensitive to composition). Now used mainly for initialization.
- **Sum-rates (SR) method (Sujata; Burningham–Otto)**: after the tridiagonal solve, use unnormalized Σx to update L_j directly (sum-rates equation), get V_j from total balances, and solve the stage energy balances simultaneously (tridiagonal Newton–Raphson in T) for temperatures. Designed for wide-boiling absorbers/strippers; converges in a few iterations.
- **Simultaneous-correction (SC) method (Naphtali–Sandholm)**: reduce the MESH set to N(2C+1) equations in component flows v_{i,j}, l_{i,j} and T_j; solve all at once by Newton–Raphson with a block-tridiagonal Jacobian (blocks ordered by stage: H, M, E functions vs. v, T, l variables).
  - When to use / How: most robust choice for highly nonideal systems (azeotropic, extractive, three-phase, reactive, electrolyte); slower and needs decent initial guesses; flexible specs via discrepancy functions (e.g., replace reboiler-duty function with Σl_{i,N} − B = 0; Murphree efficiency replaces the E equations).
- **Inside-out method (Boston–Sullivan; Russell implementation)**: two-tier iteration — inner loop solves MESH with cheap approximate property models (K_b = exp(A − B/T), constant relative volatilities α_{i,j} = K_i/K_b, linear enthalpy departures, stripping factors S_{b,j} as iteration variables); outer loop updates the approximate parameters from the rigorous property models only occasionally.
  - When to use / How: default simulator method; fast (seconds) and flexible; may fail for highly nonideal liquids → fall back to SC, then relaxation/continuation (Kister) as last resort.
- **Isothermal sum-rates (ISR) method (Tsuboka–Katayama) for extraction**: stage temperatures specified, energy balances dropped; tear variable is extract flow V_j; K-values become distribution coefficients K_D = γ_L/γ_V (NRTL preferred); inner loop refines K_D from composition, outer loop updates V_j by sum-rates.
- **Classical stage-by-stage methods (historical)**: Lewis–Matheson (1932, stage requirements from key splits; outer-loop tear = nonkey product compositions, inner-loop tear = interstage flows) and Thiele–Geddes (1933, Case II specs — stages, reflux ratio, distillate rate; tear = T_j and V_j); both numerically unstable on computers, superseded by tridiagonal-based methods (Holland's theta method was a stable Thiele–Geddes variant).

## Key Concepts
- **MESH equations**: per stage — C material balances (10-1), C equilibrium relations y = Kx (10-2), two summations (10-3, 10-4), one enthalpy balance (10-5); all nonlinear (products of unknowns) → iterative solution required.
- **Tear variables**: quantities guessed to decouple equation groups (V_j and T_j in BP/SR; l_{i,j}, v_{i,j}, T_j in SC; approximate-model parameters in inside-out); updated each iteration until residuals vanish.
- **Tridiagonal matrix (TDM)**: the N×N banded system per component from the modified M equations; solved by the Thomas (modified Gaussian elimination) algorithm.
- **Block-tridiagonal matrix (BTDM)**: SC-method Jacobian — N×N array of (2C+1)×(2C+1) submatrices; Thomas algorithm generalized with matrix inversion/multiplication at each block row.
- **Jacobian / Newton–Raphson (NR)**: linearize f_i(X) about current guesses, solve (∂F/∂X)ΔX = −F for corrections, apply with damping factor t (X^{k+1} = X^k + tΔX).
- **Damping and acceleration**: when error grows, multiply corrections by 0.3–0.7 (or by numerically optimized t); mole fractions pulled back fractionally toward 0 or 1 to stay physical. Early SC iterations on purity specs may need t as low as 0.0156.
- **Convergence criterion**: normalized, squared, summed MESH residuals (or iteration-to-iteration changes in T, flows) compared to a tolerance based on N and C; simulators report error/tolerance per iteration.
- **Initialization (starting estimates)**: feed flash composition for all stages (narrow-boiling only), linear T profile from end-point bubble/dew points, linear flow profiles, first BP or SR iteration, or user-supplied profiles.
- **Discrepancy functions**: substitute equations (e.g., spec on bottoms flow B, reflux ratio L/D, Murphree efficiency) replacing H_1/H_N or E equations to enable flexible specifications.
- **Base component / stripping factor (inside-out)**: K_b from vapor-composition weighting; S_{i,j} = α_{i,j} S_{b,j}; scalar multiplier S_b forces reasonable component distribution during initialization.

## Mental Models
- **One stage model, many solvers**: BP, SR, SC, and inside-out all solve the same MESH equations; they differ only in which variables are torn, which equations are grouped, and how the property models are evaluated. Diagnosis of a convergence problem starts with "which solver matches this feed's boiling spread and ideality?"
- **Narrow-boiling vs wide-boiling dichotomy** (Friday–Smith): where T is insensitive to composition (narrow), bubble-point updates work (BP); where energy balances are T-sensitive (wide, absorbers), sum-rates updates work (SR); intermediate cases need SC.
- **Decouple cheaply, correct simultaneously**: tearing gives fast, low-memory inner loops; simultaneous correction buys robustness at the price of Jacobian work. Inside-out gets both by making property evaluation the expensive outer loop.
- **Convergence behavior as a diagnostic**: the error/tolerance trace tells the story — SR on a hydrocarbon absorber fell 407 → 0.08 in 4 iterations despite terrible guesses; SC on methanol purity specs needed heavy damping (t = 0.03) for 11 iterations before collapsing 4 orders of magnitude in 2 steps. Growing or plateauing error means bad specs or bad initialization, not a broken solver.

## Anti-patterns
- **Specifying the impossible**: stages or reflux below the minimum for the desired split; key splits that violate an azeotrope; pressure beyond the convergence pressure or outside the thermodynamic model's range; absorbent more volatile than the solute (or stripping agent less volatile); sidestream rates larger than the stage flow — all guarantee failure or wrong answers.
- **Relying on BP for wide-boiling feeds**: bubble-point temperatures are composition-sensitive there; use SR or inside-out instead.
- **Assuming default initialization suffices for SC**: SC methods converge poorly or not at all with poor initial guesses; for nonideal systems first converge with reflux ratio + bottoms flow specified, then switch to the purity specs using the converged profile as the new starting point.
- **Trusting Kremser/shortcut results with constant factors**: in Example 10.3 the Kremser assumptions (L/V from entering streams, K at average inlet temperature) were badly wrong because absorption raised stage temperatures to 161°F; use shortcut results only to seed the rigorous run.
- **Expecting near-pure sidestream products**: a sidestream is only pure if its K-value differs greatly from neighbors, or the reflux/boilup ratio is very large (Example 10.9's attempt at near-pure n-butane vapor sidestream failed).
- **Forgetting exothermic absorption**: condensation heat raises mid-column temperatures above both inlet streams; without an interstage cooler, absorption is throttled.

## Reference Tables
**Method applicability matrix**

| Method | Boiling spread | Ideality | Typical use | Cost/robustness |
|---|---|---|---|---|
| BP (Wang–Henke) | narrow | near-ideal | distillation; now mainly initialization | fast; fails wide-boiling |
| SR (Sujata/Burningham–Otto) | wide | near-ideal | absorbers, strippers | fast (≈4 iterations); poor for narrow |
| ISR (Tsuboka–Katayama) | n/a | nonideal (NRTL K_D) | isothermal liquid–liquid extraction | needs good composition estimates |
| SC (Naphtali–Sandholm) | any | any, incl. VLL/reactive/electrolyte | hardest problems; flexible specs | slow; needs decent initial guesses |
| Inside-out (Boston–Sullivan/Russell) | narrow to wide | ideal to moderately nonideal | simulator default for nearly everything | fastest; may fail highly nonideal |
| Relaxation/continuation (Kister) | any | any | last resort when SC and inside-out fail | ~10× compute time |

**Simulator models**: Aspen Plus — RadFrac (single columns, all methods), MultiFrac (interlinked, Petlyuk, heat-integrated), PetroFrac (crude/vacuum/FCC with side strippers, pumparounds, furnace). CHEMCAD — SCDS (SC method, single columns incl. reactive), TOWR / TOWR PLUS (inside-out; hydrocarbons, petroleum, divided wall). ChemSep — single equilibrium-stage model, SC method.

**Required simulator specs**: condenser/reboiler type (or none), total stages N (condenser = stage 1, reboiler = stage N), locations of all feeds/sidestreams/heat exchangers, feed composition + 2 of (T, P, vapor fraction), pressure profile. Absorbers/strippers need no additional specs; reboiled absorbers/strippers one (bottoms rate or key recovery); ordinary distillation two (from: D or B rate, reflux or boilup ratio, LK/HK splits, distillate vapor/liquid split, subcooling).

## Worked Example
**Example 10.1 — First BP iteration for a C3/nC4/nC5 column (Fig. 10.6)**: 5 equilibrium stages, total condenser, 100 psia, feed 100 lbmol/h of 30% C3 / 30% nC4 / 40% nC5 (saturated liquid) to stage 3; reflux ratio 2, bottoms L5 = 50 lbmol/h.
- Given → material balances: U1 = 50, L1 = 100, V2 = 150 lbmol/h; guessed linear T profile 65→165°F and constant V = 150 above the feed; K-values at each stage temperature.
- Method: build coefficients A_j, B_j, C_j, D_j from (10-8)–(10-11) for each component (e.g., for C3: A5 = 200, B5 = −549.5, C1 = 244.5, D3 = −30 lbmol/h) and solve the 5×5 tridiagonal system by the Thomas algorithm (p1 = −1.630, q5 = 0.0333, then back-substitute).
- Result: liquid mole-fraction profile per stage, e.g., x_C3 falls 0.566 → 0.033 down the column while x_nC5 rises 0.019 → 0.781; stage summations Σx = 0.78–1.22 ≠ 1, which is exactly the unnormalized state the BP method normalizes (narrow-boiling → bubble-point T update) and the SR method uses directly as flow-rate updates. This first iteration is the standard initialization for the more robust methods.

## Key Takeaways
1. Every rigorous method solves the same N(2C+3) MESH equations; methods differ in tearing strategy, iteration variables, and where property models are evaluated.
2. The Thomas-algorithm tridiagonal solve of the modified M equations is the shared core of BP, SR, and the inside-out inner loop; the SC method generalizes it to a block-tridiagonal Newton–Raphson Jacobian.
3. Match the method to the feed: narrow-boiling ideal → BP/inside-out; wide-boiling absorber/stripper → SR; highly nonideal (azeotropic, three-phase, reactive, electrolyte) → SC; extraction with specified temperatures → ISR.
4. Degrees of freedom are fixed and checked automatically — the user's job is feasibility: specs above minimum reflux/stages, absorbent less volatile than the solute, pressures within the model's range.
5. Use shortcut methods (Kremser for absorbers, FUG for distillation) to choose near-optimal specs and generate initial guesses; then converge the rigorous model and iterate on specs (e.g., first R and B, then the two purities).
6. Damping is normal, not failure: SC runs on purity specs routinely start with t ≈ 0.03–0.3 and only reach t = 1 near convergence; monitor the error/tolerance trace.
7. Profile inspection validates a design: mid-column temperature bulges in absorbers suggest intercoolers; pinched composition profiles or non-optimal feed stages (check with a McCabe–Thiele plot of the converged run) call for relocation.

## Connects To
- **Ch 6 (Kremser method)**: used to set absorbent flow/stage count for absorbers and extraction solvent ratios before rigorous simulation (Examples 10.3, 10.7, 10.12); Kremser predictions match rigorous results only when absorption factors are modest.
- **Ch 9 (FUG shortcut method)**: supplies N_min, R_min, actual stages, and feed-stage location used as rigorous-method specs and initial guesses (Example 10.5).
- **Ch 4 (flash calculations)**: feed flash generates constant-composition initialization profiles; bubble-/dew-point algorithms are reused for BP-method temperature updates.
- **Ch 2 (thermodynamic models)**: K-value and enthalpy correlations (EOS, Wilson/NRTL/UNIFAC, enthalpy departures) are the "rigorous" property models the inside-out outer loop must reproduce.
- **Ch 5 / Table 5.4 (cascade configurations)**: the generalized stage of Fig. 10.1 instantiates every configuration listed there (absorber, stripper, reboiled variants, ordinary distillation).
- **Ch 11 (enhanced distillation)**: when rigorous runs of nonideal systems fail to converge or splits are azeotrope-limited, residue-curve maps and extractive/pressure-swing/azeotropic techniques take over.
