# Chapter 8: Liquid-Liquid Extraction with Ternary Systems

## Core Idea
Liquid-liquid extraction separates a solute from a carrier using a solvent with selective affinity, and for ternary systems the equilibrium-stage count is found graphically on triangular diagrams via the Hunter-Nash method — but the whole design hinges on choosing a selective solvent and workable equipment.

## Frameworks Introduced
- **Ternary Diagrams (equilateral-triangle and right-triangle)**: Binodal (equilibrium) curve with extract side left of the plait point, raffinate side right; tie lines connect equilibrium phases; lever-arm rule locates mixing points. Right-triangle plots only two components (third by difference) but allows axis expansion for accuracy (Kinney method).
  - When to use: single-section countercurrent cascades for Type I systems; process simulators preferred for two-section/refluxed cascades.
- **Hunter-Nash Graphical Method**: Three constructions on a triangular diagram: (1) locate product points via mixing point M and material balances; (2) locate difference (operating) point P at the intersection of extended lines through passing-stream pairs (E1,F) and (S,RN); (3) step off stages alternating tie lines (equilibrium) with operating lines through P.
  - How: specification sets — Set 1 (S and raffinate composition) or Set 2/3 give N directly; Sets 4-6 (fixed N) need iteration.
- **Distribution Coefficient and Relative Selectivity**: (K_A)_D = x_A(extract)/x_A(raffinate) = gamma_A(raffinate)/gamma_A(extract); beta_AC = (K_A)_D/(K_C)_D. First estimate from infinite-dilution activity coefficients or the lowest tie line.
  - When to use: first-pass solvent screening — require beta >> 1, high K_A for capacity, high (K_S)_D / low (K_C)_D for easy solvent recovery.
- **Ternary System Types (I and II)**: Type I — solute and solvent miscible in all proportions, one immiscible pair, has a plait point; Type II — two immiscible pairs (e.g., heptane/aniline/MCH), no plait point, high selectivity but poor capacity. Type can change with temperature (e.g., hexane/MCH/aniline goes Type II at 25°C to Type I at 45°C).
  - When to use: Type I solvents preferred; Type II systems suit extract-reflux cascades for sharp binary splits.
- **Solvent Selection via Group Interactions (Robbins chart, Table 8.4)**: 12 solute/solvent chemical classes; a minus sign means the solvent lowers the solute's activity coefficient — desirable. Complemented by UNIFAC-based optimization (Naser-Fournier) and partition-coefficient/Godfrey-miscibility tables.
  - When to use: water-rich feed → organic solvent; organic-rich feed → aqueous solvent; always pick the solvent that lowers the solute activity coefficient.
- **Minimum/Maximum Solvent-to-Feed Ratio**: Minimum corresponds to a pinch (tie line coincident with operating line); found by extending every tie line to the extended line through S and RN and taking the farthest intersection (P_min) on the raffinate side — or, for extract-side-sloping tie lines, the intersection closest to S. Maximum S/F occurs when M reaches the binodal (single phase, no raffinate).
  - When to use: compute before staging; operate at ~1.5 S_min; respect S_min < S/F < S_max.
- **Extractor Selection and Equipment Classes**: Mixer-settlers (good staging, high floor space/holdup), spray/packed/sieve-tray static columns (few stages only, backmixing-limited), mechanically agitated columns (Scheibel, Oldshue-Rushton, RDC, ARD, Kuhni, Karr reciprocating-plate), Graesser raining-bucket, centrifugal extractors (Podbielniak, seconds of residence time).
  - When to use: few stages → mixer-settlers; >5 stages + limited floor space → RDC/ARD; bioseparations/emulsifying systems → Karr or centrifugal.
- **Mixer-Settler Design Theory**: Power number vs. impeller Reynolds number correlation (baffled, six-flat-blade turbine, N_Po ≈ 5.7 fully turbulent); Skelland minimum-impeller-speed correlation for uniform dispersion; Sauter-mean drop size from Weber number; interfacial area a = 6φ_D/d_vs; Murphree dispersed-phase efficiency E_MD = N_OD/(1+N_OD) with N_OD = K_OD aV/Q_D (CSTR model).
  - When to use: preliminary sizing by rules of thumb (2 min mixer residence, 5 gpm/ft² settler), final design by vendor scale-up.

## Key Concepts
- **Extract phase**: solvent-rich equilibrium phase (phase II); **raffinate phase**: carrier-rich phase (phase I).
- **Tie line**: connects compositions of two equilibrium phases at fixed T; its slope (upward toward S) indicates a good solvent.
- **Plait point**: composition where the two equilibrium phases merge into one (Type I only); extract and raffinate sides of the binodal divide there.
- **Solutropy**: tie-line slopes reverse across the diagram (e.g., isopropanol/water/benzene); may vanish in mole-fraction coordinates.
- **Difference (operating) point P**: difference of passing streams (F − E1 = ... = RN − S = P); usually lies outside the diagram; locus of operating lines for stepping stages.
- **Pinch line**: tie line coincident with an operating line — gives (S/F)_min and infinite stages.
- **Conjugate line / tie-line interpolation**: constructed from existing tie lines and the plait point to generate intermediate tie lines.
- **Extract reflux**: solvent removed from extract, solute-rich liquid split into product + reflux returned; enables sharp splits for Type II systems (raffinate reflux is of little value per Skelland).
- **Dispersed vs. continuous phase**: dispersed in droplets; prefer dispersing the higher-flow phase; Marangoni effects govern coalescence.
- **HETS**: height equivalent to a theoretical stage; scales with column diameter to the 0.2-0.4 power (axial mixing).
- **Sauter mean diameter d_vs**: surface-mean drop diameter preserving interfacial area per mass; a = 6φ_D/d_vs.

## Mental Models
- **Lever-arm bookkeeping**: mixing points M (inside the diagram, F + S = RN + E1) and difference points P (outside, stream differences) are the same geometry applied to sums and differences; all passing-stream lines pass through P.
- **The stage/solvent trade-off**: like absorption — more solvent, fewer stages; (S/F)_min is the infinite-stages anchor and must be found before any stage count.
- **Solvent selectivity comes from activity-coefficient asymmetry**: the solvent must lower gamma of the solute but not the carrier; capacity requires affinity (low gamma_A in extract), which nearly ideal A-C pairs make hard.
- **Equipment is chosen by physical property regime**: low interfacial tension/viscosity + big density difference → simple columns; otherwise mechanical agitation or centrifugal force.

## Anti-patterns
- **Choosing a solvent by capacity alone**: high K_A with poor selectivity (beta near 1) just co-extracts carrier; selectivity and environmental concerns come first, capacity and cost second.
- **Ignoring the maximum S/F**: pushing M to the binodal dissolves all feed in solvent — no raffinate forms, no separation.
- **Stepping stages from a wrong difference point**: if tie lines slope toward the extract side, P_min is the intersection closest to S, not farthest; for solutropic systems, extract-side intersections govern.
- **Overspecifying a single-section cascade**: you cannot specify the split of two components without reflux (two-section cascade); you can only specify recovery of one solute.
- **Dispersing the wrong phase**: dispersing the low-flow or high-viscosity phase kills throughput; and if solvent is dispersed, solute depletion raises interfacial tension and inhibits coalescence.
- **Trusting static columns for many stages**: backmixing limits spray/packed columns to 1-2 and few stages respectively; use mechanically agitated or staged contactors beyond that.

## Reference Tables
**Ideal solvent criteria (Table 8.4-adjacent list)**: high selectivity; high solute capacity; minimal carrier solubility; volatility offset enabling distillative recovery; stability; inertness; low viscosity; non-toxic/non-flammable; low cost; moderate interfacial tension; large density difference vs. carrier; no rag/scum formation; good wetting.

**Extractor type selection (Tables 8.2/8.3/8.5)**:

| Type | Max throughput m³/m²·h | Typical UD+UC m/h | 1/HETS m⁻¹ | Notes |
|---|---|---|---|---|
| Mixer-settler cascade | — | — | ~1 unit/stage | high viscosity/flow ratio OK; big footprint |
| Packed column | — | 12-30 | 1.5-2.5 | few stages; packing wetted by continuous phase |
| Sieve-tray column | — | 27-60 | 0.8-1.2 | high capacity; flooding/entrainment limits |
| RDC | 40 | 15-30 | 2.5-3.5 | large diameters (8 m); >5 stages, tight space |
| ARD | 25 | — | — | RDC shear with less backmixing |
| Kuhni | 40 | 8-12 | 5-8 | three shafts >3 m diameter |
| Scheibel | 25 | — | 5-9 | wire mesh for coalescence (remove at high σ) |
| Karr (RPC) | 40 | 30-40 | 3.5-7 | bioseparations, emulsifiers, particulates |
| Graesser RTL | 10 | 1-2 | 6-12 | gentle; small density difference |
| Centrifugal (POD) | — | — | — | 10 s residence; Δρ as low as 0.01 g/cm³ |

**Robbins chart sign convention**: "+" raises solute activity coefficient, "−" lowers it (choose "−"); example — acetone (class 3, alcohol/water group) extracted from water by trichloroethane (class 6, tert-amine-adjacent H-acceptor... actually class 6 = tertiary amines; chart points to classes 1 and 6 for acetone).

## Worked Example
**Example 8.1 — Hunter-Nash staging, acetone/water/ethyl acetate, 30°C.** Feed: 30 wt% acetone (A) in ethyl acetate (C); solvent: pure water (S). Type I system, but tie lines slope down toward the extract side (water has low capacity for acetone — the chart-guided solvent choice trades against capacity). Raffinate spec: 5 wt% acetone (water-free, point B′ on the binodal via line B-S).
- (S/F)_min: extend each tie line to the extended line FS; take the intersection closest to S (extract-side-sloping tie lines) → P_min; locate D′_min; intersect B′D′_min with FS → M_min; lever arm gives (S/F)_min = 0.60 (N = ∞, extract 64 wt% acetone solvent-free).
- (S/F)_max = 12 (M reaches the binodal).
- At S/F = 1.75: locate M by lever arm (FM/MS = 1.75); D′ on the binodal along B′M extended; difference point P = intersection of FD′ and B′S extensions (left of diagram); step off alternating tie lines and operating lines through P → 4 equilibrium stages, extract 62 wt% acetone.
- At S/F = 3.0 (= 5×min): 2 stages, extract 50 wt% acetone.
- Feed composition limit: a line from S tangent to the binodal cuts line AC at 64 wt% acetone — richer feeds cannot split into two phases with this solvent, no matter the solvent rate.

## Key Takeaways
1. Extraction is chosen over distillation when relative volatility is unfavorable (dilute acids, azeotropes, heat-sensitive materials) — but it always adds a solvent-recovery step.
2. Selectivity β = (K_A)_D/(K_C)_D is the first solvent screen; estimate it from infinite-dilution activity coefficients or the lowest tie line; use the Robbins group-interaction chart to find solvents that lower the solute's activity coefficient.
3. Type I (plait point, solvent fully miscible with solute) beats Type II for capacity; Type II plus extract reflux enables arbitrarily sharp solute/carrier splits.
4. Hunter-Nash: three constructions (products → difference point P → tie-line stepping); the minimum S/F is found at the pinch where tie line = operating line, before staging; operate around 1.5 S_min and below (S/F)_max where the binodal swallows the feed.
5. Equipment follows the property regime: static columns for easy systems and few stages; mechanically agitated (RDC, Scheibel, Karr) for high interfacial tension or low density difference; centrifugal for fast, emulsifying, small-Δρ duties.
6. Mixer-settler rules of thumb: 30 s to 5 min residence at ~4 hp/1,000 gal gives ≥90% stage efficiency (μ < 5 cP, sg difference > 0.1); settler sized at ~5 gpm/ft² of disengaging area, L/DT ≈ 4.
7. Column extractors behave as differential contactors — use HETS from pilot data scaled as D_T^0.2-0.4; final design belongs to vendors with pilot units.

## Connects To
- **Ch 4**: triangular (ternary) LLE diagrams, tie lines, and plait points defined; activity-coefficient thermodynamics behind (8-1)-(8-4).
- **Ch 2**: distribution coefficient K_D and relative selectivity β introduced (Eqs. 2-19, 2-21).
- **Ch 6/7 (absorption/stripping, distillation)**: single-section cascade mirrors absorption (stage/solvent-rate trade-off, pinch at infinite stages); two-section refluxed cascade mirrors binary distillation (reflux ratio, feed-stage specification sets).
- **Ch 5**: degrees-of-freedom analysis via elements (cascades, splitter, divider) for the extract-reflux configuration.
- **Ch 10**: process-simulator methods for two-section and refluxed extraction, where triangular constructions become impractical.
