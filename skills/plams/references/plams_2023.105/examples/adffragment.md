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
      * ADF fragment job
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
  * [Examples](examples.html)/
  * ADF fragment job

# ADF fragment job¶

In this module a dedicated job type for ADF fragment analysis is defined. Such an analysis is performed on a molecular system divided into 2 fragments and consists of 3 separate ADF runs: one for each fragment and one for full system.

We define a new job type `ADFFragmentJob` by extending [`MultiJob`](../components/jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob"). The constructor (`__init__`) of this new job takes 2 more arguments (`fragment1` and `fragment2`) and one optional argument `full_settings` for additional input keywords that are used **only** in the full system calculation.

In the [`prerun()`](../components/jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method two fragment jobs and the full system job are created with the proper settings and molecules. They are then added to the `children` list.

The dedicated [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass for `ADFFragmentJob` does not provide too much additional functionality. It simply redirects the usual [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") methods to the results of the full system calculation.

The source code of the whole module with both abovementioned classes:
[code] 
    from ..core.basejob import MultiJob
    from ..core.results import Results
    from ..core.settings import Settings
    from ..mol.molecule import Molecule
    from ..interfaces.adfsuite.ams import AMSJob
    
    __all__ = ['ADFFragmentJob', 'ADFFragmentResults']
    
    class ADFFragmentResults(Results):
    
        def get_properties(self):
            return self.job.full.results.get_properties()
    
        def get_main_molecule(self):
            return self.job.full.results.get_main_molecule()
    
        def get_input_molecule(self):
            return self.job.full.results.get_input_molecule()
    
        def get_energy(self, unit='au'):
            return self.job.full.results.get_energy(unit)
    
        def get_dipole_vector(self, unit='au'):
            return self.job.full.results.get_dipole_vector(unit)
    
        def get_energy_decomposition(self):
            energy_section = self.job.full.results.read_rkf_section('Energy', file='adf')
            ret = {}
            for k in ['Electrostatic Energy', 'Kinetic Energy', 'Elstat Interaction', 'XC Energy']:
                ret[k] = energy_section[k]
            return ret
    
    class ADFFragmentJob(MultiJob):
        _result_type = ADFFragmentResults
    
        def __init__(self, fragment1=None, fragment2=None, full_settings=None, **kwargs):
            MultiJob.__init__(self, **kwargs)
            self.fragment1 = fragment1.copy() if isinstance(fragment1, Molecule) else fragment1
            self.fragment2 = fragment2.copy() if isinstance(fragment2, Molecule) else fragment2
            self.full_settings = full_settings or Settings()
    
        def prerun(self):
            self.f1 = AMSJob(name='frag1', molecule=self.fragment1, settings=self.settings)
            self.f2 = AMSJob(name='frag2', molecule=self.fragment2, settings=self.settings)
    
            for at in self.fragment1:
                at.properties.suffix = 'adf.f=subsystem1'
            for at in self.fragment2:
                at.properties.suffix = 'adf.f=subsystem2'
    
            self.full = AMSJob(name = 'full',
                molecule = self.fragment1 + self.fragment2,
                settings = self.settings + self.full_settings)
    
            self.full.settings.input.adf.fragments.subsystem1 = (self.f1, 'adf')
            self.full.settings.input.adf.fragments.subsystem2 = (self.f2, 'adf')
    
            self.children = [self.f1, self.f2, self.full]
    
[/code]

An example usage:
[code] 
    common = Settings() #common settings for all 3 jobs
    common.input.ams.Task= 'SinglePoint'
    common.input.adf.basis.type = 'DZP'
    common.input.adf.xc.gga = 'PBE'
    common.input.adf.symmetry = 'NOSYM'
    
    full = Settings() #additional settings for full system calculation
    full.input.adf.etsnocv  #empty block
    full.input.adf.print = 'etslowdin'
    
    mol1 = Molecule('ethene.xyz')
    mol2 = Molecule('butadiene.xyz')
    
    j = ADFFragmentJob(fragment1=mol1, fragment2=mol2,
                       settings=common, full_settings=full)
    r = j.run()
    
    print('Energy decomposition:')
    decom = r.get_energy_decomposition()
    for k in decom:
        print(k, decom[k])
    print(j.full.results.readrkf('NOCV', 'NOCV_eigenvalues_restricted', 'engine'))
    
[/code]

[Next ](ReorganizationEnergy.html "Reorganization Energy") [ Previous](MDJobs.html "AMS Molecular Dynamics PLAMS jobs")

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
