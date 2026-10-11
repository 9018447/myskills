# Patterns — Separation Process Principles (Seader, Henley & Roper, 4th ed.)

## Shortcut Distillation Design (FUG)
**When to use**: initial multicomponent column design / simulator estimates; keys are defined, split specs given.
**How**: keys & splits → set P & condenser (total ≤215 psia; partial 215–365; refrigerant above; 0.1 psi/tray ΔP) → Fenske N_min at total reflux → distribute non-keys (Fenske 9-14 to 9-16, or Winn for wide-boiling) → Underwood θ-roots → R_min → Gilliland (Molokanov/Eduljee fits) → Kirkbride feed stage → iterate 2–3× on guessed non-key splits. Optimum near R/R_min ≈ 1.3 (N/N_min ≈ 2).
**Trade-offs**: fast and robust, but assumes constant α and CMO; unreliable for strongly nonideal or stripping-dominated splits (Gilliland fails there) — verify with rigorous Ch 10 model.

## McCabe–Thiele (binary graphical)
**When to use**: binary systems, near-ideal VLE, constant molar overflow; teaching/verification of simulator results.
**How**: draw 45° line + equilibrium curve; q-line from feed condition; rectifying line slope R/(R+1) through (x_D,x_D); stripping line through (x_B,x_B); step stages between lines; feed stage where lines switch. Limiting constructions: total-reflux staircase = N_min; pinch construction = R_min.
**Trade-offs**: transparent geometry but only binary; nonideal systems need careful curve fitting; superseded by simulators for final design.

## Rigorous Equilibrium-Stage Solution
**When to use**: final design of any column; nonideal / wide-boiling / multicomponent systems.
**How**: MESH equations (N(2C+3)); pick method by system: BP (Wang–Henke) for narrow-boiling near-ideal (now mostly initializer); SR (Burningham–Otto) for wide-boiling absorbers/strippers; SC (Naphtali–Sandholm) Newton block-tridiagonal for difficult/polar; inside-out (Boston–Sullivan) as the simulator default with approximate-property inner loop; ISR (Tsuboka–Katayama) for LLE. Start from standard spec pairs (e.g. R and D or B flow) — exotic specs rarely converge.
**Trade-offs**: SC handles hardest problems at 3–10× BP cost; inside-out scales best; convergence needs sensible initial T/L profiles.

## Rate-Based (Nonequilibrium) Modeling
**When to use**: polar/nonideal systems where tray efficiency is unpredictable; absorbers; tight-spec separations; rate-limited reactive systems.
**How**: 5C+5 or 5C+6 equations per stage (MERSHQ): separate-phase balances, Maxwell–Stefan interfacial flux with two-film coefficients (Chan–Fair trays; Billet–Schultes packing), interfacial equilibrium only, hydraulics for ΔP; solve SC block-tridiagonal; back-calculate E_MV per tray or HETP per section to validate.
**Trade-offs**: 2–4× equilibrium-model cost and needs transport-property data; rewards you with efficiency prediction instead of guessing E_o.

## Packed Column Sizing (HTU–NTU + Hydraulics)
**When to use**: packed absorbers/strippers/distillation; corrosive/foaming/low-holdup service.
**How**: compute N_OG from y–x diagram or closed forms; H_OG = H_G + (KV/L)H_L via Billet–Schultes or vendor data; height Z = H_OG·N_OG; size diameter at 50–80% of flood (GPDC/Eckert charts, ΔP_flood ≈ 0.115 F_P^0.7 in H₂O/ft); check loading point (~70% flood) and HETP rules of thumb.
**Trade-offs**: forgiving on fouling/foaming vs trays' higher turndown and easier inspection; packing efficiency sensitive to distributor quality (>25 distribution points/m²).

## Tray Efficiency & Diameter
**When to use**: sieve/valve trayed columns.
**How**: diameter from Souders–Brown C-factor / Fair flooding correlation at target 80–85% flood; efficiency via O'Connell E_o = 50.3(αμ)^−0.226 (or Drickamer–Bradford on viscosity), Oldershaw data for scale-up; turndown: sieve ≈2, valve ≈4.
**Trade-offs**: valve trays cost more but double turndown; efficiency correlations are ±30% — rate-based model supersedes when accuracy matters.

## Enhanced Distillation Selection
**When to use**: azeotropes or α ≈ 1 where ordinary distillation stalls.
**How**: map residue curves/DRD first (Doherty–Perkins DAE; count singular points) → choose: extractive distillation (low-volatility H-bonded solvent above feed; solvent/feed ≈1; screen by infinite-dilution γ); pressure-swing (needs ≥5 mol% azeotrope shift); salt distillation (salting-out); homogeneous azeotropic (entrainer within same distillation region — Doherty–Caldarola Groups 1–5); heterogeneous with decanter (tie line breaks region restriction); reactive distillation (reaction and volatility windows overlap; equilibrium-limited reactions only).
**Trade-offs**: extractive = robust but solvent recovery column; pressure-swing = no additive but energy-hungry; heterogeneous = multiplicity of steady states — never trust a single converged simulation.

## Extraction Design (Hunter–Nash)
**When to use**: temperature-sensitive feeds, close boilers, azeotrope formers — where distillation is wrong tool.
**How**: solvent screen by selectivity β (Robbins chart → UNIFAC refine) → ternary diagram: mixing point M, difference point P, step stages via tie lines → S_min from pinch tie line; operate ≈1.5·S_min → check solutropy (tie-line reversal) → equipment: mixer-settler (staged), RDC/Karr (columns), centrifugal (small Δρ).
**Trade-offs**: gentle thermal treatment vs solvent inventory + recovery distillation; Type II systems allow extract reflux, Type I do not.

## Fixed-Bed Adsorption Design
**When to use**: trace PPM-level removal, drying, PSA gas separation, SMB chiral/isomer splits.
**How**: isotherm fit (Langmuir/Freundlich/Toth; IAS for mixtures) → constant-pattern Klinkenberg/LDF breakthrough model → bed length L_B = LES + LUB (Collins scale-up from lab curve) → regeneration cycle: PSA (fast gases), TSA (deep drying), displacement-purge (weakly adsorbed species) → SMB via triangle method with β≈1.05–1.2 safety margin.
**Trade-offs**: equilibrium capacity alone never sizes a bed — MTZ does; PSA energy-lean but low recovery; SMB continuous but complex valving.

## Membrane Process Design
**When to use**: gas PPM removal, RO desalination, azeotrope dehydration (pervaporation), organics recovery.
**How**: solution–diffusion transport P_M = S·D → module flow pattern (countercurrent best selectivity; crossflow ≈ Rayleigh) → cascade for purity (permeate recycle); check pressure-ratio degradation α_eff ≤ p_R/p_P; account for concentration polarization Γ and fouling.
**Trade-offs**: low energy vs modest single-stage selectivity — Robeson tradeoff means cascades or hybrid (membrane+distillation) for high purity.

## Batch Distillation
**When to use**: small/variable campaigns, multiproduct pots, heat-sensitive fine chemicals.
**How**: Rayleigh differential for simple stills; rectifier with constant reflux (Smoker–Rose) or constant composition (Bogart); slop cuts between product cuts; rigorous case = stiff DAE (Meadows/Distefano; BatchSep/CC-BATCH); optimal reflux via Pontryagin/DP (Diwekar).
**Trade-offs**: flexible but off-spec intermediate cuts recycle; holdup degrades sharpness; operationally labor-intensive.

## Process Sequencing Heuristics (Ch 1)
**When to use**: choosing operations and column order for a new separation train.
**How**: classify by ESA/MSA and phase creation/addition/barrier/field → pick most mature/cheapest operation that meets spec → order distillation sequence: hardest/most corrosive/most volatile first; easiest split last; recover valuable/unsafe components early.
**Trade-offs**: heuristics are ±; sequence count grows combinatorially (5 products → 42 sequences) — simulator-based sequence optimization eventually wins.
