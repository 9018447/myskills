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
      * [Molecule](mol_api.html)
      * Atom
      * Bond
      * [RDKit interface](mol_rdkit.html)
      * [ASE interface](mol_ase.html)
      * [Packmol interface](mol_packmol.html)
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
  * [Molecule](molecule.html)/
  * Atom

# Atom¶

_class _`Atom`(_atnum =0_, _symbol =None_, _coords =None_, _unit ='angstrom'_, _bonds =None_, _mol =None_, _** other_)[[source]](../_modules/scm/plams/mol/atom.html#Atom)¶
    
A class representing a single atom in three dimensional space.

An instance of this class has the following attributes:

  * `atnum` – atomic number (zero for “dummy atoms”)

  * `coords` – tuple of length 3 storing spatial coordinates

  * `bonds` – list of bonds (see `Bond`) this atom is a part of

  * `mol` – [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") this atom belongs to

  * `properties` – [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance storing all other information about this atom (initially it is populated with _**other_)

The above attributes can be accessed either directly or using one of the following properties:

  * `x`, `y`, `z` – allow to read or modify each coordinate separately

  * `symbol` – allows to read or write the atomic symbol directly. Atomic symbol is not stored as an attribute, instead of that the atomic number (`atnum`) indicates the type of atom. In fact, `symbol` this is just a wrapper around `atnum` that uses [`PeriodicTable`](utils.html#scm.plams.tools.periodic_table.PeriodicTable "scm.plams.tools.periodic_table.PeriodicTable") as a translator:
[code] >>> a = Atom(atnum=8)
        >>> print(a.symbol)
        O
        >>> a.symbol = 'Ca'
        >>> print(a.atnum)
        20
        
[/code]

  * `mass` – atomic mass, obtained from [`PeriodicTable`](utils.html#scm.plams.tools.periodic_table.PeriodicTable "scm.plams.tools.periodic_table.PeriodicTable"), read only

  * `radius` – atomic radius, obtained from [`PeriodicTable`](utils.html#scm.plams.tools.periodic_table.PeriodicTable "scm.plams.tools.periodic_table.PeriodicTable"), read only

  * `connectors` – number of connectors, obtained from [`PeriodicTable`](utils.html#scm.plams.tools.periodic_table.PeriodicTable "scm.plams.tools.periodic_table.PeriodicTable"), read only

Note

When creating a new atom, its type can be chosen either by setting an atomic number or a symbol (`atnum` and `symbol` constructor arguments). The `symbol` argument takes precedence – if it is supplied, the `atnum` argument is ignored.

Values stored in `coords` tuple do not necessarily have to be numeric, you can also store any string there. This might come handy for programs that allow parametrization of coordinates in the input file (to enforce some geometry constraints for example):
[code] 
    >>> a = Atom(symbol='C', coords=(1,2,3))
    >>> print(a)
             C       1.00000       2.00000       3.00000
    >>> a.y = 'param1'
    >>> print(a)
             C       1.00000        param1       3.00000
    
[/code]

However, non-numerical coordinates cannot be used together with some methods (for example `distance_to()` or `translate()`). An attempt to do this raises an exception.

Internally, atomic coordinates are always expressed in angstroms. Most of methods that read or modify atomic coordinates accept a keyword argument `unit` allowing to choose unit in which results and/or arguments are expressed (see [`Units`](utils.html#scm.plams.tools.units.Units "scm.plams.tools.units.Units") for details). Throughout the entire code angstrom is the default length unit. If you don’t specify `unit` parameter in any place of your script, all the automatic unit handling described above boils down to occasional multiplication/division by 1.0.

`__init__`(_atnum =0_, _symbol =None_, _coords =None_, _unit ='angstrom'_, _bonds =None_, _mol =None_, _** other_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`str`(_symbol =True_, _suffix =''_, _suffix_dict ={}_, _unit ='angstrom'_, _space =14_, _decimal =6_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.str)¶
    
Return a string representation of this atom.

Returned string is a single line (no newline characters) that always contains atomic coordinates (and maybe more). Each atomic coordinate is printed using _space_ characters, with _decimal_ characters reserved for decimal digits. Coordinates values are expressed in _unit_.

If _symbol_ is `True`, atomic symbol is added at the beginning of the line. If _symbol_ is a string, this exact string is printed there.

_suffix_ is an arbitrary string that is appended at the end of returned line. It can contain identifiers in curly brackets (like for example `f={fragment}`) that will be replaced by values of corresponding keys from _suffix_dict_ dictionary. See [Format String Syntax](https://docs.python.org/3.8/library/string.html#formatstrings "\(in Python v3.8\)") for details.

Example:
[code] 
    >>> a = Atom(atnum=6, coords=(1,1.5,2))
    >>> print(a.str())
             C      1.000000      1.500000      2.000000
    >>> print(a.str(unit='bohr'))
             C      1.889726      2.834589      3.779452
    >>> print(a.str(symbol=False))
          1.000000      1.500000      2.000000
    >>> print(a.str(symbol='C2.13'))
         C2.13      1.000000      1.500000      2.000000
    >>> print(a.str(suffix='protein1'))
             C      1.000000      1.500000      2.000000 protein1
    >>> a.properties.info = 'membrane'
    >>> print(a.str(suffix='subsystem={info}', suffix_dict=a.properties))
             C      1.000000      1.500000      2.000000 subsystem=membrane
    
[/code]

`__str__`()[[source]](../_modules/scm/plams/mol/atom.html#Atom.__str__)¶
    
Return a string representation of this atom. Simplified version of `str()` to work as a magic method.

`__iter__`()[[source]](../_modules/scm/plams/mol/atom.html#Atom.__iter__)¶
    
Iteration through atom yields coordinates. Thanks to that instances of `Atom` can be passed to any method requiring as an argument a point or a vector in 3D space.

`translate`(_vector_ , _unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.translate)¶
    
Move this atom in space by _vector_ , expressed in _unit_.

_vector_ should be an iterable container of length 3 (usually tuple, list or numpy array). _unit_ describes unit of values stored in _vector_.

This method requires all atomic coordinates to be numerical values, `TypeError` is raised otherwise.

`move_to`(_point_ , _unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.move_to)¶
    
Move this atom to a given _point_ in space, expressed in _unit_.

_point_ should be an iterable container of length 3 (for example: tuple, `Atom`, list, numpy array). _unit_ describes unit of values stored in _point_.

This method requires all atomic coordinates to be numerical values, `TypeError` is raised otherwise.

`distance_to`(_point_ , _unit ='angstrom'_, _result_unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.distance_to)¶
    
Measure the distance between this atom and _point_.

_point_ should be an iterable container of length 3 (for example: tuple, `Atom`, list, numpy array). _unit_ describes unit of values stored in _point_. Returned value is expressed in _result_unit_.

This method requires all atomic coordinates to be numerical values, `TypeError` is raised otherwise.

`vector_to`(_point_ , _unit ='angstrom'_, _result_unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.vector_to)¶
    
Calculate a vector from this atom to _point_.

_point_ should be an iterable container of length 3 (for example: tuple, `Atom`, list, numpy array). _unit_ describes unit of values stored in _point_. Returned value is expressed in _result_unit_.

This method requires all atomic coordinates to be numerical values, `TypeError` is raised otherwise.

`angle`(_point1_ , _point2_ , _point1unit ='angstrom'_, _point2unit ='angstrom'_, _result_unit ='radian'_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.angle)¶
    
Calculate an angle between vectors pointing from this atom to _point1_ and _point2_.

_point1_ and _point2_ should be iterable containers of length 3 (for example: tuple, `Atom`, list, numpy array). Values stored in them are expressed in, respectively, _point1unit_ and _point2unit_. Returned value is expressed in _result_unit_.

This method requires all atomic coordinates to be numerical values, `TypeError` is raised otherwise.

`rotate`(_matrix_)[[source]](../_modules/scm/plams/mol/atom.html#Atom.rotate)¶
    
Rotate this atom according to a rotation _matrix_.

_matrix_ should be a container with 9 numerical values. It can be a list (tuple, numpy array etc.) listing matrix elements row-wise, either flat (`[1,2,3,4,5,6,7,8,9]`) or in two-level fashion (`[[1,2,3],[4,5,6],[7,8,9]]`).

Note

This method does not check if _matrix_ is a proper rotation matrix.

`neighbors`()[[source]](../_modules/scm/plams/mol/atom.html#Atom.neighbors)¶
    
Return a list of neighbors of this atom within the molecule. The list follows the same order as the `bonds` attribute.

# Bond¶

_class _`Bond`(_atom1 =None_, _atom2 =None_, _order =1_, _mol =None_, _** other_)[[source]](../_modules/scm/plams/mol/bond.html#Bond)¶
    
A class representing a bond between two atoms.

An instance of this class has the following attributes:

  * `atom1` and `atom2` – two instances of `Atom` that form this bond

  * `order` – order of the bond. It is either an integer number or the floating point value stored in `Bond.AR`, indicating an aromatic bond

  * `mol` – [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") this bond belongs to

  * `properties` – [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance storing all other information about this bond (initially it is populated with _**other_)

Note

Newly created bond is **not** added to `atom1.bonds` or `atom2.bonds`. Storing information about `Bond` in `Atom` is relevant only in the context of the whole [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"), so this information is updated by `add_bond()`.

`__init__`(_atom1 =None_, _atom2 =None_, _order =1_, _mol =None_, _** other_)[[source]](../_modules/scm/plams/mol/bond.html#Bond.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`__str__`()[[source]](../_modules/scm/plams/mol/bond.html#Bond.__str__)¶
    
Return a string representation of this bond.

`__iter__`()[[source]](../_modules/scm/plams/mol/bond.html#Bond.__iter__)¶
    
Iterate over bonded atoms (`atom1` first, then `atom2`).

`is_aromatic`()[[source]](../_modules/scm/plams/mol/bond.html#Bond.is_aromatic)¶
    
Check if this bond is aromatic.

`length`(_unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/bond.html#Bond.length)¶
    
Return bond length, expressed in _unit_.

`as_vector`(_start =None_, _unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/bond.html#Bond.as_vector)¶
    
Return a vector between two atoms that form this bond. _start_ can be used to indicate which atom should be the beginning of that vector. If not specified, `self.atom1` is used. Returned value if a tuple of length 3, expressed in _unit_.

`other_end`(_atom_)[[source]](../_modules/scm/plams/mol/bond.html#Bond.other_end)¶
    
Return the atom on the other end of this bond with respect to _atom_. _atom_ has to be one of the atoms forming this bond, otherwise an exception is raised.

`resize`(_moving_atom_ , _length_ , _unit ='angstrom'_)[[source]](../_modules/scm/plams/mol/bond.html#Bond.resize)¶
    
Change the length of this bond to _length_ expressed in _unit_ by moving _moving_atom_.

_moving_atom_ should be one of the atoms that form this bond. This atom is moved along the bond axis in such a way that new bond length equals _length_. If this bond is a part of a [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") the whole part connected to _moving_atom_ is moved.

Note

Calling this method on a bond that forms a ring within a molecule raises a `MoleculeError`.

`rotate`(_moving_atom_ , _angle_ , _unit ='radian'_)[[source]](../_modules/scm/plams/mol/bond.html#Bond.rotate)¶
    
Rotate part of the molecule containing _moving_atom_ along axis defined by this bond by an _angle_ expressed in _unit_.

Calling this method makes sense only if this bond is a part of a [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"). _moving_atom_ should be one of the atoms that form this bond and it indicates which part of the molecule is rotated. A positive value of _angle_ denotes counterclockwise rotation (when looking along the bond, from the stationary part of the molecule).

Note

Calling this method on a bond that forms a ring raises a `MoleculeError`.

[Next ](mol_rdkit.html "RDKit interface") [ Previous](mol_api.html "Molecule")

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
