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
    * Results
      * Files in the job folder
      * Synchronization of parallel job executions
        * Examples
      * Cleaning job folder
        * Cleaning for multijobs
      * API
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
  * Results

# Results¶

The goal of `Results` object is to take care of the job folder after the execution is finished: gather information about produced files, help to manage them and extract data of interest from them. Every [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance has an associated `Results` instance created automatically on job creation and stored in its `results` attribute.

From the technical standpoint, `Results` class is the part of PLAMS environment responsible for thread safety and proper synchronization in parallel job execution.

## Files in the job folder¶

Directly after the execution of a job is finished (see [Running a job](jobs.html#job-life-cycle)), the job folder gets scanned by `collect()` method. All files present in the job folder, including files in subfolders, are gathered in a list stored in `files` attribute of the `Results` instance. Entries in this list correspond to paths to files relative to the job folder, so files on the top level are stored by their names and files in subfolders by something like `childjob/childjob.out`.

Note

Files produced by [Pickling](jobmanager.html#pickling) are excluded from the `files` list. Every file with `.dill` extension is simply ignored by `Results`.

If you need an absolute path to some file, the bracket notation known from dictionaries is defined for `Results` objects. When supplied with an entry from `files` list, it returns the absolute path to that file. The bracket notation is read-only:
[code] 
    >>> r = j.run()
    >>> print(r.files)
    ['plamsjob.err', 'plamsjob.in', 'plamsjob.out', 'plamsjob.run']
    >>> print(r['plamsjob.out'])
    /home/user/plams.12345/plamsjob/plamsjob.in
    >>> r['newfile.txt'] = '/home/user/abc.txt'
    TypeError: 'Results' object does not support item assignment
    
[/code]

In the bracket notation, and in every other context regarding `Results`, whenever you need to pass a string with a filename, a shortcut `$JN` can be used for the job name:
[code] 
    >>> r.rename('$JN.out', 'outputfile')
    >>> r.grep_file('$JN.err', 'NORMAL TERMINATION')
    >>> print(r['$JN.run'])
    /home/user/plams.12345/plamsjob/plamsjob.run
    
[/code]

Some produce produce fixed name files during execution. If one wants to automatically rename those files it can be done with `_rename_map` class attribute – a dictionary defining which files should be renamed and how. Renaming is done during `collect()`.

In the generic `Results` class `_rename_map` is an empty dictionary.

## Synchronization of parallel job executions¶

One of the main advantages of PLAMS is the ability to run jobs in parallel. The whole job execution logic is designed in a way that does not require a special parallel script for a parallel workflow execution. Exactly the same scripts can be used for both serial and parallel execution.

However, it is important to have a basic understanding of how parallelism in PLAMS works to avoid potential deadlocks and maximize the performance of your scripts.

To run your job in parallel you need to use a parallel job runner:
[code] 
    pjr = JobRunner(parallel=True)
    myresults = myjob.run(jobrunner=pjr)
    
[/code]

Parallelism is not something that is “on” or “off” for the entire script: within one script you can use multiple job runners, some of them may be parallel and some may be serial. However, if you wish to always use the same [`JobRunner`](runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") instance, it is convenient to set is as default at the beginning of your script:
[code] 
    config.default_jobrunner = JobRunner(parallel=True)
    
[/code]

All [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") calls without explicit `jobrunner` argument will now use that instance.

When you run a job using a serial job runner, all steps of [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") (see [Running a job](jobs.html#job-life-cycle)) are done in the main thread and `Results` instance is returned at the end. On the other hand, when a parallel job runner is used, a new thread is spawned at the beginning of [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") and all further work is done in this thread. Meanwhile the main thread proceeds with the next part of the script. The important thing is that the [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") method called in the main thread returns a `Results` instance and allows the whole script to proceed even though the job is still running in a separate thread. This `Results` instance acts as a “guardian” protecting the job from being accessed while it is still running. Every time you call a method of a `Results` instance, the guardian checks the status of the job and, if the job is not yet finished, forces the thread from which the call was done to wait. Thanks to that there is no need to explicitly put synchronization points in the script – results requests serve for that purpose.

Warning

You should **NEVER** access results in any other way than by a **method** of some `Results` instance.

The `Results` class is designed in such a way, that each of its methods automatically gets wrapped with the access guardian when a `Results` instance is created. That behavior holds for any `Results` subclasses and new methods defined by user, so no need to worry about guardian when extending `Results` functionality or subclassing it. Also [Binding decorators](functions.html#binding-decorators) recognize when you try to use them with `Results` and act accordingly. Methods whose names end with two underscores, as well as `refresh()`, `collect()`, `_clean()` are not wrapped with the guardian. The guardian gives special privileges (earlier access) to [`postrun()`](jobs.html#scm.plams.core.basejob.Job.postrun "scm.plams.core.basejob.Job.postrun") and [`check()`](jobs.html#scm.plams.core.basejob.Job.check "scm.plams.core.basejob.Job.check") (see [Prerun and postrun methods](jobs.html#prerun-postrun)).

If you never request any results of your job and just want to run it, [`finish()`](functions.html#scm.plams.core.functions.finish "scm.plams.core.functions.finish") method works as a global synchronization point. It waits for all spawned threads to end before cleaning the environment and exiting your script.

### Examples¶

This section provides a handful of examples together with an explanation of common pitfalls and good practices one should keep in mind when writing parallel PLAMS scripts.

Let us start with a simple parallel script that takes all `.xyz` files in a given folder and for each one calculates the dipole moment magnitude using a single point ADF calculation:
[code] 
     1
     2
     3
     4
     5
     6
     7
     8
     9
    10
    11
    12
    13
    14
    15
    16
    17
[/code]

| 
[code]
    config.default_jobrunner = JobRunner(parallel=True)
    config.log.stdout = 1
    folder = '/home/user/xyz'
    molecules = read_molecules(folder)
    
    s = Settings()
    s.input.ams.task = 'singlepoint'
    s.input.adf.basis.type = 'DZP'
    s.input.adf.xc.gga = 'PBE'
    
    jobs = [AMSJob(molecule=molecules[name], name=name, settings=s) for name in sorted(molecules)]
    results = [job.run() for job in jobs]
    
    for r in results:
        dipole_vec = r.readrkf('AMSResults', 'DipoleMoment', file='engine')
        dipole_magn = sum([a*a for a in dipole_vec])**0.5
        print('{}\t\t{}'.format(r.job.name, dipole_magn))
    
[/code]  
  
---|---  
  
For an explanation purpose let us assume that `/home/user/xyz` contains three files: `ammonia.xyz`, `ethanol.xyz`, `water.xyz`. When you run this script the standard output will look something like:
[code] 
    [17:31:52] PLAMS working folder: /home/user/plams_workdir
    [17:31:52] JOB 'ammonia' STARTED
    [17:31:52] JOB 'ethanol' STARTED
    [17:31:52] JOB 'water' STARTED
    [17:31:52] Waiting for job ammonia to finish
    [17:31:56] JOB 'water' SUCCESSFUL
    [17:31:56] JOB 'ammonia' SUCCESSFUL
    ammonia     0.5949493793257181
    [17:31:56] Waiting for job ethanol to finish
    [17:32:01] JOB 'ethanol' SUCCESSFUL
    ethanol     0.5946259677193089
    water       0.7082267171673067
    
[/code]

As you can see, print statements from line 17 are mixed with automatic logging messages. Let us examine in more detail what causes such a behavior. To do so we will follow the main thread. In line 11 an alphabetically sorted list of jobs is created, so the job named `'ethanol'` will come after `'ammonia'` and before `'water'`. Line 12 is a for loop that goes along the list of jobs, runs each of them and collects their `Results` instances in a new list called `results`. If we were using a serial job runner, all the computational work would happen in line 12: the `'ethanol'` job would start only when `'ammonia'` was finished, `'water'` would wait for `'ethanol'` and the main thread would proceed to the next line only when `'water'` is done.

In our case, however, we are using a parallel job runner. The first job (`'ammonia'`) is started and quickly moves to a separate thread, allowing the main thread to proceed to another instruction, which in this case is the [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run") method of the `'ethanol'` job. Thanks to that all three jobs are started almost immediately one after another, corresponding `Results` are gathered and the main thread proceeds to line 14, while the three jobs are running “in the background”, handled by separate threads. Now the main thread goes along the `results` list (which follows the same order as `jobs`) and tries to obtain a dipole vector from each job. It uses `readkf` method of `Results` instance associated with the `'ammonia'` job and since this job is still running, the main thread hangs and waits for the job to finish (_“Waiting for job ammonia to finish”_). Meanwhile we can see that the `'water'` job ends and this fact is logged. Quickly after that also the `'ammonia'` job finishes and the main thread obtains `dipole_vec`, calculates `dipole_magn` and prints it. Now the `for` loop in line 14 continues, this time for the `'ethanol'` job. This job seems to be a bit longer than `'ammonia'`, so it is still running and the main thread again hangs on the `readkf` method (_“Waiting for job ethanol to finish”_). After finally obtaining the dipole vector of ethanol, calculating the magnitude and printing it, the `for` loop goes on with its last iteration, the `'water'` job. This time there is no need to wait since the job is already finished - the result is calculated and printed immediately.

Knowing that, let us wonder what would happen if the order of jobs was different. If `'ethanol'` was the first job on the list, by the time its results would be obtained and printed, both other jobs would have finished, so no further waiting would be needed. On the other hand, if the order was `'water'`–`'ammonia'`–`'ethanol'`, the main thread would have to wait every time when executing line 15.

The most important lesson from the above is: the order in which you start jobs does not matter (too much), it is the order of results requests that makes the difference. Of course in our very simple example it influences only the way in which results are mixed with log messages, but in more complicated workflows it can directly affect the total runtime of your script.

By the way, to avoid print statements being mixed with logging messages one could first store the data and print it only when all the results are ready:
[code] 
    to_print = []
    for r in results:
        dipole_vec = r.readkf('Properties', 'Dipole')
        dipole_magn = sum([a*a for a in dipole_vec])**0.5
        to_print += [(r.job.name, dipole_magn)]
    for nam, dip in to_print:
        print('{}\t\t{}'.format(nam, dip))
    
[/code]

Another way could be disabling logging to the standard output by putting `config.log.stdout = 0` at the beginning of the script (see [`log()`](functions.html#scm.plams.core.functions.log "scm.plams.core.functions.log")).

Coming back to the main topic of our considerations, as we have seen above, parallelism in PLAMS is driven by results request. Not only the order of requests is important, but also (probably even more important) the place from which they are made. To picture this matter we will use the following script that performs geometry optimization followed by frequencies calculation of the optimized geometry:
[code] 
     1
     2
     3
     4
     5
     6
     7
     8
     9
    10
    11
    12
    13
    14
    15
[/code]

| 
[code]
    config.default_jobrunner = JobRunner(parallel=True)
    
    go = AMSJob(name='GeomOpt', molecule=Molecule('geom.xyz'))
    go.settings.input.ams.task = 'GeometryOptimization'
    ... #other settings adjustments for geometry optimisation
    go_results = go.run()
    
    opt_geo = go_results.get_main_molecule()
    
    freq = AMSJob(name='Freq', molecule=opt_geo)
    freq.settings.input.ams.properties.NormalModes = 'Yes'
    ... #other settings adjustments for frequency run
    freq_results = freq.run()
    
    do_other_work() # further part of the script, independent of GeomOpt and Freq
    
[/code]  
  
---|---  
  
Again let us follow the main thread. In line 8 we can see a results request for the optimized geometry from “GeomOpt” job. The main thread will wait for that job to finish before preparing the “Freq” job and running it. That means `do_other_work()`, whatever it is, will not start before “GeomOpt” is done, even though it could, since it is independent of GeomOpt and Freq results. This is bad. The main thread is wasting time that could be used for `do_other_work()` on idle waiting. We need to fix the script:
[code] 
     1
     2
     3
     4
     5
     6
     7
     8
     9
    10
    11
    12
    13
    14
    15
    16
    17
    18
[/code]

| 
[code]
    config.default_jobrunner = JobRunner(parallel=True)
    
    go = AMSJob(name='GeomOpt', molecule=Molecule('geom.xyz'))
    go.settings.input.ams.task = 'GeometryOptimization'
    ... #other settings adjustments for geometry optimisation
    go_results = go.run()
    
    freq = AMSJob(name='Freq')
    freq.settings.input.ams.properties.NormalModes = 'Yes'
    ... #other settings adjustments for frequency run
    
    @add_to_instance(freq)
    def prerun(self):
        self.molecule = go_results.get_main_molecule()
    
    freq_results = freq.run()
    
    do_other_work() # further part of the script, independent of GeomOpt and Freq
    
[/code]  
  
---|---  
  
The results request (`go_results.get_main_molecule()`) have been moved from the main script to the [`prerun()`](jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method of the “Freq” job. The [`prerun()`](jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun") method is executed in job’s thread rather than in the main thread. That means the main thread starts the “Freq” job immediately after starting the “GeomOpt” job and then directly proceeds to `do_other_work()`. Meanwhile in the thread spawned for the “Freq” job the result request for molecule is made and only that thread waits for “GeomOpt” to finish.

As seen in the above example, it is extremely important to properly configure jobs that are dependent (setup of one depends on results of another). Resolving all such dependencies in job’s thread rather than in the main thread guarantees that waiting for results is done only by the code that really needs them.

Note

In some cases dependencies between job are not easily expressed via methods of `Results` (for example, one job sets up some environment that is later used by another job). In such cases one can use job’s `depend` attribute to explicitly tell the job about other jobs it has to wait for. Adding `job2` to `job1.depend` is roughly equivalent to putting `job2.results.wait()` in `job1` [`prerun()`](jobs.html#scm.plams.core.basejob.Job.prerun "scm.plams.core.basejob.Job.prerun").

To sum up all the above considerations, here is the rule of thumb on how to write properly working parallel PLAMS scripts:

  1. Request results as late as possible, preferably just before using them.

  2. If possible, avoid requesting results in the main thread.

  3. Place the result request in the thread in which that data is later used.

## Cleaning job folder¶

The `Results` instance associated with a job is responsible for cleaning the job folder (removing files that are no longer needed). Cleaning is done automatically, twice for each job.

First cleaning is done during [`run()`](jobs.html#scm.plams.core.basejob.Job.run "scm.plams.core.basejob.Job.run"), just after [`check()`](jobs.html#scm.plams.core.basejob.Job.check "scm.plams.core.basejob.Job.check") and before [`postrun()`](jobs.html#scm.plams.core.basejob.Job.postrun "scm.plams.core.basejob.Job.postrun"). The value adjusting this first cleaning is taken from `myjob.settings.keep` and should be either a string or a list (see below).

This cleaning is intended for situations when your jobs produce large files that you don’t need for further processing. Running many of such jobs could deplete the disk space and cause the whole script to crash. If you wish to immediately get rid of some files produced by your jobs (without having a chance to do anything with them), use the first cleaning.

In the majority of cases it is sufficient to use the second cleaning, which is performed at the end of your script, when [`finish()`](functions.html#scm.plams.core.functions.finish "scm.plams.core.functions.finish") method is called. It is adjusted by `myjob.settings.save`. You can use the second cleaning to remove files that you no longer need after you extracted relevant data earlier in your script.

The argument passed to `_clean()` (in other words the value that is supposed to be kept in `myjob.settings.keep` and `myjob.settings.save`) can be one of the following:

  * `'all'` – nothing is removed, cleaning is skipped.

  * `'none'` or `[]` or `None` – everything is removed from the job folder.

  * list of strings – list of filenames to be kept. Shortcut `$JN` can be used here, as well as *-wildcards. For example `['geo.*', '$JN.out', 'logfile']` will keep `[jobname].out`, `logfile` and all files whose names start with `geo.` and remove everything else from the job folder.

  * list of strings with the first element `'-'` – reversed behavior to the above, listed files will be removed. For example `['-', 't21.*', '$JN.err']` will remove `[jobname].err` and all files whose names start with `t21.`

### Cleaning for multijobs¶

Cleaning happens for every job run with PLAMS, either single job or multijob. That means, for example, that a single job that is a child of some multijob will have its job folder cleaned by two different `Results` instances: it’s own `Results` and its parent’s `Results`. Those two cleanings can interfere with each other. Hence it is a good practice to set cleaning only on one level (either in a parent job or in children jobs) and disable cleaning on the other level, by using `'all'`.

Another shortcut can be used for cleaning in multijobs: `$CH` is expanded with every possible child name. For example, if you have a multijob `mj` with 5 single job children (`child1`, `child2` and so on) and you wish to keep only input and output files of children jobs you can set:
[code] 
    mj.settings.save = ['$CH/$CH.in', '$CH/$CH.out']
    
[/code]

It is equivalent to:
[code] 
    mj.settings.save = ['child1/child1.in', 'child2/child2.in', ... , 'child1/child1.out', 'child2/child2.out', ...]
    
[/code]

As you can see above, while cleaning a multijob folder you have to keep in mind that files in subfolders are kept as relative paths.

## API¶

Note

These functions work for all Results type. See the [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") class for functions extracting or manipulating results from AMS jobs.

_class _`Results`(_job_)[[source]](../_modules/scm/plams/core/results.html#Results)¶
    
General concrete class for job results.

`job` attribute stores a reference to associated job. `files` attribute is a list with contents of the job folder. `_rename_map` is a class attribute with the dictionary storing the default renaming scheme.

Bracket notation (`myresults[filename]`) can be used to obtain full absolute paths to files in the job folder.

Instance methods are automatically wrapped with the “access guardian” that ensures thread safety (see Synchronization of parallel job executions).

`__init__`(_job_)[[source]](../_modules/scm/plams/core/results.html#Results.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`refresh`()[[source]](../_modules/scm/plams/core/results.html#Results.refresh)¶
    
Refresh the contents of the `files` list. Traverse the job folder (and all its subfolders) and collect relative paths to all files found there, except files with `.dill` extension.

This is a cheap and fast method that should be used every time there is a risk the contents of the job folder changed and `files` is no longer up-to-date. For proper working of various PLAMS elements it is crucial that `files` always contains up-to-date information about the contents of the job folder.

All functions and methods defined in PLAMS that could change the state of the job folder refresh the `files` list, so there is no need to manually call `refresh()` after, for example, `rename()`. If you are implementing a new method of that kind, please don’t forget about refreshing.

`collect`()[[source]](../_modules/scm/plams/core/results.html#Results.collect)¶
    
Collect the files present in the job folder after execution of the job is finished. This method is simply `refresh()` followed by renaming according to the `_rename_map`.

If you wish to override this function, you have to call the parent version at the beginning.

`wait`()[[source]](../_modules/scm/plams/core/results.html#Results.wait)¶
    
Wait for associated job to finish.

Technical

This is **not** an abstract method. It does exactly what it should: nothing. All the work is done by `_restrict()` decorator that is wrapped around it.

`grep_file`(_filename_ , _pattern =''_, _options =''_)[[source]](../_modules/scm/plams/core/results.html#Results.grep_file)¶
    
Execute `grep` on a file given by _filename_ and search for _pattern_.

Additional `grep` flags can be passed with _options_ , which should be a single string containing all flags, space separated.

Returned value is a list of lines (strings). See `man grep` for details.

`grep_output`(_pattern =''_, _options =''_)[[source]](../_modules/scm/plams/core/results.html#Results.grep_output)¶
    
Shortcut for `grep_file()` on the output file.

`read_file`(_filename_)[[source]](../_modules/scm/plams/core/results.html#Results.read_file)¶
    
Returns the contents of the filename, where filename has to be in self.files. If filename contains the `$JN` string, it will be replaced with self.job.name.

Note

For text files only. Reading binary files such as *.rkf will result in an error.

`regex_file`(_filename_ , _regex_)[[source]](../_modules/scm/plams/core/results.html#Results.regex_file)¶
    
Applies a regular expression pattern to the output of `read_file()` such that the returned value is `re.findall(regex, read_file(filename))`.

`awk_file`(_filename_ , _script =''_, _progfile =None_, _** kwargs_)[[source]](../_modules/scm/plams/core/results.html#Results.awk_file)¶
    
Execute an AWK script on a file given by _filename_.

The AWK script can be supplied in two ways: either by directly passing the contents of the script (should be a single string) as the _script_ argument, or by providing the path (absolute or relative to _filename_) to a text file with an AWK script as the _progfile_ argument. If _progfile_ is not `None`, _script_ is ignored.

Other keyword arguments (_**kwargs_) can be used to pass additional variables to AWK (see `-v` flag in AWK manual)

Returned value is a list of lines (strings). See `man awk` for details.

`awk_output`(_script =''_, _progfile =None_, _** kwargs_)[[source]](../_modules/scm/plams/core/results.html#Results.awk_output)¶
    
Shortcut for `awk_file()` on the output file.

`rename`(_old_ , _new_)[[source]](../_modules/scm/plams/core/results.html#Results.rename)¶
    
Rename a file from `files`. In both _old_ and _new_ the shortcut `$JN` for job name can be used.

`get_file_chunk`(_filename_ , _begin =None_, _end =None_, _match =0_, _inc_begin =False_, _inc_end =False_, _process =None_)[[source]](../_modules/scm/plams/core/results.html#Results.get_file_chunk)¶
    
Extract a chunk of a text file given by _filename_ , consisting of all the lines between a line containing _begin_ and a line containing _end_.

_begin_ and _end_ should be simple strings (no regular expressions allowed) or `None` (in that case matching is done from the beginning or until the end of the file). If multiple blocks delimited by _begin_ end _end_ are present in the file, _match_ can be used to indicate which one should be printed (_match*=0 prints all of them). *inc_begin_ and _inc_end_ can be used to include the delimiting lines in the final result (by default they are excluded).

The returned value is a list of strings. _process_ can be used to provide a function executed on each element of this list before returning it.

`get_output_chunk`(_begin =None_, _end =None_, _match =0_, _inc_begin =False_, _inc_end =False_, _process =None_)[[source]](../_modules/scm/plams/core/results.html#Results.get_output_chunk)¶
    
Shortcut for `get_file_chunk()` on the output file.

`recreate_molecule`()[[source]](../_modules/scm/plams/core/results.html#Results.recreate_molecule)¶
    
Recreate the input molecule for the corresponding job based on files present in the job folder. This method is used by [`load_external()`](jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external").

The definiton here serves as a deafult fall-back template preventing [`load_external()`](jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external") from crashing when a particular `Results` subclass does not define it’s own `recreate_molecule()`.

`recreate_settings`()[[source]](../_modules/scm/plams/core/results.html#Results.recreate_settings)¶
    
Recreate the input [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance for the corresponding job based on files present in the job folder. This method is used by [`load_external()`](jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external").

The definiton here serves as a deafult fall-back template preventing [`load_external()`](jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external") from crashing when a particular `Results` subclass does not define it’s own `recreate_settings()`.

`_clean`(_arg_)[[source]](../_modules/scm/plams/core/results.html#Results._clean)¶
    
Clean the job folder. _arg_ should be a string or a list of strings. See Cleaning job folder for details.

`_copy_to`(_newresults_)[[source]](../_modules/scm/plams/core/results.html#Results._copy_to)¶
    
Copy these results to _newresults_.

This method is used when [Rerun prevention](jobmanager.html#rerun-prevention) discovers an attempt to run a job identical to a previously run job. Instead of the execution, results of the previous job are copied/linked to the new one.

This method is called from `Results` of the old job and _newresults_ should be `Results` of the new job. The goal is to faithfully recreate the state of this `Results` instance in `newresults`. To achieve that, all the contents of the job folder are copied (or hardlinked, if your platform allows that and `job.settings.link_files` is `True`) to other’s job folder. Moreover, all attributes of this `Results` instance (other than `job` and `files`) are exported to _newresults_ using `_export_attribute()` method.

`_export_attribute`(_attr_ , _other_)[[source]](../_modules/scm/plams/core/results.html#Results._export_attribute)¶
    
Export this instance’s attribute to _other_. This method should be overridden in your `Results` subclass if it has some attributes that are not properly handled by [`copy.deepcopy()`](https://docs.python.org/3.8/library/copy.html#copy.deepcopy "\(in Python v3.8\)").

_other_ is the `Results` instance, _attr_ is the **value** of the attribute to be copied. See [`SCMJob._export_attribute`](../interfaces/adf.html#scm.plams.interfaces.adfsuite.scmjob.SCMResults._export_attribute "scm.plams.interfaces.adfsuite.scmjob.SCMResults._export_attribute") for an example implementation.

_static _`_replace_job_name`(_string_ , _oldname_ , _newname_)[[source]](../_modules/scm/plams/core/results.html#Results._replace_job_name)¶
    
If _string_ starts with _oldname_ , maybe followed by some extension, replace _oldname_ with _newname_.

`__getitem__`(_name_)[[source]](../_modules/scm/plams/core/results.html#Results.__getitem__)¶
    
Magic method to enable bracket notation. Elements from `files` can be used to get absolute paths.

`__contains__`(_name_)[[source]](../_modules/scm/plams/core/results.html#Results.__contains__)¶
    
Magic method to enable the Python `in` operator notation for checking if a filename with a particular name is present.

`_process_file`(_filename_ , _command_)[[source]](../_modules/scm/plams/core/results.html#Results._process_file)¶
    
Skeleton for all file processing methods. Execute _command_ (should be a list of strings) on _filename_ and return output as a list of lines.

Technical

Other parts of `results` module described below are responsible for giving `Results` class its unique behavior described in Synchronization of parallel job executions. They are presented here for the sake of completeness, from a user’s perspective this information is not too relevant.

_class _`_MetaResults`(_name_ , _bases_ , _dct_)[[source]](../_modules/scm/plams/core/results.html#_MetaResults)¶
    
Metaclass for `Results`. During new `Results` instance creation it wraps all methods with `_restrict()` decorator ensuring proper synchronization and thread safety. Methods listed in `_dont_restrict` as well as “magic methods” are not wrapped.

_static _`__new__`(_meta_ , _name_ , _bases_ , _dct_)[[source]](../_modules/scm/plams/core/results.html#_MetaResults.__new__)¶
    
Create and return a new object. See help(type) for accurate signature.

`_restrict`(_func_)[[source]](../_modules/scm/plams/core/results.html#_restrict)¶
    
Decorator that wraps methods of `Results` instances.

Whenever decorated method is called, the status of associated job is checked. Depending of its value access to the method is granted, refused or the calling thread is forced to wait for the right [event](https://docs.python.org/3.8/library/threading.html#event-objects "\(in Python v3.8\)") to be set.

`_caller_name_and_arg`(_frame_)[[source]](../_modules/scm/plams/core/results.html#_caller_name_and_arg)¶
    
Extract information about name and arguments of a function call from a _frame_ object

`_privileged_access`()[[source]](../_modules/scm/plams/core/results.html#_privileged_access)¶
    
Analyze contents of the current stack to find out if privileged access to the `Results` methods should be granted.

Privileged access is granted to two [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") methods: [`postrun()`](jobs.html#scm.plams.core.basejob.Job.postrun "scm.plams.core.basejob.Job.postrun") and [`check()`](jobs.html#scm.plams.core.basejob.Job.check "scm.plams.core.basejob.Job.check"), but only if they are called from [`_finalize()`](jobs.html#scm.plams.core.basejob.Job._finalize "scm.plams.core.basejob.Job._finalize") of the same [`Job`](jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") instance.

[Next ](runners.html "Job runners") [ Previous](jobs.html "Jobs")

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
