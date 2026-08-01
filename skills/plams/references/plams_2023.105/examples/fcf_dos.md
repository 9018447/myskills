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
      * [Numerical Hessian](numhess.html)
      * [Global Minimum Search](global_minimum.html)
      * [Vibronic Density of States using the AH-FC method](pyAHFCDOS.html)
      * Vibronic Density of States with ADF
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Vibronic Density of States with ADF

# Vibronic Density of States with ADF¶

This example uses ADF to model the density of states involved in the charge transfer between two systems using the AH-FC method.

**Example usage** : ([`fcf_dos.py`](../_downloads/f332f39daaf7498167c74860b4b07ff5/DOS_FCF.py))
[code] 
    import os, sys
    from scm.plams import *
    
    # This is a simplified PLAMS script to calculate the density of states (DOS)
    # for the transfer between two systems, in this case NO2 radical and NO2 anion
    # We start from pre-optimized geometries to save time, though normally the
    # geometry optimization should come first, then we calculate the frequencies
    # for both systems and finally the absorption and emission FCF spectra
    # and finally the DOS is calculated from the FCF spectra using the FCFDOS utility
    # implemented in PLAMS
    
    # Pre-optimized geometries
    geom_1 = 'no2_1.xyz'
    geom_2 = 'no2_2.xyz'
    
    def freq(mol, common, pdir):
        """Frequency calculation"""
        # Define settings
        settings = Settings()
        settings.update(common)
        settings.input.ams.Properties.NormalModes = 'Yes'
        settings.input.adf.title = 'Vibrational frequencies'
        # Run job
        frqjob = AMSJob(molecule=mol, settings=settings, name=pdir)
        results = frqjob.run()
        return results
    
    def fcf(job1, job2, spctype, pdir):
        """FCF Job"""
        setfcf = Settings()
        setfcf.input.spectrum.type = spctype
        setfcf.input.state1 = job1.rkfpath(file='adf')
        setfcf.input.state2 = job2.rkfpath(file='adf')
        fcfjob = FCFJob(inputjob1=job1.rkfpath(file='adf'), inputjob2=job2.rkfpath(file='adf'), settings=setfcf, name=pdir)
        results = fcfjob.run()
        return results
    
    def main():
        init()
        # Common settings
        settings = Settings()
        settings.input.adf.symmetry = 'NoSym'
        settings.input.adf.basis.type = 'DZP'
        settings.input.adf.basis.core = 'None'
        settings.input.adf.xc.lda = 'SCF VWN'
        settings.input.ams.Task = 'SinglePoint'
        #mol1 = Molecule(filename=geom_1)
        mol1 = Molecule()
        mol1.add_atom(Atom(atnum=7, coords=(0.0, 0.0, -0.01857566)))
        mol1.add_atom(Atom(atnum=8, coords=(0.0, 1.09915770,  -0.49171967 )))
        mol1.add_atom(Atom(atnum=8, coords=(0.0,-1.09915770,  -0.49171967 )))
        #mol2 = Molecule(filename=geom_2)
        mol2 = Molecule()
        mol2.add_atom(Atom(atnum=7, coords=(0.0, 0.0, 0.12041)))
        mol2.add_atom(Atom(atnum=8, coords=(0.0, 1.070642, -0.555172)))
        mol2.add_atom(Atom(atnum=8, coords=(0.0,-1.070642, -0.555172)))
        # Acceptor vibrational frequencies calculation
        set1 = Settings()
        set1.update(settings)
        set1.input.ams.system.charge = 0
        set1.input.adf.spinpolarization = 1
        set1.input.adf.unrestricted = 'Yes'
        frq1 = freq(mol1, set1, 'gsmol1')
        # Donor vibrational frequencies calculation
        set2 = Settings()
        set2.update(settings)
        set2.input.ams.system.charge = -1
        frq2 = freq(mol2, set2, 'gsmol2')
        # FCF jobs to calculate the vibronic spectra
        fcfabs = fcf(frq1, frq2, 'absorption', 'fcfabs')
        fcfemi = fcf(frq2, frq1, 'emission', 'fcfemi')
        # DOS calculation
        job = FCFDOS(fcfabs._kf.path, fcfabs._kf.path, 10000. , 10000.)
        dos = job.dos()
        print(f'The density of states is {dos:.5e}')
        return None
    
    main()
    
[/code]

[Next ](../cookbook/cookbook.html "Cookbook") [ Previous](pyAHFCDOS.html "Vibronic Density of States using the AH-FC method")

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
