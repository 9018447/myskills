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
      * [Helium dimer dissociation curve](He2DissociationCurve.html)
      * Many jobs in parallel
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
  * Many jobs in parallel

# Many jobs in parallel¶
[code] 
    import multiprocessing
    
    # Run as many job simultaneously as there are cpu on the system:
    maxjobs = multiprocessing.cpu_count()
    print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))
    
    # Set the default jobrunner to be parallel:
    config.default_jobrunner = JobRunner(parallel=True, maxjobs=maxjobs)
    
    # Number of cores for each job:
    config.job.runscript.nproc = 1
    
    # Load all molecules in the folder 'molecules':
    molecules = read_molecules('molecules')
    
    settings = Settings()
    settings.input.ams.Task = 'GeometryOptimization'
    settings.input.dftb.Model = 'GFN1-xTB'
    
    results = []
    for name, molecule in sorted(molecules.items()):
        job = AMSJob(molecule=molecule, settings=settings, name=name)
        results.append(job.run())
    
    # Only print the results of the succesful caluclations:
    for result in [r for r in results if r.ok()]:
        print('Energy for {:<12}: {:>10.3f} kcal/mol'.format(result.name, result.get_energy(unit='kcal/mol')))
    
[/code]

Note

To execute this PLAMS script:

  * [`Download ManyJobsInParallel.py`](../_downloads/f3040904d52ef6767f2b79452da50ec9/ManyJobsInParallel.py)

  * [`Download molecules.tar`](../_downloads/2eeadbc5b7cc5b221849eafa7a2c4dbc/molecules.tar) and extract it

  * `$AMSBIN/plams ManyJobsInParallel.py`

**Output**
[code] 
    [09:42:34] PLAMS working folder: /scratch/rundir.plams.ManyJobsInParallel/plams_workdir
    Running up to 8 jobs in parallel simultaneously
    [09:42:34] JOB Acetic_acid STARTED
    [09:42:34] JOB Benzene STARTED
    [09:42:34] JOB Acetic_acid RUNNING
    [09:42:34] JOB Butane STARTED
    [09:42:34] JOB Ethane STARTED
    [09:42:34] JOB Benzene RUNNING
    ...
    ...
    [09:42:35] JOB Butane FINISHED
    [09:42:35] JOB Butane SUCCESSFUL
    [09:42:35] JOB Benzene FINISHED
    [09:42:35] JOB Benzene SUCCESSFUL
    Energy for Acetic_acid :  -9913.297 kcal/mol
    Energy for Benzene     : -12039.485 kcal/mol
    Energy for Butane      :  -8699.182 kcal/mol
    Energy for Ethane      :  -4686.355 kcal/mol
    Energy for Ethanol     :  -7629.287 kcal/mol
    Energy for Formic_acid :  -7890.662 kcal/mol
    Energy for Methanol    :  -5621.724 kcal/mol
    Energy for Water       :  -3618.401 kcal/mol
    [09:42:35] PLAMS run finished. Goodbye
    Test duration in seconds: 1
    
[/code]

[Next ](MoleculesFromRKFTrajectory.html "Extract frames from ams.rkf trajectory") [ Previous](He2DissociationCurve.html "Helium dimer dissociation curve")

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
