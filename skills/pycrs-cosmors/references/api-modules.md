# API Modules

## `pyCRS.Database`

Use for managing a SQL-backed COSKF database.

Key responsibilities:
- create a `COSKFDatabase`
- add compounds and conformers from COSKF files
- store or clear physical properties
- estimate physical properties via `PropPred`
- query, modify, or delete database rows

Representative objects and methods mentioned in the docs:
- `pyCRS.Database.COSKFDatabase(path)`
- `add_compound(...)`
- `add_physical_property(...)`
- `estimate_physical_property(...)`
- `get_compounds(...)`
- `get_attribute_by_compound_id(...)`
- `modify_attribute_by_compound_id(...)`
- row classes such as `CompoundRow`, `ConformerRow`, and `PhysicalPropertyRow`

Primary source: `Database API.md`

## `pyCRS.Input`

Use for creating a pyCRS molecule from lightweight inputs such as SMILES.

The docs describe this module as the entry point for initializing `pyCRS.Molecule` objects.

Primary source: `Input.md`

## `pyCRS.Molecule`

Use when the user wants to work from a molecule object rather than from a database row.

The docs connect `Molecule` with:
- `FastSigma.estimate(...)`
- `PropPred.estimate(...)`
- property and sigma-profile style calculations from a single structure

Primary source: `Molecule.md`

## `pyCRS.Output`

Use for writing output artifacts from pyCRS molecule data, including KF-style outputs after estimation steps.

The docs show `pyCRS.Output.write_kf(...)` after `FastSigma.estimate(...)`.

Primary source: `Output.md`

## `pyCRS.PropPred`

Use for estimating physical properties, including temperature-dependent properties.

Representative entry point:
- `PropPred.estimate(molecule, properties='all', temperatures=[...], show_errors=False)`

Typical use:
- estimate one property or multiple properties
- compute values over temperature grids
- inspect predicted property fields attached to the molecule/result

Primary sources: `PropPred.md`, `Documentation 1.md`

## `pyCRS.FastSigma`

Use for estimating sigma profiles quickly from a molecule.

Representative entry point:
- `pyCRS.FastSigma.estimate(molecule, method='COSMO-RS', model='FS1', display=False)`

Typical use:
- sigma profile estimation for `COSMO-RS` or `COSMO-SAC`
- choosing a model such as `FS1` or `SG1`
- displaying or exporting results

Primary sources: `FaseSigma.md`, `Documentation 1.md`, `Documentation 8.md`, `Documentation 9.md`

## `pyCRS.CRSManager`

Use for multi-mixture job setup, execution, and output collection.

Core objects described by the docs:
- `pyCRS.CRSManager.CRSSystem(iteration=False)`
- `pyCRS.CRSManager.CRSMixture(**kwargs)`

Representative operations:
- `add_Mixture(...)`
- `runCRSJob()`
- `runCRSIteration(parameter_sett=None, history=False)`

This module is especially relevant when the user wants:
- multiple mixtures handled in one system
- iteration workflows instead of a single job
- organized outputs for phase-equilibrium style calculations

Primary sources: `CRSManager.md`, `pyCRS Basic Usage.md`, `Documentation.md`, `Documentation 14.md`
