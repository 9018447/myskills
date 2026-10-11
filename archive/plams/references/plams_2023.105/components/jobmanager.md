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
    * Job manager
      * Rerun prevention
      * Pickling
      * Restarting scripts
      * API
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
  * [Components overview](components.html)/
  * Job manager

# Job manager¶

Job manager is the “commander” of PLAMS environment. It creates the structure of the working folder, manages its contents, and keeps track of all jobs you run.

Every instance of `JobManager` is tied to a working folder. This folder is created when `JobManager` instance is initialized and all the jobs managed by that instance have their job folders inside the working folder. You should not change job manager’s working folder after it has been created.

When you initialize PLAMS environment with the [`init()`](functions.html#scm.plams.core.functions.init "scm.plams.core.functions.init") function, an instance of `JobManager` is created and stored in `config.default_jobmanager` This instance is tied to the main working folder (see [The launch script](../started.html#master-script) for details) and used as a default every time some interaction with a job manager is required. In a normal situation you would never explicitly interact with a `JobManager` instance (create it manually, call any of its methods, explore its data etc.). All interactions are handled automatically from [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") or other methods.

Technical

Usually there is no need to use any other job manager than the default one. Splitting work between multiple instances of `JobManager` may lead to some problems (different instances don’t communicate, so Rerun prevention does not work properly).

However, it is possible to manually create another instance of `JobManager` (with a different working folder) and use it for part of your jobs (by passing it as `jobmanager` keyword argument to [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run")). If you decide to do so, make sure to pass all instances of `JobManager` you manually created to [`finish()`](functions.html#scm.plams.core.functions.finish "scm.plams.core.functions.finish") (as a list).

An example application for that could be running jobs within your script on many different machines (for example via SSH) and having a separate `JobManager` on each of them.

## Rerun prevention¶

In some situations, for example when running many automatically generated small jobs, it may happen that two or more jobs are identical – they have the same input files. PLAMS has a built-in mechanism to detect such situations and avoid unnecessary work.

During [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run"), just before the actual job execution, a unique identifier (called _hash_) of a job is calculated. Job manager stores all hashes of previously started jobs and checks if the hash of the job you are just running has already occurred. If such a situation is detected, the execution of the current job is skipped and results of the previous job are used. Results from previous job’s folder can be either copied or linked to the current job’s folder, based on `link_files` key in **previous** job’s `settings`.

Note

Linking is done using hard links. Windows does not support hard links so if you are running PLAMS under Windows results are always copied.

The crucial part of the whole rerun prevention logic is a properly working [`hash()`](jobs.html#scm.plams.core.basejob.Job.hash "scm.plams.core.basejob.Job.hash") function. It is a function that takes the whole job instance and produces its hash. The hashing function needs to produce different hashes for different jobs and exactly the same hashes for jobs that do exactly the same work. It is far from trivial to come up with the scheme that works well for all kind of external binaries, since the technical details about job preparation can differ a lot. Currently implemented method works based on calculating SHA256 hash of input and/or runscript contents. The value of `hashing` key in job manager’s `settings` can be one of the following: `'input'`, `'runscript'`, `'input+runscript'` (or `None` to disable the rerun prevention).

If you decide to implement your own hashing method, it can be done by overriding [`hash_input()`](jobs.html#scm.plams.core.basejob.SingleJob.hash_input "scm.plams.core.basejob.SingleJob.hash_input") and/or meth:~scm.plams.core.basejob.SingleJob.hash_runscript.

Warning

It may happen that two jobs with the same input and runscript files correspond to different jobs (for example, if they rely on some external file that is supplied using relative path). Sometimes it’s even a desired behavior to run multiple different copies of the same job (for example, multiple MD trajectories with the same starting point and random initial velocities). If you are experiencing problems (PLAMS refuses to run a job, becasue it was already run in the past), you can disable the rerun prevention with `config.default_jobmanager.settings.hashing = None`.

Hashing is disabled for [`MultiJob`](jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob") instances since they don’t have inputs and runscripts. Of course single jobs that are children of multijobs are hashed in the normal way, so trying to run exactly the same multijob twice will not trigger rerun prevention on the multijob level, but rather for every children job separately, effectively preventing any doubled work.

## Pickling¶

The lifetime of the whole PLAMS environment is limited to a single script. That means every PLAMS script you run uses its own independent job manager, working folder and `config` settings. These objects are initialized at the beginning of the script with [`init()`](functions.html#scm.plams.core.functions.init "scm.plams.core.functions.init") command and they cease to exist when the script ends. Also all the settings adjustments (apart from those done by editing [Defaults file](../started.html#plams-defaults)) are local and they affect only the current script.

As a consequence of that, the `JobManager` of the current script is not aware of any jobs that had been run in past scripts. But often it would be very useful to import a previously run job to the current script and use its results or build some new jobs based on it. For that purpose PLAMS offers data preservation for job objects. Every time an execution of a job successfully finishes (see [Running a job](jobs.html#job-life-cycle)), the whole job object is saved to a `.dill` file using Python serialization called [`pickling`](https://docs.python.org/3.8/library/pickle.html#module-pickle "\(in Python v3.8\)"). Such a `.dill` file can be loaded (“unpickled”) in future scripts using [`load()`](functions.html#scm.plams.core.functions.load "scm.plams.core.functions.load") function:
[code] 
    oldjob = load('/home/user/science/plams_workdir/myjob/myjob.dill')
    
[/code]

This operation brings back the old [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance in (almost) the same state it was just after its execution finished.

Note

The default Python pickling package [`pickle`](https://docs.python.org/3.8/library/pickle.html#module-pickle "\(in Python v3.8\)") is not powerful enough to handle some of common PLAMS objects. Fortunately, the [dill](https://pypi.python.org/pypi/dill) package provides an excellent replacement for `pickle`, following the same interface and being able to save and load almost everything. It is strongly recommended to use `dill` to ensure proper work of PLAMS data preservation logic. However, if `dill` is not installed for the Python interpreter you’re using to run PLAMS, the regular `pickle` package will be used instead (which can work if your [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") objects are not too fancy, but in most cases it will probably fail). Please use `dill`, it’s free, easy to get and awesome.

The pickling mechanism follows references in pickled object. That means if an object you are trying to pickle contains a reference to another object (just like a [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance has a reference to a [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") instance), that other object is saved too. Thanks to that there are no “empty” references in your objects after unpickling. However, every [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance in PLAMS has a reference to a job manager, which in turns has references to all other jobs, so pickling one job would effectively mean pickling the whole environment. To avoid that, every [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance needs to be prepared for pickling by removing references to “global” objects, as well as some local attributes (path to the job folder for example). During loading, all the removed data is replaced with “proper” values (current job manager, current path to the job folder etc.).

Note

There is a way of expanding the mechanism explained above. If your [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") object has an attribute with reference to an object you don’t want to save together with the job, you may add this object’s name to job’s `_dont_pickle` list:
[code] 
    myjob.something = some_big_and_clumsy_object_you_dont_want_to_pickle
    myjob._dont_pickle.append('something')
    
[/code]

That way big clumsy object will not be stored in the `.dill` file. After loading such a `.dill` file the value of `myjob.something` will simply be `None`.

The `_dont_pickle` list is an attribute of every [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance, initially an empty list. It does not contain names of attributes that are always removed (like `jobmanager`), it’s meant only for additional ones defined by the user (see [`Job.__getstate__`](jobs.html#scm.plams.core.basejob.Job.__getstate__ "scm.plams.core.basejob.Job.__getstate__"))

As mentioned above, pickling a job happens at the very end of [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run"). The decision if a job should be pickled is based on the `pickle` key in job’s `settings`, so it can be adjusted for each job separately. If you wish not to pickle a particular job just set `myjob.settings.pickle = False`. Of course the global default `config.job.pickle` can also be used.

If you modify a job or its corresponding [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") instance after it has been pickler, these changes are not going to be reflected in the `.dill` file, since it was created before the changes happened. To update the state of the `.dill` file to include such changes you need to repickle the job manually by calling `myjob.pickle()` after doing your changes.

Note

Not all Python objects can be properly pickled, so you need to be careful what other objects your [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") (or its [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results")) store references to.

The [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") instance associated with the job is saved together with it. However, these results don’t contain all files produced by the job execution, but only relative paths to them. For that reason the `.dill` file is not enough to fully restore the job object if you want to extract or process the results. All other files present in the job folder are needed so that [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") instance can see them. So if you want to copy a previously run job to another location make sure to copy _the whole_ job folder (including subdirectories).

A job loaded with [`load()`](functions.html#scm.plams.core.functions.load "scm.plams.core.functions.load") is **not** registered in the current job manager. That means it does not get its own subfolder in the current working folder, it never gets renamed and no [Cleaning job folder](results.html#cleaning) is done on [`finish()`](functions.html#scm.plams.core.functions.finish "scm.plams.core.functions.finish"). However, it is added to the hash registry, so it is visible to Rerun prevention.

In case of a [`MultiJob`](jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob") all the information about children jobs is stored in parent’s `.dill` file so loading a [`MultiJob`](jobs.html#scm.plams.core.basejob.MultiJob "scm.plams.core.basejob.MultiJob") results in loading all its children. Each child job can have its own `.dill` file containing information about that particular job only. When pickling, the `parent` attribute of a job is erased, so loading a child job does not result in loading its parent (and all other children).

## Restarting scripts¶

Pickling and rerun prevention combine together into a handy restart mechanism. When your script tries to do something “illegal”, an exception is raised and the script gets terminated by the Python interpreter. Usually it is caused by a mistake in the script (a typo, using wrong variable, accessing wrong element of a list etc.). In such a case one would like to correct the script and run it again. But some jobs in the terminated script may had already been run and successfully finished before the exception occurred. It would be a waste of time to run those jobs again in the corrected script if they are meant to produce exactly the same results as previously. The solution is to load all successful jobs from the old script at the beginning of the new one and let Rerun prevention do the rest. But having to go to the old script’s working folder and manually get paths to all `.dill` files present there would be cumbersome. Fortunately, one can use [`load_all()`](functions.html#scm.plams.core.functions.load_all "scm.plams.core.functions.load_all") function which takes a path to the main working folder of some finished PLAMS run and loads all `.dill` files present there. So when you edit your crashed script to remove mistakes you can add just one [`load_all()`](functions.html#scm.plams.core.functions.load_all "scm.plams.core.functions.load_all") call at the beginning. Then you run your corrected script and no unnecessary work is done: all the finished jobs are loaded from the previous run, the current run tries to run the same jobs again, but Rerun prevention detects that and copies/links old jobs’ folders into the current main working folder.

If you’re executing your PLAMS scripts using the [The launch script](../started.html#master-script) restarting is even easier. It can be done in two ways:

  1. If you wish to perform the restart run in a fresh, empty working folder, all you need to do is to import the contents of the previous working folder (from the crashed run) using `-l` flag:
[code] plams myscript.plms
         [17:28:40] PLAMS working folder: /home/user/plams_workdir
         #[crashed]
         #[correct myscript.plms]
         plams -l plams_workdir myscript.plms
         [17:35:44] PLAMS working folder: /home/user/plams_workdir.002
         
[/code]

This is eqivalent to putting `load_all('plams_workdir')` at the top of `myscript.plms` and running it with the usual `plams myscript.plms`.

  2. If you would prefer an in-place restart in the same working folder, you can use `-r` flag:
[code] plams myscript.plms
         [17:28:40] PLAMS working folder: /home/user/plams_workdir
         #[crashed]
         #[correct myscript.plms]
         plams -r myscript.plms
         [17:35:44] PLAMS working folder: /home/user/plams_workdir
         
[/code]

In this case the launch script will temporarily move all the contents of `plams_workdir` to `plams_workdir.res`, import all the jobs from there and start a regular run in now empty `plams_workdir`.

Note

Please remember that rerun prevention checks the hash of the job after the [`prerun()`](jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method is executed. So when you attempt to run a job identical to the one previously run (in the same script, or imported from a previous run), its [`prerun()`](jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method is executed anyway, even if the rest of [Running a job](jobs.html#job-life-cycle) is skipped.

## API¶

_class _`JobManager`(_settings_ , _path =None_, _folder =None_, _use_existing_folder =False_)[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager)¶
    
Class responsible for jobs and files management.

Every instance has the following attributes:

  * `foldername` – the working folder name.

  * `workdir` – the absolute path to the working folder.

  * `logfile` – the absolute path to the logfile.

  * `input` – the absolute path to the copy of the input file in the working folder.

  * `settings` – a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance for this job manager (see below).

  * `jobs` – a list of all jobs managed with this instance (in order of [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") calls).

  * `names` – a dictionary with names of jobs. For each name an integer value is stored indicating how many jobs with that basename have already been run.

  * `hashes` – a dictionary working as a hash-table for jobs.

The _path_ argument should be be a path to a directory inside which the main working folder will be created. If `None`, the directory from where the whole script was executed is used.

The `foldername` attribute is initially set to the _folder_ argument. If such a folder already exists (and `use_existing_folder` is False), the suffix `.002` is appended to _folder_ and the number is increased (`.003`, `.004`…) until a non-existsing name is found. If _folder_ is `None`, the name `plams_workdir` is used, followed by the same procedure to find a unique `foldername`.

The `settings` attribute is directly set to the value of _settings_ argument (unlike in other classes where they are copied) and it should be a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance with the following keys:

  * `hashing` – chosen hashing method (see Rerun prevention).

  * `counter_len` – length of number appended to the job name in case of a name conflict.

  * `remove_empty_directories` – if `True`, all empty subdirectories of the working folder are removed on [`finish()`](functions.html#scm.plams.core.functions.finish "scm.plams.core.functions.finish").

`__init__`(_settings_ , _path =None_, _folder =None_, _use_existing_folder =False_)[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`load_job`(_filename_)[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager.load_job)¶
    
Load previously saved job from _filename_.

_Filename_ should be a path to a `.dill` file in some job folder. A [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance stored there is loaded and returned. All attributes of this instance removed before pickling are restored. That includes `jobmanager`, `path` (the absolute path to the folder containing _filename_ is used) and `default_settings` (a list containing only `config.job`).

See Pickling for details.

`remove_job`(_job_)[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager.remove_job)¶
    
Remove _job_ from the job manager. Forget its hash.

`_register`(_job_)[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager._register)¶
    
Register the _job_. Register job’s name (rename if needed) and create the job folder.

If a job with the same name was already registered, _job_ is renamed by appending consecutive integers. The number of digits in the appended number is defined by the `counter_len` value in `settings`. Note that jobs whose name already contains a counting suffix, e.g. `myjob.002` will have the suffix stripped as the very first step.

`_check_hash`(_job_)[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager._check_hash)¶
    
Calculate the hash of _job_ and, if it is not `None`, search previously run jobs for the same hash. If such a job is found, return it. Otherwise, return `None`

`_clean`()[[source]](../_modules/scm/plams/core/jobmanager.html#JobManager._clean)¶
    
Clean all registered jobs according to the `save` parameter in their `settings`. If `remove_empty_directories` is `True`, traverse the working directory and delete all empty subdirectories.

[Next ](functions.html "Public functions") [ Previous](runners.html "Job runners")

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
