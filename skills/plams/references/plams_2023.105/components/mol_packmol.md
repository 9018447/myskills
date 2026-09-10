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
      * [Atom](atombond.html)
      * [Bond](atombond.html#bond)
      * [RDKit interface](mol_rdkit.html)
      * [ASE interface](mol_ase.html)
      * Packmol interface
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
  * Packmol interface

# Packmol interface¶

Packmol ([Packmol website](https://m3g.github.io/packmol/download.shtml)) is a program for creating liquid or gas mixtures. The PLAMS interface only supports

  * uniform mixtures

  * solid/liquid interfaces

  * microsolvation

There are three main functions:

  * `packmol` (for fluids with 1 or more components)

  * `packmol_on_slab` (for solid/liquid or solid/gas interfaces with 1 or more components in the fluid)

  * `packmol_microsolvation` (for microsolvation of a solute with a solvent)

See the [Packmol example](../examples/PackMolExample/PackMolExample.html#packmolexample) for all the ways these functions can be used.

The above functions accept an `executable` argument, which should contain the path to the packmol program. If it is not specified, the path to the packmol program included with the Amsterdam Modeling Suite will be used.

`packmol`(_molecules_ , _mole_fractions =None_, _density =None_, _n_atoms =None_, _box_bounds =None_, _n_molecules =None_, _sphere =False_, _keep_bonds =True_, _keep_atom_properties =True_, _region_names =None_, _return_details =False_, _executable =None_)[[source]](../_modules/scm/plams/interfaces/molecule/packmol.html#packmol)¶
    
Create a fluid of the given `molecules`. The function will use the given input parameters and try to obtain good values for the others. You _must_ specify `density` and/or `box_bounds`.

molecules[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or list of Molecule
    
The molecules to pack

mole_fractionslist of float
    
The mole fractions (in the same order as `molecules`). Cannot be combined with `n_molecules`. If not given, an equal (molar) mixture of all components will be created.

density: float
    
The total density (in g/cm^3) of the fluid

n_atoms: int
    
The (approximate) number of atoms in the final mixture

box_bounds: list of float (length 6)
    
The box in which to pack the molecules. The box is orthorhombic and should be specified as [xmin, ymin, zmin, xmax, ymax, zmax]. The minimum values should all be set to 0, i.e. set box_bounds=[0., 0., 0., xmax, ymax, zmax]. If not specified, a cubic box of appropriate dimensions will be used.

n_moleculesint or list of int
    
The (exact) number of molecules for each component (in the same order as `molecules`). Cannot be combined with `mole_fractions`.

sphere: bool
    
Whether the molecules should be packed in a sphere. The radius is determined by getting the volume from the box bounds!

keep_bondsbool
    
If True, the bonds from the constituent molecules will be kept in the returned Molecule

keep_atom_propertiesbool
    
If True, the atom.properties (e.g. force-field atom types) of the constituent molecules will be kept in the returned Molecule

region_namesstr or list of str
    
Populate the region information for each atom. Should have the same length and order as `molecules`. By default the regions are named `mol0`, `mol1`, etc.

return_detailsbool
    
Return a 2-tuple (Molecule, dict) where the dict has keys like ‘n_molecules’, ‘mole_fractions’, ‘density’, etc. They contain the actual details of the returned molecule, which may differ slightly from the requested quantities.

Returned keys:

  * ‘n_molecules’: list of integer with actually added number of molecules

  * ‘mole_fractions’: list of float with actually added mole fractions

  * ‘density’: float, gives the density in g/cm^3

  * ‘n_atoms’: int, the number of atoms in the returned molecule

  * ‘molecule_type_indices’: list of int of length n_atoms. For each atom, give an integer index for which TYPE of molecule it belongs to.

  * ‘molecule_indices’: list of int of length n_atoms. For each atom, give an integer index for which molecule it belongs to

  * ‘atom_indices_in_molecule’: list of int of length n_atoms. For each atom, give an integer index for which position in the molecule it is.

executablestr
    
The path to the packmol executable. If not specified, `$AMSBIN/packmol.exe` will be used (which is the correct path for the Amsterdam Modeling Suite).

Useful combinations:

  * `mole_fractions`, `density`, `n_atoms`: Create a mixture with a given density and approximate number of atoms (a cubic box will be created)

  * `mole_fractions`, `density`, `box_bounds`: Create a mixture with a given density inside a given box (the number of molecules will approximately match the density and mole fractions)

  * `n_molecules`, `density`: Create a mixture with the given number of molecules and density (a cubic box will be created)

  * `n_molecules`, `box_bounds`: Create a mixture with the given number of molecules inside the given box

Example:
[code] 
    packmol(molecules=[from_smiles('O'), from_smiles('C')],
            mole_fractions=[0.8, 0.2],
            density=0.8,
            n_atoms=100)
    
[/code]

Returns: a [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or tuple (Molecule, dict)
    
If return_details=False, return a Molecule. If return_details=True, return a tuple.

`packmol_on_slab`(_slab_ , _molecules_ , _mole_fractions =None_, _density =1.0_, _keep_bonds =True_, _keep_atom_properties =True_, _region_names =None_, _executable =None_)[[source]](../_modules/scm/plams/interfaces/molecule/packmol.html#packmol_on_slab)¶
    
Creates a solid/liquid interface with an approximately correct density. The density is calculated for the volume not occupied by the slab (+ 1.5 angstrom buffer at each side of the slab).

Returns: a [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")

slab[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")
    
The system must have a 3D lattice (including a vacuum gap along z) and be orthorhombic. The vacuum gap will be filled with the liquid.

For the other arguments, see `packmol`.

Example:
[code] 
    packmol_on_slab(slab=slab_3d_with_vacuum_gap,
                    molecules=[from_smiles('O'), from_smiles('C')],
                    mole_fractions=[0.8, 0.2],
                    density=0.8)
    
[/code]

`packmol_microsolvation`(_solute_ , _solvent_ , _density =1.0_, _threshold =3.0_, _keep_bonds =True_, _keep_atom_properties =True_, _region_names =['solute', 'solvent']_, _executable =None_)[[source]](../_modules/scm/plams/interfaces/molecule/packmol.html#packmol_microsolvation)¶
    
Microsolvation of a `solute` with a `solvent` with an approximate `density`.

solute: [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")
    
The solute to be surrounded by solvent molecules

solvent: [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")
    
The solvent molecule

density: float
    
Approximate density in g/cm^3

threshold: float
    
Distance in angstrom. Any solvent molecule for which at least 1 atom is within this threshold to the solute molecule will be kept

For the other arguments, see `packmol`.

[Next ](utils.html "Utilities") [ Previous](mol_ase.html "ASE interface")

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
