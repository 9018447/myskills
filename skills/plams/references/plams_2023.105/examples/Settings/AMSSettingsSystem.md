[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../../_static/plams_logo.png) ](../../index.html)

  * 

Table of contents

  * [General](../../general.html)
  * [Introduction](../../intro.html)
  * [Getting started](../../started.html)
  * [Components overview](../../components/components.html)
  * [Interfaces](../../interfaces/interfaces.html)
  * [Examples](../examples.html)
    * [Getting Started](../examples.html#getting-started)
      * [Geometry optimization of water](../WaterOptimization.html)
      * AMS Settings: Chemical System (Molecule)
        * Initial imports
        * Elements, coordinates, lattice vectors, and charge
        * Atomic properties: masses, regions, force field types …
        * Bonds
        * Multiple systems
        * Complete Python code
      * [Helium dimer dissociation curve](../He2DissociationCurve.html)
      * [Many jobs in parallel](../ManyJobsInParallel.html)
    * [Molecule analysis](../examples.html#molecule-analysis)
    * [Benchmarks](../examples.html#benchmarks)
    * [Workflows](../examples.html#workflows)
    * [COSMO-RS and property prediction](../examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](../examples.html#packmol-and-ams-ase-interfaces)
    * [ParAMS and pyZacros](../examples.html#params-and-pyzacros)
    * [Other AMS calculations](../examples.html#other-ams-calculations)
    * [Pymatgen](../examples.html#pymatgen)
    * [Pre-made recipes](../examples.html#pre-made-recipes)
  * [Cookbook](../../cookbook/cookbook.html)
  * [Citations](../../citations.html)

  * [FAQ](../../FAQ.html)

__[PLAMS](../../index.html)

  * [Documentation](../../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../../index.html)/
  * [Examples](../examples.html)/
  * AMS Settings: Chemical System (Molecule)

# AMS Settings: Chemical System (Molecule)¶

This example shows how to convert between a PLAMS `Molecule` object and the text input in the AMS `System` block.

See also

PLAMS documentation: [Molecule handling](../../interfaces/ams.html#amsmoleculehandling)

To follow along, either

  * Download [`ams_settings_system.py`](../../_downloads/31d8029adbe35411d52bf35cdddae564/ams_settings_system.py) (run as `$AMSBIN/amspython ams_settings_system.py`).

  * Download [`ams_settings_system.ipynb`](../../_downloads/c6125218234ef632759f2bc2a739d5e1/ams_settings_system.ipynb) (see also: how to install [Jupyterlab](../../../Scripting/Python_Stack/Python_Stack.html#install-and-run-jupyter-lab-jupyter-notebooks) in AMS)

## Initial imports¶
[code] 
    from scm.plams import *
    
[/code]

## Elements, coordinates, lattice vectors, and charge¶

### Manual molecule definition¶
[code] 
    molecule = Molecule()
    molecule.add_atom(Atom(symbol='O', coords=(0,0,0)))
    molecule.add_atom(Atom(symbol='H', coords=(1,0,0)))
    molecule.add_atom(Atom(symbol='H', coords=(0,1,0)))
    
[/code]

To see the input that will be passed to AMS, create an AMSJob and print the input:
[code] 
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
    End
    
[/code]

### Lattice vectors: 1D-periodic¶

For periodic systems in 1 dimension, the lattice vector must be along the x direction (with 0 components along y and z)
[code] 
    molecule.lattice = [
        [10, 0, 0]
    ]
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
      Lattice
            10.0000000000     0.0000000000     0.0000000000
      End
    End
    
[/code]

### Lattice vectors: 2D-periodic¶

For 2 dimensions, the two lattice vectors must lie in the xy plane (with 0 component along z).
[code] 
    molecule.lattice = [
        [10, 0, 0],
        [0, 11, 0],
    ]
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
      Lattice
            10.0000000000     0.0000000000     0.0000000000
             0.0000000000    11.0000000000     0.0000000000
      End
    End
    
[/code]

### Lattice vectors: 3D-periodic¶
[code] 
    molecule.lattice = [
        [10, 0, 0],
        [0, 11, 0],
        [-1, 0, 12]
    ]
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
      Lattice
            10.0000000000     0.0000000000     0.0000000000
             0.0000000000    11.0000000000     0.0000000000
            -1.0000000000     0.0000000000    12.0000000000
      End
    End
    
[/code]

### Delete lattice vectors¶
[code] 
    molecule.lattice = []
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
    End
    
[/code]

### Charge¶
[code] 
    molecule.properties.charge = -1
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
      Charge -1
    End
    
[/code]

To get the charge of a molecule, use `molecule.properties.get("charge", 0)`. If the charge is not defined you will then get 0 as the charge.
[code] 
    my_charge = molecule.properties.get("charge", 0)
    print(f"The charge is {my_charge}")
    
[/code]
[code] 
    The charge is -1
    
[/code]

Unset the charge:
[code] 
    if 'charge' in molecule.properties:
        del molecule.properties.charge
    
    my_charge = molecule.properties.get("charge", 0)
    print(f"The charge is {my_charge}")
    
[/code]
[code] 
    The charge is 0
    
[/code]

## Atomic properties: masses, regions, force field types …¶

In the AMS system block most atomic properties are given as a suffix at the end of the line.

To access an individual atom, use for example `molecule[1]`, which corresponds to the first atom. **Note that the indexing starts with 1** , unlike normal Python lists that start with 0!

### Isotopes (atomic masses)¶
[code] 
    molecule[2].properties.mass = 2.014
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000 mass=2.014
                  H       0.0000000000       1.0000000000       0.0000000000
      End
    End
    
[/code]

### Regions¶

Regions are used for example to

  * set special basis sets on a subset of atoms, or

  * apply a thermostat in molecular dynamics to only a subset of atoms,

  * visualize atoms easily in the AMS GUI,

  * and much more!

Use Python sets to specify regions. In this way, one atom can belong to multiple regions.
[code] 
    molecule[1].properties.region = {"region1"}
    molecule[2].properties.region = {"region1"}
    molecule[3].properties.region = {"region1", "region2"}
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000 region=region1
                  H       1.0000000000       0.0000000000       0.0000000000 mass=2.014 region=region1
                  H       0.0000000000       1.0000000000       0.0000000000 region=region1,region2
      End
    End
    
[/code]

### Force field types¶

Some force fields need to know the specific atom type and not just the chemical element. Use `ForceField.Type` for this when you use the ForceField engine:
[code] 
    molecule[1].properties.ForceField.Type = "OW" # these types would depend on what type of force field you use!
    molecule[2].properties.ForceField.Type = "HW"
    molecule[3].properties.ForceField.Type = "HW"
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000 ForceField.Type=OW region=region1
                  H       1.0000000000       0.0000000000       0.0000000000 ForceField.Type=HW mass=2.014 region=region1
                  H       0.0000000000       1.0000000000       0.0000000000 ForceField.Type=HW region=region1,region2
      End
    End
    
[/code]

### Delete all atom-specific options¶

Loop over the atoms and set `atom.properties` to an empty `Settings()`:
[code] 
    for at in molecule:
        at.properties = Settings()
    
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
    End
    
[/code]

## Bonds¶

Most methods (DFT, DFTB, ML Potential, ReaxFF) ignore any specified bonds.

When using force fields, you sometimes need to specify the bonds that connect atoms. Some force fields (UFF, GAFF) can automatically guess the correct types of bonds.

So **most of the time you do not manually need to specify bonds**.

If you **need** to specify bonds, it is easiest

  * to handle in the AMS GUI: use File -> Export Coordinates -> .in, and then load the file with `molecule = Molecule("my_file.in")`

  * to use the `from_smiles` function to generate a molecule from SMILES code, for example `molecule = from_smiles("O")` for water.

If you need to add bonds manually in PLAMS you can do it as follows:
[code] 
    molecule.add_bond(molecule[1], molecule[2], order=1.0)
    molecule.add_bond(molecule[1], molecule[3], order=1.0)
    print(AMSJob(molecule=molecule).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
      BondOrders
         1 2 1.0
         1 2 1.0
         1 3 1.0
      End
    End
    
[/code]

## Multiple systems¶

Some tasks like NEB (nudged elastic band) require more than 1 system in the input file. This can be accomplished by using a Python dictionary.

In AMS,

  * the “main system” has no name. It should have the key `""` (empty string) in the dictionary.

  * every additional system needs to have a name, that is used as the key in the dictionary.

Let’s first define two `Molecule` in the normal way:
[code] 
    molecule1 = Molecule()
    molecule1.add_atom(Atom(symbol='O', coords=(0,0,0)))
    molecule1.add_atom(Atom(symbol='H', coords=(1,0,0)))
    molecule1.add_atom(Atom(symbol='H', coords=(0,1,0)))
    
    molecule2 = Molecule()
    molecule2.add_atom(Atom(symbol='O', coords=(0,0,0)))
    molecule2.add_atom(Atom(symbol='H', coords=(3.33333,0,0)))
    molecule2.add_atom(Atom(symbol='H', coords=(0,5.555555,0)))
    
[/code]

Then create the `mol_dict` dictionary:
[code] 
    mol_dict = {
        "": molecule1,     # main system, empty key (no name)
        "final": molecule2 # for NEB, use "final" as the name for the other endpoint
    }
    
[/code]

Pass the `mol_dict` as the `molecule` argument to `AMSJob`:
[code] 
    print(AMSJob(molecule=mol_dict).get_input())
    
[/code]
[code] 
    system
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       1.0000000000       0.0000000000       0.0000000000
                  H       0.0000000000       1.0000000000       0.0000000000
      End
    End
    system final
      Atoms
                  O       0.0000000000       0.0000000000       0.0000000000
                  H       3.3333300000       0.0000000000       0.0000000000
                  H       0.0000000000       5.5555550000       0.0000000000
      End
    End
    
[/code]

Above we see that the main system is printed just as before. A second system block “system final” is also added with `molecule2`.

## Complete Python code¶
[code] 
    #!/usr/bin/env amspython
    # coding: utf-8
    
    # ## Initial imports
    
    from scm.plams import *
    
    # ## Elements, coordinates, lattice vectors, and charge
    
    # ### Manual molecule definition
    
    molecule = Molecule()
    molecule.add_atom(Atom(symbol='O', coords=(0,0,0)))
    molecule.add_atom(Atom(symbol='H', coords=(1,0,0)))
    molecule.add_atom(Atom(symbol='H', coords=(0,1,0)))
    
    # To see the input that will be passed to AMS, create an AMSJob and print the input:
    
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Lattice vectors: 1D-periodic
    # 
    # For periodic systems in 1 dimension, the lattice vector must be along the x direction (with 0 components along y and z)
    
    molecule.lattice = [
        [10, 0, 0]
    ]
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Lattice vectors: 2D-periodic
    # 
    # For 2 dimensions, the two lattice vectors must lie in the xy plane (with 0 component along z).
    
    molecule.lattice = [
        [10, 0, 0],
        [0, 11, 0],
    ]
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Lattice vectors: 3D-periodic
    
    molecule.lattice = [
        [10, 0, 0],
        [0, 11, 0],
        [-1, 0, 12]
    ]
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Delete lattice vectors
    
    molecule.lattice = []
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Charge
    
    molecule.properties.charge = -1
    print(AMSJob(molecule=molecule).get_input())
    
    # To get the charge of a molecule, use ``molecule.properties.get("charge", 0)``. If the charge is not defined you will then get 0 as the charge.
    
    my_charge = molecule.properties.get("charge", 0)
    print(f"The charge is {my_charge}")
    
    # Unset the charge:
    
    if 'charge' in molecule.properties:
        del molecule.properties.charge
        
    my_charge = molecule.properties.get("charge", 0)
    print(f"The charge is {my_charge}")
    
    # ## Atomic properties: masses, regions, force field types ...
    # 
    # In the AMS system block most atomic properties are given as a suffix at the end of the line.
    # 
    # To access an individual atom, use for example ``molecule[1]``, which corresponds to the first atom. **Note that the indexing starts with 1**, unlike normal Python lists that start with 0!
    
    # ### Isotopes (atomic masses)
    
    molecule[2].properties.mass = 2.014
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Regions
    # 
    # Regions are used for example to  
    # 
    # * set special basis sets on a subset of atoms, or 
    # * apply a thermostat in molecular dynamics to only a subset of atoms, 
    # * visualize atoms easily in the AMS GUI,
    # * and much more!
    # 
    # Use Python sets to specify regions. In this way, one atom can belong to multiple regions.
    
    molecule[1].properties.region = {"region1"}
    molecule[2].properties.region = {"region1"}
    molecule[3].properties.region = {"region1", "region2"}
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Force field types
    # 
    # Some force fields need to know the specific atom type and not just the chemical element. Use ``ForceField.Type`` for this when you use the ForceField engine:
    
    molecule[1].properties.ForceField.Type = "OW" # these types would depend on what type of force field you use!
    molecule[2].properties.ForceField.Type = "HW"
    molecule[3].properties.ForceField.Type = "HW"
    print(AMSJob(molecule=molecule).get_input())
    
    # ### Delete all atom-specific options
    # Loop over the atoms and set ``atom.properties`` to an empty ``Settings()``:
    
    for at in molecule:
        at.properties = Settings()
        
    print(AMSJob(molecule=molecule).get_input())
    
    # ## Bonds
    # 
    # Most methods (DFT, DFTB, ML Potential, ReaxFF) ignore any specified bonds. 
    # 
    # When using force fields, you sometimes need to specify the bonds that connect atoms. Some force fields (UFF, GAFF) can automatically guess the correct types of bonds. 
    # 
    # So **most of the time you do not manually need to specify bonds**.
    # 
    # If you **need** to specify bonds, it is easiest 
    # 
    # * to handle in the AMS GUI: use File -> Export Coordinates -> .in, and then load the file with ``molecule = Molecule("my_file.in")``
    # * to use the ``from_smiles`` function to generate a molecule from SMILES code, for example ``molecule = from_smiles("O")`` for water.
    # 
    # If you need to add bonds manually in PLAMS you can do it as follows:
    
    molecule.add_bond(molecule[1], molecule[2], order=1.0)
    molecule.add_bond(molecule[1], molecule[3], order=1.0)
    print(AMSJob(molecule=molecule).get_input())
    
    # ## Multiple systems
    # 
    # Some tasks like NEB (nudged elastic band) require more than 1 system in the input file. This can be accomplished by using a Python dictionary.
    # 
    # In AMS, 
    # 
    # * the "main system" has no name. It should have the key ``""`` (empty string) in the dictionary.
    # 
    # * every additional system needs to have a name, that is used as the key in the dictionary.
    # 
    # Let's first define two ``Molecule`` in the normal way:
    
    molecule1 = Molecule()
    molecule1.add_atom(Atom(symbol='O', coords=(0,0,0)))
    molecule1.add_atom(Atom(symbol='H', coords=(1,0,0)))
    molecule1.add_atom(Atom(symbol='H', coords=(0,1,0)))
    
    molecule2 = Molecule()
    molecule2.add_atom(Atom(symbol='O', coords=(0,0,0)))
    molecule2.add_atom(Atom(symbol='H', coords=(3.33333,0,0)))
    molecule2.add_atom(Atom(symbol='H', coords=(0,5.555555,0)))
    
    # Then create the ``mol_dict`` dictionary:
    
    mol_dict = {
        "": molecule1,     # main system, empty key (no name)
        "final": molecule2 # for NEB, use "final" as the name for the other endpoint
    }
    
    # Pass the ``mol_dict`` as the ``molecule`` argument to ``AMSJob``:
    
    print(AMSJob(molecule=mol_dict).get_input())
    
    # Above we see that the main system is printed just as before. A second system block "system final" is also added with ``molecule2``.
    
[/code]

[Next ](../He2DissociationCurve.html "Helium dimer dissociation curve") [ Previous](../WaterOptimization.html "Geometry optimization of water")

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
