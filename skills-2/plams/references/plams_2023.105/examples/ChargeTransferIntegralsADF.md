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
      * Charge transfer integrals with ADF
      * [Tuning the range separation](gammascan.html)
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
  * Charge transfer integrals with ADF

# Charge transfer integrals with ADF¶
[code] 
    # Add new results extraction method
    @add_to_class(ADFFragmentResults)
    def get_transfer_integrals(self):
        return self.job.full.results.read_rkf_section('TransferIntegrals', file='adf')
    
    # Common settings for all 3 jobs
    # In the interest of computational speed we use a minimal basis
    # set. For more quantitatively meaningful results, you should use 
    # a larger basis.
    common = Settings()
    common.input.ams.Task = 'SinglePoint'
    common.input.adf.Basis.Type = 'SZ'
    common.input.adf.Basis.Core = 'None'
    common.input.adf.Symmetry = 'NoSym'
    
    # Specific settings for full system job
    full = Settings()
    full.input.adf.transferintegrals = True
    
    # Load XYZ file and separate it into 2 fragments
    mol = Molecule('BenzeneDimer.xyz')
    mol.guess_bonds()
    fragments = mol.separate()
    if len(fragments) != 2:
        log('ERROR: Molecule {} was split into {} fragments'.format(mol.properties.name, len(fragments)))
        import sys; sys.exit(1)
    else:
        mol1, mol2 = fragments
    
    # Alternatively one could simply load fragments from separate xyz files:
    # mol1 = Molecule('fragment1.xyz')
    # mol2 = Molecule('fragment2.xyz')
    
    job = ADFFragmentJob(name='ADFTI',fragment1=mol1,fragment2=mol2,settings=common,full_settings=full)
    results = job.run()
    
    # TI is a dictionary with the whole TransferIntegrals section from adf.rkf
    print('== Results ==')
    TI = results.get_transfer_integrals()
    for key, value in sorted(TI.items()):
        print('{:<28}: {:>12.6f}'.format(key, value))
    
[/code]

Note

To execute this PLAMS script:

  * [`Download ChargeTransferIntegralsADF.py`](../_downloads/6e23471a18009908fd0953d4dba89826/ChargeTransferIntegralsADF.py)

  * [`Download BenzeneDimer.xyz`](../_downloads/e2b48835b804ad913e83f99b4b42af00/BenzeneDimer.xyz)

  * `$AMSBIN/plams ChargeTransferIntegralsADF.py`

**Output**
[code] 
    [10:20:01] PLAMS working folder: /scratch/rundir.plams.ChargeTransferIntegralsADF/plams_workdir
    [10:20:01] JOB ADFTI STARTED
    [10:20:01] JOB ADFTI RUNNING
    [10:20:01] JOB ADFTI/frag1 STARTED
    [10:20:01] JOB ADFTI/frag1 RUNNING
    [10:20:07] JOB ADFTI/frag1 FINISHED
    [10:20:07] JOB ADFTI/frag1 SUCCESSFUL
    [10:20:07] JOB ADFTI/frag2 STARTED
    [10:20:07] JOB ADFTI/frag2 RUNNING
    [10:20:10] JOB ADFTI/frag2 FINISHED
    [10:20:10] JOB ADFTI/frag2 SUCCESSFUL
    [10:20:10] JOB ADFTI/full STARTED
    [10:20:10] JOB ADFTI/full RUNNING
    [10:20:22] JOB ADFTI/full FINISHED
    [10:20:22] JOB ADFTI/full SUCCESSFUL
    [10:20:22] JOB ADFTI FINISHED
    [10:20:22] JOB ADFTI SUCCESSFUL
    == Results ==
    J(charge recombination 12)  :    -0.010748
    J(charge recombination 21)  :    -0.010747
    J(electron)                 :    -0.012049
    J(hole)                     :     0.034996
    S(charge recombination 12)  :     0.016227
    S(charge recombination 21)  :     0.016226
    S(electron)                 :     0.018761
    S(hole)                     :    -0.049852
    V(charge recombination 12)  :    -0.009868
    V(charge recombination 21)  :    -0.009868
    V(electron)                 :    -0.013127
    V(hole)                     :     0.026792
    Vtot(charge recombination 12):     0.013197
    Vtot(charge recombination 21):     0.013197
    Vtot(electron)              :     0.021460
    Vtot(hole)                  :     0.034181
    e1(electron)                :     0.057207
    e1(hole)                    :    -0.165894
    e2(electron)                :     0.057209
    e2(hole)                    :    -0.165896
    [10:20:22] PLAMS run finished. Goodbye
    Test duration in seconds: 22
    
[/code]

[Next ](gammascan.html "Tuning the range separation") [ Previous](AMSTSWorkflow/AMSTSWorkflow.html "AMS transition state workflow")

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
