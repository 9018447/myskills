[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](_static/plams_logo.png) ](index.html)

  * 

Table of contents

  * General
    * What’s new in PLAMS for AMS2023?
  * [Introduction](intro.html)
  * [Getting started](started.html)
  * [Components overview](components/components.html)
  * [Interfaces](interfaces/interfaces.html)
  * [Examples](examples/examples.html)
  * [Cookbook](cookbook/cookbook.html)
  * [Citations](citations.html)

  * [FAQ](FAQ.html)

__[PLAMS](index.html)

  * [Documentation](PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](index.html)/
  * General

# General¶

## What’s new in PLAMS for AMS2023?¶

  * The [ASE Calculator for AMS](interfaces/amscalculator.html#amscalculator) class for running any AMS engine with ASE (see: [AMSCalculator: ASE geometry optimizer with AMS forces](examples/AMSCalculator/ASECalculator.html#amscalculatorexample))

  * Classes for calculating [reduction and oxidation potentials](examples/RedoxPotential.html#redoxexample) with ADF and optionally COSMO-RS

  * The [ADFCOSMORSCompoundJob](examples/ADFCOSMORSCompound.html#adfcosmorscompound) class for running jobs equivalent to “Task COSMO-RS Compound” in the AMS GUI. Such a job generates a .coskf file for use with COSMO-RS.

  * The calculation of the [vibronic density of states](examples/fcf_dos.html#fcf-dos) has been added to PLAMS.

  * Classes for running and restarting [molecular dynamics (MD) jobs with AMS](examples/MDJobs.html#amsmdjob)

  * A class for generating and analyzing [conformers](interfaces/conformers.html#conformers-interface)

  * [Quick jobs](interfaces/quickjobs.html#quickjobs), like for example the `preoptimize()` function let you quickly optimize a Molecule

  * [Packmol interface](components/mol_packmol.html#packmolinterface) for generating liquid and gas mixtures, solid-liquid interfaces, and microsolvation spheres

  * [File format conversion tools](components/utils.html#fileformatconversiontools) for converting VASP, Gaussian, or Quantum ESPRESSO output to ams.rkf and engine.rkf files that can be opened with the AMS GUI

  * [Plotting tools](components/utils.html#plottingtools) for plotting a molecule or ASE Atoms inside a Jupyter notebook

  * [Plotting tools](components/utils.html#plottingtools) for plotting the [electronic band structure](examples/BandStructure/BandStructure.html#bandstructureexample)

  * Additions to [`AMSResults`](interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults"): get_homo_energies(), get_lumo_energies, get_smallest_homo_lumo_gap()

  * Additions to [`Molecule`](components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"): guess_atomic_charges(), set_density(), get_unique_bonds(), get_unique_angles()

  * Many new [Examples](examples/examples.html#examples)

[Next ](intro.html "Introduction") [ Previous](index.html "Python Library for Automating Molecular Simulations")

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
