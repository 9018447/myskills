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
  * Interfaces
    * [Amsterdam Modeling Suite](amssuite.html)
    * [Other programs](thirdparty.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * Interfaces

# Interfaces¶

In this chapter we present a list of PLAMS interfaces to other programs and packages. A majority of what follows below are interfaces to so called _external binaries_ – computational chemistry tools that come in a form of executable programs that read an input file, perform calculations and produce various output files. From PLAMS perspective each such interface is just a subclass of [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob") that implements a way of producing a working runscript ([`get_runscript()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.get_runscript "scm.plams.core.basejob.SingleJob.get_runscript")) and a valid input file ([`get_input()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.get_input "scm.plams.core.basejob.SingleJob.get_input")) for a particular binary based on the contents of job settings. Usually such a “specialized” [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob") subclass comes together with a corresponding specialized [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass providing methods for accessing the data produced by the binary. Some of these methods are just simple convenience shortcuts (like `get_energy()` or `get_main_molecule()`), others provide access to files in whatever formats a particular binary produces (XML, binary files).

Interfaces described below are divided into interfaces to programs and tools that are included in Amsterdam Modeling Suite and interfaces to third party computational chemistry packages (usually contributed by other PLAMS users). The last chapter presents a bit different kind of interfaces, so called _molecule interfaces_. They offer a way of using PLAMS [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") class with other libraries capable of manipulating molecular coordinates.

  * [Amsterdam Modeling Suite](amssuite.html)
    * [AMS driver and engines](ams.html)
      * [Preparing input](ams.html#preparing-input)
      * [Preparing runscript](ams.html#preparing-runscript)
      * [Molecule handling](ams.html#molecule-handling)
      * [AMSJob API](ams.html#amsjob-api)
      * [AMSResults API](ams.html#amsresults-api)
    * [AMS worker](amsworker.html)
      * [AMSWorker API](amsworker.html#amsworker-api)
      * [AMSWorkerResults API](amsworker.html#amsworkerresults-api)
      * [AMSWorkerPool API](amsworker.html#amsworkerpool-api)
    * [ASE Calculator for AMS](amscalculator.html)
      * [Introduction](amscalculator.html#introduction)
      * [AMS settings](amscalculator.html#ams-settings)
      * [AMS standalone and worker mode](amscalculator.html#ams-standalone-and-worker-mode)
      * [Technical](amscalculator.html#technical)
      * [AMSCalculator API](amscalculator.html#amscalculator-api)
    * [Quick jobs](quickjobs.html)
    * [Analysis tools: Densf, FCF, analysis](postadf.html)
    * [KF files](kffiles.html)
    * [COSMO-RS](crs.html)
      * [Settings](crs.html#settings)
      * [Settings with multiple compound](crs.html#settings-with-multiple-compound)
      * [ADF and CRSJob](crs.html#adf-and-crsjob)
      * [COSMO-RS Parameters](crs.html#cosmo-rs-parameters)
      * [Data analyses and plotting](crs.html#data-analyses-and-plotting)
      * [API](crs.html#api)
    * [ParAMS](params.html)
    * [Conformers](conformers.html)
      * [ConformersJob](conformers.html#conformersjob)
    * [Zacros](zacros.html)
    * [ADF (pre-2020 version)](adf.html)
      * [Preparing input](adf.html#preparing-input)
      * [Preparing runscript](adf.html#preparing-runscript)
      * [API](adf.html#api)
    * [ReaxFF (pre-2019 version)](reaxff.html)
  * [Other programs](thirdparty.html)
    * [CP2K](cp2k.html)
      * [Settings](cp2k.html#settings)
      * [Molecule parsing](cp2k.html#molecule-parsing)
      * [Loading jobs](cp2k.html#loading-jobs)
      * [Molecule loading](cp2k.html#molecule-loading)
      * [API](cp2k.html#api)
    * [Crystal](crystal.html)
      * [Preparing a calculation](crystal.html#preparing-a-calculation)
      * [Molecule parsing](crystal.html#molecule-parsing)
      * [Results extraction](crystal.html#results-extraction)
      * [Example](crystal.html#example)
      * [API](crystal.html#api)
    * [DFTB+](dftbplus.html)
      * [Preparing a calculation](dftbplus.html#preparing-a-calculation)
      * [Results extraction](dftbplus.html#results-extraction)
      * [Example](dftbplus.html#example)
      * [API](dftbplus.html#api)
    * [Dirac](dirac.html)
      * [Preparing a calculation](dirac.html#preparing-a-calculation)
      * [Results extraction](dirac.html#results-extraction)
      * [API](dirac.html#api)
    * [MOPAC (standalone program)](mopac.html)
      * [Preparing input](mopac.html#preparing-input)
      * [API](mopac.html#api)
    * [ORCA](orca.html)
      * [Settings](orca.html#settings)
      * [Loading jobs](orca.html#loading-jobs)
      * [API](orca.html#api)
    * [RASPA](raspa.html)
      * [Input](raspa.html#input)
      * [Molecule parsing](raspa.html#molecule-parsing)
      * [Loading jobs](raspa.html#loading-jobs)
      * [API](raspa.html#api)
    * [VASP](vasp.html)
      * [Results](vasp.html#results)
      * [API](vasp.html#api)

[Next ](amssuite.html "Amsterdam Modeling Suite") [ Previous](../components/trajectory.html "Trajectory class")

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
