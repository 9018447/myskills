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
      * [MOPAC (standalone program)](mopac.html)
      * [ORCA](orca.html)
      * RASPA
        * Input
        * Molecule parsing
        * Loading jobs
        * API
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
  * RASPA

# RASPA¶

(_contributed by_ [Patrick Melix](https://www.researchgate.net/profile/Patrick_Melix))

The runscript written by PLAMS expects the environment variable _$RASPA_DIR_ to be set. It should point to the location [RASPA](https://github.com/iRASPA/RASPA2) is installed in (_$RASPA_DIR/bin/simulate_ being the compiled executable).

## Input¶

The [RASPA](https://github.com/iRASPA/RASPA2) input is not easily wrapped into a [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") class because it does not know section endings and sections don’t have a common open/close statement. Like the other interfaces, the [RASPA](https://github.com/iRASPA/RASPA2) input file is generated using the `input` branch of the job settings. An example is given here:
[code] 
    settings = Settings()
    settings.input.simulationtype = 'MonteCarlo'
    settings.input.numberofcycles = 100
    settings.input.printevery = 10
    settings.input.forcefield = 'GenericMOFs'
    settings.input.usechargesfromciffile = True
    settings.input.framework._h = 0
    settings.input.framework.frameworkname = 'someMOF'
    settings.input.framework.unitcells = '4 4 4'
    settings.input.externaltemperature = 298.0
    settings.input.component['0'] = Settings()
    settings.input.component['0'].moleculename = 'helium'
    settings.input.component['0'].moleculedefinition = 'TraPPE'
    settings.input.component['0'].widomprobability = 1.0
    settings.input.component['0'].createnumberofmolecules = 0
    settings.input.component._1 = Settings()
    settings.input.component._1.moleculename = 'methane'
    settings.input.component._1.moleculedefinition = 'TraPPE'
    settings.input.component._1.widomprobability = 1.0
    settings.input.component._1.createnumberofmolecules = 0
    
[/code]

The input generated during the execution of the [RASPA](https://github.com/iRASPA/RASPA2) job is similar to:
[code] 
    numberofcycles 100
    printevery 10
    simulationtype MonteCarlo
    usechargesfromciffile yes
    
    componentexternaltemperature 298.0
    forcefield GenericMOFs
    framework 0
      frameworkname someMOF
      unitcells 4 4 4
    
    component 0 MoleculeName helium
      createnumberofmolecules 0
      moleculedefinition TraPPE
      widomprobability 1.0
    
    component 1 MoleculeName methane
      createnumberofmolecules 0
      moleculedefinition TraPPE
      widomprobability 1.0
    
[/code]

The _Component_ sections differ from the standard behaviour and are printed by the input parser as shown in this example. They can be inserted using the dictionary-like or dot-like notation as shown above. The `MoleculeName` key is obligatory.

As in other interfaces, the `_h` key results in the value being printed along the section title. No other special sections are defined.

If you need some files to be copied to the actual execution directory, pass them to the constructor using the `copy=` option. Alternatively you can symlink them using the `symlink=` option. See the API below.

## Molecule parsing¶

Molecule handling is not supported yet. Prepare the needed files and pass them to the constructor using the `copy` or `symlink` option.

For a more detailed description of the _RASPA_ input see the documentation in the [RASPA](https://github.com/iRASPA/RASPA2) GitHub repository.

## Loading jobs¶

Calculations done without PLAMS can be loaded using the [`load_external()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external") functionality. The `RaspaResults` class **does not** support reading input files into [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") objects yet.

Just do `RaspaJob.load_external(path)` to get use the job inside PLAMS.

## API¶

_class _`RaspaJob`(_copy =None_, _symlink =None_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaJob)¶
    
A single job with RASPA2 class.

Requires the ASE Python package.

Files that should be copied to the job directory can be passed as a dictionary using the `copy` argument. The dict should have the following layout: _dict[ <filename in jobdir>] = <path to file>_. If you prefer symlinks instead of copies use the `symlink` argument with the same layout. The path strings given to symlink are not altered. Remember that the job directory is not equal to the current work directory if using relative symlinks.

**Molecule parsing is not yet supported!**

The environment variable `$RASPA_DIR` needs to be set for the runscript to work.

`_result_type`¶
    
alias of `scm.plams.interfaces.thirdparty.raspa.RaspaResults`

`__init__`(_copy =None_, _symlink =None_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`_get_ready`()[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaJob._get_ready)¶
    
Copy files to execution dir if self.copy_files is set.

`get_input`()[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaJob.get_input)¶
    
Transform all contents of `settings.input` branch into string with blocks, keys and values.

RASPA2 does not interpret indentation but rather certain keys automatically start a subsection. Subsections are never closed but _automatically_ ended if the next key-value pair does not fit into it. So here we only need to care about readability of the input file. The logic is automatically preserved by using the nested PLAMS `settings` logic.

Components should be built using either `component['INT'] = Settings()` or `component._INT = Settings()`. It needs to have a key `moleculename` (case insensitive).

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaJob.get_runscript)¶
    
$RASPA_DIR has to be set in the environment!

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaJob.check)¶
    
Look for the normal termination signal in output.

_class _`RaspaResults`(_job_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaResults)¶
    
A Class for handling RASPA Results.

Note that the Output file is guessed in `self.collect`. Do not rely on it to point to the file you need and but check `self._filenames['out']`!

`collect`()[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaResults.collect)¶
    
Try to Guess the Main Output File.

Set it to whatever comes first in the ‘Output/System_0’ folder.

`get_block_value`(_search_ , _file =None_, _get_std =False_, _get_unit =False_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaResults.get_block_value)¶
    
Return a Block Value from Output File.

Can be used to retrieve block values from the final section of the output files. Uses Results.grep_file to retrieve the values. Remember to escape special grep characters in the search string. Returns the average value over all blocks.

search: string String labeling the value you desire.

file: string Defaults to the automatically detected output file. See self.collect().

get_std: boolean Also return the standard deviation of the value

get_unit: boolean Also return the unit of the value

`get_value`(_search_ , _file =None_, _get_std =False_, _get_unit =False_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaResults.get_value)¶
    
Return a Single Value from Output File.

Can be used to retrieve single values from the final section of the output files. Uses Results.grep_file to retrieve the values. Remember to escape special grep characters in the search string.

search: string String labeling the value you desire.

file: string Defaults to the automatically detected output file. See self.collect().

get_std: boolean Also return the standard deviation of the value

get_unit: boolean Also return the unit of the value

`get_from_all_files`(_* args_, _output_folder ='Output/System_0/'_, _method ='get_value'_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaResults.get_from_all_files)¶
    
Wrapper to Execute Methods on all Output files.

output_folder: string The subfolder containing the relevant output files. Default should be fine.

method: function The function to call, needs to be a function of the `RaspaResults` class that takes a _file_ argument. All _args_ and _kwargs_ are passed on.

If the _method_ returns tuples, the tuples are unpacked and added to lists.

`get_isotherm`(_output_folder ='Output/System_0/'_, _search_x ='Partial pressure:'_, _search_y ='Average loading excess \\\\[cm^3 (STP)/gr'_, _get_std =False_, _get_unit =False_)[[source]](../_modules/scm/plams/interfaces/thirdparty/raspa.html#RaspaResults.get_isotherm)¶
    
Try to automatically collect Isotherm Data.

output_folder: string The subfolder containing the relevant output files. Default should be fine.

search_x: string String labeling the desired x-Axis values in the output.

search_y: string String labeling the desired y-Axis values in the output.

get_std: boolean Return the standard deviation of the y values as a list.

get_unit: boolean Return the units of the values as strings x_unit, y_unit.

Returns two lists: x_values, y_values. Optionally after that x_std, x_unit, y_unit.

[Next ](vasp.html "VASP") [ Previous](orca.html "ORCA")

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
