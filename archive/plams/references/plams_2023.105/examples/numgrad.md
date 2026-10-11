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
      * Numerical gradients
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
  * Numerical gradients

# Numerical gradients¶

This module implements a simple numerical differentiation scheme with respect to molecular coordinates. We define a new job type `NumGradJob` by extending [`MultiJob`](../components/jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob"). The constructor (`__init__`) of this new job accepts several new arguments and simply stores them. These new arguments define the initial [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"), the type of job used for single point calculations (`jobtype`), the accuracy of the numerical differentiation scheme (`npoints`) and size and unit of displacement step.

Then the [`prerun()`](../components/jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method takes the given [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") and creates multiple copies of it, each one with one atom displaced along one axis. For each of these molecules an instance of single point job is created and stored in the `children` dictionary. Settings of `NumGradJob` are directly passed to children jobs, so creating a `NumGradJob` strongly resembles creating a regular single point job.

The dedicated [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass for `NumGradJob` takes care of extracting the gradient from the results of all single point jobs. Any function that takes results of a single point job and returns a single number can be used with the `get_gradient` method defined in `NumGradResults`

The source code of the whole module with both abovementioned classes:
[code] 
    from collections import OrderedDict
    from itertools import product
    
    from ..core.results import Results
    from ..core.basejob import MultiJob
    
    __all__ = ['NumGradJob', 'NumGradResults'] #names exported to the main namespace
    
    class NumGradResults(Results):
    
        def _get_gradient_component(self, atom, coord, extract):
            """Get gradient component for *atom* along *coord*.
    
            *atom* should be integer, *coord* a single character string with 'x', 'y' or 'z'.
            *extract* should be a function that takes results of a single point job and
            returns a single number.
            """
            energies = [extract(self.job.children[(atom,coord,i)].results) for i in self.job.steps]
            coeffs, denom = self.job._coeffs[self.job.npoints]
            return sum([c*e for c,e in zip(coeffs, energies)])/(denom * self.job.step)
    
        def get_gradient(self, extract):
            """Get the full gradient vector. Returns a list of length 3N,
            where N is the number of atoms in the calculated molecule.
    
            *extract* should be a function that takes results of a single point job and
            returns a single number.
            """
            return [self._get_gradient_component(atom, coord, extract)
                for atom,coord in product(range(1,1+len(self.job.molecule)), 'xyz')]
    
    class NumGradJob(MultiJob):
        """A class for calculating numerical gradients of energy
        (or some other single-valued property) with respect to
        cartesian displacements.
    
        The differentiation is done using the final difference method
        with 2, 4, 6 or 8 points. The length of the step can be adjusted.
        """
        _result_type = NumGradResults
    
        #finite difference coefficients for different number of points:
        _coeffs = {
            2: ([-1,1], 2),
            4: ([1,-8,8,-1], 12),
            6: ([-1,9,-75,75,-9,1], 60),
            8: ([3,-32,168,-672,672,-168,32,-3], 840),
        }
    
        def __init__(self, molecule, npoints=2, step=0.01, unit='angstrom', jobtype=None, **kwargs):
            #initialize parent class and store all additional constructor arguments
            MultiJob.__init__(self, children=OrderedDict(), **kwargs)
            self.molecule = molecule
            self.npoints = npoints
            self.step = step
            self.unit = unit
            self.jobtype = jobtype   #who is going to calculate single points
    
        def prerun(self):
            self.steps = list(range(-(self.npoints//2), 0)) + list(range(1, self.npoints//2+1))
    
            for (atom,axis,i) in product(range(1,1+len(self.molecule)), 'xyz', self.steps):
                v = (self.step * i if axis == 'x' else 0,
                     self.step * i if axis == 'y' else 0,
                     self.step * i if axis == 'z' else 0)
                newmol = self.molecule.copy()
                newmol[atom].translate(v, self.unit)
                newname = '{}_{}_{}'.format(atom,axis,i)
                #settings of NumGradJob are directly passed to children single point jobs
                self.children[(atom,axis,i)] = self.jobtype(name=newname, molecule=newmol,
                                                            settings=self.settings)
    
[/code]

An example usage:
[code] 
    config.default_jobrunner = JobRunner(parallel=True, maxjobs=8)
    
    mol = Molecule('methanol.xyz')
    
    s = Settings()
    s.input.AMS.Task = 'SinglePoint'
    s.input.ADF.basis.type = 'DZP'
    s.input.ADF.basis.core = 'None'
    s.input.ADF.basis.createoutput = 'No'
    s.input.ADF.symmetry = 'NOSYM'
    s.input.ADF.Relativity.Level = 'None'
    s.input.ADF.xc.gga = 'PW91'
    s.runscript.nproc = 1
    
    j = NumGradJob(name='numgrad', molecule=mol, settings=s, jobtype=AMSJob)
    r = j.run()
    r.wait()
    
    print('Energy gradient:')
    print(r.get_gradient(AMSResults.get_energy))
    print('Electrostatic energy gradient:')
    print(r.get_gradient(lambda x: x.readrkf('Energy', 'Electrostatic Energy', file='adf')))
    
[/code]

[Next ](numhess.html "Numerical Hessian") [ Previous](adfnbo.html "NBO with ADF")

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
