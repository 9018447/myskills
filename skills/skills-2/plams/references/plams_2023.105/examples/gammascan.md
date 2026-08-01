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
      * [Workflow: filtering molecules based on excitation energies](ExcitationsWorkflow.html)
      * [AMS transition state workflow](AMSTSWorkflow/AMSTSWorkflow.html)
      * [Charge transfer integrals with ADF](ChargeTransferIntegralsADF.html)
      * Tuning the range separation
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
  * Tuning the range separation

# Tuning the range separation¶

In this example we optimize the value of _gamma_ parameter for long-range corrected XC functional (in our case: LCY-PBE) in ADF. Long-range corrected XC functionals can be used in ADF with XCfun (see [ADF manual](../../ADF/Input/Density_Functional.html#range-separated-hybrids)).

The optimal range separation parameter _gamma_ yields the HOMO energy equal to the ionization potential (IP). Given a molecular system, we simultaneously minimize the difference between HOMO and IP for that system (N) and its anion (A) (system with one more electron). We define the J function as:

\\[J = \sqrt{N^2+A^2}\\]

and find the value of _gamma_ (within a certain range) which minimizes J. See also [this article by Kronik and coworkers](https://doi.org/10.1063/1.4807325).

We first define a new job type `GammaJob` by extending [`MultiJob`](../components/jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob"). The goal of `GammaJob` is to calculate the J function for one fixed value of _gamma_ To do that we need to perform 3 different single point calculations: 1 for the given system (let’s call it S0), 1 for the system with one more electron (S-) and 1 for the system with one less electron (S+). S+ calculation is needed to find the ionization potential of S0.

The constructor (`__init__`) of `GammaJob` accepts several new arguments and simply stores them. These new arguments define: the value of _gamma_ , the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") together with its initial charge, and the values of spin for S-, S0 and S+ (as a tuple of length 3). Then the [`prerun()`](../components/jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method is used to create three children jobs with different values of total charge and spin multiplicity. A dedicated [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass features a simple method for extracting the value of J based on results on three children jobs.

We can then treat our newly defined `GammaJob` as a blackbox with simple interface: input _gamma_ -> run -> extract J. The next step is to create multiple instances of `GammaJob` for a range of different _gammas_. That task can be conveniently wrapped in a simple function `gamma_scan`.
[code] 
    class GammaResults(Results):
    
        @staticmethod
        def get_difference(job, jobplus):
            """Calculate the difference between HOMO and IP.
            *jobplus* should be the counterpart of *job* with one less electron."""
            homo = job.results.readrkf('Properties','HOMO', file='engine')
            IP = jobplus.results.get_energy() - job.results.get_energy()
            return IP + homo
    
        def get_J(self):
            N = GammaResults.get_difference(self.job.children[1], self.job.children[2])
            A = GammaResults.get_difference(self.job.children[0], self.job.children[1])
            return (N**2 + A**2)**0.5
    
    class GammaJob(MultiJob):
        _result_type = GammaResults
    
        def __init__(self, molecule, gamma, charge, spins, **kwargs):
            MultiJob.__init__(self, **kwargs)
            self.molecule = molecule
            self.charge = charge
            self.spins = spins
            self.gamma = gamma
    
        def prerun(self):
            charges = [self.charge-1, self.charge, self.charge+1]
            for charge, spin in zip(charges, self.spins):
                name = '{}_charge_{}'.format(self.name, charge)
                newjob = AMSJob(name=name, molecule=self.molecule, settings=self.settings)
                newjob.molecule.properties.charge = charge
                newjob.settings.input.adf.xc.rangesep = "gamma={:f}".format(self.gamma)
                if spin != 0:
                    newjob.settings.input.adf.unrestricted = True
                    newjob.settings.input.adf.SpinPolarization = spin
    
                self.children.append(newjob)
    
    def gamma_scan(gammas, settings, molecule, name='scan', charge=0, spins=(1,0,1)):
        """Calculate values of J function for given range of gammas.
    
        Arguments:
        gammas   - list of gamma values to calculate the J function for
        settings - Settings object for an ADF calculation
        molecule - Molecule object with the system of interest
        name     - base name of all the jobs
        charge   - base charge of the system of interest. The J function is going to be
                   calculated based on two systems: with charge, and charge-1
        spins    - values of spin polarization for jobs with, respectively, charge-1, 
                   charge and charge +1
    
        In other words, if charge=X and spins=(a,b,c) the three resulting jobs
        are going to have the following values for charge and spin:
    
        Charge=X-1  SpinPolarization=a
        Charge=X    SpinPolarization=b
        Charge=X+1  SpinPolarization=c
    
        Returns a list of pairs (gamma, J) of the same length as the parameter *gammas*
        """
        jobs = [GammaJob(molecule=molecule, settings=settings, gamma=g,
                charge=charge, spins=spins, name=name+'_gamma_'+str(g)) for g in gammas]
        results = [j.run() for j in jobs]
        js = [r.get_J() for r in results]
        return list(zip(gammas, js))
    
    # =============================================================
    # Now we simply use the gamma_scan function to find the optimal 
    # gamma value for a toy system (H2)
    # =============================================================
    
    import numpy as np
    import multiprocessing
    
    # Run as many jobs in parallel as there are cores:
    config.default_jobrunner = JobRunner(parallel=True, maxjobs=multiprocessing.cpu_count())
    
    # Settings of the ADF calculations
    # ================================
    
    s = Settings()
    s.input.ams.task = 'SinglePoint'
    s.input.adf.basis.type = 'DZP'
    s.input.adf.basis.core = 'None'
    s.input.adf.xc.gga = 'PBE'
    s.input.adf.xc.xcfun = True
    s.runscript.nproc = 1
    
    # The molecule (here we just use H2)
    # ==================================
    
    mol = Molecule()
    mol.add_atom(Atom(symbol='H', coords=(0,0,-0.3540)))
    mol.add_atom(Atom(symbol='H', coords=(0,0, 0.3540)))
    
    # The list of gamma values
    # ========================
    
    # Here we scan just a few values for gamma. 
    # In practice, you want to scan a wider range and smaller step.
    gammas = np.around(np.arange(1.2, 1.9, 0.2), decimals=3)
    
    results = gamma_scan(gammas, s, mol)
    
    print('== Results ==')
    print('gamma \t J')
    for g,j in results:
        print('{:.4f} \t {:.8f}'.format(g,j))
    print('Optimal gamma value: {:.4f}'.format(min(results,key=lambda x:x[1])[0]))
    
[/code]

Note

To execute this PLAMS script:

  * [`Download TuningRangeSeparation.py`](../_downloads/4fa808636da9efe8e37ab016c6c0ce1d/TuningRangeSeparation.py)

  * `$AMSBIN/plams TuningRangeSeparation.py`

**Output**
[code] 
    [17:24:51] JOB scan_gamma_1.2 STARTED
    [17:24:51] JOB scan_gamma_1.4 STARTED
    [17:24:51] JOB scan_gamma_1.6 STARTED
    ...
    [17:24:51] JOB scan_gamma_1.2 RUNNING
    [17:24:51] JOB scan_gamma_1.4 RUNNING
    ....
    [17:26:21] JOB scan_gamma_1.8 FINISHED
    [17:26:21] JOB scan_gamma_1.8 SUCCESSFUL
    == Results ==
    gamma 	 J
    1.2000 	 0.01138875
    1.4000 	 0.00755822
    1.6000 	 0.00858682
    1.8000 	 0.01111191
    Optimal gamma value: 1.4000
    [17:26:21] PLAMS run finished. Goodbye
    Test duration in seconds: 90
    
[/code]

[Next ](ConformersGeneration/ConformersGeneration.html "Conformers Generation") [ Previous](ChargeTransferIntegralsADF.html "Charge transfer integrals with ADF")

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
