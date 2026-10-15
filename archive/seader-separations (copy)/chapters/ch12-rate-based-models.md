# Chapter 12: Rate-Based Models for Vapor-Liquid Separation Operations

## Core Idea
Rate-based (nonequilibrium) models replace the equilibrium-stage assumption with actual mass- and heat-transfer rates across a vapor-liquid interface, computing real trays and packing segments directly (with phase equilibrium assumed only at the interface), then back-calculating Murphree efficiencies or HETP values for comparison with equilibrium-stage shortcuts.

## Frameworks Introduced

- **Nonequilibrium (rate-based) stage model — MERSHQ equations**: The equilibrium-stage MESH set (2C+3 per stage) is replaced by separate liquid- and vapor-phase balances. Per stage: 5C+5 independent equations (M = component material balances for each phase, 2C; total material balances, 2; E = phase energy balances, 2, plus E^I interface heat-balance continuity, 1; R = mass-transfer-rate residuals, 2(C-1); S = mole-fraction summations applied at the interface, 2; Q = interface phase-equilibrium relations K·x^I − y^I = 0, C; plus the optional H hydraulic/stage-pressure-drop equation, making 5C+6 when stage pressures are computed). Degrees of freedom: N_D = 2NC + 9N + 1.
  - When to use / How: For rigorous tray and packed-tower design (real trays, diameters, pressure drops) in ChemSep, Aspen Plus RateSep (RadFrac), or CHEMCAD SCDS mass-transfer option.
- **Simultaneous-correction (SC) solution method**: Newton method in the style of Naphtali–Sandholm — variables and equations grouped by stage so the Jacobian is block-tridiagonal; analytical partial derivatives; residuals (12-48) or fractional variable corrections (12-49, default ε = 10⁻⁴) as convergence tests; step limiting (10 K temperature, 50% flows) to prevent oscillation.
  - When to use / How: 5C+6 (or 5C+5) equations per stage vs. only 2C+1 for equilibrium models; total computing time typically under an order of magnitude greater than equilibrium-based, often under 1 minute.
- **Maxwell–Stefan multicomponent diffusion / binary-pair mass-transfer coefficients**: Multicomponent fluxes are coupled — J^V = c_t^V[κ^V](y^V − y^I)_avg via a (C−1)×(C−1) matrix of Maxwell–Stefan mass-transfer coefficients [κ^P], obtained by inverting the reciprocal rate function [R^P] built from binary-pair coefficients k_ij (12-31, 12-32). For the liquid, [κ^L] = [R^L]⁻¹[Γ^L] with a thermodynamic-factor matrix [Γ^L] correcting for nonideality (driving force is the chemical-potential gradient, not the mole-fraction gradient). J for the Cth component follows from ΣJ_i = 0.
  - When to use / How: Mandatory for rigorous multicomponent rate models (Taylor & Krishna); coupling effects can be appreciable, though off-diagonal terms may be small in near-ideal ternaries.
- **Two-film mass/heat transfer with interfacial equilibrium**: Rates N_i = a_j^I·J_i + (bulk-flow/convective term y_i·N_T or x_i·N_T) combine diffusive and convective contributions. Heat rates e^V, e^L use convective coefficients plus enthalpy carried by mass transfer; e^V = e^L at the interface. Vapor h from the Chilton–Colburn analogy; liquid h from penetration theory.
  - When to use / How: Interfaces are the only place of equilibrium; bulk phases are subcooled liquid / superheated vapor at different temperatures (unlike equilibrium models where both phases share the stage temperature).
- **Bootstrap problem**: Knowing diffusion fluxes J, the total mass-transfer rate N_T needed to get component rates N_i comes from an energy balance (change in molar vapor rate across the tray); N_T = 0 only under constant molar overflow. In reactive diffusion, stoichiometry sets it.
- **Tray/packing hydraulics & transport correlations**: Number of transfer units N_V = k^V·a·h_f/u_s and N_L (12-40, 12-41); interfacial area a^I = a·h_f·A_b. Tray correlations (AIChE, Hughmark, Chan–Fair, Chen–Chuang, Garcia–Fair, Syeda et al./Vennavelli et al. for sieve; Scheffe–Weiland for valve); packing correlations (Onda–Takeuchi–Okumoto, Bravo–Fair, Bravo–Rocha–Fair for structured, Billet–Schultes semi-theoretical requiring 5 packing parameters). Column diameter from percent flooding or pressure-drop spec.
- **Vapor/liquid flow-pattern models**: Perfectly mixed (small-diameter trayed columns, Oldershaw columns), plug flow (packed towers; Kooijman–Taylor integration correction), and partial liquid mixing via a turbulent Peclet number with the Bennett–Grimm eddy-diffusivity correlation. Reactive distillation: the multicell (mixed-pool) model of Higler–Krishna–Taylor, e.g. 5×5 = 25 perfectly mixed cells per tray, in ChemSep.
- **ChemSep non-equilibrium column cases**: Two options — the rate-based model (computes actual trays, back-calculates Murphree vapor tray efficiencies; handles packed segments, sizes diameter/pressure drop) and the stage-efficiency model (MESH equations with the K-value relation replaced by the Murphree efficiency 12-3, from correlations, O'Connell, or user values). Also does liquid-liquid extraction. Back-calculate E_MV tray by tray and HETP for packing after convergence.

## Key Concepts
- **Nonequilibrium stage**: tray, group of trays, or packed-segment element; stages numbered top-down; condenser is stage 1 even if total.
- **Interface equilibrium (Q^I residual)**: K-values used only at the vapor-liquid interface; evaluated at interface T, composition, and tray pressure.
- **Maxwell–Stefan equations**: fundamental multicomponent diffusion theory (1866–1871); reciprocal diffusivity/rate-coefficient form.
- **Component-coupling effects**: flux of one component depends on driving forces of others through binary-pair coefficients; can seriously affect results.
- **Effective diffusivity / binary-pair coefficients k_ij**: experimental binary mass-transfer coefficients combined through [R]⁻¹.
- **Thermodynamic factor [Γ^L]**: δ_ij + x_i(∂ln γ_i/∂x_j) corrects liquid nonideality; substitute fugacity coefficient Φ for equation-of-state models.
- **Number of transfer units (N_V, N_L)** and froth interfacial area — the correlation currency for trays.
- **Standard specifications**: for distillation use L₁ (reflux) and L_N (bottoms) instead of Q₁^V, Q_N^L; for adiabatic absorbers/strippers all Q = 0. Basic 5N specs: r^L or U_j, r^V or W_j, P_j, Q_j^L, Q_j^V.
- **Back-calculated E_MV and HETP**: from converged rate solutions — diagnostic of real stage performance; packed towers use segment-wise HETP profiles.
- **Bootstrap problem**: closing the diffusive-to-total rate conversion via the total rate N_T.

## Mental Models
- **Equilibrium is a bookkeeping fiction; the interface is real**: an equilibrium-stage model lumps all resistance into an efficiency; a rate-based model computes actual fluxes and lets efficiency emerge as output.
- **The tray as a coupled two-film exchanger**: mass transfer in each film, heat transfer in each film, equilibrium gluing them only at the interface — everything else (bulk phases) is off-equilibrium.
- **Matrices, not scalars**: in multicomponent diffusion you invert a matrix of reciprocal binary coefficients; treating a ternary as independent binaries is structurally wrong.
- **Rate-based costs geometry, not just thermodynamics**: diameter, weir height, froth height, packing parameters all enter the equation set — the model is only as good as the hydraulics correlations.

## Anti-patterns
- **Specifying impossible pairs**: RateSep, SCDS mass-transfer option, and ChemSep flexibility lets inexperienced users specify conditions that cannot converge (e.g., N below N_min for the required purities). Start with standard specs (reflux ratio + bottoms flow rate) before using flexible/advanced string specifications.
- **Assuming constant molar overflow to close the bootstrap**: valid only as an approximation; in real distillation N_T is set by the energy balance and may be far from zero (Example 12.1: N_T^V = −54 lbmol/h).
- **Ignoring coupling corrections**: skipping the thermodynamic factor for nonideal liquids or the high-flux (composition-profile distortion) correction can seriously skew results.
- **Using one flow pattern for everything**: perfectly mixed bulk phases simulate only small-diameter columns; packed towers need plug flow with segment integration; large trayed towers need partial mixing (Peclet/Bennett–Grimm).
- **Reading a single E_MV number too literally**: back-calculated efficiencies vary per component and per tray (Example 12.2: MEK ranged −3.23 to 1.14); treat medians with engineering judgment, and discard outliers.

## Reference Tables

| Aspect | Equilibrium-stage model | Rate-based (nonequilibrium) model |
|---|---|---|
| Equations per stage | 2C + 3 (MESH) | 5C + 5 (5C + 6 if pressures computed) |
| Phase equilibrium | Whole stage (T_j, P_j) | Only at the interface |
| Balances | Combined vapor+liquid per stage | Separate L and V phase balances |
| Efficiencies | User-supplied input | Back-calculated output (E_MV, HETP) |
| Extra data needed | K-values, enthalpies | + binary-pair mass-transfer coefficients, interfacial area, heat-transfer coefficients, tray/packing geometry, ΔP correlations |
| Jacobian | Block-tridiagonal (Naphtali–Sandholm) | Block-tridiagonal (SC method), analytical derivatives |
| Computing time | Baseline | Per-iteration and iteration count 3–4× and 2–3× larger; total usually < 10× equilibrium, often < 1 min |
| Bulk-phase states | Vapor at dew point, liquid at bubble point, same T | Subcooled liquid, superheated vapor, different T |

## Worked Example
**Example 12.2 — Extractive distillation (n-heptane/toluene with MEK solvent, ChemSep rate-based):**
Given: n-heptane/toluene cannot be split at 1 atm by ordinary distillation; sieve-tray column, 20 trays, total condenser + partial reboiler, condenser outlet 14.7 psia, reflux ratio 1.5, bottoms 45 lbmol/h. Feed 1 (tray 10 from top): 55 lbmol/h n-heptane + 45 lbmol/h toluene + 100 lbmol/h MEK, saturated liquid at 20 psia. Feed 2 (tray 15): 100 lbmol/h MEK, saturated liquid. UNIFAC for liquid activity coefficients; Chan–Fair mass-transfer correlation; plug flow for vapor, mixed flow for liquid; 85% flooding; 0.5 m tray spacing, 2-in weir.

Converged in 8 iterations (variables auto-initialized). Result: distillate = 54.87 n-heptane + 0.45 toluene + 199.68 MEK lbmol/h; bottoms = 0.13 + 44.55 + 0.32. Back-calculated Murphree efficiencies (median): n-heptane 0.73, toluene 0.79, MEK 0.76 (ranges 0.52–1.10, 0.70–0.79, −3.23–1.14). The 20 trays ≈ 15 equilibrium stages. Sizing: three sections (9/5/6 trays) with diameters 1.75, 1.74, 1.83 m → choose 1.83 m; average ΔP = 0.06 psi/tray; condenser 2.544 MW, reboiler 2.482 MW.
**Example 12.3 (packed version)**: FLEXIPAC 2 structured packing at 75% flooding (13/6.5/6.5 ft heights, 50 segments per 6.5 ft, mixed flow both phases) converged in 26 iterations with a slightly better split; median HETP ≈ 0.55 m (n-heptane), 0.45 m (toluene), 0.5 m (MEK).

## Key Takeaways
1. Rate-based models (available since the late 1980s) are more accurate than equilibrium-based models because they carry rigorous multicomponent mass-transfer coupling, hydraulics, and real internals geometry.
2. The MERSHQ equation set (5C+5 or 5C+6 per stage) uses separate phase balances; phase equilibrium survives only at the interface.
3. Multicomponent rates require the Maxwell–Stefan binary-pair framework — invert [R], apply the thermodynamic factor to nonideal liquids — never independent binary treatments.
4. Transport coefficients, interfacial area, and heat-transfer coefficients come entirely from empirical correlations; the choice (Chan–Fair, Chen–Chuang, Billet–Schultes, etc.) and the flow-pattern assumption materially affect results.
5. Solution is by the simultaneous-correction (Naphtali–Sandholm-style) method; cost is typically less than an order of magnitude above equilibrium models, often under a minute.
6. Back-calculated Murphree efficiencies and HETP profiles from converged rate solutions calibrate and validate equilibrium models (20 real trays ≈ 15 equilibrium stages in Example 12.2; propane overall tray efficiency 28% in the absorber example).
7. Use rate-based models especially for absorbers and nonideal mixtures; always begin simulation studies with standard specifications before exploiting flexible options.

## Connects To
- **Ch 10**: The equilibrium-stage MESH model and the Naphtali–Sandholm SC method that the rate-based formulation and solution directly extend (2C+1 vs 5C+5 equations per stage).
- **Ch 2**: K-value and enthalpy models (EOS / activity coefficients, UNIFAC) reused here — but K-values apply only at the interface, and γ_i feeds the thermodynamic-factor matrix.
- **Ch 3**: Maxwell–Stefan diffusion, binary mass-transfer coefficients, Chilton–Colburn analogy, and penetration theory — the transport fundamentals the rate expressions build on.
- **Ch 6**: Tray efficiency (Murphree, Lewis flow-pattern cases), HETP, flooding, pressure drop, and packing hydraulics — the design quantities the rate-based model now predicts rather than assumes.
- **Ch 7**: Tray and packing mass-transfer correlations (AIChE, Chan–Fair, Billet–Schultes) supplying the binary-pair coefficients and interfacial areas.
