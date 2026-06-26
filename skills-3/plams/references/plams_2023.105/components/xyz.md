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
      * XYZ trajectory files
        * XYZ history files
      * [RKF trajectory files](rkf.html)
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
  * XYZ trajectory files

# XYZ trajectory files¶

_class _`XYZTrajectoryFile`(_filename_ , _mode ='r'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/xyzfile.html#XYZTrajectoryFile)¶
    
Class representing an XYZ file containing a molecular trajectory

An instance of this class has the following attributes:

  * `file_object` – A Python `file` object, referring to the actual XYZ file

  * `position` – The frame to which the cursor is currently pointing in the XYZ file

  * `mode` – Designates whether the file is in read or write mode (‘r’ or ‘w’)

  * `ntap` – The number of atoms in the molecular system (needs to be constant throughout)

  * `elements` – The elements of the atoms in the system (needs to be constant throughout)

An `XYZTrajectoryFile` object behaves very similar to a regular file object. It has read and write methods (`read_next()` and `write_next()`) that read and write from/to the position of the cursor in the `file_object` attribute. If the file is in read mode, an additional method `read_frame()` can be used that moves the cursor to any frame in the file and reads from there. The amount of information stored in memory is kept to a minimum, as only information from the current frame is ever stored.

Reading and writing to and from the files can be done as follows:
[code] 
    >>> from scm.plams import XYZTrajectoryFile
    
    >>> xyz = XYZTrajectoryFile('old.xyz')
    >>> mol = xyz.get_plamsmol()
    
    >>> xyzout = XYZTrajectoryFile('new.xyz',mode='w')
    
    >>> for i in range(xyz.get_length()) :
    >>>     crd,cell = xyz.read_frame(i,molecule=mol)
    >>>     xyzout.write_next(molecule=mol)
    
[/code]

The above script reads information from the XYZ file `old.xyz` into the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object `mol` in a step-by-step manner. The [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object is then passed to the `write_next()` method of the new `XYZTrajectoryFile` object corresponding to the new xyz file `new.xyz`.

The exact same result can also be achieved by iterating over the instance as a callable
[code] 
    >>> xyz = XYZTrajectoryFile('old.xyz')
    >>> mol = xyz.get_plamsmol()
    
[/code]
[code] 
    >>> xyzout = XYZTrajectoryFile('new.xyz',mode='w')
    
[/code]
[code] 
    >>> for crd,cell in xyz(mol) :
    >>>     xyzout.write_next(molecule=mol)
    
[/code]

This procedure requires all coordinate information to be passed to and from the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object for each frame, which can be time-consuming. It is therefore also possible to bypass the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object when reading through the frames:
[code] 
    >>> xyz = XYZTrajectoryFile('old.xyz')
    
    >>> xyzout = XYZTrajectoryFile('new.xyz',mode='w')
    >>> xyzout.set_elements(xyz.get_elements())
    
    >>> for crd,cell in xyz :
    >>>     xyzout.write_next(coords=crd)
    >>> xyzout.close()
    
[/code]

By default the write mode will create a minimal version of the XYZ file, containing only elements and coordinates. Additional information can be written to the file by supplying additional arguments to the `write_next()` method. The additional keywords step and energy trigger the writing of a remark containing the molecule name, the step number, the energy, and the lattice vectors.
[code] 
    >>> mol = Molecule('singleframe.xyz')
    
[/code]
[code] 
    >>> xyzout = XYZTrajectoryFile('new.xyz',mode='w')
    >>> xyzout.set_name('MyMol')
    
[/code]
[code] 
    >>> xyzout.write_next(molecule=mol, step=0, energy=5.)
    
[/code]

`__init__`(_filename_ , _mode ='r'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/xyzfile.html#XYZTrajectoryFile.__init__)¶
    
Initiates an XYZTrajectoryFile object

  * `filename` – The path to the XYZ file

  * `mode` – The mode in which to open the XYZ file (‘r’ or ‘w’)

  * `fileobject` – Optionally, a file object can be passed instead (filename needs to be set to None)

  * `ntap` – If the file is in write mode, the number of atoms needs to be passed here

`store_historydata`()[[source]](../_modules/scm/plams/trajectories/xyzfile.html#XYZTrajectoryFile.store_historydata)¶
    
Additional data should be read from/written to file

`set_name`(_name_)[[source]](../_modules/scm/plams/trajectories/xyzfile.html#XYZTrajectoryFile.set_name)¶
    
Sets the name of the system, in case an extensive write is requested

  * `name` – A string containing the name of the molecule

`read_next`(_molecule =None_, _read =True_)[[source]](../_modules/scm/plams/trajectories/xyzfile.html#XYZTrajectoryFile.read_next)¶
    
Reads coordinates from the current position of the cursor and returns it

  * `molecule` – [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object in which the new coordinates need to be stored

  * `read` – If set to False the cursor will move to the next frame without reading

`write_next`(_coords =None_, _molecule =None_, _cell =[0.0, 0.0, 0.0]_, _conect =None_, _historydata =None_)[[source]](../_modules/scm/plams/trajectories/xyzfile.html#XYZTrajectoryFile.write_next)¶
    
Write frame to next position in trajectory file

  * `coords` – A list or numpy array of (`ntap`,3) containing the system coordinates

  * `molecule` – A molecule object to read the molecular data from

  * `cell` – A set of lattice vectors or cell diameters

  * `conect` – A dictionary containing connectivity info (not used)

  * `historydata` – A dictionary containing additional variables to be written to the comment line

The `historydata` dictionary can contain for example: (‘Step’,’Energy’), the frame number and the energy respectively

Note

Either `coords` or `molecule` are mandatory arguments

`__call__`(_molecule =None_, _read =True_)¶
    
Magic method that makes an instance of this class into a callable

`close`()¶
    
Close the file

`get_elements`()¶
    
Get the elements attribute

`get_length`()¶
    
Get the number of frames in the file

`get_plamsmol`()¶
    
Extracts a PLAMS molecule object from the XYZ trajectory file

_property _`molecule`¶
    
Returns the current molecule, which exists only when the object is used as an iterator

`read_frame`(_frame_ , _molecule =None_)¶
    
Reads the relevant info from frame `frame` and returns it, or stores it in `molecule`

  * `frame` – The frame number to be read from the file

  * `molecule` – [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object in which the new coordinates need to be stored

`read_last_frame`(_molecule =None_)¶
    
Reads the last frame from the file

`rewind`(_nframes =None_)¶
    
Rewind the file either by `nframes` or to the first frame

  * `nframes` – The number of frames to rewind

`set_elements`(_elements_)¶
    
Sets the elements attribute (needed in write mode).

  * `elements` – A list containing the element symbol of each atom

## XYZ history files¶

This subsection describes the API of the `XYZHistoryFile` class, which can read and write the results from simulations with changing numbers of atoms. The majority of molecular simulations explore a subspace of the canonical, micro-canonical, or isothermal-isobaric ensembles, in which the number of atoms \\(N\\) remains constant. However, a Grand Canonical Monte Carlo simulation is one of the exceptions in which the number of atoms in the system does change. The `XYZTrajectoryFile` object cannot read and write the resulting simulation history, and the derived class `XYZHistoryFile` was developed to handle these atypical trajectories. While the methods in this class will be slower than the ones in the parent class, the API is nearly identical. The only exception is the `write_next()` method, which has an additional argument `elements`.

_class _`XYZHistoryFile`(_filename_ , _mode ='r'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/xyzhistoryfile.html#XYZHistoryFile)¶
    
Class representing an XYZ file containing a molecular simulation history with varying numbers of atoms

An instance of this class has the following attributes:

  * `file_object` – A Python `file` object, referring to the actual XYZ file

  * `position` – The frame to which the cursor is currently pointing in the XYZ file

  * `mode` – Designates whether the file is in read or write mode (‘r’ or ‘w’)

  * `elements` – The elements of the atoms in the system at the current frame

An `XYZHistoryFile` object behaves very similar to a regular file object. It has read and write methods (`read_next()` and `write_next()`) that read and write from/to the position of the cursor in the `file_object` attribute. If the file is in read mode, an additional method `read_frame()` can be used that moves the cursor to any frame in the file and reads from there. The amount of information stored in memory is kept to a minimum, as only information from the current frame is ever stored.

Reading and writing to and from the files can be done as follows:
[code] 
    >>> from scm.plams import XYZHistoryFile
    
    >>> xyz = XYZHistoryFile('old.xyz')
    >>> mol = xyz.get_plamsmol()
    
    >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    
    >>> for i in range(xyz.get_length()) :
    >>>     crd,cell = xyz.read_frame(i,molecule=mol)
    >>>     xyzout.write_next(molecule=mol)
    
[/code]

The above script reads information from the XYZ file `old.xyz` into the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object `mol` in a step-by-step manner. The [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object is then passed to the `write_next()` method of the new `XYZHistoryFile` object corresponding to the new xyz file `new.xyz`.

The exact same result can also be achieved by iterating over the instance as a callable
[code] 
    >>> xyz = XYZHistoryFile('old.xyz')
    >>> mol = xyz.get_plamsmol()
    
[/code]
[code] 
    >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    
[/code]
[code] 
    >>> for crd,cell in xyz(mol) :
    >>>     xyzout.write_next(molecule=mol)
    
[/code]

This procedure requires all coordinate information to be passed to and from the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object for each frame, which can be time-consuming. It is therefore also possible to bypass the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object when reading through the frames:
[code] 
    >>> xyz = XYZHistoryFile('old.xyz')
    
    >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    
    >>> for crd,cell in xyz :
    >>>     xyzout.write_next(coords=crd,elements=xyz.elements)
    
[/code]

By default the write mode will create a minimal version of the XYZ file, containing only elements and coordinates. Additional information can be written to the file by supplying additional arguments to the `write_next()` method. The additional keywords step and energy trigger the writing of a remark containing the molecule name, the step number, the energy, and the lattice vectors.
[code] 
    >>> mol = Molecule('singleframe.xyz')
    
[/code]
[code] 
    >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    >>> xyzout.set_name('MyMol')
    
[/code]
[code] 
    >>> xyzout.write_next(molecule=mol, step=0, energy=5.)
    
[/code]

`__init__`(_filename_ , _mode ='r'_, _fileobject =None_, _ntap =None_)[[source]](../_modules/scm/plams/trajectories/xyzhistoryfile.html#XYZHistoryFile.__init__)¶
    
Initiates an XYZHistoryFile object

  * `filename` – The path to the XYZ file

  * `mode` – The mode in which to open the XYZ file (‘r’ or ‘w’)

  * `fileobject` – Optionally, a file object can be passed instead (filename needs to be set to None)

  * `ntap` – If the file is in write mode, the number of atoms can be passed here

`write_next`(_coords =None_, _molecule =None_, _elements =None_, _cell =[0.0, 0.0, 0.0]_, _conect =None_, _historydata =None_)[[source]](../_modules/scm/plams/trajectories/xyzhistoryfile.html#XYZHistoryFile.write_next)¶
    
Write frame to next position in trajectory file

  * `coords` – A list or numpy array of (`ntap`,3) containing the system coordinates

  * `molecule` – A molecule object to read the molecular data from

  * `elements` – The element symbols of the atoms in the system

  * `cell` – A set of lattice vectors or cell diameters

  * `energy` – An energy value to be written to the remark line

  * `conect` – A dictionary containing connectivity info (not used)

  * `historydata` – A dictionary containing additional variables to be written to the comment line

The `historydata` dictionary can contain for example: (‘Step’,’Energy’), the frame number and the energy respectively

Note

Either `coords` and `elements` or `molecule` are mandatory arguments

[Next ](rkf.html "RKF trajectory files") [ Previous](trajectories.html "Trajectories")

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
