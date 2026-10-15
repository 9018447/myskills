# Chapter 5: Multistage Cascades and Hybrid Systems

## Core Idea
A single equilibrium stage rarely achieves a useful separation; arranging stages into cascades (cocurrent, crosscurrent, countercurrent; single- or two-section) multiplies separation power, and degrees-of-freedom analysis (Kwauk's method) tells you how many specifications any cascade configuration needs before it can be solved.

## Frameworks Introduced
- **Cascade configurations (§5.1)**: single-section vs. two-section; cocurrent vs. crosscurrent vs. countercurrent arrays of equilibrium stages.
  - Single-section cascade: recovers ONE key component from a feed entering one end and leaving the other (absorption, stripping, single-solvent extraction). Two-section cascade: needed when purity/recovery of TWO key components is required (distillation; extraction with two selective solvents).
  - Crosscurrent suits batch processing (esp. batch liquid–liquid extraction); countercurrent is preferred for continuous service.
- **Extraction-factor cascade formulas (§5.2)**: closed-form fraction unextracted for N equilibrium stages with immiscible carrier/solvent and constant distribution ratio K'_D, driven by the extraction factor 𝓔 = K'_D·S/F_A.
  - Cocurrent: X_R/X_F = 1/(1+𝓔) for ANY N — extra stages add only residence time, not separation.
  - Crosscurrent (S split equally): X_R/X_F = 1/(1+𝓔/N)^N → 1/e^𝓔 as N→∞ (never zero).
  - Countercurrent: X_R/X_F = 1/Σ𝓔ⁿ = (𝓔−1)/(𝓔^(N+1)−1); limit is 0 for 𝓔 > 1, (1−𝓔) for 𝓔 ≤ 1. Complete extraction possible only if 𝓔 > 1 with infinite stages.
- **Two-section distillation cascade (§5.3)**: feed stage splits column into a rectifying section (above; enriches vapor in light key via reflux) and a stripping section (below; strips light key from downflowing liquid via reboiler boilup). Partial condenser and partial reboiler each count as (diabatic) equilibrium stages; column trays are adiabatic stages. Purity rises steeply then asymptotes toward 100% with stage count — in the limit, pure light and heavy products.
- **Membrane cascades (§5.4)**: membrane modules are rate-based, NOT equilibrium stages; parallel modules handle area/pressure-drop, stages-in-series with permeate recycle boost purity. Single-section membrane cascades raise purity but barely recovery; both require a two-section cascade.
- **Hybrid systems (§5.5)**: two different separation operations in series to cut energy/raw-material cost or make otherwise impossible splits (e.g., adsorption + gas permeation for CH₄/N₂; distillation + pervaporation for ethanol–water; RO + distillation).
- **Degrees-of-freedom analysis for cascades (§5.6, Kwauk method)**: N_D = N_V − N_E (5-16); build units from elements via (5-17)–(5-20), subtracting N_R(C+3) redundant variables and N_R redundant mole-fraction constraints per interconnecting stream, adding N_A variables for unspecified repetitions.
  - Stream variables: C + 3 per stream (C mole fractions + flow + T + P; only C−1 mole fractions independent — carry the constraint equation instead).
  - Equilibrium stage with heat transfer: N_V = 4C+13, N_E = 2C+7, N_D = 2C+6.
  - N-stage single-section countercurrent unit: N_D = 2N + 2C + 5 (coefficient of C = number of feed streams entering; coefficient of N is always 2 = Q and P per stage).
- **Design vs. simulation case (Table 5.4)**: Case I — specify component recoveries, solve for stage count (design). Case II — specify stage count, compute separations (simulation; computationally simpler, the simulator default).

## Key Concepts
- Cascade; section (single vs. two-section)
- Key component vs. key components (one vs. two keys → one vs. two sections)
- Extraction factor 𝓔 = K'_D S/F_A; distribution ratio K'_D (mass-ratio basis)
- Raffinate / extract; reflux / boilup; rectifying / stripping section
- Adiabatic vs. diabatic equilibrium stages (condenser/reboiler are diabatic stages)
- Membrane module, permeate, retentate; permeate recycle
- Degrees of freedom N_D; design variables; redundant interconnecting streams N_R; additional variables N_A
- Design case vs. simulation case

## Mental Models
- **Countercurrent wins**: at equal total solvent and stage count, countercurrent > crosscurrent > cocurrent; only countercurrent with 𝓔 > 1 can drive solute to zero.
- **Sections = keys**: each section of a countercurrent cascade "owns" one key; a sharp two-key split demands two sections (reflux/boilup in distillation is the recycle that makes the second section work).
- **Asymptotic purity**: adding stages gives diminishing returns — purity curves flatten (extraction, distillation, membrane cascades all show it); the stage/reflux tradeoff is an optimization (Ch. 7).
- **Count degrees of freedom before specifying**: every element and unit has a fixed N_D; a sidestream adds 2, a second feed adds C+3, a partial condenser (vapor distillate only) removes 3 vs. a total condenser.

## Anti-patterns
- **Specifying both Q_C and Q_R (condenser and reboiler duties)**: they are tightly coupled; fix Q_C via distillate rate and reflux ratio, back-calculate Q_R from the overall energy balance.
- **Specifying condenser/reboiler duty as a design variable at all**: poorly specified Q_C can yield an unrealizable temperature; duties are outputs, not inputs.
- **Specifying recoveries of more than two keys**: the specified composition may not exist at physical equilibrium → non-convergence.
- **Choosing closely related variable pairs (D and Q_C; D and L_R/D)**: independent-variable violations.
- **Adding cocurrent stages for separation**: no merit beyond extra residence time — X never drops below 1/(1+𝓔).
- **Expecting a single-section cascade to split two keys**: structurally impossible; single-section membrane cascades raise purity but not recovery.
- **Counting membrane modules as equilibrium stages**: retentate and permeate are never in equilibrium; performance is mass-transfer-rate and area driven.

## Reference Tables
Fraction unextracted (N stages, constant K'_D, immiscible):

| Arrangement | X_R/X_F | Limit as N→∞ |
|---|---|---|
| Cocurrent | 1/(1+𝓔), any N | 1/(1+𝓔) |
| Crosscurrent | 1/(1+𝓔/N)^N | e^(−𝓔) |
| Countercurrent | (𝓔−1)/(𝓔^(N+1)−1) | 0 if 𝓔>1; (1−𝓔) if 𝓔≤1 |

Selected N_D values (Table 5.3): total condenser/reboiler C+4; partial condenser/reboiler C+4; adiabatic stage 2C+5; stage with heat transfer 2C+6; feed stage 3C+8; sidestream stage 2C+7; N-stage countercurrent unit 2N+2C+5; mixer 2C+6; divider C+5.

Unit N_D (Table 5.4): absorption/stripping/LLE (2 inlets) 2N+2C+5; LLE two solvents 2N+3C+8; distillation (total cond.) 2N+C+9; distillation (partial cond., vapor distillate) 2N+C+6; reboiled absorption 2N+2C+6; reboiled stripping 2N+C+3; extractive distillation 2N+2C+12.

Rules of thumb: coefficient of C in N_D = number of feeds entering the unit; coefficient of N = 2 always (Q and P per stage); sidestream = +2 N_D; second feed = +(C+3); total→partial condenser with vapor-only distillate = −3 N_D.

## Worked Example
**Example 5.1 — p-dioxane extraction cascade comparison.** Feed 4,536 kg/h of 25 wt% p-dioxane in water; benzene solvent 6,804 kg/h at 25 °C; water and benzene immiscible, K'_D ≈ 1.2 (constant). Carrier F_A = 4,536(0.75) = 3,402 kg/h; X_F = 0.25/0.75 = 1/3. 𝓔 = K'_D·S/F_A = 1.2(6,804)/3,402 = 2.4.
- 1 stage (any arrangement): X_R/X_F = 1/(1+2.4) = 0.294 → 70.6% extraction.
- Cocurrent, N stages: still 70.6% — no improvement.
- Crosscurrent, 2 equal solvent splits: 1/(1+2.4/2)² = 0.207 → 79.3%; maximum as N→∞ = 1−e^(−2.4) → 90.9%.
- Countercurrent, 2 stages: 1/(1+2.4+2.4²) = 0.109 → 89.1%; 5 stages reach 99.2% and 100% is approached as N→∞ (𝓔 > 1).
Moral: countercurrent with 𝓔 > 1 beats everything; distillation cannot separate this pair (b.p. 100 °C vs. 101.1 °C), motivating extraction.

## Key Takeaways
1. A cascade is a sequence of stages achieving what one stage cannot; arrays are cocurrent, crosscurrent, or countercurrent, and cascades are single- or two-section.
2. Countercurrent is the most efficient arrangement for a given solvent rate and stage count; crosscurrent is mainly for batch work; cocurrent adds nothing but residence time.
3. Complete extraction in a countercurrent cascade requires 𝓔 > 1 (with infinite stages); pick solvent and solvent rate accordingly.
4. A single-section cascade recovers one key; a sharp split of two keys requires a two-section cascade (rectifying + stripping in distillation, enabled by reflux and boilup recycle).
5. Membrane modules are rate-based, not equilibrium stages; single-section membrane cascades buy purity, not recovery — two-section cascades with recycle are needed for both.
6. Hybrid systems (two different operations in series, sometimes with recycle) achieve separations neither operation can make alone and can cut energy cost.
7. Degrees of freedom N_D = N_V − N_E, assembled element-by-element with corrections for redundant interconnecting streams; a valid, independent specification set must satisfy it before any simulator run (simulators enforce this on every unit).

## Connects To
- **Ch 4**: source of the single-equilibrium-stage model, extraction factor (4-35/4-36), flash calculations, and the single-stage degrees-of-freedom analysis extended here.
- **Ch 6 & 10**: single-section cascade applied to absorption and stripping (graphical/short-cut and simulation methods).
- **Ch 7**: binary distillation stage/reflux design — the two-section cascade in depth, plus the stage-count vs. reflux optimization.
- **Ch 8**: single-section liquid–liquid extraction cascades.
- **Ch 9 & 10**: two-section distillation cascades for multicomponent systems; RadFrac simulation.
- **Ch 11**: distillation combined with extractive/azeotropic distillation and L–L extraction hybrids.
- **Ch 14**: two-section membrane cascades achieving high purity and recovery.
