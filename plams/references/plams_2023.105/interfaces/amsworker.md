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
      * AMS worker
        * AMSWorker API
        * AMSWorkerResults API
        * AMSWorkerPool API
      * [ASE Calculator for AMS](amscalculator.html)
      * [Quick jobs](quickjobs.html)
      * [Analysis tools: Densf, FCF, analysis](postadf.html)
      * [KF files](kffiles.html)
      * [COSMO-RS](crs.html)
      * [ParAMS](params.html)
      * [Conformers](conformers.html)
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
  * AMS worker

# AMS worker¶

The PLAMS interface to the AMS driver and its engines through the [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") and [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") questions is technically quite similar to how one would run calculations from the command line or from the GUI: the AMS input files are written to disk, the AMS driver starts up, reads its input, performs the calculations and writes the results to disk in form of human readable text files as well as machine readable binary files, usually in [KF format](kffiles.html#kf-files). This setup has the advantage that any calculation that can be performed with AMS can be setup from PLAMS as an [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"), and that any result from any calculation can be accessed from PLAMS through the corresponding [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") instance. Furthermore, the resulting files on disk can often visualized using the AMS GUI, as if the job had been set up and run through the graphical user interface. As such, this way of running AMS offers maximum flexibility and convenience to users.

However, for simple and fast jobs where we only care about some basic results, this flexibility comes at a cost: input files need to be created on disk, a process is launched, possibly reading all kinds of configuration and parameter files. The process writes more files to disk, which we later need to open again to extract (in the worst case) just a single number. The overhead might be irrelevant for sufficiently slow engines, but for a very fast force field this overhead can easily become the performance bottleneck.

Starting with the AMS2019.3 release, the AMS driver implements a special task, in which the running process listens for calculation requests on a named pipe (FIFO) and communicates the results of the calculations back on another pipe. This avoids the overhead of starting processes and eliminates all file based I/O. You can find more information about the pipe interface in the AMS driver in the [corresponding part of the documentation](../../AMS/Input_Output.html#pipe-interface). In PLAMS the `AMSWorker` class is used to represent this running AMS driver process. The `AMSWorker` class handles all communication with the process and hides the technical details of underlying [communication protocol](../../AMS/Pipe_protocol.html).

Consider the following short PLAMS script, that calculates and prints the total GFN1-xTB energy for all molecules found in a folder full of xyz-files. Using the regular [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"), this can be written as:
[code] 
    molecules = read_molecules('folder/with/xyz/files')
    
    sett = Settings()
    sett.input.ams.Task = 'SinglePoint'
    sett.input.dftb.Model = 'GFN1-xTB'
    
    for name, mol in molecules.items():
        results = AMSJob(name=name, molecule=mol, settings=sett).run()
        print('Energy of {} = {}'.format(name, results.get_energy()))
    
[/code]

In order to switch this script over to using the `AMSWorker`, we need to make only a couple of changes:
[code] 
    molecules = read_molecules('folder/with/xyz/files')
    
    sett = Settings()
    sett.input.dftb.Model = 'GFN1-xTB'
    
    with AMSWorker(sett) as worker:
        for name, mol in molecules.items():
            results = worker.SinglePoint(name, mol)
            print('Energy of {} = {}'.format(name, results.get_energy()))
    
[/code]

With the first [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") based version, both the [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance and the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance were passed into the constructor of the [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"), while the `AMSWorker` constructor only accepts the [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance. The [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance is only later passed into the `SinglePoint` method. This shows the basic usage of the `AMSWorker` class: create it once, supplying the desired [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings"), and use these fixed settings for calculations on multiple molecules. It is _not_ possible to change the [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") on an already running `AMSWorker` instance. If you have to switch [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings"), you need to create a new `AMSWorker` with the new settings. It therefore only makes sense to use the `AMSWorker` if one has to do calculations on many molecules _using the same settings_.

Note that when using the `AMSWorker` the type of `results` in the above example is not actually [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") anymore: the call to `SinglePoint` returns an instance of `AMSWorkerResults`, which only implements a small subset of the methods available in the full [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults"). This is the concession we have to make for using `AMSWorker` instead of [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"): after all the [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") class has many methods to extract arbitrary data from the result files of an AMS calculation. Since none of these files exist when directly communicating with the AMS process over a pipe, the `AMSWorkerResults` class supports none of these methods.

Given these restrictions we recommend that users first try the traditional route of running the AMS driver via the [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") class, and only switch to the `AMSWorker` alternative if they observe a significant slowdown due to the startup and I/O cost. The overhead is likely only relevant for simple tasks (single points, geometry optimizations) using rather fast engines such as semi-empirical methods and force fields.

In case the worker process fails to start up or terminates unexpectedly, an `AMSWorkerError` exception will be raised. The standard output and standard error output from the failed worker process is stored in the `stdout` and `stderr` attributes in `AMSWorkerError`. If an `AMSWorkerError` or `AMSPipeRuntimeError` exception occurs during `SinglePoint`, it will be internally caught and stored in the `error` attribute of the returned `AMSWorkerResults` object for further inspection. These two types of exceptions are typically related to the calculation being performed (the combination of the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") and [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")), so they are not allowed to propagate out of `SinglePoint` to match the behavior of [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") in similar situations. However, other types of exceptions derived from `AMSPipeError` may also occur in `AMSWorker`. These correspond to other errors defined by the pipe protocol and will propagate normally, because they represent programming and logic errors, protocol incompatibilities, or unsupported features. In any case, `AMSWorker` will be ready to handle another call to `SinglePoint` after an error.

PLAMS also provides the `AMSWorkerPool` class, which represents a pool of running `AMSWorker` instances, which dynamically pick tasks from a queue of calculations to be performed. This is useful for workflows that require the execution of many trivially parallel simple tasks. Using the `AMSWorkerPool` we could write the above example as:
[code] 
    molecules = read_molecules('folder/with/xyz/files')
    
    sett = Settings()
    sett.input.dftb.Model = 'GFN1-xTB'
    sett.runscript.nproc = 1 # every worker is a serial process now
    
    with AMSWorkerPool(sett, num_workers=4) as pool:
         results = pool.SinglePoints(molecules.items())
    for r in results:
       print('Energy of {} = {}'.format(r.name, r.get_energy()))
    
[/code]

## AMSWorker API¶

_class _`AMSWorker`(_settings_ , _workerdir_root ='/tmp'_, _workerdir_prefix ='amsworker'_, _use_restart_cache =True_, _keep_crashed_workerdir =False_, _always_keep_workerdir =False_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorker)¶
    
A class representing a running instance of the AMS driver as a worker process.

Users need to supply a [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance representing the input of the AMS driver process (see [Preparing input](ams.html#ams-preparing-input)), but **not including** the `Task` keyword in the input (the `input.ams.Task` key in the [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance). The [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance should also not contain a system specification in the `input.ams.System` block, the `input.ams.Properties` block, or the `input.ams.GeometryOptimization` block. Often the settings of the AMS driver in worker mode will come down to just the engine block.

The AMS driver will then start up as a worker, communicating with PLAMS via named pipes created in a temporary directory (determined by the _workerdir_root_ and _workerdir_prefix_ arguments). This temporary directory might also contain temporary files used by the worker process. Note that while an `AMSWorker` instance exists, the associated worker process can be assumed to be running and ready: If it crashes for some reason, it is automatically restarted.

The recommended way to start an `AMSWorker` is as a context manager:
[code] 
    with AMSWorker(settings) as worker:
        results = worker.SinglePoint('my_calculation', molecule)
    # clean up happens automatically when leaving the block
    
[/code]

If it is not possible to use the `AMSWorker` as a context manager, cleanup should be manually triggered by calling the `stop()` method.

`stop`(_keep_workerdir =False_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorker.stop)¶
    
Stops the worker process and removes its working directory.

This method should be called when the `AMSWorker` instance is not used as a context manager and the instance is no longer needed. Otherwise proper cleanup is not guaranteed to happen, the worker process might be left running and files might be left on disk.

`SinglePoint`(_name_ , _molecule_ , _prev_results =None_, _quiet =True_, _gradients =False_, _stresstensor =False_, _hessian =False_, _elastictensor =False_, _charges =False_, _dipolemoment =False_, _dipolegradients =False_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorker.SinglePoint)¶
    
Performs a single point calculation on the geometry given by the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance _molecule_ and returns an instance of `AMSWorkerResults` containing the results.

Every calculation should be given a _name_. Note that the name **must be unique** for this `AMSWorker` instance: One should not attempt to reuse calculation names with a given instance of `AMSWorker`.

By default only the total energy is calculated but additional properties can be requested using the corresponding keyword arguments:

  * _gradients_ : Calculate the nuclear gradients of the total energy.

  * _stresstensor_ : Calculate the clamped-ion stress tensor. This should only be requested for periodic systems.

  * _hessian_ : Calculate the Hessian matrix, i.e. the second derivative of the total energy with respect to the nuclear coordinates.

  * _elastictensor_ : Calculate the elastic tensor. This should only be requested for periodic systems.

  * _charges_ : Calculate atomic charges.

  * _dipolemoment_ : Calculate the electric dipole moment. This should only be requested for non-periodic systems.

  * _dipolegradients_ : Calculate the nuclear gradients of the electric dipole moment. This should only be requested for non-periodic systems.

Users can pass an instance of a previously obtained `AMSWorkerResults` as the _prev_results_ keyword argument. This can trigger a restart from previous results in the worker process, the details of which depend on the used computational engine: For example, a DFT based engine might restart from the electronic density obtained in an earlier calculation on a similar geometry. This is often useful to speed up series of sequentially dependent calculations:
[code] 
    mol = Molecule('some/system.xyz')
    with AMSWorker(sett) as worker:
        last_results = None
        do i in range(num_steps):
            results = worker.SinglePoint(f'step{i}', mol, prev_results=last_results, gradients=True)
            # modify the geometry of mol using results.get_gradients()
            last_results = results
    
[/code]

Note that the restarting is disabled if the `AMSWorker` instance was created with `use_restart_cache=False`. It is still permitted to pass previous [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") instances as the _prev_results_ argument, but no restarting will happen.

The _quiet_ keyword can be used to obtain more output from the worker process. Note that the output of the worker process is not printed to the standard output but instead ends up in the `ams.out` file in the temporary working directory of the `AMSWorker` instance. This is mainly useful for debugging.

`GeometryOptimization`(_name_ , _molecule_ , _prev_results =None_, _quiet =True_, _gradients =True_, _stresstensor =False_, _hessian =False_, _elastictensor =False_, _charges =False_, _dipolemoment =False_, _dipolegradients =False_, _method =None_, _coordinatetype =None_, _usesymmetry =None_, _optimizelattice =False_, _maxiterations =None_, _pretendconverged =None_, _calcpropertiesonlyifconverged =True_, _convquality =None_, _convenergy =None_, _convgradients =None_, _convstep =None_, _convstressenergyperatom =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorker.GeometryOptimization)¶
    
Performs a geometry optimization on the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance _molecule_ and returns an instance of `AMSWorkerResults` containing the results from the optimized geometry.

The geometry optimizer can be controlled using the following keyword arguments:

  * _method_ : String identifier of a particular optimization algorithm.

  * _coordinatetype_ : Select a particular kind of optimization coordinates.

  * _usesymmetry_ : Enable the use of symmetry when applicable.

  * _optimizelattice_ : Optimize the lattice vectors together with atomic positions.

  * _maxiterations_ : Maximum number of iterations allowed.

  * _pretendconverged_ : If set to true, non converged geometry optimizations will be considered successful.

  * _calcpropertiesonlyifconverged_ : Calculate properties (e.g. the Hessian) only if the optimization converged.

  * _convquality_ : Overall convergence quality, see AMS driver manual for the GeometryOptimization task.

  * _convenergy_ : Convergence criterion for the energy (in Hartree).

  * _convgradients_ : Convergence criterion for the gradients (in Hartree/Bohr).

  * _convstep_ : Convergence criterion for displacements (in Bohr).

  * _convstressenergyperatom_ : Convergence criterion for the stress energy per atom (in Hartree).

`ParseInput`(_program_name_ , _text_input_ , _string_leafs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorker.ParseInput)¶
    
Parse the text input and return a Python dictionary representing the the JSONified input.

  * _program_name_ : the name of the program. This will be used for loading the appropriate json input definitions. e.g. if program_name=’adf’, the input definition file ‘adf.json’ will be used.

  * _text_input_ : a string containing the text input to be parsed.

  * _string_leafs_ : if _True_ the values in the parsed json input will always be string. e.g. if in the input you have ‘SomeFloat 1.2’, the json leaf node for ‘SomeFloat’ will be the string ‘1.2’ (and not the float number 1.2). If False the leaf values in the json input will be of the ‘appropriate’ type, i.e. float will be floats, strings will be strings, booleans will be boleans etc…

## AMSWorkerResults API¶

_class _`AMSWorkerResults`(_name_ , _molecule_ , _results_ , _error =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults)¶
    
A specialized class encapsulating the results from calls to an `AMSWorker`.

Technical

AMSWorkerResults is _not_ a subclass of [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") or [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults"). It does however implement some commonly used methods of the [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") class, so that results calculated by [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") and `AMSWorker` can be accessed in a uniform way.

_property _`name`¶
    
The name of a calculation.

That is the name that was passed into the `AMSWorker` method when this `AMSWorkerResults` object was created. I can not be changed after the `AMSWorkerResults` instance has been created.

`ok`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.ok)¶
    
Check if the calculation was successful. If not, the `error` attribute contains a corresponding exception.

Users should check if the calculation was successful before using the other methods of the `AMSWorkerResults` instance, as using them might raise a `ResultsError` exception otherwise.

`get_errormsg`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_errormsg)¶
    
Attempts to retreive a human readable error message from a crashed job. Returns `None` for jobs without errors.

`get_energy`(_unit ='au'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_energy)¶
    
Return the total energy, expressed in _unit_.

`get_gradients`(_energy_unit ='au'_, _dist_unit ='au'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_gradients)¶
    
Return the nuclear gradients of the total energy, expressed in _energy_unit_ / _dist_unit_.

`get_stresstensor`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_stresstensor)¶
    
Return the clamped-ion stress tensor, expressed in atomic units.

`get_hessian`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_hessian)¶
    
Return the Hessian matrix, i.e. the second derivative of the total energy with respect to the nuclear coordinates, expressed in atomic units.

`get_elastictensor`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_elastictensor)¶
    
Return the elastic tensor, expressed in atomic units.

`get_charges`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_charges)¶
    
Return the atomic charges, expressed in atomic units.

`get_dipolemoment`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_dipolemoment)¶
    
Return the electric dipole moment, expressed in atomic units.

`get_dipolegradients`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_dipolegradients)¶
    
Return the nuclear gradients of the electric dipole moment, expressed in atomic units. This is a (3*numAtoms x 3) matrix.

`get_input_molecule`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_input_molecule)¶
    
Return a [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance with the coordinates passed into the `AMSWorker`.

Note that this method may also be used if the calculation producing this `AMSWorkerResults` object has failed, i.e. `ok()` is `False`.

`get_main_molecule`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_main_molecule)¶
    
Return a [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance with the final coordinates.

`get_main_ase_atoms`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerResults.get_main_ase_atoms)¶
    
Return an ASE Atoms instance with the final coordinates.

## AMSWorkerPool API¶

_class _`AMSWorkerPool`(_settings_ , _num_workers_ , _workerdir_root ='/tmp'_, _workerdir_prefix ='awp'_, _keep_crashed_workerdir =False_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerPool)¶
    
A class representing a pool of AMS worker processes.

All workers of the pool are initialized with the same [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance, see the `AMSWorker` constructor for details.

The number of spawned workers is determined by the _num_workers_ argument. For optimal performance on many small jobs it is recommended to spawn a number of workers equal to the number of physical CPU cores of the machine the calculation is running on, and to let every worker instance run serially:
[code] 
    import psutil
    
    molecules = read_molecules('folder/with/xyz/files')
    
    sett = Settings()
    # ... more settings ...
    sett.runscript.nproc = 1 # <-- every worker itself is serial (aka export NSCM=1)
    
    with AMSWorkerPool(sett, psutil.cpu_count(logical=False)) as pool:
        results = pool.SinglePoints([ (name, molecules[name]) for name in sorted(molecules) ])
    
[/code]

As with the underlying `AMSWorker` class, the location of the temporary directories can be changed with the _workerdir_root_ and _workerdir_prefix_ arguments.

It is recommended to use the `AMSWorkerPool` as a context manager in order to ensure that cleanup happens automatically. If it is not possible to use the `AMSWorkerPool` as a context manager, cleanup should be manually triggered by calling the `stop()` method.

`SinglePoints`(_items_ , _watch =False_, _watch_interval =60_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerPool.SinglePoints)¶
    
Request to pool to execute single point calculations for all items in the iterable _items_. Returns a list of `AMSWorkerResults` objects.

The _items_ argument is expected to be an iterable of 2-tuples `(name, molecule)` and/or 3-tuples `(name, molecule, kwargs)`, which are passed on to the `SinglePoint` method of the pool’s `AMSWorker` instances. (Here `kwargs` is a dictionary containing the optional keyword arguments and their values for this method.)

If _watch_ is set to `True`, the AMSWorkerPool will regularly log progress information. The interval between messages can be set with the _watch_interval_ argument in seconds.

As an example, the following call would do single point calculations with gradients and (only for periodic systems) stress tensors for all [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instances in the dictionary `molecules`.
[code] 
    results = pool.SinglePoint([ (name, molecules[name], {
                                     "gradients": True,
                                     "stresstensor": len(molecules[name].lattice) != 0
                                  }) for name in sorted(molecules) ])
    
[/code]

`GeometryOptimizations`(_items_ , _watch =False_, _watch_interval =60_)[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerPool.GeometryOptimizations)¶
    
Request to pool to execute geometry optimizations for all items in the iterable _items_. Returns a list of `AMSWorkerResults` objects for the optimized geometries.

If _watch_ is set to `True`, the AMSWorkerPool will regularly log progress information. The interval between messages can be set with the _watch_interval_ argument in seconds.

The _items_ argument is expected to be an iterable of 2-tuples `(name, molecule)` and/or 3-tuples `(name, molecule, kwargs)`, which are passed on to the `GeometryOptimization` method of the pool’s `AMSWorker` instances. (Here `kwargs` is a dictionary containing the optional keyword arguments and their values for this method.)

`stop`()[[source]](../_modules/scm/plams/interfaces/adfsuite/amsworker.html#AMSWorkerPool.stop)¶
    
Stops the all worker processes and removes their working directories.

This method should be called when the `AMSWorkerPool` instance is not used as a context manager and the instance is no longer needed. Otherwise proper cleanup is not guaranteed to happen, worker processes might be left running and files might be left on disk.

[Next ](amscalculator.html "ASE Calculator for AMS") [ Previous](ams.html "AMS driver and engines")

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
