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
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](../examples/examples.html)
  * Cookbook
    * Settings and input
      * Create an input block with an header
      * Create an empty input block
      * Create an input block with repeating keys
      * Repeating input block
      * Convert an AMS text input into an AMS job
      * Convert an AMS text input into settings object
      * Convert an AMS .run file into an AMS job
      * Specify paths to files in the input
      * Restart from a previous job
    * Molecules
      * Generate a molecule from a SMILES string
      * Load all files in a folder as molecules
      * Generate a liquid or gas mixture
      * Write an ams.rkf-like trajectory
      * Convert a trajectory to ams.rkf with bond guessing
      * Pre-optimize a molecule
      * Counting rings
    * Extracting Results
      * Directly from Functions
        * Examples: Total Energy and Final Structure
        * AMSResults API Functions
      * From the RKF Interface
      * Finding Section/Variable Pairs
        * From Python Directories
        * KFBrowser
      * From molecular dynamics trajectories
        * General MD properties
        * Molecules from trajectories
    * Accessing Old Jobs
      * Binding Native PLAMS Jobs
      * Binding old RKF Files
    * Parallelization
      * Parallel job execution
      * PLAMS scripts under Slurm
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * Cookbook

# Cookbook¶

This is a collection of code snippets showing how to perform recurrent PLAMS tasks.

## Settings and input¶

### Create an input block with an header¶

These [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")
[code] 
    sett = Settings()
    sett.input.ams.SomeInputBlock['_h'] = 'MyHeader'
    sett.input.ams.SomeInputBlock.SomeOption = 2
    
[/code]

will generate the following text input when used for an [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"):
[code] 
    SomeInputBlock MyHeader
        SomeOption 2
    End
    
[/code]

### Create an empty input block¶

These [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")
[code] 
    sett = Settings()
    sett.input.ams.SomeInputBlock
    
[/code]

will generate the following text input when used for an [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"):
[code] 
    SomeInputBlock
    End
    
[/code]

### Create an input block with repeating keys¶

These [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")
[code] 
    sett = Settings()
    sett.input.ams.constraints.atom = [1,2,3]
    
[/code]

will generate the following text input when used for an [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"):
[code] 
    Constraints
        Atom 1
        Atom 2
        Atom 3
    End
    
[/code]

### Repeating input block¶

These [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")
[code] 
    block_1 = Settings()
    block_1.SomeOption = 1
    
    block_2 = Settings()
    block_2.SomeOption = 7
    
    sett = Settings()
    sett.input.ams.SomeInputBlock = [block_1, block_2]
    
[/code]

will generate the following text input when used for an [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob"):
[code] 
    SomeInputBlock
      SomeOption 1
    End
    SomeInputBlock
      SomeOption 7
    End
    
[/code]

### Convert an AMS text input into an AMS job¶

The [`from_input()`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob.from_input "scm.plams.interfaces.adfsuite.ams.AMSJob.from_input") function can be used to convert text input into [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") instances.
[code] 
    job = AMSJob.from_input(name='jobname', text_input='''
    Task SinglePoint
    System
        Atoms
            H 0. 0. 0.
            H 0. 0. 1.
        End
    End
    Engine Band
        Basis
            Type DZ
            Core None
        End
    EndEngine
    ''')
    
[/code]

### Convert an AMS text input into settings object¶

The [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") object corresponding to a piece of text input can easily be obtained as the `.settings` attribute of the [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") instance returned by the [`from_input()`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob.from_input "scm.plams.interfaces.adfsuite.ams.AMSJob.from_input") method.
[code] 
    settings = AMSJob.from_input("""
    Task SinglePoint
    Engine Band
        Basis
            Type DZ
            Core None
        End
    EndEngine
    """).settings
    
[/code]

### Convert an AMS .run file into an AMS job¶

The [`from_inputfile()`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob.from_inputfile "scm.plams.interfaces.adfsuite.ams.AMSJob.from_inputfile") method can be used to convert a .run file generated by the AMS GUI into a PLAMS [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob").
[code] 
    job = AMSJob.from_inputfile('/path/to/job.run')
    
[/code]

Note

This function does not work on PLAMS-generated .run files. You can instead use the PLAMS-generated .in file.

### Specify paths to files in the input¶

With PLAMS, you cannot specify relative paths to input files, because every PLAMS job launches in a new directory, which makes the relative paths invalid. To specify an absolute path, use `os.path.abspath`:
[code] 
    import os
    
    sett = Settings()
    sett.input.reaxff.forcefield = os.path.abspath('../my-forcefield.ff')
    
[/code]

### Restart from a previous job¶

To use restart features in AMS, for example the `EngineRestart`, or to read the `InitialVelocities` from the final velocities of a previous molecular dynamics run, you can use a convenient shortcut and simply assign the job to the corresponding settings entry:
[code] 
    sett = Settings()
    sett.input.ams.EngineRestart = (previous_ams_job, 'engine') # resolves to the engine.rkf
    
    sett2 = Settings()
    sett2.input.ams.MolecularDynamics.InitialVelocities.Type = 'FromFile'
    sett2.input.ams.MolecularDynamics.InitialVelocities.File = previous_ams_job # resolves to ams.rkf
    
[/code]

Alternatively, call the [`rkfpath()`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults.rkfpath "scm.plams.interfaces.adfsuite.ams.AMSResults.rkfpath") method on the previous job’s [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults"):
[code] 
    sett = Settings()
    sett.input.ams.EngineRestart = previous_ams_job.results.rkfpath(file='engine')
    
    sett2 = Settings()
    sett2.input.ams.MolecularDynamics.InitialVelocities.Type = 'FromFile'
    sett2.input.ams.MolecularDynamics.InitialVelocities.File = previous_ams_job.results.rkfpath()
    
[/code]

## Molecules¶

### Generate a molecule from a SMILES string¶

See function [`from_smiles()`](../components/mol_rdkit.html#scm.plams.interfaces.molecule.rdkit.from_smiles "scm.plams.interfaces.molecule.rdkit.from_smiles").
[code] 
    # Compute 10 conformers, optimize with UFF and pick the lowest in energy.
    ethane = from_smiles('C-C', nconfs=10, forcefield='uff')[0]
    
[/code]

### Load all files in a folder as molecules¶

See function [`read_molecules()`](../components/functions.html#scm.plams.core.functions.read_molecules "scm.plams.core.functions.read_molecules").
[code] 
    molecules = read_molecules('/some_path/folder_containing_structure_files/')
    
    for name, mol in molecules.items():
        print("Name of the file (without extension): ", name)
        print(mol)
    
[/code]

### Generate a liquid or gas mixture¶
[code] 
    # Generate a 2-to-1 water-acetonitrile mixture with a density of 0.9 g/cm^3 and approximately 200 atoms
    water = from_smiles('O')
    acetonitrile = from_smiles('CC#N')
    mixture = packmol(molecules=[water, acetonitrile],
                      mole_fractions=[0.667, 0.333],
                      n_atoms=200,
                      density=0.9)
    
[/code]

See [Packmol example](../examples/PackMolExample/PackMolExample.html#packmolexample) for more examples on how to construct liquid or gas mixtures and solid/liquid or solid/gas interfaces.

### Write an ams.rkf-like trajectory¶

If you have a list of molecules, it can be convenient to write them to an AMS-like .rkf file so that you can visualize them in the GUI module AMSmovie.
[code] 
    from scm.plams import molecules_to_rkf, from_smiles
    
    molecule_list = [from_smiles('C'), from_smiles('CC')]
    molecules_to_rkf(molecule_list, 'output.rkf', overwrite=True)
    
[/code]

### Convert a trajectory to ams.rkf with bond guessing¶

See [Convert to ams.rkf trajectory with bond guessing](../examples/ConvertToAMSRKFTrajectory.html#converttoamsrkftrajectory)

### Pre-optimize a molecule¶
[code] 
    # pre-optimize with UFF inside AMS
    optimized_mol = preoptimize(mol)
    
[/code]

See [Quick jobs](../interfaces/quickjobs.html#quickjobs) for details and options.

### Counting rings¶

Rings inside molecules can be counted in various ways, which are not all giving the same results. With the help of the RDKit library, a vast variety of ring counting approaches is readily available. The general approach to using these functions in a PLAMS scripts is to convert your PLAMS [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") into an RDKit molecule, see the page on the [RDKit interface](../components/mol_rdkit.html#rdkitmol). This is how one searches for the smallest set of rings in a molecule:
[code] 
    # import RDKit
    from rdkit import Chem
    
    # create a PLAMS molecule and convert it to an RDKit Mol
    dicyclopentadiene = from_smiles('C1C=CC2C1C3CC2C=C3')
    rdmol = to_rdmol(dicyclopentadiene)
    
    # Calculate smalles set of rings
    for atoms in Chem.GetSymmSSSR(rdmol):
         print ([atom_id for atom_id in atoms], len(atoms))
    
[/code]

For more information see also the [RDKit manual](https://www.rdkit.org/docs/GettingStartedInPython.html#ring-information).

## Extracting Results¶

You can use the following snippets to retrieve results after running the required calculations:

### Directly from Functions¶

Results can be either red from previous calculations (see Accessing Old Jobs) or from an [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") instance of a computation just executed within the same workflow. In either case an [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") object should be present at runtime:
[code] 
    myAMSJob.run()
    myAMSResults = myAMSJob.results if myAMSJob.ok() else None
    
[/code]

Warning

Access to any results data should only occur under the condition that AMSJob.ok() indicate a successful termination of the computation.

#### Examples: Total Energy and Final Structure¶

Multiple functions of the [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") API allow for simple access of the most common results.
[code] 
    myAMSEnergy = myAMSResults.get_energy(unit='au')
    
    myAMSStructure = myAMSResults.get_main_molecule()
    
[/code]

#### AMSResults API Functions¶

The following members of an [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") instance can be used as shown in the above examples to read results:

Property | Function | Return Type | Details  
---|---|---|---  
Structure | get_molecule(section) | [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") | Structure from section  
| get_input_molecule() | [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") | Input structure  
| get_main_molecule() | [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") | Final structure from any AMS task  
| get_history_molecule(step) | [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") | Structure from history section at step # step  
Energy | get_energy() | Float | Final energy  
Gradients | get_gradients() | Array (numpy) | Gradients from engine calculation  
Stress tensor | get_stresstensor() | Array (numpy) | Stress tensor from periodic engine calculation  
Hessian | get_hessian() | Array (numpy) | Hessian from frequency calculation (AMS/engine)  
Elastic tensor | get_elastictensor() | Array (numpy) | Elastic tensor from periodic calculation  
Frequencies | get_frequencies() | Array (numpy) | Vibrational frequencies  
Atomic Charges | get_charges() | Array (numpy) | Atomic partial charges  
Dipole vector | get_dipolemoment() | Array (numpy) | Electric dipole moment  
Nuclear gradients of dipole vector | get_dipolegradients() | Array (numpy) | Nuclear Gradients of Electric dipole moment  
  
### From the RKF Interface¶

Other properties not listed in the table above should be retrieved using the [`readrkf()`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults.readrkf "scm.plams.interfaces.adfsuite.ams.AMSResults.readrkf") function:
[code] 
    myProperty = myAMSResults.readrkf(section, variable)
    
[/code]

It is the responsibility of the user to provide the correct names for section and variable under which the required result is stored in the rkf file.

### Finding Section/Variable Pairs¶

Looking up the names of the needed sections and variable within rkf files is typically needed for more intricate properties when writing a new PLAMS workflow. There are two main approaches to search for this information.

#### From Python Directories¶

The [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") member function [`get_rkf_skeleton()`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults.get_rkf_skeleton "scm.plams.interfaces.adfsuite.ams.AMSResults.get_rkf_skeleton") returns a dictionary containing the available sections as keys and the containing variable names as values

#### KFBrowser¶

[KFBrowser](../../GUI/KFbrowser.html) is a GUI module used to inspect rkf files.

**1.** Open KFBrowser in the GUI via **SCM → KFBrowser**

**2.** By default KFBrowser opens the ams.rkf file. Where neccessary, switch to **File → open → <engine>.rkf**

**3.** Press **ctrl + e** or select **File → Expert Mode** to display the stored file contents

**4.** Find the entry of interest. While this is a sometimes not trivial step, most often the required variable is found in either the `Properties` or `AMSResults` sections.

**5.** Once found, the names for section and variable listed in the rkf file directly corresponds to the section/variable pair to be used in the readrkf function as shown above.

Note

When reading results from a different rkf file than ams.rkf the filename has to be specified as:
[code] 
    myEngineProperty = myAMSResults.readrkf(section, variable, file=<engine>)
    
[/code]

whereas <engine> corresponds to the file <engine>.rkf present in the calculation directory.

### From molecular dynamics trajectories¶

#### General MD properties¶

The [`KFHistory`](../interfaces/kffiles.html#scm.plams.tools.kftools.KFHistory "scm.plams.tools.kftools.KFHistory") class can be used to iterate through the History or MDHistory of a trajectory. In this example the energy, temperature and pressure per frame are read and printed.
[code] 
    kf = KFReader(mdjob.results['ams.rkf'])
    hist = KFHistory(kf, "History")
    mdhist = KFHistory(kf, "MDHistory")
    
    frame = 0
    for E, T, p in zip(hist.iter("Energy"), mdhist.iter("Temperature"), mdhist.iter("Pressure")):
        frame += 1
        print("Frame: {} Energy: {} Temperature: {} Pressure: {}".format(frame, E, T, p))
    
[/code]

Properties that can be iterated in this way are

Table 1 General properties in section History¶ Property | Return type | Unit  
---|---|---  
Coords | List of float | bohr  
nLatticeVectors | Int | n.a.  
LatticeVectors | List of float | bohr  
Energy | Float | hartree  
Gradients | List of float | hartree/bohr  
StressTensor | List of float | atomic units  
  
Note

For AMS MD simulations you must set `MolecularDynamics.Trajectory.WriteGradients = "True"` to store the gradients on the ams.rkf file.

Table 2 General MD properties in section MDHistory¶ Property | Return type | Unit  
---|---|---  
Step | Integer | n.a.  
Time | Float | fs  
TotalEnergy | Float | Hartree  
PotentialEnergy | Float | Hartree  
KineticEnergy | Float | Hartree  
Temperature | Float | Kelvin  
ConservedEnergy | Float | Hartree  
Velocities | List of float | bohr/fs  
Charges | List of float | n.a.  
PressureTensor | List of float | hartree/bohr3  
Pressure | Float | hartree/bohr3  
Density | Float | dalton/bohr3  
Number of molecules | Float | n.a.  
  
To read a single property into a numpy array, you can run
[code] 
    import numpy as np
    
    # mdjob is a finished AMSJob
    coords = mdjob.results.get_history_property('Coords', history_section='History')
    coords = np.array(coords).reshape(len(coords), -1, 3) # in bohr
    print(coords.shape)
    
[/code]

Set `history_section='MDHistory'` to read from the MDHistory section.

#### Molecules from trajectories¶

The coordinates of an MD trajectory can efficiently be obtained by creating an [`RKFTrajectoryFile`](../components/rkf.html#scm.plams.trajectories.rkffile.RKFTrajectoryFile "scm.plams.trajectories.rkffile.RKFTrajectoryFile"). To create an instance of [`RKFTrajectoryFile`](../components/rkf.html#scm.plams.trajectories.rkffile.RKFTrajectoryFile "scm.plams.trajectories.rkffile.RKFTrajectoryFile"), simply pass the according ams.rkf file to it. In this example, the atomic coordinates and lattice vectors are read via [`RKFTrajectoryFile`](../components/rkf.html#scm.plams.trajectories.rkffile.RKFTrajectoryFile "scm.plams.trajectories.rkffile.RKFTrajectoryFile") while the PLAMS Molecule function [`get_center_of_mass()`](../components/mol_api.html#scm.plams.mol.molecule.Molecule.get_center_of_mass "scm.plams.mol.molecule.Molecule.get_center_of_mass") to calculate the center of mass for every frame.
[code] 
    rkf = RKFTrajectoryFile(mdjob.results['ams.rkf'])
    mol = rkf.get_plamsmol()
    
    for i in range(rkf.get_length()):
        coords,cell = rkf.read_frame(i,molecule=mol)
        print(coords, cell, mol.get_center_of_mass())
    
[/code]

It is also possible to iterate through the History section of trajectory file. This can be useful in cases were the numbers of atoms is changing per frame or the coordinates per single molecule are needed. Here’s an example where the molecule types present in that particular frame are read for every frame:
[code] 
    kf = KFReader(mdjob.results['ams.rkf'])
    mdhist = KFHistory(kf, "MDHistory")
    hist = KFHistory(kf, "History")
    
    # get number of distinct molecule types and all their formulas
    number_of_molecules = kf.read('Molecules','Num molecules')
    formulas = [ kf.read('Molecules',f'Molecule name {i+1}') for i in range(number_of_molecules) ]
    
    for mols, step in zip( hist.iter("Mols.Type"), mdhist.iter("Step")):
        line = f"{step:8d} "
        for i in sorted(set(mols)): line += f"{formulas[i-1]:s} "
        print(line)
    
[/code]

## Accessing Old Jobs¶

The following illustrates how to load data from previously executed jobs.

### Binding Native PLAMS Jobs¶

Warning

The jobs should be loaded with a version of PLAMS that is consistent with the version originally used to run the jobs.

From an existing PLAMS working directory with the contents
[code] 
    OLDDIR/
    ├── OLDJOB1/
    |   ├── ams.log
    |   ├── ams.rkf
    |   ├── OLDJOB1.dill
    |   ├── OLDJOB1.err
    |   ├── OLDJOB1.in
    |   ├── OLDJOB1.out
    |   ├── OLDJOB1.run
    |   ├── engine.rkf
    |   ├── output.xyz
    ├── input
    └── logfile
    
[/code]

we can bind an instance of the [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") class by making use of the .dill file. The [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") object in turn contains a results object, which gives access to the data previously calculated. This can be achieved using the [`load()`](../components/functions.html#scm.plams.core.functions.load "scm.plams.core.functions.load") function as illustrated in the following snippet:
[code] 
    path       = "OLDDIR/OLDJOB1/OLDJOB1.dill"
    single_JOB = load(path)                                       # AMSJob instance
    if single_JOB.ok():
       energy     = single_JOB.results.get_energy()               # load the desired properties
       structure  = single_JOB.results.get_main_molecule()
       propertyX  = single_JOB.results.readrkf('AMSResults', 'DipoleMoment', file='engine')
    
[/code]

More often than not, the working directory will include multiple individual subdirectories, each containing individual PLAMS job.
[code] 
    OLDDIR/
    ├── OLDJOB1/
    |   ├── ams.log
    |   ├── ams.rkf
    |   ├── OLDJOB1.dill
    |   ├── OLDJOB1.err
    |   ├── OLDJOB1.in
    |   ├── OLDJOB1.out
    |   ├── OLDJOB1.run
    |   ├── engine.rkf
    |   ├── output.xyz
    ├── OLDJOB2/
    |   ├── ams.log
    |   ├── ams.rkf
    |   ├── OLDJOB2.dill
    |   ├── OLDJOB2.err
    |   ├── OLDJOB2.in
    |   ├── OLDJOB2.out
    |   ├── OLDJOB2.run
    |   ├── engine.rkf
    |   ├── output.xyz
    ├── OLDJOB3/
    |   ├── ams.log
    |   ├── ams.rkf
    |   ├── OLDJOB3.dill
    |   ├── OLDJOB3.err
    |   ├── OLDJOB3.in
    |   ├── OLDJOB3.out
    |   ├── OLDJOB3.run
    |   ├── engine.rkf
    |   ├── output.xyz
    ├── input
    └── logfile
    
[/code]

These can be loaded using the [`load_all()`](../components/functions.html#scm.plams.core.functions.load_all "scm.plams.core.functions.load_all") function and by providing only the path to the top-level directory:
[code] 
    path       = "OLDDIR"
    all_JOBS   = load_all(path)
    
[/code]

Note that [`load_all()`](../components/functions.html#scm.plams.core.functions.load_all "scm.plams.core.functions.load_all") wraps the [`load()`](../components/functions.html#scm.plams.core.functions.load "scm.plams.core.functions.load") function used above and therefore requires existing .dill files in each of the loaded subdirectories. The [`load_all()`](../components/functions.html#scm.plams.core.functions.load_all "scm.plams.core.functions.load_all") function yields a dictionary with the paths of the .dill files as keys and the corresponding job object as values:
[code] 
    print(all_JOBS)
    
[/code]
[code] 
    {'/home/user/OLDDIR/OLDJOB1/OLDJOB1.dill': <scm.plams.interfaces.adfsuite.ams.AMSJob object at 0x7f0baad340b8>,
     '/home/user/OLDDIR/OLDJOB2/OLDJOB2.dill': <scm.plams.interfaces.adfsuite.ams.AMSJob object at 0x7f0baacf24a8>,
     '/home/user/OLDDIR/OLDJOB3/OLDJOB3.dill': <scm.plams.interfaces.adfsuite.ams.AMSJob object at 0x7f0baad06cf8>}
    
[/code]

We can now access these [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") instances:
[code] 
    for this_JOB in all_JOBS.values():
       if this_JOB.ok():
          energy     = this_JOB.results.get_energy()
          structure  = this_JOB.results.get_main_molecule()
          propertyX  = this_JOB.results.readrkf('AMSResults', 'DipoleMoment', file='engine')
    
[/code]

### Binding old RKF Files¶

In cases where the .dill files are not available any more, it is still possible to load the contents of previously generated .rkf files into a PLAMS workflow:
[code] 
    path       = "OLDDIR/OLDJOB1/"
    ext_JOB    = AMSJob.load_external(path)
    if ext_JOB.ok():
       energy     = ext_JOB.results.get_energy()
       structure  = ext_JOB.results.get_main_molecule()
    
[/code]

If the .rkf file does originate from some other source than any of the direct AMS engines, also an instance of the more generic [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob") class can be used:
[code] 
    path       = "OLDDIR/OLDJOB1/ams.rkf"
    ext_JOB    = SingleJob.load_external(path)
    
[/code]

The downside of this latter approach is that the accessibility to the data is very limited and has to be implemented mostly in terms of pattern-matching searches in the output files.

An alternative way is to make use of the KFReader class:
[code] 
    path       = "OLDDIR/OLDJOB1/ams.rkf"
    rkf_reader = KFReader(path)
    n_steps    = rkf_reader.read("History", "nEntries")
    energy     = rkf_reader.read("History", "Energy({})".format(n_steps))
    structure  = rkf_reader.read("History", "Coords({})".format(n_steps))
    
[/code]

Note that also the KFReader class lacks most of the shortcut functions of a proper [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") object so that the access to the data has to be specified manually.

## Parallelization¶

### Parallel job execution¶

PLAMS supports running multiple jobs in parallel. Details on the synchronization between parallel job executions can be found [here](../components/results.html#parallel). To make sure your PLAMS script can take maximum advantage of parallel job execution there is a simple rule: Make sure to create and run as many jobs as possible before starting to access any results. (This is because the access to results of a job may block until that job has finished, preventing you to submit more independent jobs in the meantime.)

In the common case where there are _no_ dependencies between jobs, this means that we should set up and run all jobs _before_ starting to access any results. The script below shows how to parallelize the trivially parallel task of just executing the same job on a set of molecules.
[code] 
    mols = read_molecules('my_molecules')
    # mols is a dictionary mapping filenames (without
    # extension) to plams.Molecule instances, e.g.:
    # my_molecules/benzene.xyz would become mols['benzene']
    
    sett = Settings()
    # ... all your settings go here ...
    
    config.default_jobrunner = JobRunner(parallel=True, maxjobs=8)
    sett.runscript.nproc = 4
    # run up to 8 jobs (using 4 cores each) in parallel
    
    jobs    = { n: AMSJob(name=n, settings=sett, molecule=m) for n,m in mols.items() }
    results = { n: j.run() for n,j in jobs.items() }
    # make and run all jobs before accessing any results
    
    for n,r in results.items():
       print(n, r.get_energy() if r.ok() else 'Failed')
    
[/code]

Obviously, `runscript.nproc` could also be set on a per-job basis. This is useful if some of your jobs do not scale well with the number of CPU cores, or if you have jobs of very different computational cost.

### PLAMS scripts under Slurm¶

A PLAMS script can be run under the Slurm batch system and execute jobs within the resource allocation that is created for the script. The script shown in the previous section should work just fine when run under a batch system. The only change you should make is _not_ to set the maximum number of jobs.
[code] 
    config.default_jobrunner = JobRunner(parallel=True)
    
[/code]

Technical

The execution of the job is implemented as a Slurm job step, which may need to wait for free resources before actually starting. As Slurm is taking care of limiting the number of simultaneously executing jobs, we no longer need to do that through the PLAMS [`JobRunner`](../components/runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") and can therefore skip the `maxjobs` argument of its constructor.

Furthermore you may need to wrap the call to the PLAMS [launch script](../started.html#master-script) in a job script, in which we recommend you `cd` to the directory from which the job was submitted. This makes sure you will find the PLAMS working directory in the normal location. (If `$AMSBIN` is not already in your environment, this is also the place to [set up the AMS environment](../../Installation/Installation.html#set-up-the-environment).)
[code] 
    #!/bin/sh
    cd "$SLURM_SUBMIT_DIR"
    $AMSBIN/plams myscript.plms
    
[/code]

The above job script can then simply be submitted to the batch system:
[code] 
    sbatch [...] myscript.sh
    
[/code]

Alternatively you can also skip the job script, and submit the PLAMS [launch script](../started.html#master-script) itself:
[code] 
    sbatch [...] --chdir=. $AMSBIN/plams myscript.plms
    
[/code]

Warning

The integration of PLAMS, AMS and Slurm will only work on Slurm versions >=15. Furthermore AMS needs to use an MPI implementation that is integrated with the Slurm. This is the case for the IntelMPI builds of AMS, but _not_ the OpenMPI builds. Please refer to the [installation manual](../../Installation/Additional_Information_and_Known_Issues.html#running-mpi-jobs) for details on the capabilities of the different MPI versions. If the batch system integration does not work for you, you can still run PLAMS scripts via the batch system, but you will be restricted to running on a single node and will need to use the `maxjobs` argument in the constructor of the [`JobRunner`](../components/runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner") to limit the number of simultaneously running jobs.

[Next ](../citations.html "Citations") [ Previous](../examples/fcf_dos.html "Vibronic Density of States with ADF")

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
