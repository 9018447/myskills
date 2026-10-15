# Chapter 11: Enhanced Distillation and Supercritical Extraction

## Core Idea
When ordinary distillation fails — because of an azeotrope, close boiling points, or thermal sensitivity — you must change the thermodynamic landscape (add a solvent, salt, entrainer, pressure swing, or reaction) or leave the vapor–liquid regime entirely (supercritical-fluid extraction). Triangular residue-curve/distillation-curve maps are the master tool for deciding which enhanced scheme is feasible before any simulation.

## Frameworks Introduced
- **Triangular-diagram analysis (§11.1)**: Ternary composition on equilateral/right triangles; residue-curve maps (batch, `dx_i/dξ = x_i − y_i`, warped time ξ = ln[W₀/W]) and distillation-curve maps (continuous, total reflux, x_{i,j+1} = y_{i,j}).
  - When to use: First step for ANY azeotrope-forming or close-boiling ternary. Establishes distillation regions, boundaries, and singular points before column design.
- **Singular-point classification (Doherty/Perkins)**: Stable node (highest boiler in region, both eigenvalues negative — curves terminate), unstable node (lowest boiler, both positive — curves originate), saddle (intermediate boiler, one +/- — curves approach then deflect away). Topological constraints: N₁+S₁=3, N₂+S₂=B≤3, N₃+S₃=1 or 0, and 2N₃−2S₃+2N₂−B+N₁=2. ≈125 distillation region diagrams (DRD) exist; Doherty–Caldarola sketch 87 with min-boiling azeotropes.
  - How: Foucher–Doherty–Malone 9-step procedure sketches an approximate map from only boiling points + azeotrope data (Horsley, Gmehling compilations); number of distillation boundaries = number of binary saddles (S₂); each binary saddle connects min-boiling → lower-boiling unstable node, max-boiling → higher-boiling stable node.
- **Bow-tie regions (feasible product-composition regions)**: At total reflux, D and B lie on the same distillation curve through the feed; the material-balance line (chord through F) sweeps out shaded feasible regions on the convex side of the curve.
  - When to use: Test candidate splits. Caveat: a highly CURVED distillation boundary CAN be crossed by a material-balance line (convex→concave side only, feed between D and B).
- **Extractive distillation (§11.2)**: Low-volatility solvent (no azeotropes with feed) fed a few trays below the top (min-boiling azeotrope case) or with the feed (max-boiling case); raises relative volatility via differential solvent affinity. Solvent:feed molar ratio ~1. Named by Dunn et al. (toluene/paraffins with phenol).
  - When to use: Azeotropes or close boilers where a high-boiling, non-azeotrope-forming solvent with different affinities exists (acetone–methanol with water, ethanol–water with glycerine/EG, HNO₃–water with H₂SO₄).
- **Salt distillation (§11.3)**: Dissolved inorganic salt (CaCl₂ brine, K-acetate) in the solvent/reflux lowers solvent vapor pressure and can eliminate the azeotrope entirely (salting-out). Hydrotropes (p-TSA) extend it to organics.
  - When to use: Aqueous systems where too much liquid solvent contaminates the distillate; salt never enters the vapor (entrainment aside).
- **Pressure-swing distillation (§11.4)**: Two columns at different pressures exploiting azeotrope composition shift with P. Criterion: azeotrope disappears at some P, or shifts ≥5 mol% over moderate P range (Knapp & Doherty list 36 candidates). Min-boiling azeotrope → both products as bottoms; max-boiling → both as distillates. Recycle ratio is the key cost driver (compression).
- **Homogeneous azeotropic distillation (§11.5)**: Entrainer E forms azeotropes but A, B, E must lie in the SAME distillation region; A or B (not both) must be a saddle. Doherty–Caldarola Groups 1–5 (by which of L/I/H is E and min/max azeotrope formed). Rarely feasible — most intermediate-boiling entrainers form azeotropes, and max-boiling azeotropes are uncommon.
- **Heterogeneous azeotropic distillation (§11.6)**: Entrainer forms a heterogeneous (two-liquid-phase) azeotrope; condensed overhead splits in a decanter; entrainer-rich phase refluxed, other phase stripped/recovered. The two feed components may sit in DIFFERENT distillation regions — the tie line through the ternary azeotrope crosses boundaries, defeating the homogeneous restriction.
  - When to use: Ethanol–water dehydration (benzene, diethyl ether, n-pentane entrainers), acetic acid–water (ethyl acetate, n-propyl acetate). Sequences: 3-column (preconcentrator + azeotropic tower + entrainer recovery), 4-column, or 2-column (Ryan & Doherty: 2-col lower capital, higher operating cost for dilute feeds).
- **Multiplicity of solutions (§11.6.1)**: Output / input / internal-state multiplicity (Gani & Jørgensen). Azeotropic columns can have several steady states (e.g., Kovach & Seider: 5 solutions, ethanol purity 70→~100%); simulators return only one.
- **Reactive distillation (§11.7)**: Reaction + separation in one column. Also reactive entrainers for close boilers (m-/p-xylene, Δbp 0.8°C, α=1.029, with tert-butylbenzene/AlCl₃). Requires: liquid-phase (or solid-catalyst surface) reaction, same T/P window for reaction and distillation, equilibrium-limited reaction whose product removal drives conversion. Stage model: SC-method balance (11-17) with reaction-rate source term (V_LH)Σζr; equilibrium limit simulated via very large liquid holdup. Ideal configurations (Belck): A↔R with R more volatile → rectifying section only; A↔R with A more volatile → stripping only; 2A↔R+S or A+B↔R+S with R most volatile, S least → middle-fed ordinary column.
- **Supercritical-fluid extraction (§11.8)**: Solvent above T_c, P_c (CO₂: 304.2 K, 73.83 bar). Solvent power explodes near the critical point (pICB in ethylene: 0.015 → 40 g/L from 2→8 MPa, 2700× ideal-gas prediction) because density rises sharply — most useful at T_r ≈ 1.01–1.12. Bonus: diffusivity 1–2 orders above liquid solvents, viscosity ~10× lower. CO₂ preferred (moderate P_c, high critical density, nonflammable, nontoxic, T_c near ambient; solute recovery by mere pressure reduction). Thermodynamics: SRK/PR with van der Waals mixing + k_ij/l_ij binary interaction parameters for nonpolar systems; Wong–Sandler mixing rule (PR + NRTL) bridging EOS and activity-coefficient methods for polar mixtures; GC-EOS (Skjold-Jørgensen) when binary data are missing.

## Key Concepts
- **Azeotrope** (minimum-boiling, most common — unstable node; maximum-boiling — stable node; homogeneous vs heterogeneous/two-liquid-phase)
- **Distillation boundary**: curve connecting singular points that residue curves cannot cross; limits feasible products regardless of D/B ratio
- **Residue curve / distillation curve**: batch-residue trajectory vs continuous total-reflux stage sequence; distillation curves ≈ residue curves with Δξ = −1 finite difference
- **Entrainer / solvent / reactive entrainer / hydrotrope**
- **Infinite-dilution activity coefficient**: the screening quantity for solvent selection (UNIFAC); all successful extractive solvents are highly hydrogen-bonded liquids (Berg)
- **Relative volatility enhancement**: e.g., water lifts α_{acetone/methanol} ≥ 2.0 across the whole range
- **Binodal curve / tie line**: liquid–liquid solubility envelope (isobaric, not isothermal) overlaid on the residue-curve map; decanter operates on a tie line
- **Salting-out / salting-in**: salt changes solvent volatility and component activities (NaNO₃ salts out methanol; HgCl₂ salts in)
- **Retrograde / critical-region behavior**: solubility surge near T_c, P_c driven by solvent density, not ideality
- **Multiplicity** (output/input/internal-state) and tear-stream convergence in recycle flowsheets

## Mental Models
- **The map before the column**: sketch the residue-curve map (even by hand, from boiling points + azeotrope data) and place feed, D, B on it. If a material-balance line cannot connect them within a region, no amount of trays or reflux will make the split work.
- **Residue curves as batch-distillation trajectories**: arrows run low boiler → high boiler; unstable node = where all curves start (lowest boiler in region), stable node = where they end, saddles deflect them. Products of a column must be nodes/boundary-compatible species of the region containing the feed.
- **Change the game, don't fight it**: each enhanced method changes VLE differently — solvent (activity coefficients), salt (vapor-pressure suppression + salting out), pressure (azeotrope shift), reaction (consumes one component), supercritical fluid (density-tunable solvent power).
- **Entrainers pay rent in the decanter**: heterogeneous azeotropy splits phases so each liquid phase lives in a different distillation region — the region restriction is broken by liquid–liquid equilibrium, not distillation.

## Anti-patterns
- **Picking an entrainer without a residue-curve-map check**: the A–B–E ternary must have A and B in the same distillation region (homogeneous case); violations are discovered only after failed simulations. Benzene/cyclohexane with acetone violates distillation-only rules and needs a hybrid (extraction) sequence.
- **Assuming boundaries are absolute**: highly curved boundaries CAN be crossed by material-balance lines (one direction only: convex → concave, feed between D and B). Treating the boundary as a hard wall (or ignoring curvature) misjudges feasibility both ways.
- **Choosing a low-boiling solvent like water for extractive distillation without checking solvent stripping**: in Example 11.3, 2.25% of the water stripped into the distillate capped acetone purity at 95.6 mol%; aniline (184°C) or ethylene glycol (198°C) strips far less.
- **Trusting a single converged simulation of an azeotropic column**: multiple steady states (some wildly different in purity) exist; a converged "solution" may be the bad one. Use continuation/bifurcation methods and varied initial guesses.
- **Assuming SFE is a general distillation substitute**: high solvent-compression cost means SFE only wins for small amounts of large, nonvolatile, expensive solutes (bioextraction); SC-CO₂ failed to break the ethanol–water azeotrope because it dissolves water too.
- **Ignoring reaction direction along the column**: in reactive distillation, the reverse reaction can dominate on some stages (Example 11.8: reverse dominant above the upper feed and on stages 11–13), killing conversion even with 60 stages.

## Reference Tables

| Obstacle | First-choice method | Alternatives | Key check |
|---|---|---|---|
| Minimum-boiling azeotrope | Extractive distillation (high-bp solvent, no azeotropes) | Salt distillation (aqueous); pressure-swing if azeotrope shifts ≥5 mol% | Solvent infinite-dilution γ's give α ≥ ~2; no azeotrope with solvent |
| Maximum-boiling azeotrope | Extractive distillation (solvent enters WITH feed) | Pressure-swing (products as distillates) | Same solvent criteria |
| Close-boiling, zeotropic | Extractive distillation | Reactive entrainer (selective reversible reaction with one key) | α_{1.029} xylene case still hard — verify stage savings |
| Azeotrope, pressure-sensitive | Pressure-swing distillation (2 columns, 2 pressures) | — | Azeotrope vanishes at some P or shifts ≥5 mol%; recycle ratio economics |
| Azeotrope, homogeneous entrainer available | Homogeneous azeotropic distillation (Groups 1–5) | Hybrid with extraction | A, B in same distillation region; one of A/B is a saddle |
| Azeotrope + entrainer forms two liquid phases | Heterogeneous azeotropic distillation + decanter | — | Ternary heterogeneous azeotrope = unstable node; tie line crosses boundaries (feature, not bug) |
| Equilibrium-limited liquid-phase reaction | Reactive distillation | Reactor + ordinary distillation | Same T/P window; product separable by distillation; NOT for gas-phase, supercritical, high-T/P, solids |
| Small quantity of high-value, low-volatility solute (natural products) | SFE with supercritical CO₂ | Liquid extraction; add cosolvent (e.g., glycerol) for selectivity | T_r ≈ 1.01–1.12; CO₂ recovery by pressure reduction, high-P distillation, or water absorption |

**CO₂ recovery schemes (Fig 11.44)**: (a) pressure reduction + flash + recompress — simple but costly if deep expansion needed; (b) high-pressure distillation below extractor P (de Filippi & Vivian) — more versatile; (c) high-pressure absorption into water + reverse osmosis (Katz et al., coffee decaffeination).

## Worked Example
**Example 11.5 — Pressure-swing distillation of ethanol–benzene.**
Given: 90 mol/s bubble-point liquid, 2/3 ethanol + 1/3 benzene at 101.3 kPa; target 99 mol% each. Minimum-boiling azeotrope: 44.8 mol% ethanol at 101 kPa, 68°C; shifts to 36 mol% ethanol at 27 kPa, 35°C → feasible.
Method: Two columns. Column 1 at top-tray 30 kPa (vacuum): feed is ethanol-richer than the azeotrope at 30 kPa → bottoms 99% ethanol, distillate set at 37 mol% ethanol (just above azeotrope). Column 2 at 106 kPa: feed leaner than azeotrope there → bottoms 99% benzene, distillate 44 mol% ethanol (just below azeotrope) recycled to Column 1 (152.9 mol/s recycle vs 90 mol/s fresh feed — recycle dominance is the economics lesson).
Result: Column 1: 7 theoretical trays (recycle to tray 3, feed to tray 5), R = 0.5, 3.2 m diameter, 47% efficiency → 15 trays, condenser/reboiler 9.88/8.85 MW. Column 2: refluxed stripper, 3 theoretical stages, R ≈ 0.09 (25.5 mol/s reflux), 2.44 m diameter, 6 actual trays. Note: the azeotrope forces all operating lines below the 45° line in Column 1.

## Key Takeaways
1. Ordinary distillation is only one point on a spectrum; when blocked by azeotropes or α ≈ 1, first draw the ternary residue-curve map — feasibility, not tray count, is the binding constraint.
2. Singular-point topology (stable/unstable nodes, saddles) plus simple counting rules (11-9 to 11-12) lets you sketch ≈113–125 possible maps from handbook data alone; distillation boundaries number exactly S₂.
3. Extractive distillation is the workhorse: highly hydrogen-bonded, higher-boiling, non-azeotrope-forming solvent, fed below the top, solvent/feed ~1 mol/mol; screen solvents by infinite-dilution activity coefficients (UNIFAC).
4. Pressure-swing is attractive only when the azeotrope moves ≥5 mol% (or vanishes) over a moderate pressure range; the recycle stream, not the column, dominates cost.
5. Heterogeneous azeotropic distillation beats homogeneous because the decanter's phase split lets the two feed components live in different distillation regions — but beware two liquid phases forming on trays (kills efficiency) and multiplicity of steady states.
6. Reactive distillation pays only when reaction and distillation share a T/P window, the reaction is equilibrium-limited, and products favor different phases; add reaction-rate source terms to the stage balances and watch for reverse reaction on individual stages.
7. SFE is niche: near-critical density gives order-of-magnitude solubility gains (best at T_r 1.01–1.12), CO₂ is the default solvent, but compression economics confine it to high-value bioextractions; use PR/SRK with Wong–Sandler mixing or GC-EOS for polar systems.

## Connects To
- **Ch 4**: Gibbs phase rule (why binary azeotropes fix compositions at given T,P but ternaries gain a degree of freedom), triangular diagrams, heterogeneous azeotropes (§4.2.2).
- **Ch 2**: Activity-coefficient models (Wilson, NRTL, UNIQUAC, UNIFAC), cubic EOS (SRK, PR) and mixing rules — the thermodynamic engine for every VLE/LLE prediction in this chapter.
- **Ch 7 / Ch 9**: McCabe–Thiele (Example 11.3 solvent-recovery column; 45°-line comparison), Fenske/total-reflux concept underlying distillation-curve maps, direct/indirect sequences for ternaries.
- **Ch 8**: Liquid–liquid extraction (ternary diagrams, tie lines) — reused directly for bow-tie regions and for the hybrid benzene/cyclohexane sequence; extraction baseline SFE is compared against.
- **Ch 10**: SC (sum-rates) convergence method extended with reaction-rate source terms (11-17) for reactive distillation; rigorous simulation of azeotropic and extractive columns; convergence/homotopy-continuation methods for multiplicity.
- **Ch 13**: Simple batch distillation (13-1) — the physical basis of the residue-curve equation (11-1).
- **Ch 12**: Equilibrium-stage assumption itself; rate-based models become the remedy when tray efficiencies (and multicomponent coupling effects like reverse diffusion) undermine azeotropic-column simulations.
