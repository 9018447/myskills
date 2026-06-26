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
  * [Examples](examples.html)
    * [Getting Started](examples.html#getting-started)
    * [Molecule analysis](examples.html#molecule-analysis)
    * [Benchmarks](examples.html#benchmarks)
    * [Workflows](examples.html#workflows)
      * [Reduction and oxidation potentials](RedoxPotential.html)
      * Workflow: filtering molecules based on excitation energies
      * [AMS transition state workflow](AMSTSWorkflow/AMSTSWorkflow.html)
      * [Charge transfer integrals with ADF](ChargeTransferIntegralsADF.html)
      * [Tuning the range separation](gammascan.html)
      * [Conformers Generation](ConformersGeneration/ConformersGeneration.html)
    * [COSMO-RS and property prediction](examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](examples.html#packmol-and-ams-ase-interfaces)
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Workflow: filtering molecules based on excitation energies

# Workflow: filtering molecules based on excitation energies¶

Identifying systems with certain physical properties out of a large database of molecules is a typical task that can be easily automatized. In this example we will show how this can be achieved with a simple PLAMS script.

**Introducing the case study**

In our toy study, we want to scan a database of structures, looking for all molecules that absorb light within a certain energy range. For example, between 2 and 4 eV.

A simple approach would be to calculate the excitation energies (and the corresponding oscillator strengths) using ADF’s [time-dependent DFT](../../ADF/Input/Excitation_energies.html) (TD-DFT) for all the molecules in out database of structures. Since TD-DFT is an expensive method, this procedure can be computationally demanding for large numbers of molecules.

A faster approach would be to pre-screen the large database of molecules by first using a less accurate but more efficient method (e.g. time-dependent [DFTB](../../DFTB/index.html) (TD-DFTB)) and then run the expensive TD-DFT calculations with ADF only for the systems exhibiting the most promising absorption energies in the faster-but-less-accurate calculations.

The basic workflow may look as follows:

**Step 1**

  * Optimize the structure of all molecules in the database with DFTB and calculate excitation energies and oscillator strengths with TD-DFTB

  * Select the molecules with electronic excitations of energies between 1 and 6 eV and non-zero oscillator strenght (since TD-DFTB is less accurate than TD-DFT, we opt for a larger energy range in this step). This should significantly reduce the number of molecules to be considered in the following steps.

**Step 2**

  * Optimize the structures of the promising molecules with ADF.

  * Compute the electronic excitations energies using ADF’s TD-DFT and select the molecules with excitations of energies between 2 and 4 eV (and non-zero oscillator strength).

Note: in this example we focus on the **scripting** aspects rather than studying **physical phenomena**. The computational methods used here might not be entirely appropriate to describe the physical properties of interest.
[code] 
    # Workflow with PLAMS
    
    # A couple of useful function for extracting results:
    
    @add_to_class(AMSResults)
    def get_excitations(results):
        """Returns excitation energies (in eV) and oscillator strenghts (in Debye)."""
        if results.job.ok():
            exci_energies_au = results.readrkf('Excitations SS A','excenergies',file='engine')
            oscillator_str_au = results.readrkf('Excitations SS A','oscillator strengths',file='engine')
            # The results are stored in atomic units. Convert them to more convenient units:
            exci_energies = Units.convert(exci_energies_au,'au','eV')
            oscillator_str = Units.convert(oscillator_str_au,'au','Debye')
            return exci_energies, oscillator_str
        else:
            return [],[]
    
    @add_to_class(AMSResults)
    def has_good_excitations(results, min_energy, max_energy, oscillator_str_threshold=1E-4):
        """Returns True if there is at least one excitation with non-vanishing oscillator strenght
           in the energy range [min_energy, max_energy]. Unit for min_energy and max energy: eV. """
        exci_energies, oscillator_str = results.get_excitations()
        for e,o in zip(exci_energies, oscillator_str):
            if min_energy < e < max_energy and o > oscillator_str_threshold:
                return True
        return False
    
    # Calculation settings:
    # =====================
    
    # Settings for geometry optimization with the AMS driver:
    go_sett = Settings()
    go_sett.input.ams.Task = 'GeometryOptimization'
    go_sett.input.ams.GeometryOptimization.Convergence.Gradients = 1.0e-4
    
    # Settings for single point calculation with the AMS driver
    sp_sett = Settings()
    sp_sett.input.ams.Task = 'SinglePoint'
    
    # Settings for the DFTB engine (including excitations)
    dftb_sett = Settings()
    dftb_sett.input.dftb.Model = 'SCC-DFTB'
    dftb_sett.input.dftb.ResourcesDir = 'QUASINANO2015'
    dftb_sett.input.dftb.Properties.Excitations.TDDFTB.calc = 'singlet'
    dftb_sett.input.dftb.Properties.Excitations.TDDFTB.lowest = 10
    dftb_sett.input.dftb.Occupation.Temperature = 5.0
    
    # Settings for the geometry optimization with the ADF engine
    adf_sett = Settings()
    adf_sett.input.adf.Basis.Type = 'DZP'
    adf_sett.input.adf.NumericalQuality = 'Basic'
    
    # Settings for the excitation calculation using the ADF engine
    adf_exci_sett = Settings()
    adf_exci_sett.input.adf.Basis.Type = 'TZP'
    adf_exci_sett.input.adf.XC.GGA = 'PBE'
    adf_exci_sett.input.adf.NumericalQuality = 'Basic'
    adf_exci_sett.input.adf.Symmetry = 'NoSym'
    adf_exci_sett.input.adf.Excitations.lowest = 10
    adf_exci_sett.input.adf.Excitations.OnlySing = ''
    
    # Import all xyz files in the folder 'molecules'
    
    molecules = read_molecules('molecules')
    
    print("Step 1: prescreening with DFTB")
    print("==============================")
    
    promising_molecules = {}
    
    for name, mol in molecules.items():
      dftb_job = AMSJob(name='DFTB_'+name, molecule=mol, settings=go_sett+dftb_sett)
      dftb_job.run()
    
      if dftb_job.results.has_good_excitations(1,6):
        promising_molecules[name] = dftb_job.results.get_main_molecule()
    
    print(f"Found {len(promising_molecules)} promising molecules with DFTB")
    
    print("Step 2: Optimization and excitations calculation with ADF")
    print("=========================================================")
    
    for name, mol in promising_molecules.items():
      adf_go_job = AMSJob(name='ADF_GO_'+name, molecule=mol, settings=go_sett+adf_sett)
      adf_go_job.run()
    
      optimized_mol = adf_go_job.results.get_main_molecule()
    
      adf_exci_job = AMSJob(name='ADF_exci_'+name, molecule=optimized_mol, 
                            settings=sp_sett+adf_exci_sett)
      adf_exci_job.run()
    
      if adf_exci_job.results.has_good_excitations(2,4):
        print(f"Molecule {name} has excitation(s) satysfying our criteria!")
        print(optimized_mol)
        exci_energies, oscillator_str = adf_exci_job.results.get_excitations()
        print("Excitation energy [eV], oscillator strength:")
        for e,o in zip(exci_energies, oscillator_str):
            print(f"{e:8.4f}, {o:8.4f}")
    
[/code]

Note

To execute this PLAMS script:

  * [`Download ExcitationsWorkflow.py`](../_downloads/bf9c5ac4e714d334462cfbf3a22034de/ExcitationsWorkflow.py)

  * [`Download molecules.tar`](../_downloads/598c221ad3510ae5b441588167f7cfa4/molecules.tar) and extract it

  * `$AMSBIN/plams ExcitationsWorkflow.py`

**Output**
[code] 
    [14:41:27] PLAMS working folder: D:\adfsrc\trunk64\rundir.plams.ExcitationsWorkflow\plams_workdir
    Step 1: prescreening with DFTB
    ==============================
    [14:41:27] JOB DFTB_AlF3 STARTED
    [14:41:27] JOB DFTB_AlF3 RUNNING
    [14:41:28] JOB DFTB_AlF3 FINISHED
    [14:41:28] JOB DFTB_AlF3 SUCCESSFUL
    [14:41:28] JOB DFTB_CSCl2 STARTED
    [14:41:28] JOB DFTB_CSCl2 RUNNING
    [14:41:30] JOB DFTB_CSCl2 FINISHED
    [14:41:30] JOB DFTB_CSCl2 SUCCESSFUL
    [14:41:30] JOB DFTB_H2O STARTED
    [14:41:30] JOB DFTB_H2O RUNNING
    [14:41:31] JOB DFTB_H2O FINISHED
    [14:41:31] JOB DFTB_H2O SUCCESSFUL
    [14:41:31] JOB DFTB_NH3 STARTED
    [14:41:31] JOB DFTB_NH3 RUNNING
    [14:41:35] JOB DFTB_NH3 FINISHED
    [14:41:35] Job DFTB_NH3 reported warnings. Please check the the output
    [14:41:35] JOB DFTB_NH3 SUCCESSFUL
    [14:41:35] JOB DFTB_S2Cl2 STARTED
    [14:41:35] JOB DFTB_S2Cl2 RUNNING
    [14:41:36] JOB DFTB_S2Cl2 FINISHED
    [14:41:36] JOB DFTB_S2Cl2 SUCCESSFUL
    Found 2 promising molecules with DFTB
    Step 2: Optimization and excitations calculation with ADF
    =========================================================
    [14:41:36] JOB ADF_GO_CSCl2 STARTED
    [14:41:36] JOB ADF_GO_CSCl2 RUNNING
    [14:41:45] JOB ADF_GO_CSCl2 FINISHED
    [14:41:45] JOB ADF_GO_CSCl2 SUCCESSFUL
    [14:41:45] JOB ADF_exci_CSCl2 STARTED
    [14:41:45] JOB ADF_exci_CSCl2 RUNNING
    [14:41:52] JOB ADF_exci_CSCl2 FINISHED
    [14:41:52] JOB ADF_exci_CSCl2 SUCCESSFUL
    [14:41:52] JOB ADF_GO_S2Cl2 STARTED
    [14:41:52] JOB ADF_GO_S2Cl2 RUNNING
    [14:42:02] JOB ADF_GO_S2Cl2 FINISHED
    [14:42:02] JOB ADF_GO_S2Cl2 SUCCESSFUL
    [14:42:02] JOB ADF_exci_S2Cl2 STARTED
    [14:42:02] JOB ADF_exci_S2Cl2 RUNNING
    [14:42:09] JOB ADF_exci_S2Cl2 FINISHED
    [14:42:09] JOB ADF_exci_S2Cl2 SUCCESSFUL
    Molecule S2Cl2 has excitation(s) satysfying our criteria!
      Atoms: 
        1         S     -0.658306     -0.316643      0.909151 
        2         S     -0.658306      0.316643     -0.909151 
        3        Cl      0.758306      0.752857      2.053018 
        4        Cl      0.758306     -0.752857     -2.053018 
    
    Excitation energy [eV], oscillator strength:
      3.4107,   0.0114
      3.5386,   0.0160
      3.5400,   0.0011
      3.9864,   0.1105
      4.3225,   0.0049
      4.3513,   0.2551
      4.7544,   0.0011
      4.9414,   0.0105
      5.3188,   0.0036
      5.3272,   0.0721
    [14:42:09] PLAMS run finished. Goodbye
    Test duration in seconds: 43
    
[/code]

[Next ](AMSTSWorkflow/AMSTSWorkflow.html "AMS transition state workflow") [ Previous](RedoxPotential.html "Reduction and oxidation potentials")

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
