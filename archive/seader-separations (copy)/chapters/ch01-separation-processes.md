# Chapter 1: Separation Processes

## Core Idea
Every industrial chemical process is dominated by separation operations, and every separation is built from one of four basic techniques (phase creation, phase addition, barrier, external field) that exploit differences in molecular, thermodynamic, and transport properties — with rates set by mass transfer and extent limited by thermodynamic equilibrium.

## Frameworks Introduced
- **Four Basic Separation Techniques (Fig. 1.6)**: the author's canonical classification of how species are induced to partition among product phases.
  - When to use: classifying any separator before selecting or designing it.
  - How: (a) **phase creation** — second phase generated from the feed by an ESA (partial vaporization/condensation, distillation); (b) **phase addition** — second phase introduced as an MSA (absorption, stripping, extraction, adsorption); (c) **barrier** — semipermeable membrane passes some species, retards others (dialysis, reverse osmosis, gas permeation, pervaporation); (d) **external force field or gradient** — electric, centrifugal, or thermal field preferentially attracts/migrates species (centrifugation, electrodialysis, thermal diffusion, electrolysis).
- **ESA vs. MSA**: the author's agent classification.
  - **ESA (energy-separating agent)**: heat transfer or shaft work (compression, pressure reduction via valve/turbine) that creates the second phase. No new substance enters the process.
  - **MSA (mass-separating agent)**: an added phase (liquid absorbent, stripping vapor, solvent, solid adsorbent) that selectively dissolves/adsorbs feed components.
  - When to use MSA: when volatility differences are too small or distillation is impractical (temperature-sensitive feeds). Accept four penalties: (1) an extra separator to recover/recycle the MSA, (2) MSA makeup, (3) possible product contamination, (4) more complex design.
- **Purity + Recovery specification pair**: every separation is specified by product purity (mol% for gases, wt% for liquids, ppm/ppb for trace impurities) and component recovery (fraction of feed component landing in the product).
  - How: write component material balances; recovery = component in product / component in feed; purity = component in product / total product flow.
- **Light key / heavy key split**: each multistage column in a sequence separates two key components — the most volatile component that goes (mostly) down (light key) and the least volatile that goes (mostly) up (heavy key); components lighter than the light key go up, heavier than the heavy key go down.
- **Sequencing heuristics (§1.8.2)**: six plausible-but-not-infallible rules for ordering distillation columns; use for initial feasible sequence selection before economic evaluation.
- **Selection criteria (§1.7)**: choose among feasible techniques by (1) technological maturity, (2) cost, (3) ease of scale-up, (4) ease of staging, (5) need for parallel units — maturity correlates with commercial use (Keller survey, Fig. 1.8).

## Key Concepts
- **Separation operation**: an industrial unit that partitions a feed mixture into products differing in composition (and possibly phase) — not spontaneous; requires energy input.
- **Single equilibrium stage**: partial condensation/vaporization or flash where interphase mass transfer is rapid enough that product phases closely approach equilibrium; adequate only when volatility differences are wide (e.g., H2/benzene).
- **Distillation**: phase-creation operation with countercurrent vapor–liquid contact on trays, random packing, or structured packing; needs reflux (top condenser) and boilup (reboiler); the most widely used industrial separation.
- **Absorption vs. adsorption**: absorption distributes solute throughout a liquid absorbent bulk; adsorption confines solute to exterior/interior surfaces of a porous solid adsorbent (regenerable after saturating with adsorbate).
- **Stripping**: inverse of absorption — liquid feed at top contacts gas MSA entering at bottom, at elevated temperature and near-ambient pressure.
- **Liquid–liquid extraction**: solvent MSA selectively dissolves components, yielding extract (Lᴵ) and raffinate (Lᴵᴵ); use when distillation is impractical (temperature-sensitive feed, close-boiling).
- **Retentate / permeate**: membrane-separation products — retentate does not pass the membrane, permeate does; microporous membranes separate by diffusion-rate differences, nonporous by solubility + diffusion differences.
- **Pervaporation**: liquid feed species diffuse through a nonporous membrane and evaporate before exiting as permeate; low pressure + heat of vaporization supplied; used to break azeotropes.
- **Key components**: the two species that define a column's separation split (see light/heavy key above); a "multicomponent product" lumps all components less volatile than a cutoff (e.g., C₅⁺).
- **Block-flow vs. process-flow diagram**: block-flow shows only reaction + separation steps with streams; process-flow adds auxiliary operations (heat exchangers, pumps, compressors, phase splitters) with equipment icons.

## Mental Models
- Think of a separator as a black box whose feed is partitioned by an agent — ask first "what creates or adds the second phase?" and the operation names itself.
- Use "rate vs. equilibrium" framing: mass-transfer rates set how fast separation happens; thermodynamic equilibrium caps how far it can go (Chs. 2–3).
- Think of separation cost as an inverse-concentration curve (Keller, Fig. 1.9): the more dilute the product in the feed, the higher the price — dilute recoveries (proteins) are intrinsically expensive.
- Think of recycle as the standard companion to low per-pass conversion (ethylene hydration: 5% per-pass conversion + recycle → near-complete overall conversion).

## Anti-patterns
- **Reaching for an MSA when an ESA suffices**: MSA operations drag in a recovery separator, makeup, contamination risk, and harder design; prefer phase creation (distillation/flash) when volatility differences permit.
- **Single equilibrium stage for close-boiling feeds**: partial condensation/flash cannot split benzene–toluene-like mixtures adequately; multiple-stage distillation is required.
- **Trusting heuristics blindly**: the six sequencing heuristics sometimes conflict — Heuristic 1 (remove unstable/corrosive/very-volatile components early) overrides the others; heuristics give feasible sequences, not economic optima.
- **Ignoring scale-up limits when planning capacity**: all equipment has a maximum size; membranes almost always need parallel units and re-pressurization between stages, so staging/capacity analysis differs fundamentally from distillation.
- **Specifying purity without recovery (or vice versa)**: a 97.86 mol% propane product means nothing without knowing the 96.14% propane recovery behind it — design needs both.

## Reference Tables

**Table 1.1 — Phase creation (ESA-based)**

| Operation | Feed phase | Created phase | Separating agent |
|---|---|---|---|
| Partial condensation or vaporization | Vapor and/or liquid | Liquid or vapor | Heat transfer (ESA) |
| Flash vaporization | Liquid | Vapor | Pressure reduction |
| Distillation | Vapor and/or liquid | Vapor and liquid | Heat transfer (ESA), sometimes shaft work (ESA) |

**Table 1.2 — Phase addition (MSA-based)**

| Operation | Feed phase | Added phase | Separating agent |
|---|---|---|---|
| Absorption | Vapor | Liquid | Liquid absorbent (MSA) |
| Stripping | Liquid | Vapor | Stripping vapor (MSA) |
| Liquid–liquid extraction | Liquid | Liquid | Liquid solvent (MSA) |
| Adsorption | Vapor or liquid | Solid | Solid adsorbent (MSA) |

**Table 1.3 — Barrier (membrane) operations**

| Operation | Feed phase | Barrier | Separating agent |
|---|---|---|---|
| Dialysis | Liquid | Microporous membrane | Pressure (ESA) |
| Reverse osmosis | Liquid | Microporous membrane | Pressure (ESA) |
| Gas permeation | Vapor | Nonporous membrane | Pressure (ESA) |
| Pervaporation | Liquid | Nonporous membrane | Pressure + heat transfer (ESA) |

**Table 1.4 — Ease of scale-up (decreasing ease)**

| Operation | Ease of staging | Need for parallel units |
|---|---|---|
| Distillation | Easy | No need |
| Absorption | Easy | No need |
| Liquid–liquid extraction | Easy | Sometimes |
| Membranes | Re-pressurization required between stages | Almost always |
| Adsorption | Easy | Only for regeneration cycle |

**Table 1.7 — Sequence combinatorics** (single-feed columns, one distillate + one bottoms each): 2 products → 1 column → 1 sequence; 3 → 2 → 2; 4 → 3 → 5; 5 → 4 → 14; 6 → 5 → 42.

**Sequencing heuristics (§1.8.2)**: (1) remove unstable/corrosive/reactive and very-volatile components early; (2) take products one by one as overhead distillates in decreasing volatility; (3) remove most-plentiful components early (smaller later diameters); (4) make the hardest separation (e.g., isomers) last, in absence of other components; (5) defer highest-purity products to later; (6) favor near-equimolar distillate/bottoms splits in each column (lower utility cost when energy is expensive).

## Worked Example

**Example 1.1 — Material balances around a gas-permeation membrane (air separation).** Given: F = 100 kmol/h air, 21 mol% O₂ / 79 mol% N₂; membrane more permeable to O₂; products are retentate R and permeate P.
- Case 1 (two recoveries: 50% O₂ to permeate, 87.5% N₂ to retentate): component balances give P = 20.4 kmol/h at 51.5% O₂; R = 79.6 kmol/h at 86.8% N₂.
- Case 2 (50% O₂ recovery + 50 mol% O₂ purity in permeate): purity fixes total permeate n_P = 10.5/0.5 = 21 kmol/h → N₂ balance gives R = 79 kmol/h at 13.3% O₂.
- Case 3 (two purities: 85% N₂ in retentate, 50% O₂ in permeate): solve two simultaneous component balances, 0.85n_R + 0.50n_P = 79 and 0.15n_R + 0.50n_P = 21 → n_R = 82.9, n_P = 17.1 kmol/h.
Method pattern: two independent specifications (recovery, purity, or both for the two components) always close the balance; overall component balance is n_{i,1} = n_{i,2} + n_{i,4} + n_{i,6} + n_{i,7} for the multi-column hydrocarbon recovery process (Fig. 1.10 / Table 1.5), where C1 splits nC₄(light key)/iC₅(heavy key), C2 splits C₃/iC₄, C3 splits iC₄/nC₄.

**Example 1.2 — Heuristic sequence selection.** Feed (mol%): C₃ 5, iC₄ 15, nC₄ 25, iC₅ 20, nC₅ 35; hardest split is the isomer pair iC₄/nC₄. Heuristic 3+4 combined → remove the C₅ multicomponent product (55%) first, then split iC₄/nC₄ in Column 3 with C₃ as Column 2 distillate; Heuristic 6 independently favors a 45/55 first split. Three candidate sequences result — heuristics narrow 5 options to 3.

## Key Takeaways
1. Classify any separator by its agent: ESA (phase creation), MSA (phase addition), barrier, or external field — this fixes its cost structure and design complexity.
2. Rate of separation is governed by mass transfer; extent is capped by thermodynamic equilibrium — both must be reviewed (Chs. 2–3) before design.
3. Always specify separation by BOTH product purity and component recovery, and close every component material balance around the process.
4. Distillation is the default industrial choice; move to absorption/extraction/adsorption only when volatility differences are too small, the feed is temperature-sensitive, or an MSA offers a selectivity advantage.
5. For N products from a sequence of simple columns, N−1 columns are needed but the number of alternative sequences grows combinatorially (5 products → 14 sequences); use the six heuristics to prune, with Heuristic 1 (safety/corrosion/volatility removal first) taking priority.
6. Cost rises steeply as the product becomes more dilute in the feed — prefer operations whose maturity matches the required scale before considering exotic techniques.
7. Membranes trade easy staging for re-pressurization and near-mandatory parallel units; adsorption needs a regeneration cycle — factor equipment limits into capacity planning early.

## Connects To
- **Ch 2**: Thermodynamic equilibrium (fugacity, K-values, activity coefficients) — the ceiling on separation extent invoked throughout this chapter.
- **Ch 3**: Mass transfer and rate limitations — sets how fast the partitioning in Fig. 1.6 proceeds.
- **Ch 4–5**: Single-stage flash/partial condensation (Table 1.1, Operations 1–2) and multistage distillation design.
- **Ch 6**: Absorption and stripping columns (Table 1.2, Operations 1–2) with the same tray/packing internals of Fig. 1.7.
- **Ch 8**: Liquid–liquid extraction — the MSA alternative when distillation is impractical.
- **Ch 14**: Membrane separations (dialysis, reverse osmosis, gas permeation, pervaporation, electrodialysis).
- **Ch 15**: Adsorption — the solid MSA operation and its regeneration cycle.
