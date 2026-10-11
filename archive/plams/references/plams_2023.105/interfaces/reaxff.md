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
      * [Conformers](conformers.html)
      * [Zacros](zacros.html)
      * [ADF (pre-2020 version)](adf.html)
      * ReaxFF (pre-2019 version)
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
  * ReaxFF (pre-2019 version)

# ReaxFF (pre-2019 version)¶

Warning

This page describes the old interface to the standalone ReaxFF binary. As ReaxFF is now an AMS engine, you probably want to run it using [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob").

In the few simple examples below you can see how various types of ReaxFF calculations can be performed via PLAMS.

[`ReaxFF examples`](../_downloads/b2996b2f7018e9328eb9565144176a6d/reaxff_plams.zip)

_class _`ReaxFFJob`(_molecule =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob)¶
    
`check`()¶
    
Check if `termination status` variable from `General` section of main KF file equals `NORMAL TERMINATION`.

`get_input`()[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob.get_input)¶
    
Produce the `control` file based on key-value pairs present in `settings.input.control` branch.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob.get_runscript)¶
    
Generate a runscript.

Returned string is just `$AMSBIN/reaxff`, possibly prefixed with `export NSCM=(number)` if `settings.runscript.nproc` is present.

`hash_input`()[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob.hash_input)¶
    
Disable hashing for ReaxFF jobs.

It is a common task in molecular dynamics to run several trajectories with the same initial conditions. In such a case [Rerun prevention](../components/jobmanager.html#rerun-prevention) would prevent second and all consecutive executions. Hence we decided to disable [Rerun prevention](../components/jobmanager.html#rerun-prevention) for ReaxFF.

If you wish to bring it back, simply put `ReaxFFJob.hash_input = SingleJob.hash_inputs` somehwere at the beginning of your script.

`_get_ready`()[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob._get_ready)¶
    
Prepare contents of the job folder for execution.

Use the parent method from [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob") to produce the runscript and the input file (`control`). Then create `ffield` and `geo` files using, respectively, `_write_ffield()` and `_write_geofile()`.

Then copy to the job folder all files listed in `settings.input.external`. The value of this key should either be a list of strings with paths to files or a dictionary (also [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")) with paths to files as values and names under which these files should be copied to the job folder as keys.

`_write_ffield`(_ffield_)[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob._write_ffield)¶
    
Copy to the job folder a force field file indicated by _ffield*_.

_ffield_ should be a string with a path to some external file or with a filename present in `$AMSHOME/atomicdata/ForceFields/ReaxFF`. The location of this search folder is defined by `ffield_path` class attribute).

Given file is always coied to the job folder as `ffield`, due to ReaxFF program requirements.

`_write_geofile`(_molecule_ , _filename_ , _settings_ , _description_ , _lattice =False_)[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob._write_geofile)¶
    
Write to _filename_ a geo-file describing _molecule_.

_settings_ should be a [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance containing all the additional key-value pairs that should be present in the resulting geo-file. To obtain multiple occurrences of the same key in the geo-file, put all the values as a list in _settings_.

_description_ is the default value for `DESCRP` key. It is used only if `descrp` key is not present in _settings_.

If _lattice_ is `True`, the information about periodicity is printed to the resulting geo-file with `CRYSTX` key. If the supplied _molecule_ does not contain lattice vectors (or contains less then 3 of them), this method will add them (and hence alter _molecule_!). The length of added vectors is defined by `default_cell_size` class attribute.

_settings_ can also be a single string with a path to a file – in that case this file is copied as _filename_ and all the rest of this method is skipped.

Note

If _lattice_ is `True` and the lattice present in _molecule_ does not follow ReaxFF convention (the third vector aligned with Z axis, the second one with YZ plane), this method will rotate the _molecule_ to fulfill these requirements.

_static _`_convert_lattice`(_lattice_)[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#ReaxFFJob._convert_lattice)¶
    
Convert a _lattice_ expressed as three 3-dimensional vectors to (_a_ , _b_ , _c_ , _alpha_ , _beta_ , _gamma_) format. Lengths of lattice vectors are expressed as _a_ , _b_ and _c_ , angles between them as _alpha_ , _beta_ , _gamma_.

`load_reaxff_control`(_filename_ , _keep_order =True_)[[source]](../_modules/scm/plams/interfaces/adfsuite/reaxff.html#load_reaxff_control)¶
    
Return a [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance containing all data from an existing `control` file, indicated by _filename_.

If _keep_order_ is `True`, the returned [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance is enriched with the `_order` key containing a list of all keys in the same order they were present in the loaded `contol` file.

[Next ](thirdparty.html "Other programs") [ Previous](adf.html "ADF \(pre-2020 version\)")

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
