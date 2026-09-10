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
  * [Examples](examples.html)
    * [Getting Started](examples.html#getting-started)
    * [Molecule analysis](examples.html#molecule-analysis)
    * [Benchmarks](examples.html#benchmarks)
    * [Workflows](examples.html#workflows)
    * [COSMO-RS and property prediction](examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](examples.html#packmol-and-ams-ase-interfaces)
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
      * [ADF: Task COSMO-RS Compound](ADFCOSMORSCompound.html)
      * [AMS Molecular Dynamics PLAMS jobs](MDJobs.html)
      * [ADF fragment job](adffragment.html)
      * [Reorganization Energy](ReorganizationEnergy.html)
      * [NBO with ADF](adfnbo.html)
      * [Numerical gradients](numgrad.html)
      * [Numerical Hessian](numhess.html)
      * Global Minimum Search
      * [Vibronic Density of States using the AH-FC method](pyAHFCDOS.html)
      * [Vibronic Density of States with ADF](fcf_dos.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Global Minimum Search

# Global Minimum Search¶

(_contributed by_ [Bas van Beek](https://www.researchgate.net/profile/Bas_Beek))

This module implements a scheme for finding/approaching the conformational global minimum of a [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"). The script accomplishes this by systematically varying all dihedral angles, going through the following steps in the process:

  1. A list of bonds is created, filtering out all bonds are either terminal, part of a ring or have a bond order larger than 1.

  2. The geometry of the molecule is optimized with the first dihedral angle set to 120, 0 and -120 degree; the lowest energy conformer is returned.

  3. This process is repeated in an incremental manner for all valid dihedral angles found in step 1., each step starting from the lowest energy conformer of the previous step.

  4. After all dihedral angles have been exhausted, the final geometry is returned.

Optimizations are possible at various levels of theory, RDKit UFF being a cheap default. Alternatively, the geometry can be optimized at an arbitrary level of theory with the help of the PLAMS [`JobRunner`](../components/runners.html#scm.plams.core.jobrunner.JobRunner "scm.plams.core.jobrunner.JobRunner"). Besides the input molecule an additional two arguments, at minimum, are required: A type object of a class derived from [`Job`](../components/jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") and a dictionary of all keyword arguments that should be passed to aforementioned job (e.g. the job [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings")). See below for an exampling using [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") (DFT level):
[code] 
    s = Settings()
    s.input.ams.Task = 'GeometryOptimization'
    s.input.adf.basis.type = 'DZP'
    s.input.adf.XC.GGA = 'PBE'
    s.input.adf.NumericalQuality = 'Good'
    
    mol_in = Molecule('my_mol.xyz')
    job_kwarg = {'settings': s, 'name': 'my_first_DFTJob'}
    mol_out = global_minimum(mol_in, job_type=AMSJob, **job_kwarg)
    
[/code]

Depending on the [`Job`](../components/jobs.html#scm.plams.core.basejob.Job "scm.plams.core.basejob.Job") class, it may be necessary to manually bind the `get_energy()` and `get_main_molecule()` functions to the jobs matching [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") class, these two functions being used for reading energies and geometries, respectively. See below for an exampling using [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") (DFTB level):
[code] 
    s = Settings()
    s.input.ams.Task = 'GeometryOptimization'
    s.input.DFTB.Model = 'DFTB3'
    s.input.DFTB.ResourcesDir = 'DFTB.org/3ob-3-1'
    
    mol_in = Molecule('my_mol.xyz')
    job_kwarg = {'settings': s, 'name': 'my_first_AMSJob'}
    mol_out = global_minimum(mol_in, job_type=AMSJob, **job_kwarg)
    
[/code]

Lastly, by tweaking the job settings including but not excluded to: single points, constrained geometry optimizations, linear transits or a transition state search. The only requirement is that the job yields both an energy and a geometry which can be read with the `get_energy()` and `get_main_molecule()` functions, respectively. See below for an exampling using [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") (PBE level). In this example the optimizer searches for a transition state along a reaction coordinate defined by atoms 1 & 2, using the TSRC method, while simultaneously varying all dihedral angles:
[code] 
    s = Settings()
    s.input.ams.Task = 'TransitionStateSearch'
    s.input.ams.TransitionStateSearch.ReactionCoordinate.Distance = '1 2 1.0'
    s.input.adf.basis.type = 'DZP'
    s.input.adf.XC.GGA = 'PBE'
    s.input.adf.NumericalQuality = 'Good'
    
    mol_in = Molecule('my_mol.xyz')
    job_kwarg = {'settings': s, 'name': 'my_second_ADF_job'}
    mol_out = global_minimum(mol_in, job_type=AMSJob, **job_kwarg)
    
[/code]

The source code:
[code] 
    __all__ = ['global_minimum']
    
    import sys
    
    try:
        from rdkit.Chem import AllChem, rdForceFieldHelpers
        from ..interfaces.molecule.rdkit import to_rdmol, from_rdmol
    except ImportError:
        pass
    
    from ..core.functions import init, finish
    
    def global_minimum(mol, n_scans=1, no_h=True, no_ring=True, bond_orders=[1.0], job_type=False, path='.', **kwarg):
        """
        Find the global minimum of the ligand (RDKit UFF or user-defined PLAMS |Job|) by systematically varying dihedral angles within the molecule.
    
        :param |Molecule| mol: The input molecule
        :param int n_scans:: The number of times the global minimum search should be repeated
        :param bool no_h: If hydrogen-containing bonds should ignored
        :param bool no_ring: If bonds in ring systems should ignored
        :param list bond_orders: A list of accepted bond orders (floats); a bond will be ignored if its bond order is not in *bond_orders*
        :param type or bool job_type: A type object of a class derived from |Job|. Set to ''False'' to use RDKit UFF
        :param str path: The path where the PLAMS working directory will be stored
        :param dict kwarg: Keyword arguments for *job_type*
        :return |Molecule|: A copy of *mol* with a newly optimized geometry
        """
        # Creates guess bonds if no bonds are present
        if len(mol.bonds) == 0:
            mol.guess_bonds()
    
        # Create a list of 2-tuples (i.e. atomic indices) representing (valid) bonds within the molecule
        bond_list = find_bond(mol, no_h=no_h, no_ring=no_ring, bond_orders=bond_orders)
    
        # Search for the global minimum with RDKit UFF or with PLAMS at an user-defined level of theory
        if not job_type:
            if 'rdkit.Chem.AllChem' not in sys.modules or 'rdkit.Chem.rdForceFieldHelpers' not in sys.modules:
                raise ImportError('rdkit.chem module not found, aborting RDKit UFF optimization')
            if not no_ring:
                raise TypeError('no_ring=False is not supported in combination with RDKit UFF')
            if not rdForceFieldHelpers.UFFHasAllMoleculeParams(to_rdmol(mol)):
                raise ValueError('No UFF parameters found for one or more atoms')
    
            for i in range(n_scans):
                for bond in bond_list:
                    mol = global_minimum_scan_rdkit(mol, bond)
    
            # Optimize the molecule even if no valid bonds are found
            if not bond_list:
                rdmol = to_rdmol(mol)
                AllChem.UFFGetMoleculeForceField(rdmol).Minimize()
                mol = from_rdmol(rdmol)
    
        else:
            init(path=path)
            for i in range(n_scans):
                for bond in bond_list:
                    mol = global_minimum_scan_plams(mol, bond, job_type, **kwarg)
    
            # Optimize the molecule even if no valid bonds are found
            if not bond_list:
                job = job_type(molecule=mol, **kwarg)
                results = job.run()
                mol = results.get_main_molecule()
            finish()
    
        return mol
    
    def find_bond(mol, no_h=True, no_ring=True, bond_orders=[1.0]):
        """
        Create a list of bonds. Each entry is a tuple with indices of atoms forming a dihedral.
        Consider only diherdals with axis being a single bond, so that rotation is possible.
    
        :param |Molecule| mol: The input molecule
        :param bool no_h: If hydrogen-containing bonds should ignored
        :param bool no_ring: If bonds in ring systems should ignored
        :param list bond_orders: A list of accepted bond orders (floats); A bond will be ignored if its bond order is not in *bond_orders*
        :return list: A list of 2-tuples containing the atomic indices of valid bonds
        """
        mol.set_atoms_id()
    
        # Mark atoms that can form an "axis" of a diherdal, i.e atoms with more than one (non-hydrogen) neighbor
        for atom in mol:
            neighbors = mol.neighbors(atom)
            if no_h:
                neighbors = [at for at in mol.neighbors(atom) if at.atnum != 1]
            if no_ring:
                neighbors = [mol.in_ring(at) for at in neighbors]
            atom.mark = (len(neighbors) > 1)
    
        # For each bond with both ends marked add one bond to the list
        ret = []
        for i, bond in enumerate(mol.bonds):
            if bond.atom1.mark and bond.atom2.mark and bond.order in bond_orders:
                at1, at2 = bond.atom1, bond.atom2
                ret.append((at1.id-1 + 1, at2.id-1 + 1))
    
        # Clean up the molecule
        mol.unset_atoms_id()
        for atom in mol:
            del atom.mark
    
        return ret
    
    def global_minimum_scan_plams(mol, bond_tuple, job_type, **kwarg):
        """
        Optimize the molecule (A PLAMS |Job|) with 3 different values for the given dihedral angle and find the lowest energy conformer.
        The matching PLAMS |Results| object must have access to the |get_energy()| and |get_main_molecule()| functions.
        If required, functions can be added manually to a class with the |add_to_class()| function.
    
        :param |Molecule| mol: The input molecule
        :param tuple bond_tuple: A 2-tuple containing the atomic indices of valid bonds
        :param type job_type: A type object of a class derived from |Job|
        :param dict kwarg: Keyword arguments for *job_type*
        :return |Molecule|: A copy of *mol* with a newly optimized geometry
        """
        # Define a number of variables and create 3 copies of the ligand
        angles = (-120, 0, 120)
        mol_list = [mol.copy() for i in range(3)]
        for angle, mol in zip(angles, mol_list):
            bond = mol[bond_tuple]
            atom = mol[bond_tuple[0]]
            mol.rotate_bond(bond, atom, angle, unit='degree')
    
        # Optimize the geometry for all dihedral angles in angle_list
        # The geometry that yields the minimum energy is returned
        energy_list = []
        for mol in mol_list:
            job = job_type(**kwarg)
            job.molecule = mol
            results = job.run()
            energy_list.append(results.get_energy())
            mol_new = results.get_main_molecule()
            for at, at_new in zip(mol, mol_new):
                at.coords = at_new.coords
        minimum = energy_list.index(min(energy_list))
        return mol_list[minimum]
    
    def global_minimum_scan_rdkit(mol, bond_tuple):
        """
        Optimize the molecule (RDKit UFF) with 3 different values for the given dihedral angle and find the lowest energy conformer.
    
        :param |Molecule| mol: The input molecule
        :param tuple bond_tuple: A 2-tuples containing the atomic indices of valid bonds
        :return |Molecule|: A copy of *mol* with a newly optimized geometry
        """
        # Define a number of variables and create 3 copies of the ligand
        uff = AllChem.UFFGetMoleculeForceField
        angles = (-120, 0, 120)
        mol_list = [mol.copy() for i in range(3)]
        for angle, mol in zip(angles, mol_list):
            bond = mol[bond_tuple]
            atom = mol[bond_tuple[0]]
            mol.rotate_bond(bond, atom, angle, unit='degree')
    
        # Optimize the geometry for all dihedral angles in angle_list
        # The geometry that yields the minimum energy is returned
        mol_list = [to_rdmol(mol, properties=False) for mol in mol_list]
        for rdmol in mol_list:
            uff(rdmol).Minimize()
        energy_list = [uff(rdmol).CalcEnergy() for rdmol in mol_list]
        minimum = energy_list.index(min(energy_list))
        return from_rdmol(mol_list[minimum])
    
[/code]

[Next ](pyAHFCDOS.html "Vibronic Density of States using the AH-FC method") [ Previous](numhess.html "Numerical Hessian")

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
