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
    * Job runners
      * Local job runner
      * Remote job runner
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
  * Job runners

# Job runners¶

Job runners have already been mentioned in previous chapters about jobs and results. Here we sum up all that information and introduce a basic `JobRunner` object together with its subclass `GridRunner` which is meant for interacting with queueing systems that manage resources on computer clusters.

Job runners in PLAMS are very simple objects, both from user’s perspective and in terms of internal architecture. They have no methods that are meant to be called in your scripts, apart from constructors. Job runners are supposed to be created (with some parameters adjusting their behavior) and passed to the [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") method as parameters (or placed as `config.default_jobrunner`).

## Local job runner¶

_class _`JobRunner`(_parallel =False_, _maxjobs =0_, _maxthreads =256_)[[source]](../_modules/scm/plams/core/jobrunner.html#JobRunner)¶
    
Class defining the basic job runner interface. Instances of this class represent local job runners – job runners that execute computational jobs on the current machine.

The goal of the job runner is to take care of two important things – parallelization and runscript execution:

  * When the method [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") of any [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance is executed, the control, after some initial preparations, is passed to a `JobRunner` instance. This `JobRunner` instance decides if a separate thread should be spawned for the job or if the execution should proceed in the current thread. This decision is based on the `parallel` attribute which can be set on `JobRunner` creation. There are no separate classes for serial and parallel job runner, both cases are covered by `JobRunner` depending on the `parallel` parameter.

  * If the executed job is an instance of [`SingleJob`](jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"), it creates a runscript which contains most of the actual computational work (usually it’s just an execution of some external binary). The runscript is then submitted to a `JobRunner` instance using its `call()` method. This method executes the runscript as a separate subprocess and takes care of output and error streams handling, setting a proper working directory etc.

For a job runner with parallel execution enabled the number of simultaneously running jobs can be limited using the _maxjobs_ parameter. If _maxjobs_ is 0, no limit is enforced. If _parallel_ is `False`, _maxjobs_ is ignored. If _parallel_ is `True` and _maxjobs_ is a positive integer, a [`BoundedSemaphore`](https://docs.python.org/3.8/library/threading.html#threading.BoundedSemaphore "\(in Python v3.8\)") of that size is used to limit the number of simultaneously running `call()` methods.

For a parallel `JobRunner` the maximum amount of threads started is limited by the _maxthreads_ argument. As each job is running in a separate thread, this number necessarily acts as an upper limit for the number of jobs that can run in parallel. If the limit is exhausted, running further jobs with this `JobRunner` instance will block execution until another already running job thread terminates. The `maxthreads` limit should be set as large as possible, but not so large as to exceed any limits imposed by the operating system.

A `JobRunner` instance can be passed to [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") with a keyword argument `jobrunner`. If this argument is omitted, the instance stored in `config.default_jobrunner` is used.

`__init__`(_parallel =False_, _maxjobs =0_, _maxthreads =256_)[[source]](../_modules/scm/plams/core/jobrunner.html#JobRunner.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`call`(_runscript_ , _workdir_ , _out_ , _err_ , _runflags_)[[source]](../_modules/scm/plams/core/jobrunner.html#JobRunner.call)¶
    
Execute the _runscript_ in the folder _workdir_. Redirect output and error streams to _out_ and _err_ , respectively.

Arguments _runscript_ , _workdir_ , _out_ and _err_ should be strings with paths to corresponding files or folders.

_runflags_ is a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance containing the run branch of running job’s settings. The basic job runner defined here ignores them, but they can be useful in `JobRunner` subclasses (see `GridRunner.call()`).

Returns an integer with the exit code returned by the _runscript_.

This method can be safely overridden in `JobRunner` subclasses. For example, in `GridRunner` it submits the runscript to a queueing system instead of executing it locally.

Note

This method is used automatically during [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") and should never be explicitly called in your script.

`_run_job`(_job_ , _jobmanager_)[[source]](../_modules/scm/plams/core/jobrunner.html#JobRunner._run_job)¶
    
This method aggregates the parts of [Running a job](jobs.html#job-life-cycle) that are supposed to be run in a separate thread in case of parallel job execution. It is wrapped with `_in_limited_thread()` decorator.

This method should not be overridden.

Technical

Similarly to the [`Results`](results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") class, the proper behavior of `JobRunner` and its subclasses (also the ones defined by the user) is ensured using a metaclass. For the sake of completeness we present here a brief specification of all involved elements:

_class _`_MetaRunner`(_name_ , _bases_ , _dct_)[[source]](../_modules/scm/plams/core/jobrunner.html#_MetaRunner)¶
    
Metaclass for `JobRunner`. During an instance creation wrap the `call()` method with `_limit()` decorator which enforces a limit on the number of simultaneous `call()` calls.

_static _`__new__`(_meta_ , _name_ , _bases_ , _dct_)[[source]](../_modules/scm/plams/core/jobrunner.html#_MetaRunner.__new__)¶
    
Create and return a new object. See help(type) for accurate signature.

`_limit`(_func_)[[source]](../_modules/scm/plams/core/jobrunner.html#_limit)¶
    
Decorator for an instance method. If `semaphore` attribute of given instance is not `None`, use this attribute to wrap decorated method via [with](https://docs.python.org/3.8/library/threading.html#with-locks "\(in Python v3.8\)") statement.

`_in_thread`(_func_)[[source]](../_modules/scm/plams/core/jobrunner.html#_in_thread)¶
    
Decorator for an instance method. If `parallel` attribute of given instance is `True`, run decorated method in a separate [`Thread`](https://docs.python.org/3.8/library/threading.html#threading.Thread "\(in Python v3.8\)"). This thread is usually a daemon thread, the decision is based on `config.daemon_threads` entry.

## Remote job runner¶

_class _`GridRunner`(_grid ='auto'_, _sleepstep =5_, _parallel =True_, _maxjobs =0_)[[source]](../_modules/scm/plams/core/jobrunner.html#GridRunner)¶
    
Subclass of `JobRunner` that submits the runscript to a queueing system instead of executing it locally. Besides two new keyword arguments (_grid_ and _sleepstep_) it behaves and is meant to be used just like a regular `JobRunner`.

Note

The default value of the _parallel_ argument is `True`, unlike in the regular `JobRunner`.

There are many different queueing systems that are popular nowadays (for example: TORQUE, SLURM, OGE). Usually they use different commands for submitting jobs or checking the queue status. `GridRunner` class tries to build a common interface to these systems. The commands used to communicate with the queueing system are not hard-coded, but rather taken from a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance. Thanks to that the user has almost full control over the behavior of a `GridRunner` instance and the behavior can be ajdusted dynamically.

The behavior of a `GridRunner` instance is determined by the contents of a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance stored in its `settings` attribute. That [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance can be manually supplied by the user or taken from a collection of predefined instances stored as branches of `GridRunner.config`. The adjustment is done with the _grid_ parameter which should be a string or a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance. If it’s a string, it has to be a key occurring in `GridRunner.config` or `'auto'` for autodetection. For example, if `grid='slurm'` is passed, `GridRunner.config.slurm` is used as settings. If `grid='auto'` then entries present in `GridRunner.config` are tested and the first one that works (its submit command is present on your system) is chosen. When a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance is passed as _grid_ , it is directly used as `settings`.

Currently two predefined schemes are available (see [Defaults file](../started.html#plams-defaults)): `slurm` for SLURM and `pbs` for queueing systems following PBS syntax (PBS, TORQUE, Oracle Grid Engine etc.).

The settings of `GridRunner` should have the following structure:

  * `output` – flag for specifying the output file path.

  * `error` – flag for specifying the error file path.

  * `workdir` – flag for specifying path to the working directory.

  * `commands.submit` – submit command.

  * `commands.check` – queue status check command.

  * `commands.getid` – function extracting submitted job’s ID from the output of the submit command.

  * `commands.running` – function extracting a list of all running jobs from the output of queue check command

  * `commands.special` – branch storing definitions of special [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") keyword arguments.

See `call()` for more details and examples.

The _sleepstep_ parameter defines how often the queue check is performed. It should be a numerical value telling how many seconds should the interval between two consecutive checks last.

Note

Usually queueing systems are configured in such a way that output of your calculation is captured somewhere else and copied to the location indicated by the output flag only when the job is finished. Because of that it is not possible to have a peek at your output while your job is running (for example, to see if your calculation is going well). This limitation can be circumvented with `myjob.settings.runscript.stdout_redirect` flag. If set to `True`, the output redirection will not be handled by the queueing system, but rather placed in the runscript using the shell redirection `>`. That forces the output file to be created directly in _workdir_ and updated live as the job proceeds.

`__init__`(_grid ='auto'_, _sleepstep =5_, _parallel =True_, _maxjobs =0_)[[source]](../_modules/scm/plams/core/jobrunner.html#GridRunner.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`call`(_runscript_ , _workdir_ , _out_ , _err_ , _runflags_)[[source]](../_modules/scm/plams/core/jobrunner.html#GridRunner.call)¶
    
Submit _runscript_ to the queueing system with _workdir_ as the working directory. Redirect output and error streams to _out_ and _err_ , respectively. _runflags_ stores varoius submit command options.

The submit command has the following structure:
[code] 
    <commands.submit>_<workdir>_{workdir}_<error>_{err}[_<output>_{out}][FLAGS]_{runscript}
    
[/code]

Underscores denote spaces, parts in pointy brackets correspond to `settings` entries, parts in curly brackets to `call()` arguments, square brackets contain optional parts. Output part is added if _out_ is not `None`. This is handled automatically based on `runscript.stdout_redirect` value in job’s `settings`.

`FLAGS` part is built based on _runflags_ argument, which is a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance storing [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") keyword arguments. For every _(key,value)_ pair in _runflags_ the string `_-key_value` is appended to `FLAGS` **unless** the _key_ is a special key occurring in `commands.special`. In that case `_<commands.special.key>value` is used (mind the lack of space in between). For example, a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance defining interaction with SLURM has the following entries:
[code] 
    workdir = '-D'
    output  = '-o'
    error   = '-e'
    special.nodes    = '-N '
    special.walltime = '-t '
    special.memory = '--mem='
    special.queue    = '-p '
    commands.submit  = 'sbatch'
    commands.check  = 'squeue'
    
[/code]

The submit command produced by:
[code] 
    gr = GridRunner(parallel=True, maxjobs=4, grid='slurm')
    j.run(jobrunner=gr, queue='short', nodes=2, J='something', O='')
    
[/code]

will be:
[code] 
    sbatch -D {workdir} -e {err} -o {out} -p short -N 2 -J something -O  {runscript}
    
[/code]

In certain queueing systems some flags don’t have a short form with semantics `-key value`. For example, in SLURM the flag `--nodefile=value` has a short form `-F value`, but the flag `--export=value` does not. One can still use such a flag using the special keys logic:
[code] 
    gr = GridRunner(parallel=True, maxjobs=4, grid='slurm')
    gr.settings.special.export = '--export='
    j.run(jobrunner=gr, queue='short', export='value')
    
[/code]

That results in the command:
[code] 
    sbatch -D {workdir} -e {err} -o {out} -p short --export=value {runscript}
    
[/code]

The submit command is then executed and the output returned by it is used to determine the submitted job’s ID. The value stored in `commands.getid` is used for that purpose. It should be a function taking a single string (the whole output of the submit command) and returning a string with job’s ID.

The submitted job’s ID is then added to `_active_jobs` dictionary, with the key being job’s ID and the value being an instance of [`threading.Lock`](https://docs.python.org/3.8/library/threading.html#threading.Lock "\(in Python v3.8\)"). This lock is used to singal the fact that the job is finished and the thread handling it can continue. Then the `_check_queue()` method starts the thread querying the queue and unlocking finished jobs.

Since it is difficult to automatically obtain job’s exit code, the returned value is 0 (or 1, if the submit command failed). From [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") perspective it means that a job executed with `GridRunner` is _crashed_ only if it never entered the queue (usually due to improper submit command).

Note

This method is used automatically during [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") and should never be explicitly called in your script.

`_check_queue`()[[source]](../_modules/scm/plams/core/jobrunner.html#GridRunner._check_queue)¶
    
Query the queueing system to obtain a list of currently running jobs. Check for active jobs that are not any more in the queue and release their locks. Repeat this procedure every `sleepstep` seconds until there are no more active jobs. The `_mainlock` lock ensures that there is at most one thread executing the main loop of this method at the same time.

`_autodetect`()[[source]](../_modules/scm/plams/core/jobrunner.html#GridRunner._autodetect)¶
    
Try to autodetect the type of queueing system.

The autodetection mechanism is very simple. For each entry in `GridRunner.config` the submit command followed by `--version` is executed (for example `qsub --version`). If the execution was successful (which is indicated by the exit code 0), that queueing system is present and it is chosen. Thus if there are multiple queueing systems installed, only one of them is picked – the one which “name” (indicated by a key in `GridRunner.config`) is first in the lexicographical order.

Returned value is one of `GridRunner.config` branches. If autodetection was not successful, an exception is raised.

[Next ](jobmanager.html "Job manager") [ Previous](results.html "Results")

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
