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
    * Utilities
      * Periodic Table
      * Units
      * Geometry tools
      * File format conversion tools
      * Plotting tools
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
  * Utilities

# Utilities¶

Presented here is a small set of useful utility tools that can come handy in various contexts in your scripts. They are simple, standalone objects always present in the main namespace.

  * Periodic Table

  * Units

  * Geometry tools

  * File format conversion tools

  * Plotting tools

What is characteristic for the `PeriodicTable` and `Units` classes described below is that they are meant to be used in a bit different way than all other PLAMS classes. Usually one takes a class (like `DiracJob`), creates an instance of it (`myjob = DiracJob(...)`) and executes some of its methods (`r = myjob.run()`). In contrast, utility classes are designed in a way similar to so called singleton design pattern. That means it is not possible to create any instances of these classes. The class itself serves for “one and only instance” and all methods should be called using the class as the calling object:
[code] 
    >>> x = PeriodicTable()
    PTError: Instances of PeriodicTable cannot be created
    >>> s = PeriodicTable.get_symbol(20)
    >>> print(s)
    Ca
    
[/code]

## Periodic Table¶

_class _`PeriodicTable`[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable)¶
    
A singleton class for the periodic table of elements.

For each element the following properties are stored: atomic symbol, atomic mass, atomic radius and number of connectors.

Atomic mass is, strictly speaking, atomic weight, as present in Mathematica’s ElementData function.

Atomic radius and number of connectors are used by [`guess_bonds()`](mol_api.html#scm.plams.mol.molecule.Molecule.guess_bonds "scm.plams.mol.molecule.Molecule.guess_bonds"). Note that values of radii are neither atomic radii nor covalent radii. They are somewhat “emprically optimized” for the bond guessing algorithm.

Note

This class is visible in the main namespace as both `PeriodicTable` and `PT`.

`__init__`()[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

_classmethod _`get_atomic_number`(_symbol_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_atomic_number)¶
    
Convert atomic symbol to atomic number.

_classmethod _`get_symbol`(_atnum_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_symbol)¶
    
Convert atomic number to atomic symbol.

_classmethod _`get_mass`(_arg_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_mass)¶
    
Convert atomic symbol or atomic number to atomic mass.

_classmethod _`get_radius`(_arg_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_radius)¶
    
Convert atomic symbol or atomic number to radius.

_classmethod _`get_connectors`(_arg_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_connectors)¶
    
Convert atomic symbol or atomic number to number of connectors.

_classmethod _`get_metallic`(_arg_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_metallic)¶
    
Convert atomic symbol or atomic number to number of connectors.

_classmethod _`get_electronegative`(_arg_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.get_electronegative)¶
    
Convert atomic symbol or atomic number to number of connectors.

_classmethod _`set_mass`(_element_ , _value_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.set_mass)¶
    
Set the mass of _element_ to _value_.

_classmethod _`set_radius`(_element_ , _value_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.set_radius)¶
    
Set the radius of _element_ to _value_.

_classmethod _`set_connectors`(_element_ , _value_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable.set_connectors)¶
    
Set the number of connectors of _element_ to _value_.

_classmethod _`_get_property`(_arg_ , _prop_)[[source]](../_modules/scm/plams/tools/periodic_table.html#PeriodicTable._get_property)¶
    
Get property of element described by either symbol or atomic number. Skeleton method for `get_radius()`, `get_mass()` and `get_connectors()`.

## Units¶

_class _`Units`[[source]](../_modules/scm/plams/tools/units.html#Units)¶
    
A singleton class for unit converter.

All values are based on [2014 CODATA recommended values](http://physics.nist.gov/cuu/Constants).

The following constants and units are supported:

  * constants:

    * `speed_of_light` (also `c`)

    * `electron_charge` (also `e`)

    * `Avogadro_constant` (also `NA`)

    * `Bohr_radius`

  * distance:

    * `Angstrom`, `A`

    * `Bohr`, `au`, `a.u.`

    * `nm`

    * `pm`

  * reciprocal distance:

    * `1/Angstrom`, `1/A`, `Angstrom^-1`, `A^-1`,

    * `1/Bohr`, `Bohr^-1`

  * angle:

    * `degree`, `deg`,

    * `radian`, `rad`,

    * `grad`

    * `circle`

  * energy:

    * `au`, `a.u.`, `Hartree`

    * `eV`

    * `kcal/mol`

    * `kJ/mol`

    * `cm^-1`, `cm-1`

    * `K`, `Kelvin`

  * dipole moment:

    * `au`, `a.u.`

    * `Cm`

    * `Debye`, `D`

  * forces:

    * All energy units divided by angstrom or bohr, for example

    * `eV/angstrom`

    * `hartree/bohr`

  * hessian:

    * All energy units divided by angstrom^2 or bohr^2, for example

    * `eV/angstrom^2`

    * `hartree/bohr^2`

  * pressure:

    * All energy units divided by angstrom^3 or bohr^3, for example

    * `eV/angstrom^3`

    * `hartree/bohr^3`

    * And some more:

    * `Pa`

    * `GPa`

    * `bar`

    * `atm`

Example:
[code] 
    >>> print(Units.constants['speed_of_light'])
    299792458
    >>> print(Units.constants['e'])
    1.6021766208e-19
    >>> print(Units.convert(123, 'angstrom', 'bohr'))
    232.436313431
    >>> print(Units.convert([23.32, 145.0, -34.7], 'kJ/mol', 'kcal/mol'))
    [5.573613766730401, 34.655831739961755, -8.293499043977056]
    >>> print(Units.conversion_ratio('kcal/mol', 'kJ/mol'))
    4.184
    
[/code]

`__init__`()[[source]](../_modules/scm/plams/tools/units.html#Units.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

_classmethod _`conversion_ratio`(_inp_ , _out_)[[source]](../_modules/scm/plams/tools/units.html#Units.conversion_ratio)¶
    
Return conversion ratio from unit _inp_ to _out_.

_classmethod _`convert`(_value_ , _inp_ , _out_)[[source]](../_modules/scm/plams/tools/units.html#Units.convert)¶
    
Convert _value_ from unit _inp_ to _out_.

_value_ can be a single number or a container (list, tuple, numpy.array etc.). In the latter case a container of the same type and length is returned. Conversion happens recursively, so this method can be used to convert, for example, a list of lists of numbers, or any other hierarchical container structure. Conversion is applied on all levels, to all values that are numbers (also numpy number types). All other values (strings, bools etc.) remain unchanged.

_classmethod _`ascii2unicode`(_string_)[[source]](../_modules/scm/plams/tools/units.html#Units.ascii2unicode)¶
    
Converts ‘^2’ to ‘²’ etc., for prettier printing of units.

## Geometry tools¶

A small module with simple functions related to 3D geometry operations.

`rotation_matrix`(_vec1_ , _vec2_)[[source]](../_modules/scm/plams/tools/geometry.html#rotation_matrix)¶
    
Calculate the rotation matrix rotating _vec1_ to _vec2_. Vectors can be any containers with 3 numerical values. They don’t need to be normalized. Returns 3x3 numpy array.

`axis_rotation_matrix`(_vector_ , _angle_ , _unit ='radian'_)[[source]](../_modules/scm/plams/tools/geometry.html#axis_rotation_matrix)¶
    
Calculate the rotation matrix rotating along the _vector_ by _angle_ expressed in _unit_.

_vector_ can be any container with 3 numerical values. They don’t need to be normalized. A positive angle denotes counterclockwise rotation, when looking along _vector_. Returns 3x3 numpy array.

`distance_array`(_array1_ , _array2_)[[source]](../_modules/scm/plams/tools/geometry.html#distance_array)¶
    
Calculates distance between each pair of points in _array1_ and _array2_. Returns 2D `numpy` array.

Uses fast `cdist` function if `scipy` is present, otherwise falls back to slightly slower `numpy` loop. Arguments should be 2-dimensional `numpy` arrays with the same second dimension. If _array1_ is A x N and _array2_ is B x N, the returned array is A x B.

`angle`(_vec1_ , _vec2_ , _result_unit ='radian'_)[[source]](../_modules/scm/plams/tools/geometry.html#angle)¶
    
Calculate an angle between vectors _vec1_ and _vec2_.

_vec1_ and _vec2_ should be iterable containers of length 3 (for example: tuple, list, numpy array). Values stored in them are expressed in Angstrom. Returned value is expressed in _result_unit_.

This method requires all atomic coordinates to be numerical values, `TypeError` is raised otherwise.

`dihedral`(_p1_ , _p2_ , _p3_ , _p4_ , _unit ='radian'_)[[source]](../_modules/scm/plams/tools/geometry.html#dihedral)¶
    
Calculate the value of diherdal angle formed by points _p1_ , _p2_ , _p3_ and _p4_ in a 3D space. Arguments can be any containers with 3 numerical values, also instances of [`Atom`](atombond.html#scm.plams.mol.atom.Atom "scm.plams.mol.atom.Atom"). Returned value is always non-negative, measures the angle clockwise (looking along _p2-p3_ vector) and is expressed in _unit_.

`cell_shape`(_lattice_)[[source]](../_modules/scm/plams/tools/geometry.html#cell_shape)¶
    
Converts lattice vectors to lengths and angles (in radians) Sets internal cell size data, based on set of cell vectors.

_cellvectors_ is list containing three cell vectors (a 3x3 matrix)

`cellvectors_from_shape`(_box_)[[source]](../_modules/scm/plams/tools/geometry.html#cellvectors_from_shape)¶
    
Converts lengths and angles (in radians) of lattice vectors to the lattice vectors

## File format conversion tools¶

A small module for converting VASP output to AMS-like output, and for converting ASE .traj trajectory files to the .rkf format.

`traj_to_rkf`(_trajfile_ , _rkftrajectoryfile_ , _task =None_, _timestep =0.25_)[[source]](../_modules/scm/plams/tools/converters.html#traj_to_rkf)¶
    
Convert ase .traj file to .rkf file. NOTE: The order of atoms (or the number of atoms) cannot change between frames!

trajfilestr
    
path to a .traj file

rkftrajectoryfilestr 
    
path to the output .rkf file (will be created)

taskstr
    
Which task to write. If None it is auto-determined.

timestep: float
    
Which timestep to write when task == ‘moleculardynamics’

Returns2-tuple (coords, cell)
    
The final coordinates and cell in angstrom

`vasp_output_to_ams`(_vasp_folder_ , _wdir =None_, _overwrite =False_, _write_engine_rkf =True_, _task =None_, _timestep =0.25_)[[source]](../_modules/scm/plams/tools/converters.html#vasp_output_to_ams)¶
    
Converts VASP output (OUTCAR, …) to AMS output (ams.rkf, vasp.rkf)

Returns: a string containing the directory where ams.rkf was written

vasp_folderstr
    
path to a directory with an OUTCAR, INCAR, POTCAR etc. files

wdirstr or None
    
directory in which to write the ams.rkf and vasp.rkf files If None, a subdirectory “AMSJob” of vasp_folder will be created

overwritebool
    
if False, first check if wdir already contains ams.rkf and vasp.rkf, in which case do nothing if True, overwrite if exists

write_engine_rkfbool
    
If True, also write vasp.rkf alongside ams.rkf. The vasp.rkf file will only contain an AMSResults section (energy, gradients, stress tensor). It will not contain the DOS or the band structure.

taskstr
    
Which task to write to ams.rkf. If None it is auto-determined (probably set to ‘geometryoptimization’)

timestepfloat
    
If task=’moleculardynamics’, which timestep (in fs) between frames to write

`qe_output_to_ams`(_qe_outfile_ , _wdir =None_, _overwrite =False_, _write_engine_rkf =True_)[[source]](../_modules/scm/plams/tools/converters.html#qe_output_to_ams)¶
    
Converts a qe .out file to ams.rkf and qe.rkf.

Returns: a string containing the directory where ams.rkf was written

If the filename ends in .out, check if a .results directory exists. In that case, place the AMSJob subdirectory in the .results directory.

Otherwise, create a new directory called filename.AMSJob

qe_outfilestr
    
path to the qe output file

`gaussian_output_to_ams`(_outfile_ , _wdir =None_, _overwrite =False_, _write_engine_rkf =True_)[[source]](../_modules/scm/plams/tools/converters.html#gaussian_output_to_ams)¶
    
Converts a Gaussian .out file to ams.rkf and gaussian.rkf.

Returns: a string containing the directory where ams.rkf was written

If the filename ends in .out, check if a .results directory exists. In that case, place the AMSJob subdirectory in the .results directory.

Otherwise, create a new directory called filename.AMSJob

outfilestr
    
path to the gaussian output file

`rkf_to_ase_traj`(_rkf_file_ , _out_file_ , _get_results =True_)[[source]](../_modules/scm/plams/tools/converters.html#rkf_to_ase_traj)¶
    
Convert an ams.rkf trajectory to a different trajectory format (.xyz, .traj, anything supported by ASE)

rkf_file: str
    
Path to an ams.rkf file

out_file: str
    
Path to the .traj or .xyz file that will be created. If the file exists it will be overwritten. If a .xyz file is specified it will use the normal ASE format (not the AMS format).

get_results: bool
    
Whether to include results like energy, forces, and stress in the trajectory.

`rkf_to_ase_atoms`(_rkf_file_ , _get_results =True_)[[source]](../_modules/scm/plams/tools/converters.html#rkf_to_ase_atoms)¶
    
Convert an ams.rkf trajectory to a list of ASE atoms

rkf_file: str
    
Path to an ams.rkf file

out_file: str
    
Path to the .traj or .xyz file that will be created. If the file exists it will be overwritten. If a .xyz file is specified it will use the normal ASE format (not the AMS format).

get_results: bool
    
Whether to include results like energy, forces, and stress in the trajectory.

Returns: a list of all the ASE Atoms objects.

`file_to_traj`(_outfile_ , _trajfile_)[[source]](../_modules/scm/plams/tools/converters.html#file_to_traj)¶
    
outfilestr
    
path to existing file (OUTCAR, qe.out, etc.)

trajfilestr
    
will be created

## Plotting tools¶

See also

  * [Band structure](../examples/BandStructure/BandStructure.html#bandstructureexample)

Tools for creating plots with matplotlib.

`plot_band_structure`(_x_ , _y_spin_up_ , _y_spin_down =None_, _labels =None_, _fermi_energy =None_, _zero =None_, _show =False_)[[source]](../_modules/scm/plams/tools/plot.html#plot_band_structure)¶
    
Plots an electronic band structure from DFTB or BAND with matplotlib.

To control the appearance of the plot you need to call `plt.ylim(bottom, top)`, `plt.title(title)`, etc. manually outside this function.

x: list of float
    
Returned by AMSResults.get_band_structure()

y_spin_up: 2D numpy array of float
    
Returned by AMSResults.get_band_structure()

y_spin_down: 2D numpy array of float. If None, the spin down bands are not plotted.
    
Returned by AMSResults.get_band_structure()

labels: list of str
    
Returned by AMSResults.get_band_structure()

fermi_energy: float
    
Returned by AMSResults.get_band_structure(). Should have the same unit as `y`.

zero: None or float or one of ‘fermi’, ‘vbmax’, ‘cbmin’
    
Shift the curves so that y=0 is at the specified value. If None, no shift is performed. ‘fermi’, ‘vbmax’, and ‘cbmin’ require that the `fermi_energy` is not None. Note: ‘vbmax’ and ‘cbmin’ calculate the zero as the highest (lowest) eigenvalue smaller (greater) than or equal to `fermi_energy`. This is NOT necessarily equal to the valence band maximum or conduction band minimum as calculated by the compute engine.

show: bool
    
If True, call plt.show() at the end

`plot_molecule`(_molecule_ , _figsize =None_, _ax =None_, _** kwargs_)[[source]](../_modules/scm/plams/tools/plot.html#plot_molecule)¶
    
Show a molecule in a Jupyter notebook

[Next ](trajectories.html "Trajectories") [ Previous](mol_packmol.html "Packmol interface")

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
