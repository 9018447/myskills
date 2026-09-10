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
    * [Other programs](thirdparty.html)
      * [CP2K](cp2k.html)
      * [Crystal](crystal.html)
      * [DFTB+](dftbplus.html)
      * [Dirac](dirac.html)
      * MOPAC (standalone program)
        * Preparing input
        * API
      * [ORCA](orca.html)
      * [RASPA](raspa.html)
      * [VASP](vasp.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Interfaces](interfaces.html)/
  * [Other programs](thirdparty.html)/
  * MOPAC (standalone program)

# MOPAC (standalone program)¶

Technical

Starting from AMS2019, MOPAC is fully integrated as an AMS engine. If you want to use the MOPAC engine in AMS2019, you should use [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") (and not `MOPACJob`). This page documents the interface to the standalone MOPAC program.

MOPAC (Molecular Orbital PACkage) is a semiempirical quantum chemistry program based on NDDO approximation. More information about the standalone MOPAC program can be found on its [official website](http://openmopac.net/).

PLAMS features a basic interface to standalone MOPAC program via the classes `MOPACJob` and `MOPACResults`.

## Preparing input¶

Preparing an instance of `MOPACJob` follows general principles for [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"). Information adjusting input file is stored in `myjob.settings.input` branch, whereas a runscript is created based on contents of `myjob.settings.runscript`. The geometry of your system is supplied in the standard way: with the `molecule` attribute.

The input format of the standalone MOPAC program is simple and straightforward: all the keywords adjusting parameters of your calculation are placed in the first line of the input file. Next two lines are left for user’s comments and then geometry of the system follows.

Since blocks and subblocks are not present in MOPAC’s input, the ``myjob.settings.input` branch needs to have a flat structure, just like a regular dictionary, without any nested [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instances. The value of a particular key adjusts the way in which keywords are printed in the first line of the input file:

  * `myjob.settings.input.keyword = True` will print `keyword`

  * `myjob.settings.input.keyword = value` will print `keyword=value` (with `value` being casted to `str` if needed)

  * `myjob.settings.input.keyword = (val1, val2, ...)` will print `keyword=(val1,val2,...)` (when value is a **tuple**)

  * `myjob.settings.input.keyword = [val1, val2, ...]` will print `keyword(val1,val2,...)` (when value is a **list**)

Moreover, if the keyword `AUX` is not supplied by the user, it is automatically inserted in the form `AUX(0,PRECISSION=9)` (for compatibility with AMSSuite GUI).

The standalone MOPAC program allows to freeze each coordinate of each atom separately. This information is extracted from `mopac_freeze` key in each atom’s properties. If present, this key should contain a string with all axes that you wish to freeze for a particular atom:
[code] 
    mol = Molecule('system.xyz')
    mol[1].properties.mopac_freeze = 'x'    #freeze x coordinate of atom 1
    mol[2].properties.mopac_freeze = 'yz'   #freeze y and z coordinates of atom 2
    mol[3].properties.mopac_freeze = 'xyz'  #freeze atom 3
    
[/code]

## API¶

_class _`MOPACJob`(_molecule =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/mopac.html#MOPACJob)¶
    
A class representing a single computational job with MOPAC.

`get_input`()[[source]](../_modules/scm/plams/interfaces/adfsuite/mopac.html#MOPACJob.get_input)¶
    
Transform the contents of `input` branch of `settings` into the first line of MOPAC input. Print the molecular coordinates together with frozen coordinate flags.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/adfsuite/mopac.html#MOPACJob.get_runscript)¶
    
Generate a MOPAC runscript.

The name of the MOPAC executable is taken from class attribute `MOPACJob._command`. If you experience problems running MOPAC, check if that value corresponds to the name of the executable and this executable is visible in your `$PATH` (in case of AMSuite it’s in `$AMSBIN`). Note that a bare MOPAC executable should be used here, please avoid using any wrappers.

The execution of MOPAC binary is followed by calling a simple command line tool `tokf` which reads various output text files produced by MOPAC and collects all the data in a binary KF file. See [KF files](kffiles.html#kf-files) for details.

`check`()[[source]](../_modules/scm/plams/interfaces/adfsuite/mopac.html#MOPACJob.check)¶
    
Grep standard output for `* JOB ENDED NORMALLY *`.

_class _`MOPACResults`(_job_)[[source]](../_modules/scm/plams/interfaces/adfsuite/mopac.html#MOPACResults)¶
    
A class for results of computation done with MOPAC.

This class inherits all methods from [`SCMResults`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMResults "scm.plams.interfaces.adfsuite.scmjob.SCMResults").

Technical

In case of a MOPAC job, preparation is much different from other programs of AMSuite, but the result handling is quite similar due to presence of KF files. Therefore `MOPACResults` is a subclass of [`SCMResults`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMResults "scm.plams.interfaces.adfsuite.scmjob.SCMResults"), but `MOPACJob` is not a subclass of [`SCMJob`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMJob "scm.plams.interfaces.adfsuite.scmjob.SCMJob").

`_atomic_numbers_input_order`()[[source]](../_modules/scm/plams/interfaces/adfsuite/mopac.html#MOPACResults._atomic_numbers_input_order)¶
    
Return a list of atomic numbers, in the input order. Abstract method.

[Next ](orca.html "ORCA") [ Previous](dirac.html "Dirac")

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
