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
    * [Public functions](functions.html)
    * [Molecule](molecule.html)
    * [Utilities](utils.html)
    * [Trajectories](trajectories.html)
      * [XYZ trajectory files](xyz.html)
      * RKF trajectory files
        * RKF history files
      * [DCD trajectory files](dcd.html)
      * [Trajectory class](trajectory.html)
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Components overview](components.html)/
  * [Trajectories](trajectories.html)/
  * RKF trajectory files

# RKF trajectory files¶

_class _`RKFTrajectoryFile`(_filename_ , _mode ='rb'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile)¶
    
Class representing an RKF file containing a molecular trajectory

An instance of this class has the following attributes:

  * `file_object` – A PLAMS [`KFFile`](../interfaces/kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile") object, referring to the actual RKF file

  * `position` – The frame to which the cursor is currently pointing in the RKF file

  * `mode` – Designates whether the file is in read or write mode (‘rb’ or ‘wb’)

  * `ntap` – The number of atoms in the molecular system (needs to be constant throughout)

  * `elements` – The elements of the atoms in the system (needs to be constant throughout)

  * `conect` – The connectivity information of the current frame

  * `mddata` – Read mode only: A dictionary containing data from the MDHistory section in the RKF file

  * `read_lattice`– Read mode only: Wether the lattice vectors will be read from the file

  * `read_bonds` – Wether the connectivity information will be read from the file

  * `saving_freq` – How often the ‘wb’ file is written (default: only when `close()` is called)

An `RKFTrajectoryFile` object behaves very similar to a regular file object. It has read and write methods (`read_next()` and `write_next()`) that read and write from/to the position of the cursor in the `file_object` attribute. If the file is in read mode, an additional method `read_frame()` can be used that moves the cursor to any frame in the file and reads from there. The amount of information stored in memory is kept to a minimum, as only information from the latest frame is ever stored.

Reading and writing to and from the files can be done as follows:
[code] 
    >>> from scm.plams import RKFTrajectoryFile
    
    >>> rkf = RKFTrajectoryFile('ams.rkf')
    >>> mol = rkf.get_plamsmol()
    
    >>> rkfout = RKFTrajectoryFile('new.rkf',mode='wb')
    
    >>> for i in range(rkf.get_length()) :
    >>>     crd,cell = rkf.read_frame(i,molecule=mol)
    >>>     rkfout.write_next(molecule=mol)
    >>> rkfout.close()
    
[/code]

The above script reads information from the RKF file `ams.rkf` into the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object `mol` in a step-by-step manner. The [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object is then passed to the `write_next()` method of the new `RKFTrajectoryFile` object corresponding to the new rkf file `new.rkf`.

The exact same result can also be achieved by iterating over the instance as a callable
[code] 
    >>> rkf = RKFTrajectoryFile('ams.rkf')
    >>> mol = rkf.get_plamsmol()
    
[/code]
[code] 
    >>> rkfout = RKFTrajectoryFile('new.rkf',mode='wb')
    
[/code]
[code] 
    >>> for crd,cell in rkf(mol) :
    >>>     rkfout.write_next(molecule=mol)
    >>> rkfout.close()
    
[/code]

This procedure requires all coordinate information to be passed to and from the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object for each frame, which can be time-consuming. Some time can be saved by bypassing the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object:
[code] 
    >>> rkf = RKFTrajectoryFile('ams.rkf')
    
    >>> rkfout = RKFTrajectoryFile('new.rkf',mode='wb')
    >>> rkfout.set_elements(rkf.get_elements())
    
    >>> for crd,cell in rkf :
    >>>     rkfout.write_next(coords=crd,cell=cell,conect=rkf.conect)
    >>> rkfout.close()
    
[/code]

The only mandatory argument to the `write_next()` method is `coords`. Further time can be saved by setting the `read_lattice` and `read_bonds` variables to False.

By default the write mode will create a minimal version of the RKF file, containing only elements, coordinates, lattice, and connectivity information. This minimal file format can be read by AMSMovie.

It is possible to store additional information, such as energies, velocities, and charges. To enable this, the method `store_mddata()` needs to be called after creation, and a dictionary of mddata needs to be passed to the `write_next()` method. When that is done, the AMS trajectory analysis tools can be used on the file. Restarting an MD run with such a file is however currently not possible:
[code] 
    >>> rkf = RKFTrajectoryFile('ams.rkf')
    >>> rkf.store_mddata()
    >>> mol = rkf.get_plamsmol()
    
    >>> rkf_out = RKFTrajectoryFile('new.rkf',mode='wb')
    >>> rkf_out.store_mddata(rkf)
    
    >>> for i in range(len(rkf)) :
    >>>         crd,cell = rkf.read_frame(i,molecule=mol)
    >>>         rkf_out.write_next(molecule=mol,mddata=rkf.mddata)
    >>> rkf_out.close()
    
[/code]

`__init__`(_filename_ , _mode ='rb'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.__init__)¶
    
Initiates an RKFTrajectoryFile object

  * `filename` – The path to the RKF file

  * `mode` – The mode in which to open the RKF file (‘rb’ or ‘wb’)

  * `fileobject` – Optionally, a file object can be passed instead (filename needs to be set to None)

  * `ntap` – If the file is in write mode, the number of atoms needs to be passed here

`store_mddata`(_rkf =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.store_mddata)¶
    
Read/write an MDHistory section

  * `rkf` – If in write mode an RKFTrajectoryFile object in read mode needs to be passed to extract unit info

`store_historydata`()[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.store_historydata)¶
    
Read/write non-standard entries in the History section

`close`(_override_molecule_section_with_last_frame =True_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.close)¶
    
Execute all prior commands and cleanly close and garbage collect the RKF file

`_rewrite_molecule`()[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile._rewrite_molecule)¶
    
Overwrite the molecule section with the latest frame

`_update_celldata`(_cell_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile._update_celldata)¶
    
Use the newly supplied cell to update the dimensionality of the system

`get_plamsmol`()[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.get_plamsmol)¶
    
Extracts a PLAMS molecule object from the RKF file

`read_frame`(_i_ , _molecule =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.read_frame)¶
    
Reads the relevant info from frame `i` and returns it, or stores it in `molecule`

  * `i` – The frame number to be read from the RKF file

  * `molecule` – [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object in which the new coordinates need to be stored

`_store_historydata_for_step`(_istep_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile._store_historydata_for_step)¶
    
Store the extra data from the History section

`read_next`(_molecule =None_, _read =True_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.read_next)¶
    
Reads coordinates and lattice vectors from the current position of the cursor and returns it

  * `molecule` – [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object in which the new coordinates need to be stored

  * `read` – If set to False the cursor will move to the next frame without reading

`write_next`(_coords =None_, _molecule =None_, _cell =[0.0, 0.0, 0.0]_, _conect =None_, _historydata =None_, _mddata =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.write_next)¶
    
Write frame to next position in trajectory file

  * `coords` – A list or numpy array of (`ntap`,3) containing the system coordinates in angstrom

  * `molecule` – A molecule object to read the molecular data from

  * `cell` – A set of lattice vectors (or cell diameters for an orthorhombic system) in angstrom

  * `conect` – A dictionary containing the connectivity info (e.g. {1:[2],2:[1]})

  * `historydata` – A dictionary containing additional variables to be written to the History section

  * `mddata` – A dictionary containing the variables to be written to the MDHistory section

The `mddata` dictionary can contain the following keys: (‘TotalEnergy’, ‘PotentialEnergy’, ‘Step’, ‘Velocities’, ‘KineticEnergy’, ‘Charges’, ‘ConservedEnergy’, ‘Time’, ‘Temperature’)

The `historydata` dictionary can contain for example: (‘Energy’,’Gradients’,’StressTensor’) All values must be in atomic units Numpy arrays or lists of lists will be flattened before they are written to the file

Note

Either `coords` or `molecule` are mandatory arguments

`_set_energy`(_mddata_ , _historydata_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile._set_energy)¶
    
Looks if an energy is passed as input, and it not, sets to zero

`_write_dictionary_to_history`(_data_ , _section_ , _counter =1_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile._write_dictionary_to_history)¶
    
Add the entries of a dictionary to a History section

`_flatten_variable`(_var_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile._flatten_variable)¶
    
Make sure that the variable is a Python 1D list (not numpy)

`rewind`(_nframes =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.rewind)¶
    
Rewind the file either by `nframes` or to the first frame

  * `nframes` – The number of frames to rewind

`get_length`()[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.get_length)¶
    
Get the number of frames in the file

`read_last_frame`(_molecule =None_)[[source]](../_modules/scm/plams/trajectories/rkffile.html#RKFTrajectoryFile.read_last_frame)¶
    
Reads the last frame from the file

## RKF history files¶

This subsection describes the API of the `RKFHistoryFile` class, which can read and write the results from simulations with changing numbers of atoms. The majority of molecular simulations explore a subspace of the canonical, micro-canonical, or isothermal-isobaric ensembles, in which the number of atoms \\(N\\) remains constant. However, a Grand Canonical Monte Carlo simulation is one of the exceptions in which the number of atoms in the system does change. The `RKFTrajectoryFile` object cannot read and write the resulting simulation history, and the derived class `RKFHistoryFile` was developed to handle these atypical trajectories. While the methods in this class will be slower than the ones in the parent class, the API is nearly identical. The only exception is the `write_next()` method, which has an additional argument `elements`.

_class _`RKFHistoryFile`(_filename_ , _mode ='rb'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile)¶
    
Class representing an RKF file containing a molecular simulation history with varying numbers of atoms

An instance of this class has the following attributes:

  * `file_object` – A PLAMS [`KFFile`](../interfaces/kffiles.html#scm.plams.tools.kftools.KFFile "scm.plams.tools.kftools.KFFile") object, referring to the actual RKF file

  * `position` – The frame to which the cursor is currently pointing in the RKF file

  * `mode` – Designates whether the file is in read or write mode (‘rb’ or ‘wb’)

  * `elements` – The elements of the atoms in the system at the current frame

  * `conect` – The connectivity information of the current frame

  * `mddata` – Read mode only: A dictionary containing data from the MDHistory section in the RKF file

  * `read_lattice`– Read mode only: Wether the lattice vectors will be read from the file

  * `read_bonds` – Wether the connectivity information will be read from the file

An `RKFHistoryFile` object behaves very similar to a regular file object. It has read and write methods (`read_next()` and `write_next()`) that read and write from/to the position of the cursor in the `file_object` attribute. If the file is in read mode, an additional method `read_frame()` can be used that moves the cursor to any frame in the file and reads from there. The amount of information stored in memory is kept to a minimum, as only information from the latest frame is ever stored.

Reading and writing to and from the files can be done as follows:
[code] 
    >>> from scm.plams import RKFHistoryFile
    
    >>> rkf = RKFHistoryFile('ams.rkf')
    >>> mol = rkf.get_plamsmol()
    
    >>> rkfout = RKFHistoryFile('new.rkf',mode='wb')
    
    >>> for i in range(rkf.get_length()) :
    >>>     crd,cell = rkf.read_frame(i,molecule=mol)
    >>>     rkfout.write_next(molecule=mol)
    >>> rkfout.close()
    
[/code]

The above script reads information from the RKF file `ams.rkf` into the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object `mol` in a step-by-step manner.. The [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object is then passed to the `write_next()` method of the new `RKFHistoryFile` object corresponding to the new rkf file `new.rkf`.

The exact same result can also be achieved by iterating over the instance as a callable
[code] 
    >>> rkf = RKFHistoryFile('ams.rkf')
    >>> mol = rkf.get_plamsmol()
    
[/code]
[code] 
    >>> rkfout = RKFHistoryFile('new.rkf',mode='wb')
    
[/code]
[code] 
    >>> for crd,cell in rkf(mol) :
    >>>     rkfout.write_next(molecule=mol)
    >>> rkfout.close()
    
[/code]

This procedure requires all coordinate information to be passed to and from the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object for each frame, which can be time-consuming. Some time can be saved by bypassing the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object:
[code] 
    >>> rkf = RKFHistoryFile('ams.rkf')
    
    >>> rkfout = RKFHistoryFile('new.rkf',mode='wb')
    
    >>> for crd,cell in rkf :
    >>>     rkfout.write_next(coords=crd,cell=cell,elements=rkf.elements,conect=rkf.conect)
    >>> rkfout.close()
    
[/code]

The only mandatory argument to the `write_next()` method is `coords`. Further time can be saved by setting the `read_lattice` and `read_bonds` variables to False.

By default the write mode will create a minimal version of the RKF file, containing only elements, coordinates, lattice, and connectivity information. This minimal file format can be read by AMSMovie.

If the original RKF file contains an MDHistory section (if it resulted from a MolecularGun simulation) it is possible to store the information from that section and write it to another file. To enable this, the method `store_mddata()` needs to be called after creation, and a dictionary of mddata needs to be passed to the `write_next()` method. When that is done, the AMS trajectory analysis tools can be used on the file. Restarting an MD run with such a file is however currently not possible:
[code] 
    >>> rkf = RKFHistoryFile('ams.rkf')
    >>> rkf.store_mddata()
    >>> mol = rkf.get_plamsmol()
    
    >>> rkf_out = RKFHistoryFile('new.rkf',mode='wb')
    >>> rkf_out.store_mddata(rkf)
    
    >>> for i in range(rkf.get_length()) :
    >>>         crd,cell = rkf.read_frame(i,molecule=mol)
    >>>         rkf_out.write_next(molecule=mol,mddata=rkf.mddata)
    >>> rkf_out.close()
    
[/code]

`__init__`(_filename_ , _mode ='rb'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile.__init__)¶
    
Initializes the RKFHistoryFile object

  * `filename` – The path to the RKF file

  * `mode` – The mode in which to open the RKF file (‘rb’ or ‘wb’)

  * `fileobject` – Optionally, a file object can be passed instead (filename needs to be set to None)

  * `ntap` – If the file is in write mode, the number of atoms can be passed here

`get_plamsmol`()[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile.get_plamsmol)¶
    
Extracts a PLAMS molecule object from the RKF file

`_rewrite_molecule`()[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile._rewrite_molecule)¶
    
Overwrite the molecule section with the latest frame (called in close())

`_correct_chemical_system`(_elements_ , _prev_elements_ , _added_atoms_ , _removed_atoms_)[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile._correct_chemical_system)¶
    
Check if the referenced chemical system is correct, and if not, find one matching added/removed atoms

`write_next`(_coords =None_, _molecule =None_, _elements =None_, _cell =[0.0, 0.0, 0.0]_, _conect =None_, _historydata =None_, _mddata =None_)[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile.write_next)¶
    
Write frame to next position in trajectory file

  * `coords` – A list or numpy array of (`ntap`,3) containing the system coordinates

  * `molecule` – A molecule object to read the molecular data from

  * `elements` – The element symbols of the atoms in the system

  * `cell` – A set of lattice vectors (or cell diameters for an orthorhombic system)

  * `conect` – A dictionary containing the connectivity info (e.g. {1:[2],2:[1]})

  * `historydata` – A dictionary containing additional variables to be written to the History section

  * `mddata` – A dictionary containing the variables to be written to the MDHistory section

The `mddata` dictionary can contain the following keys: (‘TotalEnergy’, ‘PotentialEnergy’, ‘Step’, ‘Velocities’, ‘KineticEnergy’, ‘Charges’, ‘ConservedEnergy’, ‘Time’, ‘Temperature’)

The `historydata` dictionary can contain for example: (‘Energy’,’Gradients’,’StressTensor’) All values must be in atomic units Numpy arrays or lists of lists will be flattened before they are written to the file

Note

Either `coords` and `elements` or `molecule` are mandatory arguments

`_set_system_version_elements`()[[source]](../_modules/scm/plams/trajectories/rkfhistoryfile.html#RKFHistoryFile._set_system_version_elements)¶
    
Store all chemical systems from the file

[Next ](dcd.html "DCD trajectory files") [ Previous](xyz.html "XYZ trajectory files")

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
