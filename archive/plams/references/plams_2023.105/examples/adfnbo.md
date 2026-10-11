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
      * NBO with ADF
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
  * NBO with ADF

# NBO with ADF¶

NBO 6.0 is a tool for Natural Bond order analysis that uses the results of an ADF calculation. More information about NBO can be found in the corresponding section of the [ADF manual](../../ADF/Input/Advanced_analysis.html#adfnbo-gennbo-nbo-analysis).

NBO analysis is performed based on a prior ADF calculation (with some special keywords) by using two separate binary executables: `adfnbo` and `gennbo6`. In this case no special job type is created for these binaries. Instead of that we extend the [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") class in such a way that calls of `adfnbo` and `gennbo6` are appended to the usual ADF runscript. We also make sure that all the required ADF keywords are present in the initial ADF input file. Input keywords for `adfnbo` are taken from `myjob.settings.adfnbo`. All this work happens in [`prerun()`](../components/jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun"). No specialized [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass is defined for `ADFNBOJob`.

The source code of the whole module:
[code] 
    from ..interfaces.adfsuite.ams import AMSJob
    from ..core.functions import log
    import os
    
    __all__ = ['ADFNBOJob']
    
    class ADFNBOJob(AMSJob):
    
        def prerun(self):
            s = self.settings.input.ADF
            s.fullfock = True
            s.aomat2file = True
            s.symmetry = 'NoSym'
            s.basis.core = 'None'
            if 'save' in s:
                if isinstance(s.save, str):
                    s.save += ' TAPE15'
                elif isinstance(s.save, list):
                    s.save.append('TAPE15')
                else:
                    log("WARNING: 'SAVE TAPE15' could not be added to the input settings of {}. Make sure (thisjob).settings.input.save is a string or a list.".format(self.name), 1)
            else:
                s.save = 'TAPE15'
    
            if isinstance(self.settings.adfnbo, list):
                adfnbo_input = self.settings.adfnbo
            else:
                adfnbo_input = ['write', 'spherical', 'fock']
                log('WARNING: (thisjob).settings.adfnbo should be a list. Using default settings: write, fock, spherical', 1)
    
            self.settings.runscript.post = 'cp "'+os.path.join(self.path,'adf.rkf')+'" TAPE21\n' '$AMSBIN/adfnbo <<eor\n' + '\n'.join(adfnbo_input) + '\neor\n\n$AMSBIN/gennbo6 FILE47\n'
    
[/code]

An example usage:
[code] 
    mol = Molecule('methane.xyz')
    
    s = Settings()
    s.input.AMS.Task = 'SinglePoint'
    s.input.ADF.basis.type = 'DZP'
    s.input.ADF.xc.lda = 'SCF VWN'
    s.input.ADF.relativity.level = 'scalar'
    s.adfnbo = ['write', 'spherical', 'fock']
    
    j = ADFNBOJob(molecule=mol, settings=s)
    r = j.run()
    
    lines = r.get_output_chunk(begin='NATURAL BOND ORBITALS (Summary):', end='Charge unit', inc_begin=True, inc_end=True)
    for line in lines: print(line)
    
[/code]

[Next ](numgrad.html "Numerical gradients") [ Previous](ReorganizationEnergy.html "Reorganization Energy")

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
