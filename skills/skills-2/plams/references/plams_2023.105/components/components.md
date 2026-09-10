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
  * Components overview
    * [Settings](settings.html)
    * [Jobs](jobs.html)
    * [Results](results.html)
    * [Job runners](runners.html)
    * [Job manager](jobmanager.html)
    * [Public functions](functions.html)
    * [Molecule](molecule.html)
    * [Utilities](utils.html)
    * [Trajectories](trajectories.html)
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * Components overview

# Components overview¶

This chapter contains description of all components (classes, functions, decorators) that can be used within PLAMS scripts. In each part you can find API specification of a particular component, an explanation of its role in the whole environment and examples of usage.

  * [Settings](settings.html)
    * [Tree-like structure](settings.html#tree-like-structure)
    * [Dot notation](settings.html#dot-notation)
    * [Case sensitivity](settings.html#case-sensitivity)
    * [Global settings](settings.html#global-settings)
    * [API](settings.html#api)
  * [Jobs](jobs.html)
    * [Preparing a job](jobs.html#preparing-a-job)
      * [Contents of job settings](jobs.html#contents-of-job-settings)
      * [Default settings](jobs.html#default-settings)
    * [Running a job](jobs.html#running-a-job)
      * [Name conflicts](jobs.html#name-conflicts)
      * [Prerun and postrun methods](jobs.html#prerun-and-postrun-methods)
      * [Preview mode](jobs.html#preview-mode)
    * [Job API](jobs.html#job-api)
    * [Single jobs](jobs.html#single-jobs)
      * [Subclassing SingleJob](jobs.html#subclassing-singlejob)
    * [Multijobs](jobs.html#multijobs)
      * [Using MultiJob](jobs.html#using-multijob)
  * [Results](results.html)
    * [Files in the job folder](results.html#files-in-the-job-folder)
    * [Synchronization of parallel job executions](results.html#synchronization-of-parallel-job-executions)
      * [Examples](results.html#examples)
    * [Cleaning job folder](results.html#cleaning-job-folder)
      * [Cleaning for multijobs](results.html#cleaning-for-multijobs)
    * [API](results.html#api)
  * [Job runners](runners.html)
    * [Local job runner](runners.html#local-job-runner)
    * [Remote job runner](runners.html#remote-job-runner)
  * [Job manager](jobmanager.html)
    * [Rerun prevention](jobmanager.html#rerun-prevention)
    * [Pickling](jobmanager.html#pickling)
    * [Restarting scripts](jobmanager.html#restarting-scripts)
    * [API](jobmanager.html#api)
  * [Public functions](functions.html)
    * [Logging](functions.html#logging)
    * [Binding decorators](functions.html#binding-decorators)
  * [Molecule](molecule.html)
    * [Molecule](mol_api.html)
      * [Atom labeling](mol_api.html#atom-labeling)
    * [Atom](atombond.html)
    * [Bond](atombond.html#bond)
    * [RDKit interface](mol_rdkit.html)
    * [ASE interface](mol_ase.html)
    * [Packmol interface](mol_packmol.html)
  * [Utilities](utils.html)
    * [Periodic Table](utils.html#periodic-table)
    * [Units](utils.html#units)
    * [Geometry tools](utils.html#geometry-tools)
    * [File format conversion tools](utils.html#file-format-conversion-tools)
    * [Plotting tools](utils.html#plotting-tools)
  * [Trajectories](trajectories.html)
    * [XYZ trajectory files](xyz.html)
      * [XYZ history files](xyz.html#xyz-history-files)
    * [RKF trajectory files](rkf.html)
      * [RKF history files](rkf.html#rkf-history-files)
    * [DCD trajectory files](dcd.html)
    * [Trajectory class](trajectory.html)

[Next ](settings.html "Settings") [ Previous](../started.html "Getting started")

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
