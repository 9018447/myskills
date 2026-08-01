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
    * [COSMO-RS and property prediction](examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](examples.html#packmol-and-ams-ase-interfaces)
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
      * [ADF: Task COSMO-RS Compound](ADFCOSMORSCompound.html)
      * [AMS Molecular Dynamics PLAMS jobs](MDJobs.html)
      * [ADF fragment job](adffragment.html)
      * Reorganization Energy
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
  * [Examples](examples.html)/
  * Reorganization Energy

# Reorganization Energy¶

One of the ingredients for computing hopping rates in Marcus theory is the reorganization energy \\(\lambda\\), defined as

\\[ \begin{align}\begin{aligned}\lambda = & (E^\text{state B}_\text{at optimal geometry of state A} - E^\text{state A}_\text{at optimal geometry of state A}) +\\\& (E^\text{state A}_\text{at optimal geometry of state B} - E^\text{state B}_\text{at optimal geometry of state B})\end{aligned}\end{align} \\]

where states A and B are two electronic configurations, e.g. neutral and anion (**see the example usage below**).

In this recipe we build a job class `ReorganizationEnergyJob` by extending [`MultiJob`](../components/jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob"). Our job will perform four [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") calcualtions: two geometry optimizations for states A anb B, followed by two single point calculations (state A at the optimal geometry of state B and state B at the optimal geometry of state A).

In `ReorganizationEnergyResults`, the reorganization energy is computed by fetching and combining the results from the childern jobs.
[code] 
    from collections import OrderedDict
    from ..core.functions import add_to_instance
    from ..core.basejob import MultiJob
    from ..core.results import Results
    from ..core.settings import Settings
    from ..mol.molecule import Molecule
    from ..interfaces.adfsuite.ams import AMSJob
    
    __all__ = ['ReorganizationEnergyJob', 'ReorganizationEnergyResults']
    
    # using this function to pass a molecule inside a MultiJob ensures proper parallel execution
    def pass_molecule(source, target):
        @add_to_instance(target)
        def prerun(self):
            self.molecule = source.results.get_main_molecule()
    
    class ReorganizationEnergyResults(Results):
        """Results class for reorganization energy.
        """
        def reorganization_energy(self, unit='au'):
            energies = self.get_all_energies(unit)
    
            reorganization_energy = (energies['state B geo A'] - energies['state A geo A'] + 
                                     energies['state A geo B'] - energies['state B geo B'])
            return reorganization_energy
    
        def get_all_energies(self, unit='au'):
            energies = {}
            energies['state A geo A'] = self.job.children['go_A'].results.get_energy(unit=unit)
            energies['state B geo B'] = self.job.children['go_B'].results.get_energy(unit=unit)
            energies['state A geo B'] = self.job.children['sp_A_for_geo_B'].results.get_energy(unit=unit)
            energies['state B geo A'] = self.job.children['sp_B_for_geo_A'].results.get_energy(unit=unit)
    
            return energies
    
    class ReorganizationEnergyJob(MultiJob):
        """A class for calculating the reorganization energy using AMS. 
        Given two states, A and B, the reorganization energy is defined as follows: 
    
        reorganization energy = 
        E(state B at optimal geometry for state A) - 
        E(state A at optimal geometry for state A) + 
        E(state A at optimal geometry for state B) - 
        E(state B at optimal geometry for state B)
        
        This job will run two geometry optimizations and two single point calculations.
        """
    
        _result_type = ReorganizationEnergyResults
    
        def __init__(self, molecule, common_settings, settings_state_A, settings_state_B, **kwargs):
            """
            molecule: the molecule 
            common_settings: a setting object for an AMSJob containing the shared settings for all the calculations
            settings_state_A: Setting object for an AMSJob containing exclusivelt the options defining the state A (e.g. charge and spin)
            settings_state_B: Setting object for an AMSJob containing exclusivelt the options defining the state B (e.g. charge and spin)
            kwargs: other options to be passed to the MultiJob constructor
            """
            MultiJob.__init__(self, children=OrderedDict(), **kwargs)
    
            go_settings = common_settings.copy()
            go_settings.input.ams.task = 'GeometryOptimization'
    
            sp_settings = common_settings.copy()
            sp_settings.input.ams.task = 'SinglePoint'
    
            # copy the settings so that we wont modify the ones provided as input by the user
            settings_state_A = settings_state_A.copy()
            settings_state_B = settings_state_B.copy()
            # In case the charge key is not specified, excplicitely set the value to 0.
            # This is to prevent the charge in molecule.properties.charge (set by get_main_molecule())
            # to be used in case of neutral systems
            for s in [settings_state_A, settings_state_B]:
                if not 'charge' in s.input.ams.system:
                    s.input.ams.system.charge = 0
    
            self.children['go_A'] = AMSJob(molecule=molecule, settings=go_settings+settings_state_A, name='go_A')
            self.children['go_B'] = AMSJob(molecule=molecule, settings=go_settings+settings_state_B, name='go_B')
            self.children['sp_A_for_geo_B'] = AMSJob(settings=sp_settings+settings_state_A, name='sp_A_geo_B')
            self.children['sp_B_for_geo_A'] = AMSJob(settings=sp_settings+settings_state_B, name='sp_B_geo_A')
            pass_molecule(self.children['go_A'], self.children['sp_B_for_geo_A'])
            pass_molecule(self.children['go_B'], self.children['sp_A_for_geo_B'])
    
[/code]

**Example usage:**
[code] 
    # Compute the neutral-anion reorganization energy of pyrrole 
    # using ADF as computational engine
    
    molecule = Molecule('pyrrole.xyz')
    
    # Generic settings of the calculation
    # (for quantitatively better results, use better settings)
    common_settings = Settings()
    common_settings.input.adf.Basis.Type = 'DZ'
    
    # Specific settings for the neutral calculation.
    # Nothing special needs to be done for the neutral calculation,
    # so we just use an empty settings.
    neutral_settings = Settings()
    
    # Specific settings for the anion calculation:
    anion_settings = Settings()
    anion_settings.input.ams.System.Charge = -1
    anion_settings.input.adf.Unrestricted = 'Yes'
    anion_settings.input.adf.SpinPolarization = 1
    
    # Create and run the ReorganizationEnergyJob:
    job = ReorganizationEnergyJob(molecule, common_settings, neutral_settings,
                                  anion_settings, name=molecule.properties.name)
    job.run()
    
    # Fetch and print the results:
    
    energy_unit = 'eV'
    energies = job.results.get_all_energies(energy_unit)
    reorganization_energy = job.results.reorganization_energy(energy_unit)
    
    print('')
    print("== Results ==")
    print('')
    print(f"Molecule: {molecule.properties.name}")
    print("State A: neutral")
    print("State B: anion")
    print('')
    print(f'Reorganization energy: {reorganization_energy:.6f} [{energy_unit}]')
    print('')
    print(f'|   State   | Optim Geo | Energy [{energy_unit}]')
    print(f'|     A     |     A     | {energies["state A geo A"]:.6f}')
    print(f'|     A     |     B     | {energies["state A geo B"]:.6f}')
    print(f'|     B     |     A     | {energies["state B geo A"]:.6f}')
    print(f'|     B     |     B     | {energies["state B geo B"]:.6f}')
    print('')
    
[/code]

Note

To execute this PLAMS script:

  * [`Download ReorganizationEnergy.py`](../_downloads/5c66ef9e38bdfc5a06edf386d936414d/ReorganizationEnergy.py)

  * [`Download pyrrole.xyz`](../_downloads/b5157a6f2f3ce07c2f4c44de8c03f588/pyrrole.xyz)

  * `$AMSBIN/plams ReorganizationEnergy.py`

**Output**
[code] 
    [22:39:48] PLAMS working folder: /home/robert/workspace/jobs/SCMSUITE-5940/regtest/test.plams/rundir.plams.ReorganizationEnergy/plams_workdir
    [22:39:48] JOB pyrrole STARTED
    [22:39:48] JOB pyrrole RUNNING
    [22:39:48] JOB pyrrole/go_A STARTED
    [22:39:48] JOB pyrrole/go_A RUNNING
    [22:39:54] JOB pyrrole/go_A FINISHED
    [22:39:54] JOB pyrrole/go_A SUCCESSFUL
    [22:39:54] JOB pyrrole/go_B STARTED
    [22:39:54] JOB pyrrole/go_B RUNNING
    [22:40:04] JOB pyrrole/go_B FINISHED
    [22:40:04] JOB pyrrole/go_B SUCCESSFUL
    [22:40:04] JOB pyrrole/sp_A_geo_B STARTED
    [22:40:04] JOB pyrrole/sp_A_geo_B RUNNING
    [22:40:06] JOB pyrrole/sp_A_geo_B FINISHED
    [22:40:06] JOB pyrrole/sp_A_geo_B SUCCESSFUL
    [22:40:06] JOB pyrrole/sp_B_geo_A STARTED
    [22:40:06] JOB pyrrole/sp_B_geo_A RUNNING
    [22:40:08] JOB pyrrole/sp_B_geo_A FINISHED
    [22:40:08] JOB pyrrole/sp_B_geo_A SUCCESSFUL
    [22:40:08] JOB pyrrole FINISHED
    [22:40:09] JOB pyrrole SUCCESSFUL
    
    == Results ==
    
    Molecule: pyrrole
    State A: neutral
    State B: anion
    
    Reorganization energy: 0.473683 [eV]
    
    |   State   | Optim Geo | Energy [eV]
    |     A     |     A     | -63.801633
    |     A     |     B     | -63.487503
    |     B     |     A     | -61.702138
    |     B     |     B     | -61.861691
    
    [22:40:09] PLAMS run finished. Goodbye
    Test duration in seconds: 21
    
[/code]

[Next ](adfnbo.html "NBO with ADF") [ Previous](adffragment.html "ADF fragment job")

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
