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
    * Jobs
      * Preparing a job
        * Contents of job settings
        * Default settings
      * Running a job
        * Name conflicts
        * Prerun and postrun methods
        * Preview mode
      * Job API
      * Single jobs
        * Subclassing SingleJob
      * Multijobs
        * Using MultiJob
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
  * [Components overview](components.html)/
  * Jobs

# Jobs¶

The `Job` class is undoubtedly the most important object in PLAMS. Job is the basic piece of computational work and running jobs is the main goal of PLAMS scripts.

Various jobs may differ in details quite a lot, but they all follow the same set of common rules defined in the abstract class `Job`.

Note

Being an abstract class means that the `Job` class has some abstract methods – methods that are declared but not implemented (they do nothing). Those methods are supposed to be defined in subclasses of `Job`. When a subclass of an abstract class defines all required abstract methods, it is called a _concrete class_. You should never create an instance of an abstract class, because when you try to use it, empty abstract methods are called and your script crashes.

See also

The [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") class handles AMS jobs.

Every job has its own unique name and a separate folder (called the job folder, with the same name as the job) located in the main working folder. All files regarding that particular job (input, output, runscript, other files produced by the job execution) end up in the job folder.

In general, a job can be of one of two types: a _single job_ or a _multijob_. These types are defined as subclasses of the `Job` class: `SingleJob` and `MultiJob`.

Single job is a job representing a single calculation, usually done by executing an external binary (ADF, Dirac etc.). Single job creates a _runscript_ (which is usually just a shell script) that is then either executed locally or submitted to some external queueing system. As a result of running a single job multiple files are created, including dumps of the standard output and standard error streams, together with any other files produced by that external binary. `SingleJob` is still an abstract class that is further subclassed by program-specific concrete classes like for example [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob").

Multijob, on the other hand, does not run any calculation by itself. It is a container for other jobs, used to aggregate smaller jobs into bigger ones. There is no runscript produced by a multijob. Instead, it contains a list of subjobs called _children_ that are run together when the parent job is executed. Children jobs can in turn be either single or multijobs. Job folder of each child job is a subfolder of its parent’s folder, so the folder hierarchy on the filesystem reflects the child-parent hierarchy of jobs. `MultiJob` is a concrete class so you can create its instances and run them.

## Preparing a job¶

The first step to run a job using PLAMS is to create a `Job` instance. You need to pick a concrete class that defines a type of job you want to run ([`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") will be used as an example in our case) and create its instance:
[code] 
    myjob = AMSJob(name='myfirstjob')
    
[/code]

Various _keyword arguments_ (arguments of the form `arg=value`, like `name` in the example above) can be passed to a job constructor, depending on the type of your job. The following keyword arguments are common for all types of jobs:

  * `name` – a string containing the name of the job. If not supplied, default name `plamsjob` is used. Job name cannot contain path separator (`\` in Linux, `/` in Windows).

  * `settings` – a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance to be used by this job. It gets copied (using [`copy()`](settings.html#scm.plams.core.settings.Settings.copy "scm.plams.core.settings.Settings.copy")) so you can pass the same instance to several different jobs and changes made afterwards won’t interfere. Any instance of `Job` can be also passed as a value of this argument. In that case [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") associated with the passed job are copied.

  * `depend` – a list of jobs that need to be finished before this job can start. This is useful when you want to execute your jobs in parallel. Usually there is no need to use this argument, since dependencies between jobs are resolved automatically (see [Synchronization of parallel job executions](results.html#parallel)). However, sometimes one needs to explicitly specify such a dependency and `depend` option is meant for that.

Those values do not need to be passed to the constructor, they can be set or changed later (but they should be fixed before the job starts to run):
[code] 
    myjob = AMSJob()
    myjob.name = 'myfirstjob'
    myjob.settings.runscript.pre = 'echo HelloWorld'
    
[/code]

Single jobs can be supplied with another keyword argument, `molecule`. It is supposed to be a [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object. Multijobs, in turn, accept a keyword argument `children` that stores the collection of children jobs (usually a list or a dictionary).

The most meaningful part of each job object is its [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance. It is used to store information about contents of the input file and the runscript as well as other tweaks of job’s behavior. Thanks to the tree-like structure of [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") this information is organized in a convenient way: the top level (`myjob.settings`) stores general settings, `myjob.settings.input` is a branch for specifying input settings, `myjob.settings.runscript` holds information for runscript creation and so on. Some types of jobs will make use of their own `myjob.settings` branches and not every kind of job will require `input` or `runscript` branches (like multijob for example). The nice thing is that all the unnecessary data present in job settings is simply ignored, so accidentally plugging settings with too much data will not cause any problem (except some cases where the whole content of some branch is used, like for example the `input` branch in [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob")).

### Contents of job settings¶

The following keys and branches of job settings are meaningful for all kinds of jobs:

  * `myjob.settings.input` is a branch storing settings regarding input file of a job. The way in which the data present in `input` branch is used depends on the type of job and is specified in respective subclasses of `Job`.

  * `myjob.settings.runscript` holds runscript information, either program-specific or general:

    * `myjob.settings.runscript.shebang` – the first line of the runscript, starting with `#!`, describing an interpreter to use

    * `myjob.settings.runscript.pre` – an arbitrary string that will be placed in the runscript file just below the shebang line, before the actual contents

    * `myjob.settings.runscript.post` – an arbitrary string to put at the end of the runscript

    * `myjob.settings.runscript.stdout_redirect` – boolean flag defining if standard output redirection should be handled inside the runscript. If set to `False`, the redirection will be done by Python from outside the runscript. If set to `True`, standard output will be redirected inside the runscript using `>`

  * `myjob.settings.run` branch stores run flags for the job. Run flags is a flat collection of key-value pairs that are used by [`GridRunner`](runners.html#scm.plams.core.jobrunner.GridRunner "scm.plams.core.jobrunner.GridRunner") to construct a command used to submit the runscript to a queueing system (like, for example, number of nodes/cores or size of the memory used with `qsub` or `sbatch`)

  * `myjob.settings.keep` and `myjob.settings.save` are keys adjusting [Cleaning job folder](results.html#cleaning).

  * `myjob.settings.pickle` is a boolean value defining if the job object should be pickled after finishing (see [Pickling](jobmanager.html#pickling))

  * `myjob.settings.link_files` is a boolean value defining if files from the job folder can be linked rather than copied when copying is requested

### Default settings¶

Every job instance has an attribute called `default_settings` that stores a list of [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instances that serve as default templates for that job. Initially that list contains only one element, the global defaults for all jobs stored in `config.job`. You can add other templates by simply adding new elements to that list:
[code] 
    myjob.default_settings.append(sometemplate)
    myjob.default_settings += [temp1, temp2]
    
[/code]

During job execution, just after `prerun()` method is finished, job’s own `settings` are soft-updated with all elements of `default_settings` list, one by one, starting with the **last** one. That way, if you want to adjust some setting for all jobs present in your script, you don’t need to do it for each job separately, one change in `config.job` is enough. Similarly, if you have a group of jobs that need the same `settings` adjustments, you can create an empty [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance, put those adjustments in it and add it to each job’s `default_settings`. Keep in mind that [`soft_update()`](settings.html#scm.plams.core.settings.Settings.soft_update "scm.plams.core.settings.Settings.soft_update") is used here, so a key in a template in `default_settings` will end up in job’s final `settings` only if such a key is not yet present there. Thanks to that the order of templates in `default_settings` corresponds to their importance. The data from an “earlier” template will never override the data from a “later” one, it can only enrich it. In the example below:
[code] 
    s = Settings()
    s.input.ams.Task = 'SinglePoint'
    s.input.ams.UseSymmetry = 'True'
    t = Settings()
    t.input.ams.Task = 'GeometryOptimization'
    myjob = AMSJob(...)
    myjob.default_settings += [s,t]
    myjob.run()
    
[/code]

`Task SinglePoint` from `s` becomes replaced by `Task GeometryOptimization` from `t`, but `UseSymmetry True` from `s` stays and ends up in the final settings of `myjob`.

## Running a job¶

After creating a `Job` instance and adjusting its settings you can finally run it. It is done by invoking the `run()` method, which returns a [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") object:
[code] 
    myresults = myjob.run()
    
[/code]

(the [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") object can be also accessed as `myjob.results`). Various keyword arguments can be passed to `run()`. With `jobrunner` and `jobmanager` you can specify which [`JobRunner`](runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") and [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager") to use for your job. If those arguments are omitted, the default instances stored in `config.default_jobrunner` and `config.default_jobmanager` are taken. All other keyword arguments are collected and stored in `myjob.settings.run` branch of job settings, as one flat level. They can be used later by various objects involved in running your job, for example [`GridRunner`](runners.html#scm.plams.core.jobrunner.GridRunner "scm.plams.core.jobrunner.GridRunner") uses them to build the command executed to submit the runscript to the queueing system.

The following steps are taken after the `run()` method is called:

  1. `myjob.settings.run` is **soft-updated** with `run()` keyword arguments (so a `run()` argument will never override anything already present in `myjob.settings.run`).

  2. If a parallel [`JobRunner`](runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") was used, a new thread is spawned and all further steps of this list happen in that thread.

  3. Explicit dependencies from `myjob.depend` are resolved. This means waiting for all jobs listed in `depend` to finish.

  4. Job name gets registered in the job manager and the job folder is created. If a job with the same name has been registered before, a new unique name is created.

  5. Job’s `prerun()` method is called.

  6. `myjob.settings` are updated with the contents of `myjob.default_settings` (see Default settings).

  7. The hash of a job is calculated and checked (see [Rerun prevention](jobmanager.html#rerun-prevention)). If the same job was found as previously run, its results are copied (or linked) to the current job’s folder and `run()` method finishes.

  8. Now the real job execution happens. If the job is a single job, an input file and a runscript are created and passed to job runner’s method [`call()`](runners.html#scm.plams.core.jobrunner.JobRunner.call "scm.plams.core.jobrunner.JobRunner.call"). If the job is a multijob, `run()` method is called for all children jobs.

  9. After the execution is finished, result files produced by the job are collected and `check()` is used to test if the execution was successful.

  10. The job folder is cleaned using `myjob.settings.keep`. See [Cleaning job folder](results.html#cleaning) for details.

  11. Job’s `postrun()` method is called.

  12. If `myjob.settings.pickle` is set to `True`, the whole job instance gets pickled and saved to the `[jobname].dill` file in the job folder. See [Pickling](jobmanager.html#pickling) for details

### Name conflicts¶

Jobs are identified by their names, so names need to be unique. This is necessary also because job name corresponds to the name of its folder. Usually it is recommended to manually set unique names of your jobs (via `name` argument of job constructor) for easier navigation through results. But for some applications, especially the ones requiring running large numbers of similar jobs, this would be very cumbersome.

PLAMS automatically resolves conflicts between job names. During step 4. of the above list, if a job with the same name was already registered, the current job is renamed. The new name is created by appending some number to the old name. For example, the second job with the name `plamsjob` will be renamed to `plamsjob.002`, third to `plamsjob.003` and so on. Number of digits used in this counter can be adjusted via `config.jobmanager.counter_len` and the default value is 3. Overflowing the counter will not cause any problems, the job coming after `plamsjob.999` will be called `plamsjob.1000`.

### Prerun and postrun methods¶

`prerun()` and `postrun()` methods are intended for further customization of your jobs. They can contain arbitrary pieces of code that are executed, respectively, before or after the actual execution of your job.

`prerun()` method is run after the job folder is created but before hash checking. Here are some ideas what can be put there:

  * adjusting job settings

  * copying to the job folder some files required for the execution

  * extracting results of some other job, processing them and plugging to the current job (for example, extracting optimized geometry from a previous geometry optimization)

  * generating children jobs in multijobs

See also [Synchronization of parallel job executions](results.html#parallel) for an explanation on how to use `prerun()` to automatically handle dependencies in parallel workflows.

The other method, `postrun()`, is called after job execution is finished, the results are collected and the job folder is cleaned. It is supposed to contain any kind of essential results postprocessing that needs to be done before results of this job can be pushed further in the workflow. For that purpose code contained in `postrun()` has some special privileges. At the time the method is executed the job is not yet considered done, so all threads requesting its results are waiting. However, the guardian restricting the access to results of unfinished jobs can recognize code coming from `postrun()` and allow it to access and modify results. Thanks to that calling [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") methods can be safely done in `postrun()` and you can be sure that everything that happens in `postrun()` is done before other jobs have access to the final job’s results.

`prerun()` and `postrun()` methods can be added to your jobs in multiple ways:

  * you can create a tiny subclass which redefines the method:
[code] class MyJobWithPrerun(MyJob):
            def prerun(self):
                #do stuff
        
[/code]

It can be done right inside you script. After the above definition you can create instances of the new class and treat them in exactly the same way you would treat `MyJob` instances. The only difference is that they will be equipped with `prerun()` method you just defined.

  * you can bind the method to an existing class using [`add_to_class()`](functions.html#scm.plams.core.functions.add_to_class "scm.plams.core.functions.add_to_class") decorator:
[code] @add_to_class(MyJob)
        def prerun(self):
            #do stuff
        
[/code]

That change affects all instances of `MyJob`, even those created before the above code was executed (obviously it won’t affect instances previously run and finished).

  * you can bind the method directly to an instance using [`add_to_instance()`](functions.html#scm.plams.core.functions.add_to_instance "scm.plams.core.functions.add_to_instance") decorator:
[code] j = MyJob(...)
        @add_to_instance(j)
        def prerun(self):
            #do stuff
        
[/code]

In that case, only one specified instance `j` is affected with the new `prerun()`.

All the above works for `postrun()` as well.

### Preview mode¶

Preview mode is a special way of running jobs without the actual runscript execution. In this mode the procedure of running a job is interrupted just after input and runscript files are written to the job folder. Preview mode can be used to check if your jobs generate proper input and runscript files, without having to run the full calculation.

You can enable the preview mode by putting the following line at the beginning of your script:
[code] 
    config.preview = True
    
[/code]

## Job API¶

_class _`Job`(_name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/core/basejob.html#Job)¶
    
General abstract class for all kind of computational tasks.

Methods common for all kinds of jobs are gathered here. Instances of `Job` should never be created. It should not be subclassed either. If you wish to define a new type of job please subclass either `SingleJob` or `MultiJob`.

Methods that are meant to be explicitly called by the user are `run()` and occasionally `pickle()`. In most cases [Pickling](jobmanager.html#pickling) is done automatically, but if for some reason you wish to do it manually, you can use `pickle()` method.

Methods that can be safely overridden in subclasses are:

  * `check()`

  * `hash()` (see [Rerun prevention](jobmanager.html#rerun-prevention))

  * `prerun()` and `postrun()` (see Prerun and postrun methods)

All other methods should remain unchanged.

Class attribute `_result_type` defines the type of results associated with this job. It should point to a class and it **must** be a [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass.

Every job instance has the following attributes:

Attributes adjusted automatically that should not be changed by the user:

  * `status` – current status of the job. Possible values: _created_ , _started_ , _registered_ , _running_ , _finished_ , _crashed_ , _failed_ , _successful_ , _copied_ , _preview_.

  * `results` – a reference to a results instance. An empty instance of the type stored in `_result_type` is created when the job object is created.

  * `path` – an absolute path to the job folder.

  * `jobmanager` – a job manager associated with this job.

  * `parent` – a pointer to the parent job if this job is a child job of some `MultiJob`. `None` otherwise.

Attributes that can be modified, but only before `run()` is called:

  * `name` – the name of the job.

  * `settings` – settings of the job.

  * `default_settings` – see Default settings.

  * `depend` – a list of explicit dependencies.

  * `_dont_pickle` – additional list of this instance’s attributes that will be removed before pickling. See [Pickling](jobmanager.html#pickling) for details.

`__init__`(_name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/core/basejob.html#Job.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`run`(_jobrunner =None_, _jobmanager =None_, _** kwargs_)[[source]](../_modules/scm/plams/core/basejob.html#Job.run)¶
    
Run the job using _jobmanager_ and _jobrunner_ (or defaults, if `None`). Other keyword arguments (_**kwargs_) are stored in `run` branch of job’s settings. Returned value is the [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") instance associated with this job.

Warning

This method should **not** be overridden.

Technical

This method does not do too much by itself. After some initial preparation it passes control to the job runner, which decides if a new thread should be started for this job. The role of the job runner is to execute three methods that make the full job life cycle: `_prepare()`, `_execute()` and `_finalize()`. During `_execute()` the job runner is called once again to execute the runscript (only in case of `SingleJob`).

`pickle`(_filename =None_)[[source]](../_modules/scm/plams/core/basejob.html#Job.pickle)¶
    
Pickle this instance and save to a file indicated by _filename_. If `None`, save to `[jobname].dill` in the job folder.

`ok`(_strict =True_)[[source]](../_modules/scm/plams/core/basejob.html#Job.ok)¶
    
Check if the execution of this instance was successful. If needed, wait for the job to finish and then check if the status is _successful_ (or _copied_).

If this method is called before job’s `run()` method, a warning is logged and the returned value is `False`. The most likely cause of such a behavior is simply forgetting about `run()` call. However, in complicated workflows executed in parallel, it can sometimes naturally happen that one thread is ahead of others and calls `ok()` before some other thread has a chance to call `run()`. If you’re experiencing that kind of problems, please consider using `strict=False` to skip the `run()` check. But keep in mind that skipping that check will deadlock the current thread if `run()` never gets called.

`check`()[[source]](../_modules/scm/plams/core/basejob.html#Job.check)¶
    
Check if the execution of this instance was successful. Abstract method meant for internal use.

`hash`()[[source]](../_modules/scm/plams/core/basejob.html#Job.hash)¶
    
Calculate the hash of this instance. Abstract method meant for internal use.

`prerun`()[[source]](../_modules/scm/plams/core/basejob.html#Job.prerun)¶
    
Actions to take before the actual job execution.

This method is initially empty, it can be defined in subclasses or directly added to either the whole class or a single instance using [Binding decorators](functions.html#binding-decorators).

`postrun`()[[source]](../_modules/scm/plams/core/basejob.html#Job.postrun)¶
    
Actions to take just after the actual job execution.

This method is initially empty, it can be defined in subclasses or directly added to either the whole class or a single instance using [Binding decorators](functions.html#binding-decorators).

`_prepare`(_jobmanager_)[[source]](../_modules/scm/plams/core/basejob.html#Job._prepare)¶
    
Prepare the job for execution. This method collects steps 1-7 from Running a job. Should not be overridden. Returned value indicates if job execution should continue ([Rerun prevention](jobmanager.html#rerun-prevention) did not find this job as previously run).

`_get_ready`()[[source]](../_modules/scm/plams/core/basejob.html#Job._get_ready)¶
    
Get ready for `_execute()`. This is the last step before `_execute()` is called. Abstract method.

`_execute`(_jobrunner_)[[source]](../_modules/scm/plams/core/basejob.html#Job._execute)¶
    
Execute the job. Abstract method.

`_finalize`()[[source]](../_modules/scm/plams/core/basejob.html#Job._finalize)¶
    
Gather the results of the job execution and organize them. This method collects steps 9-12 from Running a job. Should not be overridden.

`__getstate__`()[[source]](../_modules/scm/plams/core/basejob.html#Job.__getstate__)¶
    
Prepare this job instance for pickling.

Attributes `jobmanager`, `parent`, `default_settings` and `_lock` are removed, as well as all attributes listed in `self._dont_pickle`.

`_log_status`(_level_)[[source]](../_modules/scm/plams/core/basejob.html#Job._log_status)¶
    
Log the status of this instance on a chosen log _level_. The message is uppercased to clearly stand out among other log entries.

## Single jobs¶

_class _`SingleJob`(_molecule =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/core/basejob.html#SingleJob)¶
    
Abstract class representing a job consisting of a single execution of some external binary (or arbitrary shell script in general).

In addition to constructor arguments and attributes defined by `Job`, the constructor of this class accepts the keyword argument `molecule` that should be a [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance. The constructor creates a copy of the supplied [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") and stores it as the `molecule` attribute.

Class attribute `_filenames` defines default names for input, output, runscript and error files. If you wish to override this attribute it should be a dictionary with string keys `'inp'`, `'out'`, `'run'`, `'err'`. The value for each key should be a string describing corresponding file’s name. Shortcut `$JN` can be used for job’s name. The default value is defined in the following way:
[code] 
    _filenames = {'inp':'$JN.in', 'run':'$JN.run', 'out':'$JN.out', 'err': '$JN.err'}
    
[/code]

This class defines no new methods that could be directly called in your script. Methods that can and should be overridden are `get_input()` and `get_runscript()`.

`__init__`(_molecule =None_, _** kwargs_)[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`get_input`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.get_input)¶
    
Generate the input file. Abstract method.

This method should return a single string with the full content of the input file. It should process information stored in the `input` branch of job settings and in the `molecule` attribute.

`get_runscript`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.get_runscript)¶
    
Generate the runscript. Abstract method.

This method should return a single string with the runscript contents. It can process information stored in `runscript` branch of job settings. In general the full runscript has the following form:
[code] 
    [first line defined by job.settings.runscript.shebang]
    
    [contents of job.settings.runscript.pre, when present]
    
    [value returned by get_runscript()]
    
    [contents of job.settings.runscript.post, when present]
    
[/code]

When overridden, this method should pay attention to `.runscript.stdout_redirect` key in job’s `settings`.

`hash_input`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.hash_input)¶
    
Calculate SHA256 hash of the input file.

`hash_runscript`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.hash_runscript)¶
    
Calculate SHA256 hash of the runscript.

`hash`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.hash)¶
    
Calculate unique hash of this instance.

The behavior of this method is adjusted by the value of `hashing` key in [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager") settings. If no [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager") is yet associated with this job, default setting from `config.jobmanager.hashing` is used.

Methods `hash_input()` and `hash_runscript()` are used to obtain hashes of, respectively, input and runscript.

Currently supported values for `hashing` are:

  * `False` or `None` – returns `None` and disables [Rerun prevention](jobmanager.html#rerun-prevention).

  * `input` – returns the hash of the input file.

  * `runscript` – returns the hash of the runscript.

  * `input+runscript` – returns SHA256 hash of the concatenation of **hashes** of input and runscript.

`check`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.check)¶
    
Check if the calculation was successful.

This method can be overridden in concrete subclasses of `SingleJob`. It should return a boolean value. The definition here serves as a default, to prevent crashing if a subclass does not define its own `check()`. It always returns `True`.

Warning

This method is meant for internal usage and **should not** be explicitly called in your script (but it can be overridden in subclasses). Manually calling `check()` is not thread safe. For a thread safe function to evaluate the state of your job please use `ok()`

`full_runscript`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.full_runscript)¶
    
Generate the full runscript, including shebang line and contents of `pre` and `post`, if any. In practice this method is just a simple wrapper around `get_runscript()`.

`_get_ready`()[[source]](../_modules/scm/plams/core/basejob.html#SingleJob._get_ready)¶
    
Create input and runscript files in the job folder. Methods `get_input()` and `full_runscript()` are used for that purpose. Filenames correspond to entries in the _filenames attribute

`_execute`(_jobrunner_)[[source]](../_modules/scm/plams/core/basejob.html#SingleJob._execute)¶
    
Execute previously created runscript using _jobrunner_.

The method [`call()`](runners.html#scm.plams.core.jobrunner.JobRunner.call "scm.plams.core.jobrunner.JobRunner.call") of _jobrunner_ is used. Working directory is `self.path`. `self.settings.run` is passed as `runflags` argument.

If preview mode is on, this method does nothing.

_classmethod _`load`(_path_ , _jobmanager =None_, _strict =True_)[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.load)¶
    
Loads a Job instance from path, where path can either be a directory with a *.dill file, or the full path to the *.dill file. If `init()` has been called, or a non-default jobmanager is provided, will register the job with the Job Manager.

When strict = True, will check that the loaded job is an instance of the right class (e.g. calling AMSJob.load() returns a AMSJob instance) and raise a ValueError if the check fails. Setting strict = False disables the check, allowing for signatures such as SingleJob.load() -> AMSJob.

_classmethod _`load_external`(_path_ , _settings =None_, _molecule =None_, _finalize =False_)[[source]](../_modules/scm/plams/core/basejob.html#SingleJob.load_external)¶
    
Load an external job from _path_.

In this context an “external job” is an execution of some external binary that was not managed by PLAMS, and hence does not have a `.dill` file. It can also be used in situations where the execution was started with PLAMS, but the Python process was terminated before the execution finished, resulting in steps 9-12 of Running a job not happening.

All the files produced by your computation should be placed in one folder and _path_ should be the path to this folder or a file in this folder. The name of the folder is used as a job name. Input, output, error and runscript files, if present, should have names defined in `_filenames` class attribute (usually `[jobname].in`, `[jobname].out`, `[jobname].err` and `[jobname].run`). It is not required to supply all these files, but in most cases one would like to use at least the output file, in order to use methods like [`grep_output()`](results.html#scm.plams.core.results.Results.grep_output "scm.plams.core.results.Results.grep_output") or [`get_output_chunk()`](results.html#scm.plams.core.results.Results.get_output_chunk "scm.plams.core.results.Results.get_output_chunk").

This method is a class method, so it is called via class object and it returns an instance of that class:
[code] 
    >>> j = SingleJob.load_external(path='some/path/jobname')
    >>> type(j)
    scm.plams.core.basejob.SingleJob
    >>> a = AMSJob.load_external(path='some/path/jobname')
    >>> type(a)
    scm.plams.interfaces.adfsuite.ams.AMSJob
    
[/code]

You can supply [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") and [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instances as _settings_ and _molecule_ parameters, they will end up attached to the returned job instance. If you don’t do this, PLAMS will try to recreate them automatically using methods [`recreate_settings()`](results.html#scm.plams.core.results.Results.recreate_settings "scm.plams.core.results.Results.recreate_settings") and [`recreate_molecule()`](results.html#scm.plams.core.results.Results.recreate_molecule "scm.plams.core.results.Results.recreate_molecule") of the corresponding [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass. If no [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance is obtained in either way, the defaults from `config.job` are copied.

You can set the _finalize_ parameter to `True` if you wish to run the whole `_finalize()` on the newly created job. In that case PLAMS will perform the usual `check()` to determine the job status (_successful_ or _failed_), followed by cleaning of the job folder ([Cleaning job folder](results.html#cleaning)), `postrun()` and pickling ([Pickling](jobmanager.html#pickling)). If _finalize_ is `False`, the status of the returned job is _copied_.

### Subclassing SingleJob¶

`SingleJob` class was designed in a way that makes subclassing it quick and easy. Thanks to that it takes very little effort to create a PLAMS interface for new external binary.

Your new class has to, of course, be a subclass of `SingleJob` and define methods `get_input()` and `get_runscript()`:
[code] 
    class MyJob(SingleJob):
        def get_input(self):
            ...
            return 'string with input file'
        def get_runscript(self):
            ...
            return 'string with runscript'
    
[/code]

Note

`get_runscript()` method should properly handle output redirection based on the value of `myjob.settings.runscript.stdout_redirect`. When `False`, no redirection should occur inside the runscript. If `True`, the runscript should be constructed in such a way that the standard output is redirected (using `>`) to the output file, which name can be accessed as `self._filename('out')`.

This is sufficient for your new job to work properly with other PLAMS components. However, there are other useful attributes and methods that can be overridden:

  * `check()` – the default version of this method defined in `SingleJob` always returns `True` and hence disables any correctness checking. If you wish to enable checking for your new class, you need to define `check()` method in it, just like `get_input()` and `get_runscript()` in the example above. It should take no other arguments than `self` and return a boolean value indicating if the job execution was successful. This method is privileged to have an early access to [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") methods in exactly the same way as `postrun()`.

  * if you wish to create a special [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") subclass for results of your new job, make sure to let the job know about it:
[code] class MyResults(Results):
            def get_some_results(self, ...):
                ...
        
        class MyJob(SingleJob):
            _result_type = MyResults
            def get_input(self):
                ...
                return 'string with input file'
            def get_runscript(self):
                ...
                return 'string with runscript'
        
[/code]

  * `hash_input()` and `hash_runscript()` – see [Rerun prevention](jobmanager.html#rerun-prevention) for details.

  * if your new job requires some special preparations regarding input or runscript files these preparations can be done for example in `prerun()`. However, if you wish to leave `prerun()` clean for further subclassing or adjusting in instance-based fashion, you can use another method called `_get_ready()`. This method is responsible for input and runscript creation, so if you decide to override it you **must** call its parent version in your new version:
[code] def _get_ready(self):
            # do some stuff
            SingleJob._get_ready()
            # do some other stuff
        
[/code]

Warning

Whenever you are subclassing any kind of job, either single of multi, and you wish to override its constructor (`__init__` method) it is **absolutely essential** to call the parent constructor and pass all unused keyword arguments to it:
[code] 
    class MyJob(SingleJob):
        def __init__(self, myarg1, myarg2=default2, **kwargs):
            SingleJob.__init__(self, **kwargs)
            # do stuff with myarg1 and myarg2
    
[/code]

Technical

Usually when you need to call some method from a parent class it is a good idea to use [`super()`](https://docs.python.org/3.8/library/functions.html#super "\(in Python v3.8\)"). However, there exists a known bug in Python 3 that causes the `dill` package to crash when [`super()`](https://docs.python.org/3.8/library/functions.html#super "\(in Python v3.8\)") is used. For that reason please do not use [`super()`](https://docs.python.org/3.8/library/functions.html#super "\(in Python v3.8\)").

## Multijobs¶

_class _`MultiJob`(_children =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/core/basejob.html#MultiJob)¶
    
Concrete class representing a job that is a container for other jobs.

In addition to constructor arguments and attributes defined by `Job`, the constructor of this class accepts two keyword arguments:

  * `children` – iterable container with children jobs (usually a list or a dictionary).

  * `childrunner` – by default all the children jobs are run using the same [`JobRunner`](runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") as the parent job. If you wish to use a different [`JobRunner`](runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") for children, you can pass it using `childrunner`.

Values passed as `children` and `childrunner` are stored as instance attributes and can be adjusted later, but before the `run()` method is called.

This class defines no new methods that could be directly called in your script.

When executed, a multijob runs all its children using the same [`JobManager`](jobmanager.html#scm.plams.core.jobmanager.JobManager "scm.plams.core.jobmanager.JobManager") and [`JobRunner`](runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") (unless `childrunner` is set). If you need to specify different run flags for children you can do it by manually setting them in child job settings:
[code] 
    childjob = myjob.children[0]
    childjob.settings.run.arg = 'value'
    
[/code]

Since the `run` branch of settings gets soft-updated with run flags, the value set this way is not overwritten by parent job.

The job folder of a multijob gets cleaned independently of its children. See [Cleaning job folder](results.html#cleaning) for details.

Private attributes `_active_children` and `_lock` are essential for proper parallel execution. Please do not modify them.

`__init__`(_children =None_, _childrunner =None_, _** kwargs_)[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`new_children`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.new_children)¶
    
Generate new children jobs.

This method is useful when some of children jobs are not known beforehand and need to be generated based on other children jobs, like for example in any kind of self-consistent procedure.

The goal of this method is to produce a new portion of children jobs. Newly created jobs should be returned in a container compatible with `self.children` (e.g. list for list, dict for dict). No adjustment of newly created jobs’ `parent` attribute is needed. This method **cannot** modify `_active_children` attribute.

The method defined here is a default template, returning `None`, which means no new children jobs are generated and the entire execution of the parent job consists only of running jobs initially found in `self.children`. To modify this behavior you can override this method in a `MultiJob` subclass or you can use one of [Binding decorators](functions.html#binding-decorators), just like with Prerun and postrun methods.

`hash`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.hash)¶
    
Hashing for multijobs is disabled by default. Returns `None`.

`check`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.check)¶
    
Check if the execution of this instance was successful, by calling `Job.ok()` of all the children jobs.

`other_jobs`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.other_jobs)¶
    
Iterate through other jobs that belong to this `MultiJob`, but are not in `children`.

Sometimes `prerun()` or `postrun()` methods create and run some small jobs that don’t end up in `children` collection, but are still considered a part of a `MultiJob` instance (their `parent` atribute points to the `MultiJob` and their working folder is inside MultiJob’s working folder). This method provides an iterator that goes through all such jobs.

Each attribute of this `MultiJob` that is of type `Job` and has it’s parent pointing to this `MultiJob` is returned, in a random order.

`remove_child`(_job_)[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.remove_child)¶
    
Remove _job_ from children.

`_get_ready`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob._get_ready)¶
    
Get ready for `_execute()`. Count children jobs and set their `parent` attribute.

`__iter__`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob.__iter__)¶
    
Iterate through `children`. If it is a dictionary, iterate through its values.

`_notify`()[[source]](../_modules/scm/plams/core/basejob.html#MultiJob._notify)¶
    
Notify this job that one of its children has finished.

Decrement `_active_children` by one. Use `_lock` to ensure thread safety.

`_execute`(_jobrunner_)[[source]](../_modules/scm/plams/core/basejob.html#MultiJob._execute)¶
    
Run all children from `children`. Then use `new_children()` and run all jobs produced by it. Repeat this procedure until `new_children()` returns an empty list. Wait for all started jobs to finish.

### Using MultiJob¶

`MultiJob` can be used in two ways: either by creating instances of it or by subclassing it. The simplest application is just to use an instance of `MultiJob` as a container grouping similar jobs that you wish to run at the same time using the same job runner:
[code] 
    mj = MultiJob(name='somejobs', children=[job1, job2, job3])
    mj.children.append(job4)
    mj.run(...)
    
[/code]

Such a “container job” can further be customized with Prerun and postrun methods. For example, `postrun()` can be used to collect the relevant data from all children jobs and store it in an easily accessible way in mutlijob’s [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results").

A more flexible way of using `MultiJob` is by creating your own subclasses of it. That way you can enclose several jobs that are conceptually similar in one convenient “unit”, for example:

  * `MultiJob` running a chain of single jobs: take a molecule, preoptimize its geometry using some approximate method, follow with a high-level geometry optimization and then use the optimized geoemtry for some properties calculation

  * `MultiJob` comparing different values of some parameter: run multiple single jobs with the same molecule and settings, but differing in one parameter (for example: XC functional, numerical accuracy, basis set etc.) for the sake of investigating the influence of that parameter on the final results

  * `MultiJob` running different geometries of the same system to investigate some property of the potential energy surface. A classic example here would be numerical gradient or numerical hessian calculations.

You can find examples of the above applications (and many more) in TODO: cookbook link.

[Next ](results.html "Results") [ Previous](settings.html "Settings")

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
