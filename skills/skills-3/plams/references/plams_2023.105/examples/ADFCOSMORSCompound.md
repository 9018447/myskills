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
      * ADF: Task COSMO-RS Compound
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
  * [Examples](examples.html)/
  * ADF: Task COSMO-RS Compound

# ADF: Task COSMO-RS Compound¶

The `ADFCOSMORSCompound` class mimics the “Task COSMO-RS Compound” in the AMS ADF graphical user interface.

It is used to generate .coskf files for use with COSMO-RS.

For an example, see [ADF and COSMO-RS workflow](ams_crs.html#ams-crs-workflow).
[code] 
    import os
    import shutil
    from scm.plams import Settings, JobError, AMSJob, CRSJob, Molecule, AMSResults, CRSResults, KFFile
    from collections import OrderedDict
    from ..core.functions import add_to_instance
    from ..core.basejob import MultiJob
    from ..core.results import Results
    from ..core.settings import Settings
    from ..mol.molecule import Molecule
    from ..mol.atom import Atom
    from ..interfaces.adfsuite.ams import AMSJob
    from ..tools.units import Units
    from ..interfaces.adfsuite.quickjobs import model_to_settings
    from typing import List
    import numpy as np
    
    __all__ = ['ADFCOSMORSCompoundJob', 'ADFCOSMORSCompoundResults']
    
    class ADFCOSMORSCompoundResults(Results):
        """Results class for ADFCOSMORSCompoundJob
        """
        def coskfpath(self):
            """
                Returns the path to the resulting .coskf
            """
    
            return os.path.join(self.job.path, self.job.name+".coskf")
    
        def get_main_molecule(self):
            """
                Returns the optimized molecule
            """
    
            return self.job.children['solv'].results.get_main_molecule()
    
        def get_input_molecule(self):
            """
                Returns the input molecule
            """
            for job in self.job.children.values():
                return job.results.get_input_molecule()
    
        def get_sigma_profile(self, subsection: str = 'profil'):
            """
                Returns the sigma profile of the molecule. For more details see `CRSResults.get_sigma_profile`.
            """
            return self.job.children['crs'].results.get_sigma_profile(subsection = subsection)
    
    class ADFCOSMORSCompoundJob(MultiJob):
        """A class for performing the equivalent of Task COSMO-RS Compound in the AMS GUI
        """
    
        _result_type = ADFCOSMORSCompoundResults
    
        def __init__(self, molecule:Molecule, preoptimization=None, singlepoint=False, settings=None, **kwargs):
            """
    
                Class for running the equivalent of "COSMO-RS Compound" in the AMS
                GUI. Note that these are ADF calculations, not COSMO-RS
                calculations!
    
                Initialize two or three jobs:
    
                (optional): Preoptimization with force field or semi-empirical method
                1. Gasphase optimization (BP86, DZP)
                2. Gasphase optimization (BP86, TZP, BeckeGrid Quality Good)
                3. Take optimized structure and run singlepoint with implicit solvation
    
                Access the result .coskf file with ``job.results.coskfpath()``.
                Note: this file will be called jobname.coskf, where jobname is the
                name of the ADFCOSMORSCompoundJob.
    
                molecule  : Molecule
                    The initial structure
    
                preoptimization : str or None
                    If None, do not preoptimize with a fast engine (then initial optimization is done with ADF). Otherwise, can be one of 'UFF', 'GAFF', 'GFNFF', 'GFN1-xTB', 'ANI-2x'. Note that you need valid licenses for ForceField or DFTB or MLPotential to use these preoptimizers.
    
                singlepoint : bool
                    Only run a singlepoint with solvation to generate the .coskf file on the given Molecule. (no geometry optimization)
    
                settings : settings
                    settings.runscript.nproc, settings.input.adf.custom_options. If 'adf' is in settings.input it should be provided without the solvation block.
    
                Usage:
    
                .. code-block:: python
                    
                    mol = from_smiles('O')
                    job = ADFCOSMORSCompoundJob(name='water', molecule=mol, preoptimization='UFF')
                    job.run()
                    print(job.results.coskfpath())
                    print(job.results.get_sigma_profile())
    
            """
            MultiJob.__init__(self, children=OrderedDict(), **kwargs)
            self.input_molecule = molecule
            self.settings = settings or Settings()
    
            if not singlepoint:
                if preoptimization:
                    preoptimization_s = Settings()
                    preoptimization_s.runscript.nproc = 1
                    preoptimization_s.input.ams.Task = 'GeometryOptimization'
                    preoptimization_s += model_to_settings(preoptimization)
                    preoptimization_job = AMSJob(settings=preoptimization_s, name='preoptimization', molecule=molecule)
                    self.children['preoptimization'] = preoptimization_job
    
                gas_s = Settings()
                gas_s.input.ams.Task = 'GeometryOptimization'
                gas_s += self.adf_settings(solvation=False, settings=self.settings)
                gas_job = AMSJob(settings=gas_s, name='gas')
    
                if preoptimization:
                    @add_to_instance(gas_job)
                    def prerun(self):
                        self.molecule = self.parent.children['preoptimization'].results.get_main_molecule()
                else:
                    gas_job.molecule = molecule
    
                self.children['gas'] = gas_job
    
            solv_s = Settings()
            solv_s.input.ams.Task = 'SinglePoint'
            solv_job = AMSJob(settings=solv_s, name='solv')
    
            if singlepoint:
                @add_to_instance(solv_job)
                def prerun(self):
                    self.molecule = self.parent.input_molecule
                    self.settings += self.parent.adf_settings(solvation=True, settings=self.parent.settings, elements=list(set(at.symbol for at in self.parent.input_molecule)))
            else:
                @add_to_instance(solv_job)
                def prerun(self):
                    gas_job.results.wait()
                    self.settings.input.ams.EngineRestart = "../gas/adf.rkf" 
                    self.settings.input.ams.LoadSystem.File = "../gas/ams.rkf"
                    self.settings += self.parent.adf_settings(solvation=True, settings=self.parent.settings, elements=list(set(at.symbol for at in self.parent.input_molecule)))
                    #self.settings.input.ams.EngineRestart = self.parent.children['gas'].results.rkfpath(file='adf') # this doesn't work with PLAMS restart since the file will refer to the .res directory (so the job is rerun needlessly)
                    #self.settings.input.ams.LoadSystem.File = self.parent.children['gas'].results.rkfpath(file='ams')
                    # cannot copy to gasphase-ams.rkf etc. because that conflicts with PLAMS restarts
                    #shutil.copyfile(gas_job.results.rkfpath(file='ams'), os.path.join(self.path, 'gasphase-ams.rkf'))
                    #shutil.copyfile(gas_job.results.rkfpath(file='adf'), os.path.join(self.path, 'gasphase-adf.rkf'))
    
            @add_to_instance(solv_job)
            def postrun(self):
                self.parent.convert_to_coskf(self.results.rkfpath(file='adf'), os.path.join(self.parent.path, self.parent.name+'.coskf'))
    
            self.children['solv'] = solv_job
    
            sigma_s = Settings()
            sigma_s.input.property._h = 'PURESIGMAPROFILE'
    
            compounds = [Settings()]
            sigma_s.input.compound = compounds
            crsjob = CRSJob(settings=sigma_s, name = 'sigma')
    
            @add_to_instance(crsjob)
            def prerun(self):
                self.parent.children['solv'].results.wait()
                self.settings.input.compound[0]._h = os.path.join(self.parent.path, self.parent.name+'.coskf')
    
            self.children['crs'] = crsjob
    
        @staticmethod
        def _get_radii() -> dict:
            """ Method to get the atomic radii from solvent.txt (for some elements the radii are instead the Klamt radii) """
            with open(os.path.expandvars('$AMSHOME/data/gui/solvent.txt'), 'r') as f:
                mod_allinger_radii = [float(x) for i,x in enumerate(f) if i > 0]
            radii = { PeriodicTable.get_symbol(i) : r for i,r in enumerate(mod_allinger_radii, 1) if i<= 118 }
            klamt_radii = {
                'H': 1.30,
                'C': 2.00,
                'N': 1.83,
                'O': 1.72,
                'F': 1.72,
                'Si': 2.48,
                'P': 2.13,
                'S': 2.16,
                'Cl': 2.05,
                'Br': 2.16,
                'I': 2.32
            }
            radii.update(klamt_radii)
    
            return radii
    
        @staticmethod
        def solvation_settings(elements:List[str]=None) -> Settings:
            sett = Settings()
    
            radii = {'H': 1.3, 'He': 1.275, 'Li': 2.125, 'Be': 1.858, 'B': 1.792, 'C': 2.0, 'N': 1.83, 'O': 1.72, 'F': 1.72, 'Ne': 1.333, 'Na': 2.25, 'Mg': 2.025, 'Al': 1.967, 'Si': 2.48, 'P': 2.13, 'S': 2.16, 'Cl': 2.05, 'Ar': 1.658, 'K': 2.575, 'Ca': 2.342, 'Sc': 2.175, 'Ti': 1.992, 'V': 1.908, 'Cr': 1.875, 'Mn': 1.867, 'Fe': 1.858, 'Co': 1.858, 'Ni': 1.85, 'Cu': 1.883, 'Zn': 1.908, 'Ga': 2.05, 'Ge': 2.033, 'As': 1.967, 'Se': 1.908, 'Br': 2.16, 'Kr': 1.792, 'Rb': 2.708, 'Sr': 2.5, 'Y': 2.258, 'Zr': 2.117, 'Nb': 2.025, 'Mo': 1.992, 'Tc': 1.967, 'Ru': 1.95, 'Rh': 1.95, 'Pd': 1.975, 'Ag': 2.025, 'Cd': 2.083, 'In': 2.2, 'Sn': 2.158, 'Sb': 2.1, 'Te': 2.033, 'I': 2.32, 'Xe': 1.9, 'Cs': 2.867, 'Ba': 2.558, 'La': 2.317, 'Ce': 2.283, 'Pr': 2.275, 'Nd': 2.275, 'Pm': 2.267, 'Sm': 2.258, 'Eu': 2.45, 'Gd': 2.258, 'Tb': 2.25, 'Dy': 2.242, 'Ho': 2.225, 'Er': 2.225, 'Tm': 2.225, 'Yb': 2.325, 'Lu': 2.208, 'Hf': 2.108, 'Ta': 2.025, 'W': 1.992, 'Re': 1.975, 'Os': 1.958, 'Ir': 1.967, 'Pt': 1.992, 'Au': 2.025, 'Hg': 2.108, 'Tl': 2.158, 'Pb': 2.283, 'Bi': 2.217, 'Po': 2.158, 'At': 2.092, 'Rn': 2.025, 'Fr': 3.033, 'Ra': 2.725, 'Ac': 2.567, 'Th': 2.283, 'Pa': 2.2, 'U': 2.1, 'Np': 2.1, 'Pu': 2.1, 'Am': 2.1, 'Cm': 2.1, 'Bk': 2.1, 'Cf': 2.1, 'Es': 2.1, 'Fm': 2.1, 'Md': 2.1, 'No': 2.1, 'Lr': 2.1, 'Rf': 2.1, 'Db': 2.1, 'Sg': 2.1, 'Bh': 2.1, 'Hs': 2.1, 'Mt': 2.1, 'Ds': 2.1, 'Rg': 2.1, 'Cn': 2.1, 'Nh': 2.1, 'Fl': 2.1, 'Mc': 2.1, 'Lv': 2.1, 'Ts': 2.1, 'Og': 2.1} # from _get_radii()
    
            if elements:
                radii = {k:radii[k] for k in sorted(elements)}
    
            sett.input.adf.solvation = {
                'surf': 'Delley',
                'solv': 'name=CRS cav0=0.0 cav1=0.0',
                'charged': 'method=Conj corr',
                'c-mat': 'Exact',
                'scf': 'Var All',
                'radii': radii, 
            }
            return sett
    
        @staticmethod
        def adf_settings(solvation:bool, settings=None, elements:List[str]=None) -> Settings:
            """
            Returns ADF settings with or without solvation
    
            If solvation == True, then also include the solvation block.
            """
            
            s = Settings()
            if settings:
                s = settings.copy()
            if 'basis' not in s.input.adf and 'xc' not in s.input.adf:
                s.input.adf.Basis.Type = 'TZP'
                s.input.adf.Basis.Core = 'Small'
                s.input.adf.XC.GGA = 'BP86'
                s.input.adf.Symmetry = 'NOSYM'
                s.input.adf.BeckeGrid.Quality = 'Good'
            if solvation:
                s += ADFCOSMORSCompoundJob.solvation_settings(elements=elements)
    
            return s
    
        @staticmethod
        def convert_to_coskf(rkf: str, coskf: str):
            """ rkf: absolute path to adf.rkf, coskf: path to write out the resulting .coskf file  """
            f = KFFile(rkf)
            cosmo = f.read_section("COSMO")
            coskf = KFFile(coskf)
            for k,v in cosmo.items():
                coskf.write("COSMO",k,v)
    
[/code]

[Next ](MDJobs.html "AMS Molecular Dynamics PLAMS jobs") [ Previous](XRD/XRD.html "X-Ray Diffraction \(XRD\)")

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
