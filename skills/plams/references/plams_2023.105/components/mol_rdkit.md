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
      * RDKit interface
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
  * RDKit interface

# RDKit interface¶

[RDKit](https://www.rdkit.org) is a collection of cheminformatics and machine-learning software written in C++ and Python. PLAMS interface to RDKit originates from [QMFlows](https://github.com/SCM-NV/qmflows) project and features functions for generating PLAMS molecules from string representations (SMARTS, SMILES) as well as a handful of tools for dealing with proteins and PDB files.

`add_Hs`(_mol_ , _forcefield =None_, _return_rdmol =False_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#add_Hs)¶
    
Add hydrogens to protein molecules read from PDB. Makes sure that the hydrogens get the correct PDBResidue info.

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – Molecule to be protonated

  * **forcefield** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Specify ‘uff’ or ‘mmff’ to apply forcefield based geometry optimization on new atoms.

  * **return_rdmol** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – return a RDKit molecule if true, otherwise a PLAMS molecule

Returns
    
A molecule with explicit hydrogens added

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol

`apply_reaction_smarts`(_mol_ , _reaction_smarts_ , _complete =False_, _forcefield =None_, _return_rdmol =False_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#apply_reaction_smarts)¶
    
Applies reaction smirks and returns product. If returned as a PLAMS molecule, thismolecule.properties.orig_atoms is a list of indices of atoms that have not been changed (which can for example be used partially optimize new atoms only with the freeze keyword)

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – molecule to be modified

  * **reactions_smarts** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Reactions smarts to be applied to molecule

  * **complete** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)") _or_[ _float_](https://docs.python.org/3.8/library/functions.html#float "\(in Python v3.8\)") _(__value between 0 and 1_ _)_) – Apply reaction until no further changes occur or given fraction of reaction centers have been modified

  * **forcefield** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Specify ‘uff’ or ‘mmff’ to apply forcefield based geometry optimization of product structures.

  * **return_rdmol** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – return a RDKit molecule if true, otherwise a PLAMS molecule

Returns
    
(product molecule, list of unchanged atoms)

Return type
    
([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"), list of int)

`apply_template`(_mol_ , _template_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#apply_template)¶
    
Modifies bond orders in PLAMS molecule according template smiles structure.

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – molecule to be modified

  * **template** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – smiles string defining the correct chemical structure

Returns
    
Molecule with correct chemical structure and provided 3D coordinates

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")

`get_backbone_atoms`(_mol_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#get_backbone_atoms)¶
    
Return a list of atom indices corresponding to the backbone atoms in a peptide molecule. This function assumes PDB information in properties.pdb_info of each atom, which is the case if the molecule is generated with the “readpdb” or “from_sequence” functions.

Parameters
    
**mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – a peptide molecule

Returns
    
a list of atom indices

Return type
    
[list](https://docs.python.org/3.8/library/stdtypes.html#list "\(in Python v3.8\)")

`modify_atom`(_mol_ , _idx_ , _element_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#modify_atom)¶
    
Change atom “idx” in molecule “mol” to “element” and add or remove hydrogens accordingly

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – molecule to be modified

  * **idx** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – index of the atom to be modified

  * **element** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – 

Returns
    
Molecule with new element and possibly added or removed hydrogens

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")

`to_rdmol`(_plams_mol_ , _sanitize =True_, _properties =True_, _assignChirality =False_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#to_rdmol)¶
    
Translate a PLAMS molecule into an RDKit molecule type. PLAMS [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"), [`Atom`](atombond.html#scm.plams.mol.atom.Atom "scm.plams.mol.atom.Atom") or [`Bond`](atombond.html#scm.plams.mol.bond.Bond "scm.plams.mol.bond.Bond") properties are pickled if they are neither booleans, floats, integers, floats nor strings, the resulting property names are appended with ‘_pickled’.

Parameters
    
  * **plams_mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")) – A PLAMS molecule

  * **sanitize** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – Kekulize, check valencies, set aromaticity, conjugation and hybridization

  * **properties** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – If all [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"), [`Atom`](atombond.html#scm.plams.mol.atom.Atom "scm.plams.mol.atom.Atom") and [`Bond`](atombond.html#scm.plams.mol.bond.Bond "scm.plams.mol.bond.Bond") properties should be converted from PLAMS to RDKit format.

  * **assignChirality** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – Assign R/S and cis/trans information, insofar as this was not yet present in the PLAMS molecule.

Returns
    
an RDKit molecule

Return type
    
rdkit.Chem.Mol

`from_rdmol`(_rdkit_mol_ , _confid =- 1_, _properties =True_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#from_rdmol)¶
    
Translate an RDKit molecule into a PLAMS molecule type. RDKit properties will be unpickled if their name ends with ‘_pickled’.

Parameters
    
  * **rdkit_mol** (_rdkit.Chem.Mol_) – RDKit molecule

  * **confid** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – conformer identifier from which to take coordinates

  * **properties** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – If all Chem.Mol, Chem.Atom and Chem.Bond properties should be converted from RDKit to PLAMS format.

Returns
    
a PLAMS molecule

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")

`from_sequence`(_sequence_ , _nconfs =1_, _name =None_, _forcefield =None_, _rms =0.1_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#from_sequence)¶
    
Generates PLAMS molecule from a peptide sequence. Includes explicit hydrogens and 3D coordinates.

Parameters
    
  * **sequence** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A peptide sequence, e.g. ‘HAG’

  * **nconfs** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – Number of conformers to be generated

  * **name** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A name for the molecule

  * **forcefield** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Choose ‘uff’ or ‘mmff’ forcefield for geometry optimization and ranking of comformations. The default value None results in skipping of the geometry optimization step.

  * **rms** ([_float_](https://docs.python.org/3.8/library/functions.html#float "\(in Python v3.8\)")) – Root Mean Square deviation threshold for removing similar/equivalent conformations.

Returns
    
A peptide molecule with hydrogens and 3D coordinates or a list of molecules if nconfs > 1

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or list of PLAMS Molecules

`from_smiles`(_smiles_ , _nconfs =1_, _name =None_, _forcefield =None_, _rms =0.1_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#from_smiles)¶
    
Generates PLAMS molecule(s) from a smiles strings.

Parameters
    
  * **smiles** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A smiles string

  * **nconfs** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – Number of conformers to be generated

  * **name** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A name for the molecule

  * **forcefield** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Choose ‘uff’ or ‘mmff’ forcefield for geometry optimization and ranking of comformations. The default value None results in skipping of the geometry optimization step.

  * **rms** ([_float_](https://docs.python.org/3.8/library/functions.html#float "\(in Python v3.8\)")) – Root Mean Square deviation threshold for removing similar/equivalent conformations

Returns
    
A molecule with hydrogens and 3D coordinates or a list of molecules if nconfs > 1

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or list of PLAMS Molecules

`from_smarts`(_smarts_ , _nconfs =1_, _name =None_, _forcefield =None_, _rms =0.1_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#from_smarts)¶
    
Generates PLAMS molecule(s) from a smarts strings. This allows for example to define hydrogens explicitly. However it is less suitable for aromatic molecules (use from_smiles in that case).

Parameters
    
  * **smarts** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A smarts string

  * **nconfs** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – Number of conformers to be generated

  * **name** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A name for the molecule

  * **forcefield** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Choose ‘uff’ or ‘mmff’ forcefield for geometry optimization and ranking of comformations. The default value None results in skipping of the geometry optimization step.

  * **rms** ([_float_](https://docs.python.org/3.8/library/functions.html#float "\(in Python v3.8\)")) – Root Mean Square deviation threshold for removing similar/equivalent conformations.

Returns
    
A molecule with hydrogens and 3D coordinates or a list of molecules if nconfs > 1

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or list of PLAMS Molecules

`to_smiles`(_plams_mol_ , _short_smiles =True_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#to_smiles)¶
    
Returns the RDKit-generated SMILES string of a PLAMS molecule.

Note: SMILES strings are generated based on the molecule’s connectivity. If the input PLAMS molecule does not contain any bonds, “guessed bonds” will be used.

Parameters
    
  * **plams_mol** – A PLAMS [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")

  * **short_smiles** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – whether or not to use some RDKit sanitization to get shorter smiles (e.g. for a water molecule, short_smiles=True -> “O”, short_smiles=False -> [H]O[H])

  * ****kwargs** – With ‘kwargs’ you can provide extra optional parameters to the rdkit.Chem method ‘MolToSmiles’. See the rdkit documentation for more info.

Returns
    
the SMILES string

`partition_protein`(_mol_ , _residue_bonds =None_, _split_heteroatoms =True_, _return_rdmol =False_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#partition_protein)¶
    
Splits a protein molecule into capped amino acid fragments and caps.

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – A protein molecule

  * **residue_bonds** ([_tuple_](https://docs.python.org/3.8/library/stdtypes.html#tuple "\(in Python v3.8\)")) – a tuple of pairs of residue number indicating which peptide bonds to split. If none, split all peptide bonds.

  * **split_heteroatoms** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – if True, all bonds between a heteroatom and a non-heteroatom across residues are removed

Returns
    
list of fragments, list of caps

`readpdb`(_pdb_file_ , _sanitize =True_, _removeHs =False_, _proximityBonding =False_, _return_rdmol =False_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#readpdb)¶
    
Generate a molecule from a PDB file

Parameters
    
  * **pdb_file** (_path-__or_ _file-like_) – The PDB file to read

  * **sanitize** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – 

  * **removeHs** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – Hydrogens are removed if True

  * **return_rdmol** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – return a RDKit molecule if true, otherwise a PLAMS molecule

Returns
    
The molecule

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol

`writepdb`(_mol_ , _pdb_file= <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#writepdb)¶
    
Write a PDB file from a molecule

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or rdkit.Chem.Mol) – molecule to be exported to PDB

  * **pdb_file** (_path-__or_ _file-like_) – The PDB file to write to, or a filename

`get_substructure`(_mol_ , _func_list_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#get_substructure)¶
    
Search for functional groups within a molecule based on a list of reference functional groups. SMILES strings, PLAMS and/or RDKit molecules can be used interchangeably in “func_list”.

Example:
[code] 
    >>> mol = from_smiles('OCCO')  # Ethylene glycol
    >>> func_list = ['[H]O', 'C[N+]', 'O=PO']
    >>> get_substructure(mol, func_list)
    
    {'[H]O': [(<scm.plams.mol.atom.Atom at 0x125183518>,
               <scm.plams.mol.atom.Atom at 0x1251836a0>),
              (<scm.plams.mol.atom.Atom at 0x125183550>,
               <scm.plams.mol.atom.Atom at 0x125183240>)]}
    
[/code]

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")) – A PLAMS molecule.

  * **func_list** ([_list_](https://docs.python.org/3.8/library/stdtypes.html#list "\(in Python v3.8\)")) – A list of functional groups. Functional groups can be represented by SMILES strings, PLAMS and/or RDKit molecules.

Returns
    
A dictionary with functional groups from “func_list” as keys and a list of n-tuples with matching PLAMS [`Atom`](atombond.html#scm.plams.mol.atom.Atom "scm.plams.mol.atom.Atom") as values.

`get_conformations`(_mol_ , _nconfs =1_, _name =None_, _forcefield =None_, _rms =- 1_, _enforceChirality =False_, _useExpTorsionAnglePrefs ='default'_, _constraint_ats =None_, _EmbedParameters ='EmbedParameters'_, _randomSeed =1_, _best_rms =- 1_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#get_conformations)¶
    
Generates 3D conformation(s) for an rdkit_mol or a PLAMS Molecule

Parameters
    
  * **mol** (rdkit.Chem.Mol or [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")) – RDKit or PLAMS Molecule

  * **nconfs** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – Number of conformers to be generated

  * **name** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – A name for the molecule

  * **forcefield** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Choose ‘uff’ or ‘mmff’ forcefield for geometry optimization and ranking of comformations. The default value None results in skipping of the geometry optimization step

  * **rms** ([_float_](https://docs.python.org/3.8/library/functions.html#float "\(in Python v3.8\)")) – Root Mean Square deviation threshold for removing similar/equivalent conformations.

  * **best_rms** ([_float_](https://docs.python.org/3.8/library/functions.html#float "\(in Python v3.8\)")) – Root Mean Square deviation of best atomic permutation for removing similar/equivalent conformations.

  * **enforceChirality** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – Enforce the correct chirality if chiral centers are present

  * **useExpTorsionAnglePrefs** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Use experimental torsion angles preferences for the conformer generation by rdkit

  * **constraint_ats** ([_list_](https://docs.python.org/3.8/library/stdtypes.html#list "\(in Python v3.8\)")) – List of atom indices to be constrained

  * **EmbedParameters** ([_str_](https://docs.python.org/3.8/library/stdtypes.html#str "\(in Python v3.8\)")) – Name of RDKit EmbedParameters class (‘EmbedParameters’, ‘ETKDG’)

  * **randomSeed** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – The seed for the random number generator. If set to None the generated conformers will be non-deterministic.

Returns
    
A molecule with hydrogens and 3D coordinates or a list of molecules if nconfs > 1

Return type
    
[`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") or list of PLAMS Molecules

`yield_coords`(_rdmol_ , _id =- 1_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#yield_coords)¶
    
Take an rdkit molecule and yield its coordinates as 3-tuples.
[code] 
    >>> from scm.plams import yield_coords
    >>> from rdkit import Chem
    
    >>> rdmol = Chem.Mol(...)  # e.g. Methane
    >>> for xyz in yield_coords(rdmol):
    ...     print(xyz)
    (-0.0, -0.0, -0.0)
    (0.6405, 0.6405, -0.6405)
    (0.6405, -0.6405, 0.6405)
    (-0.6405, 0.6405, 0.6405)
    (-0.6405, -0.6405, -0.6405)
    
[/code]

The iterator produced by this function can, for example, be passed to [`Molecule.from_array()`](mol_api.html#scm.plams.mol.molecule.Molecule.from_array "scm.plams.mol.molecule.Molecule.from_array") the update the coordinates of a PLAMS Molecule in-place.
[code] 
    >>> from scm.plams import Molecule
    
    >>> mol = Molecule(...)
    
    >>> xyz_iterator = yield_coords(rdmol)
    >>> mol.from_array(xyz_iterator)
    
[/code]

Parameters
    
  * **rdmol** (_rdkit.Chem.Mol_) – An RDKit mol.

  * **id** ([_int_](https://docs.python.org/3.8/library/functions.html#int "\(in Python v3.8\)")) – The ID of the desired conformer.

Returns
    
An iterator yielding 3-tuples with _rdmol_ ’s Cartesian coordinates.

Return type
    
iterator

`canonicalize_mol`(_mol_ , _inplace =False_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/molecule/rdkit.html#canonicalize_mol)¶
    
Take a PLAMS molecule and sort its atoms based on their canonical rank.

Example:
[code] 
    >>> from scm.plams import Molecule, canonicalize_mol
    
    # Methane
    >>> mol: Molecule = ...
    >>> print(mol)
    Atoms:
        1         H      0.640510      0.640510     -0.640510
        2         H      0.640510     -0.640510      0.640510
        3         C      0.000000      0.000000      0.000000
        4         H     -0.640510      0.640510      0.640510
        5         H     -0.640510     -0.640510     -0.640510
    
    >>> print(canonicalize_mol(mol))
    Atoms:
        1         C      0.000000      0.000000      0.000000
        2         H     -0.640510     -0.640510     -0.640510
        3         H     -0.640510      0.640510      0.640510
        4         H      0.640510     -0.640510      0.640510
        5         H      0.640510      0.640510     -0.640510
    
[/code]

Parameters
    
  * **mol** ([`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")) – The to-be canonicalized molecule.

  * **inplace** ([_bool_](https://docs.python.org/3.8/library/functions.html#bool "\(in Python v3.8\)")) – Whether to sort the atoms inplace or to return a new molecule.

  * ****kwargs** – Further keyword arguments for [rdkit.Chem.CanonicalRankAtoms](https://www.rdkit.org/docs/source/rdkit.Chem.rdmolfiles.html#rdkit.Chem.rdmolfiles.CanonicalRankAtoms).

Returns
    
Either `None` or a newly sorted molecule, depending on the value of `inplace`.

Return type
    
None or [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule")

[Next ](mol_ase.html "ASE interface") [ Previous](atombond.html "Atom")

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
