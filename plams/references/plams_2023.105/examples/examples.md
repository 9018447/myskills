[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../_static/plams_logo.png) ](../index.html)

  * 

Table of contents

  * [General](../general.html)
  * [Introduction](../intro.html)
  * [Getting started](../started.html)
  * [Components overview](../components/components.html)
  * [Interfaces](../interfaces/interfaces.html)
  * Examples
    * Getting Started
      * [Geometry optimization of water](WaterOptimization.html)
      * [AMS Settings: Chemical System (Molecule)](Settings/AMSSettingsSystem.html)
      * [Helium dimer dissociation curve](He2DissociationCurve.html)
      * [Many jobs in parallel](ManyJobsInParallel.html)
    * Molecule analysis
      * [Extract frames from ams.rkf trajectory](MoleculesFromRKFTrajectory.html)
      * [Table molecule counts and bond count from reactive MD ams.rkf](MoleculesTable.html)
      * [Molecule substitution: Attach ligands to substrates](MoleculeSubstitution/MoleculeSubstitutionExample.html)
      * [Convert to ams.rkf trajectory with bond guessing](ConvertToAMSRKFTrajectory.html)
    * Benchmarks
      * [Benchmark accuracy of basis sets](BasisSetBenchmark.html)
      * [Reaction energies with many different engines](ReactionEnergyBenchmark.html)
    * Workflows
      * [Reduction and oxidation potentials](RedoxPotential.html)
      * [Workflow: filtering molecules based on excitation energies](ExcitationsWorkflow.html)
      * [AMS transition state workflow](AMSTSWorkflow/AMSTSWorkflow.html)
      * [Charge transfer integrals with ADF](ChargeTransferIntegralsADF.html)
      * [Tuning the range separation](gammascan.html)
      * [Conformers Generation](ConformersGeneration/ConformersGeneration.html)
    * COSMO-RS and property prediction
      * [Property Prediction](PropertyPrediction/PropertyPrediction.html)
      * [ADF and COSMO-RS workflow](ams_crs.html)
    * Packmol and AMS-ASE interfaces
      * [Packmol example](PackMolExample/PackMolExample.html)
      * [Engine ASE: AMS geometry optimizer with forces from any ASE calculator](CustomASECalculator.html)
      * [AMSCalculator: ASE geometry optimizer with AMS forces](AMSCalculator/ASECalculator.html)
      * [AMSCalculator: Access results files & Charged systems](AMSCalculator/ChargedAMSCalculator.html)
      * [i-PI path integral MD with AMS](i-PI-AMS.html)
      * [Sella transition state search with AMS](SellaTransitionStateSearch.html)
    * ParAMS and pyZacros
    * Other AMS calculations
      * [BAND: NiO with DFT+U](BAND_NiO_HubbardU.html)
      * [Band structure](BandStructure/BandStructure.html)
      * [AMS biased MD / PLUMED](AMSPlumedMD/AMSPlumedMD.html)
      * [Quantum ESPRESSO as an AMS engine: Antiferromagnetic FeO](QE_AMS_AFM_HubbardU.html)
      * [Basic molecular dynamics analysis](BasicMDPostanalysis.html)
      * [Hybrid engine: Use lowest energy](UseLowestEnergy.html)
      * [Universal Potential: M3GNet-UP-2022](M3GNet.html)
    * Pymatgen
      * [X-Ray Diffraction (XRD)](XRD/XRD.html)
    * Pre-made recipes
      * [ADF: Task COSMO-RS Compound](ADFCOSMORSCompound.html)
      * [AMS Molecular Dynamics PLAMS jobs](MDJobs.html)
      * [ADF fragment job](adffragment.html)
      * [Reorganization Energy](ReorganizationEnergy.html)
      * [NBO with ADF](adfnbo.html)
      * [Numerical gradients](numgrad.html)
      * [Numerical Hessian](numhess.html)
      * [Global Minimum Search](global_minimum.html)
      * [Vibronic Density of States using the AH-FC method](pyAHFCDOS.html)
      * [Vibronic Density of States with ADF](fcf_dos.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * Examples

# Examples¶

In this chapter we present example PLAMS scripts covering various applications, from very simple tasks (like running the same calculation for multiple molecules) to more advanced dynamic workflows.

The example scripts use computational engines from the Amsterdam Modeling Suite, and you will need a license to run them. Contact [license@scm.com](mailto:license%40scm.com) for further questions.

In order to run the examples, the `AMSBIN` environment variable should be properly set. You can test this by typing `$AMSBIN/plams -h` in a terminal: this should print PLAMS’ help message. If this is not the case (e.g. you get ‘No such file or directory’), you need to set up the environmental variable `$AMSBIN` (see the [Linux Quickstart guide](../../Installation/Linux_Quickstart_Guide.html) for details).

## Getting Started¶

  * [Geometry optimization of water](WaterOptimization.html)
    * [Initial imports](WaterOptimization.html#initial-imports)
    * [Initial structure](WaterOptimization.html#initial-structure)
    * [Calculation settings](WaterOptimization.html#calculation-settings)
    * [Create an AMSJob](WaterOptimization.html#create-an-amsjob)
    * [Run the job](WaterOptimization.html#run-the-job)
    * [Main results files: ams.rkf and dftb.rkf](WaterOptimization.html#main-results-files-ams-rkf-and-dftb-rkf)
    * [Optimized coordinates](WaterOptimization.html#optimized-coordinates)
    * [Optimized bond lengths and angle](WaterOptimization.html#optimized-bond-lengths-and-angle)
    * [Calculation timing](WaterOptimization.html#calculation-timing)
    * [Energy](WaterOptimization.html#energy)
    * [Vibrational frequencies](WaterOptimization.html#vibrational-frequencies)
    * [Dipole moment](WaterOptimization.html#dipole-moment)
    * [HOMO, LUMO, and HOMO-LUMO gap](WaterOptimization.html#homo-lumo-and-homo-lumo-gap)
    * [Read results directly from binary .rkf files](WaterOptimization.html#read-results-directly-from-binary-rkf-files)
    * [Finish PLAMS](WaterOptimization.html#finish-plams)
  * [AMS Settings: Chemical System (Molecule)](Settings/AMSSettingsSystem.html)
    * [Initial imports](Settings/AMSSettingsSystem.html#initial-imports)
    * [Elements, coordinates, lattice vectors, and charge](Settings/AMSSettingsSystem.html#elements-coordinates-lattice-vectors-and-charge)
      * [Manual molecule definition](Settings/AMSSettingsSystem.html#manual-molecule-definition)
      * [Lattice vectors: 1D-periodic](Settings/AMSSettingsSystem.html#lattice-vectors-1d-periodic)
      * [Lattice vectors: 2D-periodic](Settings/AMSSettingsSystem.html#lattice-vectors-2d-periodic)
      * [Lattice vectors: 3D-periodic](Settings/AMSSettingsSystem.html#lattice-vectors-3d-periodic)
      * [Delete lattice vectors](Settings/AMSSettingsSystem.html#delete-lattice-vectors)
      * [Charge](Settings/AMSSettingsSystem.html#charge)
    * [Atomic properties: masses, regions, force field types …](Settings/AMSSettingsSystem.html#atomic-properties-masses-regions-force-field-types)
      * [Isotopes (atomic masses)](Settings/AMSSettingsSystem.html#isotopes-atomic-masses)
      * [Regions](Settings/AMSSettingsSystem.html#regions)
      * [Force field types](Settings/AMSSettingsSystem.html#force-field-types)
      * [Delete all atom-specific options](Settings/AMSSettingsSystem.html#delete-all-atom-specific-options)
    * [Bonds](Settings/AMSSettingsSystem.html#bonds)
    * [Multiple systems](Settings/AMSSettingsSystem.html#multiple-systems)
    * [Complete Python code](Settings/AMSSettingsSystem.html#complete-python-code)
  * [Helium dimer dissociation curve](He2DissociationCurve.html)
  * [Many jobs in parallel](ManyJobsInParallel.html)

## Molecule analysis¶

  * [Extract frames from ams.rkf trajectory](MoleculesFromRKFTrajectory.html)
  * [Table molecule counts and bond count from reactive MD ams.rkf](MoleculesTable.html)
  * [Molecule substitution: Attach ligands to substrates](MoleculeSubstitution/MoleculeSubstitutionExample.html)
    * [Initial imports](MoleculeSubstitution/MoleculeSubstitutionExample.html#initial-imports)
    * [Helper class and function](MoleculeSubstitution/MoleculeSubstitutionExample.html#helper-class-and-function)
    * [Generate substrate molecule](MoleculeSubstitution/MoleculeSubstitutionExample.html#generate-substrate-molecule)
    * [Find out which bond to cleave](MoleculeSubstitution/MoleculeSubstitutionExample.html#find-out-which-bond-to-cleave)
    * [Define ligands](MoleculeSubstitution/MoleculeSubstitutionExample.html#define-ligands)
    * [Generate substituted molecules](MoleculeSubstitution/MoleculeSubstitutionExample.html#generate-substituted-molecules)
    * [Plot 3D structures with PLAMS / ASE](MoleculeSubstitution/MoleculeSubstitutionExample.html#plot-3d-structures-with-plams-ase)
    * [Plot 2D Lewis structures with RDKit](MoleculeSubstitution/MoleculeSubstitutionExample.html#plot-2d-lewis-structures-with-rdkit)
    * [Complete Python code](MoleculeSubstitution/MoleculeSubstitutionExample.html#complete-python-code)
  * [Convert to ams.rkf trajectory with bond guessing](ConvertToAMSRKFTrajectory.html)

## Benchmarks¶

  * [Benchmark accuracy of basis sets](BasisSetBenchmark.html)
  * [Reaction energies with many different engines](ReactionEnergyBenchmark.html)

## Workflows¶

  * [Reduction and oxidation potentials](RedoxPotential.html)
  * [Workflow: filtering molecules based on excitation energies](ExcitationsWorkflow.html)
  * [AMS transition state workflow](AMSTSWorkflow/AMSTSWorkflow.html)
  * [Charge transfer integrals with ADF](ChargeTransferIntegralsADF.html)
  * [Tuning the range separation](gammascan.html)
  * [Conformers Generation](ConformersGeneration/ConformersGeneration.html)

## COSMO-RS and property prediction¶

For more examples, see the [COSMO-RS documentation](../../COSMO-RS/Advanced_scripting.html).

  * [Property Prediction](PropertyPrediction/PropertyPrediction.html)
    * [Initial imports](PropertyPrediction/PropertyPrediction.html#initial-imports)
    * [Property prediction from SMILES (ethyl acetate)](PropertyPrediction/PropertyPrediction.html#property-prediction-from-smiles-ethyl-acetate)
      * [Temperature-independent properties](PropertyPrediction/PropertyPrediction.html#temperature-independent-properties)
      * [Temperature-dependent properties (vapor pressure)](PropertyPrediction/PropertyPrediction.html#temperature-dependent-properties-vapor-pressure)
    * [Create .csv for multiple compounds](PropertyPrediction/PropertyPrediction.html#create-csv-for-multiple-compounds)
      * [Bar chart for multiple compounds](PropertyPrediction/PropertyPrediction.html#bar-chart-for-multiple-compounds)
    * [Complete Python code](PropertyPrediction/PropertyPrediction.html#complete-python-code)
  * [ADF and COSMO-RS workflow](ams_crs.html)

## Packmol and AMS-ASE interfaces¶

  * [Packmol example](PackMolExample/PackMolExample.html)
    * [Initial imports](PackMolExample/PackMolExample.html#initial-imports)
    * [Helper functions](PackMolExample/PackMolExample.html#helper-functions)
    * [Liquid water (fluid with 1 component)](PackMolExample/PackMolExample.html#liquid-water-fluid-with-1-component)
    * [Water-acetonitrile mixture (fluid with 2 or more components)](PackMolExample/PackMolExample.html#water-acetonitrile-mixture-fluid-with-2-or-more-components)
    * [Solid-liquid or solid-gas interfaces](PackMolExample/PackMolExample.html#solid-liquid-or-solid-gas-interfaces)
    * [Microsolvation](PackMolExample/PackMolExample.html#microsolvation)
    * [Bonds, atom properties (force field types, regions, …)](PackMolExample/PackMolExample.html#bonds-atom-properties-force-field-types-regions)
    * [Complete Python code](PackMolExample/PackMolExample.html#complete-python-code)
  * [Engine ASE: AMS geometry optimizer with forces from any ASE calculator](CustomASECalculator.html)
  * [AMSCalculator: ASE geometry optimizer with AMS forces](AMSCalculator/ASECalculator.html)
    * [Initial imports](AMSCalculator/ASECalculator.html#initial-imports)
    * [Construct an initial system](AMSCalculator/ASECalculator.html#construct-an-initial-system)
    * [Set the AMS settings](AMSCalculator/ASECalculator.html#set-the-ams-settings)
    * [Run the ASE optimizer](AMSCalculator/ASECalculator.html#run-the-ase-optimizer)
    * [Finish PLAMS](AMSCalculator/ASECalculator.html#finish-plams)
    * [Complete Python code](AMSCalculator/ASECalculator.html#complete-python-code)
  * [AMSCalculator: Access results files & Charged systems](AMSCalculator/ChargedAMSCalculator.html)
    * [Initial imports](AMSCalculator/ChargedAMSCalculator.html#initial-imports)
    * [Example 1: Total system charge](AMSCalculator/ChargedAMSCalculator.html#example-1-total-system-charge)
      * [Create the charged molecule (ion)](AMSCalculator/ChargedAMSCalculator.html#create-the-charged-molecule-ion)
      * [Set the AMS settings](AMSCalculator/ChargedAMSCalculator.html#set-the-ams-settings)
      * [Run AMS through the ASE Calculator](AMSCalculator/ChargedAMSCalculator.html#run-ams-through-the-ase-calculator)
      * [Access the input file](AMSCalculator/ChargedAMSCalculator.html#access-the-input-file)
      * [Access the binary .rkf results files and use PLAMS AMSResults methods](AMSCalculator/ChargedAMSCalculator.html#access-the-binary-rkf-results-files-and-use-plams-amsresults-methods)
    * [Example 2: Define atomic charges](AMSCalculator/ChargedAMSCalculator.html#example-2-define-atomic-charges)
      * [Construct a charged ion with atomic charges](AMSCalculator/ChargedAMSCalculator.html#construct-a-charged-ion-with-atomic-charges)
      * [Run AMS](AMSCalculator/ChargedAMSCalculator.html#run-ams)
    * [Example 3: Set the charge in the AMS System block](AMSCalculator/ChargedAMSCalculator.html#example-3-set-the-charge-in-the-ams-system-block)
      * [Set the charge in the AMS System block](AMSCalculator/ChargedAMSCalculator.html#set-the-charge-in-the-ams-system-block)
    * [Finish PLAMS](AMSCalculator/ChargedAMSCalculator.html#finish-plams)
    * [Complete Python code](AMSCalculator/ChargedAMSCalculator.html#complete-python-code)
  * [i-PI path integral MD with AMS](i-PI-AMS.html)
  * [Sella transition state search with AMS](SellaTransitionStateSearch.html)

## ParAMS and pyZacros¶

See the [ParAMS](../../params/index.html) and [pyZacros](../../pyzacros/index.html) documentations.

## Other AMS calculations¶

  * [BAND: NiO with DFT+U](BAND_NiO_HubbardU.html)
  * [Band structure](BandStructure/BandStructure.html)
    * [Initial imports](BandStructure/BandStructure.html#initial-imports)
    * [Metal band structure relative to Fermi energy](BandStructure/BandStructure.html#metal-band-structure-relative-to-fermi-energy)
    * [Semiconductor band structure relative to VBM](BandStructure/BandStructure.html#semiconductor-band-structure-relative-to-vbm)
    * [Spin-up and spin-down band structures](BandStructure/BandStructure.html#spin-up-and-spin-down-band-structures)
    * [Complete Python code](BandStructure/BandStructure.html#complete-python-code)
  * [AMS biased MD / PLUMED](AMSPlumedMD/AMSPlumedMD.html)
    * [Initial imports](AMSPlumedMD/AMSPlumedMD.html#initial-imports)
    * [Initial system](AMSPlumedMD/AMSPlumedMD.html#initial-system)
    * [Calculation settings](AMSPlumedMD/AMSPlumedMD.html#calculation-settings)
    * [Run the job](AMSPlumedMD/AMSPlumedMD.html#run-the-job)
    * [Analyze the trajectory](AMSPlumedMD/AMSPlumedMD.html#analyze-the-trajectory)
    * [A transition state search](AMSPlumedMD/AMSPlumedMD.html#a-transition-state-search)
    * [Complete Python code](AMSPlumedMD/AMSPlumedMD.html#complete-python-code)
  * [Quantum ESPRESSO as an AMS engine: Antiferromagnetic FeO](QE_AMS_AFM_HubbardU.html)
  * [Basic molecular dynamics analysis](BasicMDPostanalysis.html)
  * [Hybrid engine: Use lowest energy](UseLowestEnergy.html)
  * [Universal Potential: M3GNet-UP-2022](M3GNet.html)

## Pymatgen¶

  * [X-Ray Diffraction (XRD)](XRD/XRD.html)
    * [Initial imports](XRD/XRD.html#initial-imports)
    * [Create ASE atoms object for BaTiO3](XRD/XRD.html#create-ase-atoms-object-for-batio3)
    * [Save ASE Atoms to .cif format](XRD/XRD.html#save-ase-atoms-to-cif-format)
    * [Load .cif in pymatgen and calculate XRD](XRD/XRD.html#load-cif-in-pymatgen-and-calculate-xrd)
    * [Complete Python code](XRD/XRD.html#complete-python-code)

## Pre-made recipes¶

The examples presented in here are simple job types built using basic PLAMS elements. They are shipped with PLAMS in the `recipes` subpackage and can be directly used in your scripts. In other words, the code presented there is already included in PLAMS and (unlike examples from two other sections) does not need to be copied to your script. The source code of `recipes` modules is presented here to demonstrate how easy it is to build on top of existing PLAMS elements and create your own fully customized job types.

  * [ADF: Task COSMO-RS Compound](ADFCOSMORSCompound.html)
  * [AMS Molecular Dynamics PLAMS jobs](MDJobs.html)
    * [AMSMDJob API](MDJobs.html#amsmdjob-api)
    * [AMSNVEJob API](MDJobs.html#amsnvejob-api)
    * [AMSNVTJob API](MDJobs.html#amsnvtjob-api)
    * [AMSNPTJob API](MDJobs.html#amsnptjob-api)
    * [AMSNVESpawnerJob API](MDJobs.html#amsnvespawnerjob-api)
    * [AMSMDScanDensityJob API](MDJobs.html#amsmdscandensityjob-api)
    * [AMSRDFJob API](MDJobs.html#amsrdfjob-api)
    * [AMSMSDJob API](MDJobs.html#amsmsdjob-api)
    * [AMSVACFJob API](MDJobs.html#amsvacfjob-api)
  * [ADF fragment job](adffragment.html)
  * [Reorganization Energy](ReorganizationEnergy.html)
  * [NBO with ADF](adfnbo.html)
  * [Numerical gradients](numgrad.html)
  * [Numerical Hessian](numhess.html)
  * [Global Minimum Search](global_minimum.html)
  * [Vibronic Density of States using the AH-FC method](pyAHFCDOS.html)
  * [Vibronic Density of States with ADF](fcf_dos.html)

[Next ](WaterOptimization.html "Geometry optimization of water") [ Previous](../interfaces/vasp.html "VASP")

* * *

  * ### Application Areas

    * [Batteries & PVs](https://www.scm.com/applications/batteries/)
    * [Bonding Analysis](https://www.scm.com/applications/chemical-bonding-analysis/)
    * [Catalysis](https://www.scm.com/applications/catalysis/)
    * [Heavy Elements](https://www.scm.com/applications/heavy-elements/)
    * [Inorganic Chemistry](https://www.scm.com/applications/inorganic-chemistry/)
    * [Life Sciences](https://www.scm.com/applications/pharma/)
    * [Materials Science](https://www.scm.com/applications/materials-science/)
    * [Nanotechnology](https://www.scm.com/applications/nanotechnology/)
    * [Oil and Gas](https://www.scm.com/applications/oil-and-gas/)
    * [Organic Electronics](https://www.scm.com/applications/organic-electronics/)
    * [Polymers](https://www.scm.com/applications/polymers/)
    * [Spectroscopy](https://www.scm.com/applications/spectroscopy/)
    * [Supercomputer / HPC](https://www.scm.com/applications/a-computing-center/)
    * [Teaching Computational Chemistry with AMS](https://www.scm.com/applications/teaching/)

  * ### Products

    * [AMS Driver](https://www.scm.com/product/ams/)
    * [ADF](https://www.scm.com/product/adf/)
    * [BAND](https://www.scm.com/product/band_periodicdft/)
    * [COSMO-RS](https://www.scm.com/product/cosmo-rs/)
    * [DFTB](https://www.scm.com/product/dftb/)
    * [GUI](https://www.scm.com/product/gui/)
    * [ML Potentials & FF](https://www.scm.com/product/machine-learning-potentials/)
    * [MOPAC](https://www.scm.com/product/mopac/)
    * [ParAMS](https://www.scm.com/product/params/)
    * [PLAMS](https://www.scm.com/product/plams/)
    * [Quantum ESPRESSO](https://www.scm.com/product/quantum-espresso/)
    * [ReaxFF](https://www.scm.com/product/reaxff/)
    * [Workflows](https://www.scm.com/product/advanced-workflows/)

  * ### Support

    * [Brochure](https://www.scm.com/amsterdam-modeling-suite/brochures/)
    * [Consulting & Contract Research](https://www.scm.com/amsterdam-modeling-suite/consulting/)
    * [Discussion List](https://www.scm.com/adf-discussion-list/)
    * [Documentation](https://www.scm.com/support/ams-tutorials-and-manuals/)
    * [Downloads](https://www.scm.com/support/downloads/)
    * [FAQs](https://www.scm.com/faq/)
    * [GUI Tutorials](https://www.scm.com/doc/Tutorials/GUI_overview/GUI_overview_tutorials.html)
    * [Installation](https://www.scm.com/support/ams-installation-videos/)
    * [Literature Highlights](https://www.scm.com/category/highlights/)
    * [Papers Citing ADF](https://www.scm.com/amsterdam-modeling-suite/research-papers-citing-adf/)
    * [Release Notes](https://www.scm.com/support/documentation-previous-versions/release-notes/)
    * [Support Overview](https://www.scm.com/support/)
    * [Teaching Materials](https://www.scm.com/support/background/amsterdam-modeling-suite-teaching-materials/)
    * [Videos](https://www.scm.com/amsterdam-modeling-suite/videos-tutorials-and-web-presentations/)
    * [Webinars](https://www.scm.com/about-us/news-agenda/web-presentations-by-adf-experts/)
    * [Workshops](https://www.scm.com/about-us/news-agenda/adf-hands-on-workshops/)

  * ### About Us

    * [Careers](https://www.scm.com/about-us/careers/)
    * [Collaborations](https://www.scm.com/about-us/collaborations/)
    * [Contact Us](https://www.scm.com/about-us/contact-us/)
    * [Contributors](https://www.scm.com/about-us/our-authors/)
    * [EU Projects](https://www.scm.com/about-us/eu-projects/)
    * [Events](https://www.scm.com/about-us/news-agenda/)
    * [Mission & Vision](https://www.scm.com/about-us/mission-vision/)
    * [News](https://www.scm.com/category/news/)
    * [Newsletters](https://www.scm.com/newsletters/)
    * [The SCM Team](https://www.scm.com/about-us/our-people/)

  * ### Pricing & Licensing

    * [License Terms](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/scm-license-terms/)
    * [Ordering](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/ordering-procedure/)
    * [Price Calculator](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/price-quote/calculate-your-price/)
    * [Price Quote](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/price-quote/)
    * [Pricing & Licensing](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/)
    * [Resellers](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/adf-resellers/)

  * [Copyright](https://www.scm.com/copyright/)
  * [Terms of Use](https://www.scm.com/terms-of-use/)
  * [Privacy Policy](https://www.scm.com/privacy-policy/)
