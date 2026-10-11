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
      * [Analysis tools: Densf, FCF, analysis](postadf.html)
      * [KF files](kffiles.html)
      * [COSMO-RS](crs.html)
      * [ParAMS](params.html)
      * Conformers
        * ConformersJob
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
  * Conformers

# Conformers¶

AMS’s [Conformers](../../AMS/Utilities/Conformers.html) is a flexible tool for conformers generation.

This page documents the PLAMS interface to **Conformers**. For a description of the capabilities and options of the Conformers tool, see the [documentation](../../AMS/Utilities/Conformers.html) in the AMS user manual.

See also

The [conformers generation example](../examples/ConformersGeneration/ConformersGeneration.html#conformers-example) in the [Examples](../examples/examples.html#examples) section of the PLAMS manual.

## ConformersJob¶

Technical

Import these classes from `scm.conformers`, not `scm.plams` !
[code] 
    from scm.conformers import ConformersJob, ConformersResults
    
[/code]

The `ConformersJob` class, which derives from [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob") class, can be used to set up and run a Conformers calculation.

The input options for the Conformers tool (described [here](../../AMS/Utilities/Conformers.html)) can be specified in the `input.ams` branch of a setting object. See the [Conformers Generation](../examples/ConformersGeneration/ConformersGeneration.html#conformers-example) example.

_class _`ConformersJob`(_name ='conformers'_, _molecule =None_, _** kwargs_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersJob)¶
    
`_result_type`¶
    
alias of `scm.conformers.plams.interface.ConformersResults`

`__init__`(_name ='conformers'_, _molecule =None_, _** kwargs_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`check`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersJob.check)¶
    
Check if the calculation was successful.

This method can be overridden in concrete subclasses of [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"). It should return a boolean value. The definition here serves as a default, to prevent crashing if a subclass does not define its own [`check()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.check "scm.plams.core.basejob.SingleJob.check"). It always returns `True`.

Warning

This method is meant for internal usage and **should not** be explicitly called in your script (but it can be overridden in subclasses). Manually calling [`check()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.check "scm.plams.core.basejob.SingleJob.check") is not thread safe. For a thread safe function to evaluate the state of your job please use [`ok()`](../components/jobs.html#scm.plams.core.basejob.Job.ok "scm.plams.core.basejob.Job.ok")

`get_input`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersJob.get_input)¶
    
Generate the input file. Abstract method.

This method should return a single string with the full content of the input file. It should process information stored in the `input` branch of job settings and in the `molecule` attribute.

`get_runscript`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersJob.get_runscript)¶
    
Generate the runscript. Abstract method.

This method should return a single string with the runscript contents. It can process information stored in `runscript` branch of job settings. In general the full runscript has the following form:
[code] 
    [first line defined by job.settings.runscript.shebang]
    
    [contents of job.settings.runscript.pre, when present]
    
    [value returned by get_runscript()]
    
    [contents of job.settings.runscript.post, when present]
    
[/code]

When overridden, this method should pay attention to `.runscript.stdout_redirect` key in job’s `settings`.

_class _`ConformersResults`(_* args_, _** kwargs_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults)¶
    
A specialized [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass for accessing the results of ConformersJob. Conformers are sorted by energy, from lowest to highest.

`__init__`(_* args_, _** kwargs_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`rkfpath`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.rkfpath)¶
    
Absolute path to the ‘conformers.rkf’ results file

`get_lowest_conformer`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.get_lowest_conformer)¶
    
Return the conformer with the lowest energy

`get_conformers`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.get_conformers)¶
    
Return a list containing all conformers found. The conformers are sorted according to their energy, the first element being the lowest energy conformer.

`get_relative_energies`(_unit ='au'_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.get_relative_energies)¶
    
Return the relative energies of the conformers i.e. the energy of the conformer minus the energy of the lowest conformer found. This list is sorted according to the energy of the conformers, the first element corresponding to the lowest energy conformer. So, by definition, the first element will have an energy of 0.

`get_energies`(_unit ='au'_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.get_energies)¶
    
Return the energies of the conformers. This list is sorted according to the energy of the conformers, the first element corresponding to the lowest energy conformer.

`get_lowest_energy`(_unit ='au'_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.get_lowest_energy)¶
    
Return the energy of the lowest-energy conformer.

`get_boltzmann_distribution`(_temperature_)[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.get_boltzmann_distribution)¶
    
Return the Boltzmann distribution at a given temperature: exp^(E_i/kB*temperature) / (sum_j exp^(E_j/kB*temperature)), where E_i is the energy of conformer i. This list is sorted according to the energy of the conformers, the first element corresponding to the lowest energy (and highest probability) conformer. The temperature is in Kelvin.

`__str__`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.__str__)¶
    
Return str(self).

`collect`()[[source]](../_modules/scm/conformers/plams/interface.html#ConformersResults.collect)¶
    
Collect files present in the job folder.

Use parent method from [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") to get a list of all files in the results folder. Then instantiate `self.rkf` to be a [`KFFile`](kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile") instance for the main `conformers.rkf` output file. Also instantiate `self._conformers` to be a Conformers instance built from it.

This method is called automatically during the final part of the job execution and there is no need to call it manually.

[Next ](zacros.html "Zacros") [ Previous](params.html "ParAMS")

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
