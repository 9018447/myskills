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
  * [Components overview](components.html)
    * [Settings](settings.html)
    * [Jobs](jobs.html)
    * [Results](results.html)
    * [Job runners](runners.html)
    * [Job manager](jobmanager.html)
    * Public functions
      * Logging
      * Binding decorators
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
  * [Components overview](components.html)/
  * Public functions

# Public functions¶

This chapter gathers information about public functions that can be used in PLAMS scripts.

`init`(_path =None_, _folder =None_, _config_settings =None_, _quiet =False_, _use_existing_folder =False_)[[source]](../_modules/scm/plams/core/functions.html#init)¶
    
Initialize PLAMS environment. Create global `config` and the default [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager").

An empty [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance is created and populated with default settings by executing `plams_defaults`. The following locations are used to search for the defaults file, in order of precedence:

  * If `$PLAMSDEFAULTS` variable is in your environment and it points to a file, this file is used (executed as a Python script).

  * If `$AMSHOME` variable is in your environment and `$AMSHOME/scripting/scm/plams/plams_defaults` exists, it is used.

  * Otherwise, the path `../plams_defaults` relative to the current file (`functions.py`) is checked. If defaults file is not found there, an exception is raised.

Then a [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager") instance is created as `config.default_jobmanager` using _path_ and _folder_ to determine the main working folder. Settings for this instance are taken from `config.jobmanager`. If _path_ is not supplied, the current directory is used. If _folder_ is not supplied, `plams_workdir` is used. If _use_existing_folder_ is True and the working folder already exists, PLAMS will not create a new working folder with an incremental suffix (e.g. plams_workdir.002). Instead, it will just use the pre-existing folder (note: that this might lead to issues if the working folder is not empty).

Optionally, an additional dict (or [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance) can be provided to the config_settings argument which will be used to update the values from the `plams_defaults`.

Warning

This function **must** be called before any other PLAMS command can be executed. Trying to do anything without it results in a crash. See also [The launch script](../started.html#master-script).

`finish`(_otherJM =None_)[[source]](../_modules/scm/plams/core/functions.html#finish)¶
    
Wait for all threads to finish and clean the environment.

This function must be called at the end of your script for [Cleaning job folder](results.html#cleaning) to take place. See [The launch script](../started.html#master-script) for details.

If you used some other job managers than just the default one, they need to be passed as _otherJM_ list.

`load`(_filename_)[[source]](../_modules/scm/plams/core/functions.html#load)¶
    
Load previously saved job from `.dill` file. This is just a shortcut for [`load_job()`](jobmanager.html#scm.plams.core.jobmanager.JobManager.load_job "scm.plams.core.jobmanager.JobManager.load_job") method of the default [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager") `config.default_jobmanager`.

`load_all`(_path_ , _jobmanager =None_)[[source]](../_modules/scm/plams/core/functions.html#load_all)¶
    
Load all jobs from _path_.

This function works as multiple executions of [`load_job()`](jobmanager.html#scm.plams.core.jobmanager.JobManager.load_job "scm.plams.core.jobmanager.JobManager.load_job"). It searches for `.dill` files inside the directory given by _path_ , yet not directly in it, but one level deeper. In other words, all files matching `path/*/*.dill` are used. That way a path to the main working folder of a previously run script can be used to import all the jobs run by that script.

In case of partially failed [`MultiJob`](jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob") instances (some children jobs finished successfully, but not all) the function will search for `.dill` files in children folders. That means, if `path/[multijobname]/` contains some subfolders (for children jobs) but does not contail a `.dill` file (the [`MultiJob`](jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob") was not fully successful), it will look into these subfolders. This behavior is recursive up to any folder tree depth.

The purpose of this function is to provide a quick way of restarting a script. Loading all successful jobs from the previous run prevents double work and allows the new execution of the script to proceed directly to the place where the previous execution failed.

Jobs are loaded using default job manager stored in `config.default_jobmanager`. If you wish to use a different one you can pass it as _jobmanager_ argument of this function.

Returned value is a dictionary containing all loaded jobs as values and absolute paths to `.dill` files as keys.

`read_molecules`(_folder_ , _formats =None_)[[source]](../_modules/scm/plams/core/functions.html#read_molecules)¶
    
Read all molecules from _folder_.

Read all the files present in _folder_ with extensions compatible with [`Molecule.read`](mol_api.html#scm.plams.mol.molecule.Molecule.read "scm.plams.mol.molecule.Molecule.read"). Returned value is a dictionary with keys being molecule names (filename without extension) and values being [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instances.

The optional argument _formats_ can be used to narrow down the search to files with specified extensions:
[code] 
    molecules = read_molecules('mymols', formats=['xyz', 'pdb'])
    
[/code]

`read_all_molecules_in_xyz_file`(_filename_)[[source]](../_modules/scm/plams/core/functions.html#read_all_molecules_in_xyz_file)¶
    
The .xyz format allows to store multiple geometries on a single file (such file is essentially a concatenated series of xyz files)

This function returns a _list_ of all molecules found in the file _filename_

_filename_ : path (absolute or relative to the current working directory) to the xyz file.

## Logging¶

PLAMS features a simple logging mechanism. All important actions happening in functions and methods register their activity using log messages. These massages can be printed to the standard output and/or saved to the logfile located in the main working folder.

Every log message has its “verbosity” defined as an integer number: the higher the number, the more detailed and descriptive the message is. In other words, it is a measure of importance of the message. Important events (like “job started”, “job finished”, “something went wrong”) should have low verbosity, whereas less crucial ones (for example “pickling of job X successful”) – higher verbosity. The purpose of that is to allow the user to choose how verbose the whole logfile is. Each log output (either file or stdout) has an integer number associated with it, defining which messages are printed to this channel (for example, if this number is 3, all messages with verbosity 3 or less are printed). That way using a smaller number results in the log being short and containing only the most relevant information while larger numbers produce longer and more detailed log messages.

The behavior of the logging mechanism is adjusted by `config.log` settings branch with the following keys:

  * `file` (integer) – verbosity of logs printed to the `logfile` in the main working folder.

  * `stdout` (integer) – verbosity of logs printed to the standard output.

  * `time` (boolean) – print time of each log event.

  * `date` (boolean) – print date of each log event.

Log messages used within the PLAMS code use four different levels of verbosity:

  * **1** : important

  * **3** : normal

  * **5** : verbose

  * **7** : debug

Even levels are left empty for the user. For example, if you find level 5 too verbose and still want to be able to switch on and off log messages of your own code, you can log them with verbosity 4.

Note

Your own code can (and should) contain some `log()` calls. They are very important for debugging purposes.

`log`(_message_ , _level =0_)[[source]](../_modules/scm/plams/core/functions.html#log)¶
    
Log _message_ with verbosity _level_.

Logs are printed independently to the text logfile (a file called `logfile` in the main working folder) and to the standard output. If _level_ is equal or lower than verbosity (defined by `config.log.file` or `config.log.stdout`) the message is printed. Date and/or time can be added based on `config.log.date` and `config.log.time`. All logging activity is thread safe.

## Binding decorators¶

Sometimes one wants to expand the functionality of a class by adding a new method or modifying an existing one. It can be done in a few different ways:

  * One can go directly to the source code defining the class and modify it there before running a script. Such a change is global – it affects all the future scripts, so in most cases it is not a good thing (for defining [`prerun()`](jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun"), for example).

  * Creating a subclass with new or modified method definitions is usually the best solution. It can be done directly in your script before the work is done or in a separate dedicated file executed before the actual script (see [The launch script](../started.html#master-script)). Newly defined class can be then used instead of the old one. However, this solution fails in some rare cases when a method needs to differ for different instances or when it needs to be changed during the runtime of the script.

  * PLAMS binding decorators (`add_to_class()` and `add_to_instance()`) can be used.

Binding decorators allow to bind methods to existing classes or even directly to particular instances without having to define a subclass. Such changes are visible only inside the script in which they are used.

To fully understand how binding decorators work let us take a look at how Python handles method calling. Assume we have an instance of a class (let’s say `myres` is an instance of [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults")) and there is a method call in our script (let it be `myres.somemethod(arguments)`). Python first looks for `somemethod` amongst attributes of `myres`. If it is not there (which is usually the case, since methods are defined in classes), attributes of [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") class are checked. If `somemethod` is still not there, parent classes are checked in the order of inheritance (in our case it’s only [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results")). That implies two important things:

  * `add_to_instance()` affects only one particular instance, but is “stronger” than `add_to_class()` – method added to instance always takes precedence before the same method added to (or just defined in) a class

  * changes done with `add_to_class()` affect all instances of that particular class, including even those created before `add_to_class()` was used.

The usage of binding decorators is straightforward. You simply define a regular function somewhere inside your script and decorate it with one of the decorators (see below). The function needs to have a valid method syntax, so it should have `self` as the first argument and use it to reference the class instance.

`add_to_class`(_classname_)[[source]](../_modules/scm/plams/core/functions.html#add_to_class)¶
    
Add decorated function as a method to the whole class _classname_.

The decorated function should follow a method-like syntax, with the first argument `self` that references the class instance. Example usage:
[code] 
    @add_to_class(ADFResults)
    def get_energy(self):
        return self.readkf('Energy', 'Bond Energy')
    
[/code]

After executing the above code all instances of `ADFResults` in the current script (even the ones created beforehand) are enriched with `get_energy` method that can be invoked by:
[code] 
    someadfresults.get_energy()
    
[/code]

The added method is accessible also from subclasses of _classname_ so `@add_to_class(Results)` in the above example will work too.

If _classname_ is [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") or any of its subclasses, the added method will be wrapped with the thread safety guard (see [Synchronization of parallel job executions](results.html#parallel)).

`add_to_instance`(_instance_)[[source]](../_modules/scm/plams/core/functions.html#add_to_instance)¶
    
Add decorated function as a method to one particular _instance_.

The decorated function should follow a method-like syntax, with the first argument `self` that references the class instance. Example usage:
[code] 
    results = myjob.run()
    
    @add_to_instance(results)
    def get_energy(self):
        return self.readkf('Energy', 'Bond Energy')
    
    results.get_energy()
    
[/code]

The added method is accessible only for that one particular instance and it overrides any methods with the same name defined on a class level (in original class’ source) or added with `add_to_class()` decorator.

If _instance_ is an instance of [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") or any of its subclasses, the added method will be wrapped with the thread safety guard (see [Synchronization of parallel job executions](results.html#parallel)).

Technical

Each of the above decorators is in fact a decorator factory that, given an object (class or instance), produces a decorator that binds function as a method of that object. Both decorators are adding instance methods only, they cannot be used for static or class methods.

[Next ](molecule.html "Molecule") [ Previous](jobmanager.html "Job manager")

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
