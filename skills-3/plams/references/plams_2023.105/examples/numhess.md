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
      * [Reorganization Energy](ReorganizationEnergy.html)
      * [NBO with ADF](adfnbo.html)
      * [Numerical gradients](numgrad.html)
      * Numerical Hessian
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
  * Numerical Hessian

# Numerical Hessian¶

This module implements a simple scheme for calculating a numerical Hessian matrix. We define a new job type `NumHessJob` by extending [`MultiJob`](../components/jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob"). The constructor (`__init__`) of this new job accepts several new arguments and simply stores them. These new arguments define the initial [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"), the type of job used for single point calculations (`jobtype`), the size and unit of displacement step and the way of extracting gradients from single point results.

Then the [`prerun()`](../components/jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method takes the given [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") and creates multiple copies of it, each one with one atom displaced along one axis. For each of these molecules an instance of single point job is created and stored in the `children` dictionary. Settings of `NumHessJob` are directly passed to children jobs, so creating a `NumHessJob` strongly resembles creating a regular single point job.

The dedicated [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass for `NumHessJob` takes care of extracting the Hessian from results of all single point jobs. The returned Hessian can optionally be mass weighted.

The source code of the whole module with both abovementioned classes:
[code] 
    from collections import OrderedDict
    from itertools import product
    import numpy as np
    
    from ..core.results import Results
    from ..core.basejob import MultiJob
    from ..tools.units import Units
    
    __all__ = ['NumHessJob', 'NumHessResults'] #names exported to the main namespace
    
    class NumHessResults(Results):
    
        def get_hessian(self, mass_weighted=False):
            j = self.job
            n = len(j.molecule)
            hessian = np.empty((3*n,3*n))
    
            for (atom,axis) in product(range(1,n+1), range(3)):
                v1 = np.array(j.gradient(j.children[(atom, axis, -1)].results))
                v2 = np.array(j.gradient(j.children[(atom, axis, 1)].results))
                hessian[3*(atom-1) + axis] = (v2 - v1)/(2 * Units.convert(j.step,'angstrom', 'bohr'))
    
            if mass_weighted:
                masses = [at.mass for at in j.molecule]
                weights = np.empty((n,n))
                for i,j in product(range(n), repeat=2):
                    weights[i,j] = masses[i] * masses[j]
                hessian /= np.kron(weights, np.ones((3,3)))
            return (hessian+hessian.T)/2
    
    class NumHessJob(MultiJob):
        """A class for calculating numerical hessian.
    
        The length and unit of the geometry displacement step can be adjusted.
        *gradient* should be a function that takes results of *jobtype* and
        returns energy gradient in hartree/bohr.
        """
        _result_type = NumHessResults
    
        def __init__(self, molecule, step=0.01, unit='angstrom', jobtype=None, gradient=None, **kwargs):
            MultiJob.__init__(self, children=OrderedDict(), **kwargs)
            self.molecule = molecule
            self.step = Units.convert(step, unit, 'angstrom')
            self.jobtype = jobtype   #who is going to calculate single points
            self.gradient = gradient   #function extracting gradients from children
    
        def prerun(self):
            for (atom,axis,step) in product(range(1,1+len(self.molecule)), range(3), [-1,1]):
                vec = [0,0,0]
                vec[axis] = self.step * step
                newmol = self.molecule.copy()
                newmol[atom].translate(vec)
                newname = '{}_{}_{}'.format(atom,axis,step)
                self.children[(atom,axis,step)] = self.jobtype(name=newname, molecule=newmol,
                                                               settings=self.settings)
    
[/code]

An example usage:
[code] 
    mol = Molecule('methanol.xyz')
    
    s = Settings()
    s.input.ams.task = 'SinglePoint'
    s.input.ams.Properties.Gradients = 'Yes'
    s.input.adf.basis.type = 'DZP'
    s.input.adf.symmetry = 'NOSYM'
    s.input.adf.xc.gga = 'PW91'
    s.runscript.nproc = 1
    
    j = NumHessJob(name='test', molecule=mol, settings=s, jobtype=AMSJob,
                   gradient = lambda x: x.get_gradients().reshape(-1))
    r = j.run(jobrunner=JobRunner(parallel=True, maxjobs=8))
    print(r.get_hessian(mass_weighted=True))
    
[/code]

[Next ](global_minimum.html "Global Minimum Search") [ Previous](numgrad.html "Numerical gradients")

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
