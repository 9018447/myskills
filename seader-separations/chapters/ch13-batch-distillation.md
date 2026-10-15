# Chapter 13: Batch Distillation

## Core Idea
Batch distillation has no steady state: a finite charge (pot charge) is boiled off while pot composition depletes and still temperature rises, so design means choosing a reflux policy, stage count, and a time-sequenced set of cuts rather than a single operating point. The chapter builds from the Rayleigh equation for a single-stage still up to rigorous stiff-DAE simulation of multicomponent rectifiers with holdup.

## Frameworks Introduced
- **Differential (Rayleigh) distillation**: no reflux; still pot is the only equilibrium stage; instantaneous vapor in equilibrium with perfectly mixed residue. Component balance d(Wx_W)/dt = −D·y_D integrates to ∫dx/(y−x) = ln(W/W₀). Use for wide-boiling mixtures (HCl–H₂O, H₂SO₄–H₂O, NH₃–H₂O) where one stage suffices.
  - Closed forms: constant K → ln(W/W₀) = ln(x/x₀)/(K−1); constant α → the two-log binary form. Graphical/numerical integration of 1/(y−x) vs x when equilibrium is tabular.
  - Multicomponent covariance form: ln(M_i/M_i0) = α_i,j·ln(M_j/M_j0) for constant relative volatility — instantly shows how much impurity of the heavy key rides along for a given vaporization of the light key.
- **Batch rectification at constant reflux (Smoker–Rose method)**: fix R (hence L/V) and stage count; step off McCabe–Thiele stages repeatedly as x_W falls to generate x_D(x_W) pairs, then integrate the Rayleigh equation graphically. Easiest to implement (flow sensors respond fast); distillate purity is above spec early, below spec late.
  - Block's time equation: t = (R+1)(W₀ − W_t)/V.
- **Batch rectification at constant distillate composition (Bogart method)**: hold x_D fixed, continuously raise R (or cut D) as the pot depletes; W = W₀(x_D − x_W₀)/(x_D − x_W); time by integrating dx_W/(1−L/V)(x_D−x_W)². Needs a fast composition sensor; justified mainly for large systems. Terminate when R → total reflux against the final x_W.
- **McCabe–Thiele adaptation to batch**: same construction as continuous columns, but the operating line of fixed slope pivots with the moving pot composition (constant-R) or a rising-slope line slides down at fixed x_D (constant-composition). Minimum stages estimated at total reflux for the final pot composition.
- **Multicomponent batch stoichiometry (slop/intermediate-cut strategy)**: LK cut → intermediate (slop) cut → HK residue; slop cut is recycled into the next charge. Slop fraction grows sharply as relative volatility (or reflux ratio) falls; ternaries need multiple slop cuts with termination specs found by simulation trial.
- **Rigorous stage-by-stage DAE model (Meadows/Distefano, Boston et al.)**: equilibrium stages, perfect mixing, negligible vapor holdup, constant molar liquid holdup M per stage, adiabatic stages. C(N+2) ODEs for liquid mole fractions plus algebraic total balances, enthalpy balances, K-value, sum, and holdup equations; initialized from a total-reflux steady state, then stepped through operation steps (cut → dump receiver → new spec).
- **Stiffness/numerical-integration control**: holdup on trays is tiny vs the reboiler, so eigenvalues of the Jacobian span orders of magnitude. Explicit Euler needs Δt ≤ 1/|λ|max (oscillation criterion); implicit Euler is unconditionally stable but truncation-error limited (Example 13.6: Δt 40× larger than explicit limit still accurate). Gear-type implicit methods (ode15s, ODEPACK) are the practical choice; stiffness ratio SR ≈ 2[(L+K_light·V)/(L+K_heavy·V)]·(M⁰_reboiler/M_tray), SR ≳ 1000 = stiff.
- **Optimal control of reflux ratio (§13.7)**: Diwekar's objectives — maximize distillate in fixed time, minimize time for fixed distillate, or maximize profit — solved by calculus of variations / Pontryagin maximum principle / Bellman dynamic programming / NLP. The optimal R{t} curve rises less sharply than constant-composition control and beats both simple policies most on difficult separations.

## Key Concepts
- **Rayleigh equation** — ln(W/W₀) = ∫dx_W/(y_D − x_W); the single governing material balance of all batch calculations.
- **Pot charge / residue (W)** — moles of liquid in the still; subscript 0 = initial charge; W depletes, x_W falls, T_rises monotonically.
- **Constant reflux (constant-R) operation** — x_D decays with time; average distillate found by overall balance x_D,avg = (W₀x₀ − W_t·x_Wt)/(W₀ − W_t).
- **Variable (constant-composition) reflux** — R rises through the run; instantaneous distillate rate dD/dt = V(1 − L/V) falls toward zero at the total-reflux limit.
- **Cut points / product, slop, and residue cuts** — receivers are switched at purity break points; slop cuts recycle to the next charge.
- **Liquid holdup (M_j)** — trays/condenser holdup depletes light material from the pot before withdrawal (total-reflux startup), lowering initial purity; effects are conflicting and best judged case-by-case by rigorous simulation; trayed > packed impact.
- **Stiffness ratio (SR)** — |λ|max/|λ|min from the Jacobian; measures tray-vs-reboiler holdup and K-value spread; governs integrator choice.
- **Block equation** — batch time from constant boilup: t = (R+1)(W₀ − W_t)/V.
- **Batch stripper / complex batch column** — accumulator-fed column stripping volatile impurities into a bottoms cut; the complex (middle-vessel) unit of Hasebe/Barolo/Phimister–Seider rectifies and strips simultaneously.
- **BatchSep (Aspen Plus) / CC-BATCH (CHEMCAD)** — simulator models; per operation step specify two modes (e.g., reflux ratio + boilup rate) and a stop criterion; converge most reliably by stopping on time.

## Mental Models
- **The pot as an integrator**: the Rayleigh equation is just "whatever leaves must have been in the pot"; every batch method (graphical, algebraic, simulator) reduces to integrating that balance against a time-varying equilibrium relation.
- **The slop cut as a volatility tax**: impurity you cannot avoid is diverted into a recycled intermediate cut; you pay either reflux ratio/stages (to shrink it) or recycle time (to tolerate it).
- **Time-varying operating line**: a batch rectifier is a continuous column whose operating line and product spec slide with the pot composition; each instant is a McCabe–Thiele snapshot.
- **Scale separation = stiffness**: small tray holdups respond in seconds, the reboiler in hours; the model inherits both time constants, so integrator selection is part of the design, not an afterthought.

## Anti-patterns
- **Treating differential distillation as adequate for close-boiling binaries**: at α ≈ 2 and 50% vaporization, ~29% of the heavy component vaporizes with the light (Example 13.3); a sharp single-stage cut needs α ≥ 100. Add stages, not optimism.
- **Cutting on instantaneous distillate purity for the accumulator spec**: accumulated (average) purity is what ships; the instantaneous x_D crashes to near zero within ~0.5 h after breakthrough (Example 13.7), so stop on receiver-average composition, not the momentary value.
- **Ignoring holdup because it is "a few percent"**: when holdup/charge exceeds a few percent — especially with dilute light components — purity, cut sizes, cycle time, and energy all degrade; total-reflux startup also strips light material out of the pot before the first drop is taken.
- **Explicit Euler with a hand-picked time step on the DAE system**: instability shows up as mole fractions >1 or negative within a handful of steps (Example 13.6); without the |λ|max criterion the results are garbage with no warning.
- **Specifying an unreachable stop criterion**: e.g., demanding 90 mol% C7 instantaneously at R = 4 when only 88% is achievable; some specs are infeasible — screen by simulating with time-based stops first.
- **Assuming constant-composition control is always optimal**: for easy separations the extra sensor/control cost is not justified; constant-R wins on simplicity, and optimal-R saves the most only on difficult splits.

## Reference Tables

| Feature | Constant reflux (Smoker–Rose) | Constant distillate composition (Bogart) | Optimal control |
|---|---|---|---|
| Held constant | R (L/V), boilup V | x_D, boilup V | neither — R{t} optimized |
| Varies with time | x_D falls, x_W falls | R rises (→∞ at end), D rate falls | R{t}, x_D{t} both |
| Sensing required | flow only | fast composition sensor | composition + optimizer |
| Implementation | easiest | moderate/harder | hardest (optimization) |
| Key equations | Rayleigh graphic + t=(R+1)(W₀−W)/V | W = W₀(x_D−x_W₀)/(x_D−x_W); time integral (13-17) | variational/Pontryagin/DP/NLP |
| Typical outcome | purity straddles spec; needs slop cut | ~2.6–8% more distillate or less time (Ex. 13.11) | best on difficult separations |

| α_A,B (differential, 50% A vaporized) | % B vaporized | x_B in distillate |
|---|---|---|
| 2 | 29.3 | 0.369 |
| 5 | 12.9 | 0.206 |
| 10 | 6.7 | 0.118 |
| 100 | 0.69 | 0.014 |
| 1,000 | 0.07 | 0.0014 |

## Worked Example
**Example 13.1 — Differential distillation of benzene–toluene (Rayleigh).**
Given: 100 kmol equimolar charge, constant boilup D = 10 kmol/h, α = 2.41 at 101.3 kPa.
Method: solve the constant-α Rayleigh form (13-5) for W at descending x_W (0.5 → 0.05 in 0.05 steps); get time from t = (W₀ − W)/10; instantaneous vapor from y = αx/[1+(α−1)x]; average distillate from the overall balance (13-6) x_D,avg = (W₀x₀ − Wx)/(W₀ − W); pot temperature from T–x–y data.
Result: e.g., at t = 3.75 h, W = 62.5 kmol, x_W = 0.40; at t = 9.35 h, W = 6.5 kmol, x_W = 0.05. Pot temperature climbs from ~92 °C (x_B = 0.5) toward the toluene end while y_D falls from 0.713 — quantifying the decay of a simple still with no reflux. Example 13.2 repeats this with tabular T–x–y data via trapezoidal integration of 1/(y−x) vs x (W = 62.5 kmol at x = 0.4), showing constant-α agrees within ~10% at low x.

## Key Takeaways
1. Batch distillation is inherently transient — no steady state; pot composition falls, temperature rises, and distillate composition drifts, so all design is in the time domain.
2. The Rayleigh equation ∫dx/(y−x) = ln(W/W₀) is the universal skeleton; closed forms exist for constant K or α, otherwise integrate graphically/numerically or simulate.
3. Differential distillation alone only separates wide-boiling mixtures; sharp binary cuts require a rectifying column plus a slop-cut policy, with slop fraction rising as α or R falls.
4. Choose the reflux policy by economics and instrumentation: constant-R for simplicity, constant-x_D for larger units with composition sensing, optimal R{t} for difficult separations.
5. Liquid holdup (a few percent of charge or more, dilute lights, trayed columns) degrades purity and cuts; quantify it with the rigorous Distefano/Boston DAE model, not hand corrections.
6. Rigorous batch models are stiff (SR ≈ 10³–10⁶ from tray-vs-reboiler holdup and K spread): use implicit/Gear integrators (ode15s, ODEPACK; BatchSep/CC-BATCH defaults), never naive explicit stepping.
7. Operation is a sequence of steps (total-reflux startup → cuts → receiver dumps), each with two specifications and a stop criterion; stop on time first, then refine to purity-based stops.

## Connects To
- **Ch 7 (VLE / single-stage flash)**: Rayleigh distillation is the differential limiting case of the flash; same y = Kx and α relations, applied incrementally.
- **Ch 9 (binary distillation, McCabe–Thiele)**: batch rectification reuses the stage-stepping construction with a moving operating line; total-reflux shortcut estimates minimum stages.
- **Ch 10 (rigorous multicomponent methods / tridiagonal algorithm)**: the Distefano DAE model is the transient extension of continuous-column stage equations; implicit-Euler leads to tridiagonal solves per component, and Boston et al. adapt the inside-out algorithm.
- **Ch 12 / batch separations context**: batch operation economics — when capacity, product variety, fouling solids, or upstream batchwise operation make a continuous column the wrong tool.
- **Optimization (Diwekar; Ch 7.3.7 reflux economics)**: optimal R{t} replaces the single steady-state economic optimum of continuous distillation with an optimal-control trajectory.
