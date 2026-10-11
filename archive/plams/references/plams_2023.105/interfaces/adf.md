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
      * ADF (pre-2020 version)
        * Preparing input
        * Preparing runscript
        * API
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
  * ADF (pre-2020 version)

# ADF (pre-2020 version)¶

Warning

This page describes the old interface to the standalone ADF binary. Starting from AMS2020, ADF is an AMS engine and should be run using [`AMSJob`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"). If you are running AMS2019.3 or older version, you should still use `ADFJob`

ADF can be run from PLAMS using the `ADFJob` class and the corresponding `ADFResults`. The are subclasses of, respectively, `SCMJob` and `SCMResults`, which gather common pre-AMS logic for all members of the former ADFSuite.

## Preparing input¶

Input files for ADF consist of blocks and subblocks containg keys and values. That kind of structure can be easily reflected by [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") objects since they are built in a similar way.

The input file is generated based on `input` branch of job’s [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings"). All data present there is translated to input contents. Nested [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instances define blocks and subblocks, as in the example below:
[code] 
    myjob = ADFJob(molecule=Molecule('water.xyz'))
    myjob.settings.input.basis.type = 'DZP'
    myjob.settings.input.basis.core = 'None'
    myjob.settings.input.basis.createoutput = 'None'
    myjob.settings.input.scf.iterations = 100
    myjob.settings.input.scf.converge = '1.0e-06 1.0e-06'
    myjob.settings.input.save = 'TAPE13'
    
[/code]

Input file created during execution of `myjob` looks like:
[code] 
    atoms
        #coordinates from water.xyz
    end
    
    basis
      createoutput None
      core None
      type DZP
    end
    
    save TAPE13
    
    scf
      converge 1.0e-06 1.0e-06
      iterations 100
    end
    
[/code]

As you can see, entries present in `myjob.settings.input.` are listed in the alphabetical order. If an entry is a regular key-value pair it is printed in one line (like `save TAPE13` above). If an entry is a nested [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance it is printed as a block and entries in this instance correspond to contents of a the block. Both keys and values are kept in their original case. Strings put as values can contain spaces like `converge` above – the whole string is printed after the key. That allows to handle lines that need to contain more than one key=value pair. If you need to put a key without any value, `True` or empty string can be given as a value:
[code] 
    >>> myjob.settings.input.geometry.SP = True
    >>> myjob.settings.input.writefock = ''
    # translates to:
    geometry
      SP
    end
    
    writefock
    
[/code]

If a value of a particualr key is `False`, that key is omitted. To produce an empty block simply type:
[code] 
    >>> myjob.settings.input.geometry  # this is equivalent to myjob.settings.input.geometry = Settings()
    #
    geometry
    end
    
[/code]

The algorithm translating [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") contents into input file does not check the correctness of the data - it simply takes keys and values from [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance and puts them in the text file. Due to that you are not going to be warned if you make a typo, use wrong keyword or improper syntax. Beware of that.
[code] 
    >>> myjob.settings.input.dog.cat.apple = 'pear'
    #
    dog
      cat
        apple pear
      subend
    end
    
[/code]

Some blocks require (or allow) some data to be put in the header line, next to the block name. Special key `_h` is helpful in these situations:
[code] 
    >>> myjob.settings.input.someblock._h = 'header=very important'
    >>> myjob.settings.input.someblock.key1 = 'value1'
    >>> myjob.settings.input.someblock.key2 = 'value2'
    #
    someblock header=very important
      key1 value1
      key2 value2
    end
    
[/code]

The order of blocks within input file and subblocks within a parent block follows [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") iteration order which is lexicographical (however, `SCMJob` is smart enough to put blocks like DEFINE or UNITS at the top of the input). In rare cases you would want to override this order, for example when you supply ATOMS block manually, which can be done when automatic molecule handling is disabled (see below). That behavior can be achieved by another type of special key:
[code] 
    >>> myjob.settings.input.block._1 = 'entire line that has to be the first line of block'
    >>> myjob.settings.input.block._2 = 'second line'
    >>> myjob.settings.input.block._4 = 'I will not be printed'
    >>> myjob.settings.input.block.key1 = 'value1'
    >>> myjob.settings.input.block.key2 = 'value2'
    #
    block
      entire line that has to be the first line of block
      second line
      key1 value1
      key2 value2
    end
    
[/code]

Sometimes one needs to put more instances of the same key within one block, like for example in CONSTRAINTS block in ADF. It can be done by using list of values instead of a single value:
[code] 
    >>> myjob.settings.input.constraints.atom = [1,5,4]
    >>> myjob.settings.input.constraints.block = ['ligand', 'residue']
    #
    constraints
      atom 1
      atom 5
      atom 4
      block ligand
      block residue
    end
    
[/code]

Finally, in some rare cases key and value pair in the input needs to be printed in a form `key=value` instead of `key value`. When value is a string starting with the equal sign, no space is inserted between key and value:
[code] 
    >>> myjob.settings.input.block.key = '=value'
    #
    block
      key=value
    end
    
[/code]

Sometimes a value of a key in the input file needs to be a path to some file, usually KF file with results of some previous calculation. Of course such a path can be given explicitly `newjob.restart = '/home/user/science/plams.12345/oldjob/oldjob.t21'`, but for user’s convenience instances of `SCMJob` or `SCMResults` (or directly [`KFFile`](kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile")) can be also used. Algorithm will detect it and use an absolute path to the main KF file instead:
[code] 
    >>> myjob.settings.input.restart = oldjob
    >>> myjob.settings.input.fragment.frag1 = fragjob
    #
    restart /home/user/science/plams.12345/oldjob/oldjob.t21
    fragment
      frag1 /home/user/science/fragmentresults/somejob/somejob.t21
    end
    
[/code]

[`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance stored in job’s `molecule` attribute is automatically processed during the input file preparation and printed in the proper format, depending on the program. It is possible to disable that and give molecular coordinates explicitly as entries in `myjob.settings.input.`. Automatic molecule processing can be turned off by `myjob.settings.ignore_molecule = True`.

### Special atoms in ADF¶

In ADF atomic coordinates in `atoms` block can be enriched with some additional information like special names of atoms (for example in case of using different isotopes) or block/fragment membership. Since usually contents of `atoms` block are generated automatically based on the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") associated with a job, this information needs to be supplied inside the given [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance. Details about every atom can be adjusted separately, by modifying attributes of a particular [`Atom`](../components/atombond.html#scm.plams.mol.atom.Atom "scm.plams.mol.atom.Atom") instance according to the following convention:

  * Atomic symbol is generated based on atomic number stored in `atnum` attribute of a corresponding [`Atom`](../components/atombond.html#scm.plams.mol.atom.Atom "scm.plams.mol.atom.Atom"). Atomic number 0 corresponds to the “dummy atom” for which the symbol is empty.

  * If `atom.properties.ghost` exists and is `True`, the above atomic symbol is prefixed with `Gh.`.

  * If `atom.properties.name` exists, its contents are added after the symbol. Hence setting `atnum` to 0 and adjusting `name` allows to put an arbitrary string as the atomic symbol.

  * If `atom.properties.adf.fragment` exists, its contents are added after atomic coordinates with `f=` prefix.

  * If `atom.properties.adf.block` exists, its contents are added after atomic coordinates with `b=` prefix.

The following example illustrates the usage of this mechanism:
[code] 
    >>> mol = Molecule('xyz/Ethanol.xyz')
    >>> mol[1].properties.ghost = True
    >>> mol[2].properties.name = 'D'
    >>> mol[3].properties.ghost = True
    >>> mol[3].properties.name = 'T'
    >>> mol[4].properties.atnum = 0
    >>> mol[4].properties.name = 'J.XYZ'
    >>> mol[5].properties.atnum = 0
    >>> mol[5].properties.name = 'J.ASD'
    >>> mol[5].properties.ghost = True
    >>> mol[6].properties.adf.fragment = 'myfragment'
    >>> mol[7].properties.adf.block = 'block1'
    >>> mol[8].properties.adf.fragment = 'frag'
    >>> mol[8].properties.adf.block = 'block2'
    >>> myjob = ADFJob(molecule=mol)
    #
    atoms
          1      Gh.C       0.01247       0.02254       1.08262
          2       C.D      -0.00894      -0.01624      -0.43421
          3    Gh.H.T      -0.49334       0.93505       1.44716
          4     J.XYZ       1.05522       0.04512       1.44808
          5  Gh.J.ASD      -0.64695      -1.12346       2.54219
          6         H       0.50112      -0.91640      -0.80440 f=myfragment
          7         H       0.49999       0.86726      -0.84481 b=block1
          8         H      -1.04310      -0.02739      -0.80544 f=frag b=block2
          9         O      -0.66442      -1.15471       1.56909
    end
    
[/code]

## Preparing runscript¶

Runscripts for ADF are very simple. The only adjustable option (apart from usual `pre`, `post`, `shebang` and `stdout_redirect` which are common for all single jobs) is `myjob.settings.runscript.nproc`, indicating the number of parallel processes to run ADF with (like with `-n` flag or `NSCM` environmental variable).

## API¶

_class _`ADFResults`(_job_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults)¶
    
A specialized `SCMResults` subclass for accessing the results of `ADFJob`.

`get_properties`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_properties)¶
    
Return a dictionary with all the entries from `Properties` section in the main KF file (`$JN.t21`).

`get_main_molecule`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_main_molecule)¶
    
Return a [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance based on the `Geometry` section in the main KF file (`$JN.t21`).

For runs with multiple geometries (geometry optimization, transition state search, intrinsic reaction coordinate) this is the **final** geometry. In such a case, to access the initial (or any intermediate) coordinates please use `get_input_molecule()` or extract coordinates from section `History`, variables `xyz 1`, `xyz 2` and so on. Mind the fact that all coordinates written by ADF to `History` section are in bohr and internal atom order:
[code] 
    mol = results.get_molecule(section='History', variable='xyz 1', unit='bohr', internal=True)
    
[/code]

`get_input_molecule`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_input_molecule)¶
    
Return a [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance with initial coordinates.

All data used by this method is taken from `$JN.t21` file. The `molecule` attribute of the corresponding job is ignored.

`get_energy`(_unit ='au'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_energy)¶
    
Return final bond energy, expressed in _unit_.

`get_dipole_vector`(_unit ='au'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_dipole_vector)¶
    
Return the dipole vector, expressed in _unit_.

`get_gradients`(_energy_unit ='au'_, _dist_unit ='bohr'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_gradients)¶
    
Return the cartesian gradients from the ‘Gradients_InputOrder’ field of the ‘GeoOpt’ Section in the kf-file, expressed in given units. Returned value is a numpy array with shape (nAtoms,3).

`_extract_hessian`(_section_ , _variable_ , _internal_order_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults._extract_hessian)¶
    
Extract Hessian from _section_ /_variable_ of the TAPE21 file. Reorder from internal to input order, if _internal_order_ is `True`.

`get_hessian`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_hessian)¶
    
Try extracting Hessian, either analytical or numerical, whichever is present in the TAPE21 file, in the input order. Returned value is a square numpy array of size 3*nAtoms.

`get_energy_decomposition`(_unit ='au'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_energy_decomposition)¶
    
get_energy(unit=’au’) Return a dictionary with energy decomposition terms, expressed in _unit_.

The following keys are present in the returned dictionary: `Electrostatic`, `Kinetic`, `Coulomb`, `XC`. The sum of all the values is equal to the value returned by `get_energy()`. Note that additional contributions might be included, those are up to now: `Dispersion`.

`get_frequencies`(_unit ='cm^-1'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_frequencies)¶
    
Return a numpy array of vibrational frequencies, expressed in _unit_.

`get_timings`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.get_timings)¶
    
Return a dictionary with timing statistics of the job execution. Returned dictionary contains keys `cpu`, `system` and `elapsed`. The values are corresponding timings, expressed in seconds.

`_atomic_numbers_input_order`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults._atomic_numbers_input_order)¶
    
Return a list of atomic numbers, in the input order.

`_int2inp`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults._int2inp)¶
    
Get mapping from the internal atom order to the input atom order.

`recreate_molecule`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.recreate_molecule)¶
    
Recreate the input molecule for the corresponding job based on files present in the job folder. This method is used by [`load_external()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external").

`recreate_settings`()[[source]](../_modules/scm/plams/interfaces/adfsuite/adf.html#ADFResults.recreate_settings)¶
    
Recreate the input [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance for the corresponding job based on files present in the job folder. This method is used by [`load_external()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external").

Parent abstract classes:

_class _`SCMJob`(_molecule =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob)¶
    
Abstract class gathering common mechanisms for jobs with ADF Suite programs.

`__init__`(_** kwargs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`get_input`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.get_input)¶
    
Generate the input file. This method is just a wrapper around `_serialize_input()`.

Each instance of `SCMJob` or `SCMResults` present as a value in `settings.input` branch is replaced with an absolute path to the main KF file of that job.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.get_runscript)¶
    
Generate a runscript. Returned string is of the form:
[code] 
    $AMSBIN/name [-n nproc] <jobname.in [>jobname.out]
    
[/code]

`name` is taken from the class attribute `_command`. `-n` flag is added if `settings.runscript.nproc` exists. `[>jobname.out]` is used based on `settings.runscript.stdout_redirect`.

`check`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.check)¶
    
Check if `termination status` variable from `General` section of main KF file equals `NORMAL TERMINATION`.

`hash_input`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.hash_input)¶
    
Calculate the hash of the input file.

All instances of `SCMJob` or `SCMResults` present as values in `settings.input` branch are replaced with hashes of corresponding job’s inputs.

`_serialize_input`(_special_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob._serialize_input)¶
    
Transform all contents of `setting.input` branch into string with blocks, keys and values.

On the highest level alphabetic order of iteration is modified: keys occuring in attribute `_top` are printed first. Special values can be indicated with _special_ argument, which should be a dictionary having types of objects as keys and functions translating these types to strings as values.

Automatic handling of `molecule` can be disabled with `settings.ignore_molecule = True`.

`_serialize_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob._serialize_mol)¶
    
Process [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance stored in `molecule` attribute and add it as relevant entries of `settings.input` branch. Abstract method.

`_remove_mol`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob._remove_mol)¶
    
Remove from `settings.input` all entries added by `_serialize_mol()`. Abstract method.

_static _`_atom_symbol`(_atom_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob._atom_symbol)¶
    
Return the atomic symbol of _atom_. Ensure proper formatting for ADFSuite input taking into account `ghost` and `name` entries in `properties` of _atom_.

_classmethod _`from_inputfile`(_filename_ , _heredoc_delimit ='eor'_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.from_inputfile)¶
    
Construct a `SCMJob` instance from an ADF inputfile.

If a runscript is provide than this method will attempt to extract the input file based on the heredoc delimiter (see _heredoc_delimit_).

_static _`settings_to_mol`(_s_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMJob.settings_to_mol)¶
    
An abstract method for extracting molecules from input settings (see `SCMJob.from_inputfile()`).

_class _`SCMResults`(_job_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults)¶
    
Abstract class gathering common mechanisms for results of ADF Suite programs.

`collect`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.collect)¶
    
Collect files present in the job folder. Use parent method from [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results"), then create an instance of [`KFFile`](kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile") for the main KF file and store it as `_kf` attribute.

`refresh`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.refresh)¶
    
Refresh the contents of `files` list. Use parent method from [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results"), then look at all attributes that are instances of [`KFFile`](kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile") and check if they point to existing files. If not, try to reinstantiate them with current job path (that can happen while loading a pickled job after the entire job folder was moved).

`readkf`(_section_ , _variable_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.readkf)¶
    
Read data from _section_ /_variable_ of the main KF file.

The type of the returned value depends on the type of _variable_ defined inside KF file. It can be: single int, list of ints, single float, list of floats, single boolean, list of booleans or string.

`newkf`(_filename_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.newkf)¶
    
Create new [`KFFile`](kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile") instance using file _filename_ in the job folder.

Example usage:
[code] 
    >>> res = someadfjob.run()
    >>> tape13 = res.newkf('$JN.t13')
    >>> print(tape13.read('Geometry', 'xyz'))
    
[/code]

`get_properties`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.get_properties)¶
    
Return a dictionary with all the entries from `Properties` section in the main KF file.

`get_molecule`(_section_ , _variable_ , _unit ='bohr'_, _internal =False_, _n =1_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.get_molecule)¶
    
Read molecule coordinates from _section_ /_variable_ of the main KF file.

Returned [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance is created by copying a molecule from associated `SCMJob` instance and updating atomic coordinates with values read from _section_ /_variable_. The format in which coordinates are stored is not consistent for all programs or even for different sections of the same KF file. Sometimes coordinates are stored in bohr, sometimes in angstrom. The order of atoms can be either input order or internal order. These settings can be adjusted with _unit_ and _internal_ parameters. Some variables store more than one geometry, in those cases _n_ can be used to choose the preferred one.

`_get_single_value`(_section_ , _variable_ , _output_unit_ , _native_unit ='au'_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults._get_single_value)¶
    
A small method template for all the single number “get_something()” methods extracting data from main KF file. Returned value is converted from _native_unit_ to _output_unit_.

`_atomic_numbers_input_order`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults._atomic_numbers_input_order)¶
    
Return a list of atomic numbers, in the input order. Abstract method.

`kfpath`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.kfpath)¶
    
Return the absolute path to the main KF file.

`_kfpath`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults._kfpath)¶
    
Return the absolute path to the main KF file.

`_kfpresent`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults._kfpresent)¶
    
Check if this instance has a valid `_kf` attribute.

`_export_attribute`(_attr_ , _other_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults._export_attribute)¶
    
If _attr_ is a KF file take care of a proper path. Otherwise use parent method. See [`Results._copy_to`](../components/results.html#scm.plams.core.results.Results._copy_to "scm.plams.core.results.Results._copy_to") for details.

`_int2inp`()[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults._int2inp)¶
    
Obtain mapping from internal atom order to the input one. Abstract method.

`to_input_order`(_self_ , _data_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.to_input_order)¶
    
Reorder any iterable _data_ from the internal atom order to the input atom order. The length of _data_ must be equal to the number of atoms, otherwise an exception is raised. Returned value is a container of the same type as _data_.

`readarray`(_section_ , _subsection_ , _** kwargs_)[[source]](../_modules/scm/plams/interfaces/adfsuite/scmjob.html#SCMResults.readarray)¶
    
Read data from _section_ /_subsection_ of the main KF file and return as NumPy array.

All additional provided keyword arguments will be passed onto the [numpy.array](https://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html) function.

[Next ](reaxff.html "ReaxFF \(pre-2019 version\)") [ Previous](zacros.html "Zacros")

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
