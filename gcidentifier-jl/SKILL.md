---
name: gcidentifier-jl
description: Guide to GCIdentifier.jl — fragmenting a molecular SMILES or name into functional groups for group-contribution methods (UNIFAC, original UNIFAC, Joback, SAFT-γ Mie, gcPC-SAFT, gcPCP-SAFT, PR-78, GC-Aly-Lee), and proposing brand-new groups for molecules that aren't covered yet. Use this skill whenever the user works with group-contribution methods, holds a SMILES or SMARTS string and needs the corresponding groups, wants to fragment/decompose a molecule, needs to find or propose missing groups, or is building Clapeyron.jl group-contribution models such as `UNIFAC`, `SAFTgammaMie`, `JobackIdeal`, or `gcPCSAFT`. Trigger on any mention of group contribution, molecular fragmentation, SMILES-to-groups conversion, UNIFAC/Joback/SAFT-γ-Mie groups, SMARTS pattern matching for functional groups, or computer-aided molecular design (CAMD) — even when GCIdentifier is not named explicitly.
---

# GCIdentifier.jl — Molecular Fragmentation for Group-Contribution Methods

GCIdentifier takes a molecule (as a **SMILES** string, or a **name** via ChemicalIdentifiers) and decomposes it into the functional groups defined by an existing group-contribution (GC) method. It can also *propose new groups* for atoms no method covers yet. It is the bridge between "I have a structure" and "I can run a GC thermodynamic model in Clapeyron.jl".

## The mental model

Everything in this package is built on one idea: **a SMILES string gets matched against SMARTS patterns** (one pattern per group). The exported group lists (`UNIFACGroups`, `SAFTgammaMieGroups`, …) are just `Vector{GCPair}` where each `GCPair` holds a SMARTS pattern and a name. A function walks the molecule, matches every group, and reports `name => count`. When atoms are left uncovered, that's either an error (the default) or a signal to *propose* a new group.

- **SMILES** = describes a whole molecule (input). Aromatic atoms are lowercase: benzene is `c1ccccc1`, not `C1=CC=CC=C1`.
- **SMARTS** = a substructure query pattern (used internally to *find* a group). SMARTS strings contain backslashes, so they must be written as `raw"..."` in Julia.
- **Group list** = a `Vector{GCPair}`, e.g. `UNIFACGroups`.

## Which function do I need?

| Goal | Function |
|------|----------|
| Split a SMILES into groups for a known method | `get_groups_from_smiles(smiles, UNIFACGroups)` |
| Same, but I only have a molecule name | `get_groups_from_name("ethanol", UNIFACGroups)` (needs `using ChemicalIdentifiers`) |
| The method can't cover every atom — propose new groups | `find_missing_groups_from_smiles(smiles, SAFTgammaMieGroups)` |
| Fragment a molecule with no reference method at all | `find_missing_groups_from_smiles(smiles)` (no group-list arg) |
| Define my own groups / a new GC method | build a `Vector{GCPair}`, pass it to `get_groups_from_smiles` |
| Feed the result into Clapeyron | `UNIFAC(["water", (component, groups)])` |

## Supported group-contribution methods

Each is an exported `Vector{GCPair}` constant. Pass it as the second argument to the functions above.

| Constant | Method |
|----------|--------|
| `UNIFACGroups` | (Dortmund) modified UNIFAC |
| `ogUNIFACGroups` | Original UNIFAC |
| `JobackGroups` | Joback's method |
| `SAFTgammaMieGroups` | SAFT-γ Mie |
| `gcPCSAFTGroups` | gcPC-SAFT |
| `gcPPCSAFTGroups` | gcPCP-SAFT (also bound to the alias `gcPCPSAFTGroups` — same list, two names) |
| `EPPR78Groups` | Enhanced Predictive PR-78 |
| `Burkhardt2025Groups` | GC-Aly-Lee groups for ideal-gas heat capacity |
| `GCIdentifier.SAFTgammaMieChemeoGroups` | SAFT-γ Mie groups generated from the Chemeo database (not exported by name — qualify it) |

The `gcPPCSAFTGroups` / `gcPCPSAFTGroups` naming is a frequent source of confusion: they are **identical** (one is an alias). Use either.

---

## 1. Assign groups from a SMILES

```julia
using GCIdentifier

(smiles, groups) = get_groups_from_smiles("CC(Cc1ccc(cc1)C(C(=O)O)C)C", UNIFACGroups)
# ("CC(Cc1ccc(cc1)C(C(=O)O)C)C", ["COOH" => 1, "CH3" => 3, "CH" => 1, "ACH" => 4, "ACCH2" => 1, "ACCH" => 1])
```

Signature: `get_groups_from_smiles(smiles::String, groups; connectivity=false, check=true)`.

Returns a tuple `(smiles, groups)` where `groups` is a `Vector{Pair{String,Int}}` — group name `=>` how many times it occurs.

### `check=false`: partial assignment instead of an error

By default the function throws `Could not find all groups for …` when any atom is left uncovered (i.e. the method simply lacks a group for that atom). Pass `check=false` to get whatever groups *were* found — useful to see how far it got before switching to `find_missing_groups`:

```julia
# SAFT-γ Mie has no ketone group, so this throws by default:
(smiles, groups) = get_groups_from_smiles("CCC(=O)CC", SAFTgammaMieGroups; check=false)
# ("CCC(=O)CC", ["CH3" => 2, "CH2" => 2])
```

When the default throws, the cause is almost always one of: an unphysical/invalid SMILES, a SMARTS coverage gap in the method, or wrong atom casing (aromatic `c` vs aliphatic `C`).

---

## 2. Assign groups from a molecule name

```julia
using GCIdentifier, ChemicalIdentifiers     # ChemicalIdentifiers MUST be loaded

(component, groups) = get_groups_from_name("ibuprofen", UNIFACGroups)
# ("ibuprofen", ["COOH" => 1, "CH3" => 3, "CH" => 1, "ACH" => 4, "ACCH2" => 1, "ACCH" => 1])
```

Signature: `get_groups_from_name(name::String, groups; connectivity=false)`. The first return element is the *name you passed in* (not a SMILES), which is convenient because Clapeyron identifies components by name.

`get_groups_from_name` is provided by a package extension and only exists once `ChemicalIdentifiers` is loaded. Forgetting `using ChemicalIdentifiers` is the most common reason name lookup fails.

---

## 3. Propose missing or new groups — `find_missing_groups_from_smiles`

When a method can't cover a molecule, ask GCIdentifier to *invent* SMARTS groups for the uncovered atoms:

```julia
groups = find_missing_groups_from_smiles("CCC(=O)CC", SAFTgammaMieGroups)
# 3-element Vector{GCPair}:
#  GCPair("[CX3;H0;!R]", "C=")
#  GCPair("[OX1;H0;!R]", "O=")
#  GCPair("[CX3;H0;!R](=[OX1;H0;!R])", "C=O=")
```

Signature: `find_missing_groups_from_smiles(smiles, groups=nothing; max_group_size=nothing, environment=false, reduced=false)`. Returns `Vector{GCPair}`.

- **`groups=nothing`** (the default) → ignore any existing method and fragment the *whole* molecule into candidate groups. This is how you bootstrap a brand-new GC method.
- **`reduced=true`** → apply internal heuristics and return only the *minimal* recommended set. Without it you get every candidate combination. Start with `reduced=true`; drop it only when you want to see all options.
- **`max_group_size=N`** → allow groups spanning up to `N` heavy atoms. The default (`nothing`) keeps groups tiny (≈1–2 atoms). For large molecules with a cluster that *should* be one group (e.g. a phosphate), raise this so the cluster combines into a single group instead of fragmenting.
- **`environment=true`** → bake the neighbour context into each group's SMARTS. A single `CH2` becomes several distinct `CH2(...)` groups depending on what it's bonded to. Produces far more groups; use when neighbour identity matters for parameter fitting.

Combination heuristic worth knowing: two adjacent carbons are generally **not** merged into one group (similar electronegativity → little property impact), but carbon–heteroatom combinations are. That's why ketones become `C=O=` rather than separate `C=` and `O=` under `reduced=true`.

### Worked example: tuning `max_group_size`

For adenylic acid, tiny groups split the phosphate into `O=`, `OH`, etc. Raising `max_group_size=5` collapses it into one sensible `POO=OHOH` group:

```julia
find_missing_groups_from_smiles("C1=NC(=C2C(=N1)N(C=N2)C3C(C(C(O3)COP(=O)(O)O)O)O)N";
                                 reduced=true, max_group_size=5)
```

---

## 4. Connectivity between groups

Some methods (gcPCP-SAFT, s-SAFT-γ Mie) need to know *how* groups are linked, not just which groups exist. Pass `connectivity=true`:

```julia
(smiles, groups, connectivity) = get_groups_from_smiles("CC(=O)C", gcPPCSAFTGroups; connectivity=true)
# ("CC(=O)C", ["C=O" => 1, "CH3" => 2], [("C=O", "CH3") => 2])
```

`connectivity` is a `Vector{Pair{Tuple{String,String},Int}}` — a `(groupA, groupB) => bond_count` pair per inter-group link. The return value is now a **3-tuple**. This works for both `get_groups_from_smiles` and `get_groups_from_name`.

---

## 5. Custom groups and new GC methods

A group is a `GCPair`:

```julia
struct GCPair
    smarts::String      # SMARTS query pattern
    name::String        # arbitrary label
    group_order::Int    # 1 = primary; >1 for Constantinou-Gani second-order groups
    multiplicity::Int
end
GCPair(smarts, name; group_order=1, multiplicity=1)
```

Build your own list and pass it straight in:

```julia
mygroups = [GCPair(raw"[CX4H3]", "CH3"), GCPair(raw"[CX4H2]", "CH2")]
get_groups_from_smiles("CCCC", mygroups)   # ("CCCC", ["CH3" => 2, "CH2" => 2])
```

Two critical points when authoring SMARTS:

1. **Always use `raw"..."` strings.** SMARTS patterns contain backslashes (e.g. `$([...])`, `\`-escapes). A normal `"..."` string will mangle them and matching silently fails. `GCPair("[CX4H3]", "CH3")` happens to work only because it has no backslashes — don't rely on that; use `raw"..."` as a habit.
2. **Validate the SMARTS** before trusting it. Cross-check against the [SMARTS theory spec](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html) or visualise it at [smarts.plus](https://smarts.plus). A pattern that matches too broadly or too narrowly is the usual bug.

The built-in group lists (e.g. `UNIFACGroups` in `src/database/UNIFAC.jl`) are the best reference for correct SMARTS — copy their style when adding groups.

### Multi-order groups (Constantinou–Gani style)

Set `group_order=2` (or higher) on some `GCPair`s. Order-1 groups are matched with strict full-coverage checking; order ≥2 are matched *without* strict coverage and independently, so second-order groups refine an already-complete order-1 assignment rather than replacing it.

---

## 6. Helpers

### `group_replace` — rewrite a group list after the fact

```julia
(smiles, groups) = get_groups_from_smiles("CCO", UNIFACGroups)  # [..., "OH (P)" => 1, ...]
# Replace each "OH (P)" with one "OH"; split each "CH3" into "C"=>1 and "H"=>3
group_replace(groups, "OH (P)" => ("OH" => 1), "CH3" => [("C" => 1), ("H" => 3)])
```

Useful when a downstream tool expects different group names than the GC method produces.

### `gcstring"..."` — a literal group list (not exported)

The `@gcstring_str` macro behind `gcstring"..."` is **not exported**, so it is not in scope after a plain `using GCIdentifier`. Bring it in explicitly first:

```julia
using GCIdentifier: @gcstring_str
gcstring"CH3:2;CH2:1"  # == ["CH3" => 2, "CH2" => 1]
```

Handy for writing expected group lists compactly (e.g. in tests or known answers). For one-off group lists you can also just write the pairs directly — `["CH3" => 2, "CH2" => 1]` — with no import needed.

---

## 7. Bridge into Clapeyron.jl

GCIdentifier's `(component, groups)` tuple plugs directly into Clapeyron's group-contribution model constructors. Clapeyron is a *weak dependency* — load it with `using Clapeyron` and the bridge activates automatically.

```julia
using GCIdentifier, Clapeyron

(component, groups) = get_groups_from_name("ibuprofen", UNIFACGroups)
model = UNIFAC(["water", (component, groups)])
activity_coefficient(model, 1e5, 298.15, [1.0, 0.0])
```

The same tuple shape works for `SAFTgammaMie([...])`, `JobackIdeal([...])`, `gcPCSAFT([...])`. If you already constructed a Clapeyron GC model type, the Clapeyron extension even lets you pass that *type* as the group list and GCIdentifier resolves the right SMARTS set via `get_grouplist`.

### Full example: solid-liquid solubility

```julia
using GCIdentifier, Clapeyron

(component, groups) = get_groups_from_name("ibuprofen", UNIFACGroups)
liquid = UNIFAC(["water", (component, groups)])
solid  = SolidHfus(["water", "ibuprofen"])
model  = CompositeModel(["water", "ibuprofen"]; solid=solid, liquid=liquid)
sle_solubility(model, 1e5, 298.15, [1.0, 0.0]; solute=["ibuprofen"])[2]
```

For the thermodynamic-property side of this workflow (activity coefficients, flash, saturation, etc.), defer to the **clapeyronjl-skill** — this skill only owns the *fragmentation → group tuple* step.

---

## Common pitfalls

- **SMARTS without `raw"..."`** → silent match failure. Use raw strings for every hand-written SMARTS.
- **Name lookup does nothing** → `using ChemicalIdentifiers` is missing.
- **`get_groups_from_smiles` throws "Could not find all groups"** → the method genuinely lacks a group for some atom. Use `check=false` to inspect the partial result, then `find_missing_groups_from_smiles` to propose the missing group(s).
- **Wrong atom casing in SMILES** → aromatic atoms are lowercase (`c`, `n`, `o`). `C1=CC=CC=C1` and `c1ccccc1` are different inputs.
- **Forgot the 3-tuple** → with `connectivity=true` the return has three elements; destructure as `(smiles, groups, connectivity)`.
- **`gcPCPSAFTGroups` vs `gcPPCSAFTGroups`** → identical; the alias exists for historical naming. Don't treat them as different methods.
- **First call is slow** → Julia compiles on first use; subsequent calls are fast. Precompilation, not a bug.
- **`gcstring"..."` fails with `UndefVarError: @gcstring_str`** → the macro isn't exported. Add `using GCIdentifier: @gcstring_str`, or just write the pairs literally as `["CH3" => 2]`.

## Reference

- Docs: https://clapeyronthermo.github.io/GCIdentifier.jl/dev
- Source: https://github.com/ClapeyronThermo/GCIdentifier.jl
- SMARTS spec: https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html
- Cite: Walker, Riedemann & Wang, *J. Open Source Softw.* **9**(96), 6453 (2024), doi:10.21105/joss.06453
