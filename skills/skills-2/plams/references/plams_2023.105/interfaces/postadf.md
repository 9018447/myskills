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
    * [Amsterdam Modeling Suite](amssuite.html)
      * [AMS driver and engines](ams.html)
      * [AMS worker](amsworker.html)
      * [ASE Calculator for AMS](amscalculator.html)
      * [Quick jobs](quickjobs.html)
      * Analysis tools: Densf, FCF, analysis
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
  * [Amsterdam Modeling Suite](amssuite.html)/
  * Analysis tools: Densf, FCF, analysis

# Analysis tools: Densf, FCF, analysis¶

Apart from main computational programs mentioned above, Amsterdam Modeling Suite offers a range of small utility tools that can be used to obtain more specific results. These tools usually base on the prior run of one of the main programs and need the KF file produced by them as a part of the input.

From the functional point of view these tools are very similar to ADF or AMS. Their results are stored in KF files and their input files follow the same structure of blocks, keys and values. Because of that the same classes ([`SCMJob`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMJob "scm.plams.interfaces.adfsuite.scmjob.SCMJob") and [`SCMResults`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMResults "scm.plams.interfaces.adfsuite.scmjob.SCMResults")) are used as bases and hence preparation, running and results extraction for utility tools follow the same rules as the AMS program.

The main difference is that usually utility jobs don’t need molecular coordinates as part of the input (they extract this information from previous calculation’s KF file). So no [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance is needed and the `molecule` attribute of the job object is simply ignored. Because of that `get_molecule()` method does not work with `FCFResults`, `DensfResults` etc.

Below you can find the list of dedicated job classes that are currently available. Details about input specification for those jobs can be found in corresponding part of AMS suite documentation.

_class _`FCFJob`(_inputjob1 =None_, _inputjob2 =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/fcf.html#FCFJob)¶
    
A class representing calculation of Franck-Condon factors using `fcf` program.

Two new attributes are introduced: `inputjob1` and `inputjob2`. They are used to supply KF files from previous runs to `fcf` program. The value can either be a string with a path to KF file or an instance of any type of [`SCMJob`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMJob "scm.plams.interfaces.adfsuite.scmjob.SCMJob") or [`SCMResults`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMResults "scm.plams.interfaces.adfsuite.scmjob.SCMResults") (in this case the path to corresponding KF file will be extracted automatically). If the value of `inputjob1` or `inputjob2` is `None`, no automatic handling occurs and user needs to manually supply paths to input jobs using proper keywords placed in `myjob.settings.input` (`STATES` or `STATE1` and `STATE2`).

The resulting `TAPE61` file is renamed to `jobname.t61`.

`__init__`(_inputjob1 =None_, _inputjob2 =None_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/fcf.html#FCFJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`_serialize_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/fcf.html#FCFJob._serialize_mol)¶
    
Process [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance stored in `molecule` attribute and add it as relevant entries of `settings.input` branch. Abstract method.

`_remove_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/fcf.html#FCFJob._remove_mol)¶
    
Remove from `settings.input` all entries added by `_serialize_mol()`. Abstract method.

_class _`DensfJob`(_inputjob =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/densf.html#DensfJob)¶
    
A class representing calculation of molecular properties on a grid using `densf` program.

A new attribute `inputjob` is introduced to supply KF file from previously run job. The value can either be a string with a path to KF file or an instance of any type of [`SCMJob`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMJob "scm.plams.interfaces.adfsuite.scmjob.SCMJob") or [`SCMResults`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMResults "scm.plams.interfaces.adfsuite.scmjob.SCMResults") (in this case the path to corresponding KF file will be extracted automatically). If the value of `inputjob` is `None`, no automatic handling occurs and user needs to manually supply path to input job using `INPUTFILE` keyword placed in `myjob.settings.input`.

The resulting `TAPE41` file is renamed to `jobname.t41`.

`__init__`(_inputjob =None_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/densf.html#DensfJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`_serialize_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/densf.html#DensfJob._serialize_mol)¶
    
Process [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance stored in `molecule` attribute and add it as relevant entries of `settings.input` branch. Abstract method.

`_remove_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/densf.html#DensfJob._remove_mol)¶
    
Remove from `settings.input` all entries added by `_serialize_mol()`. Abstract method.

`check`()[[source]](../_modules/scm/plams/interfaces/adfsuite/densf.html#DensfJob.check)¶
    
Check if `termination status` variable from `General` section of main KF file equals `NORMAL TERMINATION`.

_class _`AMSAnalysisJob`(_name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsanalysis.html#AMSAnalysisJob)¶
    
A class for analyzing molecular dynamics trajectories using the `analysis` program.

`__init__`(_** kwargs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsanalysis.html#AMSAnalysisJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`_serialize_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsanalysis.html#AMSAnalysisJob._serialize_mol)¶
    
Process [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance stored in `molecule` attribute and add it as relevant entries of `settings.input` branch. Abstract method.

`_remove_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsanalysis.html#AMSAnalysisJob._remove_mol)¶
    
Remove from `settings.input` all entries added by `_serialize_mol()`. Abstract method.

`check`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsanalysis.html#AMSAnalysisJob.check)¶
    
Check if `termination status` variable from `General` section of main KF file equals `NORMAL TERMINATION`.

[Next ](kffiles.html "KF files") [ Previous](quickjobs.html "Quick jobs")

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
