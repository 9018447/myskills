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
  * [Interfaces](interfaces.html)
    * Amsterdam Modeling Suite
      * [AMS driver and engines](ams.html)
      * [AMS worker](amsworker.html)
      * [ASE Calculator for AMS](amscalculator.html)
      * [Quick jobs](quickjobs.html)
      * [Analysis tools: Densf, FCF, analysis](postadf.html)
      * [KF files](kffiles.html)
      * [COSMO-RS](crs.html)
      * [ParAMS](params.html)
      * [Conformers](conformers.html)
      * [Zacros](zacros.html)
      * [ADF (pre-2020 version)](adf.html)
      * [ReaxFF (pre-2019 version)](reaxff.html)
    * [Other programs](thirdparty.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Interfaces](interfaces.html)/
  * Amsterdam Modeling Suite

# Amsterdam Modeling Suite¶

PLAMS offers interfaces to the main programs of the Amsterdam Modelling Suite.

All possible input keywords and options are covered, as well as extraction of arbitrary data from binary files (called KF files) produced by these programs.

Note

How do I run X using PLAMS?

  * ADF : [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") with ADF engine

  * BAND : [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") with BAND engine

  * DFTB : [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") with DFTB engine

  * ReaxFF : [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") with ReaxFF engine

  * MOPAC : [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") with MOPAC engine

  * ForceField : [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") with ForceField engine

  * ParAMS : [ParAMSJob](params.html#params)

  * Densf : [`DensfJob`](postadf.html#scm.plams.interfaces.adfsuite.densf.DensfJob "scm.plams.interfaces.adfsuite.densf.DensfJob")

  * FCF : [`FCFJob`](postadf.html#scm.plams.interfaces.adfsuite.fcf.FCFJob "scm.plams.interfaces.adfsuite.fcf.FCFJob")

  * COSMO-RS : [`CRSJob`](crs.html#scm.plams.interfaces.adfsuite.crs.CRSJob "scm.plams.interfaces.adfsuite.crs.CRSJob")

  * Zacros : [ZacrosJob](zacros.html#zacros)

  * [AMS driver and engines](ams.html)
    * [Preparing input](ams.html#preparing-input)
    * [Preparing runscript](ams.html#preparing-runscript)
    * [Molecule handling](ams.html#molecule-handling)
      * [Multiple molecules](ams.html#multiple-molecules)
    * [AMSJob API](ams.html#amsjob-api)
    * [AMSResults API](ams.html#amsresults-api)
  * [AMS worker](amsworker.html)
    * [AMSWorker API](amsworker.html#amsworker-api)
    * [AMSWorkerResults API](amsworker.html#amsworkerresults-api)
    * [AMSWorkerPool API](amsworker.html#amsworkerpool-api)
  * [ASE Calculator for AMS](amscalculator.html)
    * [Introduction](amscalculator.html#introduction)
    * [AMS settings](amscalculator.html#ams-settings)
      * [ASE results](amscalculator.html#ase-results)
      * [Charge](amscalculator.html#charge)
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
      * [Special atoms in ADF](adf.html#special-atoms-in-adf)
    * [Preparing runscript](adf.html#preparing-runscript)
    * [API](adf.html#api)
  * [ReaxFF (pre-2019 version)](reaxff.html)

[Next ](ams.html "AMS driver and engines") [ Previous](interfaces.html "Interfaces")

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
