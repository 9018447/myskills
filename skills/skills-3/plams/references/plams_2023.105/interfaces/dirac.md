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
      * Dirac
        * Preparing a calculation
        * Results extraction
        * API
      * [MOPAC (standalone program)](mopac.html)
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
  * Dirac

# Dirac¶

DIRAC is an _ab initio_ quantum chemistry program for all electron relativistic calculation. It features a variety of methods including HF, MP2, DFT, CI and CC. More information about DIRAC can be found on its [official website](http://www.diracprogram.org).

PLAMS offers a simple DIRAC interface and is capable of running DIRAC calculations. The relevant classes are `DiracJob` and `DiracResults`.

## Preparing a calculation¶

Preparing an instance of `DiracJob` follows general principles for [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"). Information adjusting input file is stored in `myjob.settings.input` branch, whereas a runscript is created based on contents of `myjob.settings.runscript`. The geometry of your system can be supplied in two ways. Unlike ADF or BAND, DIRAC uses two separate files, one for input settings and the other for atomic coordinates. Geometry file needs to be in `.xyz` format and it can be either generated automatically based on `myjob.molecule` or given directly by the user (see below for details).

### Input¶

Input files for DIRAC are organized using blocks and subblocks with three level hierarchy. On the top level there are _blocks_ (indicated by keywords starting with `**`) which can contain _keys_ (starting with `.`) or _subblocks_ (starting with `*`), which in turn can contain more keys. This structure can be easily reflected with tree-like [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") objects. In general, the preparation process is quite similar to [`SCMJob`](adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMJob "scm.plams.interfaces.adfsuite.scmjob.SCMJob"), however, there are a few nuances. The details are explained below.

  * Each key present on the top level of `myjob.settings.input` is translated to a block. Values of those keys should be [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instances. The block `DIRAC` is always printed as the first one, all other are ordered lexicographically (this behavior can be changed with `DiracJob._top` class attribute).

  * In each block various keys and subblocks can be present. Subblocks are indicated by nested [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instances, all other values are interpreted as keys.

  * An empty value of a key can be obtained by setting its value to `True`.

  * An empty block or subblock can be obtained with an empty [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance.

  * If the value of a key is a list, each element of this list will be printed in a separate line.

  * All keywords are written to the input file with upper case, values remain unchanged.

  * Many DIRAC keywords contain spaces (for example `WAVE FUNCTION` or `LINEAR RESPONSE`) and thus cannot be used with convenient dot notation. Usual bracket notation has to be used in those cases (see [Dot notation](../components/settings.html#dot-notation)).

  * Some subblocks follow the special requirement - they need to be “enabled” by presence of the corresponding keyword in the parent block. For example, in `**HAMILTONIAN` block a _subblock_ `*FDE` can be used to specify frozen density embedding parameters, but this subblock is taken into account only if a _key_ `.FDE` is present in `**HAMILTONIAN`. This introduces a problem, since you cannot store two entries with the same name in [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings"):
[code] #sets the .FDE key on the top level of HAMILOTNIAN block
        myjob.setting.input.hamiltonian.fde = True
        #sets the *FDE subblock in the HAMILTONIAN block, but overwrites the key .FDE defined above
        myjob.setting.input.hamiltonian.fde.frdens = 'value2'
        
[/code]

To solve this problem a special “enabler” key `_en` can be used _inside the subblock_. If such a key is present, the parent block of this subblock will be enriched with corresponding key and value:
[code] #sets the .FDE key on the top level of HAMILOTNIAN block, its value can be set just like any other key
        myjob.setting.input.hamiltonian.fde._en = True
        #sets the "proper" contents of *FDE subblock.
        myjob.setting.input.hamiltonian.fde.frdens = 'value2'
        
[/code]

### Runscript¶

Calculations with DIRAC are executed using a start script called `pam`. This script accepts a range of option flags adjusting various technical aspects of calculation, including input and geometry files. You can type `pam -h` in you command line for details.

A runscript calling `pam` is automatically generated by PLAMS. Its contents are based on `myjob.settings.runscript` branch and follow general rules described in [Contents of job settings](../components/jobs.html#job-settings). Besides that, the subbranch `myjob.settings.runscript.pam` is used to store option flags. Every key-value pair present there is transformed to `--key=value` flag appended to `pam` execution command. Following the usual convention, `True` represents an “empty value” (to get flags like `--key`) and list can be used for keys with multiple values (`--key="val1 val2 val3"`).

Initially, when an instance of `DiracJob` is created, the following `pam` options are set by default:
[code] 
    self.settings.runscript.pam.noarch = True
    self.settings.runscript.pam.get = ['DFCOEF', 'GRIDOUT', 'dirac.xml']
    
[/code]

Their role is to obtain from DIRAC scratch space all the files produced by your calculation (they can be later discarded with [Cleaning job folder](../components/results.html#cleaning) if not needed) and prevent creating a `.tgz` archive out of them (to allow PLAMS to process them). These two default flags can be changed or removed if needed, but this can hinder some [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") functionalities, so make sure to know what you are doing.

You don’t need to manually set mandatory `inp` and `mol` flags, they are added automatically just before the runscript is generated. If, for some reason, you don’t want to use automatic molecule handling and wish to provide a geometry file by yourself, all you need to do is to set `mol` entry in `myjob.settings.runscript.pam` with the path of your geometry file. PLAMS will then ignore geometry stored in `myjob.molecule` and use the supplied path.

## Results extraction¶

DIRAC produces two output files that can contain meaningful information. One is a “real” output of the calculation and the other is more technical output of `pam` script. For the sake of consistency PLAMS concatenates those two files into a single output file. The `pam` output is appended at the end of the “real” output, separated by a visual delimeter. Besides the regular text output some other files are produced by DIRAC. By default, `DFCOEF`, `GRIDOUT` and `dirac.xml` are fetched from the scratch space and renamed to, respectively, `jobname.dfcoef`, `jobname.grid` and `jobname.xml`.

General text processing methods from [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") can be used to obtain data from results files. At the moment, no special tools are present for binary files. Contents of `.xml` files can be easily accessed with standard Python libraries present in [`xml`](https://docs.python.org/3.8/library/xml.html#module-xml "\(in Python v3.8\)") package.

## API¶

_class _`DiracJob`(_molecule =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracJob)¶
    
A class representing a single computational job with DIRAC.

`__init__`(_** kwargs_)[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`_get_ready`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracJob._get_ready)¶
    
Before generating runscript and input with parent method [`SingleJob._get_ready`](../components/jobs.html#scm.plams.core.basejob.SingleJob._get_ready "scm.plams.core.basejob.SingleJob._get_ready") add proper `mol` and `inp` entries to `self.settings.runscript.pam`. If already present there, `mol` will not be added.

`get_input`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracJob.get_input)¶
    
Transform all contents of `input` branch of `settings` into string with blocks, subblocks, keys and values.

On the highest level alphabetic order of iteration is modified: keys occuring in class attribute `_top` are printed first. See Input for details.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracJob.get_runscript)¶
    
Generate a runscript. Returned string is a `pam` call followed by option flags generated based on `self.settings.runscript.pam` contents. See Runscript for details.

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracJob.check)¶
    
Check if the calculation was successful by examining the last line of `pam` output.

_class _`DiracResults`(_job_)[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracResults)¶
    
A class for result of computation done with DIRAC.

`collect`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dirac.html#DiracResults.collect)¶
    
After collecting the files produced by job execution with parent method [`Results.collect`](../components/results.html#scm.plams.core.results.Results.collect "scm.plams.core.results.Results.collect") append the `pam` output to the regular output file.

[Next ](mopac.html "MOPAC \(standalone program\)") [ Previous](dftbplus.html "DFTB+")

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
