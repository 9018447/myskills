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
      * [Geometry optimization of water](WaterOptimization.html)
      * [AMS Settings: Chemical System (Molecule)](Settings/AMSSettingsSystem.html)
      * Helium dimer dissociation curve
      * [Many jobs in parallel](ManyJobsInParallel.html)
    * [Molecule analysis](examples.html#molecule-analysis)
    * [Benchmarks](examples.html#benchmarks)
    * [Workflows](examples.html#workflows)
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
  * Helium dimer dissociation curve

# Helium dimer dissociation curve¶
[code] 
    import numpy as np
    
    # Calcualte bond energy of He dimers for a series of bond 
    # distances using ADF
    
    # type of atoms
    atom1 = 'He'
    atom2 = 'He'
    
    # interatomic distance values
    dmin = 2.2
    dmax = 4.2
    step = 0.2
    
    # create a list with interatomic distances
    distances = np.arange(dmin,dmax,step)
    
    # calculation parameters (single point, TZP/PBE+GrimmeD3)
    sett = Settings()
    sett.input.ams.task = 'SinglePoint'
    sett.input.adf.basis.type = 'TZP'
    sett.input.adf.xc.gga = 'PBE'
    sett.input.adf.xc.dispersion = 'Grimme3'
    
    energies = []
    for d in distances:
        mol = Molecule()
        mol.add_atom(Atom(symbol=atom1, coords=(0.0, 0.0, 0.0)))
        mol.add_atom(Atom(symbol=atom2, coords=(  d, 0.0, 0.0)))
        job = AMSJob(molecule=mol, settings=sett, name=f'dist_{d:.2f}')
        job.run()
        energies.append(job.results.get_energy(unit='kcal/mol'))
    
    # print
    print('== Results ==')
    print('d[A]    E[kcal/mol]')
    for d,e in zip(distances, energies):
        print(f'{d:.2f}    {e:.3f}')
    
[/code]

Note

To execute this PLAMS script:

  * [`Download He2DissociationCurve.py`](../_downloads/32e0bc39e253d66961d7d7179b67c7ff/He2DissociationCurve.py)

  * `$AMSBIN/plams He2DissociationCurve.py`

**Output**
[code] 
    [10:45:48] PLAMS working folder: scratch/rundir.plams.He2DissociationCurve/plams_workdir
    [10:45:48] JOB dist_2.20 STARTED
    [10:45:48] JOB dist_2.20 RUNNING
    [10:45:49] JOB dist_2.20 FINISHED
    [10:45:49] JOB dist_2.20 SUCCESSFUL
    ...
    [10:45:57] JOB dist_4.00 STARTED
    [10:45:57] JOB dist_4.00 RUNNING
    [10:45:58] JOB dist_4.00 FINISHED
    [10:45:58] JOB dist_4.00 SUCCESSFUL
    == Results ==
    d[A]    E[kcal/mol]
    2.20    0.230
    2.40    -0.054
    2.60    -0.127
    2.80    -0.122
    3.00    -0.094
    3.20    -0.066
    3.40    -0.045
    3.60    -0.030
    3.80    -0.020
    4.00    -0.013
    [10:45:58] PLAMS run finished. Goodbye
    Test duration in seconds: 10
    
[/code]

[Next ](ManyJobsInParallel.html "Many jobs in parallel") [ Previous](Settings/AMSSettingsSystem.html "AMS Settings: Chemical System \(Molecule\)")

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
