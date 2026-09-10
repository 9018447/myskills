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
      * Benchmark accuracy of basis sets
      * [Reaction energies with many different engines](ReactionEnergyBenchmark.html)
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
  * Benchmark accuracy of basis sets

# Benchmark accuracy of basis sets¶
[code] 
    import multiprocessing
    
    # Run jobs as many jobs as possible in parallel:
    config.default_jobrunner = JobRunner(parallel=True, maxjobs=multiprocessing.cpu_count())
    config.job.runscript.nproc = 1
    
    # The molecules we want to use in our benchmark:
    mol_smiles = {'Methane'  : 'C',
                  'Ethane'   : 'C-C',
                  'Ethylene' : 'C=C',
                  'Acetylene': 'C#C'}
    molecules = {}
    for name, smiles in mol_smiles.items():
        # Compute 10 conformers, optimize with UFF and pick the lowest in energy.
        molecules[name] = from_smiles(smiles, nconfs=10, forcefield='uff')[0]
        print(name, molecules[name])
    
    # Initialize the common settings:
    common_settings = Settings()
    common_settings.input.ams.Task = 'SinglePoint'
    common_settings.input.ams.System.Symmetrize = 'Yes'
    common_settings.input.adf.Basis.Core = 'None'
    
    basis = ['QZ4P', 'TZ2P', 'TZP', 'DZP', 'DZ', 'SZ']
    reference_basis = 'QZ4P'
    
    # Set up and run the calculations: 
    results = {}
    for bas in basis:
        for name, molecule in molecules.items():
            settings = common_settings.copy()
            settings.input.adf.Basis.Type = bas
            job = AMSJob(name=name+'_'+bas, molecule=molecule, settings=settings)
            results[(name,bas)] = job.run()
    
    # Calculate the average absolute error in bond energy per atom for each basis set:
    average_errors = {}
    for bas in basis:
        if bas != reference_basis:
            errors = []
            for name, molecule in molecules.items():
                reference_energy = results[(name,reference_basis)].get_energy(unit='kcal/mol')
                energy = results[(name,bas)].get_energy(unit='kcal/mol')
                errors.append(abs(energy - reference_energy)/len(molecule))
                print('Energy for {} using {} basis set: {} [kcal/mol]'.format(name,bas,energy))
            average_errors[bas] = sum(errors)/len(errors)
    
    print('== Results ==')
    print('Average absolute error in bond energy per atom')
    for bas in basis:
        if bas != reference_basis:
            print('Error for basis set {:<4}: {:>10.3f} [kcal/mol]'.format(bas, average_errors[bas]))
    
[/code]

Note

To execute this PLAMS script:

  * [`Download BasisSetBenchmark.py`](../_downloads/1b4c8758c3fce620a327413cc65a9a0c/BasisSetBenchmark.py)

  * `$AMSBIN/plams BasisSetBenchmark.py`

**Output**
[code] 
    [21:51:53] PLAMS working folder: /home/mirko/scratch/test.plams/rundir.plams.BasisSetBenchmark/plams_workdir
    Methane   Atoms: 
        1         C      0.000000      0.000000      0.000000 
        2         H      0.538912      0.762358     -0.599295 
        3         H      0.731244     -0.596616      0.583182 
        4         H     -0.567129     -0.670302     -0.678108 
        5         H     -0.703028      0.504560      0.694220 
      Bonds: 
       (1)--1.0--(2)
       (1)--1.0--(3)
       (1)--1.0--(4)
       (1)--1.0--(5)
    
    Ethane   Atoms: 
        1         C     -0.757196     -0.040522      0.044605 
        2         C      0.757196      0.040522     -0.044605 
        3         H     -1.205222      0.185290     -0.945970 
        4         H     -1.130281      0.694397      0.788688 
        5         H     -1.061719     -1.061491      0.357407 
        6         H      1.205222     -0.185290      0.945971 
        7         H      1.130281     -0.694396     -0.788689 
        8         H      1.061719      1.061491     -0.357406 
      Bonds: 
       (1)--1.0--(2)
       (1)--1.0--(3)
       (1)--1.0--(4)
       (1)--1.0--(5)
       (2)--1.0--(6)
       (2)--1.0--(7)
       (2)--1.0--(8)
    
    Ethylene   Atoms: 
        1         C      0.664485      0.027988     -0.023685 
        2         C     -0.664485     -0.027988      0.023685 
        3         H      1.253433     -0.878614      0.070299 
        4         H      1.167038      0.980564     -0.156575 
        5         H     -1.253433      0.878614     -0.070299 
        6         H     -1.167038     -0.980564      0.156575 
      Bonds: 
       (1)--2.0--(2)
       (1)--1.0--(3)
       (1)--1.0--(4)
       (2)--1.0--(5)
       (2)--1.0--(6)
    
    Acetylene   Atoms: 
        1         C     -0.587409      0.175060     -0.002211 
        2         C      0.587409     -0.094463      0.002211 
        3         H     -1.618985      0.411721     -0.006095 
        4         H      1.618985     -0.331124      0.006094 
      Bonds: 
       (1)--3.0--(2)
       (1)--1.0--(3)
       (2)--1.0--(4)
    
    [21:51:53] JOB Methane_QZ4P STARTED
    [21:51:53] JOB Ethane_QZ4P STARTED
    [21:51:53] JOB Ethylene_QZ4P STARTED
    [21:51:53] JOB Acetylene_QZ4P STARTED
    [21:51:53] JOB Methane_QZ4P RUNNING
    [21:51:53] JOB Methane_TZ2P STARTED
    [21:51:53] JOB Ethane_QZ4P RUNNING
    [21:51:53] JOB Ethylene_QZ4P RUNNING
    [21:51:53] JOB Ethane_TZ2P STARTED
    [21:51:53] JOB Ethylene_TZ2P STARTED
    [21:51:53] JOB Acetylene_QZ4P RUNNING
    [21:51:53] JOB Acetylene_TZ2P STARTED
    [21:51:53] JOB Methane_TZ2P RUNNING
    [21:51:53] JOB Methane_TZP STARTED
    [21:51:53] JOB Ethane_TZ2P RUNNING
    [21:51:53] JOB Ethane_TZP STARTED
    [21:51:53] JOB Ethylene_TZ2P RUNNING
    [21:51:53] JOB Acetylene_TZ2P RUNNING
    [21:51:53] JOB Ethylene_TZP STARTED
    [21:51:53] JOB Methane_TZP RUNNING
    [21:51:53] JOB Acetylene_TZP STARTED
    [21:51:53] JOB Ethane_TZP RUNNING
    [21:51:53] JOB Methane_DZP STARTED
    [21:51:53] JOB Ethane_DZP STARTED
    [21:51:53] JOB Ethylene_TZP RUNNING
    [21:51:53] JOB Ethylene_DZP STARTED
    [21:51:53] JOB Acetylene_TZP RUNNING
    [21:51:53] JOB Acetylene_DZP STARTED
    [21:51:53] JOB Methane_DZP RUNNING
    [21:51:53] JOB Methane_DZ STARTED
    [21:51:53] JOB Ethane_DZP RUNNING
    [21:51:53] JOB Ethylene_DZP RUNNING
    [21:51:53] JOB Acetylene_DZP RUNNING
    [21:51:53] JOB Ethane_DZ STARTED
    [21:51:53] JOB Ethylene_DZ STARTED
    [21:51:53] JOB Methane_DZ RUNNING
    [21:51:53] JOB Ethane_DZ RUNNING
    [21:51:53] JOB Acetylene_DZ STARTED
    [21:51:53] JOB Ethylene_DZ RUNNING
    [21:51:53] JOB Methane_SZ STARTED
    [21:51:53] JOB Acetylene_DZ RUNNING
    [21:51:53] JOB Ethane_SZ STARTED
    [21:51:53] JOB Ethylene_SZ STARTED
    [21:51:53] JOB Acetylene_SZ STARTED
    [21:51:53] JOB Methane_SZ RUNNING
    [21:51:53] JOB Ethane_SZ RUNNING
    [21:51:53] Waiting for job Methane_QZ4P to finish
    [21:51:53] JOB Ethylene_SZ RUNNING
    [21:51:53] JOB Acetylene_SZ RUNNING
    [21:51:56] JOB Methane_DZP FINISHED
    [21:51:56] JOB Methane_DZP SUCCESSFUL
    [21:51:57] JOB Methane_TZP FINISHED
    [21:51:57] JOB Methane_TZP SUCCESSFUL
    [21:51:57] JOB Methane_TZ2P FINISHED
    [21:51:57] JOB Methane_TZ2P SUCCESSFUL
    [21:51:58] JOB Ethylene_DZP FINISHED
    [21:51:58] JOB Ethylene_DZP SUCCESSFUL
    [21:51:58] JOB Acetylene_DZP FINISHED
    [21:51:58] JOB Acetylene_DZP SUCCESSFUL
    [21:51:58] JOB Acetylene_TZP FINISHED
    [21:51:58] JOB Acetylene_TZP SUCCESSFUL
    [21:51:58] JOB Methane_QZ4P FINISHED
    [21:51:58] JOB Methane_QZ4P SUCCESSFUL
    Energy for Methane using TZ2P basis set: -572.1101629292748 [kcal/mol]
    [21:51:58] Waiting for job Ethane_QZ4P to finish
    [21:51:58] JOB Ethylene_TZP FINISHED
    [21:51:58] JOB Ethylene_TZP SUCCESSFUL
    [21:51:59] JOB Methane_DZ FINISHED
    [21:51:59] JOB Methane_DZ SUCCESSFUL
    [21:51:59] JOB Ethane_DZP FINISHED
    [21:51:59] JOB Ethane_DZP SUCCESSFUL
    [21:52:00] JOB Ethylene_TZ2P FINISHED
    [21:52:00] JOB Ethylene_TZ2P SUCCESSFUL
    [21:52:00] JOB Acetylene_TZ2P FINISHED
    [21:52:00] JOB Acetylene_TZ2P SUCCESSFUL
    [21:52:00] JOB Methane_SZ FINISHED
    [21:52:00] JOB Methane_SZ SUCCESSFUL
    [21:52:00] JOB Ethylene_DZ FINISHED
    [21:52:00] JOB Ethylene_DZ SUCCESSFUL
    [21:52:00] JOB Ethane_TZP FINISHED
    [21:52:00] JOB Ethane_TZP SUCCESSFUL
    [21:52:01] JOB Acetylene_SZ FINISHED
    [21:52:01] JOB Acetylene_SZ SUCCESSFUL
    [21:52:01] JOB Acetylene_DZ FINISHED
    [21:52:01] JOB Acetylene_DZ SUCCESSFUL
    [21:52:01] JOB Ethylene_SZ FINISHED
    [21:52:01] JOB Ethylene_SZ SUCCESSFUL
    [21:52:01] JOB Ethane_DZ FINISHED
    [21:52:01] JOB Ethane_DZ SUCCESSFUL
    [21:52:02] JOB Ethylene_QZ4P FINISHED
    [21:52:02] JOB Ethylene_QZ4P SUCCESSFUL
    [21:52:02] JOB Ethane_SZ FINISHED
    [21:52:02] JOB Ethane_SZ SUCCESSFUL
    [21:52:02] JOB Acetylene_QZ4P FINISHED
    [21:52:02] JOB Acetylene_QZ4P SUCCESSFUL
    [21:52:03] JOB Ethane_TZ2P FINISHED
    [21:52:03] JOB Ethane_TZ2P SUCCESSFUL
    [21:52:08] JOB Ethane_QZ4P FINISHED
    [21:52:08] JOB Ethane_QZ4P SUCCESSFUL
    Energy for Ethane using TZ2P basis set: -971.882012717666 [kcal/mol]
    Energy for Ethylene using TZ2P basis set: -769.43290265999 [kcal/mol]
    Energy for Acetylene using TZ2P basis set: -555.6672866640299 [kcal/mol]
    Energy for Methane using TZP basis set: -571.0449016648643 [kcal/mol]
    Energy for Ethane using TZP basis set: -970.0758795895841 [kcal/mol]
    Energy for Ethylene using TZP basis set: -767.3275161232395 [kcal/mol]
    Energy for Acetylene using TZP basis set: -552.956282573915 [kcal/mol]
    Energy for Methane using DZP basis set: -569.1190167665213 [kcal/mol]
    Energy for Ethane using DZP basis set: -966.0916462896635 [kcal/mol]
    Energy for Ethylene using DZP basis set: -764.4133003958359 [kcal/mol]
    Energy for Acetylene using DZP basis set: -550.6461780402834 [kcal/mol]
    Energy for Methane using DZ basis set: -560.9344371700147 [kcal/mol]
    Energy for Ethane using DZ basis set: -951.1667072119619 [kcal/mol]
    Energy for Ethylene using DZ basis set: -750.1745137243371 [kcal/mol]
    Energy for Acetylene using DZ basis set: -537.1008064541019 [kcal/mol]
    Energy for Methane using SZ basis set: -723.550125571837 [kcal/mol]
    Energy for Ethane using SZ basis set: -1216.9142215158688 [kcal/mol]
    Energy for Ethylene using SZ basis set: -934.6558219377758 [kcal/mol]
    Energy for Acetylene using SZ basis set: -647.5029900541123 [kcal/mol]
    == Results ==
    Average absolute error in bond energy per atom
    Error for basis set TZ2P:      0.170 [kcal/mol]
    Error for basis set TZP :      0.537 [kcal/mol]
    Error for basis set DZP :      1.024 [kcal/mol]
    Error for basis set DZ  :      3.339 [kcal/mol]
    Error for basis set SZ  :     27.683 [kcal/mol]
    [21:52:08] PLAMS run finished. Goodbye
    Test duration in seconds: 15
    
[/code]

[Next ](ReactionEnergyBenchmark.html "Reaction energies with many different engines") [ Previous](ConvertToAMSRKFTrajectory.html "Convert to ams.rkf trajectory with bond guessing")

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
