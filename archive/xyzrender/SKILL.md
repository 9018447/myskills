---
name: xyzrender
description: Use this skill when the user wants publication-quality molecular graphics or animations from XYZ, PDB, SDF, CIF, SMILES, quantum chemistry outputs, or cube files using xyzrender. Trigger it for requests involving molecule rendering, presets, surfaces, overlays, transition states, orbital or density plots, or CLI/Python workflows around xyzrender, even if the user only describes the chemistry goal and does not name the library directly.
compatibility: Requires Bash or Python access when installation, CLI execution, or script examples need to be verified.
---

# xyzrender

Use this skill to work with the `xyzrender` Python package and CLI for molecular structure rendering. It is best for tasks that need accurate install guidance, command construction, Python API usage, preset selection, optional dependency handling, troubleshooting around exported SVG, PNG, PDF, or GIF outputs, and local workflows that generate cube data with Multiwfn before handing off to xyzrender.

## When to use this skill

Use it when the user wants to:

- render molecules from structure files such as XYZ, PDB, MOL/SDF, MOL2, CIF, or SMILES
- render from quantum chemistry outputs or cube files
- generate cube files from `*.fchk` with Multiwfn for downstream xyzrender rendering, especially NCI surface and ESP workflows
- generate static figures, rotation GIFs, trajectory GIFs, or transition-state visuals
- choose or customize xyzrender presets such as `default`, `flat`, `paton`, `pmol`, `skeletal`, `wire`, or `graph`
- use the Python API (`load`, `render`, `render_gif`, `measure`, `orient`, `build_config`) instead of the CLI
- diagnose missing extras for SMILES, CIF, or interactive orientation support

## Communicating with the user

Keep the guidance practical and chemistry-task-oriented. Translate the user’s goal into the smallest working `xyzrender` command or Python snippet that matches their input files and desired output. If the real workflow starts in Multiwfn rather than xyzrender, say so immediately and give the handoff point clearly. Prefer concrete commands, file paths, and flags over abstract descriptions.

## Workflow

1. Identify the input type: structure file, quantum chemistry output, cube file, SMILES string, or trajectory/ensemble.
2. Identify the target output: inline preview, SVG, PNG, PDF, or GIF.
3. Choose the narrowest viable interface:
   - CLI for one-off rendering and export commands
   - Python API for notebooks, scripts, repeated rendering, or programmatic configuration
4. Check whether optional dependencies are required:
   - `xyzrender[smi]` for SMILES via rdkit
   - `xyzrender[cif]` for CIF parsing via ase
   - `xyzrender[v]` for interactive orientation with `v`
   - `xyzrender[all]` when the task may need several extras
5. Build the command or snippet using the simplest working preset first, then add style or feature flags only if the user asked for them.
6. If the user asks for custom styling, prefer presets or `build_config` before inventing low-level changes.
7. If the request is about NCI surface or ESP and the user has `*.fchk` files, check whether the fastest path is to generate cube files with Multiwfn first and then render with xyzrender.
8. If troubleshooting is needed, check dependency extras, file format support, output backend behavior, and whether the requested feature is CLI-based or API-based.

## Workspace integrations

This workspace already contains local helper assets that should be preferred when they match the user’s request:

- `nci.txt` at the workspace root for driving `Multiwfn *.fchk < nci.txt` in the local NCI workflow
- `drawesp/fchk2cub.sh` for batch generation of `DENSITY*.cube` and `ESP*.cube` from `*.fchk`
- `drawesp/cube2esp.sh` for batch rendering those ESP surfaces with `xyzrender`

When these files exist, do not reinvent the workflow. Reuse them and explain the handoff into xyzrender.

## Installation and setup

Use only installation paths supported by the repository:

```bash
pip install xyzrender
pip install --upgrade git+https://github.com/aligfellow/xyzrender.git
uv tool install xyzrender
uvx xyzrender
```

Optional extras:

```bash
pip install 'xyzrender[smi]'
pip install 'xyzrender[cif]'
pip install 'xyzrender[v]'
pip install 'xyzrender[all]'
```

Development workflow from source:

```bash
git clone https://github.com/aligfellow/xyzrender.git
cd xyzrender
pip install -e .
just setup
just check
```

Useful project commands:

- `just lint`
- `just type`
- `just test`
- `just fix`
- `just build`

## CLI patterns

Start from a minimal command and expand only when needed:

```bash
xyzrender caffeine.xyz
xyzrender caffeine.xyz -o figure.png
xyzrender calc.out --ts -o ts.png
xyzrender caffeine.xyz --gif-rot -go movie.gif
xyzrender caffeine.xyz --config paton --hy -o styled.svg
```

Use these patterns when mapping user requests:

- static structure figure → `xyzrender input.xyz -o figure.svg`
- alternate raster/vector export → choose output extension such as `.png` or `.pdf`
- transition state visualization → `--ts`
- NCI surface from cube data → `xyzrender dens.cube --nci-surf grad.cube -o nci_surface.svg`
- ESP-mapped density surface → `xyzrender dens.cube --esp esp.cube -o esp_surface.svg`
- rotation animation → `--gif-rot -go output.gif`
- preset-driven appearance → `--config <preset>`
- explicit hydrogens → `--hy`

## Multiwfn handoff patterns

Use these patterns when the user starts from `*.fchk` rather than ready-made cube files.

### NCI surface from `*.fchk`

In this workspace, a local Multiwfn driver file already exists:

```bash
Multiwfn molecule.fchk < nci.txt
```

This workflow produces the two volumetric files needed for xyzrender NCI surface rendering. If Multiwfn writes them as `.cub`, rename them to `.cube` before passing them to xyzrender:

```bash
mv density.cub density.cube
mv grad.cub grad.cube
xyzrender density.cube --nci-surf grad.cube -o nci_surface.svg
```

If the generated filenames differ, keep the same role mapping: density cube as the primary input, RDG/gradient cube as the `--nci-surf` input.

### ESP from `*.fchk`

This workspace also has a ready-made batch workflow:

```bash
bash drawesp/fchk2cub.sh
bash drawesp/cube2esp.sh
```

The first script runs Multiwfn on each `*.fchk` and writes paired files named like `DENSITY*.cube` and `ESP*.cube`. The second script renders them with:

```bash
xyzrender DENSITYname.cube --esp ESPname.cube --iso 0.005 --opacity 0.75 -o name_esp.svg
```

For one-off rendering, mirror the same pairing manually instead of inventing a different layout.

## Python API patterns

Use the public API exported by `xyzrender`:

```python
from xyzrender import load, render, render_gif

mol = load("caffeine.xyz")
render(mol)
render(mol, output="caffeine.svg")
render(mol, config="paton", hy=True)
render_gif(mol, gif_rot="y")
```

Public API components worth reaching for:

- `load`
- `render`
- `render_gif`
- `measure`
- `orient`
- `build_config`
- `load_cmap`
- `Molecule`
- `RenderConfig`
- `StyleRegion`

Prefer `load()` when the task starts from files or SMILES, and `render()` when the goal is a single exported figure. Use `render_gif()` only for actual animation tasks.

When the user starts from Multiwfn-generated cube files, the Python handoff stays simple:

```python
from xyzrender import load, render

mol = load("density.cube")
render(mol, nci="grad.cube", output="nci_surface.svg")
render(mol, esp="esp.cube", output="esp_surface.svg")
```

## Feature mapping

Map common user goals to known xyzrender features:

- preset styling → `config`
- hydrogen visibility → `hy` / `no_hy`
- bond order display → `bo`
- transition-state or NCI bonds → `ts_bonds`, `nci_bonds`, or auto-detection options during loading
- volumetric or surface visualization → `mo`, `dens`, `esp`, `nci`, `vdw`, `hull`, `cmap`
- region-specific styling → `regions`
- structural alignment overlays → `overlay`
- measurements → `measure`
- interactive orientation → `orient` with the `v` extra available

If the user asks for a custom look, mention the built-in presets first: `default`, `flat`, `paton`, `pmol`, `skeletal`, `bubble`, `tube`, `mtube`, `wire`, `graph`.

For NCI surface requests, distinguish carefully between:

- `--nci` / `nci_bonds` for dotted NCI interaction overlays on a structure
- `--nci-surf` in the CLI or `nci=` in Python for true NCI surface rendering from cube data

## Troubleshooting

- SMILES input failing usually means rdkit is missing: install `xyzrender[smi]`.
- CIF input failing usually means ase is missing: install `xyzrender[cif]`.
- Interactive orientation requires the `v` integration and is not a default install path.
- NCI surface needs cube data, not a plain `.xyz` alone. If the user only has `*.fchk`, route through Multiwfn first.
- In this workspace, Multiwfn may emit `.cub`; renaming to `.cube` is acceptable before passing files to xyzrender.
- For ESP in this workspace, prefer the existing `drawesp/fchk2cub.sh` and `drawesp/cube2esp.sh` scripts instead of rewriting the pipeline.
- If a raster or PDF export behaves differently from SVG, mention that conversion backends may differ and `cairosvg` fallback can ignore some filters.
- If the request involves a feature not clearly documented, prefer repository-backed examples and note the uncertainty instead of guessing hidden flags.

## Output format

When answering with concrete usage guidance, prefer this structure:

```text
Install: <only if needed>
Command or code: <smallest working example>
Why this fits: <one short sentence>
Notes: <optional dependency or limitation only if relevant>
```

## Examples

**Example 1**

Input: Render `caffeine.xyz` to a PNG using a PyMOL-like style and show hydrogens.

Output:

```bash
xyzrender caffeine.xyz --config paton --hy -o caffeine.png
```

Why this fits: `paton` is a built-in preset and `--hy` makes hydrogen display explicit.

**Example 2**

Input: Generate a rotation GIF from an XYZ file in Python.

Output:

```python
from xyzrender import load, render_gif

mol = load("caffeine.xyz")
render_gif(mol, gif_rot="y", output="caffeine.gif")
```

Why this fits: it uses the public API directly for an animation workflow.

**Example 3**

Input: Render a SMILES string but the environment does not have rdkit installed.

Output:

```bash
pip install 'xyzrender[smi]'
```

Then load or render with SMILES support enabled.

Why this fits: SMILES support is optional, not included in the base install.

**Example 4**

Input: I have `calc.fchk` and want an NCI surface with the local Multiwfn workflow before rendering in xyzrender.

Output:

```bash
Multiwfn calc.fchk < nci.txt
mv density.cub density.cube
mv grad.cub grad.cube
xyzrender density.cube --nci-surf grad.cube -o calc_nci.svg
```

Why this fits: the local workflow starts in Multiwfn, then hands the density and RDG/gradient cube files to xyzrender for NCI surface rendering.

**Example 5**

Input: Batch-convert all `*.fchk` files to ESP figures using the local helper scripts.

Output:

```bash
bash drawesp/fchk2cub.sh
bash drawesp/cube2esp.sh
```

Why this fits: the first script generates the `DENSITY*.cube` and `ESP*.cube` pairs with Multiwfn, and the second script renders them with xyzrender.

## Evals

If you evaluate or improve this skill, store test prompts in `evals/evals.json` and keep the field names aligned with `skill-creator/references/schemas.md`.

## Resources

- Repository: https://github.com/aligfellow/xyzrender
- Docs: https://xyzrender.readthedocs.io/
- Installation guide: https://xyzrender.readthedocs.io/en/latest/installation.html
- CLI quickstart: https://xyzrender.readthedocs.io/en/latest/quickstart_cli.html
- Python API guide: https://xyzrender.readthedocs.io/en/latest/python_api.html
- Configuration: https://xyzrender.readthedocs.io/en/latest/configuration.html
- CLI reference: https://xyzrender.readthedocs.io/en/latest/cli_reference.html
- Formats: https://xyzrender.readthedocs.io/en/latest/formats.html
