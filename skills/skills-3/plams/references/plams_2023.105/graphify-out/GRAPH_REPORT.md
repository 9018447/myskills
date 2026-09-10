# Graph Report - .  (2026-04-10)

## Corpus Check
- Large corpus: 356 files · ~463,335 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 557 nodes · 776 edges · 121 communities detected
- Extraction: 56% EXTRACTED · 44% INFERRED · 0% AMBIGUOUS · INFERRED: 344 edges (avg confidence: 0.51)
- Token cost: 145,116 input · 20,689 output

## God Nodes (most connected - your core abstractions)
1. `keys()` - 19 edges
2. `cb()` - 17 edges
3. `nn()` - 15 edges
4. `iteratee()` - 14 edges
5. `max()` - 13 edges
6. `qn()` - 10 edges
7. `each()` - 9 edges
8. `mr()` - 9 edges
9. `Job Component` - 9 edges
10. `Ee()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `ADFCOSMORSCompound` --generates_input_for--> `COSMO-RS Interface`  [EXTRACTED]
  examples/ADFCOSMORSCompound.md → interfaces/crs.md
- `ChargedAMSCalculator` --uses--> `AMSCalculator Interface`  [EXTRACTED]
  examples/AMSCalculator/ChargedAMSCalculator.md → interfaces/amscalculator.md
- `Job Component` --can_contain--> `Molecule Component`  [INFERRED]
  components/jobs.md → components/molecule.md
- `Geometry Optimization` --uses_method--> `Parallel Job Execution`  [INFERRED]
  examples/WaterOptimization.md → examples/ManyJobsInParallel.md
- `Reaction Energy Benchmark` --evaluates--> `Geometry Optimization`  [INFERRED]
  examples/ReactionEnergyBenchmark.md → examples/WaterOptimization.md

## Hyperedges (group relationships)
- **plams_workflow** — job_component, results_component, jobrunner_component, parallel_job_execution, molecule_component [EXTRACTED 0.90]
- **trajectory_formats** — xyz_component, dcd_component, rkf_trajectory [EXTRACTED 1.00]

## Communities

### Community 0 - "JavaScript Underscore"
Cohesion: 0.04
Nodes (85): allKeys(), baseCreate(), baseIteratee(), cb(), chain(), chainResult(), clone(), collectNonEnumProps() (+77 more)

### Community 1 - "jQuery Core"
Cohesion: 0.04
Nodes (49): addCombinator(), adoptValue(), ajaxConvert(), ajaxHandleResponses(), Animation(), boxModelAdjustment(), buildFragment(), buildParams() (+41 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (35): A(), Ae(), b(), be(), Bt(), ce(), D(), Dt() (+27 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (40): A(), an(), br(), Dn(), en(), fn(), Gr(), hr() (+32 more)

### Community 4 - "Job Classes"
Cohesion: 0.07
Nodes (28): AMSJob, Config Settings, DiracJob, Dot Notation, finish Function, init Function, Job Component, JobManager Component (+20 more)

### Community 5 - "MoleculesTable Analysis"
Cohesion: 0.18
Nodes (15): analyze_bonds(), analyze_molecules(), bo2symbol(), main(), plot_results(), Round off bond order to integer or half integer., Convert bond order to bond symbol., ams_rkf_path: str             Path to an ams.rkf file from a reactive MD simulat (+7 more)

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (11): hybrid_settings(), initial_pesscan(), main(), plot_results(), Generate a plot of the energy vs. bond length for the three different jobs.  Sav, Run a bond scan for hydrogen peroxide with UFF. Returns the finished job, Look at the file plams_workdir/hybrid/hybrid.in to see how the below is translat, Replay the structures from the UFF pesscan with ADF. Use three different engines (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.36
Nodes (6): addition(), get_active_i(), get_atom_radius(), preliminary_md(), relax_from_saddle(), ts_search()

### Community 8 - "Community 8"
Cohesion: 0.43
Nodes (7): adf_settings(), get_molecule(), main(), Run a TS search with Sella, Run DFT transition state search but use initial hessian calculated with DFTB, run_ams(), run_sella()

### Community 9 - "Community 9"
Cohesion: 0.38
Nodes (4): main(), MoleculeConnector, Returns: Molecule with the ligand added to the substrate, replacing the respecti, substitute()

### Community 10 - "Community 10"
Cohesion: 0.43
Nodes (6): get_settings(), get_system(), main(), pseudopotentials_block(), Returns a PLAMS Molecule for FeO with the QE.Label properties set to 'Fe1'     a, Transforms a dictionary to a single string

### Community 11 - "Community 11"
Cohesion: 0.53
Nodes (4): changeTabs(), deselectTabList(), selectNamedTabs(), selectTab()

### Community 12 - "Community 12"
Cohesion: 0.6
Nodes (5): generate_coskf(), main(), plot_results(), plot_sigma_profile(), solubility()

### Community 13 - "Core Interfaces"
Cohesion: 0.33
Nodes (6): ADF Interface, AMS Driver, AMSCalculator Interface, ChargedAMSCalculator, Conformers Interface, MOPAC Interface

### Community 14 - "Community 14"
Cohesion: 0.6
Nodes (4): fcf(), freq(), main(), Frequency calculation

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (4): get_excitations(), has_good_excitations(), Returns True if there is at least one excitation with non-vanishing oscillator s, Returns excitation energies (in eV) and oscillator strenghts (in Debye).

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 0.83
Nodes (3): get_main_results(), plot_conformers(), print_results()

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (2): Show a molecule in a Jupyter notebook, show()

### Community 19 - "Community 19"
Cohesion: 0.83
Nodes (3): main(), plot_results(), run_md()

### Community 20 - "Community 20"
Cohesion: 0.5
Nodes (2): get_calculator(), Return an ASE calculator for use with Engine ASE.           The function must be

### Community 21 - "Results Classes"
Cohesion: 0.5
Nodes (4): AMSResults, DiracResults, Results Component, VASPResults

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (2): main(), print_results()

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (2): convert_to_ams_rkf_with_bond_guessing(), main()

### Community 24 - "Example Workflows"
Cohesion: 1.0
Nodes (3): Geometry Optimization, Parallel Job Execution, Reaction Energy Benchmark

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "MD Analysis"
Cohesion: 1.0
Nodes (2): Molecular Dynamics Jobs, MoleculesTable Analysis

### Community 37 - "COSMO-RS"
Cohesion: 1.0
Nodes (2): ADFCOSMORSCompound, COSMO-RS Interface

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Calculate the difference between HOMO and IP.         *jobplus* should be the co

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Documentation"
Cohesion: 1.0
Nodes (1): Getting Started

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Introduction

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): M3GNet Universal Potential

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): i-PI Path Integral MD

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Sella Transition State Search

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): ConvertToAMSRKFTrajectory

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Reduction Oxidation Potentials

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Charge Transfer Integrals ADF

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Basis Set Benchmark

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Basic MD Postanalysis

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): ADF Fragment

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): BAND NiO HubbardU

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): FCF DOS

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): pyAHFCDOS

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): ParAMS Interface

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): PostADF Tools

### Community 70 - "Quick Jobs"
Cohesion: 1.0
Nodes (1): Quick Jobs

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Zacros Interface

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): DFTB+ Interface

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Crystal Interface

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): RASPA Interface

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): KF Files Tools

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): PLAMS Cookbook

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): ORCA Interface

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): VASP Interface

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): DIRAC Interface

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): ReaxFF Interface

### Community 81 - "AMS Suite"
Cohesion: 1.0
Nodes (1): Amsterdam Modeling Suite

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): AMS Worker

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): Packmol Interface

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): DCD Trajectory

### Community 85 - "PLAMS Functions"
Cohesion: 1.0
Nodes (1): Public Functions

### Community 86 - "Trajectories"
Cohesion: 1.0
Nodes (1): Trajectories Module

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): XYZ Trajectory

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): ASE Interface

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): Third-Party Interfaces

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): ADF Engine

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (1): BAND Engine

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): DFTB Engine

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): MOPAC Engine

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): ForceField Engine

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): AMSWorkerResults

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): AMSWorkerPool

### Community 97 - "Community 97"
Cohesion: 1.0
Nodes (1): load Function

### Community 98 - "Community 98"
Cohesion: 1.0
Nodes (1): load_all Function

### Community 99 - "Community 99"
Cohesion: 1.0
Nodes (1): read_molecules Function

### Community 100 - "Community 100"
Cohesion: 1.0
Nodes (1): check Method

### Community 101 - "Community 101"
Cohesion: 1.0
Nodes (1): hash Method

### Community 102 - "Community 102"
Cohesion: 1.0
Nodes (1): Pickling

### Community 103 - "Rerun Prevention"
Cohesion: 1.0
Nodes (1): Rerun Prevention

### Community 104 - "Community 104"
Cohesion: 1.0
Nodes (1): Restart Mechanism

### Community 105 - "Community 105"
Cohesion: 1.0
Nodes (1): Preview Mode

### Community 106 - "Community 106"
Cohesion: 1.0
Nodes (1): Logging

### Community 107 - "Community 107"
Cohesion: 1.0
Nodes (1): log Function

### Community 108 - "Community 108"
Cohesion: 1.0
Nodes (1): Binding Decorators

### Community 109 - "Community 109"
Cohesion: 1.0
Nodes (1): add_to_class Function

### Community 110 - "Community 110"
Cohesion: 1.0
Nodes (1): add_to_instance Function

### Community 111 - "Community 111"
Cohesion: 1.0
Nodes (1): KF Files

### Community 112 - "Community 112"
Cohesion: 1.0
Nodes (1): RKF Trajectory

### Community 113 - "Community 113"
Cohesion: 1.0
Nodes (1): XYZHistoryFile

### Community 114 - "Community 114"
Cohesion: 1.0
Nodes (1): ASE Atoms

### Community 115 - "Community 115"
Cohesion: 1.0
Nodes (1): Pipe Interface

### Community 116 - "Community 116"
Cohesion: 1.0
Nodes (1): AMSWorkerError

### Community 117 - "Community 117"
Cohesion: 1.0
Nodes (1): Job Cleaning

### Community 118 - "Community 118"
Cohesion: 1.0
Nodes (1): Job Folder

### Community 119 - "Community 119"
Cohesion: 1.0
Nodes (1): Master Script

### Community 120 - "Community 120"
Cohesion: 1.0
Nodes (1): Hashing

## Knowledge Gaps
- **117 isolated node(s):** `Run a TS search with Sella`, `Run DFT transition state search but use initial hessian calculated with DFTB`, `Show a molecule in a Jupyter notebook`, `Frequency calculation`, `Run a bond scan for hydrogen peroxide with UFF. Returns the finished job` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 25`** (2 nodes): `language_data.js`, `splitQuery()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `doctools.js`, `highlight()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (2 nodes): `theme.js`, `t()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (2 nodes): `badge_only.js`, `r()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (2 nodes): `run-ase.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `ChargeTransferIntegralsADF.py`, `get_transfer_integrals()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `MoleculesFromRKFTrajectory.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (2 nodes): `ams_plumed.py`, `get_molecule()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (2 nodes): `M3GNet.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `property_prediction.py`, `get_csv()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (2 nodes): `BAND_NiO_HubbardU.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `MD Analysis`** (2 nodes): `Molecular Dynamics Jobs`, `MoleculesTable Analysis`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `COSMO-RS`** (2 nodes): `ADFCOSMORSCompound`, `COSMO-RS Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `searchindex.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `documentation_options.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `copybutton.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `ReactionEnergyBenchmark.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `ManyJobsInParallel.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `xrd.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Calculate the difference between HOMO and IP.         *jobplus* should be the co`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `He2DissociationCurve.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `BasisSetBenchmark.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `AMSCalculatorWorkerMode.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `ReorganizationEnergy.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `LiVoltageProfile.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `BandStructureExample.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `water_optimization.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `ams_settings_system.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `ChargedAMSCalculatorExample.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Documentation`** (1 nodes): `Getting Started`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Introduction`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `M3GNet Universal Potential`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `i-PI Path Integral MD`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Sella Transition State Search`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `ConvertToAMSRKFTrajectory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Reduction Oxidation Potentials`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Charge Transfer Integrals ADF`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Basis Set Benchmark`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Basic MD Postanalysis`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `ADF Fragment`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `BAND NiO HubbardU`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `FCF DOS`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `pyAHFCDOS`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `ParAMS Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `PostADF Tools`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Quick Jobs`** (1 nodes): `Quick Jobs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Zacros Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `DFTB+ Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Crystal Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `RASPA Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `KF Files Tools`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `PLAMS Cookbook`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `ORCA Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `VASP Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `DIRAC Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `ReaxFF Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `AMS Suite`** (1 nodes): `Amsterdam Modeling Suite`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `AMS Worker`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `Packmol Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `DCD Trajectory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PLAMS Functions`** (1 nodes): `Public Functions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Trajectories`** (1 nodes): `Trajectories Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `XYZ Trajectory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `ASE Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `Third-Party Interfaces`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `ADF Engine`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `BAND Engine`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `DFTB Engine`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `MOPAC Engine`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `ForceField Engine`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `AMSWorkerResults`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (1 nodes): `AMSWorkerPool`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 97`** (1 nodes): `load Function`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 98`** (1 nodes): `load_all Function`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 99`** (1 nodes): `read_molecules Function`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 100`** (1 nodes): `check Method`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 101`** (1 nodes): `hash Method`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 102`** (1 nodes): `Pickling`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Rerun Prevention`** (1 nodes): `Rerun Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 104`** (1 nodes): `Restart Mechanism`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 105`** (1 nodes): `Preview Mode`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 106`** (1 nodes): `Logging`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 107`** (1 nodes): `log Function`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 108`** (1 nodes): `Binding Decorators`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 109`** (1 nodes): `add_to_class Function`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 110`** (1 nodes): `add_to_instance Function`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 111`** (1 nodes): `KF Files`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 112`** (1 nodes): `RKF Trajectory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 113`** (1 nodes): `XYZHistoryFile`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 114`** (1 nodes): `ASE Atoms`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 115`** (1 nodes): `Pipe Interface`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 116`** (1 nodes): `AMSWorkerError`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 117`** (1 nodes): `Job Cleaning`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 118`** (1 nodes): `Job Folder`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 119`** (1 nodes): `Master Script`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 120`** (1 nodes): `Hashing`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 18 inferred relationships involving `keys()` (e.g. with `isObject()` and `has()`) actually correct?**
  _`keys()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `cb()` (e.g. with `iteratee()` and `baseIteratee()`) actually correct?**
  _`cb()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `nn()` (e.g. with `w()` and `Z()`) actually correct?**
  _`nn()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `iteratee()` (e.g. with `baseIteratee()` and `cb()`) actually correct?**
  _`iteratee()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `max()` (e.g. with `restArguments()` and `times()`) actually correct?**
  _`max()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Run a TS search with Sella`, `Run DFT transition state search but use initial hessian calculated with DFTB`, `Show a molecule in a Jupyter notebook` to the rest of the system?**
  _117 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `JavaScript Underscore` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._